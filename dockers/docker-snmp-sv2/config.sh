#!/bin/bash

mkdir -p /etc/ssw

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/sonic_version.yml -t /usr/share/sonic/templates/sysDescription.j2 >/etc/ssw/sysDescription

mkdir -p /etc/snmp

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/snmp.yml -t /usr/share/sonic/templates/snmpd.conf.j2 >/etc/snmp/snmpd.conf

sonic-cfggen -m /etc/sonic/minigraph.xml -s >/etc/snmp/alias_map.json

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

rm -f /var/run/rsyslogd.pid
