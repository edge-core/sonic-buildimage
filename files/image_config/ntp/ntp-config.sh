#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/ntp.yml -t /etc/sonic/templates/ntp.conf.j2 >/etc/ntp.conf
