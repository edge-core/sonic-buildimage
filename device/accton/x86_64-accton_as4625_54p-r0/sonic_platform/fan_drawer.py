########################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Fan-Drawers' information available in the platform.
#
########################################################################

try:
    from sonic_platform_base.fan_drawer_base import FanDrawerBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FANS_PER_FANTRAY = 1

class FanDrawer(FanDrawerBase):
    """Platform-specific Fan class"""

    def __init__(self, fantray_index):
        FanDrawerBase.__init__(self)
        self.fantrayindex = fantray_index
        # FanTray is 0-based in platforms
        self.__initialize_fan()

    def __initialize_fan(self):
        from sonic_platform.fan import Fan

        for i in range(FANS_PER_FANTRAY):
            self._fan_list.append(Fan(self.fantrayindex, i))

    def get_name(self):
        """
        Retrieves the fan drawer name
        Returns:
            string: The name of the device
        """
        return "FanTray-{}".format(self.fantrayindex + 1)

    def get_presence(self):
        """
        Retrieves the presence of the device
        Returns:
            bool: True if device is present, False if not
        """
        return self._fan_list[0].get_presence()

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self._fan_list[0].get_model()

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return self._fan_list[0].get_serial()

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        from sonic_platform.fan import Fan

        for fan in self._fan_list:
            if not fan.get_status():
                return False

        return True

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of
        entPhysicalContainedIn is'0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device
            or -1 if cannot determine the position
        """
        return self.fantrayindex+1

    def get_status_led(self):
        """
        Gets the state of the fan status LED
        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        return {
            True: self.STATUS_LED_COLOR_GREEN,
            False: self.STATUS_LED_COLOR_AMBER
        }.get(self.get_status(), self.STATUS_LED_COLOR_AMBER)

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        return False #Not supported

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False
