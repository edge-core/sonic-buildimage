#!/usr/bin/env python

# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    from socket import *
    from select import *
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


def DBG_PRINT(str):
    print str + "\n"


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def sfp_base(self):
        return self.SFP_BASE

    @property
    def qsfp_ports(self):
        return ()

    @property
    def port_to_eeprom_mapping(self):
        return self.eeprom_mapping

    def is_logical_port(self, port_name):
        return True

    def get_logical_to_physical(self, port_name):
        if not port_name.startswith(self.SONIC_PORT_NAME_PREFIX):
            return None

        port_idx = int(port_name[len(self.SONIC_PORT_NAME_PREFIX):])

        return [port_idx]

    def get_eeprom_data(self, port):
        ret = None
        port_num = self.get_logical_to_physical(port)[0]
        if port_num < self.port_start or port_num > self.port_end:
            return ret
        if port_num < self.sfp_base:
            return ret
        try:
            with open(self.eeprom_mapping[port_num], 'r') as eeprom_file:
                ret = eeprom_file.read()
        except IOError as e:
            DBG_PRINT(str(e))

        return ret

    # todo
    #def _get_port_eeprom_path(self, port_num, devid):
    #    pass

    def __init__(self):
        self.SONIC_PORT_NAME_PREFIX = "Ethernet"
        self.PORT_START = 1
        self.PORT_END = 52
	self.SFP_BASE = 49
        self.PORTS_IN_BLOCK = 52

        self.eeprom_mapping = {}
        self.f_sfp_present = "/sys/class/sfp/sfp{}/sfp_presence"
        self.f_sfp_enable = "/sys/class/sfp/sfp{}/sfp_enable"
	for x in range(self.port_start, self.sfp_base):
            self.eeprom_mapping[x] = None
        for x in range(self.sfp_base, self.port_end + 1):
            self.eeprom_mapping[x] = "/sys/class/sfp/sfp{}/sfp_eeprom".format(x - self.sfp_base + 1)
        self.presence = {}
        for x in range(self.sfp_base, self.port_end + 1):
            self.presence[x] = False;

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False
        if port_num < self.sfp_base:
            return False
        try:
            with open(self.f_sfp_present.format(port_num - self.sfp_base + 1), 'r') as sfp_file:
                return 1 == int(sfp_file.read())
        except IOError as e:
            DBG_PRINT(str(e))

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        return False

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        return False

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        return False

    def get_transceiver_change_event(self, timeout=0):
        port_dict = {}
        while True:
            for x in range(self.sfp_base, self.port_end + 1):
                presence = self.get_presence(x)
                if presence != self.presence[x]:
                    self.presence[x] = presence
                    port_dict[x] = presence
                    return True, port_dict
            time.sleep(0.5)
