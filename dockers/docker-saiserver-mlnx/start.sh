#!/bin/bash

function clean_up {
    service rsyslog stop
}

start_mlnx()
{
    [ -e /dev/sxdevs/sxcdev ] || ( mkdir -p /dev/sxdevs && mknod /dev/sxdevs/sxcdev c 231 193 )
}

trap clean_up SIGTERM SIGKILL

service rsyslog start

start_mlnx

/usr/bin/saiserver -p /etc/sai/profile.ini -f /etc/sai/portmap.ini
