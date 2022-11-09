#!/bin/bash

# Generate the sources.list.<arch> in the config path
CONFIG_PATH=$1
export ARCHITECTURE=$2
export DISTRIBUTION=$3

# The default mirror urls
DEFAULT_MIRROR_URLS=http://debian-archive.trafficmanager.net/debian/,http://packages.trafficmanager.net/debian/debian/
DEFAULT_MIRROR_SECURITY_URLS=http://debian-archive.trafficmanager.net/debian-security/,http://packages.trafficmanager.net/debian/debian-security/

# The debian-archive.trafficmanager.net does not support armhf, use debian.org instead
if [ "$ARCHITECTURE" == "armhf" ]; then
    DEFAULT_MIRROR_URLS=http://deb.debian.org/debian/,http://packages.trafficmanager.net/debian/debian/
    DEFAULT_MIRROR_SECURITY_URLS=http://deb.debian.org/debian-security/,http://packages.trafficmanager.net/debian/debian-security/
fi

[ -z "$MIRROR_URLS" ] && MIRROR_URLS=$DEFAULT_MIRROR_URLS
[ -z "$MIRROR_SECURITY_URLS" ] && MIRROR_SECURITY_URLS=$DEFAULT_MIRROR_SECURITY_URLS

TEMPLATE=files/apt/sources.list.j2
[ -f files/apt/sources.list.$ARCHITECTURE.j2 ] && TEMPLATE=files/apt/sources.list.$ARCHITECTURE.j2
[ -f $CONFIG_PATH/sources.list.j2 ] && TEMPLATE=$CONFIG_PATH/sources.list.j2
[ -f $CONFIG_PATH/sources.list.$ARCHITECTURE.j2 ] && TEMPLATE=$CONFIG_PATH/sources.list.$ARCHITECTURE.j2

MIRROR_URLS=$MIRROR_URLS MIRROR_SECURITY_URLS=$MIRROR_SECURITY_URLS j2 $TEMPLATE | sed '/^$/N;/^\n$/D' > $CONFIG_PATH/sources.list.$ARCHITECTURE
