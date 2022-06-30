#!/usr/bin/env python

#############################################################################
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import os.path

try:
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = []
    SYSFS_THERMAL_DIR = ["/sys/bus/i2c/devices/0-004f/",
                         "/sys/bus/i2c/devices/0-0049/",
                         "/sys/bus/i2c/devices/0-004a/",
                         "/sys/bus/i2c/devices/0-004b/",
                         "/sys/bus/i2c/devices/0-004c/",
                         "/sys/bus/i2c/devices/0-004d/",
                         "/sys/bus/i2c/devices/0-004e/"]

    def __init__(self, thermal_index):
        self.index = thermal_index

        # Add thermal name
        self.THERMAL_NAME_LIST.append("Top-Rear")
        self.THERMAL_NAME_LIST.append("Top-Front")
        self.THERMAL_NAME_LIST.append("Right-Front")
        self.THERMAL_NAME_LIST.append("Top-Center")
        self.THERMAL_NAME_LIST.append("Left-Front")
        self.THERMAL_NAME_LIST.append("Bottom-Front")
        self.THERMAL_NAME_LIST.append("Bottom-Rear")
        ThermalBase.__init__(self)

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return ""

    def __get_temp(self, temp_file):
        temp_file_path = os.path.join(self.SYSFS_THERMAL_DIR[self.index], temp_file)
        raw_temp = self.__read_txt_file(temp_file_path)
        temp = float(raw_temp)/1000
        return "{:.3f}".format(temp)

    def __set_threshold(self, file_name, temperature):
        temp_file_path = os.path.join(self.hwmon_path, file_name)
        try:
            with open(temp_file_path, 'w') as fd:
                fd.write(str(temperature))
            return True
        except IOError:
            return False

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        temp_file = "temp1_input"
        return float(self.__get_temp(temp_file))

    def get_low_threshold(self):
        """
        Retrieves the low threshold temperature of thermal
        :return: A float number, the low threshold temperature of thermal in Celsius
                 up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return int(9)

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold temperature of thermal
        :return: A float number, the low critical threshold temperature of thermal in Celsius
                 up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return int(7)

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.index==0:
            return int(56)
        elif self.index==1:
            return int(74)
        elif self.index==2:
            return int(55)
        elif self.index==3:
            return int(74)
        elif self.index==4:
            return int(55)
        elif self.index==5:
            return int(74)
        else:
            return int(56)

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal
        :return: A float number, the high critical threshold temperature of thermal in Celsius
                 up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.index==0:
            return int(58)
        elif self.index==1:
            return int(76)
        elif self.index==2:
            return int(57)
        elif self.index==3:
            return int(76)
        elif self.index==4:
            return int(57)
        elif self.index==5:
            return int(76)
        else:
            return int(58)

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        return self.THERMAL_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        temp_file = "temp1_input"
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        return os.path.isfile(temp_file_path)

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if not self.get_presence():
            return False

        return True

