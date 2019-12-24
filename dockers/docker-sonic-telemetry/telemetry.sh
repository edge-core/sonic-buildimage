#!/usr/bin/env bash

# Try to read telemetry and x509 config from ConfigDB.
# Use default value if no valid config exists
X509=`sonic-cfggen -d -v "DEVICE_METADATA['x509']"`
TELEMETRY=`sonic-cfggen -d -v 'TELEMETRY.keys() | join(" ") if TELEMETRY'`

TELEMETRY_ARGS=" -logtostderr"
export CVL_SCHEMA_PATH=/usr/sbin/schema

if [ -n "$X509" ]; then
	SERVER_CRT=`sonic-cfggen -d -v "DEVICE_METADATA['x509']['server_crt']"`
	SERVER_KEY=`sonic-cfggen -d -v "DEVICE_METADATA['x509']['server_key']"`
	if [ -z $SERVER_CRT  ] || [ -z $SERVER_KEY  ]; then
		TELEMETRY_ARGS+=" --insecure"
	else
        TELEMETRY_ARGS+=" --server_crt $SERVER_CRT --server_key $SERVER_KEY "
    fi
else
	TELEMETRY_ARGS+=" --insecure"
fi

if [ -n "$X509" ]; then
	CA_CRT=`sonic-cfggen -d -v "DEVICE_METADATA['x509']['ca_crt']"`
	if [ ! -z $CA_CRT ]; then
	    TELEMETRY_ARGS+=" --ca_crt $CA_CRT"
	fi
fi

# If no configuration entry exists for TELEMETRY, create one default port
if [ -z $TELEMETRY ]; then
    redis-cli -n 4 hset "TELEMETRY|gnmi" port 8080
fi

PORT=`sonic-cfggen -d -v "TELEMETRY['gnmi']['port']"`
TELEMETRY_ARGS+=" --port $PORT"

CLIENT_AUTH=`sonic-cfggen -d -v "TELEMETRY['gnmi']['client_auth']"`
if [ -z $CLIENT_AUTH ] || [ $CLIENT_AUTH == "false" ]; then
	TELEMETRY_ARGS+=" --allow_no_client_auth"
fi

LOG_LEVEL=`sonic-cfggen -d -v "TELEMETRY['gnmi']['log_level']"`
if [ ! -z $LOG_LEVEL ]; then
	TELEMETRY_ARGS+=" -v=$LOG_LEVEL"
else
	TELEMETRY_ARGS+=" -v=2"
fi

exec /usr/sbin/telemetry ${TELEMETRY_ARGS}
