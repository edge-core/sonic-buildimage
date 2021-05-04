#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Fan Drawer status which are available in the platform
#
#############################################################################

import os

try:
    from sonic_platform_base.fan_drawer_base import FanDrawerBase
    from sonic_platform_base.fan_base import FanBase
    from .led import FanLed, SharedLed
    from .utils import read_int_from_file
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


class MellanoxFanDrawer(FanDrawerBase):
    def __init__(self, index, fan_data):
        from .fan import FAN_PATH
        super(MellanoxFanDrawer, self).__init__()
        self._index = index + 1
        self._fan_data = fan_data
        self._presence_path = os.path.join(FAN_PATH, 'fan{}_status'.format(self._index))
        self._led = None

    def get_index(self):
        return self._index

    def get_led(self):
        return self._led

    def get_presence(self):
        if not self._fan_data['hot_swappable']:
            return True

        status = 0
        try:
            with open(self._presence_path, 'r') as presence_status:
                status = int(presence_status.read())
        except (ValueError, IOError) as e:
            status = 0

        return status == 1

    def get_direction(self):
        if not self._fan_data['support_fan_direction'] or not self.get_presence():
            return FanBase.FAN_DIRECTION_NOT_APPLICABLE
        
        try:
            from .fan import FAN_DIR, FAN_DIR_VALUE_INTAKE, FAN_DIR_VALUE_EXHAUST
            fan_dir = read_int_from_file(FAN_DIR.format(self._index), raise_exception=True)
            if fan_dir == FAN_DIR_VALUE_INTAKE:
                return FanBase.FAN_DIRECTION_INTAKE
            elif fan_dir == FAN_DIR_VALUE_EXHAUST:
                return FanBase.FAN_DIRECTION_EXHAUST
            else:
                raise RuntimeError("Got wrong value {} for fan direction {}".format(fan_dir, self._index))
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to read fan direction status to {}".format(repr(e)))

    def set_status_led(self, color):
        """
        Sets the state of the fan drawer status LED

        Args:
            color: A string representing the color with which to set the
                   fan drawer status LED

        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        return True

    def get_status_led(self):
        """
        Gets the state of the fan drawer LED

        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        return self._led.get_status()

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device
        Returns:
            integer: The 1-based relative physical position in parent device
        """
        return self._index

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return self._fan_data['hot_swappable']


class RealDrawer(MellanoxFanDrawer):
    def __init__(self, index, fan_data):
        super(RealDrawer, self).__init__(index, fan_data)
        self._name = 'drawer{}'.format(self._index)
        self._led = SharedLed(FanLed(self._index))

    def get_name(self):
        return self._name

    
class VirtualDrawer(MellanoxFanDrawer):
    def __init__(self, index, fan_data):
        super(VirtualDrawer, self).__init__(index, fan_data)
        self._led = SharedLed(FanLed(None))

    def get_name(self):
        return 'N/A'
