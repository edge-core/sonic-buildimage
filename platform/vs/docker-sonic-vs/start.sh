#!/bin/bash -e

# generate configuration

PLATFORM=x86_64-kvm_x86_64-r0
HWSKU=Force10-S6000

ln -sf /usr/share/sonic/device/$PLATFORM/$HWSKU /usr/share/sonic/hwsku

pushd /usr/share/sonic/hwsku

# filter available front panel ports in lanemap.ini
[ -f lanemap.ini.orig ] || cp lanemap.ini lanemap.ini.orig
for p in $(ip link show | grep -oE "eth[0-9]+" | grep -v eth0); do
    grep ^$p: lanemap.ini.orig
done > lanemap.ini

# filter available sonic front panel ports in port_config.ini
[ -f port_config.ini.orig ] || cp port_config.ini port_config.ini.orig
grep ^# port_config.ini.orig > port_config.ini
for lanes in $(awk -F ':' '{print $2}' lanemap.ini); do
    grep -E "\s$lanes\s" port_config.ini.orig
done >> port_config.ini

popd

[ -d /etc/sonic ] || mkdir -p /etc/sonic

SYSTEM_MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
sonic-cfggen -a '{"DEVICE_METADATA":{"localhost": {"mac": "'$SYSTEM_MAC_ADDRESS'"}}}' --print-data > /etc/sonic/init_cfg.json

if [ -f /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/init_cfg.json -j /etc/sonic/config_db.json --print-data > /tmp/config_db.json
    mv /tmp/config_db.json /etc/sonic/config_db.json
else
    # generate and merge buffers configuration into config file
    sonic-cfggen -k $HWSKU -p /usr/share/sonic/hwsku/port_config.ini -t /usr/share/sonic/hwsku/buffers.json.j2 > /tmp/buffers.json
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
