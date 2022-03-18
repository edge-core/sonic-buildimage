#############################################################################
# PDDF
#
# PDDF fan_drawer base class inherited from the common base class fan_drawer.py
#
#############################################################################

try:
    from sonic_platform_base.fan_drawer_base import FanDrawerBase
    from sonic_platform.fan import Fan
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class PddfFanDrawer(FanDrawerBase):
    """PDDF generic Fan Drawer class"""

    pddf_obj = {}
    plugin_data = {}

    def __init__(self, tray_idx, pddf_data=None, pddf_plugin_data=None):
        FanDrawerBase.__init__(self)
        if not pddf_data or not pddf_plugin_data:
            raise ValueError('PDDF JSON data error')

        self.pddf_obj = pddf_data
        self.plugin_data = pddf_plugin_data
        self.platform = self.pddf_obj.get_platform()

        if tray_idx < 0 or tray_idx >= self.platform['num_fantrays']:
            print("Invalid fantray index %d\n" % tray_idx)
            return

        self.fantray_index = tray_idx+1
        for j in range(self.platform['num_fans_pertray']):
            # Fan index is 0-based for the init call
            self._fan_list.append(Fan(tray_idx, j, self.pddf_obj, self.plugin_data))

    def get_name(self):
        """
        Retrieves the fan drawer name
        Returns: String containing fan-drawer name
        """
        return "Fantray{0}".format(self.fantray_index)

    def get_presence(self):
        status = False
	# Usually if a tray is removed, all the fans inside it are absent
        if self._fan_list:
            status = self._fan_list[0].get_presence()

        return status

    def get_status(self):
        status = False
        # if all the fans are working fine, then tray status should be okay
        if self._fan_list:
            status = all(fan.get_status() == True for fan in self._fan_list)

        return status

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        # Usually Fantrays are replaceable
        return True

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        Returns:
            integer: The 1-based relative physical position in parent
            device or -1 if cannot determine the position
        """
        return self.fantray_index

    def get_status_led(self):
        led_device_name = "FANTRAY{}".format(self.fantray_index) + "_LED"

        if led_device_name not in self.pddf_obj.data.keys():
            # Implement a generic status_led color scheme
            if self.get_status():
                return self.STATUS_LED_COLOR_GREEN
            else:
                return self.STATUS_LED_COLOR_OFF

        device_name = self.pddf_obj.data[led_device_name]['dev_info']['device_name']
        self.pddf_obj.create_attr('device_name', device_name,  self.pddf_obj.get_led_path())
        self.pddf_obj.create_attr('index', str(self.fantray_index-1), self.pddf_obj.get_led_path())
        self.pddf_obj.create_attr('dev_ops', 'get_status',  self.pddf_obj.get_led_path())
        color = self.pddf_obj.get_led_color()
        return (color)

    def set_status_led(self, color):
        result = False
        led_device_name = "FANTRAY{}".format(self.fantray_index) + "_LED"
        result, msg = self.pddf_obj.is_supported_sysled_state(led_device_name, color)
        if result == False:
            print(msg)
            return (False)

        device_name = self.pddf_obj.data[led_device_name]['dev_info']['device_name']
        self.pddf_obj.create_attr('device_name', device_name,  self.pddf_obj.get_led_path())
        self.pddf_obj.create_attr('index', str(self.fantray_index-1), self.pddf_obj.get_led_path())
        self.pddf_obj.create_attr('color', color, self.pddf_obj.get_led_cur_state_path())
        self.pddf_obj.create_attr('dev_ops', 'set_status',  self.pddf_obj.get_led_path())
        return (True)
