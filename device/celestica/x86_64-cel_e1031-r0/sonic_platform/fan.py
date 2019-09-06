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
FAN_PATH = "/sys/devices/platform/e1031.smc/"
EMC2305_MAX_PWM = 255
EMC2305_FAN_PWM = "pwm{}"
EMC2305_FAN_TARGET = "fan{}_target"
EMC2305_FAN_INPUT = "pwm{}"
FAN_NAME_LIST = ["FAN-1", "FAN-2", "FAN-3"]
PSU_FAN_MAX_RPM = 11000
PSU_HWMON_PATH = "/sys/bus/i2c/devices/i2c-{0}/{0}-00{1}/hwmon"
PSU_I2C_MAPPING = {
    0: {
        "num": 13,
        "addr": "5b"
    },
    1: {
        "num": 12,
        "addr": "5a"
    },
}


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_tray_index, fan_index=0, is_psu_fan=False, psu_index=0):
        self.fan_index = fan_index
        self.fan_tray_index = fan_tray_index
        self.is_psu_fan = is_psu_fan
        if self.is_psu_fan:
            self.psu_index = psu_index
            self.psu_i2c_num = PSU_I2C_MAPPING[self.psu_index]["num"]
            self.psu_i2c_addr = PSU_I2C_MAPPING[self.psu_index]["addr"]
            self.psu_hwmon_path = PSU_HWMON_PATH.format(
                self.psu_i2c_num, self.psu_i2c_addr)

        # e1031 fan attributes
        # Single emc2305 chip located at i2c-23-4d
        # to control a fan module
        self.emc2305_chip_mapping = [
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

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return ""

    def __write_txt_file(self, file_path, value):
        try:
            with open(file_path, 'w') as fd:
                fd.write(str(value))
        except:
            return False
        return True

    def __search_file_by_name(self, directory, file_name):
        for dirpath, dirnames, files in os.walk(directory):
            for name in files:
                file_path = os.path.join(dirpath, name)
                if name in file_name:
                    return file_path
        return None

    def get_direction(self):
        """
        Retrieves the direction of fan
        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        direction = self.FAN_DIRECTION_EXHAUST
        if not self.is_psu_fan:
            fan_direction_file = (FAN_PATH +
                                  self.fan_e1031_direction.format(self.fan_tray_index+1))
            raw = self.__read_txt_file(fan_direction_file).strip('\r\n')
            direction = self.FAN_DIRECTION_INTAKE if str(
                raw).upper() == "F2B" else self.FAN_DIRECTION_EXHAUST

        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        Note:
            speed = pwm_in/255*100
        """
        speed = 0
        if self.is_psu_fan:
            fan_speed_sysfs_name = "fan{}_input".format(self.fan_index+1)
            fan_speed_sysfs_path = self.__search_file_by_name(
                self.psu_hwmon_path, fan_speed_sysfs_name)
            fan_speed_rpm = self.__read_txt_file(fan_speed_sysfs_path) or 0
            fan_speed_raw = float(fan_speed_rpm)/PSU_FAN_MAX_RPM * 100
            speed = math.ceil(float(fan_speed_rpm) * 100 / PSU_FAN_MAX_RPM)
        elif self.get_presence():
            chip = self.emc2305_chip_mapping[self.fan_index]
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_PATH, device, EMC2305_FAN_INPUT)
            sysfs_path = sysfs_path.format(fan_index[self.fan_tray_index])
            raw = self.__read_txt_file(sysfs_path).strip('\r\n')
            pwm = int(raw, 10) if raw else 0
            speed = math.ceil(float(pwm * 100 / EMC2305_MAX_PWM))

        return int(speed)

    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        Note:
            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use
        """
        target = 0
        if not self.is_psu_fan:
            chip = self.emc2305_chip_mapping[self.fan_index]
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_PATH, device, EMC2305_FAN_TARGET)
            sysfs_path = sysfs_path.format(fan_index[self.fan_tray_index])
            raw = self.__read_txt_file(sysfs_path).strip('\r\n')
            pwm = int(raw, 10) if raw else 0
            target = math.ceil(float(pwm) * 100 / EMC2305_MAX_PWM)

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
        Sets the fan speed
        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 0 (off) to 100 (full speed)
        Returns:
            A boolean, True if speed is set successfully, False if not

        Note:
            Depends on pwm or target mode is selected:
            1) pwm = speed_pc * 255             <-- Currently use this mode.
            2) target_pwm = speed_pc * 100 / 255
             2.1) set pwm{}_enable to 3

        """
        pwm = speed * 255 / 100
        if not self.is_psu_fan and self.get_presence():
            chip = self.emc2305_chip_mapping[self.fan_index]
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                EMC2305_PATH, device, EMC2305_FAN_PWM)
            sysfs_path = sysfs_path.format(fan_index[self.fan_tray_index])
            return self.__write_txt_file(sysfs_path, int(pwm))

        return False

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        set_status_led = False
        if not self.is_psu_fan:
            fan_led_file = (FAN_PATH +
                            self.fan_e1031_led.format(self.fan_tray_index+1))

            set_status_led = self.__write_txt_file(
                fan_led_file, self.fan_e1031_led_col_map[color]) if self.get_presence() else False

        return set_status_led

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        fan_name = FAN_NAME_LIST[self.fan_tray_index] if not self.is_psu_fan else "PSU-{} FAN-{}".format(
            self.psu_index+1, self.fan_index+1)

        return fan_name

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        fan_direction_file = (FAN_PATH +
                              self.fan_e1031_presence.format(self.fan_tray_index+1))
        present_str = self.__read_txt_file(fan_direction_file) or '1'

        return int(present_str) == 0 if not self.is_psu_fan else True
