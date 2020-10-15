#!/bin/bash

PREV_REBOOT_CAUSE="/host/reboot-cause/"
DEVICE="/usr/share/sonic/device"
PLATFORM=$(/usr/local/bin/sonic-cfggen -H -v DEVICE_METADATA.localhost.platform)
FILES=$DEVICE/$PLATFORM/plugins
FILENAME="udevprefix.conf"

if [ "$1" = "clear" ]
then
	if [ -e $FILES/$FILENAME ]; then
		rm $FILES/$FILENAME
	fi
else
	if [ -e $FILES/$FILENAME ]; then
		: > $FILES/$FILENAME 
		echo -n "$1" > $FILES/$FILENAME
	else
		touch $FILES/$FILENMAE
		echo -n "$1" > $FILES/$FILENAME 
	fi
fi

