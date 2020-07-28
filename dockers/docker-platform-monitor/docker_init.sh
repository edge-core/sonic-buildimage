#!/usr/bin/env bash

# Generate supervisord config file and the start.sh scripts
mkdir -p /etc/supervisor/conf.d/

SENSORS_CONF_FILE="/usr/share/sonic/platform/sensors.conf"
FANCONTROL_CONF_FILE="/usr/share/sonic/platform/fancontrol"

HAVE_SENSORS_CONF=0
HAVE_FANCONTROL_CONF=0

if [ -e $SENSORS_CONF_FILE ]; then
    HAVE_SENSORS_CONF=1
fi

if [ -e $FANCONTROL_CONF_FILE ]; then
    HAVE_FANCONTROL_CONF=1
fi

confvar="{\"HAVE_SENSORS_CONF\":$HAVE_SENSORS_CONF, \"HAVE_FANCONTROL_CONF\":$HAVE_FANCONTROL_CONF}"

if [ -e /usr/share/sonic/platform/pmon_daemon_control.json ];
then
    sonic-cfggen -j /usr/share/sonic/platform/pmon_daemon_control.json -a "$confvar" -t /usr/share/sonic/templates/docker-pmon.supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf
else
    sonic-cfggen -a "$confvar" -t /usr/share/sonic/templates/docker-pmon.supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf
fi

# If this platform has an lm-sensors config file, copy it to its proper place
if [ $HAVE_SENSORS_CONF -eq 1 ]; then
    mkdir -p /etc/sensors.d
    /bin/cp -f $SENSORS_CONF_FILE /etc/sensors.d/
fi

# If this platform has a fancontrol config file, copy it to its proper place
if [ $HAVE_FANCONTROL_CONF -eq 1 ]; then
    # Remove stale pid file if it exists
    rm -f /var/run/fancontrol.pid

    /bin/cp -f $FANCONTROL_CONF_FILE /etc/
fi

exec /usr/bin/supervisord
