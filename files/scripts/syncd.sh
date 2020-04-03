#!/bin/bash

SERVICE="syncd"
PEER="swss"
DEBUGLOG="/tmp/swss-syncd-debug.log"
LOCKFILE="/tmp/swss-syncd-lock"

function debug()
{
    /usr/bin/logger $1
    /bin/echo `date` "- $1" >> ${DEBUGLOG}
}

function lock_service_state_change()
{
    debug "Locking ${LOCKFILE} from ${SERVICE} service"

    exec {LOCKFD}>${LOCKFILE}
    /usr/bin/flock -x ${LOCKFD}
    trap "/usr/bin/flock -u ${LOCKFD}" 0 2 3 15

    debug "Locked ${LOCKFILE} (${LOCKFD}) from ${SERVICE} service"
}

function unlock_service_state_change()
{
    debug "Unlocking ${LOCKFILE} (${LOCKFD}) from ${SERVICE} service"
    /usr/bin/flock -u ${LOCKFD}
}

function check_warm_boot()
{
    SYSTEM_WARM_START=`sonic-db-cli STATE_DB hget "WARM_RESTART_ENABLE_TABLE|system" enable`
    SERVICE_WARM_START=`sonic-db-cli STATE_DB hget "WARM_RESTART_ENABLE_TABLE|${SERVICE}" enable`
    # SYSTEM_WARM_START could be empty, always make WARM_BOOT meaningful.
    if [[ x"$SYSTEM_WARM_START" == x"true" ]] || [[ x"$SERVICE_WARM_START" == x"true" ]]; then
        WARM_BOOT="true"
    else
        WARM_BOOT="false"
    fi
}

function wait_for_database_service()
{
    # Wait for redis server start before database clean
    /usr/bin/docker exec database ping_pong_db_insts

    # Wait for configDB initialization
    until [[ $(sonic-db-cli CONFIG_DB GET "CONFIG_DB_INITIALIZED") ]];
        do sleep 1;
    done
}

function getBootType()
{
    # same code snippet in files/build_templates/docker_image_ctl.j2
    case "$(cat /proc/cmdline)" in
    *SONIC_BOOT_TYPE=warm*)
        TYPE='warm'
        ;;
    *SONIC_BOOT_TYPE=fastfast*)
        TYPE='fastfast'
        ;;
    *SONIC_BOOT_TYPE=fast*|*fast-reboot*)
        # check that the key exists
        if [[ $(sonic-db-cli STATE_DB GET "FAST_REBOOT|system") == "1" ]]; then
            TYPE='fast'
        else
            TYPE='cold'
        fi
        ;;
    *)
        TYPE='cold'
    esac
    echo "${TYPE}"
}

start() {
    debug "Starting ${SERVICE} service..."

    lock_service_state_change

    mkdir -p /host/warmboot

    wait_for_database_service
    check_warm_boot

    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    if [[ x"$WARM_BOOT" == x"true" ]]; then
        # Leave a mark for syncd scripts running inside docker.
        touch /host/warmboot/warm-starting
    else
        rm -f /host/warmboot/warm-starting
    fi

    # platform specific tasks

    # start mellanox drivers regardless of
    # boot type
    if [[ x"$sonic_asic_platform" == x"mellanox" ]]; then
        BOOT_TYPE=`getBootType`
        if [[ x"$WARM_BOOT" == x"true" || x"$BOOT_TYPE" == x"fast" ]]; then
            export FAST_BOOT=1
        fi

        if [[ x"$WARM_BOOT" != x"true" ]]; then
            if [[ x"$(/bin/systemctl is-active pmon)" == x"active" ]]; then
                /bin/systemctl stop pmon
                debug "pmon is active while syncd starting, stop it first"
            fi
        fi

        if [[ x"$BOOT_TYPE" == x"fast" ]]; then
            /usr/bin/hw-management.sh chipupdis
        fi

        /usr/bin/mst start
        /usr/bin/mlnx-fw-upgrade.sh
        /etc/init.d/sxdkernel start
    fi

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        if [ x$sonic_asic_platform == x'cavium' ]; then
            /etc/init.d/xpnet.sh start
        fi
    fi

    # start service docker
    /usr/bin/${SERVICE}.sh start
    debug "Started ${SERVICE} service..."

    unlock_service_state_change
}

wait() {
    if [[ x"$sonic_asic_platform" == x"mellanox" ]]; then
        debug "Starting pmon service..."
        /bin/systemctl start pmon
        debug "Started pmon service"
    fi
    /usr/bin/${SERVICE}.sh wait
}

stop() {
    debug "Stopping ${SERVICE} service..."

    lock_service_state_change
    check_warm_boot
    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    if [[ x"$WARM_BOOT" == x"true" ]]; then
        TYPE=warm
    else
        TYPE=cold
    fi

    if [[ x$sonic_asic_platform == x"mellanox" ]] && [[ x$TYPE == x"cold" ]]; then
        debug "Stopping pmon service ahead of syncd..."
        /bin/systemctl stop pmon
        debug "Stopped pmon service"
    fi

    if [[ x$sonic_asic_platform != x"mellanox" ]] || [[ x$TYPE != x"cold" ]]; then
        debug "${TYPE} shutdown syncd process ..."
        /usr/bin/docker exec -i syncd /usr/bin/syncd_request_shutdown --${TYPE}

        # wait until syncd quits gracefully
        while docker top syncd | grep -q /usr/bin/syncd; do
            sleep 0.1
        done

        /usr/bin/docker exec -i syncd /bin/sync
        debug "Finished ${TYPE} shutdown syncd process ..."
    fi

    /usr/bin/${SERVICE}.sh stop
    debug "Stopped ${SERVICE} service..."

    # platform specific tasks

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        if [ x$sonic_asic_platform == x'mellanox' ]; then
            /etc/init.d/sxdkernel stop
            /usr/bin/mst stop
        elif [ x$sonic_asic_platform == x'cavium' ]; then
            /etc/init.d/xpnet.sh stop
            /etc/init.d/xpnet.sh start
        fi
    fi

    unlock_service_state_change
}

case "$1" in
    start|wait|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|wait|stop}"
        exit 1
        ;;
esac
