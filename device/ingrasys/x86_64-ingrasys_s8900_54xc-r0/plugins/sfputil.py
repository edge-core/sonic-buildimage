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
    PORT_END = 53
    QSFP_PORT_START = 48
    PORTS_IN_BLOCK = 54
    
    BASE_DIR_PATH = "/sys/class/gpio/gpio{0}/direction"
    BASE_VAL_PATH = "/sys/class/gpio/gpio{0}/value"

    _port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
        0: 18,
        1: 19,
        2: 20,
        3: 21,
        4: 22,
        5: 23,
        6: 24,
        7: 25,
        8: 26,
        9: 27,
        10: 28,
        11: 29,
        12: 30,
        13: 31,
        14: 32,
        15: 33,
        16: 34,
        17: 35,
        18: 36,
        19: 37,
        20: 38,
        21: 39,
        22: 40,
        23: 41,
        24: 42,
        25: 43,
        26: 44,
        27: 45,
        28: 46,
        29: 47,
        30: 48,
        31: 49,
        32: 50,
        33: 51,
        34: 52,
        35: 53,
        36: 54,
        37: 55,
        38: 56,
        39: 57,
        40: 58,
        41: 59,
        42: 60,
        43: 61,
        44: 62,
        45: 63,
        46: 64,
        47: 65,
        48: 66,
        49: 67,
        50: 68,
        51: 69,
        52: 70,
        53: 71
    }

    abs_to_gpio_mapping = {
        0: 192,
        1: 193,
        2: 194,
        3: 195,
        4: 196,
        5: 197,
        6: 198,
        7: 199,
        8: 200,
        9: 201,
        10: 202,
        11: 203,
        12: 204,
        13: 205,
        14: 206,
        15: 207,
        16: 176,
        17: 177,
        18: 178,
        19: 179,
        20: 180,
        21: 181,
        22: 182,
        23: 183,
        24: 184,
        25: 185,
        26: 186,
        27: 187,
        28: 188,
        29: 189,
        30: 190,
        31: 191,
        32: 160,
        33: 161,
        34: 162,
        35: 163,
        36: 164,
        37: 165,
        38: 166,
        39: 167,
        40: 168,
        41: 169,
        42: 170,
        43: 171,
        44: 172,
        45: 173,
        46: 174,
        47: 175,
        48: 240,
        49: 241,
        50: 242,
        51: 243,
        52: 244,
        53: 245
    }

    lpmode_to_gpio_mapping = {
        48: 224,
        49: 225,
        50: 226,
        51: 227,
        52: 228,
        53: 229
    }

    reset_to_gpio_mapping = {
        48: 208,
        49: 209,
        50: 210,
        51: 211,
        52: 212,
        53: 213
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

        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.port_end:
            return False

        try:
            lpmode_val_device_file = self.BASE_VAL_PATH.format(
                    self.lpmode_to_gpio_mapping[port_num])
            val_file = open(lpmode_val_device_file)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
            
        content = val_file.readline().rstrip()
        
        # content is a string, either "0" or "1"
        if content == "1":
            return True

        return False

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.port_end:
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
        if port_num < self.qsfp_port_start or port_num > self.port_end:
            print "Error: unable to reset non-QSFP module: port %s" % str(port_num)
            return False
       
        try:
            print "port %s" % str(port_num)
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
