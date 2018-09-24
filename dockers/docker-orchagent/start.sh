#!/usr/bin/env bash

mkdir -p /etc/swss/config.d/

sonic-cfggen -d -t /usr/share/sonic/templates/switch.json.j2 > /etc/swss/config.d/switch.json
sonic-cfggen -d -t /usr/share/sonic/templates/ipinip.json.j2 > /etc/swss/config.d/ipinip.json
sonic-cfggen -d -t /usr/share/sonic/templates/ports.json.j2 > /etc/swss/config.d/ports.json

# Executed HWSKU specific initialization tasks.
if [ -x /usr/share/sonic/hwsku/hwsku-init ]; then
    /usr/share/sonic/hwsku/hwsku-init
fi

export platform=`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start orchagent

supervisorctl start portsyncd

supervisorctl start intfsyncd

supervisorctl start neighsyncd

supervisorctl start swssconfig

supervisorctl start vlanmgrd

supervisorctl start intfmgrd

supervisorctl start portmgrd

supervisorctl start buffermgrd

supervisorctl start enable_counters

supervisorctl start vrfmgrd

# Start arp_update when VLAN exists
VLAN=`sonic-cfggen -d -v 'VLAN.keys() | join(" ") if VLAN'`
if [ "$VLAN" != "" ]; then
    supervisorctl start arp_update
fi
