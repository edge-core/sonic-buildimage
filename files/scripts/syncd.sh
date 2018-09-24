#!/bin/bash

SERVICE="syncd"
PEER="swss"
DEBUGLOG="/tmp/swss-syncd-debug.log"
LOCKFILE="/tmp/swss-syncd-lock"

function debug()
{
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
    SYSTEM_WARM_START=`/usr/bin/redis-cli -n 4 hget "WARM_RESTART|system" enable`
    # SYSTEM_WARM_START could be empty, always make WARM_BOOT meaningful.
    if [[ x"$SYSTEM_WARM_START" == x"true" ]]; then
        WARM_BOOT="true"
    else
        WARM_BOOT="false"
    fi
}

function wait_for_database_service()
{
    # Wait for redis server start before database clean
    until [[ $(/usr/bin/docker exec database redis-cli ping | grep -c PONG) -gt 0 ]];
        do sleep 1;
    done

    # Wait for configDB initialization
    until [[ $(/usr/bin/docker exec database redis-cli -n 4 GET "CONFIG_DB_INITIALIZED") ]];
        do sleep 1;
    done
}

start() {
    debug "Starting ${SERVICE} service..."

    lock_service_state_change

    wait_for_database_service
    check_warm_boot

    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    # Don't flush DB during warm boot
    if [[ x"$WARM_BOOT" != x"true" ]]; then
        /usr/bin/docker exec database redis-cli -n 1 FLUSHDB

        # platform specific tasks
        if [ x$sonic_asic_platform == x'mellanox' ]; then
            FAST_BOOT=1
            /usr/bin/mst start
            /usr/bin/mlnx-fw-upgrade.sh
            /etc/init.d/sxdkernel start
            /sbin/modprobe i2c-dev
            /etc/mlnx/mlnx-hw-management start
        elif [ x$sonic_asic_platform == x'cavium' ]; then
            /etc/init.d/xpnet.sh start
        fi
    fi

    # start service docker
    /usr/bin/${SERVICE}.sh start
    debug "Started ${SERVICE} service..."

    unlock_service_state_change
    /usr/bin/${SERVICE}.sh attach
}

stop() {
    debug "Stopping ${SERVICE} service..."

    lock_service_state_change
    check_warm_boot
    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    /usr/bin/${SERVICE}.sh stop
    debug "Stopped ${SERVICE} service..."

    # if warm start enabled, don't stop peer service docker
    if [[ x"$WARM_BOOT" != x"true" ]]; then
        # platform specific tasks
        if [ x$sonic_asic_platform == x'mellanox' ]; then
            /etc/mlnx/mlnx-hw-management stop
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
    start|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
