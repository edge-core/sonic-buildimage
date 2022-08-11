#!/usr/bin/env python

#############################################################################
# Celestica
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import os.path

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NULL_VAL = "N/A"
I2C_ADAPTER_PATH = "/sys/class/i2c-adapter"
IPMI_SENSOR_TEMP_CMD = "ipmitool sensor | grep degrees"
THERMAL_INFO = [
    {'name': 'TEMP_FB_U52', 'temp': 'na'},  # 0
    {'name': 'TEMP_FB_U17', 'temp': 'na'},  # 1
    {'name': 'TEMP_SW_U2', 'temp': 'na'},  # 2
    {'name': 'TEMP_CPU', 'temp': 'na'},  # 3
    {'name': 'TEMP_DIMM0', 'temp': 'na'},  # 4
    {'name': 'TEMP_DIMM1', 'temp': 'na'},  # 5
    {'name': 'TEMP_SW_Internal', 'temp': 'na'},  # 6
    {'name': 'PSU1_Temp1', 'temp': 'na'},  # 7
    {'name': 'PSU1_Temp2', 'temp': 'na'},  # 8
    {'name': 'PSU1_Temp3', 'temp': 'na'},  # 9
    {'name': 'PSU2_Temp1', 'temp': 'na'},  # 10
    {'name': 'PSU2_Temp2', 'temp': 'na'},  # 11
    {'name': 'PSU2_Temp3', 'temp': 'na'},  # 12
    {'name': 'TEMP_SW_U52', 'temp': 'na'},  # 13
    {'name': 'TEMP_SW_U16', 'temp': 'na'},  # 14
    {'name': 'I89_CORE_Temp', 'temp': 'na'},  # 15
    {'name': 'I89_AVDD_Temp', 'temp': 'na'},  # 16
    {'name': 'QSFP_DD_Temp1', 'temp': 'na'},  # 17
    {'name': 'QSFP_DD_Temp2', 'temp': 'na'},  # 18
]

thermal_temp_dict = {
    "TEMP_FB_U52": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "TEMP_FB_U17": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": {"B2F": 52, "F2B": NULL_VAL}, "high_critical_threshold": {"B2F": 57, "F2B": NULL_VAL}},
    "TEMP_SW_U2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "TEMP_CPU": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": 103, "high_critical_threshold": NULL_VAL},
    "TEMP_DIMM0": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": 85},
    "TEMP_DIMM1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max":NULL_VAL, "high_critical_threshold": 85},
    "TEMP_SW_Internal": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": 105, "high_critical_threshold": 111},
    "PSU1_Temp1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": 60},
    "PSU1_Temp2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": 113},
    "PSU1_Temp3": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": {"B2F": 75, "F2B": 88}},
    "PSU2_Temp1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": 60},
    "PSU2_Temp2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": 113},
    "PSU2_Temp3": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": {"B2F": 75, "F2B": 88}},
    "TEMP_SW_U52": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": {"B2F": NULL_VAL, "F2B": 58}, "high_critical_threshold": {"B2F": NULL_VAL, "F2B": 62}},
    "TEMP_SW_U16": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_CORE_Temp": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 125},
    "I89_AVDD_Temp": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 125},
    "QSFP_DD_Temp1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 125},
    "QSFP_DD_Temp2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 125},
}



temp_result = []
class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    SS_CONFIG_PATH = "/usr/share/sonic/device/x86_64-cel_silverstone-x-r0/sonic_platform/sensors.conf"

    def __init__(self, thermal_index, airflow):

        self.index = thermal_index
        self._api_helper = APIHelper()
        self._airflow = str(airflow).upper()
        self._thermal_info = THERMAL_INFO[self.index]
        self.name = self.get_name()

    def __get_thermal_info(self):
        """
        Complete other path information according to the corresponding BUS path
        """
        global temp_result

        if self.index == 0:
            status, temp_result_str = self._api_helper.run_command(IPMI_SENSOR_TEMP_CMD)
            temp_result = temp_result_str.split('\n')

        for i in temp_result:
            if '|' not in i:
                continue
            sigle_list = i.split('|')
            if self._thermal_info["name"] == sigle_list[0].strip():
                self._thermal_info["temp"] = sigle_list[1].strip()
                break

    def __set_threshold(self, temperature):
        temp_file_path = self._thermal_info.get("max_temp", "N/A")
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
        self.__get_thermal_info()
        temperature = self._thermal_info.get("temp", "na")
        if temperature != "na":
            temperature = float(temperature)
        else:
            temperature = 0
        return float("{:.3f}".format(temperature))

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        high_threshold = thermal_temp_dict.get(self.name).get("max")
        if isinstance(high_threshold, dict):
            high_threshold = high_threshold.get(self._airflow)
        if high_threshold != NULL_VAL:
            high_threshold = float("{:.3f}".format(high_threshold))
        return high_threshold

    def get_low_threshold(self):
        """
        Retrieves the low threshold temperature of thermal
        Returns:
            A float number, the low threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        low_threshold = thermal_temp_dict.get(self.name).get("min")
        if low_threshold != NULL_VAL:
            low_threshold = float("{:.3f}".format(low_threshold))
        return low_threshold

    def set_high_threshold(self, temperature):
        """
        Sets the high threshold temperature of thermal
        Args :
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125
        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        temp_file = "temp1_max"
        is_set = self.__set_threshold(int(temperature) * 1000)
        file_set = False
        if is_set:
            try:
                with open(self.SS_CONFIG_PATH, 'r+') as f:
                    content = f.readlines()
                    f.seek(0)
                    ss_found = False
                    for idx, val in enumerate(content):
                        if self.name in val:
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

    @staticmethod
    def set_low_threshold(temperature):
        """
        Sets the low threshold temperature of thermal
        Args : 
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125
        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        # Not Support
        return False

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal
        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        high_critical_threshold = thermal_temp_dict.get(self.name).get("high_critical_threshold")
        if isinstance(high_critical_threshold, dict):
            high_critical_threshold = high_critical_threshold.get(str(self._airflow).upper())
        if high_critical_threshold != NULL_VAL:
            high_critical_threshold = float("{:.3f}".format(float(high_critical_threshold)))
        return high_critical_threshold

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold temperature of thermal
        Returns:
            A float number, the low critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        low_critical_threshold = thermal_temp_dict.get(self.name).get("low_critical_threshold")
        if low_critical_threshold != NULL_VAL:
            low_critical_threshold = float("{:.3f}".format(float(low_critical_threshold)))
        return low_critical_threshold

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        return self._thermal_info.get("name")

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        return os.path.isfile(self._thermal_info.get("temp", NULL_VAL))

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self._thermal_info.get("model", NULL_VAL)

    @staticmethod
    def get_serial():
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return NULL_VAL

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if not self.get_presence():
            return False
        return True
