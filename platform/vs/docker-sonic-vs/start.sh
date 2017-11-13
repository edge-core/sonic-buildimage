#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/mirror.json.j2 > /etc/swss/config.d/mirror.json
# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ports.json.j2 > /etc/swss/config.d/ports.json

# export platform=`sonic-cfggen -v platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

mkdir -p /var/run/redis

supervisorctl start redis-server

supervisorctl start syncd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start intfsyncd

supervisorctl start neighsyncd

supervisorctl start teamsyncd

supervisorctl start fpmsyncd

# Start arp_update when VLAN exists
# VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
# if [ "$VLAN" != "" ]; then
#     supervisorctl start arp_update
# fi
