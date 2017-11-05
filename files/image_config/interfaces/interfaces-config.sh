#!/bin/bash

SONIC_ASIC_TYPE=$(sonic-cfggen -y /etc/sonic/sonic_version.yml -v asic_type)
SYSTEM_MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')

# Align last byte of MAC if necessary
if [ "$SONIC_ASIC_TYPE" == "mellanox" -o "$SONIC_ASIC_TYPE" == "centec" ]; then
    last_byte=$(python -c "print '$SYSTEM_MAC_ADDRESS'[-2:]")
    aligned_last_byte=$(python -c "print format(int(int('$last_byte', 16) & 0b11000000), '02x')")  # put mask and take away the 0x prefix
    SYSTEM_MAC_ADDRESS=$(python -c "print '$SYSTEM_MAC_ADDRESS'[:-2] + '$aligned_last_byte'")      # put aligned byte into the end of MAC
fi

sonic-cfggen -d -a '{"hwaddr":"'$SYSTEM_MAC_ADDRESS'"}' -t /usr/share/sonic/templates/interfaces.j2 > /etc/network/interfaces

# Also store the system mac to configDB switch table. User configured switch_mac is not supported for now.
/usr/bin/docker exec database redis-cli -n 4 hset SWITCH\|SWITCH_ATTR switch_mac $SYSTEM_MAC_ADDRESS

[ -f /var/run/dhclient.eth0.pid ] && kill `cat /var/run/dhclient.eth0.pid` && rm -f /var/run/dhclient.eth0.pid

systemctl restart networking

ifdown lo && ifup lo
