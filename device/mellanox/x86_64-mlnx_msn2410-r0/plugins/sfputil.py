#! /usr/bin/python

try:
    from sonic_sfp.sfputilbase import sfputilbase
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class sfputil(sfputilbase):
    """Platform specific sfputil class"""

    port_start = 0
    port_end = 55
    ports_in_block = 56

    eeprom_offset = 1

    port_to_eeprom_mapping = {}

    _qsfp_ports = range(0, ports_in_block + 1)

    def __init__(self, port_num):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/bsp/qsfp/qsfp{0}'
        for x in range(0, self.port_end + 1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(x + self.eeprom_offset)
        sfputilbase.__init__(self, port_num)
        
