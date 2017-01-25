#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /etc/swss/lldp/lldpd.conf.j2 >/etc/lldpd.conf

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

