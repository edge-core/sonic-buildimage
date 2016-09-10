#!/bin/bash

function clean_up {
    service syncd stop
    service rsyslog stop
    exit
}

trap clean_up SIGTERM SIGKILL

service rsyslog start
service syncd start

read
