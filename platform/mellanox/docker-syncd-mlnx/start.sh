#!/usr/bin/env bash

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start syncd

supervisorctl start mlnx-sfpd

BOOT_TYPE="$(cat /proc/cmdline | grep -o 'SONIC_BOOT_TYPE=\S*' | cut -d'=' -f2)"
if [[ x"$BOOT_TYPE" == x"fastfast" ]] && [[ -f /var/warmboot/issu_started ]]; then
    rm -f /var/warmboot/issu_started
    /usr/bin/ffb &>/dev/null &
fi
