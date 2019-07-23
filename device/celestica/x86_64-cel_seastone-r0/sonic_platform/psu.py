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

FAN_DX010_SPEED_PATH = "/sys/class/hwmon/hwmon{}/fan1_input"
GREEN_LED_PATH = "/sys/devices/platform/leds_dx010/leds/dx010:green:p-{}/brightness"
FAN_MAX_RPM = 11000
SYS_GPIO_DIR = "/sys/class/gpio"
PSU_NAME_LIST = ["PSU-1", "PSU-2"]


class Psu(PsuBase):
    """Platform-specific Psu class"""

    def __init__(self, psu_index):
        PsuBase.__init__(self)
        self.index = psu_index
        self.green_led_path = GREEN_LED_PATH.format(self.index+1)
        self.dx010_psu_gpio = [
            {'base': self.get_gpio_base()},
            {'prs': 27, 'status': 22},
            {'prs': 28, 'status': 25}
        ]

    def get_gpio_base(self):
        for r in os.listdir(SYS_GPIO_DIR):
            if "gpiochip" in r:
                return int(r[8:], 10)
        return 216  # Reserve

    def get_gpio_value(self, pinnum):
        gpio_base = self.dx010_psu_gpio[0]['base']
        gpio_file = "{}/gpio{}/value".format(SYS_GPIO_DIR,
                                             str(gpio_base+pinnum))

        try:
            with open(gpio_file, 'r') as fd:
                retval = fd.read()
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

        retval = retval.rstrip('\r\n')
        return retval

    def get_fan(self):
        """
        Retrieves object representing the fan module contained in this PSU
        Returns:
            An object dervied from FanBase representing the fan module
            contained in this PSU
        """

        fan_speed_path = FAN_DX010_SPEED_PATH.format(
            str(self.index+8))
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

        set_status_str = {
            self.STATUS_LED_COLOR_GREEN: '1',
            self.STATUS_LED_COLOR_OFF: '0'
        }.get(color, None)

        if not set_status_str:
            return False

        try:
            with open(self.green_led_path, 'w') as file:
                file.write(set_status_str)
        except IOError:
            return False

        return True

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
        raw = self.get_gpio_value(self.dx010_psu_gpio[self.index+1]['prs'])
        return int(raw, 10) == 0

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        raw = self.get_gpio_value(self.dx010_psu_gpio[self.index+1]['status'])
        return int(raw, 10) == 1
