#!/bin/bash

FIRST_BOOT_PLATFORM_FILE="/tmp/notify_firstboot_to_platform"

if [ -f ${FIRST_BOOT_PLATFORM_FILE} ]; then

     # Re-install the igb and ixgbe again to make the NIC sequence follow the udev rule
     modprobe -r igb
     modprobe -r ixgbe
     udevadm control --reload-rules
     udevadm trigger
     modprobe igb
     modprobe ixgbe    
     echo "reload ixgbe ko"
fi

exit 0
