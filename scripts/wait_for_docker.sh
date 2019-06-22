#!/bin/bash

total_time=$1
cnt=0
while [ $cnt -le $total_time ]; do
    docker info 1>/dev/null
    rv=$?
    if [ $rv -eq 0 ]; then
        exit 0
    fi
    sleep 1
    cnt=$((cnt+1))
done

exit 1
