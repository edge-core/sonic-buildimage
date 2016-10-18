#!/bin/bash

function clean_up {
    service syncd stop
    service rsyslog stop
    exit
}

trap clean_up SIGTERM SIGKILL

# fw-upgrade will exit if firmware was actually upgraded or if some error
# occures
. mlnx-fw-upgrade.sh

service rsyslog start
service syncd start

read
