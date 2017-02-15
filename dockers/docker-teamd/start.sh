#!/bin/bash

TEAMD_CONF_PATH=/etc/teamd

function start_app {
    if [ -d $TEAMD_CONF_PATH ]; then
        for f in $TEAMD_CONF_PATH/*; do
            teamd -f $f -d
        done
    fi
    teamsyncd &
}

function clean_up {
    pkill -9 teamd
    pkill -9 teamsyncd
    service rsyslog stop
    exit
}

trap clean_up SIGTERM SIGKILL

service rsyslog start

# Before teamd could automatically add newly created host interfaces into the
# LAG, this workaround will wait until the host interfaces are created and then
# the processes will be started.
while true; do
    # Check if front-panel ports are configured
    result=`echo -en "SELECT 0\nHGETALL PORT_TABLE:ConfigDone" | redis-cli | sed -n 3p`
    if [ "$result" != "0" ]; then
        start_app
        read
    fi
    sleep 1
done
