#!/usr/bin/env python

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase 
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    PORT_START = 0
    PORT_END = 55
    QSFP_PORT_START = 48
    PORTS_IN_BLOCK = 56

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
         0 : 32,
         1 : 33,
         2 : 34,
         3 : 35,
         4 : 36,
         5 : 37,
         6 : 38,
         7 : 39,
         8 : 40,
         9 : 41,
        10 : 42,
        11 : 43,
        12 : 44,
        13 : 45,
        14 : 46,
        15 : 47,
        16 : 48,
        17 : 49,
        18 : 50,
        19 : 51,
        20 : 52,
        21 : 53,
        22 : 54,
        23 : 55,
        24 : 56,
        25 : 57,
        26 : 58,
        27 : 59,
        28 : 60,
        29 : 61,
        30 : 62,
        31 : 63,
        32 : 64,
        33 : 65,
        34 : 66,
        35 : 67,
        36 : 68,
        37 : 69,
        38 : 70,
        39 : 71,
        40 : 72,
        41 : 73,
        42 : 74,
        43 : 75,
        44 : 76,
        45 : 77,
        46 : 78,
        47 : 79,
        48 : 80,#QSFP49
        49 : 81,#QSFP50
        50 : 82,#QSFP51
        51 : 83,#QSFP52
        52 : 84,#QSFP53
        53 : 85,#QSFP54
        54 : 86,#QSFP55
        55 : 87,#QSFP56
    }

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def qsfp_port_start(self):
        return self.QSFP_PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping

    def __init__(self):
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/eeprom'
        for x in range(0, self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(self._port_to_i2c_mapping[x])
        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.PORT_START or port_num > self.PORT_END:
            return False

        try:
            if port_num < 48:
                reg_file = open("/sys/class/cpld-sfp28/port-"+str(port_num+1)+"/pre_n")
            else:
                reg_file = open("/sys/class/gpio/gpio"+str((port_num-48)*4+34)+"/value")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = reg_file.readline().rstrip()
        if port_num < 48:
            if reg_value == '1':
                return True
        else:
            if reg_value == '0':
                return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open("/sys/class/gpio/gpio"+str((port_num-48)*4+35)+"/value")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = int(reg_file.readline().rstrip())

        if reg_value == 0:
            return False

        return True

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open("/sys/class/gpio/gpio"+str((port_num-48)*4+35)+"/value", "r+")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = int(reg_file.readline().rstrip())

        # LPMode is active high; set or clear the bit accordingly
        if lpmode is True:
            reg_value = 1
        else:
            reg_value = 0

        reg_file.write(hex(reg_value))
        reg_file.close()

        return True

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open("/sys/class/gpio/gpio"+str((port_num-48)*4+32)+"/value", "r+")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = 0
        reg_file.write(hex(reg_value))
        reg_file.close()

        # Sleep 2 second to allow it to settle
        time.sleep(2)

        # Flip the value back write back to the register to take port out of reset
        try:
            reg_file = open("/sys/class/gpio/gpio"+str((port_num-48)*4+32)+"/value", "r+")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = 1
        reg_file.write(hex(reg_value))
        reg_file.close()

        return True

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError
