#!/usr/bin/env python

try:
    import os
    import sys
    import time

    sys.path.append(os.path.dirname(__file__))

    from .platform_thrift_client import thrift_try

    from sonic_platform_base.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class Psu(PsuBase):
    """Platform-specific PSU class"""

    def __init__(self, index):
        PsuBase.__init__(self)
        self.__index = index
        self.__info = None
        self.__ts = 0
        # STUB IMPLEMENTATION
        self.color = ""

    '''
    Units of returned info object values:
        vin - V
        iout - mA
        vout - V
        pwr_out - mW
        fspeed - RPM
    '''
    def __info_get(self):
        def psu_info_get(client):
            return client.pltfm_mgr.pltfm_mgr_pwr_supply_info_get(self.__index)

        # Update cache once per 2 seconds
        if self.__ts + 2 < time.time():
            self.__info = None
            try:
                self.__info = thrift_try(psu_info_get, attempts=1)
            finally:
                self.__ts = time.time()
                return self.__info
        return self.__info


    @staticmethod
    def get_num_psus():
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
        """
        return 2

    def get_name(self):
        return f"psu-{self.__index}"

    def get_powergood_status(self):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by 1-based self.index <self.index>
        :param self.index: An integer, 1-based self.index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is faulty
        """
        info = self.__info_get()
        if info is None:
            return False
        return info.ffault == False and info.vout != 0

    def get_voltage(self):
        """
        Retrieves current PSU voltage output

        Returns:
            A float number, the output voltage in volts,
            e.g. 12.1
        """
        info = self.__info_get()
        return float(info.vout) if info else 0

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU

        Returns:
            A float number, the electric current in amperes, e.g 15.4
        """
        info = self.__info_get()
        return info.iout / 1000 if info else 0

    def get_power(self):
        """
        Retrieves current energy supplied by PSU

        Returns:
            A float number, the power in watts, e.g. 302.6
        """
        info = self.__info_get()
        return info.pwr_out / 1000 if info else 0

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based self.index <self.index>
        :param self.index: An integer, 1-based self.index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        def psu_present_get(client):
            return client.pltfm_mgr.pltfm_mgr_pwr_supply_present_get(self.__index)

        status = False
        try:
            status = thrift_try(psu_present_get)
        finally:
            return status

    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED

        Args:
            color: A string representing the color with which to set the
                   PSU status LED

        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        # STUB IMPLEMENTATION
        self.color = color
        return True

    def get_status_led(self):
        """
        Gets the state of the PSU status LED

        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        # STUB IMPLEMENTATION
        return self.color

    # DeviceBase iface:
    def get_serial(self):
        """
        Retrieves the serial number of the device

        Returns:
            string: Serial number of device
        """
        info = self.__info_get()
        return info.serial if info else "N/A"

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device

        Returns:
            string: Model/part number of device
        """
        info = self.__info_get()
        return info.model if info else "N/A"

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return True

    def get_revision(self):
        """
        Retrieves the hardware revision of the device

        Returns:
            string: Revision value of device
        """
        info = self.__info_get()
        return info.rev if info else "N/A"

    def get_status(self):
        """
        Retrieves the operational status of the device

        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_powergood_status()

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device. If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of entPhysicalContainedIn is '0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device or -1 if cannot determine the position
        """
        return self.__index

def psu_list_get():
    psu_list = []
    for i in range(1, Psu.get_num_psus() + 1):
        psu = Psu(i)
        psu_list.append(psu)
    return psu_list
