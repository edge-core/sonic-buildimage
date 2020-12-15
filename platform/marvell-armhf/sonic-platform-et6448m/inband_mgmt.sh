#!/bin/sh

#inband_mgmt

inband_mgmt(){

# The intent of this sequence is to ensure 12c bus enumeration order by
# controlling the order in which the various i2c device drivers are
# loaded. Hence the drivers are unloaded and then reloaded in the prescribed
# order.
# NOTE: In the nokia platform the following sequence is performed by the Nokia
# platform service init script and thus should not be performed here
 if [ ! -f /host/machine.conf ]; then
     exit 0
 fi
 grep ^onie_platform /host/machine.conf 2>/dev/null | grep nokia >/dev/null
 if [ $? != 0 ]; then
     rmmod i2c-dev
     rmmod i2c_mux_gpio
     rmmod i2c_mv64xxx
     modprobe i2c_mv64xxx
     modprobe i2c-dev
     modprobe i2c_mux_gpio
     sleep 60
 fi
 while :; do
   ip -br link show eth0 2> /dev/null
   if [ $? -eq 0 ]; then
       ip address show eth0 | grep -qw "inet" 2>/dev/null
       if [ $? -ne 0 ]; then
           ifconfig eth0 down
           systemctl restart networking
       fi
       sleep 120
   else
     sleep 3
   fi
 done
}
(inband_mgmt > /dev/null)&
