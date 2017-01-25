#!/bin/bash

mkdir -p /etc/teamd

for pc in `sonic-cfggen -m /etc/sonic/minigraph.xml --var-keys minigraph_portchannel_interfaces`; do
  sonic-cfggen -m /etc/sonic/minigraph.xml -a '{"pc":"'$pc'"}' -t /etc/swss/teamd/teamd.j2 >/etc/teamd/$pc.conf
done

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" >/var/sonic/config_status

