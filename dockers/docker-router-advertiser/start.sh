#!/usr/bin/env bash

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# Router advertiser should only run on ToR (T0) devices
DEVICE_ROLE=$(sonic-cfggen -d -v "DEVICE_METADATA.localhost.type")
if [[ "$DEVICE_ROLE" != "ToRRouter" && "$DEVICE_ROLE" != "MgmtToRRouter" && "$DEVICE_ROLE" != "EPMS" ]]; then
    echo "Device role is not ToRRouter, MgmtToRRouter, or EPMS. Not starting router advertiser process."
    exit 0
fi

# Generate /etc/radvd.conf config file
sonic-cfggen -d -t /usr/share/sonic/templates/radvd.conf.j2 > /etc/radvd.conf

# Enusre at least one interface is specified in radvd.conf
NUM_IFACES=$(grep -c "^interface " /etc/radvd.conf)
if [ $NUM_IFACES -eq 0 ]; then
    echo "No interfaces specified in radvd.conf. Not starting router advertiser process."
    exit 0
fi

# Generate the script that waits for pertinent interfaces to come up and make it executable
sonic-cfggen -d -t /usr/share/sonic/templates/wait_for_intf.sh.j2 > /usr/bin/wait_for_intf.sh
chmod +x /usr/bin/wait_for_intf.sh

# Wait for pertinent interfaces to come up
/usr/bin/wait_for_intf.sh

# Start the router advertiser
supervisorctl start radvd
