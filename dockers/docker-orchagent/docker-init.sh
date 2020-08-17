#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

CFGGEN_PARAMS=" \
    -d \
    -y /etc/sonic/constants.yml \
    -t /usr/share/sonic/templates/switch.json.j2,/etc/swss/config.d/switch.json \
    -t /usr/share/sonic/templates/ipinip.json.j2,/etc/swss/config.d/ipinip.json \
    -t /usr/share/sonic/templates/ports.json.j2,/etc/swss/config.d/ports.json \
    -t /usr/share/sonic/templates/copp.json.j2,/etc/swss/config.d/00-copp.config.json \
    -t /usr/share/sonic/templates/vlan_vars.j2 \
"
VLAN=$(sonic-cfggen $CFGGEN_PARAMS)

# Executed HWSKU specific initialization tasks.
if [ -x /usr/share/sonic/hwsku/hwsku-init ]; then
    /usr/share/sonic/hwsku/hwsku-init
fi

# Start arp_update when VLAN exists
if [ "$VLAN" != "" ]; then
    cp /usr/share/sonic/templates/arp_update.conf /etc/supervisord/conf.d/
fi

exec /usr/bin/supervisord
