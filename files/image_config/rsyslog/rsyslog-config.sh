#!/bin/bash

sonic-cfggen -d -t /usr/share/sonic/templates/rsyslog.conf.j2 >/etc/rsyslog.conf
systemctl restart rsyslog
