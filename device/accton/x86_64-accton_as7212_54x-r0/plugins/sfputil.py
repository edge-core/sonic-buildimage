#!/usr/bin/env python

try:
    from sonic_sfp.sfputilbase import sfputilbase
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class sfputil(sfputilbase):
    """Platform specific sfputil class"""

    port_start = 0
    port_end = 31
    ports_in_block = 32

    port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
         9 : 18,
        10 : 19,
        11 : 20,
        12 : 21,
         1 : 22,
         2 : 23,
         3 : 24,
         4 : 25,
         6 : 26,
         5 : 27,
         8 : 28,
         7 : 29,
        13 : 30,
        14 : 31,
        15 : 32,
        16 : 33,
        17 : 34,
        18 : 35,
        19 : 36,
        20 : 37,
        25 : 38,
        26 : 39,
        27 : 40,
        28 : 41,
        29 : 42,
        30 : 43,
        31 : 44,
        32 : 45,
        21 : 46,
        22 : 47,
        23 : 48,
        24 : 49,
    }

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/sfp_eeprom'
        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x+1])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        sfputilbase.__init__(self, port_num)
