#
# Copyright (c) 2020-2022 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from sonic_platform_base.sonic_thermal_control.thermal_action_base import ThermalPolicyActionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .thermal import Thermal


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
        Thermal.set_expect_cooling_level(self.speed / 10)


@thermal_json_object('thermal.recover')
class ThermalRecoverAction(ThermalPolicyActionBase):
    UNKNOWN_SKU_COOLING_LEVEL = 6

    def execute(self, thermal_info_dict):
        from .device_data import DeviceDataManager
        from .thermal import MAX_COOLING_LEVEL, MIN_COOLING_LEVEL_FOR_HIGH, logger
        Thermal.monitor_asic_themal_zone()

        # Calculate dynamic minimum cooling level
        dynamic_min_cooling_level = None
        minimum_table = DeviceDataManager.get_minimum_table()
        if not minimum_table:
            # If there is no minimum_table defined, set dynamic_min_cooling_level to default value
            dynamic_min_cooling_level = ThermalRecoverAction.UNKNOWN_SKU_COOLING_LEVEL
        else:
            trust_state = Thermal.check_module_temperature_trustable()
            temperature = Thermal.get_min_amb_temperature()
            temperature = int(temperature / 1000)
            minimum_table = minimum_table['unk_{}'.format(trust_state)]

            for key, cooling_level in minimum_table.items():
                temp_range = key.split(':')
                temp_min = int(temp_range[0].strip())
                temp_max = int(temp_range[1].strip())
                if temp_min <= temperature <= temp_max:
                    dynamic_min_cooling_level = cooling_level - 10
                    break

        if not dynamic_min_cooling_level:
            # Should not go to this branch, just in case
            logger.log_error('Failed to get dynamic minimum cooling level')
            dynamic_min_cooling_level = MAX_COOLING_LEVEL

        if Thermal.last_set_cooling_level is not None and dynamic_min_cooling_level > Thermal.last_set_cooling_level and dynamic_min_cooling_level >= MIN_COOLING_LEVEL_FOR_HIGH:
            # No need to check thermal zone as dynamic_min_cooling_level is greater than previous value and MIN_COOLING_LEVEL_FOR_HIGH
            Thermal.set_expect_cooling_level(dynamic_min_cooling_level)
        else:
            min_cooling_level_by_tz = Thermal.get_min_allowed_cooling_level_by_thermal_zone()
            if min_cooling_level_by_tz is not None:
                cooling_level = max(dynamic_min_cooling_level, min_cooling_level_by_tz)
                Thermal.set_expect_cooling_level(cooling_level)
