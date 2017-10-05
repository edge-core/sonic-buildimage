#!/usr/bin/env bash

# Remove stale rsyslog PID file if it exists
rm -f /var/run/rsyslogd.pid

# Start rsyslog
supervisorctl start rsyslogd

# Wait for all interfaces to come up before starting the DHCP relay agent(s)
/usr/bin/wait_for_intf.sh

# Start the DHCP relay agent(s)
supervisorctl start isc-dhcp-relay:*
