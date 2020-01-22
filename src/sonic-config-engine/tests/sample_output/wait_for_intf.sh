#!/usr/bin/env bash

function wait_until_iface_ready
{
    IFACE_NAME=$1
    IFACE_CIDR=$2

    echo "Waiting until interface ${IFACE_NAME} is ready..."

    # Wait for the interface to come up
    # (i.e., interface is present in STATE_DB and state is "ok")
    while true; do
        RESULT=$(sonic-db-cli STATE_DB HGET "INTERFACE_TABLE|${IFACE_NAME}|${IFACE_CIDR}" "state" 2> /dev/null)
        if [ x"$RESULT" == x"ok" ]; then
            break
        fi

        sleep 1
    done

    echo "Interface ${IFACE_NAME} is ready!"
}


# Wait for all interfaces with IPv4 addresses to be up and ready
wait_until_iface_ready Vlan1000 192.168.0.1/27
wait_until_iface_ready PortChannel01 10.0.0.56/31
wait_until_iface_ready PortChannel02 10.0.0.58/31
wait_until_iface_ready PortChannel03 10.0.0.60/31
wait_until_iface_ready PortChannel04 10.0.0.62/31

