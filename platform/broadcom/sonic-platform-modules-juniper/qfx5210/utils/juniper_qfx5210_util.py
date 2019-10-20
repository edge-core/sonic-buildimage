#!/usr/bin/env python
#
# Modified to work on Juniper QFX5210
#
# Based on accton_as7816_util.py
# 
# Copyright (C) 2016 Accton Networks, Inc.
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
    show        : show all systen status
    sff         : dump SFP eeprom
    set         : change board setting with fan|led|sfp    
"""

import os
import commands
import sys, getopt
import binascii
import logging
import re
import time
import random
import optparse
from collections import namedtuple




PROJECT_NAME = 'qfx5210_64x'
version = '0.1.0'
verbose = False
DEBUG = False
args = []
ALL_DEVICE = {}               
DEVICE_NO = {'led':4, 'fan':4,'thermal':6, 'psu':2, 'sfp':64}
FORCE = 0
FUNCTION_NAME = '/var/log/juniper_qfx5210_util'

if DEBUG == True:
    print sys.argv[0]
    print 'ARGV      :', sys.argv[1:]   


def main():
    global DEBUG
    global args
    global FORCE

    log_file = '%s.log' % FUNCTION_NAME
    log_level = logging.DEBUG
        
    if len(sys.argv)<2:
        show_help()
         
    options, args = getopt.getopt(sys.argv[1:], 'hdf', ['help',
                                                       'debug',
                                                       'force',
                                                          ])
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=log_level,
        format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S')

    if DEBUG == True:                                                           
        print options
        print args
        print len(sys.argv)
        # set up logging to console
        if log_level == logging.DEBUG:
            console = logging.StreamHandler()
            console.setLevel(log_level)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
     
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
           do_install()
        elif arg == 'clean':
           do_uninstall()
        elif arg == 'show':
           device_traversal()
        elif arg == 'sff':
            if len(args)!=2:
                show_eeprom_help()
            elif int(args[1]) ==0 or int(args[1]) > DEVICE_NO['sfp']:              
                show_eeprom_help()
            else:
                show_eeprom(args[1])  
            return                              
        elif arg == 'set':
            if len(args)<3:
                show_set_help()
            else:
                set_device(args[1:])                
            return                
        else:
            show_help()
           
    DisableWatchDogCmd = '/usr/sbin/i2cset -f -y 0 0x65 0x3 0x04' 
    # Disable watchdog
    try:
        os.system(DisableWatchDogCmd)
    except OSError:
        print 'Error: Execution of "%s" failed', DisableWatchDogCmd
        return False
  
 
    CPUeepromFileCmd = 'cat /sys/devices/pci0000:00/0000:00:1f.3/i2c-0/0-0056/eeprom > /etc/init.d/eeprom_qfx5210_ascii' 
    # Write the contents of CPU EEPROM to file
    try:
        os.system(CPUeepromFileCmd)
    except OSError:
        print 'Error: Execution of "%s" failed', CPUeepromFileCmd
        return False

    eeprom_ascii = '/etc/init.d/eeprom_qfx5210_ascii'
    # Read file contents in Hex format
    with open(eeprom_ascii, 'rb') as Hexformat:
        content = Hexformat.read()
    Hexformatoutput = binascii.hexlify(content)

    eeprom_hex = '/etc/init.d/eeprom_qfx5210_hex'
    #Write contents of CPU EEPROM to new file in hexa format
    with open(eeprom_hex, 'wb+') as Hexfile:
        Hexfile.write(Hexformatoutput)
  
    # Read from EEPROM Hex file and extract the different fields like Product name,
    # Part Number, Serial Number MAC Address, Mfg Date ... etc and store in /var/run/eeprom file
    with open(eeprom_hex, 'rb') as eeprom_hexfile:
        # moving the file pointer to required position where product name is stored in EEPROM file and reading the required bytes from this position

        product_position = eeprom_hexfile.seek(26, 0)
        product_read = eeprom_hexfile.read(36)
        product_name = binascii.unhexlify(product_read)
   
        # creating the "/var/run/eeprom" file and storing all the values of different fields in this file.
        eeprom_file = open ("/var/run/eeprom", "a+")
        eeprom_file.write("Product Name=%s\r\n" % str(product_name))

        # like wise we are moving the file pointer to respective position where other fields are stored and extract these fields and store in /var/run/eeprom file
        partnumber_position = eeprom_hexfile.seek(66, 0)
        partnumber_read = eeprom_hexfile.read(20)
        partnumber_name = binascii.unhexlify(partnumber_read)
        eeprom_file.write("Part Number=%s\r\n" % str(partnumber_name))

        serialnumber_position = eeprom_hexfile.seek(90, 0)
        serialnumber_read = eeprom_hexfile.read(24)
        serialnumber_name = binascii.unhexlify(serialnumber_read)
        eeprom_file.write("Serial Number=%s\r\n" % str(serialnumber_name))

        macaddress_position = eeprom_hexfile.seek(118, 0)
        macaddress_read = eeprom_hexfile.read(12)
        macaddress_name=""
        for i in range(0,12,2):
            macaddress_name += macaddress_read[i:i+2] + ":"
        macaddress_name=macaddress_name[:-1]
        eeprom_file.write("MAC Address=%s\r\n" % str(macaddress_name))

        mfgdate_position = eeprom_hexfile.seek(132, 0)
        mfgdate_read = eeprom_hexfile.read(40)
        mfgdate_name = binascii.unhexlify(mfgdate_read)
        eeprom_file.write("Manufacture Date=%s\r\n" % str(mfgdate_name))

        devversion_position = eeprom_hexfile.seek(176, 0)
        devversion_read = eeprom_hexfile.read(2)
        eeprom_file.write("Device Version=%s\r\n" % str(devversion_read))

        platform_position = eeprom_hexfile.seek(182, 0)
        platform_read = eeprom_hexfile.read(68)
        platform_name = binascii.unhexlify(platform_read)
        eeprom_file.write("Platform Name=%s\r\n" % str(platform_name))

        MACnumber_position = eeprom_hexfile.seek(254, 0)
        MACnumber_read = eeprom_hexfile.read(4)
        MACnumber = int(MACnumber_read, 16)
        eeprom_file.write("Number of MAC Addresses=%s\r\n" % str(MACnumber))

        vendorName_position = eeprom_hexfile.seek(262, 0)
        vendorName_read = eeprom_hexfile.read(40)
        vendorName = binascii.unhexlify(vendorName_read)
        eeprom_file.write("Vendor Name=%s\r\n" % str(vendorName))

        mfgname_position = eeprom_hexfile.seek(306, 0)
        mfgname_read = eeprom_hexfile.read(40)
        mfgname = binascii.unhexlify(mfgname_read)
        eeprom_file.write("Manufacture Name=%s\r\n" % str(mfgname))

        vendorext_position = eeprom_hexfile.seek(350, 0)
        vendorext_read = eeprom_hexfile.read(124)
        vendorext=""
        vendorext += "0x" + vendorext_read[0:2]
        for i in range(2,124,2):
            vendorext += " 0x" + vendorext_read[i:i+2]
        eeprom_file.write("Vendor Extension=%s\r\n" % str(vendorext))

        IANA_position = eeprom_hexfile.seek(350, 0)
        IANA_read = eeprom_hexfile.read(8)
        IANAName = binascii.unhexlify(IANA_read)
        eeprom_file.write("IANA=%s\r\n" % str(IANAName))

        ASMpartrev_position = eeprom_hexfile.seek(358, 0)
        ASMpartrev_read = eeprom_hexfile.read(4)
        ASMpartrev = binascii.unhexlify(ASMpartrev_read)
        eeprom_file.write("Assembly Part Number Rev=%s\r\n" % str(ASMpartrev))

        ASMpartnum_position = eeprom_hexfile.seek(374, 0)
        ASMpartnum_read = eeprom_hexfile.read(20)
        ASMpartnum_read = binascii.unhexlify(ASMpartnum_read)
        eeprom_file.write("Assembly Part Number=%s\r\n" % str(ASMpartnum_read))

        ASMID_position = eeprom_hexfile.seek(402, 0)
        ASMID_read = eeprom_hexfile.read(4)
        ASMID_read_upper = ASMID_read.upper()
        eeprom_file.write("Assembly ID=0x%s\r\n" % str(ASMID_read_upper))

        ASMHWMajRev_position = eeprom_hexfile.seek(410, 0)
        ASMHWMajRev_read = eeprom_hexfile.read(2)
        eeprom_file.write("Assembly Major Revision=0x%s\r\n" % str(ASMHWMajRev_read))

        ASMHWMinRev_position = eeprom_hexfile.seek(416, 0)
        ASMHWMinRev_read = eeprom_hexfile.read(2)
        eeprom_file.write("Assembly Minor Revision=0x%s\r\n" % str(ASMHWMinRev_read))

        Deviation_position = eeprom_hexfile.seek(422, 0)
        Deviation_read = eeprom_hexfile.read(28)
        Deviation_read_upper = Deviation_read.upper()
        eeprom_file.write("Deviation=0x%s\r\n" % str(Deviation_read_upper))

        CLEI_position = eeprom_hexfile.seek(450, 0)
        CLEI_read = eeprom_hexfile.read(20)
        CLEI_name = binascii.unhexlify(CLEI_read)
        eeprom_file.write("CLEI code=%s\r\n" % str(CLEI_name))

        ONIEversion_position = eeprom_hexfile.seek(478, 0)
        ONIEversion_read = eeprom_hexfile.read(22)
        ONIEversion = binascii.unhexlify(ONIEversion_read)
        eeprom_file.write("ONIE Version=%s\r\n" % str(ONIEversion))

        CRC_position = eeprom_hexfile.seek(504, 0)
        CRC = eeprom_hexfile.read(8)
        eeprom_file.write("CRC=%s\r\n" % str(CRC))

        eeprom_file.close()

    return True              
        
def show_help():
    print __doc__ % {'scriptName' : sys.argv[0].split("/")[-1]}
    sys.exit(0)

def  show_set_help():
    cmd =  sys.argv[0].split("/")[-1]+ " "  + args[0]
    print  cmd +" [led|sfp|fan]"
    print  "    use \""+ cmd + " led 0-4 \"  to set led color"
    print  "    use \""+ cmd + " fan 0-100\" to set fan duty percetage"    
    print  "    use \""+ cmd + " sfp 1-32 {0|1}\" to set sfp# tx_disable" 
    sys.exit(0)  
    
def  show_eeprom_help():
    cmd =  sys.argv[0].split("/")[-1]+ " "  + args[0]
    print  "    use \""+ cmd + " 1-32 \" to dump sfp# eeprom" 
    sys.exit(0)           
            
def my_log(txt):
    if DEBUG == True:
        print txt    
    return
    
def log_os_system(cmd, show):
    logging.info('Run :'+cmd)  
    status, output = commands.getstatusoutput(cmd)    
    my_log (cmd +"with result:" + str(status))
    my_log ("      output:"+output)    
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output
            
def driver_check():
    ret, lsmod = log_os_system("lsmod| grep juniper", 0)
    logging.info('mods:'+lsmod)
    if len(lsmod) ==0:
        return False   
    return True



kos = [
'modprobe i2c_dev',
'modprobe i2c_mux_pca954x force_deselect_on_exit=1',
'modprobe optoe',
'modprobe juniper_i2c_cpld'  ,
'modprobe ym2651y'                  ,
'modprobe x86-64-juniper-qfx5210-64x-fan'     ,
'modprobe x86-64-juniper-qfx5210-64x-leds'      ,
'modprobe x86-64-juniper-qfx5210-64x-psu' ]

def driver_install():
    global FORCE
    status, output = log_os_system("depmod", 1)
    for i in range(0,len(kos)):
        status, output = log_os_system(kos[i], 1)
        if status:
            if FORCE == 0:        
                return status              
    return 0
    
def driver_uninstall():
    global FORCE
    for i in range(0,len(kos)):
        rm = kos[-(i+1)].replace("modprobe", "modprobe -rq")
        rm = rm.replace("insmod", "rmmod")        
        status, output = log_os_system(rm, 1)
        if status:
            if FORCE == 0:        
                return status              
    return 0

led_prefix ='/sys/class/leds/'
hwmon_types = {'led': ['alarm','system','master','beacon']}
hwmon_nodes = {'led': ['brightness'] }
hwmon_prefix ={'led': led_prefix}

i2c_prefix = '/sys/bus/i2c/devices/'
i2c_bus = {'fan': ['17-0068']                 ,
           'thermal': ['18-0048','18-0049', '18-004a' , '18-004b', '17-004d', '17-004e'] ,
           'psu': ['10-0053','9-0050'], 
           'sfp': ['-0050']}
i2c_nodes = {'fan': ['present', 'front_speed_rpm', 'rear_speed_rpm'] ,
           'thermal': ['hwmon/hwmon*/temp1_input'] ,
           'psu': ['psu_present ', 'psu_power_good']    ,
           'sfp': ['sfp_is_present ', 'module_present']}
                   
sfp_map =  [37,38,39,40,42,41,44,43,33,34,35,36,45,46,47,48,49,50,51,52,
           61,62,63,64,53,54,55,56,57,58,59,60,69,70,71,72,77,78,79,80,65,
	   66,67,68,73,74,75,76,85,86,87,88,31,32,29,30,81,82,83,84,25,26,
           27,28]

mknod =[   
'echo pca9548  0x77 > /sys/bus/i2c/devices/i2c-0/new_device',
'echo pca9548  0x71 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo pca9548  0x76 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo pca9548  0x73 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo pca9548  0x70 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x71 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x72 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x73 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x74 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x75 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548  0x76 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo 24c02  0x56 > /sys/bus/i2c/devices/i2c-0/new_device',
'echo qfx5210_64x_psu1  0x53 > /sys/bus/i2c/devices/i2c-10/new_device',
'echo ym2851  0x5b > /sys/bus/i2c/devices/i2c-10/new_device',
'echo qfx5210_64x_psu2  0x50 > /sys/bus/i2c/devices/i2c-9/new_device',
'echo ym2851  0x58 > /sys/bus/i2c/devices/i2c-9/new_device',
'echo qfx5210_64x_fan  0x68 > /sys/bus/i2c/devices/i2c-17/new_device',
'echo lm75  0x48 > /sys/bus/i2c/devices/i2c-18/new_device',
'echo lm75  0x49 > /sys/bus/i2c/devices/i2c-18/new_device',
'echo lm75  0x4a > /sys/bus/i2c/devices/i2c-18/new_device',
'echo lm75  0x4b > /sys/bus/i2c/devices/i2c-18/new_device',
'echo lm75  0x4d > /sys/bus/i2c/devices/i2c-17/new_device',
'echo lm75  0x4e > /sys/bus/i2c/devices/i2c-17/new_device',
'echo cpld_qfx5210  0x60 > /sys/bus/i2c/devices/i2c-19/new_device',
'echo cpld_plain  0x62 > /sys/bus/i2c/devices/i2c-20/new_device',
'echo cpld_plain  0x64 > /sys/bus/i2c/devices/i2c-21/new_device',
'echo cpld_plain  0x66 > /sys/bus/i2c/devices/i2c-22/new_device',
'echo cpld_plain  0x65 > /sys/bus/i2c/devices/i2c-0/new_device 2>/dev/null'
]
       
def i2c_order_check():    
    return 0
                     
def device_install():
    global FORCE
    
    for i in range(0,len(mknod)):
        #for pca954x need times to built new i2c buses            
        if mknod[i].find('pca954') != -1:
           time.sleep(1)         
           
        status, output = log_os_system(mknod[i], 1)
        if status:
            print output
            if FORCE == 0:                
                return status  

    for i in range(0,len(sfp_map)):
        path = "/sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/new_device"
        status, output =log_os_system("echo optoe1 0x50 > " + path, 1)
        if status:
            print output
            if FORCE == 0:            
                return status
        status, output =log_os_system("echo Port"+str(i)+" > /sys/bus/i2c/devices/"+str(sfp_map[i])+"-0050/port_name", 1)
        if status:
            print output
            if FORCE == 0:
                return status
    return 
    
def device_uninstall():
    global FORCE
    
    status, output =log_os_system("ls /sys/bus/i2c/devices/1-0076", 0)
    
    for i in range(0,len(sfp_map)):
        target = "/sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/delete_device"
        status, output =log_os_system("echo 0x50 > "+ target, 1)
        if status:
            print output
            if FORCE == 0:            
                return status
       
    nodelist = mknod
           
    for i in range(len(nodelist)):
        target = nodelist[-(i+1)]
        temp = target.split()
        del temp[1]
        temp[-1] = temp[-1].replace('new_device', 'delete_device')
        status, output = log_os_system(" ".join(temp), 1)
        if status:
            print output
            if FORCE == 0:            
                return status  
                                  
    return 
        
def system_ready():
    if driver_check() == False:
        return False
    if not device_exist(): 
        return False
    return True
               
def do_install():
    logging.info('Checking system....')
    if driver_check() == False:
        logging.info('No driver, installing....')
        status = driver_install()
        if status:
            if FORCE == 0:        
                return  status
    else:
        print PROJECT_NAME.upper()+" drivers detected...."                      
    if not device_exist():
        logging.info('No device, installing....')     
        status = device_install() 
        if status:
            if FORCE == 0:        
                return  status        
    else:
        print PROJECT_NAME.upper()+" devices detected...."           
    return
    
def do_uninstall():
    logging.info('Checking system....')
    if not device_exist():
        print PROJECT_NAME.upper() +" has no device installed...."         
    else:
        logging.info('Removing device....')
        status = device_uninstall() 
        if status:
            if FORCE == 0:            
                return  status  
                
    if driver_check()== False :
        print PROJECT_NAME.upper() +" has no driver installed...."
    else:
        logging.info('Removing installed driver....')
        status = driver_uninstall()
        if status:
            if FORCE == 0:        
                return  status                          
                    
    return       

def devices_info():
    global DEVICE_NO
    global ALL_DEVICE
    global i2c_bus, hwmon_types
    for key in DEVICE_NO:   
        ALL_DEVICE[key]= {} 
        for i in range(0,DEVICE_NO[key]):
            ALL_DEVICE[key][key+str(i+1)] = []
            
    for key in i2c_bus:
        buses = i2c_bus[key]
        nodes = i2c_nodes[key]    
        for i in range(0,len(buses)):
            for j in range(0,len(nodes)):
                if  'fan' == key:
                    for k in range(0,DEVICE_NO[key]):
                        node = key+str(k+1)
                        path = i2c_prefix+ buses[i]+"/fan"+str(k+1)+"_"+ nodes[j]
                        my_log(node+": "+ path)
                        ALL_DEVICE[key][node].append(path) 
                elif  'sfp' == key:
                    for k in range(0,DEVICE_NO[key]):
                        node = key+str(k+1)
                        fmt = i2c_prefix+"19-0060/{0}_{1}"
                        path =  fmt.format(nodes[j], k+1)
                        my_log(node+": "+ path)
                        ALL_DEVICE[key][node].append(path)                                        
                else:
                    node = key+str(i+1)
                    path = i2c_prefix+ buses[i]+"/"+ nodes[j]                
                    my_log(node+": "+ path)
                    ALL_DEVICE[key][node].append(path)  
                                     
    for key in hwmon_types:
        itypes = hwmon_types[key]
        nodes = hwmon_nodes[key]    
        for i in range(0,len(itypes)):
            for j in range(0,len(nodes)): 
                node = key+"_"+itypes[i]
                path = hwmon_prefix[key]+ itypes[i]+"/"+ nodes[j]           
                my_log(node+": "+ path)
                ALL_DEVICE[key][ key+str(i+1)].append(path)                   
    
    #show dict all in the order
    if DEBUG == True:
        for i in sorted(ALL_DEVICE.keys()):
            print(i+": ")
            for j in sorted(ALL_DEVICE[i].keys()):    
                print("   "+j)
                for k in (ALL_DEVICE[i][j]):    
                    print("   "+"   "+k)
    return 
        
def show_eeprom(index):
    if system_ready()==False:
        print("System's not ready.")        
        print("Please install first!")
        return 
              
    i = int(index)-1
    node = i2c_prefix+ str(sfp_map[i])+ i2c_bus['sfp'][0]+"/"+ 'eeprom'
    # check if got hexdump command in current environment
    ret, log = log_os_system("which hexdump", 0)
    ret, log2 = log_os_system("which busybox hexdump", 0)    
    if len(log):
        hex_cmd = 'hexdump'
    elif len(log2):
        hex_cmd = ' busybox hexdump'
    else:
        log = 'Failed : no hexdump cmd!!'
        logging.info(log)
        print log
        return 1                                 
            
    print node + ":"
    ret, log = log_os_system(hex_cmd +" -C "+node, 1)
    if ret==0:                                      
        print  log 
    else:
        print "**********device no found**********"       
    return 
         
def set_device(args):
    global DEVICE_NO
    global ALL_DEVICE
    if system_ready()==False:
        print("System's not ready.")        
        print("Please install first!")
        return     
    
    if len(ALL_DEVICE)==0:
        devices_info()  
        
    if args[0]=='led':
        if int(args[1])>4:
            show_set_help()
            return
        #print  ALL_DEVICE['led']
        for i in range(0,len(ALL_DEVICE['led'])):   
            for k in (ALL_DEVICE['led']['led'+str(i+1)]):  
                ret, log = log_os_system("echo "+args[1]+" >"+k, 1)
                if ret:
                    return ret  
    elif args[0]=='fan':
        if int(args[1])>100:
            show_set_help()
            return
        #print  ALL_DEVICE['fan']
        #fan1~6 is all fine, all fan share same setting        
        node = ALL_DEVICE['fan'] ['fan1'][0] 
        node = node.replace(node.split("/")[-1], 'fan_duty_cycle_percentage')
        ret, log = log_os_system("cat "+ node, 1)            
        if ret==0:
            print ("Previous fan duty: " + log.strip() +"%")            
        ret, log = log_os_system("echo "+args[1]+" >"+node, 1)
        if ret==0:
            print ("Current fan duty: " + args[1] +"%")          
        return ret
    elif args[0]=='sfp':
        if int(args[1])> DEVICE_NO[args[0]] or int(args[1])==0:
            show_set_help()
            return     
        if len(args)<2:
            show_set_help()
            return 
                            
        if int(args[2])>1:
            show_set_help()
            return
       
        #print  ALL_DEVICE[args[0]]   
        for i in range(0,len(ALL_DEVICE[args[0]])):   
            for j in ALL_DEVICE[args[0]][args[0]+str(args[1])]:        
                if j.find('tx_disable')!= -1:  
                    ret, log = log_os_system("echo "+args[2]+" >"+ j, 1)
                    if ret:
                        return ret  
                                                                           
    return
    
#get digits inside a string. 
#Ex: 31 for "sfp31"   
def get_value(input):
    digit = re.findall('\d+', input)
    return int(digit[0])
              
def device_traversal():
    if system_ready()==False:
        print("System's not ready.")        
        print("Please install first!")
        return 
        
    if len(ALL_DEVICE)==0:
        devices_info()
    for i in sorted(ALL_DEVICE.keys()):
        print("============================================")        
        print(i.upper()+": ")
        print("============================================")
         
        for j in sorted(ALL_DEVICE[i].keys(), key=get_value):    
            print "   "+j+":",
            for k in (ALL_DEVICE[i][j]):
                ret, log = log_os_system("cat "+k, 0)
                func = k.split("/")[-1].strip()
                func = re.sub(j+'_','',func,1)
                func = re.sub(i.lower()+'_','',func,1)                 
                if ret==0:
                    print func+"="+log+" ",                  
                else:
                    print func+"="+"X"+" ",
            print                    
            print("----------------------------------------------------------------")
                                              
     
        print
    return
            
def device_exist():
    ret1, log = log_os_system("ls "+i2c_prefix+"*0076", 0)
    ret2, log = log_os_system("ls "+i2c_prefix+"i2c-2", 0)
    return not(ret1 or ret2)

if __name__ == "__main__":
    main()
