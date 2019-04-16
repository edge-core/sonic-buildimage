#!/usr/bin/env bash

mkdir -p /etc/ssw
sonic-cfggen -d -y /etc/sonic/sonic_version.yml -t /usr/share/sonic/templates/sysDescription.j2 > /etc/ssw/sysDescription

mkdir -p /etc/snmp
sonic-cfggen -d -y /etc/sonic/snmp.yml -t /usr/share/sonic/templates/snmpd.conf.j2 > /etc/snmp/snmpd.conf

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

CURRENT_HOSTNAME=`hostname`
HOSTNAME=`sonic-cfggen -d -v DEVICE_METADATA[\'localhost\'][\'hostname\']`

if [ "$?" == "0" ] && [ "$HOSTNAME" != "" ]; then
    echo $HOSTNAME > /etc/hostname
    hostname -F /etc/hostname

    sed -i "/\s$CURRENT_HOSTNAME$/d" /etc/hosts
    echo "127.0.0.1 $HOSTNAME" >> /etc/hosts
fi

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd
supervisorctl start snmpd
supervisorctl start snmp-subagent
