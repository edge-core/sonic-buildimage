#!/bin/bash

# Provie file paths to archive for debug image as relative to src subdir
#
SRC_DIR_LIST="\
    libteam \
    lldpd \
    libnl3 \
    radvd \
    redis \
    snmpd \
    sonic-dbsyncd \
    sonic-frr \
    sonic-platform-common \
    sonic-platform-daemons \
    sonic-py-swsssdk \
    sonic-sairedis \
    sonic-snmpagent \
    sonic-swss \
    sonic-swss-common \
    tacacs"

for i in $SRC_DIR_LIST
do
    find $i/ -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -type f
done

