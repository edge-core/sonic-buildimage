#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs status which are available in the platform
#
#############################################################################

import os.path
import sonic_platform

try:
    from sonic_platform_base.psu_base import PsuBase
    from sonic_platform.fan import Fan
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FAN_E1031_SPEED_PATH = "/sys/class/hwmon/hwmon{}/fan1_input"
FAN_MAX_RPM = 11000
PSU_NAME_LIST = ["PSU-R", "PSU-L"]


class Psu(PsuBase):
    """Platform-specific Psu class"""

    def __init__(self, psu_index):
        PsuBase.__init__(self)
        self.index = psu_index
        self.psu_path = "/sys/devices/platform/e1031.smc/"
        self.psu_presence = "psu{}_prs"
        self.psu_oper_status = "psu{}_status"

    def get_fan(self):
        """
        Retrieves object representing the fan module contained in this PSU
        Returns:
            An object dervied from FanBase representing the fan module
            contained in this PSU
        """
        fan_speed_path = FAN_E1031_SPEED_PATH.format(
            str(self.index+3))
        try:
            with open(fan_speed_path) as fan_speed_file:
                fan_speed_rpm = int(fan_speed_file.read())
        except IOError:
            fan_speed = 0

        fan_speed = float(fan_speed_rpm)/FAN_MAX_RPM * 100
        fan = Fan(0)
        fan.fan_speed = int(fan_speed) if int(fan_speed) <= 100 else 100
        return fan

    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED
        Args:
            color: A string representing the color with which to set the PSU status LED
                   Note: Only support green and off
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        # Hardware not supported
        return False

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return PSU_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        psu_location = ["R", "L"]
        status = 0
        try:
            with open(self.psu_path + self.psu_presence.format(psu_location[self.index]), 'r') as psu_prs:
                status = int(psu_prs.read())
        except IOError:
            return False

        return status == 1

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        psu_location = ["R", "L"]
        status = 0
        try:
            with open(self.psu_path + self.psu_oper_status.format(psu_location[self.index]), 'r') as power_status:
                status = int(power_status.read())
        except IOError:
            return False

        return status == 1
