#!/bin/bash

ifdown --force eth0

sonic-cfggen -d -t /usr/share/sonic/templates/interfaces.j2 > /etc/network/interfaces

# Add usb0 interface for bfn platforms
platform=$(sonic-cfggen -H -v 'DEVICE_METADATA["localhost"]["platform"]')
if [[ "$platform" == "x86_64-accton_wedge100bf_32x-r0" || "$platform" == "x86_64-accton_wedge100bf_65x-r0" ]]; then
cat <<'EOF' >> /etc/network/interfaces
# BMC interface
auto usb0
allow-hotplug usb0
iface usb0 inet6 auto
up ifconfig usb0 txqueuelen 64
EOF
fi

[ -f /var/run/dhclient.eth0.pid ] && kill `cat /var/run/dhclient.eth0.pid` && rm -f /var/run/dhclient.eth0.pid

systemctl restart networking

ifdown --force lo
ip addr flush dev lo
ifup lo
