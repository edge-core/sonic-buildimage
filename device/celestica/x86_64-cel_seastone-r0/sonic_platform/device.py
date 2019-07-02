#!/usr/bin/env python

#############################################################################
# Celestica
#
# Device contains an implementation of SONiC Platform Base API and
# provides the device information
#
#############################################################################

try:
    from sonic_platform_base.device_base import DeviceBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Device(DeviceBase):
    """Platform-specific Device class"""

    COMPONENTS_NAME = ["CPLD1", "CPLD2", "CPLD3", "CPLD4", "BIOS"]

    def __init__(self, device_type, index=None):
        self.device_type = device_type
        self.index = index
        DeviceBase.__init__(self)

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        device_name = {
            "component": self.COMPONENTS_NAME[self.index]
        }.get(self.device_type, None)
        return device_name

    def get_name_list(self):
        """
        Retrieves list of the device name that available in this device type
            Returns:
            string: The list of device name
        """
        name_list = {
            "component": self.COMPONENTS_NAME
        }.get(self.device_type, None)
        return name_list
