#!/usr/bin/env bash

TEAMD_CONF_PATH=/etc/teamd

function start_app {
    rm -f /var/run/teamd/*
    if [ "$(ls -A $TEAMD_CONF_PATH)" ]; then
        for f in $TEAMD_CONF_PATH/*; do
            teamd -f $f -d
        done
    fi
    teamsyncd &
}

function clean_up {
    if [ "$(ls -A $TEAMD_CONF_PATH)" ]; then
        for f in $TEAMD_CONF_PATH/*; do
            teamd -f $f -k
        done
    fi
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
