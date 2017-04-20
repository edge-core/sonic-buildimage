#!/bin/bash

rm -f /var/run/rsyslogd.pid
service rsyslog start
service frr start
fpmsyncd &
