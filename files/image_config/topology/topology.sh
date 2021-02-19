#!/bin/bash
# This script is invoked by topology.service only
# for multi-asic virtual platform. For multi-asic platform
# multiple Database instances are present
# and HWKSU information is retrieved from first database instance.
#

get_hwsku() {
    # Get HWSKU from config_db. If HWSKU is not available in config_db
    # get HWSKU from minigraph.xml if minigraph file exists.
    HWSKU=`sonic-cfggen -d -v 'DEVICE_METADATA["localhost"]["hwsku"]' 2>&1`
    if [[ $? -ne 0 || $HWSKU == "" ]]; then
            if [[ -f "/etc/sonic/minigraph.xml" ]]; then
                HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v "DEVICE_METADATA['localhost']['hwsku']" 2>&1`
                if [[ $? -ne 0 || $HWSKU == "" ]]; then
                    HWSKU=""
                fi
            else
                HWSKU=""
            fi
    fi
    echo "${HWSKU}"
}

start() {
    TOPOLOGY_SCRIPT="topology.sh"
    PLATFORM=`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`
    HWSKU=`get_hwsku`
    if [[ $HWSKU != "" ]]; then
        /usr/share/sonic/device/$PLATFORM/$HWSKU/$TOPOLOGY_SCRIPT start
    else
        echo "Failed to get HWSKU"
        exit 1
    fi
}

stop() {
    TOPOLOGY_SCRIPT="topology.sh"
    PLATFORM=`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`
    HWSKU=`get_hwsku`
    if [[ $HWSKU != "" ]]; then
        /usr/share/sonic/device/$PLATFORM/$HWSKU/$TOPOLOGY_SCRIPT stop
    else
        echo "Failed to get HWSKU"
        exit 1
    fi
}

# read SONiC immutable variables
[ -f /etc/sonic/sonic-environment ] && . /etc/sonic/sonic-environment

case "$1" in
    start|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        ;;
esac
