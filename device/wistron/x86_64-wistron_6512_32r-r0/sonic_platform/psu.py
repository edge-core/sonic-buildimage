#!/usr/bin/env python

#############################################################################
# psuutil.py
# Platform-specific PSU status interface for SONiC
#############################################################################

try:
    from sonic_platform_base.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PSU_NAME_LIST = ["PSU-1", "PSU-2"]

class Psu(PsuBase):
    """Platform-specific Psu class"""

    SYSFS_PSU_DIR = ["/sys/bus/i2c/devices/0-005a",
                     "/sys/bus/i2c/devices/0-0059"]

    def __init__(self, psu_index):
        self.index = psu_index
        PsuBase.__init__(self)


    def get_fan(self):
        """
        Retrieves object representing the fan module contained in this PSU
        Returns:
            An object dervied from FanBase representing the fan module
            contained in this PSU
        """
        # Hardware not supported
        return False

    def get_powergood_status(self):
        """
        Retrieves the powergood status of PSU
        Returns:
            A boolean, True if PSU has stablized its output voltages and passed all
            its internal self-tests, False if not.
        """
        return self.get_status()

    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED
        Args:
            color: A string representing the color with which to set the PSU status LED
                   Note: Only support green and off
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        # Hardware not supported
        return False

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
        attr_file ='present'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        status = 0
        try:
            with open(attr_path, 'r') as psu_prs:
                status = int(psu_prs.read())
        except IOError:
            return False

        return status == 1

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        attr_file = 'power_good'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        status = 0
        try:
            with open(attr_path, 'r') as power_status:
                status = int(power_status.read())
        except IOError:
            return False

        return status == 1

    def get_model(self):
        """
        Retrieves the model number/name of a power supply unit (PSU) defined
                by 1-based index <idx>
        :param idx: An integer, 1-based index of the PSU of which to query model number
        :return: String, denoting model number/name
        """
        attr_file ='model'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        model = ""
        try:
            with open(attr_path, 'r') as psu_model:
                model = psu_model.read()
        except IOError:
            return model

        return model

    def get_mfr_id(self):
        """
        Retrieves the manufacturing id of a power supply unit (PSU) defined
                by 1-based index <idx>
        :param idx: An integer, 1-based index of the PSU of which to query mfr id
        :return: String, denoting manufacturing id
        """
        attr_file ='vendor'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        vendor = ""
        try:
            with open(attr_path, 'r') as psu_vendor:
                vendor = psu_vendor.read()
        except IOError:
            return vendor

        return vendor

    def get_serial(self):
        """
        Retrieves the serial number of a power supply unit (PSU) defined
                by 1-based index <idx>
        :param idx: An integer, 1-based index of the PSU of which to query serial number
        :return: String, denoting serial number of the PSU unit
        """
        attr_file ='sn'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        sn = ""
        try:
            with open(attr_path, 'r') as psu_sn:
                sn = psu_sn.read()
        except IOError:
            return sn

        return sn

    def get_temperature(self):
        """
        Retrieves current temperature reading from PSU
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        attr_file ='temp1_input'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        temp = 0.0
        try:
            with open(attr_path, 'r') as psu_temp:
                temp = float(psu_temp.read()) / 1000
        except IOError:
            return temp

        return temp

    def get_temperature_high_threshold(self):
        """
        Retrieves the high threshold temperature of PSU
        Returns:
            A float number, the high threshold temperature of PSU in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return False #Not supported

    def get_voltage_high_threshold(self):
        """
        Retrieves the high threshold PSU voltage output
        Returns:
            A float number, the high threshold output voltage in volts,
            e.g. 12.1
        """
        return False #Not supported

    def get_voltage_low_threshold(self):
        """
        Retrieves the low threshold PSU voltage output
        Returns:
            A float number, the low threshold output voltage in volts,
            e.g. 12.1
        """
        return False #Not supported

    def get_voltage(self):
        """
        Retrieves current PSU voltage output
        Returns:
            A float number, the output voltage in volts,
            e.g. 12.1
        """
        attr_file ='in2_input'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        volt = 0.0
        try:
            with open(attr_path, 'r') as psu_volt:
                volt = float(psu_volt.read()) / 1000
        except IOError:
            return volt

        return volt

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU
        Returns:
            A float number, the electric current in amperes, e.g 15.4
        """
        attr_file ='curr2_input'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        curr = 0.0
        try:
            with open(attr_path, 'r') as psu_curr:
                curr = float(psu_curr.read()) / 1000
        except IOError:
            return curr

        return curr

    def get_power(self):
        """
        Retrieves current energy supplied by PSU
        Returns:
            A float number, the power in watts, e.g. 302.6
        """
        attr_file ='power2_input'
        attr_path = self.SYSFS_PSU_DIR[self.index-1] +'/' + attr_file
        power = 0.0
        try:
            with open(attr_path, 'r') as psu_power:
                power = float(psu_power.read()) / 1000000
        except IOError:
            return power

        return power
