#!/bin/bash

mkdir -p /etc/frr
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/bgpd.conf.j2 >/etc/frr/bgpd.conf
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/zebra.conf.j2 >/etc/frr/zebra.conf

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/isolate.j2 >/usr/sbin/bgp-isolate
chown root:root /usr/sbin/bgp-isolate
chmod 0755 /usr/sbin/bgp-isolate

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/unisolate.j2 >/usr/sbin/bgp-unisolate
chown root:root /usr/sbin/bgp-unisolate
chmod 0755 /usr/sbin/bgp-unisolate

# If there's an integrated-config file, go ahead and remote it
if [ -f /etc/frr/frr.conf ]; then
    rm -rf /etc/frr/frr.conf
fi

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status
