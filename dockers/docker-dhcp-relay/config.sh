#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/dhcp_relay.yml -t /usr/share/sonic/templates/isc-dhcp-relay.j2 > /etc/default/isc-dhcp-relay

