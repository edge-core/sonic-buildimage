#! /usr/bin/python

try:
   from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class SfpUtil(SfpUtilBase):
    """Platform specific sfputil class"""

    _port_start = 0
    _port_end = 31
    ports_in_block = 32


    _port_to_eeprom_mapping = {}

    _qsfp_ports = range(0, ports_in_block + 1)
   
    def __init__(self):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/sfp_eeprom'
        for x in range(self.port_start, self.port_end + 1):
            self._port_to_eeprom_mapping[x] = eeprom_path.format(x + 18)
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        raise NotImplementedErro

    def set_low_power_mode(self, port_nuM, lpmode):
        raise NotImplementedErro

    def get_low_power_mode(self, port_num):
        raise NotImplementedErro

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = "/sys/bus/i2c/devices/{0}-0050/sfp_is_present"
        port_ps = path.format(port_num+18)


        try:
            reg_file = open(port_ps)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = reg_file.readline().rstrip()
        if reg_value == '1':
            return True

        return False

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end

    @property
    def qsfp_ports(self):
        return range(0, self.ports_in_block + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping
