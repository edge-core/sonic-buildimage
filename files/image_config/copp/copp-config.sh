#!/bin/bash

asic_type=$(sonic-cfggen -d -y /etc/sonic/sonic_version.yml --var asic_type)

sonic-cfggen -d -a "{\"asic_type\": \"$asic_type\"}" \
  -t /usr/share/sonic/templates/copp_cfg.j2 > /etc/sonic/copp_cfg.json
