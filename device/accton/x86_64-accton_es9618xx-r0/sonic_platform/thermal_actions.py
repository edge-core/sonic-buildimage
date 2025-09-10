from sonic_platform_base.sonic_thermal_control.thermal_action_base import ThermalPolicyActionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from sonic_platform import platform
from .helper import APIHelper
from .thermal import logger
import time
import os

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
        # See on top of thermal.py how to enable log_debug
        logger.log_debug('thermal_actions:SetAllFanSpeedAction: Set all Fan\'s speed to {}%'.format(self.speed))

        SetAllFanSpeedAction.set_psu_fan_speed(thermal_info_dict, self.speed)

    @classmethod
    def set_psu_fan_speed(cls, thermal_info_dict, speed):
        from .thermal_infos import ChassisInfo
        if ChassisInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ChassisInfo.INFO_NAME], ChassisInfo):
            chassis = thermal_info_dict[ChassisInfo.INFO_NAME].get_chassis()
            for psu in chassis.get_all_psus():
                for psu_fan in psu.get_all_fans():
                    psu_fan.set_speed(speed)
        

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
        from .thermal import Thermal
        status_changed = Thermal.set_thermal_algorithm_status(self.status, False)

        if status_changed:
            logger.log_info('Changed thermal algorithm status to {}'.format(self.status))


@thermal_json_object('switch.power_cycling')
class SwitchPolicyAction(ThermalPolicyActionBase):
    """
    Class for thermal action. Once all thermal conditions in a thermal policy are matched,
    all predefined thermal action will be executed.
    """

    def execute(self, thermal_info_dict):
        """
        Take action when thermal condition matches.
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        logger.log_notice("Thermal policy action: switch.power_cycling")

        # 1. Indicate thermal overheating by setting the diag LED to amber,
        #    It's done in the `led_control` plugin

        # 2. Stop the `SWSS` Docker container, followed by a reset of the X2 chip,
        #    It's done by the `es9618xx-platform-monitor` service
        SHUTDOWN_FILE = '/usr/share/sonic/firmware/pmon_system_shutdown'
        SHUTDOWN_OVERHEAT_CODE = "overheat"
        api_helper = APIHelper()
        api_helper.write_txt_file(SHUTDOWN_FILE, "{}".format(SHUTDOWN_OVERHEAT_CODE))
        # Wait up to 120 seconds for the `SHUTDOWN_FILE` file to be deleted, which
        # signals the completion of the above operation
        for index in range(120):
            time.sleep(1)
            if not os.path.exists(SHUTDOWN_FILE):
                break
        if os.path.exists(SHUTDOWN_FILE):
            logger.log_error("Timeout expired while waiting for the SWSS Docker container " \
            "to stop and the X2 chip to reset")

        # 3. Set all transceivers to LPM (Low Power Mode) mode
        sfps = platform.Platform().get_chassis().get_all_sfps()
        for sfp in sfps:
            if sfp.get_lpmode() == False:
                logger.log_notice("Set transceiver {} to LPM mode".format(sfp.get_name()))
                sfp.set_lpmode(True)


@thermal_json_object('update.cool.level')
class ChangeMinCoolingLevelAction(ThermalPolicyActionBase):
    from .thermal import Thermal
    previous_cooling_stage = -1
    thermal_policy_pause_countdown = 0
    MINIMAL_TEMPERATURE = -127
    MINIMAL_COOLING_LEVEL = 4
    THERMAL_X48 = 0
    THERMAL_X49 = 1
    THERMAL_X4A = 2
    THERMAL_ASIC = Thermal.ASIC_CALCULATED_TEMP_OFFSET
    WARNING_COOLING_STAGE = 1

    # JSON field definition
    JSON_FIELD_MIN_COOL_LEVEL = 'min_cool_level'

    def __init__(self):
        self.min_cool_level = ChangeMinCoolingLevelAction.MINIMAL_COOLING_LEVEL

    def load_from_json(self, json_obj):
        """
        :param json_obj: A JSON object representing a ChangeMinCoolingLevelAction action.
        :return:
        """
        if self.JSON_FIELD_MIN_COOL_LEVEL in json_obj:
            min_cool_level = int(json_obj[self.JSON_FIELD_MIN_COOL_LEVEL])
            if min_cool_level < 0 or min_cool_level > 10:
                raise ValueError('{} invalid min_cool_level value {} in JSON policy file, valid value should be [0, 10]'.
                                 format(type(self).__name__, min_cool_level))
            self.min_cool_level = min_cool_level
        else:
            raise ValueError('{} missing mandatory field {} in JSON policy file'.
                             format(type(self).__name__, self.JSON_FIELD_MIN_COOL_LEVEL))

    @staticmethod
    def set_previous_cooling_stage(stage):
        ChangeMinCoolingLevelAction.previous_cooling_stage = stage

    def process_sensor_data(self, temperature_table, sensor_index):
        temp_min = ChangeMinCoolingLevelAction.MINIMAL_TEMPERATURE
        for indx in range(0, len(temperature_table)):
            temp_range = temperature_table[indx].split(':')
            temp_threshold = float(temp_range[0].strip())
            temp_max = float(temp_range[1].strip())
            cool_lvl = float(temp_range[2].strip())
            logger.log_debug('threshold: {} to {}; hyst: {}'.format(temp_min, temp_max, temp_threshold))
            if temp_min <= float(self.temperatures[sensor_index]) <= temp_max:
                if self.cooling_stage < indx:
                    self.cooling_stage = indx
                break
            temp_min = temp_max
        if (temp_threshold > float(self.temperatures[sensor_index])):
            self.cooling_stage_decrease += 1
            logger.log_debug('cooling_stage {} cooling_stage_decrease {}'.format(self.cooling_stage, self.cooling_stage_decrease))

    def execute(self, thermal_info_dict):
        from sonic_platform import platform
        from .thermal_device_data import DEVICE_DATA
        from .thermal import Thermal
        from .fan import Fan
        from .thermal_conditions import MinCoolingLevelChangeCondition
        from .helper import APIHelper

        api_helper = APIHelper()
        thermal_x48 = DEVICE_DATA['thermal']['thresholds']['thermal_x48']
        thermal_x49 = DEVICE_DATA['thermal']['thresholds']['thermal_x49']
        thermal_x4A = DEVICE_DATA['thermal']['thresholds']['thermal_x4A']
        thermal_asic = DEVICE_DATA['thermal']['thresholds']['asic_average']
        # Add all transceivers thermal sensors and limits
        thermal_xcvr_list = []
        for i in range(0, len(Thermal.TRANSCEIVER_TEMP_LIST)):
            thermal_xcvr_list.append(["{}:{}:10".format(Thermal.TRANSCEIVER_TEMP_LIST[i][1] - 3, Thermal.TRANSCEIVER_TEMP_LIST[i][1] - 2),
                                      "{}:{}:10".format(Thermal.TRANSCEIVER_TEMP_LIST[i][1] - 2, Thermal.TRANSCEIVER_TEMP_LIST[i][1]),
                                      "{}:{}:10".format(Thermal.TRANSCEIVER_TEMP_LIST[i][2] - 2, Thermal.TRANSCEIVER_TEMP_LIST[i][2])])
            logger.log_debug("added transceiver {} temperatures: {}".format(i, thermal_xcvr_list[i]))

        self.temperatures = MinCoolingLevelChangeCondition.temperatures
        self.cooling_stage_decrease = 0
        self.cooling_stage = 0
        min_cooling_level = 5

        self.process_sensor_data(thermal_x48, ChangeMinCoolingLevelAction.THERMAL_X48)
        self.process_sensor_data(thermal_x49, ChangeMinCoolingLevelAction.THERMAL_X49)
        self.process_sensor_data(thermal_x4A, ChangeMinCoolingLevelAction.THERMAL_X4A)
        self.process_sensor_data(thermal_asic, ChangeMinCoolingLevelAction.THERMAL_ASIC)
        # Process all transceivers sensor
        for i in range(0, len(thermal_xcvr_list)):
            self.process_sensor_data(thermal_xcvr_list[i], Thermal.XCVR_TEMP_SENSORS_OFFSET + i)

        if (ChangeMinCoolingLevelAction.previous_cooling_stage <= self.cooling_stage):
            if 0 == self.cooling_stage:
                cool_lvl = self.min_cool_level
            else:
                temp_range = thermal_asic[self.cooling_stage].split(':')
                cool_lvl = int(temp_range[2].strip())
        min_cooling_level = cool_lvl
        logger.log_debug("ChangeMinCoolingLevelAction: prev.stage: {} current: {}".format(
            ChangeMinCoolingLevelAction.previous_cooling_stage, self.cooling_stage))

        if (ChangeMinCoolingLevelAction.previous_cooling_stage > self.cooling_stage):
            if (self.cooling_stage_decrease == len(thermal_asic) and 0 < ChangeMinCoolingLevelAction.previous_cooling_stage):
                self.cooling_stage = ChangeMinCoolingLevelAction.previous_cooling_stage - 1

        if ((ChangeMinCoolingLevelAction.previous_cooling_stage != ChangeMinCoolingLevelAction.WARNING_COOLING_STAGE) and
            (self.cooling_stage == ChangeMinCoolingLevelAction.WARNING_COOLING_STAGE)):
            logger.log_notice("ChangeMinCoolingLevelAction: Colling stage has changed from {} to {}".format(
                ChangeMinCoolingLevelAction.previous_cooling_stage, ChangeMinCoolingLevelAction.WARNING_COOLING_STAGE))

        ChangeMinCoolingLevelAction.set_previous_cooling_stage(self.cooling_stage)

        logger.log_debug("ChangeMinCoolingLevelAction: {}; Current level: {}; Next level: {} ".format(
            self.temperatures, Fan.get_cooling_level(), min_cooling_level))
        Fan.set_cooling_level(min_cooling_level, Fan.min_cooling_level)

