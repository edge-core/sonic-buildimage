#!/bin/bash

start() {
    # Wait for redis server start before database clean
    until [[ $(/usr/bin/docker exec database redis-cli ping | grep -c PONG) -gt 0 ]]; 
        do sleep 1;
    done

    # Flush DB
    /usr/bin/docker exec database redis-cli -n 0 FLUSHDB
    /usr/bin/docker exec database redis-cli -n 1 FLUSHDB
    /usr/bin/docker exec database redis-cli -n 2 FLUSHDB
    /usr/bin/docker exec database redis-cli -n 5 FLUSHDB
    /usr/bin/docker exec database redis-cli -n 6 FLUSHDB

    # platform specific tasks
    if [ x$sonic_asic_platform == x'mellanox' ]; then
        FAST_BOOT=1
        /usr/bin/mst start
        /usr/bin/mlnx-fw-upgrade.sh
        /etc/init.d/sxdkernel start
        /sbin/modprobe i2c-dev
        /etc/mlnx/mlnx-hw-management start
    elif [ x$sonic_asic_platform == x'cavium' ]; then
        /etc/init.d/xpnet.sh start
    fi

    # start swss and syncd docker 
    /usr/bin/swss.sh start 
    /usr/bin/syncd.sh start
    /usr/bin/swss.sh attach
}

stop() {
    /usr/bin/swss.sh stop
    /usr/bin/syncd.sh stop

    # platform specific tasks
    if [ x$sonic_asic_platform == x'mellanox' ]; then
        /etc/mlnx/mlnx-hw-management stop
        /etc/init.d/sxdkernel stop
        /usr/bin/mst stop
    elif [ x$sonic_asic_platform == x'cavium' ]; then
        /etc/init.d/xpnet.sh stop
        /etc/init.d/xpnet.sh start
    fi
}

case "$1" in
    start|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
