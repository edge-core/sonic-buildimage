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

# Create isc-dhcp-relay config file
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/isc-dhcp-relay.j2 > /etc/default/isc-dhcp-relay

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# Wait for all interfaces to come up before starting the DHCP relay

FRONT_PANEL_IFACES=$(sonic-cfggen -m /etc/sonic/minigraph.xml --var-json "minigraph_interfaces" | grep "\"attachto\":" | sed 's/^\s*"attachto":\s"\(.*\)".*$/\1/')
for IFACE in $FRONT_PANEL_IFACES; do
    wait_until_iface_exists $IFACE
done

VLAN_IFACES=$(sonic-cfggen -m /etc/sonic/minigraph.xml --var-json "minigraph_vlan_interfaces" | grep "\"attachto\":" | sed 's/^\s*"attachto":\s"\(.*\)".*$/\1/')
for IFACE in $VLAN_IFACES; do
    wait_until_iface_exists $IFACE
done

PORTCHANNEL_IFACES=$(sonic-cfggen -m /etc/sonic/minigraph.xml --var-json "minigraph_portchannel_interfaces" | grep "\"attachto\":" | sed 's/^\s*"attachto":\s"\(.*\)".*$/\1/')
for IFACE in $PORTCHANNEL_IFACES; do
    wait_until_iface_exists $IFACE
done

# Start the DHCP relay
supervisorctl start isc-dhcp-relay

