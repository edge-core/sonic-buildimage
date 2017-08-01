#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/mirror.json.j2 > /etc/swss/config.d/mirror.json

export platform=`sonic-cfggen -m /etc/sonic/minigraph.xml -v platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start intfsyncd

supervisorctl start neighsyncd

supervisorctl start swssconfig

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -m /etc/sonic/minigraph.xml -v 'minigraph_vlans.keys() | join(" ")'`
if [ "$VLAN" != "" ]; then
    supervisorctl start arp_update
fi
