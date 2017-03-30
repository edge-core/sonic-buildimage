#!/bin/bash

mkdir -p /etc/sensors.d
if [ -e /usr/share/sonic/platform/sensors.conf ]
then
  /bin/cp -rf /usr/share/sonic/platform/sensors.conf /etc/sensors.d/
fi

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

rm -f /var/run/rsyslogd.pid
