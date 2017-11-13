#!/usr/bin/env bash

TEAMD_CONF_FILE=$1

function clean_up {
    teamd -f $TEAMD_CONF_FILE -k
    exit $?
}

trap clean_up SIGTERM SIGKILL

teamd -f $TEAMD_CONF_FILE &
TEAMD_PID=$!
wait $TEAMD_PID
exit $?
