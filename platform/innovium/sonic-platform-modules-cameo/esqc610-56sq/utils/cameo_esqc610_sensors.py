#!/usr/bin/python

from __future__ import print_function
import os
import sys
import logging
import json

MAX_FAN_NUM = 4
MAX_PSU_NUM = 2
PSU_LIST = ['PSU1','PSU2'] #0x58, 0x59

PLATFORM_INSTALL_INFO_FILE  = '/etc/sonic/platform_install.json'

FAN_SYSFILE_PATH        = '/sys/class/hwmon/hwmon2/device/ESQC610_FAN/'
THERMAL_SYSFILE_PATH    = '/sys/class/hwmon/hwmon2/device/ESQC610_Sensor/'
POWER_SYSFILE_PATH      = '/sys/class/hwmon/hwmon2/device/ESQC610_PSU/'
BMC_SYSFILE_PATH        = '/sys/class/hwmon/hwmon2/device/ESQC610_BMC/'

def get_psu_path():
    """
    get psu path when without BMC control
    """
    psu_path = []
    try:
        with open(PLATFORM_INSTALL_INFO_FILE) as fd:
            install_info = json.load(fd)
            for psu_name in PSU_LIST:
                psu = install_info[1][psu_name]
                psu_path.append(psu['path']+'/')
            return psu_path
    except Exception:
        print("Fail to get psu sysfsfile path")
    
    return psu_path

def get_thermal_sensor_path():
    sensor_path = []
    try:
        with open(PLATFORM_INSTALL_INFO_FILE) as fd:
            install_info = json.load(fd)
            for sensor_name in THERMAL_SENSOR_LIST:
                sensor = install_info[1][sensor_name]
                sensor_path.append(sensor['path']+'/')
            return sensor_path
    except Exception:
        print("Fail to get sensor sysfsfile path")
        
    return sensor_path

# Get sysfs attribute
def get_attr_value(attr_path):
    retval = 'ERR'
    if not os.path.isfile(attr_path):
        return retval

    try:
        with open(attr_path, 'r') as fd:
            retval = fd.read()
    except Exception as error:
        logging.error("Unable to open ", attr_path, " file !")

    retval = retval.rstrip('\r\n')
    fd.close()
    return retval

def bmc_is_exist():
    value = ''
    if os.path.exists(BMC_SYSFILE_PATH+"bmc_present"):
       value = get_attr_value(BMC_SYSFILE_PATH+"bmc_present")
       if value.find('not') < 0:
            return True
       else:
            return False
    else:
       return False

def print_attr_value_lines(sys_path):
    retval = 'ERR'
    if not os.path.isfile(sys_path):
        return retval
    try:
        fo = open(sys_path, "r")
    except Exception as error:
        logging.error("Unable to open ", sys_path, " file !")
    for line in fo.readlines():
        line = line.strip()
        print ("    %s" % line)
    fo.close()
    return retval

def sensors_status():
    if bmc_is_exist():
        print ('SENSOR STATUS:')
        sys_path = THERMAL_SYSFILE_PATH + 'sensor_status'
        print_attr_value_lines(sys_path)

    return

def sensors_temp():
    if bmc_is_exist():
        print ('SENSOR TEMPERATURE:')
        sys_path = BMC_SYSFILE_PATH + 'bmc_sersor_1'
        print_attr_value_lines(sys_path)
        sys_path = BMC_SYSFILE_PATH + 'bmc_sersor_2'
        print_attr_value_lines(sys_path)
        sys_path = BMC_SYSFILE_PATH + 'bmc_sersor_3'
        print_attr_value_lines(sys_path)
        sys_path = BMC_SYSFILE_PATH + 'bmc_sersor_4'
        print_attr_value_lines(sys_path)
    return

def get_voltage():
    return

def fan_status():
    sys_path = FAN_SYSFILE_PATH + 'fan_status'
    print ('FAN STATUS:')
    print_attr_value_lines(sys_path)
    return

def fan_present():
    sys_path = FAN_SYSFILE_PATH + 'fan_present'
    print ('FAN PRESENT:')
    print_attr_value_lines(sys_path)
    return

def fan_power():
    sys_path = FAN_SYSFILE_PATH + 'fan_power'
    print ('FAN POWER:')
    print_attr_value_lines(sys_path)
    return

def fan_speed():
    sys_path = FAN_SYSFILE_PATH + 'fan_speed_rpm'
    print ('FAN SPEED:')
    print_attr_value_lines(sys_path)
    return


def is_psu_present(psu_number):
    sys_path = POWER_SYSFILE_PATH + 'psu_present'
    search_str = "PSU {} is present".format(psu_number)
    if os.path.exists(sys_path):
       value = get_attr_value(sys_path)
       if search_str in value:
            return True
       else:
            return False
    
    return False

def show_psu_status(path):
    # [model, vin, vout, fan_speed, temperature, pin, pout, iin, iout, max_iout]
    result_list = [0]*10
    if bmc_is_exist():  
        try:
          reg_file = open(path, 'r')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False 
        
        text_lines = reg_file.readlines()
        reg_file.close()
        
        for line in text_lines:
            spline = line.split(' ')
            if "MFR_MODEL" in spline:
                result_list[0] = spline[-1]
            if "VIN" in spline:
                result_list[1] = spline[-1]
            if "VOUT" in spline:
                result_list[2] = spline[-1]
            if "FAN_SPEED" in spline:
                result_list[3] = spline[-1]
            if "TEMP_1" in spline:
                result_list[4] = spline[-1]
            if "PIN" in spline:
                result_list[5] = spline[-1]
            if "POUT" in spline:
                result_list[6] = spline[-1]
            if "IIN" in spline:
                result_list[7] = spline[-1]
            if "IOUT" in spline:
                result_list[8] = spline[-1]
            if "MFR_IOUT_MAX" in spline:
                result_list[9] = spline[-1]                
                
    else:
        result_list[0] = get_attr_value(path+"psu_mfr_model")
        result_list[1] = get_attr_value(path+"psu_vin")
        result_list[2] = get_attr_value(path+"psu_vout")   
        result_list[3] = get_attr_value(path+"psu_fan_speed_1")
        result_list[4] = get_attr_value(path+"psu_temp_1")
        result_list[5] = get_attr_value(path+"psu_pin")
        result_list[6] = get_attr_value(path+"psu_pout")
        result_list[7] = get_attr_value(path+"psu_iin")
        result_list[8] = get_attr_value(path+"psu_iout")
        result_list[9] = get_attr_value(path+"psu_iout_max")
        if result_list[0] != 'ERR':
            print ('    model: {}'.format(result_list[0]))
    
    if result_list[1] != 'ERR':
        vin = int(result_list[1])/1000.0
        print ('    Input Voltage:  {:+3.2f} V'.format(vin))
        
    if result_list[2] != 'ERR':
        vout = int(result_list[2])/1000.0
        print ('    Output Voltage:  {:+3.2f} V'.format(vout))
    
    if result_list[3] != 'ERR':
        fan_speed = int(result_list[3])
        print ('    Fan Speed:      {:3d} RPM'.format(fan_speed))   
    
    if result_list[4] != 'ERR':
        temperature = int(result_list[4])/1000.0
        print ('    Temperature:    {:+3.1f} C'.format(temperature))    
    
    if result_list[5] != 'ERR':
        pin = int(result_list[5])/1000000.0
        print ('    Input Power:    {:3.2f} W'.format(pin))    
    
    if result_list[6] != 'ERR':
        pout = int(result_list[6])/1000000.0
        print ('    Output Power:   {:3.2f} W'.format(pout))    
    
    if result_list[7] != 'ERR':
        iin = int(result_list[7])/1000.0
        print ('    Input Current:  {:+3.2f} A'.format(iin))    
    
    if result_list[8] != 'ERR':
        iout = int(result_list[8])/1000.0
        print ('    Output Current: {:+3.2f} A'.format(iout),end='')    
    
    if result_list[9] != 'ERR':
        max_iout = int(result_list[9])/1000.0
        print ('  (max = {:+3.2f} A)'.format(max_iout))
        
    print('')
    return

def psu_status():
    psu_path = []
    for x in range(0,MAX_PSU_NUM):
        if is_psu_present(x+1):
            print("PSU{} present".format(x+1))
            if bmc_is_exist():
                show_psu_status(POWER_SYSFILE_PATH + 'psu_module_{}'.format(x+1))
            else:
                psu_path = get_psu_path()
                show_psu_status(psu_path[x])

    return


def main():
    """
    Usage: %(scriptName)s command object

    command:
        fan_status     : display fans status(present/power good)
    """

    if len(sys.argv)<2:
        print (main.__doc__)

    for arg in sys.argv[1:]:
        if arg == 'fan_status':
            fan_status()
            fan_present()
            fan_power()
            fan_speed()
        elif arg == 'sensor_status':
            sensors_temp()
            sensors_status()
            psu_status()
            
            
        else:
            print (main.__doc__)

if __name__ == "__main__":
    main()
