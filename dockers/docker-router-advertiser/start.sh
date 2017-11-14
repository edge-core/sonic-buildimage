#!/usr/bin/env bash

# Generate /etc/radvd.conf config file
sonic-cfggen -d -t /usr/share/sonic/templates/radvd.conf.j2 > /etc/radvd.conf

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# Start the router advertiser
supervisorctl start radvd
