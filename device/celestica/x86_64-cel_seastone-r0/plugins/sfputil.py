#!/usr/bin/env python
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
    PORT_END = 31
    PORTS_IN_BLOCK = 32

    _port_to_eeprom_mapping = {}
    qsfp_ports = range(0, PORTS_IN_BLOCK + 1)

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return range(0, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def __init__(self):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/bus/i2c/devices/i2c-{0}/{0}-0050/eeprom'

        for x in range(self.PORT_START, self.PORT_END + 1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format( x + 26 )
        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        raise NotImplementedError

    def get_low_power_mode(self, port_num):
        raise NotImplementedError

    def set_low_power_mode(self, port_num, lpmode):
        raise NotImplementedError

    def reset(self, port_num):
        raise NotImplementedError

