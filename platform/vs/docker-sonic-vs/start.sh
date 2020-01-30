#!/bin/bash -e

# generate configuration

PLATFORM=x86_64-kvm_x86_64-r0
HWSKU=Force10-S6000

ln -sf /usr/share/sonic/device/$PLATFORM/$HWSKU /usr/share/sonic/hwsku

[ -d /etc/sonic ] || mkdir -p /etc/sonic

SYSTEM_MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
sonic-cfggen -a '{"DEVICE_METADATA":{"localhost": {"mac": "'$SYSTEM_MAC_ADDRESS'"}}}' --print-data > /etc/sonic/init_cfg.json

if [ -f /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/config_db.json -j /etc/sonic/init_cfg.json --print-data > /tmp/config_db.json
    mv /tmp/config_db.json /etc/sonic/config_db.json
else
    # generate and merge buffers configuration into config file
    sonic-cfggen -t /usr/share/sonic/hwsku/buffers.json.j2 > /tmp/buffers.json
    sonic-cfggen -j /etc/sonic/init_cfg.json -t /usr/share/sonic/hwsku/qos.json.j2 > /tmp/qos.json
    sonic-cfggen -p /usr/share/sonic/hwsku/port_config.ini -k $HWSKU --print-data > /tmp/ports.json
    sonic-cfggen -j /etc/sonic/init_cfg.json -j /tmp/buffers.json -j /tmp/qos.json -j /tmp/ports.json --print-data > /etc/sonic/config_db.json
fi

mkdir -p /etc/swss/config.d/

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

mkdir -p /var/run/redis/sonic-db
cp /etc/default/sonic-db/database_config.json /var/run/redis/sonic-db/

supervisorctl start redis-server

/usr/bin/configdb-load.sh

supervisorctl start syncd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start neighsyncd

supervisorctl start teamsyncd

supervisorctl start fpmsyncd

supervisorctl start teammgrd

supervisorctl start vrfmgrd

supervisorctl start portmgrd

supervisorctl start intfmgrd

supervisorctl start vlanmgrd

supervisorctl start zebra

supervisorctl start staticd

supervisorctl start buffermgrd

supervisorctl start nbrmgrd

supervisorctl start vxlanmgrd

supervisorctl start sflowmgrd

supervisorctl start natmgrd

supervisorctl start natsyncd

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
if [ "$VLAN" != "" ]; then
    supervisorctl start arp_update
fi
