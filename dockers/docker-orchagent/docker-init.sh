#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

sonic-cfggen -d -y /etc/sonic/sonic_version.yml -t /usr/share/sonic/templates/switch.json.j2 > /etc/swss/config.d/switch.json
sonic-cfggen -d -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
sonic-cfggen -d -t /usr/share/sonic/templates/ports.json.j2 > /etc/swss/config.d/ports.json
sonic-cfggen -d -t /usr/share/sonic/templates/copp.json.j2 > /etc/swss/config.d/00-copp.config.json

# Executed HWSKU specific initialization tasks.
if [ -x /usr/share/sonic/hwsku/hwsku-init ]; then
    /usr/share/sonic/hwsku/hwsku-init
fi

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
if [ "$VLAN" != "" ]; then
    cp /usr/share/sonic/templates/arp_update.conf /etc/supervisor/conf.d/
fi

exec /usr/bin/supervisord
