#!/usr/bin/env bash

function clean_up {
    service syncd stop
    exit
}

trap clean_up SIGTERM SIGKILL

# fw-upgrade will exit if firmware was actually upgraded or if some error
# occures
. mlnx-fw-upgrade.sh

# FIXME: the script cannot trap SIGTERM signal and it exits without clean_up
# Remove rsyslogd.pid file manually so that to start the rsyslog instantly
service syncd start

read

