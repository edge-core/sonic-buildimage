#!/bin/bash
# This script is invoked by topology.service only
# for multi-asic virtual platform. For multi-asic platform 
# multiple Database instances are present 
# and HWKSU information is retrieved from first database instance.
#

start() {
    TOPOLOGY_SCRIPT="topology.sh"
    PLATFORM=${PLATFORM:-`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`}
    HWSKU=${HWSKU:-`sonic-cfggen -d -v 'DEVICE_METADATA["localhost"]["hwsku"]'`}
    /usr/share/sonic/device/$PLATFORM/$HWSKU/$TOPOLOGY_SCRIPT start
}
stop() {
    TOPOLOGY_SCRIPT="topology.sh"
    PLATFORM=${PLATFORM:-`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`}
    HWSKU=${HWSKU:-`sonic-cfggen -d -v 'DEVICE_METADATA["localhost"]["hwsku"]'`}
    usr/share/sonic/device/$PLATFORM/$HWSKU/$TOPOLOGY_SCRIPT stop 
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
