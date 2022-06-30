#!/usr/bin/env python

#############################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################

import os.path

try:
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FAN_PATH = "/sys/bus/i2c/devices/0-0066/"
FANTRAY_NAME_LIST = ["FANTRAY-1", "FANTRAY-2",
                     "FANTRAY-3", "FANTRAY-4",
                     "FANTRAY-5", "FANTRAY-6", "FANTRAY-7"]
FAN_NAME_LIST = ["fan1_front","fan2_front","fan3_front","fan4_front","fan5_front","fan6_front", "fan7_front",\
"fan1_rear","fan2_rear","fan3_rear","fan4_rear", "fan5_rear", "fan6_rear", "fan7_rear",]

class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_index):
        self.fan_tray_index = fan_index
        self.fan_presence = "fan{}_presence"
        self.fan_direction = "fan{}_direction"
        self.fan_speed_rpm = "fan{}_{}_speed_rpm"
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
        except BaseException:
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
        index1=self.fan_tray_index
        if self.fan_tray_index>6:
            index1=self.fan_tray_index%7
        fan_direction_file = (FAN_PATH +
            self.fan_direction.format(index1+1))
        raw = self.__read_txt_file(fan_direction_file).strip('\r\n')
        direction = self.FAN_DIRECTION_INTAKE if str(
            raw).upper() == "1" else self.FAN_DIRECTION_EXHAUST

        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 12000 (full speed)
        """
        if self.fan_tray_index<=6:
            index1=self.fan_tray_index
            speed = 0
            if self.get_presence():
                fan_speed_file = (FAN_PATH +
                self.fan_speed_rpm.format(index1+1,"front"))
                speed = self.__read_txt_file(fan_speed_file).strip('\r\n')
        else:
            index1=self.fan_tray_index%7
            if self.get_presence():
                fan_speed_file = (FAN_PATH +
                self.fan_speed_rpm.format(index1+1,"rear"))
                speed = self.__read_txt_file(fan_speed_file).strip('\r\n')
            
        return int(speed)

    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        """
        if self.fan_tray_index<=6:
            index1=self.fan_tray_index
            speed = 0
            if self.get_presence():
                fan_speed_file = (FAN_PATH +
                self.fan_speed_rpm.format(index1+1,"front"))
                speed = self.__read_txt_file(fan_speed_file).strip('\r\n')
        else:
            index1=self.fan_tray_index%7
            if self.get_presence():
                fan_speed_file = (FAN_PATH +
                self.fan_speed_rpm.format(index1+1,"rear"))
                speed = self.__read_txt_file(fan_speed_file).strip('\r\n')

        return int(speed)

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
        return False

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        fan_name = FAN_NAME_LIST[self.fan_tray_index]

        return fan_name

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        index1=self.fan_tray_index
        if self.fan_tray_index>6:
            index1=self.fan_tray_index%7
        fan_direction_file = (FAN_PATH +
                              self.fan_presence.format(index1+1))
        present_str = self.__read_txt_file(fan_direction_file) or '1'

        return int(present_str) == 1

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence() and self.get_speed() > 0
