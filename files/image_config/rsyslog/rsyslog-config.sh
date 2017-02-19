#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/rsyslog.yml -t /usr/share/sonic/templates/rsyslog.conf.j2 >/etc/rsyslog.conf
