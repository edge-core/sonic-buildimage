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

start_app
read
