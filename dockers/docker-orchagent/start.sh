#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/switch.json.j2 > /etc/swss/config.d/switch.json
sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ports.json.j2 > /etc/swss/config.d/ports.json

export platform=`sonic-cfggen -v platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start intfsyncd

supervisorctl start neighsyncd

supervisorctl start swssconfig

supervisorctl start vlanmgrd

supervisorctl start intfmgrd

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
if [ "$VLAN" != "" ]; then
    supervisorctl start arp_update
fi
