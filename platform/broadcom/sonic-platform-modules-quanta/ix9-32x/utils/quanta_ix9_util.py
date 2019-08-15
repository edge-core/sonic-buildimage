#!/usr/bin/env python
#
# Copyright (C) 2018 Quanta Computer Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Usage: %(scriptName)s [options] command object

options:
    -h | --help     : this help message
    -d | --debug    : run with debug mode
    -f | --force    : ignore error during installation or clean
command:
    install     : install drivers and generate related sysfs nodes
    clean       : uninstall drivers and remove related sysfs nodes
"""

import os
import commands
import sys, getopt
import logging
import re
import time
from collections import namedtuple

DEBUG = False
args = []
FORCE = 0
i2c_prefix = '/sys/bus/i2c/devices/'


if DEBUG == True:
    print sys.argv[0]
    print 'ARGV      :', sys.argv[1:]


def main():
    global DEBUG
    global args
    global FORCE

    if len(sys.argv)<2:
        show_help()

    options, args = getopt.getopt(sys.argv[1:], 'hdf', ['help',
                                                       'debug',
                                                       'force',
                                                          ])
    if DEBUG == True:
        print options
        print args
        print len(sys.argv)

    for opt, arg in options:
        if opt in ('-h', '--help'):
            show_help()
        elif opt in ('-d', '--debug'):
            DEBUG = True
            logging.basicConfig(level=logging.INFO)
        elif opt in ('-f', '--force'):
            FORCE = 1
        else:
            logging.info('no option')
    for arg in args:
        if arg == 'install':
           install()
        elif arg == 'clean':
           uninstall()
        else:
            show_help()

    return 0

def show_help():
    print __doc__ % {'scriptName' : sys.argv[0].split("/")[-1]}
    sys.exit(0)

def show_log(txt):
    if DEBUG == True:
        print "[IX9-32X]"+txt
    return

def exec_cmd(cmd, show):
    logging.info('Run :'+cmd)
    status, output = commands.getstatusoutput(cmd)
    show_log (cmd +"with result:" + str(status))
    show_log ("      output:"+output)
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output

instantiate =[
#turn on module power
'echo 21 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio21/direction',
'echo 1 >/sys/class/gpio/gpio21/value',
#Reset fron-ports LED CPLD
'echo 33 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio33/direction',
'echo 0 >/sys/class/gpio/gpio33/value',
'echo 1 >/sys/class/gpio/gpio33/value',
#Enable front-ports LED decoding
'echo 1 > /sys/class/cpld-led/CPLDLED-1/led_decode',
'echo 1 > /sys/class/cpld-led/CPLDLED-2/led_decode',
#Update System LED
'echo 39 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio39/direction',
'echo 0 > /sys/class/gpio/gpio39/value',
'echo 40 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio40/direction',
'echo 1 > /sys/class/gpio/gpio40/value',
]

drivers =[
'lpc_ich',
'i2c-i801',
'i2c-dev',
'i2c-mux-pca954x',
'gpio-pca953x',
'qci_cpld_qsfpdd',
'qci_cpld_led',
'qci_platform_ix9',
'ipmi_devintf'
]



def system_install():
    global FORCE

    #remove default drivers to avoid modprobe order conflicts
    status, output = exec_cmd("rmmod i2c_ismt ", 1)
    status, output = exec_cmd("rmmod i2c-i801 ", 1)
    #setup driver dependency
    status, output = exec_cmd("depmod -a ", 1)
    #install drivers
    for i in range(0,len(drivers)):
       status, output = exec_cmd("modprobe "+drivers[i], 1)
    if status:
       print output
       if FORCE == 0:
          return status

    #remove net rules for generating new net rules
    status, output = exec_cmd("systemctl stop systemd-udevd.service ", 1)
    status, output = exec_cmd("rm /etc/udev/rules.d/70-persistent-net.rules ", 1)
    status, output = exec_cmd("rmmod ixgbe ", 1)
    status, output = exec_cmd("rmmod igb ", 1)
    status, output = exec_cmd("modprobe igb ", 1)
    status, output = exec_cmd("modprobe ixgbe ", 1)
    status, output = exec_cmd("systemctl start systemd-udevd.service ", 1)

    #instantiate devices
    for i in range(0,len(instantiate)):
       status, output = exec_cmd(instantiate[i], 1)
    if status:
       print output
       if FORCE == 0:
          return status

    #QSFPDD for 1~32 port
    for port_number in range(1,33):
        bus_number = port_number + 31
        os.system("echo %d >/sys/bus/i2c/devices/%d-0050/port_name" % (port_number, bus_number))

    return

def system_ready():
    if not device_found():
        return False
    return True

def install():
    if not device_found():
        print "No device, installing...."
        status = system_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print " ix9 driver already installed...."
    return

def uninstall():
    global FORCE
    #uninstall drivers
    for i in range(len(drivers)-1,-1,-1):
       status, output = exec_cmd("rmmod "+drivers[i], 1)
    if status:
	   print output
	   if FORCE == 0:
	      return status
    return

def device_found():
    ret1, log = exec_cmd("ls "+i2c_prefix+"i2c-0", 0)
    return ret1

if __name__ == "__main__":
    main()



