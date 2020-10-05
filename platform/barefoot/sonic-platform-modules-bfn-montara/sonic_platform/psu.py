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
        self.index = index

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
        def psu_info_get(client):
            return client.pltfm_mgr.pltfm_mgr_pwr_supply_info_get(self.index)

        try:
            psu_info = thrift_try(psu_info_get)
        except Exception:
            return False

        return (psu_info.ffault == False)

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based self.index <self.index>
        :param self.index: An integer, 1-based self.index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        def psu_present_get(client):
            return client.pltfm_mgr.pltfm_mgr_pwr_supply_present_get(self.index)

        try:
            status = thrift_try(psu_present_get)
        except Exception:
            return False

        return status
