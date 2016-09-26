#!/bin/bash

export XP_ROOT=/usr/bin/

service rsyslog start
syncd -p /etc/ssw/AS7512/profile.ini -N
