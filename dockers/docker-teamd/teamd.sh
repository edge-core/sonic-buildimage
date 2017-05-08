#!/usr/bin/env bash

TEAMD_CONF_PATH=/etc/teamd

# Before teamd could automatically add newly created host interfaces into the
# LAG, this workaround will be needed. It will remove the obsolete files and
# net devices that are failed to be removed in the previous run.
function start_app {
    # Remove *.pid and *.sock files if there are any
    rm -f /var/run/teamd/*
    if [ -d $TEAMD_CONF_PATH ]; then
        for f in $TEAMD_CONF_PATH/*; do
            # Remove netdevs if there are any
            intf=`echo $f | awk -F'[/.]' '{print $4}'`
            ip link del $intf
            teamd -f $f -d
        done
    fi
    teamsyncd &
}

function clean_up {
    pkill -9 teamd
    pkill -9 teamsyncd
    exit
}

trap clean_up SIGTERM SIGKILL

# Before teamd could automatically add newly created host interfaces into the
# LAG, this workaround will wait until the host interfaces are created and then
# the processes will be started.
while true; do
    # Check if front-panel ports are configured
    result=`echo -en "SELECT 0\nHGETALL PORT_TABLE:ConfigDone" | redis-cli | sed -n 3p`
    if [ "$result" == "0" ]; then
        start_app
        read
    fi
    sleep 1
done

