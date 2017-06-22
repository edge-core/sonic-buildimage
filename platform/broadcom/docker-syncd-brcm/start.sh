#!/usr/bin/env bash

PLATFORM_DIR=/usr/share/sonic/platform

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

supervisorctl start syncd

# If this platform has an initialization file for the Broadcom LED microprocessor, load it
if [ -r ${PLATFORM_DIR}/led_proc_init.soc ]; then
    # Wait until syncd has created the socket for bcmcmd to connect to
    while true; do
        if [ -e /var/run/sswsyncd/sswsyncd.socket ]; then
            break
        fi
        sleep 1
    done

    /usr/bin/bcmcmd -t 60 "rcload ${PLATFORM_DIR}/led_proc_init.soc"
fi

