#
# Copyright (c) 2020-2021 NVIDIA CORPORATION & AFFILIATES.
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
import os
from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
from .thermal_actions import *
from .thermal_conditions import *
from .thermal_infos import *


class ThermalManager(ThermalManagerBase):
    @classmethod
    def initialize(cls):
        """
        Initialize thermal manager, including register thermal condition types and thermal action types
        and any other vendor specific initialization.
        :return:
        """
        cls._add_private_thermal_policy()

    @classmethod
    def start_thermal_control_algorithm(cls):
        """
        Start thermal control algorithm

        Returns:
            bool: True if set success, False if fail. 
        """
        from .thermal import Thermal
        Thermal.set_thermal_algorithm_status(True)

    @classmethod
    def stop_thermal_control_algorithm(cls):
        """
        Stop thermal control algorithm

        Returns:
            bool: True if set success, False if fail. 
        """
        from .thermal import Thermal
        Thermal.set_thermal_algorithm_status(False)

    @classmethod
    def _add_private_thermal_policy(cls):
        dynamic_min_speed_policy = ThermalPolicy()
        dynamic_min_speed_policy.conditions[MinCoolingLevelChangeCondition] = MinCoolingLevelChangeCondition()
        dynamic_min_speed_policy.actions[ChangeMinCoolingLevelAction] = ChangeMinCoolingLevelAction()
        cls._policy_dict['DynamicMinCoolingLevelPolicy'] = dynamic_min_speed_policy

        update_psu_fan_speed_policy = ThermalPolicy()
        update_psu_fan_speed_policy.conditions[CoolingLevelChangeCondition] = CoolingLevelChangeCondition()
        update_psu_fan_speed_policy.actions[UpdatePsuFanSpeedAction] = UpdatePsuFanSpeedAction()
        cls._policy_dict['UpdatePsuFanSpeedPolicy'] = update_psu_fan_speed_policy

        update_cooling_level_policy = ThermalPolicy()
        update_cooling_level_policy.conditions[UpdateCoolingLevelToMinCondition] = UpdateCoolingLevelToMinCondition()
        update_cooling_level_policy.actions[UpdateCoolingLevelToMinAction] = UpdateCoolingLevelToMinAction()
        cls._policy_dict['UpdateCoolingLevelPolicy'] = update_cooling_level_policy
