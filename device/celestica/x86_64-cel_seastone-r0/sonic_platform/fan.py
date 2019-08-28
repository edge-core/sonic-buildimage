#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################

import json
import math
import os.path

try:
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

EMC2305_PATH = "/sys/bus/i2c/drivers/emc2305/"
SYS_GPIO_DIR = "/sys/class/gpio"
EMC2305_MAX_PWM = 255
EMC2305_FAN_PWM = "pwm{}"
EMC2305_FAN_TARGET = "fan{}_target"
EMC2305_FAN_INPUT = "pwm{}"
FAN_NAME_LIST = ["FAN-1", "FAN-2", "FAN-3", "FAN-4", "FAN-5"]


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_index):
        self.index = fan_index
        self.config_data = {}
        self.fan_speed = 0
        FanBase.__init__(self)

        # dx010 fan attributes
        # Two EMC2305s located at i2c-13-4d and i2c-13-2e
        # to control a dual-fan module.
        self.dx010_emc2305_chip = [
            {
                'device': "13-002e",
                'index_map': [2, 1, 4, 5, 3]
            },
            {
                'device': "13-004d",
                'index_map': [2, 4, 5, 3, 1]
            }
        ]

        self.dx010_fan_gpio = [
            {'base': self.get_gpio_base()},
            {'prs': 10, 'dir': 15, 'color': {'red': 31, 'green': 32}},
            {'prs': 11, 'dir': 16, 'color': {'red': 29, 'green': 30}},
            {'prs': 12, 'dir': 17, 'color': {'red': 35, 'green': 36}},
            {'prs': 13, 'dir': 18, 'color': {'red': 37, 'green': 38}},
            {'prs': 14, 'dir': 19, 'color': {'red': 33, 'green': 34}},
        ]

    def get_gpio_base(self):
        for r in os.listdir(SYS_GPIO_DIR):
            if "gpiochip" in r:
                return int(r[8:], 10)
        return 216  # Reserve

    def get_gpio_value(self, pinnum):
        gpio_base = self.dx010_fan_gpio[0]['base']

        gpio_dir = SYS_GPIO_DIR + '/gpio' + str(gpio_base+pinnum)
        gpio_file = gpio_dir + "/value"

        try:
            with open(gpio_file, 'r') as fd:
                retval = fd.read()
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

        retval = retval.rstrip('\r\n')
        return retval

    def set_gpio_value(self, pinnum, value=0):
        gpio_base = self.dx010_fan_gpio[0]['base']

        gpio_dir = SYS_GPIO_DIR + '/gpio' + str(gpio_base+pinnum)
        gpio_file = gpio_dir + "/value"

        try:
            with open(gpio_file, 'w') as fd:
                retval = fd.write(str(value))
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

    def get_direction(self):

        direction = self.FAN_DIRECTION_INTAKE
        raw = self.get_gpio_value(self.dx010_fan_gpio[self.index+1]['dir'])

        if int(raw, 10) == 0:
            direction = self.FAN_DIRECTION_INTAKE
        else:
            direction = self.FAN_DIRECTION_EXHAUST

        return direction

    def get_speed(self):
        """
        DX010 platform specific data:

            speed = pwm_in/255*100
        """
        # TODO: Seperate PSU's fan and main fan class
        if self.fan_speed != 0:
            return self.fan_speed
        else:
            speed = 0
            pwm = []
            emc2305_chips = self.dx010_emc2305_chip

            for chip in emc2305_chips:
                device = chip['device']
                fan_index = chip['index_map']
                sysfs_path = "%s%s/%s" % (
                    EMC2305_PATH, device, EMC2305_FAN_INPUT)
                sysfs_path = sysfs_path.format(fan_index[self.index])
                try:
                    with open(sysfs_path, 'r') as file:
                        raw = file.read().strip('\r\n')
                        pwm.append(int(raw, 10))
                except IOError:
                    raise IOError("Unable to open " + sysfs_path)

                speed = math.ceil(
                    float(pwm[0]) * 100 / EMC2305_MAX_PWM)

            return int(speed)

    def get_target_speed(self):
        """
        DX010 platform specific data:

            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use

        """
        target = 0
        pwm = []
        emc2305_chips = self.dx010_emc2305_chip

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_PATH, device, EMC2305_FAN_TARGET)
            sysfs_path = sysfs_path.format(fan_index[self.index])
            try:
                with open(sysfs_path, 'r') as file:
                    raw = file.read().strip('\r\n')
                    pwm.append(int(raw, 10))
            except IOError:
                raise IOError("Unable to open " + sysfs_path)

            target = pwm[0] * 100 / EMC2305_MAX_PWM

        return target

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        return 10

    def set_speed(self, speed):
        """
        Depends on pwm or target mode is selected:
            1) pwm = speed_pc * 255             <-- Currently use this mode.
            2) target_pwm = speed_pc * 100 / 255
             2.1) set pwm{}_enable to 3

        """
        pwm = speed * 255 / 100
        emc2305_chips = self.dx010_emc2305_chip

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_PATH, device, EMC2305_FAN_PWM)
            sysfs_path = sysfs_path.format(fan_index[self.index])
            try:
                with open(sysfs_path, 'w') as file:
                    file.write(str(int(pwm)))
            except IOError:
                return False

        return True

    def set_status_led(self, color):
        try:
            if color == self.STATUS_LED_COLOR_GREEN:
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['red'], 1)
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['green'], 0)

            elif color == self.STATUS_LED_COLOR_RED:
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['red'], 0)
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['green'], 1)

            elif color == self.STATUS_LED_COLOR_OFF:
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['red'], 1)
                self.set_gpio_value(
                    self.dx010_fan_gpio[self.index+1]['color']['green'], 1)
            else:
                return False

        except IOError:
            return False

        return True

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return FAN_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        raw = self.get_gpio_value(self.dx010_fan_gpio[self.index+1]['prs'])

        return int(raw, 10) == 0
