#!/bin/bash

mkdir -p /etc/frr
sonic-cfggen -d -t /usr/share/sonic/templates/frr.conf.j2 >/etc/frr/frr.conf

sonic-cfggen -d -t /usr/share/sonic/templates/isolate.j2 >/usr/sbin/bgp-isolate
chown root:root /usr/sbin/bgp-isolate
chmod 0755 /usr/sbin/bgp-isolate

sonic-cfggen -d -t /usr/share/sonic/templates/unisolate.j2 >/usr/sbin/bgp-unisolate
chown root:root /usr/sbin/bgp-unisolate
chmod 0755 /usr/sbin/bgp-unisolate

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status
