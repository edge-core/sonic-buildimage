#!/bin/bash -e

# generate configuration

export PLATFORM=x86_64-kvm_x86_64-r0
export HWSKU=Force10-S6000

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

if [[ -f /usr/share/sonic/virtual_chassis/default_config.json ]]; then
    CHASS_CFG="-j /usr/share/sonic/virtual_chassis/default_config.json"
fi

SYSTEM_MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
if [ -f /etc/sonic/init_cfg.json ]; then
    sonic-cfggen -j /etc/sonic/init_cfg.json -a '{"DEVICE_METADATA":{"localhost": {"mac": "'$SYSTEM_MAC_ADDRESS'"}}}' $CHASS_CFG --print-data > /tmp/init_cfg.json
    mv /tmp/init_cfg.json /etc/sonic/init_cfg.json
else
    sonic-cfggen -a '{"DEVICE_METADATA":{"localhost": {"mac": "'$SYSTEM_MAC_ADDRESS'"}}}' $CHASS_CFG --print-data > /etc/sonic/init_cfg.json
fi

if [ -f /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/init_cfg.json -j /etc/sonic/config_db.json --print-data > /tmp/config_db.json
    mv /tmp/config_db.json /etc/sonic/config_db.json
else
    # generate and merge buffers configuration into config file
    sonic-cfggen -k $HWSKU -p /usr/share/sonic/device/$PLATFORM/platform.json -t /usr/share/sonic/hwsku/buffers.json.j2 > /tmp/buffers.json
    sonic-cfggen -j /etc/sonic/init_cfg.json -t /usr/share/sonic/hwsku/qos.json.j2 > /tmp/qos.json
    sonic-cfggen -p /usr/share/sonic/device/$PLATFORM/platform.json -k $HWSKU --print-data > /tmp/ports.json
    # change admin_status from up to down; Test cases dependent
    sed -i "s/up/down/g" /tmp/ports.json
    sonic-cfggen -j /etc/sonic/init_cfg.json -j /tmp/buffers.json -j /tmp/qos.json -j /tmp/ports.json --print-data > /etc/sonic/config_db.json
fi

mkdir -p /etc/swss/config.d/

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisord_cfg="/etc/supervisor/conf.d/supervisord.conf"
chassis_cfg_file="/usr/share/sonic/virtual_chassis/default_config.json"
chassis_cfg_file_default="/etc/default/sonic-db/default_chassis_cfg.json"
host_template="/usr/share/sonic/templates/hostname.j2"
db_cfg_file="/var/run/redis/sonic-db/database_config.json"
db_cfg_file_tmp="/var/run/redis/sonic-db/database_config.json.tmp"

if [ -r "$chassis_cfg_file" ]; then
   echo $(sonic-cfggen -j $chassis_cfg_file -t $host_template) >> /etc/hosts
else
   chassis_cfg_file="$chassis_cfg_file_default"
   echo "10.8.1.200 redis_chassis.server" >> /etc/hosts
fi

mkdir -p /var/run/redis/sonic-db
cp /etc/default/sonic-db/database_config.json /var/run/redis/sonic-db/

supervisorctl start redis-server

start_chassis_db=`sonic-cfggen -v DEVICE_METADATA.localhost.start_chassis_db -y $chassis_cfg_file`
if [[ "$HOSTNAME" == *"supervisor"* ]] || [ "$start_chassis_db" == "1" ]; then
   supervisorctl start redis-chassis
   python /usr/bin/chassis_db.py
fi

conn_chassis_db=`sonic-cfggen -v DEVICE_METADATA.localhost.connect_to_chassis_db -y $chassis_cfg_file`
if [ "$start_chassis_db" != "1" ] && [ "$conn_chassis_db" != "1" ]; then
   cp $db_cfg_file $db_cfg_file_tmp
   remove_chassisdb_config -j $db_cfg_file_tmp
   cp $db_cfg_file_tmp $db_cfg_file
fi


/usr/bin/configdb-load.sh

supervisorctl start syncd

supervisorctl start portsyncd

supervisorctl start orchagent

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
