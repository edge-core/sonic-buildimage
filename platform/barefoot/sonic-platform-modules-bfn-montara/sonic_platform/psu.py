#!/usr/bin/env python

try:
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))

    from .platform_thrift_client import ThriftClient

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
        try:
            with ThriftClient() as client:
                psu_info = client.pltfm_mgr.pltfm_mgr_pwr_supply_info_get(self.index)
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
        try:
            with ThriftClient() as client:
                status = client.pltfm_mgr.pltfm_mgr_pwr_supply_present_get(self.index)
        except Exception:
            return False

        return status
