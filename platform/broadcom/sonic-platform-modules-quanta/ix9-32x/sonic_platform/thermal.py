#!/usr/bin/env python

#############################################################################
# Quanta
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Thermal information
#
#############################################################################

import logging
import os

try:
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

HWMON_DIR = "/sys/class/hwmon/hwmon2/"

thermal_index_mapping = {
    1:40,
    2:41,
    3:42,
    4:50,
    5:51,
    6:52,
    7:73,
    8:74,
    9:75,
   10:76,
   11:77,
   12:78,
   13:79,
   14:80,
   15:81,
   16:82,
   17:83,
   18:84,
   19:85
}

class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    def __init__(self, thermal_index):
        self.index        = thermal_index
        self.temp_attr    = "temp{}_input".format(thermal_index_mapping[self.index])
        self.high_th_attr = "temp{}_ncrit".format(thermal_index_mapping[self.index])
        self.high_crit_th_attr = "temp{}_crit".format(thermal_index_mapping[self.index])
        self.name_attr    = "temp{}_label".format(thermal_index_mapping[self.index])


    def __get_attr_value(self, attr_path):

        retval = 'ERR'
        if (not os.path.isfile(attr_path)):
            return retval

        try:
            with open(attr_path, 'r') as fd:
                retval = fd.read()
        except Exception as error:
            logging.error("Unable to open " + attr_path + " file !")

        retval = retval.rstrip(' \t\n\r')
        return retval

    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        attr_path = HWMON_DIR + self.name_attr
        attr_rv = self.__get_attr_value(attr_path)

        if (attr_rv != 'ERR'):
            return attr_rv
        else:
            return None

    def get_presence(self):
        """
        Retrieves the presence of the device

        Returns:
            bool: True if device is present, False if not
        """
        attr_path = HWMON_DIR + self.name_attr
        attr_rv = self.__get_attr_value(attr_path)

        if (attr_rv != 'ERR'):
            return True
        else:
            return False

    def get_status(self):
        """
        Retrieves the operational status of the device

        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if (self.get_temperature() != None):
            return True
        else:
            return False

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        attr_path = HWMON_DIR + self.temp_attr
        attr_rv = self.__get_attr_value(attr_path)

        if (attr_rv != 'ERR'):
            return float(attr_rv) / 1000
        else:
            return None

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        attr_path = HWMON_DIR + self.high_th_attr
        attr_rv = self.__get_attr_value(attr_path)

        if (attr_rv != 'ERR'):
            return float(attr_rv) / 1000
        else:
            return None

    def get_high_critical_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        attr_path = HWMON_DIR + self.high_crit_th_attr
        attr_rv = self.__get_attr_value(attr_path)

        if (attr_rv != 'ERR'):
            return float(attr_rv) / 1000
        else:
            return None

