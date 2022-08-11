#!/usr/bin/env python
#
# Platform-specific SFP transceiver interface for SONiC
# This plugin supports QSFP-DD, QSFP and SFP.

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 0
    PORT_END = 33
    OSFP_PORT_START = 0
    OSFP_PORT_END = 31
    SFP_PORT_START = 32
    SFP_PORT_END = 33

    EEPROM_OFFSET = 12
    QSFP_PORT_INFO_PATH = '/sys/class/SFF'
    SFP_PORT_INFO_PATH = '/sys/devices/platform/fpga-xcvr'
    PORT_INFO_PATH = QSFP_PORT_INFO_PATH
	
    OSFP_INFO_PAGE = 0
    PAGE_SELETCT_OFFSET = 127

    _port_name = ""
    _port_to_eeprom_mapping = {}
    _port_to_i2cbus_mapping = {}

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return []

    @property
    def osfp_ports(self):
        return range(self.OSFP_PORT_START, self.OSFP_PORT_END + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    @property
    def port_to_i2cbus_mapping(self):
        return self._port_to_i2cbus_mapping

    @property
    def get_transceiver_status(self):
        content = 0
        port = 0
        try:
            while self.port_start <= port <= self.port_end:
                if self.get_presence(port):
                    content = content | (1 << port)
                port = port + 1

        except IOError as error:
            print("Error: unable to open file: %s" % str(error))
            return False

        return content 

    def get_port_name(self, port_num):
        if port_num in self.osfp_ports:
            self._port_name = "QSFP" + str(port_num - self.OSFP_PORT_START + 1)
        else:
            self._port_name = "SFP" + str(port_num - self.SFP_PORT_START + 1)
        return self._port_name

    def get_eeprom_dom_raw(self, port_num):
        if port_num in self.osfp_ports:
            # QSFP DOM EEPROM is also at addr 0x50 and thus also stored in eeprom_ifraw
            return None
        else:
            # Read dom eeprom at addr 0x51
            return self._read_eeprom_devid(port_num, self.DOM_EEPROM_ADDR, 256)

    def __write_eeprom_specific_bytes(self, port_num, offset, write_bytes):
        """
        Writes bytes to sfp eeprom
        Args:
            offset: integer, 0-0xff
            bytes : list, [0x12, 0x13, ...], bytes to write
        Returns:
            A boolean, True if bytes are written successfully, False if not
        """

        sysfs_sfp_i2c_client_eeprom_path = self.port_to_eeprom_mapping[port_num]
        try:
            with open(sysfs_sfp_i2c_client_eeprom_path, mode="r+b", buffering=0) as sysfsfile_eeprom:
                sysfsfile_eeprom.seek(offset)
                for i in range(len(write_bytes)):
                    sysfsfile_eeprom.write(chr(write_bytes[i]))
        except Exception as error:
            # print(str(error))
            return False

    def __init__(self):
        # Override port_to_eeprom_mapping for class initialization
        eeprom_path = '/sys/bus/i2c/devices/i2c-{0}/{0}-0050/eeprom'

        for x in range(self.PORT_START, self.PORT_END + 1):
            self.port_to_i2cbus_mapping[x] = (x + self.EEPROM_OFFSET)
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                x + self.EEPROM_OFFSET)
        # Get Transceiver status
        self.modprs_register = self.get_transceiver_status

        # All SFPs' eeprom switch to page 0
        for x in range(self.PORT_START, self.PORT_END + 1):
            if self.get_presence(x):
                self.__write_eeprom_specific_bytes(x, self.PAGE_SELETCT_OFFSET, [self.OSFP_INFO_PAGE])

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num not in range(self.port_start, self.port_end + 1):
            return False

        # Get path for access port presence status
        port_name = self.get_port_name(port_num)
        sysfs_filename = "qsfp_modprs" if port_num in self.osfp_ports else "sfp_modabs"
        self.PORT_INFO_PATH = self.QSFP_PORT_INFO_PATH if port_num in self.osfp_ports else self.SFP_PORT_INFO_PATH
        reg_path = "/".join([self.PORT_INFO_PATH, port_name, sysfs_filename])

        # Read status
        try:
            reg_file = open(reg_path)
            content = reg_file.readline().rstrip()
            reg_value = int(content)
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # Module present is active low
        if reg_value == 0:
            return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid QSFP port_num
        self.PORT_INFO_PATH = self.QSFP_PORT_INFO_PATH if port_num in self.osfp_ports else self.SFP_PORT_INFO_PATH
        if port_num not in self.osfp_ports:
            return False

        try:
            port_name = self.get_port_name(port_num)
            reg_file = open("/".join([self.PORT_INFO_PATH,
                                      port_name, "qsfp_lpmode"]))
        except IOError as error:
            print ("Error: unable to open file: %s" % str(error))
            return False

        # Read status
        content = reg_file.readline().rstrip()
        reg_value = int(content)
        # low power mode is active high
        if reg_value == 0:
            return False

        return True

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid QSFP port_num
        self.PORT_INFO_PATH = self.QSFP_PORT_INFO_PATH if port_num in self.osfp_ports else self.SFP_PORT_INFO_PATH
        if port_num not in self.osfp_ports:
            return False

        try:
            port_name = self.get_port_name(port_num)
            reg_file = open("/".join([self.PORT_INFO_PATH,
                                      port_name, "qsfp_lpmode"]), "r+")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        content = hex(lpmode)

        reg_file.seek(0)
        reg_file.write(content)
        reg_file.close()

        return True

    def reset(self, port_num):
        # Check for invalid QSFP port_num
        self.PORT_INFO_PATH = self.QSFP_PORT_INFO_PATH if port_num in self.osfp_ports else self.SFP_PORT_INFO_PATH
        if port_num not in self.osfp_ports:
            return False

        try:
            port_name = self.get_port_name(port_num)
            reg_file = open("/".join([self.PORT_INFO_PATH,
                                      port_name, "qsfp_reset"]), "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # Convert our register value back to a hex string and write back
        reg_file.seek(0)
        reg_file.write(hex(0))
        reg_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        # Flip the bit back high and write back to the register to take port out of reset
        try:
            reg_file = open(
                "/".join([self.PORT_INFO_PATH, port_name, "qsfp_reset"]), "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        reg_file.seek(0)
        reg_file.write(hex(1))
        reg_file.close()

        return True

    def get_transceiver_change_event(self, timeout=0):

        start_time = time.time()
        port_dict = {}
        port = self.port_start
        forever = False

        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000) # Convert to secs
        else:
            print ("get_transceiver_change_event:Invalid timeout value")
            return False, {}

        end_time = start_time + timeout
        if start_time > end_time:
            print ('get_transceiver_change_event:' \
                       'time wrap / invalid timeout value')

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
        print ("get_transceiver_change_event: Should not reach here.")
        return False, {}
