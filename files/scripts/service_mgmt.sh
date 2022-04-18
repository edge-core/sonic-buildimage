#!/bin/bash

function debug()
{
    /usr/bin/logger $1
    /bin/echo `date` "- $1" >> ${DEBUGLOG}
}

function check_warm_boot()
{
    SYSTEM_WARM_START=`$SONIC_DB_CLI STATE_DB hget "WARM_RESTART_ENABLE_TABLE|system" enable`
    SERVICE_WARM_START=`$SONIC_DB_CLI STATE_DB hget "WARM_RESTART_ENABLE_TABLE|${SERVICE}" enable`
    if [[ x"$SYSTEM_WARM_START" == x"true" ]] || [[ x"$SERVICE_WARM_START" == x"true" ]]; then
        WARM_BOOT="true"
    else
        WARM_BOOT="false"
    fi
}

function check_fast_boot ()
{
    if [[ $($SONIC_DB_CLI STATE_DB GET "FAST_REBOOT|system") == "1" ]]; then
        FAST_BOOT="true"
    else
        FAST_BOOT="false"
    fi
}

start() {
    debug "Starting ${SERVICE}$DEV service..."

    # start service docker
    /usr/bin/${SERVICE}.sh start $DEV
    debug "Started ${SERVICE}$DEV service..."
}

wait() {
    /usr/bin/${SERVICE}.sh wait $DEV
}

stop() {
    debug "Stopping ${SERVICE}$DEV service..."

    check_warm_boot
    check_fast_boot
    debug "Warm boot flag: ${SERVICE}$DEV ${WARM_BOOT}."
    debug "Fast boot flag: ${SERVICE}$DEV ${FAST_BOOT}."

    # For WARM/FAST boot do not perform service stop
    if [[ x"$WARM_BOOT" != x"true" ]] && [[ x"$FAST_BOOT" != x"true" ]]; then
        /usr/bin/${SERVICE}.sh stop $DEV
        debug "Stopped ${SERVICE}$DEV service..."
    else
        debug "Killing Docker ${SERVICE}${DEV}..."
        /usr/bin/${SERVICE}.sh kill $DEV
    fi
}

DEV=$2

SCRIPT_NAME=$(basename -- "$0")
SERVICE="${SCRIPT_NAME%.*}"
DEBUGLOG="/tmp/$SERVICE-debug$DEV.log"
NAMESPACE_PREFIX="asic"
if [ "$DEV" ]; then
    NET_NS="$NAMESPACE_PREFIX$DEV" #name of the network namespace
    SONIC_DB_CLI="sonic-db-cli -n $NET_NS"
else
    SONIC_DB_CLI="sonic-db-cli"
fi

case "$1" in
    start|wait|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|wait|stop}"
        exit 1
        ;;
esac
