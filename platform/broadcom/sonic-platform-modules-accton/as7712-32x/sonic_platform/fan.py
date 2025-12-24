#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_fan import PddfFan
    from .helper import APIHelper
    import os.path
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

SPEED_TOLERANCE = 10
HOST_FAN_TOLERANCE_FILE = "/usr/share/sonic/device/{}/tolerance_flag"
PMON_FAN_TOLERANCE_FILE = "/usr/share/sonic/platform/tolerance_flag"

class Fan(PddfFan):
    """PDDF Platform-Specific Fan class"""

    def __init__(self, tray_idx, fan_idx=0, pddf_data=None, pddf_plugin_data=None, is_psu_fan=False, psu_index=0):
        # idx is 0-based 
        PddfFan.__init__(self, tray_idx, fan_idx, pddf_data, pddf_plugin_data, is_psu_fan, psu_index)

        self._api_helper = APIHelper()
        self.is_psu_fan = is_psu_fan
        self.is_host = self._api_helper.is_host()

        # tolerance path
        self.tolerance_flag = PMON_FAN_TOLERANCE_FILE
        if self.is_host:
            self.tolerance_flag = HOST_FAN_TOLERANCE_FILE.format(self._api_helper.get_platform())

    # Provide the functions/variables below for which implementation is to be overwritten e.g.
    def set_tolerance_mode(self, mode):
        """
        Set the fan tolerance mode using a flag file.
        Args:
            mode:
                - "off":  tolerance off      → create flag file
                - "on": tolerance activate   → delete flag file
        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        try:
            if mode == "off":
                open(self.tolerance_flag, "a").close()
            elif mode == "on":
                if os.path.exists(self.tolerance_flag):
                    os.remove(self.tolerance_flag)
            else:
                return False
            return True

        except OSError:
            return False

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        speed_tolerance = SPEED_TOLERANCE
        if self.is_psu_fan:
            return speed_tolerance

        if os.path.exists(self.tolerance_flag):
            raise NotImplementedError

        return speed_tolerance
