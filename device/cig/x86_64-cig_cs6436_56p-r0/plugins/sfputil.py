#!/usr/bin/env python

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase 
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    _port_start = 0
    _port_end = 55
    _qsfp_port_start = 48
    _ports_in_block = 55

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
        0 : 8,
        1 : 9,
        2 : 10,
        3 : 11,
        4 : 12,
        5 : 13,
        6 : 14,
        7 : 15,
        8 : 16,
        9 : 17,
        10 : 18,
        11 : 19,
        12 : 20,
        13 : 21,
        14 : 22,
        15 : 23,
        16 : 24,
        17 : 25,
        18 : 26,
        19 : 27,
        20 : 28,
        21 : 29,
        22 : 30,
        23 : 31,
        24 : 32,
        25 : 33,
        26 : 34,
        27 : 35,
        28 : 36,
        29 : 37,
        30 : 38,
        31 : 39,
        32 : 40,
        33 : 41,
        34 : 42,
        35 : 43,
        36 : 44,
        37 : 45,
        38 : 46,
        39 : 47,
        40 : 48,
        41 : 49,
        42 : 50,
        43 : 51,
        44 : 52,
        45 : 53,
        46 : 54,
        47 : 55,
        48 : 56,
        49 : 57,
        50 : 58,
        51 : 59,
        52 : 60,
        53 : 61,
        54 : 62,
        55 : 63,         
    }

    _qsfp_ports = range(_qsfp_port_start, _ports_in_block + 1)

    def __init__(self):
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/sfp_eeprom'
        for x in range(self._port_start, self._port_end + 1):
            port_eeprom_path = eeprom_path.format(self._port_to_i2c_mapping[x])
            self._port_to_eeprom_mapping[x] = port_eeprom_path
                
            SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = "/sys/bus/i2c/devices/{0}-0050/sfp_port_reset"
        port_ps = path.format(self._port_to_i2c_mapping[port_num])
          
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        #toggle reset
        reg_file.seek(0)
        reg_file.write('1')
        time.sleep(1)
        reg_file.seek(0)
        reg_file.write('0')
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
        port_ps = path.format(self._port_to_i2c_mapping[port_num])

          
        try:
            reg_file = open(port_ps)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = reg_file.readline().rstrip()
        if reg_value == '1':
            return True

        return False

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end

    @property
    def qsfp_ports(self):
        return self._qsfp_ports

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping
