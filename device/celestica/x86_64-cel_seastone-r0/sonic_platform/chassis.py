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
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

CONFIG_DB_PATH = "/etc/sonic/config_db.json"
NUM_FAN = 5
NUM_PSU = 2


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

    def __read_config_db(self):
        try:
            with open(CONFIG_DB_PATH, 'r') as fd:
                data = json.load(fd)
                return data
        except IOError:
            raise IOError("Unable to open config_db file !")

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
            raise KeyError("Base MAC not found")

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
