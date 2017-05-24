#!/usr/bin/env bash

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

# mlnx-fw-upgrade.sh will exit if firmware was actually upgraded
# or if some error occurs
. mlnx-fw-upgrade.sh

supervisorctl start syncd
