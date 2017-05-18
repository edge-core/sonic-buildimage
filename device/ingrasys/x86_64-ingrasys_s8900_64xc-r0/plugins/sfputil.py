#!/usr/bin/env python

import subprocess

try:
    from sonic_sfp.sfputilbase import sfputilbase
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

i2c_set = 'i2cset'
cpld_addr = '0x33'
mux_reg = '0x4A'

class sfputil(sfputilbase):
    """Platform specific sfputil class"""

    port_start = 0
    port_end = 63
    ports_in_block = 64

    port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
           0: [2,1],
           1: [2,2],
           2: [2,3],
           3: [2,4],
           4: [2,5],
           5: [2,6],
           6: [2,7],
           7: [2,8],
           8: [2,9],
           9: [2,10],
           10: [2,11],
           11: [2,12],
           12: [2,13],
           13: [2,14],
           14: [2,15],
           15: [2,16],
           16: [2,17],
           17: [2,18],
           18: [2,19],
           19: [2,20],
           20: [2,21],
           21: [2,22],
           22: [2,23],
           23: [2,24],
           24: [3,1],
           25: [3,2],
           26: [3,3],
           27: [3,4],
           28: [3,5],
           29: [3,6],
           30: [3,7],
           31: [3,8],
           32: [3,9],
           33: [3,10],
           34: [3,11],
           35: [3,12],
           36: [3,13],
           37: [3,14],
           38: [3,15],
           39: [3,16],
           40: [3,17],
           41: [3,18],
           42: [3,19],
           43: [3,20],
           44: [3,21],
           45: [3,22],
           46: [3,23],
           47: [3,24],
           48: [4,1],
           49: [4,2],
           50: [4,3],
           51: [4,4],
           52: [4,5],
           53: [4,6],
           54: [4,7],
           55: [4,8],
           56: [4,9],
           57: [4,10],
           58: [4,11],
           59: [4,12],
           60: [4,13],
           61: [4,14],
           62: [4,15],
           63: [4,16]
    }


    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        i2c_bus = self.port_to_i2c_mapping[port_num][0]
        sfp_idx = self.port_to_i2c_mapping[port_num][1]
        proc = subprocess.Popen([i2c_set, '-y', str(i2c_bus), cpld_addr, mux_reg, str(sfp_idx)],
                                stdout=subprocess.PIPE,
                                shell=False,
                                stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        proc.wait()

        eeprom_path = '/sys/class/i2c-adapter/i2c-{0[0]}/{0[0]}-0050/eeprom'
        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        sfputilbase.__init__(self, port_num)
