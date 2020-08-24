#!/usr/bin/env bash

MAC_ADDRESS=$(sonic-cfggen -d -v 'DEVICE_METADATA.localhost.mac')
if [ "$MAC_ADDRESS" == "None" ] || [ -z "$MAC_ADDRESS" ]; then
    MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
    logger "Mac address not found in Device Metadata, Falling back to eth0"
fi

# Create a folder for SsWW record files
mkdir -p /var/log/swss
ORCHAGENT_ARGS="-d /var/log/swss "

# Set orchagent pop batch size to 8192
ORCHAGENT_ARGS+="-b 8192 "

# Set synchronous mode if it is enabled in CONFIG_DB
SYNC_MODE=$(sonic-cfggen -d -v DEVICE_METADATA.localhost.synchronous_mode)
if [ "$SYNC_MODE" == "enable" ]; then
    ORCHAGENT_ARGS+="-s "
fi

# Set mac address
ORCHAGENT_ARGS+="-m $MAC_ADDRESS"

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}
