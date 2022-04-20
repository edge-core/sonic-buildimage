#!/bin/bash

. /usr/local/bin/syncd_common.sh

function startplatform() {
    # Add gbsyncd to FEATURE table, if not in. It did have same config as syncd.
    if [ -z $($SONIC_DB_CLI CONFIG_DB HGET 'FEATURE|gbsyncd' state) ]; then
        local CMD="local r=redis.call('DUMP', KEYS[1]); redis.call('RESTORE', KEYS[2], 0, r)"
        $SONIC_DB_CLI CONFIG_DB EVAL "$CMD" 2 'FEATURE|syncd' 'FEATURE|gbsyncd'
    fi
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

SERVICE="$gbsyncd_platform"
PEER="swss"
DEBUGLOG="/tmp/swss-$SERVICE-debug$DEV.log"
LOCKFILE="/tmp/swss-$SERVICE-lock$DEV"
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
