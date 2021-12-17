#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

CFGGEN_PARAMS=" \
    -d \
    -y /etc/sonic/constants.yml \
    -t /usr/share/sonic/templates/switch.json.j2,/etc/swss/config.d/switch.json \
    -t /usr/share/sonic/templates/ipinip.json.j2,/etc/swss/config.d/ipinip.json \
    -t /usr/share/sonic/templates/ports.json.j2,/etc/swss/config.d/ports.json \
    -t /usr/share/sonic/templates/vlan_vars.j2 \
    -t /usr/share/sonic/templates/ndppd.conf.j2,/etc/ndppd.conf \
    -t /usr/share/sonic/templates/wait_for_link.sh.j2,/usr/bin/wait_for_link.sh \
"
VLAN=$(sonic-cfggen $CFGGEN_PARAMS)
SUBTYPE=$(sonic-cfggen -d -v "DEVICE_METADATA['localhost']['subtype']")

chmod +x /usr/bin/wait_for_link.sh

# Executed platform specific initialization tasks.
if [ -x /usr/share/sonic/platform/platform-init ]; then
    /usr/share/sonic/platform/platform-init
fi

# Executed HWSKU specific initialization tasks.
if [ -x /usr/share/sonic/hwsku/hwsku-init ]; then
    /usr/share/sonic/hwsku/hwsku-init
fi

# Start arp_update and NDP proxy daemon when VLAN exists
if [ "$VLAN" != "" ]; then
    cp /usr/share/sonic/templates/arp_update.conf /etc/supervisor/conf.d/
    cp /usr/share/sonic/templates/ndppd.conf /etc/supervisor/conf.d/
fi

if [ "$SUBTYPE" == "DualToR" ]; then
    cp /usr/share/sonic/templates/tunnel_packet_handler.conf /etc/supervisor/conf.d/
fi

exec /usr/local/bin/supervisord
