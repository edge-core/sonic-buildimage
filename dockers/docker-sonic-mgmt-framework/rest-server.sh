#!/usr/bin/env bash

# Startup script for SONiC Management REST Server

SERVER_PORT=
LOG_LEVEL=
CLIENT_AUTH=
SERVER_CRT=
SERVER_KEY=
CA_CERT=

# Read basic server settings from REST_SERVER|default entry
HAS_REST_CONFIG=$(sonic-cfggen -d -v "1 if REST_SERVER and REST_SERVER['default']")
if [ "$HAS_REST_CONFIG" == "1" ]; then
    SERVER_PORT=$(sonic-cfggen -d -v "REST_SERVER['default']['port']")
    CLIENT_AUTH=$(sonic-cfggen -d -v "REST_SERVER['default']['client_auth']")
    LOG_LEVEL=$(sonic-cfggen -d -v "REST_SERVER['default']['log_level']")
fi

# Read certificate file paths from DEVICE_METADATA|x509 entry.
HAS_X509_CONFIG=$(sonic-cfggen -d -v "1 if DEVICE_METADATA and DEVICE_METADATA['x509']")
if [ "$HAS_X509_CONFIG" == "1" ]; then
    SERVER_CRT=$(sonic-cfggen -d -v "DEVICE_METADATA['x509']['server_crt']")
    SERVER_KEY=$(sonic-cfggen -d -v "DEVICE_METADATA['x509']['server_key']")
    CA_CRT=$(sonic-cfggen -d -v "DEVICE_METADATA['x509']['ca_crt']")
fi

# Create temporary server certificate if they not configured in ConfigDB
if [ -z $SERVER_CRT ] && [ -z $SERVER_KEY ]; then
    echo "Generating temporary TLS server certificate ..."
    (cd /tmp && /usr/sbin/generate_cert --host="localhost,127.0.0.1")
    SERVER_CRT=/tmp/cert.pem
    SERVER_KEY=/tmp/key.pem
fi


REST_SERVER_ARGS="-ui /rest_ui -logtostderr"
[ ! -z $SERVER_PORT ] && REST_SERVER_ARGS+=" -port $SERVER_PORT"
[ ! -z $LOG_LEVEL   ] && REST_SERVER_ARGS+=" -v $LOG_LEVEL"
[ ! -z $CLIENT_AUTH ] && REST_SERVER_ARGS+=" -client_auth $CLIENT_AUTH"
[ ! -z $SERVER_CRT  ] && REST_SERVER_ARGS+=" -cert $SERVER_CRT"
[ ! -z $SERVER_KEY  ] && REST_SERVER_ARGS+=" -key $SERVER_KEY"
[ ! -z $CA_CRT      ] && REST_SERVER_ARGS+=" -cacert $CA_CRT"

echo "REST_SERVER_ARGS = $REST_SERVER_ARGS"


export CVL_SCHEMA_PATH=/usr/sbin/schema

exec /usr/sbin/rest_server ${REST_SERVER_ARGS}
