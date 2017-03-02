#!/bin/bash

service rsyslog start
service quagga start
fpmsyncd &
