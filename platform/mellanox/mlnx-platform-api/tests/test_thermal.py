#
# Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES.
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

import glob
import os
import sys
if sys.version_info.major == 3:
    from unittest import mock
else:
    import mock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.chassis import Chassis
from sonic_platform.device_data import DeviceDataManager


class TestThermal:
    def test_chassis_thermal(self):
        from sonic_platform.thermal import THERMAL_NAMING_RULE
        os.path.exists = mock.MagicMock(return_value=True)
        DeviceDataManager.get_gearbox_count = mock.MagicMock(return_value=2)
        DeviceDataManager.get_cpu_thermal_count = mock.MagicMock(return_value=2)
        DeviceDataManager.get_platform_name = mock.MagicMock(return_value='x86_64-mlnx_msn2700-r0')
        chassis = Chassis()
        thermal_list = chassis.get_all_thermals()
        assert thermal_list
        thermal_dict = {thermal.get_name(): thermal for thermal in thermal_list}
        gearbox_thermal_rule = None
        cpu_thermal_rule = None
        for rule in THERMAL_NAMING_RULE['chassis thermals']:
            thermal_type = rule.get('type', 'single')
            if thermal_type == 'single':
                thermal_name = rule['name']
                if rule['temperature'] == 'comex_amb':
                    assert thermal_name not in thermal_dict
                    continue
                assert thermal_name in thermal_dict
                thermal = thermal_dict[thermal_name]
                assert rule['temperature'] in thermal.temperature
                assert rule['high_threshold'] in thermal.high_threshold if 'high_threshold' in rule else thermal.high_threshold is None
                assert rule['high_critical_threshold'] in thermal.high_critical_threshold if 'high_critical_threshold' in rule else thermal.high_critical_threshold is None
            else:
                if 'Gearbox' in rule['name']:
                    gearbox_thermal_rule = rule
                elif 'CPU Core' in rule['name']:
                    cpu_thermal_rule = rule
                
        gearbox_thermal_count = 0
        cpu_thermal_count = 0
        for thermal in thermal_list:
            if 'Gearbox' in thermal.get_name():
                start_index = gearbox_thermal_rule.get('start_index', 1)
                start_index += gearbox_thermal_count
                assert thermal.get_name() == gearbox_thermal_rule['name'].format(start_index)
                assert gearbox_thermal_rule['temperature'].format(start_index) in thermal.temperature
                assert gearbox_thermal_rule['high_threshold'].format(start_index) in thermal.high_threshold
                assert gearbox_thermal_rule['high_critical_threshold'].format(start_index) in thermal.high_critical_threshold
                gearbox_thermal_count += 1
            elif 'CPU Core' in thermal.get_name():
                start_index = cpu_thermal_rule.get('start_index', 1)
                start_index += cpu_thermal_count
                assert thermal.get_name() == cpu_thermal_rule['name'].format(start_index)
                assert cpu_thermal_rule['temperature'].format(start_index) in thermal.temperature
                assert cpu_thermal_rule['high_threshold'].format(start_index) in thermal.high_threshold
                assert cpu_thermal_rule['high_critical_threshold'].format(start_index) in thermal.high_critical_threshold
                cpu_thermal_count += 1
        
        assert gearbox_thermal_count == 2
        assert cpu_thermal_count == 2

    def test_psu_thermal(self):
        from sonic_platform.thermal import initialize_psu_thermal, THERMAL_NAMING_RULE
        os.path.exists = mock.MagicMock(return_value=True)
        presence_cb = mock.MagicMock(return_value=(True, ''))
        thermal_list = initialize_psu_thermal(0, presence_cb)
        assert len(thermal_list) == 1
        thermal = thermal_list[0]
        rule = THERMAL_NAMING_RULE['psu thermals']
        start_index = rule.get('start_index', 1)
        assert thermal.get_name() == rule['name'].format(start_index)
        assert rule['temperature'].format(start_index) in thermal.temperature
        assert rule['high_threshold'].format(start_index) in thermal.high_threshold
        assert thermal.high_critical_threshold is None
        assert thermal.get_position_in_parent() == 1
        assert thermal.is_replaceable() == False

        presence_cb = mock.MagicMock(return_value=(False, 'Not present'))
        thermal_list = initialize_psu_thermal(0, presence_cb)
        assert len(thermal_list) == 1
        thermal = thermal_list[0]
        assert thermal.get_temperature() is None
        assert thermal.get_high_threshold() is None
        assert thermal.get_high_critical_threshold() is None

    def test_sfp_thermal(self):
        from sonic_platform.thermal import initialize_sfp_thermal, THERMAL_NAMING_RULE
        os.path.exists = mock.MagicMock(return_value=True)
        thermal_list = initialize_sfp_thermal(0)
        assert len(thermal_list) == 1
        thermal = thermal_list[0]
        rule = THERMAL_NAMING_RULE['sfp thermals']
        start_index = rule.get('start_index', 1)
        assert thermal.get_name() == rule['name'].format(start_index)
        assert rule['temperature'].format(start_index) in thermal.temperature
        assert rule['high_threshold'].format(start_index) in thermal.high_threshold
        assert rule['high_critical_threshold'].format(start_index) in thermal.high_critical_threshold
        assert thermal.get_position_in_parent() == 1
        assert thermal.is_replaceable() == False

    def test_get_temperature(self):
        from sonic_platform.thermal import Thermal
        from sonic_platform import utils
        thermal = Thermal('test', 'temp_file', None, None, 1)
        utils.read_float_from_file = mock.MagicMock(return_value=35727)
        assert thermal.get_temperature() == 35.727

        utils.read_float_from_file = mock.MagicMock(return_value=0.0)
        assert thermal.get_temperature() is None
        
        utils.read_float_from_file = mock.MagicMock(return_value=None)
        assert thermal.get_temperature() is None

    def test_get_high_threshold(self):
        from sonic_platform.thermal import Thermal
        from sonic_platform import utils
        thermal = Thermal('test', None, None, None, 1)
        assert thermal.get_high_threshold() is None

        thermal.high_threshold = 'high_th_file'
        utils.read_float_from_file = mock.MagicMock(return_value=25833)
        assert thermal.get_temperature() == 25.833

        utils.read_float_from_file = mock.MagicMock(return_value=0.0)
        assert thermal.get_temperature() is None
        
        utils.read_float_from_file = mock.MagicMock(return_value=None)
        assert thermal.get_temperature() is None

    def test_get_high_critical_threshold(self):
        from sonic_platform.thermal import Thermal
        from sonic_platform import utils
        thermal = Thermal('test', None, None, None, 1)
        assert thermal.get_high_critical_threshold() is None

        thermal.high_critical_threshold = 'high_th_file'
        utils.read_float_from_file = mock.MagicMock(return_value=120839)
        assert thermal.get_high_critical_threshold() == 120.839

        utils.read_float_from_file = mock.MagicMock(return_value=0.0)
        assert thermal.get_high_critical_threshold() is None
        
        utils.read_float_from_file = mock.MagicMock(return_value=None)
        assert thermal.get_high_critical_threshold() is None

    def test_set_thermal_algorithm_status(self):
        from sonic_platform.thermal import Thermal, THERMAL_ZONE_FOLDER_WILDCARD, THERMAL_ZONE_POLICY_FILE, THERMAL_ZONE_MODE_FILE
        from sonic_platform import utils
        glob.iglob = mock.MagicMock(return_value=['thermal_zone1', 'thermal_zone2'])
        utils.write_file = mock.MagicMock()
        assert Thermal.set_thermal_algorithm_status(True, False)

        for folder in glob.iglob(THERMAL_ZONE_FOLDER_WILDCARD):
            utils.write_file.assert_any_call(os.path.join(folder, THERMAL_ZONE_POLICY_FILE), 'step_wise')
            utils.write_file.assert_any_call(os.path.join(folder, THERMAL_ZONE_MODE_FILE), 'enabled')
   
        assert Thermal.set_thermal_algorithm_status(False, False)
        for folder in glob.iglob(THERMAL_ZONE_FOLDER_WILDCARD):
            utils.write_file.assert_any_call(os.path.join(folder, THERMAL_ZONE_POLICY_FILE), 'user_space')
            utils.write_file.assert_any_call(os.path.join(folder, THERMAL_ZONE_MODE_FILE), 'disabled')

        assert not Thermal.set_thermal_algorithm_status(False, False)

        assert Thermal.set_thermal_algorithm_status(False)

    def test_check_thermal_zone_temperature(self):
        from sonic_platform.thermal import Thermal, THERMAL_ZONE_FOLDER_WILDCARD, THERMAL_ZONE_THRESHOLD_FILE, THERMAL_ZONE_TEMP_FILE
        from sonic_platform import utils
        glob.iglob = mock.MagicMock(return_value=['thermal_zone1', 'thermal_zone2'])

        utils.read_int_from_file = mock.MagicMock(side_effect=Exception(''))
        assert not Thermal.check_thermal_zone_temperature()

        mock_file_content = {}
        def mock_read_int_from_file(file_path, default=0, raise_exception=False):
            return mock_file_content[file_path]

        utils.read_int_from_file = mock_read_int_from_file
        mock_file_content[os.path.join('thermal_zone1', THERMAL_ZONE_THRESHOLD_FILE)] = 25
        mock_file_content[os.path.join('thermal_zone1', THERMAL_ZONE_TEMP_FILE)] = 30
        mock_file_content[os.path.join('thermal_zone2', THERMAL_ZONE_THRESHOLD_FILE)] = 25
        mock_file_content[os.path.join('thermal_zone2', THERMAL_ZONE_TEMP_FILE)] = 24
        assert not Thermal.check_thermal_zone_temperature()

        mock_file_content[os.path.join('thermal_zone1', THERMAL_ZONE_TEMP_FILE)] = 24
        assert Thermal.check_thermal_zone_temperature()

    def test_check_module_temperature_trustable(self):
        from sonic_platform.thermal import Thermal
        from sonic_platform import utils
        glob.iglob = mock.MagicMock(return_value=['thermal_zone1', 'thermal_zone2'])

        utils.read_int_from_file = mock.MagicMock(return_value=1)
        assert Thermal.check_module_temperature_trustable() == 'untrust'

        utils.read_int_from_file = mock.MagicMock(return_value=0)
        assert Thermal.check_module_temperature_trustable() == 'trust'

    def test_get_min_amb_temperature(self):
        from sonic_platform.thermal import Thermal, MAX_AMBIENT_TEMP, CHASSIS_THERMAL_SYSFS_FOLDER
        from sonic_platform import utils

        utils.read_int_from_file = mock.MagicMock(side_effect=Exception(''))
        assert Thermal.get_min_amb_temperature() == MAX_AMBIENT_TEMP

        mock_file_content = {}
        def mock_read_int_from_file(file_path, default=0, raise_exception=False):
            return mock_file_content[file_path]

        utils.read_int_from_file = mock_read_int_from_file
        mock_file_content[os.path.join(CHASSIS_THERMAL_SYSFS_FOLDER, 'fan_amb')] = 50
        mock_file_content[os.path.join(CHASSIS_THERMAL_SYSFS_FOLDER, 'port_amb')] = 40
        assert Thermal.get_min_amb_temperature() == 40
