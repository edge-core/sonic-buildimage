#!/bin/bash

function start_app {
    orchagent $ORCHAGENT_ARGS &
    portsyncd $PORTSYNCD_ARGS &
    intfsyncd &
    neighsyncd &
    for file in $SWSSCONFIG_ARGS
    do
      swssconfig /etc/swss/config.d/$file
      sleep 1
    done
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

SWSSCONFIG_ARGS="00-copp.config.json "

if [ "$onie_platform" == "x86_64-dell_s6000_s1220-r0" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    PORTSYNCD_ARGS+="-p /etc/ssw/Force10-S6000/port_config.ini"
    SWSSCONFIG_ARGS+="td2.32ports.qos.1.json td2.32ports.qos.2.json td2.32ports.qos.3.json td2.32ports.qos.4.json td2.32ports.qos.5.json td2.32ports.qos.6.json "
    SWSSCONFIG_ARGS+="td2.32ports.buffers.1.json td2.32ports.buffers.2.json td2.32ports.buffers.3.json "
elif [ "$onie_platform" == "x86_64-dell_s6100_c2538-r0" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    PORTSYNCD_ARGS+="-p /etc/ssw/Force10-S6100/port_config.ini"
elif [ "$aboot_platform" == "x86_64-arista_7050_qx32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    PORTSYNCD_ARGS+="-p /etc/ssw/Arista-7050-QX32/port_config.ini"
    SWSSCONFIG_ARGS+="td2.32ports.qos.1.json td2.32ports.qos.2.json td2.32ports.qos.3.json td2.32ports.qos.4.json td2.32ports.qos.5.json td2.32ports.qos.6.json "
    SWSSCONFIG_ARGS+="td2.32ports.buffers.1.json td2.32ports.buffers.2.json td2.32ports.buffers.3.json "
elif [ "$onie_platform" == "x86_64-mlnx_x86-r5.0.1400" ] || [ "$onie_platform" == "x86_64-mlnx_msn2700-r0" ]; then
    PORTSYNCD_ARGS+="-p /etc/ssw/ACS-MSN2700/port_config.ini"
elif [ "$onie_platform" == "x86_64-accton_as7512_32x-r0" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    PORTSYNCD_ARGS+="-p /etc/ssw/AS7512/port_config.ini"
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
