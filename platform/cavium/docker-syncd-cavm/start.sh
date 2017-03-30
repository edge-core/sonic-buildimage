#!/bin/bash

export XP_ROOT=/usr/bin/

rm -f /var/run/rsyslogd.pid
service rsyslog start

while true; do

    # Check if redis-server starts

    result=$(redis-cli ping)

    if [ "$result" == "PONG" ]; then

        redis-cli FLUSHALL
        syncd -p /etc/ssw/AS7512/profile.ini -N
        break

    fi

    sleep 1

done
