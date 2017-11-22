#!/bin/bash -e

CURRENT_HOSTNAME=`hostname`
HOSTNAME=`sonic-cfggen -d -v DEVICE_METADATA[\'localhost\'][\'hostname\']`

echo $HOSTNAME > /etc/hostname
hostname -F /etc/hostname

sed -i "/\s$CURRENT_HOSTNAME$/d" /etc/hosts
echo "127.0.0.1 $HOSTNAME" >> /etc/hosts

