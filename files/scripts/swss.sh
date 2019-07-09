#!/bin/bash

SERVICE="swss"
PEER="syncd"
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
    SYSTEM_WARM_START=`/usr/bin/redis-cli -n 6 hget "WARM_RESTART_ENABLE_TABLE|system" enable`
    SERVICE_WARM_START=`/usr/bin/redis-cli -n 6 hget "WARM_RESTART_ENABLE_TABLE|${SERVICE}" enable`
    if [[ x"$SYSTEM_WARM_START" == x"true" ]] || [[ x"$SERVICE_WARM_START" == x"true" ]]; then
        WARM_BOOT="true"
    else
        WARM_BOOT="false"
    fi
}

function validate_restore_count()
{
    if [[ x"$WARM_BOOT" == x"true" ]]; then
        RESTORE_COUNT=`/usr/bin/redis-cli -n 6 hget "WARM_RESTART_TABLE|orchagent" restore_count`
        # We have to make sure db data has not been flushed.
        if [[ -z "$RESTORE_COUNT" ]]; then
            WARM_BOOT="false"
        fi
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

# This function cleans up the tables with specific prefixes from the database
# $1 the index of the database
# $2 the string of a list of table prefixes
function clean_up_tables()
{
    redis-cli -n $1 EVAL "
    local tables = {$2}
    for i = 1, table.getn(tables) do
        local matches = redis.call('KEYS', tables[i])
        for j,name in ipairs(matches) do
            redis.call('DEL', name)
        end
    end" 0
}

startPeerService() {
    check_warm_boot

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        /bin/systemctl start ${PEER}
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
        /usr/bin/docker exec database redis-cli -n 0 FLUSHDB
        /usr/bin/docker exec database redis-cli -n 1 FLUSHDB
        /usr/bin/docker exec database redis-cli -n 2 FLUSHDB
        /usr/bin/docker exec database redis-cli -n 5 FLUSHDB
        clean_up_tables 6 "'PORT_TABLE*', 'MGMT_PORT_TABLE*', 'VLAN_TABLE*', 'VLAN_MEMBER_TABLE*', 'LAG_TABLE*', 'LAG_MEMBER_TABLE*', 'INTERFACE_TABLE*', 'MIRROR_SESSION*', 'VRF_TABLE*', 'FDB_TABLE*'"
    fi

    # start service docker
    /usr/bin/${SERVICE}.sh start
    debug "Started ${SERVICE} service..."

    # Unlock has to happen before reaching out to peer service
    unlock_service_state_change
}

wait() {
    startPeerService
    /usr/bin/${SERVICE}.sh wait
}

stop() {
    debug "Stopping ${SERVICE} service..."

    [[ -f ${LOCKFILE} ]] || /usr/bin/touch ${LOCKFILE}

    lock_service_state_change
    check_warm_boot
    debug "Warm boot flag: ${SERVICE} ${WARM_BOOT}."

    /usr/bin/${SERVICE}.sh stop
    debug "Stopped ${SERVICE} service..."

    # Unlock has to happen before reaching out to peer service
    unlock_service_state_change

    # if warm start enabled or peer lock exists, don't stop peer service docker
    if [[ x"$WARM_BOOT" != x"true" ]]; then
        /bin/systemctl stop ${PEER}
    fi
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
