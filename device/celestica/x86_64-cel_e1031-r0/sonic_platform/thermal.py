#!/usr/bin/env python

#############################################################################
# Celestica
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import re
import os.path

try:
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = []
    MAINBOARD_SS_PATH = "/sys/class/i2c-adapter/i2c-11/11-001a/hwmon/hwmon2"
    CPUBOARD_SS_PATH = "/sys/class/i2c-adapter/i2c-3/3-001a/hwmon/hwmon1"
    SS_CONFIG_PATH = "/usr/share/sonic/device/x86_64-cel_e1031-r0/sensors.conf"

    def __init__(self, thermal_index):
        self.index = thermal_index

        # Add thermal name
        self.THERMAL_NAME_LIST.append("Rear  panel-Inlet ambient sensor")
        self.THERMAL_NAME_LIST.append("Rear  panel-Helix shutdown sensor")
        self.THERMAL_NAME_LIST.append(
            "Front panel-Inlet ambient sensor (right)")
        self.THERMAL_NAME_LIST.append("Front panel-Helix shutdown sensor")
        self.THERMAL_NAME_LIST.append(
            "Front panel-Inlet ambient sensor (left)")
        self.THERMAL_NAME_LIST.append("CPU board temperature sensor : 1")
        self.THERMAL_NAME_LIST.append("CPU board temperature sensor : 2")

        # Set hwmon path
        self.ss_index, self.hwmon_path = self.__get_ss_info(self.index)
        self.ss_key = self.THERMAL_NAME_LIST[self.index]

    def __get_ss_info(self, index):
        if self.index <= 4:
            ss_path = self.MAINBOARD_SS_PATH
            ss_index = index+1
        else:
            ss_path = self.CPUBOARD_SS_PATH
            ss_index = index-3
        return ss_index, ss_path

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            raise IOError("Unable to open %s file !" % file_path)

    def __get_temp(self, temp_file):
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
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
        temp_file = "temp{}_input".format(self.ss_index)
        return self.__get_temp(temp_file)

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        temp_file = "temp{}_max".format(self.ss_index)
        return self.__get_temp(temp_file)

    def set_high_threshold(self, temperature):
        """
        Sets the high threshold temperature of thermal
        Args :
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125
        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        temp_file = "temp{}_max".format(self.ss_index)
        is_set = self.__set_threshold(temp_file, int(temperature*1000))
        file_set = False
        if is_set:
            try:
                with open(self.SS_CONFIG_PATH, 'r+') as f:
                    content = f.readlines()
                    f.seek(0)
                    ss_found = False
                    for idx, val in enumerate(content):
                        if self.ss_key in val:
                            ss_found = True
                        elif ss_found and temp_file in val:
                            content[idx] = "        set {} {}\n".format(
                                temp_file, temperature)
                            f.writelines(content)
                            file_set = True
                            break
            except IOError:
                file_set = False

        return is_set & file_set

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
        temp_file = "temp{}_input".format(self.ss_index)
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

        fault_file = "temp{}_fault".format(self.ss_index)
        fault_file_path = os.path.join(self.hwmon_path, fault_file)
        if not os.path.isfile(fault_file_path):
            return True

        raw_txt = self.__read_txt_file(fault_file_path)
        return int(raw_txt) == 0
