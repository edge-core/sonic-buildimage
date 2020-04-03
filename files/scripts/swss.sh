#!/bin/bash

SERVICE="swss"
PEER="syncd"
DEPENDENT="teamd radv dhcp_relay"
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
    if [[ x"$SYSTEM_WARM_START" == x"true" ]] || [[ x"$SERVICE_WARM_START" == x"true" ]]; then
        WARM_BOOT="true"
    else
        WARM_BOOT="false"
    fi
}

function validate_restore_count()
{
    if [[ x"$WARM_BOOT" == x"true" ]]; then
        RESTORE_COUNT=`sonic-db-cli STATE_DB hget "WARM_RESTART_TABLE|orchagent" restore_count`
        # We have to make sure db data has not been flushed.
        if [[ -z "$RESTORE_COUNT" ]]; then
            WARM_BOOT="false"
        fi
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

# This function cleans up the tables with specific prefixes from the database
# $1 the index of the database
# $2 the string of a list of table prefixes
function clean_up_tables()
{
    sonic-db-cli $1 EVAL "
    local tables = {$2}
    for i = 1, table.getn(tables) do
        local matches = redis.call('KEYS', tables[i])
        for j,name in ipairs(matches) do
            redis.call('DEL', name)
        end
    end" 0
}

start_peer_and_dependent_services() {
    check_warm_boot

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        /bin/systemctl start ${PEER}
        for dep in ${DEPENDENT}; do
            /bin/systemctl start ${dep}
        done
    fi
}

stop_peer_and_dependent_services() {
    # if warm start enabled or peer lock exists, don't stop peer service docker
    if [[ x"$WARM_BOOT" != x"true" ]]; then
        /bin/systemctl stop ${PEER}
        for dep in ${DEPENDENT}; do
            /bin/systemctl stop ${dep}
        done
    fi
}

start() {
    debug "Starting ${SERVICE} service..."

    lock_service_state_change

    wait_for_database_service
    check_warm_boot
    validate_restore_count

    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    # Don't flush DB during warm boot
    if [[ x"$WARM_BOOT" != x"true" ]]; then
        debug "Flushing APP, ASIC, COUNTER, CONFIG, and partial STATE databases ..."
        sonic-db-cli APPL_DB FLUSHDB
        sonic-db-cli ASIC_DB FLUSHDB
        sonic-db-cli COUNTERS_DB FLUSHDB
        sonic-db-cli FLEX_COUNTER_DB FLUSHDB
        clean_up_tables STATE_DB "'PORT_TABLE*', 'MGMT_PORT_TABLE*', 'VLAN_TABLE*', 'VLAN_MEMBER_TABLE*', 'LAG_TABLE*', 'LAG_MEMBER_TABLE*', 'INTERFACE_TABLE*', 'MIRROR_SESSION*', 'VRF_TABLE*', 'FDB_TABLE*'"
    fi

    # start service docker
    /usr/bin/${SERVICE}.sh start
    debug "Started ${SERVICE} service..."

    # Unlock has to happen before reaching out to peer service
    unlock_service_state_change
}

wait() {
    start_peer_and_dependent_services

    # Allow some time for peer container to start
    # NOTE: This assumes Docker containers share the same names as their
    # corresponding services
    for SECS in {1..60}; do
        RUNNING=$(docker inspect -f '{{.State.Running}}' ${PEER})
        if [[ x"$RUNNING" == x"true" ]]; then
            break
        else
            sleep 1
        fi
    done

    # NOTE: This assumes Docker containers share the same names as their
    # corresponding services
    /usr/bin/docker-wait-any ${SERVICE} ${PEER}
}

stop() {
    debug "Stopping ${SERVICE} service..."

    [[ -f ${LOCKFILE} ]] || /usr/bin/touch ${LOCKFILE}

    lock_service_state_change
    check_warm_boot
    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    /usr/bin/${SERVICE}.sh stop
    debug "Stopped ${SERVICE} service..."

    # Flush FAST_REBOOT table when swss needs to stop. The only
    # time when this would take effect is when fast-reboot
    # encountered error, e.g. syncd crashed. And swss needs to
    # be restarted.
    debug "Clearing FAST_REBOOT flag..."
    clean_up_tables STATE_DB "'FAST_REBOOT*'"

    # Unlock has to happen before reaching out to peer service
    unlock_service_state_change

    stop_peer_and_dependent_services
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
