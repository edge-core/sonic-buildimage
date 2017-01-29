#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/rsyslog.yml -t /etc/sonic/templates/rsyslog.conf.j2 >/etc/rsyslog.conf
