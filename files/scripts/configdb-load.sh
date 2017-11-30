#!/usr/bin/env bash

# Wait until redis starts
while true; do
    if [ `redis-cli ping` == "PONG" ]; then
        break
    fi
    sleep 1
done

# If there is a config db dump file, load it
if [ -r /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/config_db.json --write-to-db
fi

echo -en "SELECT 4\nSET CONFIG_DB_INITIALIZED true" | redis-cli

