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
    """
    Action to update the fan speed based on the system temperature
    """
    from .thermal import Thermal
    THERMAL_X48_IDX = 0
    THERMAL_X49_IDX = 1
    THERMAL_X4A_IDX = 2
    THERMAL_ASIC_IDX = Thermal.ASIC_CALCULATED_TEMP_OFFSET
    THERMAL_XCVR_OFFSET = Thermal.XCVR_TEMP_SENSORS_OFFSET
    THERMAL_DATA_IDX_FAN_SPEED = 2
    MINIMAL_COOLING_LEVEL = 4
    COOL_LEVEL_IDX_0 = 0
    COOL_LEVEL_IDX_1 = 1
    COOL_LEVEL_IDX_2 = 2
    COOL_LEVEL_IDX_3 = 3

    # JSON field definition
    JSON_FIELD_MIN_COOL_LEVEL = 'min_cool_level'

    class HysteresisMonitor:
        """
        A class per sensor to manage and update its hysteresis state

        Attributes:
            thresholds: This is a list containing three string elements, where each
                        element follows this format:
                        "low hysteresis threshold : high hysteresis threshold : fan cooling level"
                        For example:
                            thresholds = ["64:69:10", "70:75:10", "80:85:10"]
                            parameter                       value
                            ---------                       -----
                            low hysteresis threshold 1      64
                            high hysteresis threshold 1     69
                            fan cooling level 1             10
                            low hysteresis threshold 2      70
                            high hysteresis threshold 2     75
                            fan cooling level 2             10
                            low hysteresis threshold 3      80
                            high hysteresis threshold 3     85
                            fan cooling level 3             10
        """
        THERMAL_DATA_IDX_LOW_TH = 0
        THERMAL_DATA_IDX_HIGH_TH = 1

        def __init__(self, thresholds):
            self.thresholds = thresholds

            # Track the current hysteresis state of each instance (True = high hyst, False = low hyst)
            self.hyst_state_list = [False] * len(thresholds)

        def update(self, value):
            """Update the hysteresis state based on the new input temperature value

            Args:
                value: integer value of the input temperature used to update the hysteresis state

            Returns:
                An integer representing the cool level index used to determine the actual fan speed
            """
            cool_lvl_idx = 0
            for idx, thresholds in enumerate(self.thresholds):
                low = int(thresholds.split(':')[self.THERMAL_DATA_IDX_LOW_TH])
                high = int(thresholds.split(':')[self.THERMAL_DATA_IDX_HIGH_TH])

                # If the sensor is in the low state and the value crosses the high threshold
                if not self.hyst_state_list[idx] and value > high:
                    self.hyst_state_list[idx] = True
                # If the sensor is in the high state and the value crosses below or equals the low threshold
                elif self.hyst_state_list[idx] and value <= low:
                    self.hyst_state_list[idx] = False

                # Record the highest index crossed, which represents the cool level
                if self.hyst_state_list[idx]:
                    cool_lvl_idx = idx + 1

            return cool_lvl_idx

    def __init__(self):
        from .thermal import Thermal
        from .thermal_device_data import DEVICE_DATA

        self.min_cool_level = self.MINIMAL_COOLING_LEVEL
        self.last_cool_lvl_idx = self.COOL_LEVEL_IDX_0

        api_helper = APIHelper()
        thermal_thresh_list = []
        thermal_thresh_list.append(DEVICE_DATA['thermal']['thresholds']['thermal_x48'])
        thermal_thresh_list.append(DEVICE_DATA['thermal']['thresholds']['thermal_x49'])
        thermal_thresh_list.append(DEVICE_DATA['thermal']['thresholds']['thermal_x4A'])
        thermal_thresh_list.append(DEVICE_DATA['thermal']['thresholds']['asic_average'])

        # Add transceiver thermal thresholds
        self.xcvrs_temp_list = Thermal.TRANSCEIVER_TEMP_LIST
        for idx in range(0, len(self.xcvrs_temp_list)):
            lst = ["{}:{}:10".format(self.xcvrs_temp_list[idx][1] - 3, self.xcvrs_temp_list[idx][1] - 2),
                   "{}:{}:10".format(self.xcvrs_temp_list[idx][1] - 2, self.xcvrs_temp_list[idx][1]),
                   "{}:{}:10".format(self.xcvrs_temp_list[idx][2] - 2, self.xcvrs_temp_list[idx][2])]
            thermal_thresh_list.append(lst)
            logger.log_debug("{}: Added transceiver {} temperatures: {}".format(self.__class__.__name__, idx, lst))

        self.hyst_monitor_list = []
        for idx in range(0, len(thermal_thresh_list)):
            self.hyst_monitor_list.append(self.HysteresisMonitor(thermal_thresh_list[idx]))

        # Create a mapping based solely on the `asic_average` sensor that maps
        # each `fan cooling level index` to its corresponding `fan cooling level`,
        # which represents the actual fan speed value.
        # Note: The `fan cooling level` retrieved from the `DEVICE_DATA` dictionary
        # represents the fan speed divided by 10. For example, a fan cooling level
        # of 3 corresponds to a fan speed of 30%.
        asic_temp_data = DEVICE_DATA['thermal']['thresholds']['asic_average']
        self.cool_lvl_map = []
        self.cool_lvl_map.append(self.min_cool_level)
        self.cool_lvl_map.append(int(asic_temp_data[0].split(':')[self.THERMAL_DATA_IDX_FAN_SPEED]))
        self.cool_lvl_map.append(int(asic_temp_data[1].split(':')[self.THERMAL_DATA_IDX_FAN_SPEED]))
        self.cool_lvl_map.append(int(asic_temp_data[2].split(':')[self.THERMAL_DATA_IDX_FAN_SPEED]))

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

    def execute(self, thermal_info_dict):
        """
        Check the hysteresis state of the specified temperature sensors and set
        the fan speed accordingly.
        :param thermal_info_dict: A dictionary stores all thermal information.
        :return:
        """
        from .fan import Fan
        from .thermal_conditions import MinCoolingLevelChangeCondition

        self.temperatures = MinCoolingLevelChangeCondition.temperatures

        # The indices of `thermal_samp_list` should match those of `thermal_thresh_list`
        # as used in the `__init__` function
        thermal_samp_list = []
        thermal_samp_list.append(float(self.temperatures[self.THERMAL_X48_IDX]))
        thermal_samp_list.append(float(self.temperatures[self.THERMAL_X49_IDX]))
        thermal_samp_list.append(float(self.temperatures[self.THERMAL_X4A_IDX]))
        thermal_samp_list.append(float(self.temperatures[self.THERMAL_ASIC_IDX]))

        # Collect samples from transceiver thermal sensors
        for idx in range(0, len(self.xcvrs_temp_list)):
            thermal_samp_list.append(float(self.temperatures[self.THERMAL_XCVR_OFFSET + idx]))

        # Determine the maximum cool level index from all sensors
        try:
            cool_lvl_idx = self.COOL_LEVEL_IDX_0
            for idx in range(0, len(thermal_samp_list)):
                cool_lvl_idx = max(cool_lvl_idx, self.hyst_monitor_list[idx].update(thermal_samp_list[idx]))
        except:
            cool_lvl_idx = self.COOL_LEVEL_IDX_1
            logger.log_error("{}: Failure occurred while calculating the cool level index, " \
            "forced cool level index to {}".format(self.__class__.__name__, cool_lvl_idx))

        if cool_lvl_idx != self.last_cool_lvl_idx:
            logger.log_notice("{}: The cool level index has changed from {} to {}".format(
                self.__class__.__name__, self.last_cool_lvl_idx, cool_lvl_idx))

        if self.last_cool_lvl_idx < self.COOL_LEVEL_IDX_2 and cool_lvl_idx == self.COOL_LEVEL_IDX_2:
            logger.log_notice("{}: Thermal warning detected".format(self.__class__.__name__))

        if self.last_cool_lvl_idx > self.COOL_LEVEL_IDX_1 and cool_lvl_idx == self.COOL_LEVEL_IDX_1:
            logger.log_notice("{}: Thermal warning cleared".format(self.__class__.__name__))

        self.last_cool_lvl_idx = cool_lvl_idx
        cool_lvl = self.cool_lvl_map[cool_lvl_idx]

        logger.log_debug("{}: Temperatures: {}; Current level: {}; Next level: {}".format(
            self.__class__.__name__, self.temperatures, Fan.get_cooling_level(), cool_lvl))

        Fan.set_cooling_level(cool_lvl, Fan.min_cooling_level)

