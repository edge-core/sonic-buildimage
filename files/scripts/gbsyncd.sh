#!/bin/bash

. /usr/local/bin/syncd_common.sh

function startplatform() {
    :
}

function waitplatform() {
    :
}

function stopplatform1() {
    :
}

function stopplatform2() {
    :
}

OP=$1
DEV=$2

SERVICE="gbsyncd"
PEER="swss"
DEBUGLOG="/tmp/swss-gbsyncd-debug$DEV.log"
LOCKFILE="/tmp/swss-gbsyncd-lock$DEV"
NAMESPACE_PREFIX="asic"
if [ "$DEV" ]; then
    NET_NS="$NAMESPACE_PREFIX$DEV" #name of the network namespace
    SONIC_DB_CLI="sonic-db-cli -n $NET_NS"
else
    NET_NS=""
    SONIC_DB_CLI="sonic-db-cli"
fi

case "$1" in
    start|wait|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|wait|stop}"
        exit 1
        ;;
esac
