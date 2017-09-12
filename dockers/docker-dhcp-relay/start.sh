#!/usr/bin/env bash

# Create isc-dhcp-relay config file
sonic-cfggen -d -t /usr/share/sonic/templates/isc-dhcp-relay.j2 > /etc/default/isc-dhcp-relay

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# Wait for all interfaces to come up before starting the DHCP relay
sonic-cfggen -d -t /usr/share/sonic/templates/wait_for_intf.sh.j2 > /usr/bin/wait_for_intf.sh
chmod +x /usr/bin/wait_for_intf.sh
/usr/bin/wait_for_intf.sh

# Start the DHCP relay
supervisorctl start isc-dhcp-relay
