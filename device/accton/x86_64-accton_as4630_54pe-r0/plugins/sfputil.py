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

     
    PORT_START = 48
    PORT_END = 53
    PORTS_IN_BLOCK = 54
    
    BASE_OOM_PATH = "/sys/bus/i2c/devices/{0}-0050/"
    BASE_CPLD_PATH = "/sys/bus/i2c/devices/3-0060/"
    
    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           48: [18],
           49: [19],              
           50: [20], 
           51: [21],
           52: [22],              
           53: [23], 
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
	    if x < 48:
                self.port_to_eeprom_mapping[x] = eeprom_path.format(0)
            else:
                self.port_to_eeprom_mapping[x] = eeprom_path.format(
                    self._port_to_i2c_mapping[x][0])

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
        raise NotImplementedError

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError
