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
        0: 22,
        1: 23,
        2: 24,
        3: 25,
        4: 26,
        5: 27,
        6: 28,
        7: 29,
        8: 30,
        9: 31,
        10: 32,
        11: 33,
        12: 34,
        13: 35,
        14: 36,
        15: 37,
        16: 6,
        17: 7,
        18: 8,
        19: 9,
        20: 10,
        21: 11,
        22: 12,
        23: 13,
        24: 14,
        25: 15,
        26: 16,
        27: 17,
        28: 18,
        29: 19,
        30: 20,
        31: 21
    }

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom'
        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        sfputilbase.__init__(self, port_num)
