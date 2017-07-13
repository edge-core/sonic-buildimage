#!/usr/bin/env bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/lldpd.conf.j2 > /etc/lldpd.conf

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd
supervisorctl start lldpd
supervisorctl start lldpd-conf-reload
supervisorctl start lldp-syncd
