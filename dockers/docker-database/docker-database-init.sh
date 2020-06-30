#!/usr/bin/env bash

# For linux host namespace, in both single and multi ASIC platform use the loopback interface
# For other namespaces, use eth0 interface which is connected to the docker0 bridge in the host.
if [[ $NAMESPACE_ID == "" ]]
then
    INTFC=lo
else
    INTFC=eth0
fi

# Get the ip address of the interface
# if the ip address was not retrieved correctly, put localhost(127.0.0.1) as the default.
host_ip=$(ip -4 -o addr show $INTFC | awk '{print $4}' | cut -d'/' -f1 | head -1)
if [[ $host_ip == "" ]]
then
    host_ip=127.0.0.1
fi

REDIS_DIR=/var/run/redis$NAMESPACE_ID
mkdir -p $REDIS_DIR/sonic-db

if [ -f /etc/sonic/database_config$NAMESPACE_ID.json ]; then
    cp /etc/sonic/database_config$NAMESPACE_ID.json $REDIS_DIR/sonic-db/database_config.json
else
    HOST_IP=$host_ip j2 /usr/share/sonic/templates/database_config.json.j2 > $REDIS_DIR/sonic-db/database_config.json
fi

mkdir -p /etc/supervisor/conf.d/

# copy/generate the database_global.json file if this is global database service in multi asic platform.
if [[ $NAMESPACE_ID == "" ]] && [[ $NAMESPACE_COUNT -gt 1 ]]
then
    if [ -f /etc/sonic/database_global.json ]; then
        cp /etc/sonic/database_global.json $REDIS_DIR/sonic-db/database_global.json
    else
        j2 /usr/share/sonic/templates/database_global.json.j2 > $REDIS_DIR/sonic-db/database_global.json
    fi
fi

# generate all redis server supervisord configuration file
sonic-cfggen -j /var/run/redis/sonic-db/database_config.json -t /usr/share/sonic/templates/supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf

exec /usr/bin/supervisord
