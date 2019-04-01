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
    PORT_END = 128
    
    BASE_OOM_PATH = "/sys/bus/i2c/devices/{0}-0050/"
    
    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END
   
    @property
    def qsfp_ports(self):
        return range(self.PORT_START, self.PORT_END + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def sfp_map(self, index):
        port = index + 1
        base = ((port-1)/8*8) + 10
        index = (port - 1) % 8
        index = 7 - index
        if (index%2):
            index = index -1
        else:
            index = index +1
        bus = base + index
        return bus


    def __init__(self):
        eeprom_path = self.BASE_OOM_PATH + "eeprom"
        
        for x in range(0, self.port_end+1):
            bus = self.sfp_map(x)
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                bus)

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        eeprom_path = self.port_to_eeprom_mapping[port_num]
        with open(eeprom_path) as f:
            try:
                content = f.read(1)
            except IOError as e:
                #Not print any error, for if any, treat as Not present.
                return False
        return True

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
