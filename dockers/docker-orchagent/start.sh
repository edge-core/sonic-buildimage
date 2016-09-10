#!/bin/bash

function clean_up {
    kill -9 $ORCHAGENT_PID
    kill -9 $PORTSYNCD_PID
    kill -9 $INTFSYNCD_PID
    kill -9 $NEIGHSYNCD_PID
    service rsyslog stop
    exit
}

trap clean_up SIGTERM SIGKILL

. /host/machine.conf

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

ORCHAGENT_ARGS=""

PORTSYNCD_ARGS=""

if [ "$onie_platform" == "x86_64-dell_s6000_s1220-r0" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    PORTSYNCD_ARGS+="-p /etc/ssw/ACS-S6000/port_config.ini"
elif [ "$onie_platform" == "x86_64-mlnx_x86-r5.0.1400" ]; then
    PORTSYNCD_ARGS+="-p /etc/ssw/ACS-MSN2700/port_config.ini"
fi

service rsyslog start
orchagent $ORCHAGENT_ARGS &
ORCHAGENT_PID=$!
sleep 5
portsyncd $PORTSYNCD_ARGS &
PORTSYNCD_PID=$!
sleep 5
intfsyncd &
INTFSYNCD_PID=$!
sleep 5
neighsyncd &
NEIGHSYNCD_PID=$!

read
