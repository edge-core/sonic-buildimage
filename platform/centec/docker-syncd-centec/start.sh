#!/bin/bash

function clean_up {
    service syncd stop
    service rsyslog stop
    exit
}

trap clean_up SIGTERM SIGKILL

rm -f /var/run/rsyslogd.pid
service rsyslog start
service syncd start

read
