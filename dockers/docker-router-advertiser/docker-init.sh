#!/usr/bin/env bash

mkdir -p /etc/supervisor/conf.d
sonic-cfggen -d -t /usr/share/sonic/templates/docker-router-advertiser.supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf

# Generate /etc/radvd.conf config file
sonic-cfggen -d -t /usr/share/sonic/templates/radvd.conf.j2 > /etc/radvd.conf

# Generate the script that waits for pertinent interfaces to come up and make it executable
sonic-cfggen -d -t /usr/share/sonic/templates/wait_for_intf.sh.j2 > /usr/bin/wait_for_intf.sh
chmod +x /usr/bin/wait_for_intf.sh

exec /usr/bin/supervisord
