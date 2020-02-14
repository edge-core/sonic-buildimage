#!/bin/bash

ifdown --force eth0

sonic-cfggen -d -t /usr/share/sonic/templates/interfaces.j2 > /etc/network/interfaces

[ -f /var/run/dhclient.eth0.pid ] && kill `cat /var/run/dhclient.eth0.pid` && rm -f /var/run/dhclient.eth0.pid

systemctl restart networking
