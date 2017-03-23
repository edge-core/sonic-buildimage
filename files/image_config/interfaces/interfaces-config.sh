#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /usr/share/sonic/templates/interfaces.j2 >/etc/network/interfaces
service networking restart
