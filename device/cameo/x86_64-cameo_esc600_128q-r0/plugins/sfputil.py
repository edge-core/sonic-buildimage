#!/usr/bin/env python

try:
    import os
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase 
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

attr_path = '/sys/class/hwmon/hwmon2/device/'
qsfp_sysfile_path = '/sys/bus/i2c/devices/{}-0032/'
i2c_bus_base = 0

class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    _port_start = 0
    _port_end = 127
    _port_in_block = 128
    _port_to_eeprom_mapping = {}
    _global_port_pres_dict = {}
    _port_position_mapping = []

    def __init__(self):
        self.create_port_position_mapping()
        eeprom_path = "/sys/bus/i2c/devices/{0}-0050/eeprom"
        for x in range(self._port_start, self._port_end + 1):
            port_eeprom_path = eeprom_path.format(self._port_position_mapping[x][2])
            self._port_to_eeprom_mapping[x] = port_eeprom_path

        self.init_global_port_presence()        
        SfpUtilBase.__init__(self)

    def get_attr_value(self,attr_path):
        retval = 'ERR'
        try:
            with open(attr_path, 'r') as fd:
                retval = fd.read()
        except Exception as error:
            print("Unable to open ", attr_path, " file !")
            return retval

        retval = retval.rstrip('\r\n')
        fd.close()
        return retval

    def bmc_is_exist(self):
        value = ''
        bmc_filePath = '/sys/class/hwmon/hwmon2/device/ESC600_SYS/bmc_present'
        if os.path.exists(bmc_filePath):
           value = self.get_attr_value(bmc_filePath)
           if value.find('not') < 0:
                return True
           else:
                return False
        else:
           return False

    def get_inserted_slots(self):
        """ return list of inserted slots """
        path = attr_path+'ESC600_Module/module_insert'
        try:
          reg_file = open(path, 'r')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False 
        
        text_lines = reg_file.readlines()
        reg_file.close()
        
        slots = []
        for line in text_lines:
            if "is present" in line:
                slots.append(int(filter(str.isdigit, line)))
        
        return slots

    def create_port_position_mapping(self):
        inserted_slots = []
        ports_in_slots = [0]*8
        # record inserted slots
        inserted_slots = self.get_inserted_slots()
        
        # record the numbers of port on each slot
        for slot in inserted_slots:
            path = qsfp_sysfile_path.format(slot+i2c_bus_base) + 'portnum'
            ports_in_slots[slot-1] = int(self.get_attr_value(path))

        # mapping
        nport = 0
        if self.bmc_is_exist():
            PATH_71_BUS_BASE = 9
        else:
            PATH_71_BUS_BASE = 33
            
        sfp_bus = PATH_71_BUS_BASE
        for i in range(0,8):
            for x in range(0,ports_in_slots[i]):
                self._port_position_mapping.append((i, x+1, sfp_bus+x))
                nport = nport + 1
            
            if ports_in_slots[i] == 4:
                sfp_bus = sfp_bus + 8
            elif ports_in_slots[i] == 16:
                sfp_bus = sfp_bus + 16

        self._port_end = nport-1


    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        pos = self._port_position_mapping[port_num]
        path = qsfp_sysfile_path.format(pos[0]+i2c_bus_base+1)+'QSFP_reset_{}'.format(pos[1])
        try:
            reg_file = open(path, 'w')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False

        #toggle reset
        #reg_file.seek(0)
        reg_file.write(str(port_num+1))
        #time.sleep(1)
        #reg_file.seek(0)
        #reg_file.write('0')
        reg_file.close()
        return True

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        pos = self._port_position_mapping[port_num]
        path = qsfp_sysfile_path.format(pos[0]+i2c_bus_base+1)+'QSFP_low_power_{}'.format(pos[1])

        try:
            reg_file = open(path, 'w')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False

        # the gpio pin is ACTIVE_HIGH
        if lpmode is True:
            val = "1"
        else:
            val = "0"

        # write value to gpio
        reg_file.seek(0)
        reg_file.write(val)
        reg_file.close()

        return True

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        pos = self._port_position_mapping[port_num]
        path = qsfp_sysfile_path.format(pos[0]+i2c_bus_base+1)+'QSFP_low_power_{}'.format(pos[1])

        res = self.get_attr_value(path)
        if res == 'ERR':
            return False
          
        if int(res) == 1:
            return True

        return False
        
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        pos = self._port_position_mapping[port_num]
        path = qsfp_sysfile_path.format(pos[0]+i2c_bus_base+1)+'QSFP_present_{}'.format(pos[1])
        res = self.get_attr_value(path)
        if res == 'ERR':
            return False

        if int(res) == 1:
            return True

        return False

    def init_global_port_presence(self):
        for port_num in range(self.port_start, (self.port_end + 1)):
            presence = self.get_presence(port_num)
            if(presence):
                self._global_port_pres_dict[port_num] = '1'
            else:
                self._global_port_pres_dict[port_num] = '0'  
 
    def get_transceiver_change_event(self, timeout=0):
        port_dict = {}
        while True:
            for port_num in range(self.port_start, (self.port_end + 1)):
                presence = self.get_presence(port_num)
                if(presence and self._global_port_pres_dict[port_num] == '0'):
                    self._global_port_pres_dict[port_num] = '1'
                    port_dict[port_num] = '1'
                elif(not presence and
                     self._global_port_pres_dict[port_num] == '1'):
                    self._global_port_pres_dict[port_num] = '0'
                    port_dict[port_num] = '0'

                if(len(port_dict) > 0):
                    return True, port_dict

            time.sleep(1)

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end

    @property
    def qsfp_ports(self):
        return range(0, self._port_in_block + 1)

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping
