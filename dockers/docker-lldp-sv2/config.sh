#!/bin/bash

sonic-cfggen -m /etc/sonic/minigraph.xml -t /etc/swss/lldp/lldpd.conf.j2 >/etc/lldpd.conf

