#!/usr/bin/env bash

function wait_until_iface_exists
{
    IFACE=$1

    echo "Waiting for interface ${IFACE}..."

    # Wait for the interface to come up (i.e., 'ip link show' returns 0)
    until ip link show $IFACE > /dev/null 2>&1; do
        sleep 1
    done

    echo "Interface ${IFACE} is created"
}


# Wait for all interfaces to come up before starting the DHCP relay
wait_until_iface_exists Vlan1000
wait_until_iface_exists PortChannel04
wait_until_iface_exists PortChannel02
wait_until_iface_exists PortChannel03
wait_until_iface_exists PortChannel03
wait_until_iface_exists PortChannel01
wait_until_iface_exists PortChannel02
wait_until_iface_exists PortChannel04
wait_until_iface_exists PortChannel01

