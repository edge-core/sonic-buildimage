#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/rsyslog.conf.j2 >/etc/rsyslog.conf
systemctl restart rsyslog
