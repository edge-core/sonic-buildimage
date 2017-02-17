#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /etc/sonic/templates/interfaces.j2 >/etc/network/interfaces
sonic-cfggen -m /etc/sonic/minigraph.xml -t /etc/sonic/templates/vlan_interfaces.j2 >/etc/network/interfaces.d/vlan_interfaces
sonic-cfggen -m /etc/sonic/minigraph.xml -t /etc/sonic/templates/lag_interfaces.j2 >/etc/network/interfaces.d/lag_interfaces
ifdown eth0 && ifup eth0
ifdown lo && ifup lo

