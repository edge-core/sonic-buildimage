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
from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
from .thermal_actions import *
from .thermal_conditions import *
from .thermal_infos import *
from .thermal import logger, MAX_COOLING_LEVEL, Thermal


class ThermalManager(ThermalManagerBase):
    @classmethod
    def start_thermal_control_algorithm(cls):
        """
        Start thermal control algorithm

        Returns:
            bool: True if set success, False if fail.
        """
        Thermal.set_thermal_algorithm_status(True)

    @classmethod
    def stop_thermal_control_algorithm(cls):
        """
        Stop thermal control algorithm

        Returns:
            bool: True if set success, False if fail.
        """
        Thermal.set_thermal_algorithm_status(False)

    @classmethod
    def run_policy(cls, chassis):
        if not cls._policy_dict:
            return

        try:
            cls._collect_thermal_information(chassis)
        except Exception as e:
            logger.log_error('Failed to collect thermal information {}'.format(repr(e)))
            Thermal.set_expect_cooling_level(MAX_COOLING_LEVEL)
            Thermal.commit_cooling_level(cls._thermal_info_dict)
            return

        for policy in cls._policy_dict.values():
            if not cls._running:
                return
            try:
                print(policy.name)
                if policy.is_match(cls._thermal_info_dict):
                    policy.do_action(cls._thermal_info_dict)
            except Exception as e:
                logger.log_error('Failed to run thermal policy {} - {}'.format(policy.name, repr(e)))
                # In case there is an exception, we put cooling level to max value
                Thermal.set_expect_cooling_level(MAX_COOLING_LEVEL)

        Thermal.commit_cooling_level(cls._thermal_info_dict)
