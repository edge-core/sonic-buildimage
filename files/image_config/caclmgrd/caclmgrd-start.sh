#!/usr/bin/env bash

# Only start control plance ACL manager daemon if not an Arista platform.
# Arista devices will use their own service ACL manager daemon(s) instead.
if [ "$(sonic-cfggen -H -v "DEVICE_METADATA.localhost.platform" | grep -c "arista")" -gt 0 ]; then
    echo "Not starting caclmgrd - unsupported platform"
    exit 0
fi

exec /usr/bin/caclmgrd
