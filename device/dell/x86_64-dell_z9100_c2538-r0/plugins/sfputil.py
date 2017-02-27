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
        0: 18,
        1: 19,
        2: 20,
        3: 21,
        4: 22,
        5: 23,
        6: 24,
        7: 25,
        8: 26,
        9: 27,
        10: 28,
        11: 29,
        12: 31,
        13: 30,
        14: 33,
        15: 32,
        16: 34,
        17: 35,
        18: 36,
        19: 37,
        20: 38,
        21: 39,
        22: 40,
        23: 41,
        24: 42,
        25: 43,
        26: 44,
        27: 45,
        28: 46,
        29: 47,
        30: 48,
        31: 49
    }

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom'
        for x in range(0, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        sfputilbase.__init__(self, port_num)
