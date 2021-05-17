#!/usr/bin/python

from __future__ import print_function
import os
import sys
import logging

FAN_NUM = 5
MAX_PSU_NUM = 4

fans_path       = '/sys/class/hwmon/hwmon2/device/ESC600_FAN/'
sensors_path    = '/sys/class/hwmon/hwmon2/device/ESC600_Sensor/'
cameo_psu_path  = '/sys/class/hwmon/hwmon2/device/ESC600_PSU/'

psu_path = [ '/sys/bus/i2c/devices/21-0058/',
             '/sys/bus/i2c/devices/21-0059/',
             '/sys/bus/i2c/devices/21-005a/',
             '/sys/bus/i2c/devices/21-005b/']

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
    bmc_filePath = '/sys/class/hwmon/hwmon2/device/ESC600_SYS/bmc_present'
    if os.path.exists(bmc_filePath):
       value = get_attr_value(bmc_filePath)
       if value.find('not') < 0:
            return True
       else:
            return False
    else:
       return False

def calc_mac_temp():
    value = ''
    try:
        if bmc_is_exist():
            mac_temp_string = get_attr_value(sensors_path+'mac_temp').split(' ')
            value = int(mac_temp_string[-1], 16)
            mac_sensor= (((value&0xFF)<<8)|((value&0xFF00)>>8)) /1000.0
        else:
            raw = get_attr_value('/sys/bus/i2c/devices/28-0068/iio:device0/in_voltage0_raw')
            scale = get_attr_value('/sys/bus/i2c/devices/28-0068/iio:device0/in_voltage0_scale')
            mac_sensor= int(raw,10)*float(scale)
    except Exception as e:
        print("Failed to get MAC sensor temp: {}".format(e.args[0]))
        return 0
    
    temp1 = -124.28 * mac_sensor * mac_sensor
    temp2 = -422.03 * mac_sensor
    temp_sensor = 384.62 + temp1 + temp2
    return round(temp_sensor,2)

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

def get_fan_alert(number):
    return

def get_fan_inner_rpm(number):
    return

def get_fan_outer_rpm(number):
    return

def sensors_status():
    print ('SENSOR STATUS:')
    if bmc_is_exist():
        sys_path = sensors_path + 'sensor_status'
        print_attr_value_lines(sys_path)

    return

def sensors_temp():
    print ('SENSOR TEMPERATURE:')
    print ('    MAC sensor temp:%.2f degrees (C)'% calc_mac_temp())
    
    if bmc_is_exist():
        sys_path = sensors_path + 'sensor_temp'
        print_attr_value_lines(sys_path)
        sys_path = sensors_path + 'module_temp'
        print_attr_value_lines(sys_path)
    
    return

def get_voltage():
    return

def fan_status():
    sys_path = fans_path + 'fan_status'
    print ('FAN STATUS:')
    print_attr_value_lines(sys_path)
    return

def fan_present():
    sys_path = fans_path + 'fan_insert'
    print ('FAN PRESENT:')
    print_attr_value_lines(sys_path)
    return

def fan_power():
    sys_path = fans_path + 'fan_power'
    print ('FAN POWER:')
    print_attr_value_lines(sys_path)
    return

def fan_speed():
    sys_path = fans_path + 'fan_speed_rpm'
    print ('FAN SPEED:')
    print_attr_value_lines(sys_path)
    return


def is_psu_present(psu_number):
    sys_path = cameo_psu_path + 'psu_present'
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


def show_psu_status_bmc(path):
    print_attr_value_lines(path)
    return   


def psu_status():

    for x in range(0,MAX_PSU_NUM):
        if is_psu_present(x+1):
            print("PSU{} present".format(x+1))
            if bmc_is_exist():
                show_psu_status(cameo_psu_path + 'psu_module_{}'.format(x+1))
            else:
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
