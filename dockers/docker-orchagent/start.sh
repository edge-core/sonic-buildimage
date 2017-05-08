#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/mirror.json.j2 > /etc/swss/config.d/mirror.json

export platform=`sonic-cfggen -m /etc/sonic/minigraph.xml -v platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start orchagent

