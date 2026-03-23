from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
from .helper import APIHelper
from sonic_platform.thermal import logger
from .thermal_actions import *
from .thermal_conditions import *
from .thermal_infos import *

CPLD_I2C_PATH = "/sys/bus/i2c/devices/10-0066/fan"
FAN_LED_MODE = CPLD_I2C_PATH + "_led_mode"

TC_INTERVAL_SEC = 30
WD_TIMEOUT = TC_INTERVAL_SEC * 2

class ThermalManager(ThermalManagerBase):

    # Override default thermal control interval
    _interval = TC_INTERVAL_SEC

    @classmethod
    def initialize(cls):
        """
        Initialize thermal manager, including register thermal condition types and thermal action types
        and any other vendor specific initialization.
        :return:
        """
        cls._api_helper = APIHelper()

        # Prevent the "Policy {} already exists" exception when reloading the JSON configuration
        # file via thermalctld's call to `load` in `thermal_manager.py`` by deleting all existing policies.
        # This was done to reload all thermal control configurations during instantiation
        # of `ThermalControlDaemon` in each thermal control test run.
        cls._policy_dict = {}

        cls._api_helper.write_txt_file(FAN_LED_MODE, 0) # Disable LED debug mode

    @classmethod
    def init_thermal_algorithm(cls, chassis):
        """
        Initialize thermal algorithm according to policy file.
        :param chassis: The chassis object.
        :return:
        """
        cls._chassis = chassis

        # Enable fan watchdog and set its initial timeout to twice the thermal control interval
        cls.fan_watchdog = chassis.get_fan_watchdog()
        if cls.fan_watchdog:
            cls.fan_watchdog.arm(WD_TIMEOUT)
        else:
            logger.log_error("Failed to get fan watchdog")

        # Align 'sensors' command thresholds with thermal control thresholds
        from .thermal_device_data import DEVICE_DATA
        from sonic_platform import thermal_infos
        LOW_TH_IDX = 0
        HIGH_TH_IDX = 1
        for idx in thermal_infos.ThermalInfo.PCB_SENSOR_IDX_LIST:
            thermal = chassis.get_thermal(idx)
            threshs_list = DEVICE_DATA['thresholds'][idx]
            thresh_list = threshs_list[len(threshs_list) - 2].split(':')
            low_thresh = int(thresh_list[LOW_TH_IDX]) * 1000
            high_thresh = int(thresh_list[HIGH_TH_IDX]) * 1000
            cls._api_helper.write_txt_file(thermal.hwmon_path + "temp1_max", high_thresh)
            cls._api_helper.write_txt_file(thermal.hwmon_path + "temp1_max_hyst", low_thresh)

        # Call the base implementation
        super().init_thermal_algorithm(chassis)

    @classmethod
    def run_policy(cls, chassis):
        """
        Collect thermal information, run each policy, if one policy matches, execute the policy's action.
        :param chassis: The chassis object.
        :return:
        """
        if cls.fan_watchdog:
            cls.fan_watchdog.arm(WD_TIMEOUT)

        # Call the base implementation
        super().run_policy(chassis)

    @classmethod
    def deinitialize(cls):
        """
        Destroy thermal manager, including any vendor specific cleanup. The default behavior of this function
        is a no-op.
        :return:
        """
        if cls._chassis:
            for fan in cls._chassis.get_all_fans():
                fan.set_speed(100)

        if cls.fan_watchdog:
            cls.fan_watchdog.disarm()

        cls._api_helper.write_txt_file(FAN_LED_MODE, 1) # Enable LED debug mode
