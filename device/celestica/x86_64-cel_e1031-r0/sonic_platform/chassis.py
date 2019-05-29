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
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

MMC_CPLD_ADDR = '0x100'
BIOS_VERSION_PATH = "/sys/class/dmi/id/bios_version"
CONFIG_DB_PATH = "/etc/sonic/config_db.json"
SMC_CPLD_PATH = "/sys/devices/platform/e1031.smc/version"
MMC_CPLD_PATH = "/sys/devices/platform/e1031.smc/getreg"
NUM_FAN = 3


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        self.config_data = {}
        for index in range(0, NUM_FAN):
            fan = Fan(index)
            self._fan_list.append(fan)
        ChassisBase.__init__(self)

    def __get_register_value(self, path, register):
        cmd = "echo {1} > {0}; cat {0}".format(path, register)
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        if err is not '':
            return 'None'
        else:
            return raw_data.strip()

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

    def get_component_versions(self):
        """
        Retrieves platform-specific hardware/firmware versions for chassis
        componenets such as BIOS, CPLD, FPGA, etc.
        Returns:
            A string containing platform-specific component versions
        """

        component_versions = dict()

        # Get BIOS version
        try:
            with open(BIOS_VERSION_PATH, 'r') as fd:
                bios_version = fd.read()
        except IOError:
            raise IOError("Unable to open version file !")

        # Get CPLD version
        cpld_version = dict()

        with open(SMC_CPLD_PATH, 'r') as fd:
            smc_cpld_version = fd.read()
        smc_cpld_version = 'None' if smc_cpld_version is 'None' else "{}.{}".format(
            int(smc_cpld_version[2], 16), int(smc_cpld_version[3], 16))

        mmc_cpld_version = self.__get_register_value(
            MMC_CPLD_PATH, MMC_CPLD_ADDR)
        mmc_cpld_version = 'None' if mmc_cpld_version is 'None' else "{}.{}".format(
            int(mmc_cpld_version[2], 16), int(mmc_cpld_version[3], 16))

        cpld_version["SMC"] = smc_cpld_version
        cpld_version["MMC"] = mmc_cpld_version

        component_versions["CPLD"] = cpld_version
        component_versions["BIOS"] = bios_version.strip()
        return str(component_versions)
