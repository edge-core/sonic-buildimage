from sonic_platform_base.sonic_thermal_control.thermal_action_base import ThermalPolicyActionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .helper import APIHelper
from .thermal import logger
import getpass
import time

class FanAction(ThermalPolicyActionBase):
    def get_fan_info(self, thermal_info_dict):
        from .thermal_infos import FanInfo
        fan_info_obj = None
        if FanInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[FanInfo.INFO_NAME], FanInfo):
            fan_info_obj = thermal_info_dict[FanInfo.INFO_NAME]
        else:
            logger.log_error("Failed to get fans information")
        return fan_info_obj

class ThermalAction(ThermalPolicyActionBase):
    def get_thermal_info(self, thermal_info_dict):
        from .thermal_infos import ThermalInfo
        thermal_info_obj = None
        if ThermalInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ThermalInfo.INFO_NAME], ThermalInfo):
            thermal_info_obj = thermal_info_dict[ThermalInfo.INFO_NAME]
        else:
            logger.log_error("Failed to get thermals information")
        return thermal_info_obj


class SetFanSpeedAction(FanAction):
    """
    Base thermal action class to set speed for fans
    """
    # JSON field definition
    JSON_FIELD_SPEED = 'speed'

    def __init__(self):
        """
        Constructor of SetFanSpeedAction which actually do nothing.
        """
        self.speed = None

    def load_from_json(self, json_obj):
        """
        Construct SetFanSpeedAction via JSON. JSON example:
            {
                "type": "fan.all.set_speed"
                "speed": "100"
            }
        :param json_obj: A JSON object representing a SetFanSpeedAction action.
        :return:
        """
        self.speed = 100
        if SetFanSpeedAction.JSON_FIELD_SPEED in json_obj:
            speed = float(json_obj[SetFanSpeedAction.JSON_FIELD_SPEED])
            if speed >= 0 and speed <= 100:
                self.speed = speed
            else:
                logger.log_error('{}: Invalid speed value {} in JSON policy file, value should be in range [0, 100]. ' \
                'Forcing speed to 100%.'.format(self.__class__.__name__, speed))
        else:
            logger.log_error('{}: Missing mandatory field `{}` in JSON policy file. Forcing speed to 100%.'.
                             format(self.__class__.__name__, SetFanSpeedAction.JSON_FIELD_SPEED))

@thermal_json_object('fan.all.set_speed')
class SetAllFanSpeedAction(SetFanSpeedAction):
    """
    Action to set speed for all fans
    """
    def execute(self, thermal_info_dict):
        """
        Set speed for all fans
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        if fan_info_obj:
            logger.log_notice("Set all Fan\'s speed to {}%".format(self.speed))
            for fan in fan_info_obj.get_presence_fans():
                fan.set_speed(self.speed)

@thermal_json_object('thermal_control.control')
class ControlThermalAlgoAction(ThermalPolicyActionBase):
    """
    Action to control the thermal control algorithm
    """
    # JSON field definition
    JSON_FIELD_STATUS = 'status'

    def __init__(self):
        self.status = True

    def load_from_json(self, json_obj):
        """
        Construct ControlThermalAlgoAction via JSON. JSON example:
            {
                "type": "thermal_control.control"
                "status": "true"
            }
        :param json_obj: A JSON object representing a ControlThermalAlgoAction action.
        :return:
        """
        self.status = False
        if ControlThermalAlgoAction.JSON_FIELD_STATUS in json_obj:
            status_str = json_obj[ControlThermalAlgoAction.JSON_FIELD_STATUS].lower()
            if status_str in ['true', 'false']:
                self.status = status_str
            else:
                logger.log_error('{}: Invalid `{}` field value ({}), value should be true or false. Forcing false.'.
                                 format(self.__class__.__name__, ControlThermalAlgoAction.JSON_FIELD_STATUS, status_str))
        else:
            logger.log_error('{}: Missing mandatory field `{}` in JSON policy file. Forcing false.'.
                             format(self.__class__.__name__, ControlThermalAlgoAction.JSON_FIELD_STATUS))

    def execute(self, thermal_info_dict):
        """
        Disable thermal control algorithm
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        from .thermal_infos import ChassisInfo
        chassis_info_obj = None
        if ChassisInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ChassisInfo.INFO_NAME], ChassisInfo):
            chassis_info_obj = thermal_info_dict[ChassisInfo.INFO_NAME]
            chassis = chassis_info_obj.get_chassis()
            thermal_manager = chassis.get_thermal_manager()
            if self.status:
                thermal_manager.start_thermal_control_algorithm()
            else:
                thermal_manager.stop_thermal_control_algorithm()

@thermal_json_object('thermal.warning.overheat')
class ThermalWarningAction(ThermalAction):
    """
    Action for handling thermal warning overheat.
    """

    def execute(self, thermal_info_dict):
        """
        Perform thermal warning logic.
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            temp_list = thermal_info_obj.get_temperatures()
            thermal_list = thermal_info_obj.get_thermal_list()
            sensor_idx_list = thermal_info_obj.get_warning_overheat_sensor_idx_list()
            for sensor_idx in sensor_idx_list:
                thermal = thermal_list[sensor_idx]
                logger.log_warning("Thermal warning overheat detected by '{}' sensor: temperature = {}, threshold = {}".
                                    format(thermal.get_name(), temp_list[sensor_idx],
                                        thermal.get_high_threshold()))

@thermal_json_object('thermal.critical.overheat')
class ThermalCriticalAction(ThermalAction):
    """
    Action for handling thermal critical overheat, also known as thermal shutdown logic.
    """
    def __init__(self):
        super().__init__()
        self.api_helper = APIHelper()

    def reboot_device(self):
        from .chassis import HOST_REBOOT_CAUSE_PATH, REBOOT_CAUSE_FILE

        reboot_user = getpass.getuser()
        reboot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        reboot_cause_path = (HOST_REBOOT_CAUSE_PATH + REBOOT_CAUSE_FILE)
        msg = "User issued 'Thermal Overload' command [User: {}, Time: {}]".format(reboot_user, reboot_time)
        sts = self.api_helper.write_txt_file(reboot_cause_path, msg)
        if not sts:
            logger.log_error("Failed to write reboot cause to the file: {}".format(reboot_cause_path))

        sts, res = self.api_helper.run_command("sync")
        if not (sts and res == ''):
            logger.log_error("Failed to run sync command")
        time.sleep(3)

        sts, res = self.api_helper.run_command("/opt/xplt/utils/pwcycle_box.sh")
        if not sts:
            logger.log_error("Failed to reboot device: {}".format(res))

    def execute(self, thermal_info_dict):
        """
        Perform thermal shutdown logic based on whether the sensor is a chassis or xcvr sensor.
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            temp_list = thermal_info_obj.get_temperatures()
            thermal_list = thermal_info_obj.get_thermal_list()
            sensor_idx_list = thermal_info_obj.get_critical_overheat_sensor_idx_list()
            for sensor_idx in sensor_idx_list:
                thermal = thermal_list[sensor_idx]
                logger.log_error("Thermal critical overheat detected by '{}' sensor: temperature = {}, threshold = {}".
                                    format(thermal.get_name(), temp_list[sensor_idx],
                                        thermal.get_high_critical_threshold()))
            logger.log_error("Thermal critical overheat detected. Rebooting the device.")
            self.reboot_device()

@thermal_json_object('update.cooling.level')
class ThermalCoolLevelUpdateAction(ThermalAction, FanAction):
    """
    Action to adjust fan speed according to the current system cooling level.
    """

    def __init__(self):
        from .thermal_device_data import DEVICE_DATA

        # Get the list of fan speeds, where each index corresponds to a specific
        # cooling level index.
        self.cool_lvl_map = DEVICE_DATA['fan_speed']

    def execute(self, thermal_info_dict):
        """
        Adjust the fan speed according to the current system cooling level.
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        if thermal_info_obj and fan_info_obj:
            cool_lvl_idx = thermal_info_obj.get_cooling_level_idx()
            if cool_lvl_idx in range(len(self.cool_lvl_map)):
                for fan in fan_info_obj.get_presence_fans():
                    fan.set_speed(self.cool_lvl_map[cool_lvl_idx])
            else:
                logger.log_error("Invalid cooling level index: {}".format(cool_lvl_idx))
