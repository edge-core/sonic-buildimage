# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    import os
    import string
    from ctypes import create_string_buffer
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 0
    PORT_END = 31
    PORTS_IN_BLOCK = 32
    QSFP_PORT_START = 0
    QSFP_PORT_END = 32

    I2C_DEV_PATH = "/sys/bus/i2c/devices/"
    BASE_VAL_PATH = "/sys/class/i2c-adapter/i2c-{0}/{1}-0050/"
    BASE_OOM_PATH = "/sys/bus/i2c/devices/{0}-0050/"
    CPLD_ADDRESS = ['-0062', '-0064']

    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           0: [1, 2],
           1: [2, 3],
           2: [3, 4],
           3: [4, 5],
           4: [5, 6],
           5: [6, 7],
           6: [7, 8],
           7: [8, 9],
           8: [9, 10],            
           9: [10, 11],
           10: [11, 12],
           11: [12, 13],
           12: [13, 14],
           13: [14, 15],
           14: [15, 16],
           15: [16, 17],
           16: [17, 18],
           17: [18, 19],
           18: [19, 20],
           19: [20, 21],            
           20: [21, 22],
           21: [22, 23],
           22: [23, 24],
           23: [24, 25],
           24: [25, 26],
           25: [26, 27],
           26: [27, 28],
           27: [28, 29],
           28: [29, 30],
           29: [30, 31],
           30: [31, 32],
           31: [32, 33],
           32: [33, 34],
           33: [34, 35],
           34: [35, 36],
           35: [36, 37],
           36: [37, 38],
           37: [38, 39],
           38: [39, 40],
           39: [40, 41],
           40: [41, 42],
           41: [42, 43],
           42: [43, 44],
           43: [44, 45],
           44: [45, 46],
           45: [46, 47],
           46: [47, 48],
           47: [48, 49],
           48: [49, 50],#QSFP49
           49: [49, 50],
           50: [49, 50],
           51: [49, 50],            
           52: [50, 52],#QSFP50
           53: [50, 52],
           54: [50, 52],
           55: [50, 52],
           56: [51, 54],#QSFP51
           57: [51, 54],
           58: [51, 54],
           59: [51, 54],
           60: [52, 51],#QSFP52
           61: [52, 51],
           62: [52, 51],
           63: [52, 51], 
           64: [53, 53], #QSFP53
           65: [53, 53],
           66: [53, 53],
           67: [53, 53],
           68: [54, 55],#QSFP54          
           69: [54, 55],          
           70: [54, 55],          
           71: [54, 55],          
           }

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_port_start(self):
        return self.QSFP_PORT_START

    @property
    def qsfp_port_end(self):
        return self.QSFP_PORT_END
    
    @property
    def qsfp_ports(self):
        return range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def __init__(self):
        eeprom_path = self.BASE_OOM_PATH + "eeprom"

        for x in range(0, self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                self._port_to_i2c_mapping[x][1]
                )

        SfpUtilBase.__init__(self)

    def get_cpld_dev_path(self, port_num):
        if port_num < 16:
            cpld_num = 0
        else:
            cpld_num = 1
        
        #cpld can be at either bus 0 or bus 1.
        cpld_path = self.I2C_DEV_PATH + str(0) + self.CPLD_ADDRESS[cpld_num]
        if not os.path.exists(cpld_path):        
            cpld_path = self.I2C_DEV_PATH + str(1) + self.CPLD_ADDRESS[cpld_num]
        return cpld_path
        
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        cpld_path = self.get_cpld_dev_path(port_num)
        present_path = cpld_path + "/module_present_" 
        present_path += str(self._port_to_i2c_mapping[port_num][0])

        self.__port_to_is_present = present_path

        try:
            val_file = open(self.__port_to_is_present)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)          
            return False

        content = val_file.readline().rstrip()
        val_file.close()

        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def get_low_power_mode_cpld(self, port_num):   
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False
         
        cpld_path = self.get_cpld_dev_path(port_num)
        _path = cpld_path + "/module_lp_mode_" 
        _path += str(self._port_to_i2c_mapping[port_num][0])

        try:
            reg_file = open(_path)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)          
            return False

        content = reg_file.readline().rstrip()
        reg_file.close()

        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def get_low_power_mode(self, port_num):             
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False
        
        if not self.get_presence(port_num):
            return False

        try:
            eeprom = None

            eeprom = open(self.port_to_eeprom_mapping[port_num], mode="rb", buffering=0)
            eeprom.seek(93)
            lpmode = ord(eeprom.read(1))

            if not (lpmode & 0x1): # 'Power override' bit is 0
                return self.get_low_power_mode_cpld(port_num)
            else:
                if ((lpmode & 0x2) == 0x2):
                    return True # Low Power Mode if "Power set" bit is 1
                else:
                    return False # High Power Mode if "Power set" bit is 0
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    def set_low_power_mode(self, port_num, lpmode):
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False    

        try:
            eeprom = None

            if not self.get_presence(port_num):
                return False # Port is not present, unable to set the eeprom

            # Fill in write buffer
            regval = 0x3 if lpmode else 0x1 # 0x3:Low Power Mode, 0x1:High Power Mode
            buffer = create_string_buffer(1)
            buffer[0] = chr(regval)

            # Write to eeprom
            eeprom = open(self.port_to_eeprom_mapping[port_num], mode="r+b", buffering=0)
            eeprom.seek(93)
            eeprom.write(buffer[0])
            return True
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    def reset(self, port_num):
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False
         
        cpld_path = self.get_cpld_dev_path(port_num)
        _path = cpld_path + "/module_reset_" 
        _path += str(self._port_to_i2c_mapping[port_num][0])

        try:
            reg_file = open(_path, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)          
            return False

        reg_file.seek(0)
        reg_file.write('1')
        time.sleep(1)
        reg_file.seek(0)
        reg_file.write('0')
        reg_file.close()
        
        return True

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError

