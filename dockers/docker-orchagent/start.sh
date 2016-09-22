#!/bin/bash

function start_app {
    orchagent $ORCHAGENT_ARGS &
    portsyncd $PORTSYNCD_ARGS &
    intfsyncd &
    neighsyncd &
    swssconfig &
}

function clean_up {
    pkill -9 orchagent
    pkill -9 portsyncd
    pkill -9 intfsyncd
    pkill -9 neighsyncd
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
while true; do
    # Check if syncd starts
    result=`echo -en "SELECT 1\nHLEN HIDDEN" | redis-cli | sed -n 2p`
    if [ "$result" != "0" ]; then
        start_app
        read
    fi
    sleep 1
done
