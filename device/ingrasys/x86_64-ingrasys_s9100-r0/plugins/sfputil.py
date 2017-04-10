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
        0: 11,
        1: 10,
        2: 13,
        3: 12,
        4: 15,
        5: 14,
        6: 17,
        7: 16,
        8: 19,
        9: 18,
        10: 21,
        11: 20,
        12: 23,
        13: 22,
        14: 25,
        15: 24,
        16: 27,
        17: 26,
        18: 29,
        19: 28,
        20: 31,
        21: 30,
        22: 33,
        23: 32,
        24: 35,
        25: 34,
        26: 37,
        27: 36,
        28: 39,
        29: 38,
        30: 41,
        31: 40
    }

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom'
        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        sfputilbase.__init__(self, port_num)
