# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    import string
    from ctypes import create_string_buffer
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 0
    PORT_END = 71
    PORTS_IN_BLOCK = 72
    QSFP_PORT_START = 48
    QSFP_PORT_END = 72

    BASE_VAL_PATH = "/sys/class/i2c-adapter/i2c-{0}/{1}-0050/"

    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _cpld_mapping = {
       0:  "4-0060",
       1:  "5-0062",
       2:  "6-0064",
           }
    _port_to_i2c_mapping = {
           0:  18, 
           1:  19, 
           2:  20, 
           3:  21, 
           4:  22, 
           5:  23, 
           6:  24, 
           7:  25, 
           8:  26,
           9:  27,
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
           48: 66, #QSFP49
           49: 66,
           50: 66,
           51: 66,
           52: 67, #QSFP50
           53: 67,
           54: 67,
           55: 67,
           56: 68, #QSFP51
           57: 68,
           58: 68,
           59: 68,
           60: 69, #QSFP52
           61: 69,
           62: 69,
           63: 69,
           64: 70, #QSFP53
           65: 70,
           66: 70,
           67: 70,
           68: 71, #QSFP54
           69: 71,
           70: 71,
           71: 71,
           }

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_port_start(self):
        return self.QSFP_PORT_START

    @property
    def qsfp_port_end(self):
        return self.QSFP_PORT_END
    
    @property
    def qsfp_ports(self):
        return range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def __init__(self):
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/eeprom'
        for x in range(0, self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                self._port_to_i2c_mapping[x])

        SfpUtilBase.__init__(self)


    # For port 48~51 are QSFP, here presumed they're all split to 4 lanes.
    def get_cage_num(self, port_num):             
        cage_num = port_num
        if (port_num >= self.QSFP_PORT_START):
            cage_num = (port_num - self.QSFP_PORT_START)/4
            cage_num = cage_num + self.QSFP_PORT_START

        return cage_num

    # For cage 0~23 and 48~51 are at cpld2, others are at cpld3.
    def get_cpld_num(self, port_num):             
        cpld_i = 1
        cage_num = self.get_cage_num(port_num)
        if (port_num > 23 and port_num < self.QSFP_PORT_START):
            cpld_i = 2

        if (cage_num >= 52): 
            cpld_i = 2

        return cpld_i

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False
        
        cage_num = self.get_cage_num(port_num)
        cpld_i = self.get_cpld_num(port_num)

        cpld_ps = self._cpld_mapping[cpld_i]
        path = "/sys/bus/i2c/devices/{0}/module_present_{1}"
        port_ps = path.format(cpld_ps, cage_num+1)

        try:
            val_file = open(port_ps)
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
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False

        try:
            eeprom = None

            if not self.get_presence(port_num):
                return False

            eeprom = open(self.port_to_eeprom_mapping[port_num], "rb")
            eeprom.seek(93)
            lpmode = ord(eeprom.read(1))

            if ((lpmode & 0x3) == 0x3):
                return True # Low Power Mode if "Power override" bit is 1 and "Power set" bit is 1
            else:
                return False # High Power Mode if one of the following conditions is matched:
                             # 1. "Power override" bit is 0
                             # 2. "Power override" bit is 1 and "Power set" bit is 0 
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    def set_low_power_mode(self, port_num, lpmode): 
        # Check for invalid port_num
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False

        try:
            eeprom = None

            if not self.get_presence(port_num):
                return False # Port is not present, unable to set the eeprom

            # Fill in write buffer
            regval = 0x3 if lpmode else 0x1 # 0x3:Low Power Mode, 0x1:High Power Mode
            buffer = create_string_buffer(1)
            buffer[0] = chr(regval)

            # Write to eeprom
            eeprom = open(self.port_to_eeprom_mapping[port_num], "r+b")
            eeprom.seek(93)
            eeprom.write(buffer[0])
            return True
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    def reset(self, port_num):
        if port_num < self.qsfp_port_start or port_num > self.qsfp_port_end:
            return False
         
        cage_num = self.get_cage_num(port_num)
        cpld_i = self.get_cpld_num(port_num)
        cpld_ps = self._cpld_mapping[cpld_i]
        path = "/sys/bus/i2c/devices/{0}/module_reset_{1}"
        port_ps = path.format(cpld_ps, cage_num+1)
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)          
            return False

        reg_value = '0'

        reg_file.write(reg_value)
        reg_file.close()
        
        return True

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError
