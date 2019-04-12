#! /bin/bash

VERBOSE=no

# Check components
COMP_LIST="orchagent neighsyncd bgp"
EXP_STATE="reconciled"

ASSISTANT_SCRIPT="/usr/bin/neighbor_advertiser"


function debug()
{
    /usr/bin/logger "WARMBOOT_FINALIZER : $1"
    if [[ x"${VERBOSE}" == x"yes" ]]; then
        echo `date` "- $1"
    fi
}


function check_warm_boot()
{
    WARM_BOOT=`/usr/bin/redis-cli -n 6 hget "WARM_RESTART_ENABLE_TABLE|system" enable`
}


function wait_for_database_service()
{
    debug "Wait for database to become ready..."

    # Wait for redis server start before database clean
    until [[ $(/usr/bin/docker exec database redis-cli ping | grep -c PONG) -gt 0 ]];
        do sleep 1;
    done

    # Wait for configDB initialization
    until [[ $(/usr/bin/docker exec database redis-cli -n 4 GET "CONFIG_DB_INITIALIZED") ]];
        do sleep 1;
    done

    debug "Database is ready..."
}


function get_component_state()
{
    /usr/bin/redis-cli -n 6 hget "WARM_RESTART_TABLE|$1" state
}


function check_list()
{
    RET_LIST=''
    for comp in $@; do
        state=`get_component_state ${comp}`
	if [[ x"${state}" != x"${EXP_STATE}" ]]; then
            RET_LIST="${RET_LIST} ${comp}"
	fi
    done

    echo ${RET_LIST}
}


function finalize_warm_boot()
{
    debug "Finalizing warmboot..."
    sudo config warm_restart disable
}


wait_for_database_service

check_warm_boot

if [[ x"${WARM_BOOT}" != x"true" ]]; then
    debug "warmboot is not enabled ..."
    exit 0
fi

list=${COMP_LIST}

# Wait up to 5 minutes
for i in `seq 60`; do
    list=`check_list ${list}`
    if [[ -z "${list}" ]]; then
	break
    fi
    sleep 5
done

if [[ -n "${list}" ]]; then
    debug "Some components didn't finish reconcile: ${list} ..."
fi

finalize_warm_boot
