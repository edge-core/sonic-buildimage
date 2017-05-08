#!/usr/bin/env bash

TEAMD_CONF_PATH=/etc/teamd

rm -rf $TEAMD_CONF_PATH
mkdir -p $TEAMD_CONF_PATH

for pc in `sonic-cfggen -m /etc/sonic/minigraph.xml -v "minigraph_portchannels.keys() | join(' ')"`; do
    sonic-cfggen -m /etc/sonic/minigraph.xml -a '{"pc":"'$pc'"}' -t /usr/share/sonic/templates/teamd.j2 > $TEAMD_CONF_PATH/$pc.conf
done

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start teamd

