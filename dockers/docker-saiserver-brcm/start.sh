#!/bin/bash

function clean_up {
    service rsyslog stop
}

start_bcm()
{
    [ -e /dev/linux-bcm-knet ] || mknod /dev/linux-bcm-knet c 122 0
    [ -e /dev/linux-user-bde ] || mknod /dev/linux-user-bde c 126 0
    [ -e /dev/linux-kernel-bde ] || mknod /dev/linux-kernel-bde c 127 0
}

trap clean_up SIGTERM SIGKILL

service rsyslog start

start_bcm

/usr/bin/saiserver -p /etc/sai/profile.ini -f /etc/sai/portmap.ini
