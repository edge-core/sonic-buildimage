#!/bin/bash

echo "Set onie_platform to x86_64-barefoot_p4-r0"
export onie_platform=x86_64-barefoot_p4-r0

echo "Start rsyslog"
rm -f /var/run/rsyslogd.pid
service rsyslog start

echo "Start redis server"
service redis-server start &
sleep 3

redis-cli flushall

echo "Veth setup"
veth_setup.sh  > /tmp/veth_setup.log 2>&1

echo "Start BMV2"
/scripts/run_bm.sh > /tmp/run_bm.log 2>&1 &
sleep 15

redis-cli -n 1 set LOGLEVEL DEBUG

echo "Start Syncd"
syncd -N > /tmp/syncd.log 2>&1  &
sleep 10

echo "Start Orchagent"
orchagent $* > /tmp/orchagent.log 2>&1 &
sleep 10

echo "Start Portsyncd"
portsyncd -p /port_config.ini > /tmp/portsyncd.log 2>&1 &

echo "Start Intfsync"
intfsyncd > /tmp/intfsyncd.log 2>&1 &

echo "Start Neighsyncd"
neighsyncd > /tmp/neighsyncd.log 2>&1 &

echo "Start Fpmsyncd"
fpmsyncd > /tmp/fpmsyncd.log 2>&1 &
