#!/bin/bash -e

CURRENT_HOSTNAME=`hostname`
HOSTNAME=`sonic-cfggen -d -v DEVICE_METADATA[\'localhost\'][\'hostname\']`

echo $HOSTNAME > /etc/hostname
hostname -F /etc/hostname

# Remove the old hostname entry from hosts file.
# But, 'localhost' entry is used by multiple applications. Don't remove it altogether.
if [ $CURRENT_HOSTNAME  != "localhost" ] || [ $CURRENT_HOSTNAME == $HOSTNAME ] ;  then
 sed -i "/\s$CURRENT_HOSTNAME$/d" /etc/hosts
fi

echo "127.0.0.1 $HOSTNAME" >> /etc/hosts

