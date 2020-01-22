#!/usr/bin/env bash

# Wait until redis starts
until [[ $(redis-cli ping | grep -c PONG) -gt 0 ]]; do
  sleep 1;
done

# If there is a config db dump file, load it
if [ -r /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/config_db.json --write-to-db
fi

sonic-db-cli CONFIG_DB SET "CONFIG_DB_INITIALIZED" "1"
