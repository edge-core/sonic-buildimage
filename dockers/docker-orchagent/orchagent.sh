#!/usr/bin/env bash

HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

# Create a folder for SsWW record files
mkdir -p /var/log/swss
ORCHAGENT_ARGS="-d /var/log/swss "

if [ "$HWSKU" == "Force10-S6000" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-S6000-Q32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-S6100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Force10-Z9100" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7050-QX32S" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "Arista-7060-CX32S" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "AS7512" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "INGRASYS-S9100-C32" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "INGRASYS-S8900-54XC" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$HWSKU" == "INGRASYS-S8900-64XC" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
else
    echo "Unsupported HWSKU:$HWSKU. Exiting..." > /dev/stderr
    exit 1
fi

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}

