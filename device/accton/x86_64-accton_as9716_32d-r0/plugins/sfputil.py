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
    PORT_END = 33
    PORTS_IN_BLOCK = 34
    
    BASE_OOM_PATH = "/sys/bus/i2c/devices/{0}-0050/"
    BASE_CPLD1_PATH = "/sys/bus/i2c/devices/20-0061/"
    BASE_CPLD2_PATH = "/sys/bus/i2c/devices/21-0062/"
    
    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           0: [1, 25],
           1: [2, 26],
           2: [3, 27],
           3: [4, 28],
           4: [5, 29],
           5: [6, 30],
           6: [7, 31],
           7: [8, 32],
           8: [9, 33],
           9: [10, 34],
           10: [11, 35],
           11: [12, 36],
           12: [13, 37],
           13: [14, 38],
           14: [15, 39],
           15: [16, 40],
           16: [17, 41],
           17: [18, 42],
           18: [19, 43],
           19: [20, 44],
           20: [21, 45],
           21: [22, 46],
           22: [23, 47],
           23: [24, 48],
           24: [25, 49],
           25: [26, 50],
           26: [27, 51],
           27: [28, 52],
           28: [29, 53],
           29: [30, 54],
           30: [31, 55],
           31: [32, 56],              
           32: [33, 57], 
           33: [34, 58], 
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
        if port_num < 16 :
            present_path = self.BASE_CPLD1_PATH + "module_present_" + str(port_num+1)
        else:
            present_path = self.BASE_CPLD2_PATH + "module_present_" + str(port_num+1)
        self.__port_to_is_present = present_path

        content="0"
        try:
            val_file = open(self.__port_to_is_present)
            content = val_file.readline().rstrip()
            val_file.close()
        except IOError as e:
            print "Error: unable to access file: %s" % str(e)          
            return False

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
            
        if port_num < 16 :
            mod_rst_path = self.BASE_CPLD1_PATH + "module_reset_" + str(port_num+1)
        else:
            mod_rst_path = self.BASE_CPLD2_PATH + "module_reset_" + str(port_num+1)
        
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
        
    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError        