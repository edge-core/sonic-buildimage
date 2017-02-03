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

HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

ORCHAGENT_ARGS=""

PORTSYNCD_ARGS="-p /usr/share/sonic/$HWSKU/port_config.ini"

SWSSCONFIG_ARGS="00-copp.config.json "

if [ "$HWSKU" == "Force10-S6000" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    SWSSCONFIG_ARGS+="td2.32ports.qos.1.json td2.32ports.qos.2.json td2.32ports.qos.3.json td2.32ports.qos.4.json td2.32ports.qos.5.json td2.32ports.qos.6.json "
    SWSSCONFIG_ARGS+="td2.32ports.buffers.1.json td2.32ports.buffers.2.json td2.32ports.buffers.3.json "
elif [ "$HWSKU" == "Force10-S6100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    SWSSCONFIG_ARGS+="td2.32ports.qos.1.json td2.32ports.qos.2.json td2.32ports.qos.3.json td2.32ports.qos.4.json td2.32ports.qos.5.json td2.32ports.qos.6.json "
    SWSSCONFIG_ARGS+="td2.32ports.buffers.1.json td2.32ports.buffers.2.json td2.32ports.buffers.3.json "
elif [ "$HWSKU" == "AS7512" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
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
