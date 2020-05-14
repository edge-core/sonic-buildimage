#!/usr/bin/env bash

mkdir -p /etc/frr
mkdir -p /etc/supervisor/conf.d

sonic-cfggen -d -t /usr/share/sonic/templates/supervisord/supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf

CONFIG_TYPE=`sonic-cfggen -d -v 'DEVICE_METADATA["localhost"]["docker_routing_config_mode"]'`
if [ -z "$CONFIG_TYPE" ] || [ "$CONFIG_TYPE" == "separated" ]; then
    sonic-cfggen -d -t /usr/share/sonic/templates/bgpd/bgpd.conf.j2 -y /etc/sonic/constants.yml > /etc/frr/bgpd.conf
    sonic-cfggen -d -t /usr/share/sonic/templates/zebra/zebra.conf.j2 > /etc/frr/zebra.conf
    sonic-cfggen -d -t /usr/share/sonic/templates/staticd/staticd.conf.j2 > /etc/frr/staticd.conf
    echo "no service integrated-vtysh-config" > /etc/frr/vtysh.conf
    rm -f /etc/frr/frr.conf
elif [ "$CONFIG_TYPE" == "unified" ]; then
    sonic-cfggen -d -y /etc/sonic/constants.yml -t /usr/share/sonic/templates/frr.conf.j2 >/etc/frr/frr.conf
    echo "service integrated-vtysh-config" > /etc/frr/vtysh.conf
    rm -f /etc/frr/bgpd.conf /etc/frr/zebra.conf /etc/frr/staticd.conf
fi

chown -R frr:frr /etc/frr/

sonic-cfggen -d -t /usr/share/sonic/templates/isolate.j2 > /usr/sbin/bgp-isolate
chown root:root /usr/sbin/bgp-isolate
chmod 0755 /usr/sbin/bgp-isolate

sonic-cfggen -d -t /usr/share/sonic/templates/unisolate.j2 > /usr/sbin/bgp-unisolate
chown root:root /usr/sbin/bgp-unisolate
chmod 0755 /usr/sbin/bgp-unisolate

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

exec /usr/bin/supervisord
