# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 0
    PORT_END = 31
    PORTS_IN_BLOCK = 32
    
    BASE_OOM_PATH = "/sys/bus/i2c/devices/{0}-0050/"
    BASE_CPLD_PATH = "/sys/bus/i2c/devices/11-0060/"
    
    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           0: [1, 29],
           1: [2, 30],
           2: [3, 31],
           3: [4, 32],
           4: [5, 34],
           5: [6, 33],
           6: [7, 36],
           7: [8, 35],
           8: [9, 25],
           9: [10, 26],
           10: [11, 27],
           11: [12, 28],
           12: [14, 37],
           13: [15, 38],
           14: [16, 39],
           15: [17, 40],
           16: [18, 41],
           17: [19, 42],
           18: [20, 43],
           19: [21, 44],
           20: [22, 53],
           21: [23, 54],
           22: [24, 55],
           23: [25, 56],
           24: [26, 45],
           25: [27, 46],
           26: [28, 47],
           27: [29, 48],
           28: [30, 49],
           29: [31, 50],
           30: [32, 51],
           31: [33, 52],              
           }

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END
   
    @property
    def qsfp_ports(self):
        return range(self.PORT_START, self.PORTS_IN_BLOCK + 1)

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

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False
       
        present_path = self.BASE_CPLD_PATH + "module_present_" + str(port_num+1)
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

    def get_low_power_mode(self, port_num): 
      raise NotImplementedError
        
    def set_low_power_mode(self, port_num, lpmode):
        raise NotImplementedError

    def reset(self, port_num):
        if port_num < self.port_start or port_num > self.port_end:
            return False
         
        mod_rst_path = self.BASE_CPLD_PATH + "module_reset_" + str(port_num+1)
        self.__port_to_mod_rst = mod_rst_path
        try:
            reg_file = open(self.__port_to_mod_rst, 'r+')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)          
            return False

        reg_value = '1'

        reg_file.write(reg_value)
        reg_file.close()
        
        return True