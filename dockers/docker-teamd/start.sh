#!/usr/bin/env bash

rm -f /var/run/rsyslogd.pid
rm -f /var/run/teamd/*

mkdir -p /var/warmboot/teamd

supervisorctl start rsyslogd

supervisorctl start teammgrd

supervisorctl start teamsyncd
