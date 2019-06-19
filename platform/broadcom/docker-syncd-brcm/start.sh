#!/usr/bin/env bash

PLATFORM_DIR=/usr/share/sonic/platform
HWSKU_DIR=/usr/share/sonic/hwsku

SYNCD_SOCKET_FILE=/var/run/sswsyncd/sswsyncd.socket

# Function: wait until syncd has created the socket for bcmcmd to connect to
wait_syncd() {
    while true; do
        if [ -e ${SYNCD_SOCKET_FILE} ]; then
            break
        fi
        sleep 1
    done

    # wait until bcm sdk is ready to get a request
    counter=0
    while true; do
        /usr/bin/bcmcmd -t 1 "show unit" | grep BCM >/dev/null 2>&1
        rv=$?
        if [ $rv -eq 0 ]; then
            break
        fi
        counter=$((counter+1))
        if [ $counter -ge 60 ]; then
            echo "syncd is not ready to take commands after $counter re-tries; Exiting!"
            break
        fi
        sleep 1
    done
}


# Remove stale files if they exist
rm -f /var/run/rsyslogd.pid
rm -f ${SYNCD_SOCKET_FILE}

supervisorctl start rsyslogd

mkdir -p /etc/sai.d/

# Create/Copy the sai.profile to /etc/sai.d/sai.profile
if [ -f $HWSKU_DIR/sai.profile.j2 ]; then
    sonic-cfggen -d -t $HWSKU_DIR/sai.profile.j2 > /etc/sai.d/sai.profile
else
    if [ -f $HWSKU_DIR/sai.profile ]; then
        cp $HWSKU_DIR/sai.profile /etc/sai.d/sai.profile
    fi
fi

supervisorctl start syncd

# If this platform has an initialization file for the Broadcom LED microprocessor, load it
if [[ -r ${PLATFORM_DIR}/led_proc_init.soc && ! -f /var/warmboot/warm-starting ]]; then
    wait_syncd
    supervisorctl start ledinit
fi
