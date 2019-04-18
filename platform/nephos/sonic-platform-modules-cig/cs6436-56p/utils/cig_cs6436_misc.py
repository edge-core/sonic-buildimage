#!/usr/bin/env python
#
# Copyright (C) 2018 Cambridge, Inc.
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

import os
import commands
import sys, getopt
import logging
import re
import time
from collections import namedtuple
from threading import Thread

DEBUG = False
i2c_prefix = '/sys/bus/i2c/devices/'
cs6436__prefix = '/sys/devices/platform/cs6436_56p_led/leds/'

def my_log(txt):
    if DEBUG == True:
        print "[ROY]"+txt
    return

def device_exist():
    ret1, log = log_os_system("ls "+i2c_prefix+"5-005a", 0)
    ret2, log = log_os_system("ls "+i2c_prefix+"5-005b", 0)
    ret3, log = log_os_system("ls "+cs6436__prefix+"cs6436_56p_led*", 0)
    return not(ret1 or ret2 or ret3)
    

def log_os_system(cmd, show):
    logging.info('Run :'+cmd)  
    status, output = commands.getstatusoutput(cmd)    
    my_log (cmd +"with result:" + str(status))
    my_log ("      output:"+output)    
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return status, output


def system_misc_polling(threadName,delay):    
    for count in range(1,5):
        if device_exist() == False:
            time.sleep(delay+3)
            print "%s: %s, count=%d" % ( threadName, time.ctime(time.time()), count)
        else:
            break

    if count == 4:
        return
        
    status, output = log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::sys/brightness", 1)
    status, output = log_os_system("hwconfig -cfp 1", 1)

    while 1:
        status, output = log_os_system("cat /sys/bus/i2c/devices/5-005a/psu_present", 1)
        if status:
          print "failed to check status for 5-005a/psu_present"
          continue
          
        if output=='1':
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::psu1/brightness", 1)
        else:
           log_os_system("echo 0 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::psu1/brightness", 1)
           
        status, output = log_os_system("cat /sys/bus/i2c/devices/5-005b/psu_present", 1)
        if status:
          print "failed to check status for 5-005b/psu_present"
          continue     
          
        if output=='1':
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::psu2/brightness", 1)
        else:
            log_os_system("echo 0 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::psu2/brightness", 1)

        status, fan1 = log_os_system(" cat /sys/devices/platform/cs6436_56p_fan/fan1_fault",1)
        if status:
          print "failed to check status for cs6436_56p_fan/fan1_fault"
          continue
          
        if fan1=='0':		
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan1/brightness", 1)
        else:	    
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan1/brightness", 1)
            
        status, fan2 = log_os_system(" cat /sys/devices/platform/cs6436_56p_fan/fan2_fault",1)
        
        if status:
          print "failed to check status for cs6436_56p_fan/fan2_fault"
          continue
          
        if fan2=='0':		
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan2/brightness", 1)
        else:	    
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan2/brightness", 1)
            
        status, fan3 = log_os_system(" cat /sys/devices/platform/cs6436_56p_fan/fan3_fault",1)
        if status:
          print "failed to check status for cs6436_56p_fan/fan3_fault"
          continue
          
        if fan3=='0':		
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan3/brightness", 1)
        else:	    
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan3/brightness", 1)
            
        status, fan4 = log_os_system(" cat /sys/devices/platform/cs6436_56p_fan/fan4_fault",1)
        if status:
          print "failed to check status for cs6436_56p_fan/fan4_fault"
          continue
          
        if fan4=='0':		
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan4/brightness", 1)
        else:	    
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan4/brightness", 1)
            
        status, fan5 = log_os_system(" cat /sys/devices/platform/cs6436_56p_fan/fan5_fault",1)
        if status:
          print "failed to check status for cs6436_56p_fan/fan5_fault"
          continue 
       
        if fan5=='0':		
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan5/brightness", 1)
        else:	    
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan5/brightness", 1)
            
        if fan1=='0' or fan2=='0' or fan3=='0' or fan4=='0' or fan5=='0':
            log_os_system("echo 1 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan/brightness", 1)
        else:
            log_os_system("echo 3 > /sys/devices/platform/cs6436_56p_led/leds/cs6436_56p_led::fan/brightness", 1)
        time.sleep(delay)
        print "%s: %s" % ( threadName, time.ctime(time.time()))
    return

if __name__ == '__main__':
    target=system_misc_polling("Thread-misc",3)




