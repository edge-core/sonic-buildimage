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
    PORT_END = 81
    PORTS_IN_BLOCK = 82
    QSFP_PORT_START = 48
    QSFP_PORT_END = 82

    BASE_VAL_PATH = "/sys/class/i2c-adapter/i2c-{0}/{1}-0050/"

    _port_to_is_present = {}
    _port_to_lp_mode = {}

    _port_to_eeprom_mapping = {}
    _cpld_mapping = {
       1:  "12-0062",
       2:  "18-0060",
       3:  "19-0064",
           }

    _port_to_i2c_mapping = {
           0:  42,
           1:  41,
           2:  44,
           3:  43,
           4:  47,
           5:  45,
           6:  46,
           7:  50,
           8:  48,
           9:  49,
           10:  51,
           11:  52,
           12:  53,
           13:  56,
           14:  55,
           15:  54,
           16:  58,
           17:  57,
           18:  59,
           19:  60,
           20:  61,
           21:  63,
           22:  62,
           23:  64,
           24:  66,
           25:  68,
           26:  65,
           27:  67,
           28:  69,
           29:  71,
           30:  72,
           31:  70,
           32:  74,
           33:  73,
           34:  76,
           35:  75,
           36:  77,
           37:  79,
           38:  78,
           39:  80,
           40:  81,
           41:  82,
           42:  84,
           43:  85,
           44:  83,
           45:  87,
           46:  88,
           47:  86,
           48:  25,  #QSFP49
           49:  25,  
           50:  25,  
           51:  25,  
           52:  26,  #QSFP50
           53:  26,
           54:  26,
           55:  26,
           56:  27,  #QSFP51
           57:  26,
           58:  26,
           59:  26,
           60:  28,  #QSFP52
           61:  26,
           62:  26,
           63:  26,
           64:  29,  #QSFP53
           65:  26,
           66:  26,
           67:  26,
           68:  30,  #QSFP54
           69:  26,
           70:  26,
           71:  26,
           72:  31,  #QSFP55
           73:  26,
           74:  26,
           75:  26,
           76:  32,  #QSFP56
           77:  26,
           78:  26,
           79:  26,
           80:  22,
           81:  23}

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
        if (port_num > 29):
            cpld_i = 2
        return cpld_i

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        cage_num = self.get_cage_num(port_num)
        cpld_i = self.get_cpld_num(port_num)
        #print "[ROY] cpld:%d" % cpld_i

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
        raise NotImplementedError

    def set_low_power_mode(self, port_num, lpmode):                
        raise NotImplementedError

    def reset(self, port_num):
        raise NotImplementedError
