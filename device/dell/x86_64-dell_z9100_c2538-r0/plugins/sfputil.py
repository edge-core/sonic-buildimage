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
    IOM_1_PORT_START = 0
    IOM_1_PORT_END = 11
    IOM_2_PORT_START = 12
    IOM_2_PORT_END = 21
    IOM_3_PORT_START = 22
    IOM_3_PORT_END = 31

    BASE_VAL_PATH = "/sys/class/i2c-adapter/i2c-{0}/{0}-003e/"

    _port_to_eeprom_mapping = {}
    _port_to_i2c_mapping = {
           0: [9, 18],
           1: [9, 19],
           2: [9, 20],
           3: [9, 21],
           4: [9, 22],
           5: [9, 23],
           6: [9, 24],
           7: [9, 25],
           8: [8, 26],
           9: [8, 27],
           10: [8, 28],
           11: [8, 29],
           12: [8, 31],  # reordered
           13: [8, 30],
           14: [8, 33],  # reordered
           15: [8, 32],
           16: [7, 34],
           17: [7, 35],
           18: [7, 36],
           19: [7, 37],
           20: [7, 38],
           21: [7, 39],
           22: [7, 40],
           23: [7, 41],
           24: [6, 42],
           25: [6, 43],
           26: [6, 44],
           27: [6, 45],
           28: [6, 46],
           29: [6, 47],
           30: [6, 48],
           31: [6, 49]
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
    def iom1_port_start(self):
        return self.IOM_1_PORT_START

    @property
    def iom1_port_end(self):
        return self.IOM_1_PORT_END

    @property
    def iom2_port_start(self):
        return self.IOM_2_PORT_START

    @property
    def iom2_port_end(self):
        return self.IOM_2_PORT_END

    @property
    def iom3_port_start(self):
        return self.IOM_3_PORT_START

    @property
    def iom3_port_end(self):
        return self.IOM_3_PORT_END

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    @property
    def port_to_i2c_mapping(self):
        return self._port_to_i2c_mapping

    def __init__(self):
        eeprom_path = "/sys/class/i2c-adapter/i2c-{0}/i2c-{1}/{1}-0050/eeprom"

        for x in range(0, self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                self.port_to_i2c_mapping[x][0],
                self.port_to_i2c_mapping[x][1])

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):

        global i2c_line

        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False
        # port_num and i2c match
        if port_num >= self.iom1_port_start and port_num <= self.iom1_port_end:
            i2c_line = 14
        elif (port_num >= self.iom2_port_start and
                port_num <= self.iom2_port_end):
            i2c_line = 15
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            i2c_line = 16

        try:
            qsfp_path = self.BASE_VAL_PATH.format(i2c_line)+"qsfp_modprs"
            reg_file = open(qsfp_path, "r")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # Absence of IOM throws read error
        if (content == 'read error'):
            return False

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Rationalize port settings
        if port_num >= self.iom2_port_start and port_num <= self.iom2_port_end:
            port_num = port_num % 12
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            port_num = port_num % 22

        # Mask off the bit corresponding to our port
        mask = (1 << port_num)

        # ModPrsL is active low
        if reg_value & mask == 0:
            return True

        return False

    def get_low_power_mode(self, port_num):

        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        # port_num and i2c match
        if port_num >= self.iom1_port_start and port_num <= self.iom1_port_end:
            i2c_line = 14
        elif (port_num >= self.iom2_port_start and
                port_num <= self.iom2_port_end):
            i2c_line = 15
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            i2c_line = 16

        try:
                qsfp_path = self.BASE_VAL_PATH.format(i2c_line)+"qsfp_lpmode"
                reg_file = open(qsfp_path, "r")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # Absence of IOM throws read error
        if (content == 'read error'):
            return False

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Rationalize port settings
        if port_num >= self.iom2_port_start and port_num <= self.iom2_port_end:
            port_num = port_num % 12
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            port_num = port_num % 22

        # Mask off the bit corresponding to our port
        mask = (1 << port_num)

        # LPMode is active high
        if reg_value & mask == 0:
            return False

        return True

    def set_low_power_mode(self, port_num, lpmode):

        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        # port_num and i2c match
        if port_num >= self.iom1_port_start and port_num <= self.iom1_port_end:
            i2c_line = 14
        elif (port_num >= self.iom2_port_start and
                port_num <= self.iom2_port_end):
            i2c_line = 15
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            i2c_line = 16

        try:
                qsfp_path = self.BASE_VAL_PATH.format(i2c_line)+"qsfp_lpmode"
                reg_file = open(qsfp_path, "r+")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # Absence of IOM throws read error
        if (content == 'read error'):
            return False

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Rationalize port settings
        if port_num >= self.iom2_port_start and port_num <= self.iom2_port_end:
            port_num = port_num % 12
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            port_num = port_num % 22

        # Mask off the bit corresponding to our port
        mask = (1 << port_num)
        # LPMode is active high; set or clear the bit accordingly
        if lpmode is True:
            reg_value = reg_value | mask
        else:
            reg_value = reg_value & ~mask

        # Convert our register value back to a hex string and write back
        content = hex(reg_value)

        reg_file.seek(0)
        reg_file.write(content)
        reg_file.close()

        return True

    def reset(self, port_num):

        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        # port_num and i2c match
        if port_num >= self.iom1_port_start and port_num <= self.iom1_port_end:
            i2c_line = 14
        elif (port_num >= self.iom2_port_start and
                port_num <= self.iom2_port_end):
            i2c_line = 15
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            i2c_line = 16

        try:
                qsfp_path = self.BASE_VAL_PATH.format(i2c_line)+"qsfp_lpmode"
                reg_file = open(qsfp_path, "r+")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # File content is a string containing the hex representation of th
        reg_value = int(content, 16)

        # Rationalize port settings
        if port_num >= self.iom2_port_start and port_num <= self.iom2_port_end:
            port_num = port_num % 12
        elif (port_num >= self.iom3_port_start and
                port_num <= self.iom3_port_end):
            port_num = port_num % 22

        # Mask off the bit corresponding to our port
        mask = (1 << port_num)

        # ResetL is active low
        reg_value = reg_value & ~mask

        # Convert our register value back to a hex string and write back
        reg_file.seek(0)
        reg_file.write(hex(reg_value))
        reg_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        # Flip the bit back high and write back to the register to take
        # port out of reset
        try:
                qsfp_path = self.BASE_VAL_PATH.format(i2c_line)+"qsfp_lpmode"
                reg_file = open(qsfp_path, "w+")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = reg_value | mask
        reg_file.seek(0)
        reg_file.write(hex(reg_value))
        reg_file.close()

        return True
