#!/bin/bash

function clean_up {
    service rsyslog stop
}

trap clean_up SIGTERM SIGKILL

rm -f /var/run/rsyslogd.pid
service rsyslog start

/usr/bin/saiserver -p /etc/sai/profile.ini -f /etc/sai/portmap.ini
