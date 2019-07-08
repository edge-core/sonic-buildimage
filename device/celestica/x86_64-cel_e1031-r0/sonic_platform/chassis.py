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
    from sonic_platform.device import Device
    from sonic_platform.component import Component
    from sonic_platform.watchdog import Watchdog
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

CONFIG_DB_PATH = "/etc/sonic/config_db.json"
NUM_FAN = 3
NUM_PSU = 2
RESET_REGISTER = "0x112"
REBOOT_CAUSE_PATH = "/host/reboot-cause/previous-reboot-cause.txt"


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
        ChassisBase.__init__(self)
        self._component_device = Device("component")
        self._component_name_list = self._component_device.get_name_list()
        self._watchdog = Watchdog()

    def __read_config_db(self):
        try:
            with open(CONFIG_DB_PATH, 'r') as fd:
                data = json.load(fd)
                return data
        except IOError:
            raise IOError("Unable to open config_db file !")

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
        try:
            self.config_data = self.__read_config_db()
            base_mac = self.config_data["DEVICE_METADATA"]["localhost"]["mac"]
            return str(base_mac)
        except KeyError:
            return str(None)

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
        self.component = Component("SMC_CPLD")
        description = 'None'
        reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
        hw_reboot_cause = self.component.get_register_value(RESET_REGISTER)
        sw_reboot_cause = self.__read_txt_file(REBOOT_CAUSE_PATH)

        if sw_reboot_cause != "Unexpected reboot":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
        elif hw_reboot_cause == "0x11":
            reboot_cause = self.REBOOT_CAUSE_POWER_LOSS
        elif hw_reboot_cause == "0x33" or hw_reboot_cause == "0x55":
            reboot_cause = self.REBOOT_CAUSE_WATCHDOG
        else:
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'Unknown reason'

        return (reboot_cause, description)
