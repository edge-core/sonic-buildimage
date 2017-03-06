#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/ntp.conf.j2 >/etc/ntp.conf
