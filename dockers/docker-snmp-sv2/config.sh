#!/bin/bash

#sysDescription is currently mounted, uncomment this line and provide version.yml instead if use copying instead of mounting
#sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/version.yml -t /etc/swss/snmp/sysDescription.j2 >/etc/ssw/sysDescription

mkdir -p /etc/snmp

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/snmp.yml -t /etc/swss/snmp/snmpd.conf.j2 >/etc/snmp/snmpd.conf

hwsku=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`
/bin/cp -rf /usr/share/sonic/$hwsku/alias_map.json /etc/snmp/


