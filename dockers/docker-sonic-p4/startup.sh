#!/bin/bash

echo "Start rsyslog"
service rsyslog start

echo "Start redis server"
service redis-server start

echo "Veth setup"
/usr/share/bmpd/tools/veth_setup.sh  > /tmp/veth_setup.log 2>&1

echo "Disable IPv6"
/usr/share/bmpd/tools/veth_disable_ipv6.sh > /tmp/veth_disable.log 2>&1

echo "Start BMV2"
/run_bm.sh > /tmp/run_bm.log 2>&1 &
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
