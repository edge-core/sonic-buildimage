#############################################################################
# Accton
#
# Sfp contains an implementation of SONiC Platform Base API and
# provides the sfp device status which are available in the platform
#
#############################################################################

import os
import sys
import time
import struct
import subprocess
from ctypes import create_string_buffer

try:
    from sonic_py_common import logger
    from sonic_platform_base.sonic_xcvr.sfp_optoe_base import SfpOptoeBase
    from sonic_platform_base.sonic_sfp.sfputilhelper import SfpUtilHelper
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

SYSLOG_IDENTIFIER = "sfp"
logger = logger.Logger(SYSLOG_IDENTIFIER)
logger.set_min_log_priority_debug()
logger.log_debug("Load {} module".format(__name__))

QSFP_POWEROVERRIDE_OFFSET = 93
SFP_STATUS_INSERTED = '1'
SFP_STATUS_REMOVED = '0'

SYSFS_RESET_DISABLE = 0
SYSFS_RESET_ENABLE = 1

SYSFS_LPM_MODE_DISABLE = 0
SYSFS_LPM_MODE_ENABLE = 1

class Sfp(SfpOptoeBase):
    """Platform-specific Sfp class"""

    EEPROM_PATH = '/sys/bus/i2c/devices/{0}-0050/eeprom'
    CPLD_I2C_PATH = "/sys/bus/i2c/devices/"
    PLATFORM_ROOT_PATH = "/usr/share/sonic/device"
    PMON_JSON_PATH = "/usr/share/sonic/platform"
    PMON_HWSKU_PATH = '/usr/share/sonic/hwsku'
    SFP_ERROR_DESCRIPTION_HIGH_VCC = "High VCC detected"
    SFP_ERROR_DESCRIPTION_LOW_VCC = "Low VCC detected"

    # Port number
    PORT_START = 1
    PORT_END = 32

    _cpld_mapping = {
        0:  "13-0061",
        1:  "15-0062",
    }

    _port_to_i2c_mapping = list(range(18, 50))
    _sfp_port = range(PORT_START, PORT_END + 1)


    def __init__(self, sfp_index=0):

        SfpOptoeBase.__init__(self)
        self._index = sfp_index
        self._port_num = self._index + 1
        self._api_helper = APIHelper()
        self.data = {'present': False}

        self.eeprom_path = self.EEPROM_PATH.format(Sfp._port_to_i2c_mapping[self._index])

        if self._index <= 15:
            cpld_index = 0
        else:
            cpld_index = 1

        self.reset_path = f"{Sfp.CPLD_I2C_PATH}{Sfp._cpld_mapping[cpld_index]}/module_reset_{self._port_num}"
        self.present_path = f"{Sfp.CPLD_I2C_PATH}{Sfp._cpld_mapping[cpld_index]}/module_present_{self._port_num}"
        self.lpmode_path = f"{Sfp.CPLD_I2C_PATH}{Sfp._cpld_mapping[cpld_index]}/module_lpmode_{self._port_num}"

    def __is_host():
        try:
            result = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except FileNotFoundError:
            # 'docker' command is not found, assume not host (or minimal container)
            return False

    def __get_path_to_port_config_file(self):
        platform_path = "/".join([self.PLATFORM_ROOT_PATH, self._api_helper.platform])
        platform_json_path = platform_path if self.__is_host() else self.PMON_JSON_PATH
        config_file_path = "/".join([platform_json_path, "platform.json"])
        return config_file_path


    def get_eeprom_path(self):
        return self.eeprom_path


    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        sfputil_helper = SfpUtilHelper()
        sfputil_helper.read_porttab_mappings(self.__get_path_to_port_config_file())
        name = sfputil_helper.logical[self._index] or "Unknown"
        return name


    def get_presence(self):
        """
        Retrieves the presence of the device
        Returns:
            bool: True if device is present, False if not
        """
        val = self._api_helper.read_txt_file(self.present_path)

        if val is not None:
            return int(val, 10)==1
        else:
            return False


    def get_transceiver_change_event(self, timeout=2000):
        """
        Checks if transceiver has been inserted/removed
        Returns:
            SFP_STATUS_INSERTED, SFP_STATUS_REMOVED or None
        """
        present = self.get_presence()
        if present != self.data['present']:
            if present == True:
                sfp_event = SFP_STATUS_INSERTED
                logger.log_debug("get_transceiver_change_event: port {}: SFP_STATUS_INSERTED".format(self._port_num))
            else:
                sfp_event = SFP_STATUS_REMOVED
                logger.log_debug("get_transceiver_change_event: port {}: SFP_STATUS_REMOVED".format(self._port_num))
        else:
            sfp_event = None

        self.data['present'] = present
        return sfp_event


    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        val=self._api_helper.read_txt_file(self.reset_path)
        if val is None:
            return 0

        return int(val, 10)==1


    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        if self._port_num > self.PORT_END:
            # SFP doesn't support this feature
            return False
        else:
            val = self._api_helper.read_txt_file(self.lpmode_path)
            if val is not None:
                return int(val, 10) == 1
            else:
                return False


    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        # Check for invalid port_num

        if self._port_num > self.PORT_END:
            return False # SFP doesn't support this feature
        elif not self.get_presence():
            return False

        ret = self._api_helper.write_txt_file(self.reset_path, SYSFS_RESET_ENABLE)
        if ret is not True:
            return ret

        time.sleep(0.2)
        ret = self._api_helper.write_txt_file(self.reset_path, SYSFS_RESET_DISABLE)
        time.sleep(0.2)

        return ret


    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        if self._port_num > self.PORT_END:
            return False # SFP doesn't support this feature
        else:
            if not self.get_presence():
                return False

            val = SYSFS_LPM_MODE_ENABLE
            if lpmode == False:
                val = SYSFS_LPM_MODE_DISABLE
            return self._api_helper.write_txt_file(self.lpmode_path, val)


    def get_transceiver_info(self):
        transceiver_info_dict = SfpOptoeBase.get_transceiver_info(self)
        if transceiver_info_dict is not None:
            transceiver_info_dict['hardware_rev'] = 'N/A'

        return transceiver_info_dict


    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence() and not self.get_reset_status()

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return True

    def get_error_description(self):
        """
        Get error description

        Args:
            None

        Returns:
            The error description
        """
        if not self.get_presence():
            return self.SFP_STATUS_UNPLUGGED

        api = SfpOptoeBase.get_xcvr_api(self)
        flags = api.get_module_level_flag()
        case_temp = flags.get("case_temp_flags")
        case_voltage = flags.get("voltage_flags")
        if case_temp.get("case_temp_high_alarm_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_HIGH_TEMP
        elif case_temp.get("case_temp_high_warn_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_HIGH_TEMP
        elif case_voltage.get("voltage_high_alarm_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_HIGH_VCC
        elif case_voltage.get("voltage_high_warn_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_HIGH_VCC
        elif case_voltage.get("voltage_low_alarm_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_LOW_VCC
        elif case_voltage.get("voltage_low_warn_flag"):
            error_description = self.SFP_ERROR_DESCRIPTION_LOW_VCC
        else:
            error_description = self.SFP_STATUS_OK

        return error_description
