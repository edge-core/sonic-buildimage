#!/bin/bash

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
sleep 5
portsyncd $PORTSYNCD_ARGS &
sleep 5
intfsyncd &
sleep 5
neighsyncd &
