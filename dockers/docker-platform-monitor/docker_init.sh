#!/usr/bin/env bash

# Generate supervisord config file and the start.sh scripts
mkdir -p /etc/supervisor/conf.d/


HAVE_SENSORS_CONF=0
HAVE_FANCONTROL_CONF=0

if [ -e /usr/share/sonic/platform/sensors.conf ]; then
    HAVE_SENSORS_CONF=1
fi

if [ -e /usr/share/sonic/platform/fancontrol ]; then
    HAVE_FANCONTROL_CONF=1
fi

confvar="{\"HAVE_SENSORS_CONF\":$HAVE_SENSORS_CONF, \"HAVE_FANCONTROL_CONF\":$HAVE_FANCONTROL_CONF}"

if [ -e /usr/share/sonic/platform/pmon_daemon_control.json ];
then
    sonic-cfggen -j /usr/share/sonic/platform/pmon_daemon_control.json -a "$confvar" -t /usr/share/sonic/templates/docker-pmon.supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf
else
    sonic-cfggen -a "$confvar" -t /usr/share/sonic/templates/docker-pmon.supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf
fi

# If this platform has an lm-sensors config file, copy it to it's proper place.
if [ -e /usr/share/sonic/platform/sensors.conf ]; then
    mkdir -p /etc/sensors.d
    /bin/cp -f /usr/share/sonic/platform/sensors.conf /etc/sensors.d/
fi

# If this platform has a fancontrol config file, copy it to it's proper place
# and start fancontrol
if [ -e /usr/share/sonic/platform/fancontrol ]; then
    # Remove stale pid file if it exists
    rm -f /var/run/fancontrol.pid

    /bin/cp -f /usr/share/sonic/templates/fancontrol.conf /etc/supervisord/conf.d/
fi

exec /usr/bin/supervisord
