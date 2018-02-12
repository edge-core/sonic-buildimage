#!/usr/bin/env bash

mkdir -p /etc/ssw
sonic-cfggen -d -y /etc/sonic/sonic_version.yml -t /usr/share/sonic/templates/sysDescription.j2 > /etc/ssw/sysDescription

mkdir -p /etc/snmp
sonic-cfggen -d -y /etc/sonic/snmp.yml -t /usr/share/sonic/templates/snmpd.conf.j2 > /etc/snmp/snmpd.conf
sonic-cfggen -d -t /usr/share/sonic/templates/alias_map.j2 > /etc/snmp/alias_map.json

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd
supervisorctl start snmpd-config-updater
supervisorctl start snmpd
supervisorctl start snmp-subagent
