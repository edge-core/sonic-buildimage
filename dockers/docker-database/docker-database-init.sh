#!/usr/bin/env bash

mkdir -p /var/run/redis/sonic-db
if [ -f /etc/sonic/database_config.json ]; then
    cp /etc/sonic/database_config.json /var/run/redis/sonic-db
else
    cp /etc/default/sonic-db/database_config.json /var/run/redis/sonic-db
fi

mkdir -p /etc/supervisor/conf.d/
# generate all redis server supervisord configuration file
sonic-cfggen -j /var/run/redis/sonic-db/database_config.json -t /usr/share/sonic/templates/supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf

exec /usr/bin/supervisord
