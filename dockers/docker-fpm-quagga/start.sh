#!/usr/bin/env bash

mkdir -p /etc/quagga
if [ -f /etc/sonic/bgp_admin.yml ]; then
    sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/bgp_admin.yml -y /etc/sonic/deployment_id_asn_map.yml -t /usr/share/sonic/templates/bgpd.conf.j2 > /etc/quagga/bgpd.conf
else
    sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/deployment_id_asn_map.yml -t /usr/share/sonic/templates/bgpd.conf.j2 > /etc/quagga/bgpd.conf
fi
sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/zebra.conf.j2 > /etc/quagga/zebra.conf

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/isolate.j2 > /usr/sbin/bgp-isolate
chown root:root /usr/sbin/bgp-isolate
chmod 0755 /usr/sbin/bgp-isolate

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/unisolate.j2 > /usr/sbin/bgp-unisolate
chown root:root /usr/sbin/bgp-unisolate
chmod 0755 /usr/sbin/bgp-unisolate

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# Quagga has its own monitor process, 'watchquagga'
service quagga start

supervisorctl start fpmsyncd

