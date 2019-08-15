#!/usr/bin/env python

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
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.fan import Fan
    from sonic_platform.psu import Psu
    from sonic_platform.component import Component
    from sonic_platform.watchdog import Watchdog
    from sonic_platform.thermal import Thermal
    from sonic_platform.sfp import Sfp
    from sonic_platform.eeprom import Tlv
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_FAN = 5
NUM_PSU = 2
NUM_THERMAL = 5
NUM_SFP = 32
RESET_REGISTER = "0x103"
REBOOT_CAUSE_PATH = "/host/reboot-cause/previous-reboot-cause.txt"
COMPONENT_NAME_LIST = ["CPLD1", "CPLD2", "CPLD3", "CPLD4", "BIOS"]


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        self.config_data = {}
        for index in range(0, NUM_FAN):
            fan = Fan(index)
            self._fan_list.append(fan)
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)
        for index in range(0, NUM_THERMAL):
            thermal = Thermal(index)
            self._thermal_list.append(thermal)
        for index in range(0, NUM_SFP):
            sfp = Sfp(index)
            self._sfp_list.append(sfp)
        ChassisBase.__init__(self)
        self._component_name_list = COMPONENT_NAME_LIST
        self._watchdog = Watchdog()
        self._eeprom = Tlv()

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            raise IOError("Unable to open %s file !" % file_path)

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.get_mac()

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis
        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self._eeprom.get_serial()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.get_eeprom()

    def get_firmware_version(self, component_name):
        """
        Retrieves platform-specific hardware/firmware versions for chassis
        componenets such as BIOS, CPLD, FPGA, etc.
        Args:
            type: A string, component name

        Returns:
            A string containing platform-specific component versions
        """
        self.component = Component(component_name)
        if component_name not in self._component_name_list:
            return None
        return self.component.get_firmware_version()

    def install_component_firmware(self, component_name, image_path):
        """
        Install firmware to module
        Args:
            type: A string, component name.
            image_path: A string, path to firmware image.

        Returns:
            A boolean, True if install successfully, False if not
        """
        self.component = Component(component_name)
        if component_name not in self._component_name_list:
            return False
        return self.component.upgrade_firmware(image_path)

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
        self.component = Component("CPLD1")
        description = 'None'
        reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
        hw_reboot_cause = self.component.get_register_value(RESET_REGISTER)
        sw_reboot_cause = self.__read_txt_file(REBOOT_CAUSE_PATH)

        if sw_reboot_cause != "Unexpected reboot":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = sw_reboot_cause
        elif hw_reboot_cause == "0x11":
            reboot_cause = self.REBOOT_CAUSE_POWER_LOSS
        elif hw_reboot_cause == "0x22":
            reboot_cause = self.REBOOT_CAUSE_WATCHDOG,
        else:
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'Unknown reason'

        return (reboot_cause, description)
