#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

import sys
import re
import os
import subprocess
import json

try:
    from sonic_platform_base.sonic_sfp.sfputilhelper import SfpUtilHelper
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_py_common import device_info
    from .event import SfpEvent
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_FAN_TRAY = 3
NUM_FAN = 1
NUM_PSU = 2
NUM_THERMAL = 7
NUM_SFP = 52
NUM_COMPONENT = 3
RESET_REGISTER = "0x112"
HOST_REBOOT_CAUSE_PATH = "/host/reboot-cause/previous-reboot-cause.txt"
PMON_REBOOT_CAUSE_PATH = "/usr/share/sonic/platform/api_files/reboot-cause/previous-reboot-cause.txt"
HOST_CHK_CMD = "docker > /dev/null 2>&1"


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        ChassisBase.__init__(self)
        self._api_helper = APIHelper()
        self.sfp_module_initialized = False
        self.__initialize_eeprom()
        self.is_host = self._api_helper.is_host()


        if not self.is_host:
            self.__initialize_fan()
            self.__initialize_psu()
            self.__initialize_thermals()
        else:
            self.__initialize_components()

        self._reboot_cause_path = HOST_REBOOT_CAUSE_PATH if self.__is_host(
        ) else PMON_REBOOT_CAUSE_PATH

    def __initialize_sfp(self):
        sfputil_helper = SfpUtilHelper()
        port_config_file_path = device_info.get_path_to_port_config_file()
        sfputil_helper.read_porttab_mappings(port_config_file_path, 0)

        from sonic_platform.sfp import Sfp
        for index in range(0, NUM_SFP):
            name_idx = 0 if index+1 == NUM_SFP else index+1
            sfp = Sfp(index, sfputil_helper.logical[name_idx])
            self._sfp_list.append(sfp)
        self.sfp_module_initialized = True

    def __initialize_psu(self):
        from sonic_platform.psu import Psu
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

    def __initialize_fan(self):
        from sonic_platform.fan import Fan
        for fant_index in range(0, NUM_FAN_TRAY):
            for fan_index in range(0, NUM_FAN):
                fan = Fan(fant_index, fan_index)
                self._fan_list.append(fan)

    def __initialize_thermals(self):
        from sonic_platform.thermal import Thermal
        for index in range(0, NUM_THERMAL):
            thermal = Thermal(index)
            self._thermal_list.append(thermal)

    def __initialize_eeprom(self):
        from sonic_platform.eeprom import Tlv
        self._eeprom = Tlv()

    def __initialize_components(self):
        from sonic_platform.component import Component
        for index in range(0, NUM_COMPONENT):
            component = Component(index)
            self._component_list.append(component)

    def __is_host(self):
        return os.system(HOST_CHK_CMD) == 0

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return None

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.get_mac()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.get_eeprom()

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot

        Returns:
            A tuple (string, string) where the first element is a string
            containing the cause of the previous reboot. This string must be
            one of the predefined strings in this class. If the first string
            is "REBOOT_CAUSE_HARDWARE_OTHER", the second string can be used
            to pass a description of the reboot cause.
        """
        description = 'None'
        reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
        hw_reboot_cause = self._component_list[0].get_register_value(
            RESET_REGISTER)
        sw_reboot_cause = self.__read_txt_file(
            self._reboot_cause_path) or "Unknown"

        if hw_reboot_cause == "0x55":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = sw_reboot_cause
        elif hw_reboot_cause == "0x11":
            reboot_cause = self.REBOOT_CAUSE_POWER_LOSS
        elif hw_reboot_cause == "0x33":
            reboot_cause = self.REBOOT_CAUSE_WATCHDOG
        else:
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'Unknown reason'

        return (reboot_cause, description)

    def get_watchdog(self):
        """
        Retreives hardware watchdog device on this chassis
        Returns:
            An object derived from WatchdogBase representing the hardware
            watchdog device
        """
        if self._watchdog is None:
            from sonic_platform.watchdog import Watchdog
            self._watchdog = Watchdog()

        return self._watchdog

    def get_change_event(self, timeout=0):
        """
        Returns a nested dictionary containing all devices which have
        experienced a change at chassis level
        Args:
            timeout: Timeout in milliseconds (optional). If timeout == 0,
                this method will block until a change is detected.
        Returns:
            (bool, dict):
                - True if call successful, False if not;
                - A nested dictionary where key is a device type,
                  value is a dictionary with key:value pairs in the format of
                  {'device_id':'device_event'},
                  where device_id is the device ID for this device and
                        device_event,
                             status='1' represents device inserted,
                             status='0' represents device removed.
                  Ex. {'fan':{'0':'0', '2':'1'}, 'sfp':{'11':'0'}}
                      indicates that fan 0 has been removed, fan 2
                      has been inserted and sfp 11 has been removed.
        """
        # SFP event
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        sfp_event = SfpEvent(self._sfp_list).get_sfp_event(timeout)
        if sfp_event:
            return True, {'sfp': sfp_event}

        return False, {'sfp': {}}

    ##############################################################
    ######################## SFP methods #########################
    ##############################################################

    def get_num_sfps(self):
        """
        Retrieves the number of sfps available on this chassis
        Returns:
            An integer, the number of sfps available on this chassis
        """
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        return len(self._sfp_list)

    def get_all_sfps(self):
        """
        Retrieves all sfps available on this chassis
        Returns:
            A list of objects derived from SfpBase representing all sfps
            available on this chassis
        """
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        return self._sfp_list

    def get_sfp(self, index):
        """
        Retrieves sfp represented by (1-based) index <index>
        Args:
            index: An integer, the index (1-based) of the sfp to retrieve.
            The index should be the sequence of a physical port in a chassis,
            starting from 1.
            For example, 1 for Ethernet0, 2 for Ethernet4 and so on.
        Returns:
            An object dervied from SfpBase representing the specified sfp
        """
        sfp = None
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        try:
            # The index will start from 1
            sfp = self._sfp_list[index-1]
        except IndexError:
            sys.stderr.write("SFP index {} out of range (1-{})\n".format(
                             index, len(self._sfp_list)))
        return sfp

    ##############################################################
    ###################### Device methods ########################
    ##############################################################

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return self._api_helper.hwsku

    def get_presence(self):
        """
        Retrieves the presence of the Chassis
        Returns:
            bool: True if Chassis is present, False if not
        """
        return True

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self._eeprom.get_pn()

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return self._eeprom.get_serial()

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return True
