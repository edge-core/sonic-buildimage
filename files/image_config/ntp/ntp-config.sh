#!/bin/bash

sonic-cfggen -d -t /usr/share/sonic/templates/ntp.conf.j2 >/etc/ntp.conf

systemctl restart ntp
