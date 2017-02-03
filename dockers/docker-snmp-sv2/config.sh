#!/bin/bash

mkdir -p /etc/ssw

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/sonic_version.yml -t /etc/swss/snmp/sysDescription.j2 >/etc/ssw/sysDescription

mkdir -p /etc/snmp

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/snmp.yml -t /etc/swss/snmp/snmpd.conf.j2 >/etc/snmp/snmpd.conf

hwsku=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`
/bin/cp -rf /usr/share/sonic/$hwsku/alias_map.json /etc/snmp/

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

