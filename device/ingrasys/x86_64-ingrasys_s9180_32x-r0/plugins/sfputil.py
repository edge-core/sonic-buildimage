# sfputil.py
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
    PORT_END = 33
    SFP_PORT_START = 32
    PORTS_IN_BLOCK = 34

    BASE_DIR_PATH = "/sys/class/gpio/gpio{0}/direction"
    BASE_VAL_PATH = "/sys/class/gpio/gpio{0}/value"

    _port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
        0: 10,
        1: 9,
        2: 12,
        3: 11,
        4: 14,
        5: 13,
        6: 16,
        7: 15,
        8: 18,
        9: 17,
        10: 20,
        11: 19,
        12: 22,
        13: 21,
        14: 24,
        15: 23,
        16: 26,
        17: 25,
        18: 28,
        19: 27,
        20: 30,
        21: 29,
        22: 32,
        23: 31,
        24: 34,
        25: 33,
        26: 36,
        27: 35,
        28: 38,
        29: 37,
        30: 40,
        31: 39,
        32: 45,
        33: 46
    }

    abs_to_gpio_mapping = {
        0: 241,
        1: 240,
        2: 243,
        3: 242,
        4: 245,
        5: 244,
        6: 247,
        7: 246,
        8: 249,
        9: 248,
        10: 251,
        11: 250,
        12: 253,
        13: 252,
        14: 255,
        15: 254,
        16: 225,
        17: 224,
        18: 227,
        19: 226,
        20: 229,
        21: 228,
        22: 231,
        23: 230,
        24: 233,
        25: 232,
        26: 235,
        27: 234,
        28: 237,
        29: 236,
        30: 239,
        31: 238,
        32: 177,
        33: 176
    }

    lpmode_to_gpio_mapping = {
        0: 161,
        1: 160,
        2: 163,
        3: 162,
        4: 165,
        5: 164,
        6: 167,
        7: 166,
        8: 169,
        9: 168,
        10: 171,
        11: 170,
        12: 173,
        13: 172,
        14: 175,
        15: 174,
        16: 145,
        17: 144,
        18: 147,
        19: 146,
        20: 149,
        21: 148,
        22: 151,
        23: 150,
        24: 153,
        25: 152,
        26: 155,
        27: 154,
        28: 157,
        29: 156,
        30: 159,
        31: 158
    }

    reset_to_gpio_mapping = {
        0: 129,
        1: 128,
        2: 131,
        3: 130,
        4: 133,
        5: 132,
        6: 135,
        7: 134,
        8: 137,
        9: 136,
        10: 139,
        11: 138,
        12: 141,
        13: 140,
        14: 143,
        15: 142,
        16: 113,
        17: 112,
        18: 115,
        19: 114,
        20: 117,
        21: 116,
        22: 119,
        23: 118,
        24: 121,
        25: 120,
        26: 123,
        27: 122,
        28: 125,
        29: 124,
        30: 127,
        31: 126
    }

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
    @property
    def sfp_port_start(self):
        return self.SFP_PORT_START

    def __init__(self):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = "/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom"

        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        try:
            abs_device_file = self.BASE_VAL_PATH.format(
                    self.abs_to_gpio_mapping[port_num])
            val_file = open(abs_device_file)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = val_file.readline().rstrip()
        val_file.close()

        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.sfp_port_start: # TBD
            return False

        try:
            lpmode_val_device_file = self.BASE_VAL_PATH.format(
                    self.lpmode_to_gpio_mapping[port_num])
            val_file = open(lpmode_val_device_file)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = val_file.readline().rstrip()
        val_file.close()

        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.sfp_port_start: # TBD
            return False

        try:
            lpmode_val_device_file = self.BASE_VAL_PATH.format(
                    self.lpmode_to_gpio_mapping[port_num])
            val_file = open(lpmode_val_device_file, "w")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        val_file.write("1" if lpmode is True else "0")
        val_file.close()

        return True

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.sfp_port_start: # TBD
            return False

        try:
            reset_val_device_file = self.BASE_VAL_PATH.format(
                    self.reset_to_gpio_mapping[port_num])
            val_file = open(reset_val_device_file, "w")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        val_file.write("1")
        val_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        try:
            reset_val_device_file = self.BASE_VAL_PATH.format(
                    self.reset_to_gpio_mapping[port_num])
            val_file = open(reset_val_device_file, "w")
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        val_file.write("0")
        val_file.close()

        return True
