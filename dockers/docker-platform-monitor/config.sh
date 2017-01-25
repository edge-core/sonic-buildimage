#!/bin/bash

mkdir -p /etc/sensors.d

hwsku=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`
/bin/cp -rf /usr/share/sonic/$hwsku/sensors.conf /etc/sensors.d/

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

