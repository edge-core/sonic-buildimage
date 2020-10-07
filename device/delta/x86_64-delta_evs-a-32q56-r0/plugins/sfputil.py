# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import os.path
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 0
    PORT_START_SFP = 32
    PORT_END = 33
    PORTS_IN_BLOCK = 34

    _port_to_eeprom_mapping = {}
    port_dict = {}

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def port_start_sfp(self):
        return self.PORT_START_SFP

    @property
    def qsfp_ports(self):
        return range(0, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    @property
    def get_transceiver_status(self):

        try:
            reg_file = open("/sys/kernel/sfp/sfp_is_present")

        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()
        reg_file.close()

        return int(content, 16)

    def __init__(self):
        eeprom_path = "/sys/bus/i2c/devices/{0}-0050/eeprom"

        for x in range(0, self.port_end + 1):
            if x >= self.port_start_sfp:
                # SFP1: 41-0050, SFP2: 42-0050
                self.port_to_eeprom_mapping[x] = eeprom_path.format(x + 9)
            else:
                # QSFP1: 51-0050  ~  QSFP32: 82-0050
                self.port_to_eeprom_mapping[x] = eeprom_path.format(x + 51)

        self.modprs_register = self.get_transceiver_status
        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        if port_num < 16 or port_num >= self.port_start_sfp:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x01")
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x10")

        if port_num >= self.port_start_sfp:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x01").readline().strip()
        else:
            if ((port_num / 8) % 2 == 0):
                content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x08").readline().strip()
            else:
                content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x09").readline().strip()

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Mask off the bit corresponding to our port
        mask = (1 << (port_num % 8))

        # ModPrsL is active low
        if reg_value & mask == 0:
            return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end - 2:
            return False

        if port_num < 16:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x01")
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x10")

        if ((port_num / 8) % 2 == 0):
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x12").readline().strip()
        else:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x13").readline().strip()

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Mask off the bit corresponding to our port
        mask = (1 << (port_num % 8))

        # LPMode is active high
        if reg_value & mask == 0:
            return False

        return True

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end - 2:
            return False

        if port_num < 16:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x01")
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x10")

        if ((port_num / 8) % 2 == 0):
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x12").readline().strip()
        else:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x13").readline().strip()

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Mask off the bit corresponding to our port
        mask = (1 << (port_num % 8))

        # LPMode is active high; set or clear the bit accordingly
        if lpmode is True:
            reg_value = reg_value | mask
        else:
            reg_value = reg_value & ~mask

        # Convert our register value back to a hex string and write back
        content = hex(reg_value).rstrip("L") or "0"
        if ((port_num / 8) % 2 == 0):
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x12 {0}".format(content))
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x13 {0}".format(content))

        return True

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end - 2:
            return False

        if port_num < 16:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x01")
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0xe2 0x01 0x10")

        if ((port_num / 8) % 2 == 0):
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x06").readline().strip()
        else:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x01 0x07").readline().strip()

        # File content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Mask off the bit corresponding to our port
        mask = (1 << (port_num % 8))

        # ResetL is active low
        reg_value = reg_value & ~mask

        # Convert our register value back to a hex string and write back
        if ((port_num / 8) % 2 == 0):
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x06 {0}".format(hex(reg_value)))
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x07 {0}".format(hex(reg_value)))

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        # Flip the bit back high and write back to the register to take port out of reset
        reg_value = reg_value | mask
        if ((port_num / 8) % 2 == 0):
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x06 {0}".format(hex(reg_value)))
        else:
            os.popen("ipmitool raw 0x06 0x52 0x07 0x64 0x00 0x07 {0}".format(hex(reg_value)))

        return True

    def get_transceiver_change_event(self, timeout=2000):
        start_time = time.time()
        port_dict = {}
        port = self.port_start
        forever = False
        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000) # Convert to secs
        else:
            print "get_transceiver_change_event:Invalid timeout value", timeout
            return False, {}

        end_time = start_time + timeout
        if start_time > end_time:
            print 'get_transceiver_change_event:' \
                       'time wrap / invalid timeout value', timeout

            return False, {} # Time wrap or possibly incorrect timeout
        while timeout >= 0:
            # Check for OIR events and return updated port_dict
            reg_value = self.get_transceiver_status
            if reg_value != self.modprs_register:
                changed_ports = self.modprs_register ^ reg_value
                while port >= self.port_start and port <= self.port_end:

                    # Mask off the bit corresponding to our port
                    mask = (1 << port)
                    if changed_ports & mask:
                        # ModPrsL is active low
                        if reg_value & mask == 0:
                            port_dict[port] = '1'
                        else:
                            port_dict[port] = '0'

                    port += 1

                # Update reg value
                self.modprs_register = reg_value
                return True, port_dict
            if forever:
                time.sleep(1)
            else:
                timeout = end_time - time.time()
                if timeout >= 1:
                    time.sleep(1) # We poll at 1 second granularity
                else:
                    if timeout > 0:
                        time.sleep(timeout)
                    return True, {}
        print "get_transceiver_change_event: Should not reach here."
        return False, {}
