#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/isc-dhcp-relay.j2 > /etc/default/isc-dhcp-relay

