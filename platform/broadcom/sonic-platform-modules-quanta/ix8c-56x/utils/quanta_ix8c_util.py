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
        print "[IX8C-56X]"+txt
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
#export pca9698 for qsfp present
'echo 34 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio34/direction',
'echo 38 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio38/direction',
'echo 42 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio42/direction',
'echo 46 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio46/direction',
'echo 50 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio50/direction',
'echo 54 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio54/direction',
'echo 58 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio58/direction',
'echo 62 > /sys/class/gpio/export',
'echo in > /sys/class/gpio/gpio62/direction',
#export pca9698 for qsfp reset
'echo 32 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio32/direction',
'echo 1 >/sys/class/gpio/gpio32/value',
'echo 36 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio36/direction',
'echo 1 >/sys/class/gpio/gpio36/value',
'echo 40 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio40/direction',
'echo 1 >/sys/class/gpio/gpio40/value',
'echo 44 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio44/direction',
'echo 1 >/sys/class/gpio/gpio44/value',
'echo 48 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio48/direction',
'echo 1 >/sys/class/gpio/gpio48/value',
'echo 52 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio52/direction',
'echo 1 >/sys/class/gpio/gpio52/value',
'echo 56 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio56/direction',
'echo 1 >/sys/class/gpio/gpio56/value',
'echo 60 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio60/direction',
'echo 1 >/sys/class/gpio/gpio60/value',
#export pca9698 for qsfp lpmode
'echo 35 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio35/direction',
'echo 0 >/sys/class/gpio/gpio35/value',
'echo 39 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio39/direction',
'echo 0 >/sys/class/gpio/gpio39/value',
'echo 43 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio43/direction',
'echo 0 >/sys/class/gpio/gpio43/value',
'echo 47 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio47/direction',
'echo 0 >/sys/class/gpio/gpio47/value',
'echo 51 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio51/direction',
'echo 0 >/sys/class/gpio/gpio51/value',
'echo 55 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio55/direction',
'echo 0 >/sys/class/gpio/gpio55/value',
'echo 59 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio59/direction',
'echo 0 >/sys/class/gpio/gpio59/value',
'echo 63 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio63/direction',
'echo 0 >/sys/class/gpio/gpio63/value',
#Reset fron-ports LED CPLD
'echo 73 > /sys/class/gpio/export',
'echo out > /sys/class/gpio/gpio73/direction',
'echo 0 >/sys/class/gpio/gpio73/value',
'echo 1 >/sys/class/gpio/gpio73/value',
#Enable front-ports LED decoding
'echo 1 > /sys/class/cpld-led/CPLDLED-1/led_decode',
'echo 1 > /sys/class/cpld-led/CPLDLED-2/led_decode',
#SFP28 Module TxEnable
'echo 0 > /sys/class/cpld-sfp28/port-1/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-2/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-3/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-4/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-5/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-6/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-7/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-8/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-9/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-10/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-11/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-12/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-13/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-14/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-15/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-16/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-17/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-18/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-19/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-20/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-21/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-22/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-23/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-24/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-25/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-26/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-27/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-28/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-29/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-30/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-31/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-32/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-33/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-34/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-35/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-36/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-37/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-38/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-39/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-40/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-41/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-42/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-43/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-44/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-45/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-46/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-47/tx_dis',
'echo 0 > /sys/class/cpld-sfp28/port-48/tx_dis'
]

drivers =[
'lpc_ich',
'i2c-i801',
'i2c-dev',
'i2c-mux-pca954x',
'gpio-pca953x',
'optoe',
'qci_cpld_sfp28',
'qci_cpld_led',
'qci_platform_ix8c',
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

    #QSFP for 1~56 port
    for port_number in range(1,57):
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
        print " ix8c driver already installed...."
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



