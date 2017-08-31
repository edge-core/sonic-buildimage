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
    PORT_END = 31
    PORTS_IN_BLOCK = 32

    BASE_DIR_PATH = "/sys/class/gpio/gpio{0}/direction"
    BASE_VAL_PATH = "/sys/class/gpio/gpio{0}/value"

    _port_to_eeprom_mapping = {}
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
        31: 238
    }

    lpmode_to_gpio_mapping = {
        0: 177,
        1: 176,
        2: 179,
        3: 178,
        4: 181,
        5: 180,
        6: 183,
        7: 182,
        8: 185,
        9: 184,
        10: 187,
        11: 186,
        12: 189,
        13: 188,
        14: 191,
        15: 190,
        16: 161,
        17: 160,
        18: 163,
        19: 162,
        20: 165,
        21: 164,
        22: 167,
        23: 166,
        24: 169,
        25: 168,
        26: 171,
        27: 170,
        28: 173,
        29: 172,
        30: 175,
        31: 174
    }

    reset_to_gpio_mapping = {
        0: 145,
        1: 144,
        2: 147,
        3: 146,
        4: 149,
        5: 148,
        6: 151,
        7: 150,
        8: 153,
        9: 152,
        10: 155,
        11: 154,
        12: 157,
        13: 156,
        14: 159,
        15: 158,
        16: 129,
        17: 128,
        18: 131,
        19: 130,
        20: 133,
        21: 132,
        22: 135,
        23: 134,
        24: 137,
        25: 136,
        26: 139,
        27: 138,
        28: 141,
        29: 140,
        30: 143,
        31: 142
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
        if port_num < self.port_start or port_num > self.port_end:
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
        if port_num < self.port_start or port_num > self.port_end:
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
        if port_num < self.port_start or port_num > self.port_end:
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
