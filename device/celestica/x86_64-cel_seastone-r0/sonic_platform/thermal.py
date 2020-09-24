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
    from helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = []
    I2C_ADAPTER_PATH = "/sys/class/i2c-adapter"
    SS_CONFIG_PATH = "/usr/share/sonic/device/x86_64-cel_seastone-r0/sensors.conf"

    def __init__(self, thermal_index):
        self.index = thermal_index
        self._api_helper = APIHelper()

        # Add thermal name
        self.THERMAL_NAME_LIST.append("Front-panel temp sensor 1")
        self.THERMAL_NAME_LIST.append("Front-panel temp sensor 2")
        self.THERMAL_NAME_LIST.append("ASIC temp sensor")
        self.THERMAL_NAME_LIST.append("Rear-panel temp sensor 1")
        self.THERMAL_NAME_LIST.append("Rear-panel temp sensor 2")

        # Set hwmon path
        i2c_path = {
            0: "i2c-5/5-0048/hwmon/hwmon1",    # u4 system-inlet
            1: "i2c-6/6-0049/hwmon/hwmon2",    # u2 system-inlet
            2: "i2c-7/7-004a/hwmon/hwmon3",    # u44 bmc56960-on-board
            3: "i2c-14/14-0048/hwmon/hwmon4",  # u9200 cpu-on-board
            4: "i2c-15/15-004e/hwmon/hwmon5"   # u9201 system-outlet
        }.get(self.index, None)

        self.hwmon_path = "{}/{}".format(self.I2C_ADAPTER_PATH, i2c_path)
        self.ss_key = self.THERMAL_NAME_LIST[self.index]
        self.ss_index = 1

    def __get_temp(self, temp_file):
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        raw_temp = self._api_helper.read_txt_file(temp_file_path)
        temp = float(raw_temp)/1000
        return float("{:.3f}".format(temp))

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
                            content[idx] = "    set {} {}\n".format(
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
