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

HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

ORCHAGENT_ARGS=""

PORTSYNCD_ARGS="-p /usr/share/sonic/hwsku/port_config.ini"

SWSSCONFIG_ARGS="00-copp.config.json "

if [ "$HWSKU" == "Force10-S6000" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    SWSSCONFIG_ARGS+="td2.32ports.qos.json td2.32ports.buffers.json "
elif [ "$HWSKU" == "Force10-S6100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-Z9100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
    SWSSCONFIG_ARGS+="td2.32ports.qos.json td2.32ports.buffers.json "
elif [ "$HWSKU" == "Arista-7060-CX32S" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "AS7512" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "INGRASYS-S9100-C32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "ACS-MSN2700" ]; then
    SWSSCONFIG_ARGS+="msn2700.32ports.buffers.json msn2700.32ports.qos.json "
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
