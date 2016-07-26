#!/bin/sh

echo "Replace ONIE reboot with Dell reset commands"

# set I2C GPIO mux
echo 1 > /sys/class/gpio/export
echo 2 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio1/direction
echo out > /sys/class/gpio/gpio2/direction
echo 0 > /sys/class/gpio/gpio1/value
echo 0 > /sys/class/gpio/gpio2/value

# replace the original reboot binary with the following command
rm /sbin/reboot
echo 'i2cset -y 0 0x31 1 0xfd' > /sbin/reboot
chmod a+x /sbin/reboot
