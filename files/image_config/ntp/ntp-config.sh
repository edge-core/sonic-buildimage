#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/ntp.yml -t /usr/share/sonic/templates/ntp.conf.j2 >/etc/ntp.conf
