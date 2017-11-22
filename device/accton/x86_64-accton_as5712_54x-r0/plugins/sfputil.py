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
    PORT_END = 71
    PORTS_IN_BLOCK = 72
    QSFP_PORT_START = 72
    QSFP_PORT_END = 72

    BASE_VAL_PATH = "/sys/class/i2c-adapter/i2c-{0}/{1}-0050/"

    _port_to_is_present = {}

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           0: [2, 2],
           1: [3, 3],
           2: [4, 4],
           3: [5, 5],
           4: [6, 6],
           5: [7, 7],
           6: [8, 8],
           7: [9, 9],
           8: [10, 10],
           9: [11, 11],
           10: [12, 12],
           11: [13, 13],
           12: [14, 14],
           13: [15, 15],
           14: [16, 16],
           15: [17, 17],
           16: [18, 18],
           17: [19, 19],
           18: [20, 20],
           19: [21, 21],
           20: [22, 22],
           21: [23, 23],
           22: [24, 24],
           23: [25, 25],
           24: [26, 26],
           25: [27, 27],
           26: [28, 28],
           27: [29, 29],
           28: [30, 30],
           29: [31, 31],
           30: [32, 32],
           31: [33, 33],
           32: [34, 34],
           33: [35, 35],
           34: [36, 36],
           35: [37, 37],
           36: [38, 38],
           37: [39, 39],
           38: [40, 40],
           39: [41, 41],
           40: [42, 42],
           41: [43, 43],
           42: [44, 44],
           43: [45, 45],
           44: [46, 46],
           45: [47, 47],
           46: [48, 48],
           47: [49, 49],
           48: [50, 50], #QSFP49
           49: [50, 50],
           50: [50, 50],
           51: [50, 50],
           52: [52, 52], #QSFP50
           53: [52, 52],
           54: [52, 52],
           55: [52, 52],
           56: [54, 54], #QSFP51
           57: [54, 54],
           58: [54, 54],
           59: [54, 54],
           60: [51, 51], #QSFP52
           61: [51, 51],
           62: [51, 51],
           63: [51, 51],
           64: [53, 53], #QSFP53
           65: [53, 53],
           66: [53, 53],
           67: [53, 53],
           68: [55, 55], #QSFP54
           69: [55, 55],
           70: [55, 55],
           71: [55, 55],
           }

    @property
    def port_start(self):
        return self.PORT_START

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
        eeprom_path = self.BASE_VAL_PATH + "sfp_eeprom"

        for x in range(0, self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                self._port_to_i2c_mapping[x][0],
                self._port_to_i2c_mapping[x][1])

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        present_path = self.BASE_VAL_PATH + "sfp_is_present"
        self.__port_to_is_present = present_path.format(self._port_to_i2c_mapping[port_num][0], self._port_to_i2c_mapping[port_num][1])

        try:
            val_file = open(self.__port_to_is_present)
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
        raise NotImplementedError

    def set_low_power_mode(self, port_num, lpmode):
        raise NotImplementedError

    def reset(self, port_num):
        raise NotImplementedError
