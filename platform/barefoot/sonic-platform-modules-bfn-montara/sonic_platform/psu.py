#!/usr/bin/env python

try:
    import os
    import sys

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

        return thrift_try(psu_info_get)

    @staticmethod
    def get_num_psus():
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
        """
        return 2

    def get_powergood_status(self):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by 1-based self.index <self.index>
        :param self.index: An integer, 1-based self.index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is faulty
        """
        info = self.__info_get()
        return info.ffault == False and info.vout != 0

    def get_voltage(self):
        """
        Retrieves current PSU voltage output

        Returns:
            A float number, the output voltage in volts,
            e.g. 12.1
        """
        return float(self.__info_get().vout)

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU

        Returns:
            A float number, the electric current in amperes, e.g 15.4
        """
        return self.__info_get().iout / 1000.

    def get_power(self):
        """
        Retrieves current energy supplied by PSU

        Returns:
            A float number, the power in watts, e.g. 302.6
        """
        return self.__info_get().pwr_out / 1000.

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based self.index <self.index>
        :param self.index: An integer, 1-based self.index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        def psu_present_get(client):
            return client.pltfm_mgr.pltfm_mgr_pwr_supply_present_get(self.__index)

        status = thrift_try(psu_present_get)
        return status

    # DeviceBase iface:
    def get_serial(self):
        return self.__info_get().serial

    def get_model(self):
        return self.__info_get().model

    def is_replaceable(self):
        return True

def psu_list_get():
    psu_list = []
    for i in range(1, Psu.get_num_psus() + 1):
        psu = Psu(i)
        psu_list.append(psu)
    return psu_list
