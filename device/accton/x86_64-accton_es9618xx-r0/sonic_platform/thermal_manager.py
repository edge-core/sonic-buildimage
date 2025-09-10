import os
from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
from .thermal_actions import *
from .thermal_conditions import *
from .thermal_infos import *
from .helper import APIHelper

CPLD_I2C_PATH = "/sys/bus/i2c/devices/10-0066/fan"
FAN_LED_MODE = CPLD_I2C_PATH + "_led_mode"

class ThermalManager(ThermalManagerBase):
    @classmethod
    def initialize(cls):
        """
        Initialize thermal manager, including register thermal condition types and thermal action types
        and any other vendor specific initialization.
        :return:
        """
        _api_helper = APIHelper()
        _api_helper.write_txt_file(FAN_LED_MODE, 0) # Disable LED debug mode

    @classmethod
    def deinitialize(cls):
        """
        Destroy thermal manager, including any vendor specific cleanup. The default behavior of this function
        is a no-op.
        :return:
        """
        cls.start_thermal_control_algorithm()
        _api_helper = APIHelper()
        _api_helper.write_txt_file(FAN_LED_MODE, 1) # Enable LED debug mode

    @classmethod
    def start_thermal_control_algorithm(cls):
        """
        Start thermal control algorithm

        Returns:
            bool: True if start succeeded. False - if failed. 
        """
        from .thermal import Thermal
        return Thermal.set_thermal_algorithm_status(True)

    @classmethod
    def stop_thermal_control_algorithm(cls):
        """
        Stop thermal control algorithm

        Returns:
            bool: True if start succeeded. False - if failed.
        """
        from .thermal import Thermal
        return Thermal.set_thermal_algorithm_status(False)
