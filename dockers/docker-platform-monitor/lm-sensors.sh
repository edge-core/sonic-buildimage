#!/usr/bin/env bash
#
# Based off /etc/init.d/lm-sensors
#

/usr/bin/sensors -s > /dev/null 2>&1
/usr/bin/sensors > /dev/null 2>&1

# Currently, there is no way to run sensord in the foreground, so we
# can't use supervisord. Instead, we just start the service for now.
service sensord start
