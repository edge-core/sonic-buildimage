#!/usr/bin/env python

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase 
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    _port_start = 0
    _port_end = 63
    ports_in_block = 64

    _port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
        61 : 25,
        62 : 26,
        63 : 27,
        64 : 28,
        55 : 29,
        56 : 30,
        53 : 31,
        54 : 32,
        9  : 33,
        10 : 34,
        11 : 35,
        12 : 36,
        1  : 37,
        2  : 38,
        3  : 39,
        4  : 40,
        6  : 41,
        5  : 42,
        8  : 43,
        7  : 44,
        13 : 45,
        14 : 46,
        15 : 47,
        16 : 48,
        17 : 49,
        18 : 50,
        19 : 51,
        20 : 52,
        25 : 53,
        26 : 54,
        27 : 55,
        28 : 56,
        29 : 57,
        30 : 58,
        31 : 59,
        32 : 60,
        21 : 61,
        22 : 62,
        23 : 63,
        24 : 64,
        41 : 65,
        42 : 66,
        43 : 67,
        44 : 68,
        33 : 69,
        34 : 70,
        35 : 71,
        36 : 72,
        45 : 73,
        46 : 74,
        47 : 75,
        48 : 76,
        37 : 77,
        38 : 78,
        39 : 79,
        40 : 80,
        57 : 81,
        58 : 82,
        59 : 83,
        60 : 84,
        49 : 85,
        50 : 86,
        51 : 87,
        52 : 88,}

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self):
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/sfp_eeprom'
        for x in range(0, self._port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x+1])
            self._port_to_eeprom_mapping[x] = port_eeprom_path
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False
	path = "/sys/bus/i2c/devices/19-0060/module_reset_{0}"
        port_ps = path.format(port_num+1)
          
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        #HW will clear reset after set.
        reg_file.seek(0)
        reg_file.write('1')
        reg_file.close()
        return True

    def set_low_power_mode(self, port_nuM, lpmode):
        raise NotImplementedError

    def get_low_power_mode(self, port_num):
        raise NotImplementedError
        
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = "/sys/bus/i2c/devices/{0}-0050/sfp_is_present"
        port_ps = path.format(self.port_to_i2c_mapping[port_num+1])

          
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


