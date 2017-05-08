#!/usr/bin/env bash
#
# Based off /etc/init.d/isc-dhcp-relay
#

# Read init script configuration (interfaces the daemon should listen on
# and the DHCP server we should forward requests to.)
[ -f /etc/default/isc-dhcp-relay ] && . /etc/default/isc-dhcp-relay

# Build command line for interfaces (will be passed to dhrelay below.)
IFCMD=""
if test "$INTERFACES" != ""; then
        for I in $INTERFACES; do
                IFCMD=${IFCMD}"-i "${I}" "
        done
fi

exec /usr/sbin/dhcrelay -d -q ${OPTIONS} ${IFCMD} ${SERVERS}

