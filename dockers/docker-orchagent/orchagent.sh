#!/usr/bin/env bash

EXIT_SWSS_VARS_FILE_NOT_FOUND=1
SWSS_VARS_FILE=/usr/share/sonic/templates/swss_vars.j2

if [ ! -f "$SWSS_VARS_FILE" ]; then
    echo "SWSS vars template file not found"
    exit $EXIT_SWSS_VARS_FILE_NOT_FOUND
fi

# Retrieve SWSS vars from sonic-cfggen
SWSS_VARS=$(sonic-cfggen -d -y /etc/sonic/sonic_version.yml -t $SWSS_VARS_FILE)
export platform=$(echo $SWSS_VARS | jq -r '.asic_type')

MAC_ADDRESS=$(echo $SWSS_VARS | jq -r '.mac')
if [ "$MAC_ADDRESS" == "None" ] || [ -z "$MAC_ADDRESS" ]; then
    MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
    logger "Mac address not found in Device Metadata, Falling back to eth0"
fi

# Create a folder for SwSS record files
mkdir -p /var/log/swss
ORCHAGENT_ARGS="-d /var/log/swss "

# Set orchagent pop batch size to 8192
ORCHAGENT_ARGS+="-b 8192 "

# Set synchronous mode if it is enabled in CONFIG_DB
SYNC_MODE=$(echo $SWSS_VARS | jq -r '.synchronous_mode')
if [ "$SYNC_MODE" == "enable" ]; then
    ORCHAGENT_ARGS+="-s "
fi

# Check if there is an "asic_id field" in the DEVICE_METADATA in configDB.
#"DEVICE_METADATA": {
#    "localhost": {
#        ....
#        "asic_id": "0",
#    }
#},
# ID field could be integers just to denote the asic instance like 0,1,2...
# OR could be PCI device ID's which will be strings like "03:00.0"
# depending on what the SAI/SDK expects.
asic_id=$(echo $SWSS_VARS | jq -r '.asic_id')
if [ -n "$asic_id" ]
then
    ORCHAGENT_ARGS+="-i $asic_id "
fi

# Add platform specific arguments if necessary
if [ "$platform" == "broadcom" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "cavium" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "nephos" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "centec" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "barefoot" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "vs" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
elif [ "$platform" == "mellanox" ]; then
    ORCHAGENT_ARGS+=""
elif [ "$platform" == "innovium" ]; then
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
else
    # Should we use the fallback MAC in case it is not found in Device.Metadata
    ORCHAGENT_ARGS+="-m $MAC_ADDRESS"
fi

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}
