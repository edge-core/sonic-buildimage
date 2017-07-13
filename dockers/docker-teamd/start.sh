#!/usr/bin/env bash

TEAMD_CONF_PATH=/etc/teamd

rm -rf $TEAMD_CONF_PATH
mkdir -p $TEAMD_CONF_PATH

SONIC_ASIC_TYPE=$(sonic-cfggen -y /etc/sonic/sonic_version.yml -v asic_type)
MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')

# Align last byte
if [ "$SONIC_ASIC_TYPE" == "mellanox" -o "$SONIC_ASIC_TYPE" == "centec" ]; then
    last_byte=$(python -c "print '$MAC_ADDRESS'[-2:]")
    aligned_last_byte=$(python -c "print format(int(int('$last_byte', 16) & 0b11000000), '02x')")  # put mask and take away the 0x prefix
    MAC_ADDRESS=$(python -c "print '$MAC_ADDRESS'[:-2] + '$aligned_last_byte'")                    # put aligned byte into the end of MAC
fi

for pc in `sonic-cfggen -m /etc/sonic/minigraph.xml -v "minigraph_portchannels.keys() | join(' ')"`; do
    sonic-cfggen -m /etc/sonic/minigraph.xml -a '{"pc":"'$pc'","hwaddr":"'$MAC_ADDRESS'"}' -t /usr/share/sonic/templates/teamd.j2 > $TEAMD_CONF_PATH/$pc.conf
done

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start teamd
