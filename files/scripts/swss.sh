#!/bin/bash

start() {
    # Wait for redis server start before database clean
    until [[ $(/usr/bin/docker exec database redis-cli ping | grep -c PONG) -gt 0 ]];
        do sleep 1;
    done

    # Wait for configDB initialization
    until [[ $(/usr/bin/docker exec database redis-cli -n 4 GET "CONFIG_DB_INITIALIZED") ]];
        do sleep 1;
    done

    SYSTEM_WARM_START=`/usr/bin/docker exec database redis-cli -n 4 HGET "WARM_RESTART|system" enable`
    SWSS_WARM_START=`/usr/bin/docker exec database redis-cli -n 4 HGET "WARM_RESTART|swss" enable`
    # if warm start enabled, just do swss docker start.
    # Don't flush DB or try to start other modules.
    if [[ "$SYSTEM_WARM_START" == "true" ]] || [[ "$SWSS_WARM_START" == "true" ]]; then
      RESTART_COUNT=`redis-cli -n 6 hget "WARM_RESTART_TABLE|orchagent" restart_count`
      # We have to make sure db data has not been flushed.
      if [[ -n "$RESTART_COUNT" ]]; then
        /usr/bin/swss.sh start
        /usr/bin/swss.sh attach
        return 0
      fi
    fi

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

    SYSTEM_WARM_START=`redis-cli -n 4 hget "WARM_RESTART|system" enable`
    SWSS_WARM_START=`redis-cli -n 4 hget "WARM_RESTART|swss" enable`
    # if warm start enabled, just stop swss docker, then return
    if [[ "$SYSTEM_WARM_START" == "true" ]] || [[ "$SWSS_WARM_START" == "true" ]]; then
        return 0
    fi

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
