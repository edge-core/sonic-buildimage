#!/usr/bin/env bash

ASIC=`sonic-cfggen -y /etc/sonic/sonic_version.yml -v asic_type`

MAC_ADDRESS=`ip link show eth0 | grep ether | awk '{print $2}'`

# Create a folder for SsWW record files
mkdir -p /var/log/swss
ORCHAGENT_ARGS="-d /var/log/swss "

# Add platform specific arguments if necessary
if [ "$ASIC" == "broadcom" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$ASIC" == "cavium" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
fi

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}

