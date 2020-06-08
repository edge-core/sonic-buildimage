from sonic_platform_base.sonic_thermal_control.thermal_action_base import ThermalPolicyActionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .thermal import logger


class SetFanSpeedAction(ThermalPolicyActionBase):
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
        if SetFanSpeedAction.JSON_FIELD_SPEED in json_obj:
            speed = float(json_obj[SetFanSpeedAction.JSON_FIELD_SPEED])
            if speed < 0 or speed > 100:
                raise ValueError('SetFanSpeedAction invalid speed value {} in JSON policy file, valid value should be [0, 100]'.
                                 format(speed))
            self.speed = float(json_obj[SetFanSpeedAction.JSON_FIELD_SPEED])
        else:
            raise ValueError('SetFanSpeedAction missing mandatory field {} in JSON policy file'.
                             format(SetFanSpeedAction.JSON_FIELD_SPEED))


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
        from .thermal_infos import FanInfo
        if FanInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[FanInfo.INFO_NAME], FanInfo):
            fan_info_obj = thermal_info_dict[FanInfo.INFO_NAME]
            for fan in fan_info_obj.get_presence_fans():
                fan.set_speed(self.speed)
        logger.log_info('Set all system FAN speed to {}'.format(self.speed))

        SetAllFanSpeedAction.set_psu_fan_speed(thermal_info_dict, self.speed)

    @classmethod
    def set_psu_fan_speed(cls, thermal_info_dict, speed):
        from .thermal_infos import ChassisInfo
        if ChassisInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ChassisInfo.INFO_NAME], ChassisInfo):
            chassis = thermal_info_dict[ChassisInfo.INFO_NAME].get_chassis()
            for psu in chassis.get_all_psus():
                for psu_fan in psu.get_all_fans():
                    psu_fan.set_speed(speed)


@thermal_json_object('fan.all.check_and_set_speed')
class CheckAndSetAllFanSpeedAction(SetAllFanSpeedAction):
    """
    Action to check thermal zone temperature and recover speed for all fans
    """
    def execute(self, thermal_info_dict):
        """
        Check thermal zone and set speed for all fans
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        from .thermal import Thermal
        if Thermal.check_thermal_zone_temperature():
            SetAllFanSpeedAction.execute(self, thermal_info_dict)
        

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
        if ControlThermalAlgoAction.JSON_FIELD_STATUS in json_obj:
            status_str = json_obj[ControlThermalAlgoAction.JSON_FIELD_STATUS].lower()
            if status_str == 'true':
                self.status = True
            elif status_str == 'false':
                self.status = False
            else:
                raise ValueError('Invalid {} field value, please specify true of false'.
                                 format(ControlThermalAlgoAction.JSON_FIELD_STATUS))
        else:
            raise ValueError('ControlThermalAlgoAction '
                             'missing mandatory field {} in JSON policy file'.
                             format(ControlThermalAlgoAction.JSON_FIELD_STATUS))

    def execute(self, thermal_info_dict):
        """
        Disable thermal control algorithm
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        from .thermal_infos import FanInfo
        from .thermal import Thermal
        from .thermal_conditions import UpdateCoolingLevelToMinCondition
        from .fan import Fan
        status_changed = Thermal.set_thermal_algorithm_status(self.status, False)

        # Only update cooling level if thermal algorithm status changed
        if status_changed:
            if self.status:
                # Check thermal zone temperature, if all thermal zone temperature
                # back to normal, set it to minimum allowed speed to
                # save power
                UpdateCoolingLevelToMinAction.update_cooling_level_to_minimum(thermal_info_dict)

            logger.log_info('Changed thermal algorithm status to {}'.format(self.status))


@thermal_json_object('thermal.recover')
class ThermalRecoverAction(ThermalPolicyActionBase):
    def execute(self, thermal_info_dict):
         UpdateCoolingLevelToMinAction.update_cooling_level_to_minimum(thermal_info_dict)


class ChangeMinCoolingLevelAction(ThermalPolicyActionBase):
    UNKNOWN_SKU_COOLING_LEVEL = 6
    def execute(self, thermal_info_dict):
        from .device_data import DEVICE_DATA
        from .fan import Fan
        from .thermal_infos import ChassisInfo
        from .thermal_conditions import MinCoolingLevelChangeCondition
        from .thermal_conditions import UpdateCoolingLevelToMinCondition

        chassis = thermal_info_dict[ChassisInfo.INFO_NAME].get_chassis()
        if chassis.platform_name not in DEVICE_DATA or 'thermal' not in DEVICE_DATA[chassis.platform_name] or 'minimum_table' not in DEVICE_DATA[chassis.platform_name]['thermal']:
            Fan.min_cooling_level = ChangeMinCoolingLevelAction.UNKNOWN_SKU_COOLING_LEVEL
        else:
            trust_state = MinCoolingLevelChangeCondition.trust_state
            temperature = MinCoolingLevelChangeCondition.temperature
            minimum_table = DEVICE_DATA[chassis.platform_name]['thermal']['minimum_table']['unk_{}'.format(trust_state)]

            for key, cooling_level in minimum_table.items():
                temp_range = key.split(':')
                temp_min = int(temp_range[0].strip())
                temp_max = int(temp_range[1].strip())
                if temp_min <= temperature <= temp_max:
                    Fan.min_cooling_level = cooling_level - 10
                    break
        
        current_cooling_level = Fan.get_cooling_level()
        if current_cooling_level < Fan.min_cooling_level:
            Fan.set_cooling_level(Fan.min_cooling_level, Fan.min_cooling_level)
            SetAllFanSpeedAction.set_psu_fan_speed(thermal_info_dict, Fan.min_cooling_level * 10)
        else:
            Fan.set_cooling_level(Fan.min_cooling_level, current_cooling_level)
            UpdateCoolingLevelToMinAction.update_cooling_level_to_minimum(thermal_info_dict)


class UpdatePsuFanSpeedAction(ThermalPolicyActionBase):
    def execute(self, thermal_info_dict):
        from .thermal_conditions import CoolingLevelChangeCondition
        SetAllFanSpeedAction.set_psu_fan_speed(thermal_info_dict, CoolingLevelChangeCondition.cooling_level * 10)


class UpdateCoolingLevelToMinAction(ThermalPolicyActionBase):
    def execute(self, thermal_info_dict):
        self.update_cooling_level_to_minimum(thermal_info_dict)

    @classmethod
    def update_cooling_level_to_minimum(cls, thermal_info_dict):
        from .fan import Fan
        from .thermal import Thermal
        from .thermal_conditions import UpdateCoolingLevelToMinCondition
        from .thermal_infos import FanInfo
        if Thermal.check_thermal_zone_temperature():
            fan_info_obj = thermal_info_dict[FanInfo.INFO_NAME]
            speed = Fan.min_cooling_level * 10
            for fan in fan_info_obj.get_presence_fans():
                fan.set_speed(speed)
            SetAllFanSpeedAction.set_psu_fan_speed(thermal_info_dict, speed)
            UpdateCoolingLevelToMinCondition.enable = False
        else:
            UpdateCoolingLevelToMinCondition.enable = True

