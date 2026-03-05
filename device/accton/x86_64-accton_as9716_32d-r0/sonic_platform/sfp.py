#############################################################################
# Edgecore
#
# Sfp contains an implementation of SONiC Platform Base API and
# provides the sfp device status which are available in the platform
#
#############################################################################

import os
import sys
import time
import struct
import logging

from ctypes import create_string_buffer

try:
    from sonic_py_common.logger import Logger
    from sonic_platform_base.sonic_xcvr.sfp_optoe_base import SfpOptoeBase
    from sonic_platform_base.sonic_sfp.sfputilhelper import SfpUtilHelper
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

#Edge-core definitions
CPLD_ADDR_MAPPING = {
    0: {
        "bus": 20,
        "addr": "61"
    },  # port 1-16
    1: {
        "bus": 21,
        "addr": "62"
    },  # port  17-34
}
CPLD_I2C_PATH = "/sys/bus/i2c/devices/{}-00{}/"

NULL_VAL = 'N/A'

I2C_EEPROM_PATH = '/sys/bus/i2c/devices/{0}-0050/eeprom'
OPTOE_DEV_CLASS_PATH = '/sys/bus/i2c/devices/{0}-0050/dev_class'

logger = Logger()
class Sfp(SfpOptoeBase):
    """Platform-specific Sfp class"""

    # Port number
    PORT_START = 1
    PORT_END = 34
    QSFP_PORT_START = 1
    QSFP_PORT_END = 32

    # Path to sysfs
    PLATFORM_ROOT_PATH = "/usr/share/sonic/device"
    PMON_HWSKU_PATH = "/usr/share/sonic/hwsku"
    HOST_CHK_CMD = "which systemctl > /dev/null 2>&1"
    PLATFORM = "x86_64-accton_as9716_32d-r0"
    HWSKU = "Accton-AS9716-32D"

    SFP_TYPE = "SFP"
    QSFP_TYPE = "QSFP"
    OSFP_TYPE = "OSFP"
    QSFP_DD_TYPE = "QSFP_DD"

    SFP_TYPE_CODE_LIST = [
        0x03,  # SFP/SFP+/SFP28
        0x0b   # DWDM-SFP/SFP+
    ]
    QSFP_TYPE_CODE_LIST = [
        0x0c, # QSFP
        0x0d, # QSFP+ or later
        0x11, # QSFP28 or later
        0xe1  # QSFP28 EDFA
    ]
    QSFP_DD_TYPE_CODE_LIST = [
        0x18, # QSFP-DD Double Density 8X Pluggable Transceiver
        0x1E  # QSFP+ or later with CMIS
    ]

    _port_to_i2c_mapping = {
        1: 25,
        2: 26,
        3: 27,
        4: 28,
        5: 29,
        6: 30,
        7: 31,
        8: 32,
        9: 33,
        10: 34,
        11: 35,
        12: 36,
        13: 37,
        14: 38,
        15: 39,
        16: 40,
        17: 41,
        18: 42,
        19: 43,
        20: 44,
        21: 45,
        22: 46,
        23: 47,
        24: 48,
        25: 49,
        26: 50,
        27: 51,
        28: 52,
        29: 53,
        30: 54,
        31: 55,
        32: 56,
        33: 57,
        34: 58,
    }

    def __init__(self, sfp_index=0, sfp_name=None):
        self._api_helper=APIHelper()
        self.index = sfp_index
        self.port_num = self.index + 1
        self._name = sfp_name
        self.prev_present = False

        cpld_idx = 1 if self.port_num > 16 else 0

        self.bus = CPLD_ADDR_MAPPING[cpld_idx]["bus"]
        self.addr = CPLD_ADDR_MAPPING[cpld_idx]["addr"]
        self.i2c_cpld_path = CPLD_I2C_PATH.format(self.bus,self.addr)
        # Since get_eeprom_path() will check if the current device is 
        # a faulty device or not, it needs to be executed after the i2c_cpld_path
        self._eeprom_path = self.get_eeprom_path()

        SfpOptoeBase.__init__(self)

        if self.port_num > self.QSFP_PORT_END:
            self.sfp_type = self.SFP_TYPE
        else:
            self.sfp_type = self.QSFP_TYPE

    def __is_host(self):
        return os.system(self.HOST_CHK_CMD) == 0

    def __get_path_to_port_config_file(self):
        platform_path = "/".join([self.PLATFORM_ROOT_PATH, self.PLATFORM])
        hwsku_path = "/".join([platform_path, self.HWSKU]
                              ) if self.__is_host() else self.PMON_HWSKU_PATH
        return "/".join([hwsku_path, "port_config.ini"])

    def __is_faulty_device(self):
        val = self._api_helper.read_txt_file(
            self.i2c_cpld_path + "faulty_device_" + str(self.port_num))
        if val is not None:
            return int(val, 10)==1
        else:
            return False

    def _convert_string_to_num(self, value_str):
        if "-inf" in value_str:
            return 'N/A'
        elif "Unknown" in value_str:
            return 'N/A'
        elif 'dBm' in value_str:
            t_str = value_str.rstrip('dBm')
            return float(t_str)
        elif 'mA' in value_str:
            t_str = value_str.rstrip('mA')
            return float(t_str)
        elif 'C' in value_str:
            t_str = value_str.rstrip('C')
            return float(t_str)
        elif 'Volts' in value_str:
            t_str = value_str.rstrip('Volts')
            return float(t_str)
        else:
            return 'N/A'

    def get_eeprom_path(self):
        if self.__is_faulty_device():
            return 'N/A'

        port_eeprom_path = I2C_EEPROM_PATH.format(self._port_to_i2c_mapping[self.port_num])
        return port_eeprom_path

    def get_i2c_list(self):
        """
        Retrieves I2C device information for the SFP EEPROM.

        Extracts the bus number and device address from the SFP EEPROM path, determines the region 
        based on the bus range, and returns this information in a list.

        Returns:
            list: A list with I2C device details for the SFP EEPROM.
        """
        i2c_list = []
        eeprom_path = I2C_EEPROM_PATH.format(self._port_to_i2c_mapping[self.port_num])
        path_parts = eeprom_path.rsplit('/', 2)[1].split('-')
        bus = int(path_parts[0])
        device_addr = int(path_parts[1], 16)
        bus_region_map = {
            range(25, 33): '77-2-72',
            range(33, 41): '77-2-73',
            range(41, 49): '77-2-74',
            range(49, 57): '77-2-75',
            range(57, 65): '77-2-76'
        }
        region_prefix = next((prefix for r, prefix in bus_region_map.items() if bus in r), None)

        region = f"{region_prefix}-{((self._port_to_i2c_mapping[self.port_num] - self._port_to_i2c_mapping[1]) % 8) + 1}"
        register_addr = '0x0'
        i2c_list = [{
            'name': self.get_name(),
            'region': region,
            'bus': str(bus),
            'device_addr': hex(device_addr),
            'register_addr': register_addr
        }]

        return i2c_list

    def set_faulty_device(self, faulty):
        faulty_device_path = self.i2c_cpld_path + "faulty_device_" + str(self.port_num)

        val = '1' if faulty else '0'

        return self._api_helper.write_txt_file(faulty_device_path, val)

    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        if not self.get_presence():
            return False

        if 1 <= self.port_num <= 32:
            reset_path = "{}{}{}".format(self.i2c_cpld_path, '/module_reset_', self.port_num)
        else:
            return False

        val = self._api_helper.read_txt_file(reset_path)
        if val is not None:
            return int(val, 10)==1
        else:
            return False

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        if self.sfp_type == self.SFP_TYPE:
            # SFP doesn't support this feature
            return False
        else:
            if not self.get_presence():
                return False

            api = self.get_xcvr_api()
            if self.sfp_type == self.QSFP_DD_TYPE:
                return api.get_lpmode()
            else:
                power_override = api.get_power_override()
                power_set = api.get_power_set()
                if power_override == True and power_set == True:
                    return True  # Low Power Mode if "Power override" bit is 1 and "Power set" bit is 1
                else:
                    # High Power Mode if one of the following conditions is matched:
                    # 1. "Power override" bit is 0
                    # 2. "Power override" bit is 1 and "Power set" bit is 0
                    return False

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        # Check for invalid port_num

        if not self.get_presence():
            return False

        if 1 <= self.port_num <= 32:
            reset_path = "{}{}{}".format(self.i2c_cpld_path, 'module_reset_', self.port_num)
        else:
            return False

        ret = self._api_helper.write_txt_file(reset_path, 1) #sysfs 1: enable reset
        if ret is not True:
            return ret

        time.sleep(0.2)
        ret = self._api_helper.write_txt_file(reset_path, 0) #sysfs 1: disable reset
        time.sleep(0.2)

        return ret

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override
        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        if self.sfp_type == self.SFP_TYPE:
            return False # SFP doesn't support this feature
        else:
            if not self.get_presence():
                return False

            api = self.get_xcvr_api()
            if api is None:
                return False
            if api.get_lpmode_support() == False:
                logger.log_notice("The transceiver of port {} doesn't support to set low power mode.". format(self.port_num))
                return True
            if self.sfp_type == self.QSFP_DD_TYPE:
                # ToDO: The return code for CMIS set_lpmode have some issue
                # workaround: always return True
                api.set_lpmode(lpmode)
                ret = True
            else:
                ret = api.set_power_override(True, lpmode)
            return ret

    ##############################################################
    ###################### Device methods ########################
    ##############################################################

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        sfputil_helper = SfpUtilHelper()
        sfputil_helper.read_porttab_mappings(
            self.__get_path_to_port_config_file())
        name = sfputil_helper.logical[self.index] or "Unknown"
        return name

    def get_presence(self):
        """
        Retrieves the presence of the device
        Returns:
            bool: True if device is present, False if not
        """
        val = self._api_helper.read_txt_file(
            self.i2c_cpld_path + "module_present_" + str(self.port_num))

        if val is not None:
            status = int(val, 10) == 1
            self.prev_present = status
        else:
            return self.prev_present

        return status

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence() and not self.get_reset_status()

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of
        entPhysicalContainedIn is'0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device
            or -1 if cannot determine the position
        """
        return self.port_num

    def is_replaceable(self):
        """
        Retrieves if replaceable
        Returns:
            A boolean value, True if replaceable
        """
        return True

    def __validate_eeprom_sfp(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(0, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 63):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[63]:
                return False

        checksum_test = 0
        for i in range(64, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        return True
    def __validate_eeprom_sfp(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(0, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 63):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[63]:
                return False

        checksum_test = 0
        for i in range(64, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        return True

    def __validate_eeprom_qsfp(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(128, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 63):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[63]:
                return False

        checksum_test = 0
        for i in range(64, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        return True

    def __validate_eeprom_cmis(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(128, 95)
        if eeprom_raw is None:
            return None

        for i in range(0, 94):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[94]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(258, 126)
        if eeprom_raw is None:
            return None

        for i in range(0, 125):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[125]:
                return False

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 128)
        if eeprom_raw is None:
            return None

        for i in range(0, 127):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[127]:
                return False
    def __validate_eeprom_cmis(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(128, 95)
        if eeprom_raw is None:
            return None

        for i in range(0, 94):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[94]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(258, 126)
        if eeprom_raw is None:
            return None

        for i in range(0, 125):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[125]:
                return False

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 128)
        if eeprom_raw is None:
            return None

        for i in range(0, 127):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[127]:
                return False

        # CMIS_5.0 starts to support the checksum of page 04h
        cmis_rev = float(api.get_cmis_rev())
        if cmis_rev >= 5.0:
            checksum_test = 0
            eeprom_raw = self.read_eeprom(640, 128)
            if eeprom_raw is None:
                return None

            for i in range(0, 127):
                checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
            else:
                if checksum_test != eeprom_raw[127]:
                    return False

        return True

    def validate_eeprom(self):
        id_byte_raw = self.read_eeprom(0, 1)
        if id_byte_raw is None:
            return None

        id = id_byte_raw[0]
        if id in self.QSFP_TYPE_CODE_LIST:
            return self.__validate_eeprom_qsfp()
        elif id in self.SFP_TYPE_CODE_LIST:
            return self.__validate_eeprom_sfp()
        elif id in self.QSFP_DD_TYPE_CODE_LIST:
            return self.__validate_eeprom_cmis()
        else:
            return False

    def validate_temperature(self):
        temperature = self.get_temperature()
        if temperature is None:
            return None

        threshold_dict = self.get_transceiver_threshold_info()
        if threshold_dict is None:
            return None

        if isinstance(temperature, float) is not True:
            return True

        if isinstance(threshold_dict['temphighalarm'], float) is not True:
            return True

        return threshold_dict['temphighalarm'] > temperature

    def __get_error_description(self):
        if not self.get_presence():
            return self.SFP_STATUS_UNPLUGGED

        err_stat = self.SFP_STATUS_BIT_INSERTED

        status = self.validate_eeprom()
        if status is not True:
            err_stat = (err_stat | self.SFP_ERROR_BIT_BAD_EEPROM)

        status = self.validate_temperature()
        if status is not True:
            err_stat = (err_stat | self.SFP_ERROR_BIT_HIGH_TEMP)

        if err_stat is self.SFP_STATUS_BIT_INSERTED:
            return self.SFP_STATUS_OK
        else:
            err_desc = ''
            cnt = 0
            for key in self.SFP_ERROR_BIT_TO_DESCRIPTION_DICT:
                if (err_stat & key) != 0:
                    if cnt > 0:
                        err_desc = err_desc + "|"
                        cnt = cnt + 1
                    err_desc = err_desc + self.SFP_ERROR_BIT_TO_DESCRIPTION_DICT[key]

            return err_desc

    def get_error_description(self):
        """
        Retrives the error descriptions of the SFP module

        Returns:
            String that represents the current error descriptions of vendor specific errors
            In case there are multiple errors, they should be joined by '|',
            like: "Bad EEPROM|Unsupported cable"
        """
        try:
            ret = super().get_error_description()
            if ret is not None:
                return ret
        except NotImplementedError:
            pass
        return self.__get_error_description()

