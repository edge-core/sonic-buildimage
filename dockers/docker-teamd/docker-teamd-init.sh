#!/usr/bin/env bash

TEAMD_CONF_PATH="/etc/teamd"

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

for pc in `sonic-cfggen -d -v "PORTCHANNEL.keys() | join(' ') if PORTCHANNEL"`; do
    sonic-cfggen -d -a '{"pc":"'$pc'","hwaddr":"'$MAC_ADDRESS'"}' -t /usr/share/sonic/templates/teamd.j2 > $TEAMD_CONF_PATH/$pc.conf
    # bring down all member ports before starting teamd
    for member in $(sonic-cfggen -d -v "PORTCHANNEL['$pc']['members'] | join(' ')" ); do
        if [ -L /sys/class/net/$member ]; then
            ip link set $member down
        fi
    done
done

# Create a Python dictionary where the key is the Jinja2 variable name
# "lags" and the value is a list of dctionaries containing the name of
# the LAG and the path of the LAG config file. Then output this in
# JSON format, as we will pass it to sonic-cfggen as additional data
# below for generating the supervisord config file.
# Example output: {"lags": [{"name": "PortChannel1", "file": "/etc/teamd/PortChannel1.conf"}, {"name": "PortChannel2", "file": "/etc/teamd/PortChannel2.conf"}]}
LAG_INFO_DICT=$(python -c "import json,os,sys; lags_dict = {}; lags_dict['lags'] = [{'name': os.path.basename(file).split('.')[0], 'file': os.path.join('${TEAMD_CONF_PATH}', file)} for file in sorted(os.listdir('${TEAMD_CONF_PATH}'))]; sys.stdout.write(json.dumps(lags_dict))")

# Generate supervisord config file
mkdir -p /etc/supervisor/conf.d/
sonic-cfggen -d -a "${LAG_INFO_DICT}" -t /usr/share/sonic/templates/docker-teamd.supervisord.conf.j2 > /etc/supervisor/conf.d/docker-teamd.supervisord.conf

# The Docker container should start this script as PID 1, so now that we
# have generated the proper supervisord configuration, we exec supervisord
# so that it runs as PID 1 for the duration of the container's lifetime
exec /usr/bin/supervisord
