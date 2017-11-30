#!/bin/bash -e

# generate configuration

[ -d /etc/sonic ] || mkdir -p /etc/sonic

SYSTEM_MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
sonic-cfggen -a '{"DEVICE_METADATA":{"localhost": {"mac": "'$SYSTEM_MAC_ADDRESS'"}}}' --print-data > /etc/sonic/init_cfg.json

if [ -f /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/config_db.json -j /etc/sonic/init_cfg.json --print-data > /tmp/config_db.json
    mv /tmp/config_db.json /etc/sonic/config_db.json
else
    sonic-cfggen -j /etc/sonic/init_cfg.json --print-data > /etc/sonic/config_db.json
fi

mkdir -p /etc/swss/config.d/

# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/mirror.json.j2 > /etc/swss/config.d/mirror.json
# sonic-cfggen -m /etc/sonic/minigraph.xml -d -t /usr/share/sonic/templates/ports.json.j2 > /etc/swss/config.d/ports.json

# export platform=`sonic-cfggen -v platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

mkdir -p /var/run/redis

supervisorctl start redis-server

/usr/bin/configdb-load.sh

supervisorctl start syncd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start intfsyncd

supervisorctl start neighsyncd

supervisorctl start teamsyncd

supervisorctl start fpmsyncd

supervisorctl start intfmgrd

supervisorctl start vlanmgrd

supervisorctl start zebra

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
if [ "$VLAN" != "" ]; then
    supervisorctl start arp_update
fi
