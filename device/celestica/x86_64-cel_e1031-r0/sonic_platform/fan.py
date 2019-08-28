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

EMC2305_FAN_PATH = "/sys/bus/i2c/drivers/emc2305/"
FAN_PATH = "/sys/devices/platform/e1031.smc/"
SYS_GPIO_DIR = "/sys/class/gpio"
EMC2305_MAX_PWM = 255
EMC2305_FAN_PWM = "pwm{}"
EMC2305_FAN_TARGET = "fan{}_target"
EMC2305_FAN_INPUT = "pwm{}"
FAN_NAME_LIST = ["FAN-1", "FAN-2", "FAN-3"]


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_index):
        self.index = fan_index
        self.config_data = {}
        self.fan_speed = 0
        FanBase.__init__(self)

        # e1031 fan attributes
        # Single emc2305 chip located at i2c-23-4d
        # to control a fan module
        self.e1031_emc2305_chip = [
            {
                'device': "23-004d",
                'index_map': [1, 2, 4]
            }
        ]

        self.fan_e1031_presence = "fan{}_prs"
        self.fan_e1031_direction = "fan{}_dir"
        self.fan_e1031_led = "fan{}_led"
        self.fan_e1031_led_col_map = {
            self.STATUS_LED_COLOR_GREEN: "green",
            self.STATUS_LED_COLOR_RED: "amber",
            self.STATUS_LED_COLOR_OFF: "off"
        }
        FanBase.__init__(self)

    def get_direction(self):

        direction = self.FAN_DIRECTION_INTAKE

        try:
            fan_direction_file = (FAN_PATH +
                                  self.fan_e1031_direction.format(self.index+1))
            with open(fan_direction_file, 'r') as file:
                raw = file.read().strip('\r\n')
            if str(raw).upper() == "F2B":
                direction = self.FAN_DIRECTION_INTAKE
            else:
                direction = self.FAN_DIRECTION_EXHAUST
        except IOError:
            return False

        return direction

    def get_speed(self):
        """
        E1031 platform specific data:

            speed = pwm_in/255*100
        """
        # TODO: Seperate PSU's fan and main fan class
        if self.fan_speed != 0:
            return self.fan_speed
        else:
            speed = 0
            pwm = []
            emc2305_chips = self.e1031_emc2305_chip

            for chip in emc2305_chips:
                device = chip['device']
                fan_index = chip['index_map']
                sysfs_path = "%s%s/%s" % (
                    EMC2305_FAN_PATH, device, EMC2305_FAN_INPUT)
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
        E1031 platform specific data:

            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use

        """
        target = 0
        pwm = []
        emc2305_chips = self.e1031_emc2305_chip

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_FAN_PATH, device, EMC2305_FAN_TARGET)
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
        emc2305_chips = self.e1031_emc2305_chip

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_FAN_PATH, device, EMC2305_FAN_PWM)
            sysfs_path = sysfs_path.format(fan_index[self.index])
            try:
                with open(sysfs_path, 'w') as file:
                    file.write(str(int(pwm)))
            except IOError:
                return False

        return True

    def set_status_led(self, color):

        try:
            fan_led_file = (FAN_PATH +
                            self.fan_e1031_led.format(self.index+1))
            with open(fan_led_file, 'r') as file:
                file.write(self.fan_e1031_led_col_map[color])
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

        try:
            fan_direction_file = (FAN_PATH +
                                  self.fan_e1031_presence.format(self.index+1))
            with open(fan_direction_file, 'r') as file:
                present = int(file.read().strip('\r\n'))
        except IOError:
            return False

        return present == 0
