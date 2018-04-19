#!/usr/bin/env bash

function wait_until_iface_ready
{
    IFACE=$1

    echo "Waiting until interface $IFACE is up..."

    # Wait for the interface to come up (i.e., 'ip link show' returns 0)
    until ip link show dev $IFACE up > /dev/null 2>&1; do
        sleep 1
    done

    echo "Interface $IFACE is up"

    echo "Waiting until interface $IFACE has an IPv4 address..."

    # Wait until the interface gets assigned an IPv4 address
    while true; do
        IP=$(ip -4 addr show dev $IFACE | grep "inet " | awk '{ print $2 }' | cut -d '/' -f1)

        if [ -n "$IP" ]; then
            break
        fi

        sleep 1
    done

    echo "Interface $IFACE is configured with IP $IP"
}


# Wait for all interfaces to come up and have IPv4 addresses assigned
wait_until_iface_ready Vlan1000
wait_until_iface_ready PortChannel01
wait_until_iface_ready PortChannel01
wait_until_iface_ready PortChannel02
wait_until_iface_ready PortChannel02
wait_until_iface_ready PortChannel03
wait_until_iface_ready PortChannel03
wait_until_iface_ready PortChannel04
wait_until_iface_ready PortChannel04

