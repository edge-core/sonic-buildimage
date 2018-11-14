#!/usr/bin/env bash

start_mlnx()
{
    [ -e /dev/sxdevs/sxcdev ] || ( mkdir -p /dev/sxdevs && mknod /dev/sxdevs/sxcdev c 231 193 )
}


rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

start_mlnx

supervisorctl start saiserver
