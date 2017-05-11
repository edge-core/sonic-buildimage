#!/usr/bin/env bash

HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

ORCHAGENT_ARGS=""

if [ "$HWSKU" == "Force10-S6000" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-S6100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-Z9100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7060-CX32S" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "AS7512" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "INGRASYS-S9100-C32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
fi

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}

