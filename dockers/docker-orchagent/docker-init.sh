#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/
mkdir -p /etc/supervisor/
mkdir -p /etc/supervisor/conf.d/

CFGGEN_PARAMS=" \
    -d \
    -y /etc/sonic/constants.yml \
    -t /usr/share/sonic/templates/switch.json.j2,/etc/swss/config.d/switch.json \
    -t /usr/share/sonic/templates/ipinip.json.j2,/etc/swss/config.d/ipinip.json \
    -t /usr/share/sonic/templates/ports.json.j2,/etc/swss/config.d/ports.json \
    -t /usr/share/sonic/templates/vlan_vars.j2 \
    -t /usr/share/sonic/templates/ndppd.conf.j2,/etc/ndppd.conf \
    -t /usr/share/sonic/templates/critical_processes.j2,/etc/supervisor/critical_processes \
    -t /usr/share/sonic/templates/supervisord.conf.j2,/etc/supervisor/conf.d/supervisord.conf
"
VLAN=$(sonic-cfggen $CFGGEN_PARAMS)

# Executed HWSKU specific initialization tasks.
if [ -x /usr/share/sonic/hwsku/hwsku-init ]; then
    /usr/share/sonic/hwsku/hwsku-init
fi

# Start arp_update and NDP proxy daemon when VLAN exists
if [ "$VLAN" != "" ]; then
    cp /usr/share/sonic/templates/arp_update.conf /etc/supervisor/conf.d/
    cp /usr/share/sonic/templates/ndppd.conf /etc/supervisor/conf.d/
fi

exec /usr/local/bin/supervisord
