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
import sys
import pytest
import json
from mock import MagicMock, patch
from .mock_platform import MockChassis, MockFan, MockFanDrawer, MockPsu

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.thermal_manager import ThermalManager
from sonic_platform.thermal_infos import FanInfo, PsuInfo
from sonic_platform.thermal import Thermal, MAX_COOLING_LEVEL
from sonic_platform.device_data import DeviceDataManager


@pytest.fixture(scope='session', autouse=True)
def thermal_manager():
    policy_file = os.path.join(test_path, 'thermal_policy.json')
    ThermalManager.load(policy_file)
    return ThermalManager


def test_load_policy(thermal_manager):
    assert 'psu_info' in thermal_manager._thermal_info_dict
    assert 'fan_info' in thermal_manager._thermal_info_dict
    assert 'chassis_info' in thermal_manager._thermal_info_dict

    assert 'any fan absence' in thermal_manager._policy_dict
    assert 'any psu absence' in thermal_manager._policy_dict
    assert 'any fan broken' in thermal_manager._policy_dict
    assert 'all fan and psu presence' in thermal_manager._policy_dict

    assert thermal_manager._fan_speed_when_suspend == 60
    assert thermal_manager._run_thermal_algorithm_at_boot_up == False


def test_fan_info():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan_info = FanInfo()
    fan_info.collect(chassis)
    assert len(fan_info.get_absence_fans()) == 1
    assert len(fan_info.get_presence_fans()) == 0
    assert len(fan_info.get_fault_fans()) == 0
    assert fan_info.is_status_changed()

    chassis.get_all_fan_drawers()[0].get_all_fans()[0].presence = True
    fan_info.collect(chassis)
    assert len(fan_info.get_absence_fans()) == 0
    assert len(fan_info.get_presence_fans()) == 1
    assert len(fan_info.get_fault_fans()) == 0
    assert fan_info.is_status_changed()

    chassis.get_all_fan_drawers()[0].get_all_fans()[0].status = False
    fan_info.collect(chassis)
    assert len(fan_info.get_absence_fans()) == 0
    assert len(fan_info.get_presence_fans()) == 1
    assert len(fan_info.get_fault_fans()) == 1
    assert fan_info.is_status_changed()

def test_psu_info():
    chassis = MockChassis()
    chassis.make_psu_absence()
    psu_info = PsuInfo()
    psu_info.collect(chassis)
    assert len(psu_info.get_absence_psus()) == 1
    assert len(psu_info.get_presence_psus()) == 0
    assert psu_info.is_status_changed()

    psu_list = chassis.get_all_psus()
    psu_list[0].presence = True
    psu_info.collect(chassis)
    assert len(psu_info.get_absence_psus()) == 0
    assert len(psu_info.get_presence_psus()) == 1
    assert psu_info.is_status_changed()

    psu_list[0].powergood = False
    psu_info.collect(chassis)
    assert len(psu_info.get_absence_psus()) == 0
    assert len(psu_info.get_presence_psus()) == 1
    assert not psu_info.is_status_changed()


@patch('sonic_platform.thermal.Thermal.monitor_asic_themal_zone', MagicMock())
@patch('sonic_platform.thermal.Thermal.get_cooling_level', MagicMock(return_value=6))
@patch('sonic_platform.thermal.Thermal.get_min_allowed_cooling_level_by_thermal_zone', MagicMock(return_value=2))
@patch('sonic_platform.thermal.Thermal.set_cooling_state')
@patch('sonic_platform.thermal.Thermal.set_cooling_level')
def test_fan_policy(mock_set_cooling_level, mock_set_cooling_state, thermal_manager):
    print('In test_fan_policy')
    from sonic_platform.thermal import MIN_COOLING_LEVEL_FOR_NORMAL
    chassis = MockChassis()
    chassis.make_fan_absence()
    chassis.get_all_fan_drawers()[0].get_all_fans().append(MockFan())
    chassis.platform_name = 'some_platform'
    thermal_manager.run_policy(chassis)

    mock_set_cooling_level.assert_called_with(MAX_COOLING_LEVEL)
    mock_set_cooling_state.assert_called_with(MAX_COOLING_LEVEL)

    Thermal.expect_cooling_level = None
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list[0].presence = True
    thermal_manager.run_policy(chassis)
    mock_set_cooling_level.assert_called_with(6)
    mock_set_cooling_state.assert_called_with(6)

    Thermal.expect_cooling_level = None
    fan_list[0].status = False
    thermal_manager.run_policy(chassis)
    mock_set_cooling_level.assert_called_with(MAX_COOLING_LEVEL)

    Thermal.expect_cooling_level = None
    fan_list[0].status = True
    thermal_manager.run_policy(chassis)
    mock_set_cooling_level.assert_called_with(6)
    mock_set_cooling_state.assert_called_with(6)


@patch('sonic_platform.thermal.Thermal.monitor_asic_themal_zone', MagicMock())
@patch('sonic_platform.thermal.Thermal.get_min_allowed_cooling_level_by_thermal_zone', MagicMock(return_value=2))
@patch('sonic_platform.thermal.Thermal.get_cooling_level', MagicMock(return_value=6))
@patch('sonic_platform.thermal.Thermal.set_cooling_state')
@patch('sonic_platform.thermal.Thermal.set_cooling_level')
def test_psu_policy(mock_set_cooling_level, mock_set_cooling_state, thermal_manager):
    chassis = MockChassis()
    chassis.make_psu_absence()
    chassis.platform_name = 'some_platform'
    thermal_manager.run_policy(chassis)
    mock_set_cooling_level.assert_called_with(MAX_COOLING_LEVEL)
    mock_set_cooling_state.assert_called_with(MAX_COOLING_LEVEL)

    psu_list = chassis.get_all_psus()
    psu_list[0].presence = True
    thermal_manager.run_policy(chassis)
    mock_set_cooling_level.assert_called_with(6)
    mock_set_cooling_state.assert_called_with(6)


def test_any_fan_absence_condition():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AnyFanAbsenceCondition
    condition = AnyFanAbsenceCondition()
    assert condition.is_match({'fan_info': fan_info})

    fan = chassis.get_all_fan_drawers()[0].get_all_fans()[0]
    fan.presence = True
    fan_info.collect(chassis)
    assert not condition.is_match({'fan_info': fan_info})


def test_all_fan_absence_condition():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan = MockFan()
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list.append(fan)
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AllFanAbsenceCondition
    condition = AllFanAbsenceCondition()
    assert not condition.is_match({'fan_info': fan_info})

    fan.presence = False
    fan_info.collect(chassis)
    assert condition.is_match({'fan_info': fan_info})


def test_all_fan_presence_condition():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan = MockFan()
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list.append(fan)
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AllFanPresenceCondition
    condition = AllFanPresenceCondition()
    assert not condition.is_match({'fan_info': fan_info})

    fan_list[0].presence = True
    fan_info.collect(chassis)
    assert condition.is_match({'fan_info': fan_info})

def test_any_fan_fault_condition():
    chassis = MockChassis()
    chassis.get_all_fan_drawers().append(MockFanDrawer())
    fan = MockFan()
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list.append(fan)
    fault_fan = MockFan()
    fault_fan.status = False
    fan_list.append(fault_fan)
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AnyFanFaultCondition
    condition = AnyFanFaultCondition()
    assert condition.is_match({'fan_info': fan_info})

    fault_fan.status = True
    fan_info.collect(chassis)
    assert not condition.is_match({'fan_info': fan_info})

def test_all_fan_good_condition():
    chassis = MockChassis()
    chassis.get_all_fan_drawers().append(MockFanDrawer())
    fan = MockFan()
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list.append(fan)
    fault_fan = MockFan()
    fault_fan.status = False
    fan_list.append(fault_fan)
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AllFanGoodCondition
    condition = AllFanGoodCondition()
    assert not condition.is_match({'fan_info': fan_info})

    fault_fan.status = True
    fan_info.collect(chassis)
    assert condition.is_match({'fan_info': fan_info})


def test_any_psu_absence_condition():
    chassis = MockChassis()
    chassis.make_psu_absence()
    psu_info = PsuInfo()
    psu_info.collect(chassis)

    from sonic_platform.thermal_conditions import AnyPsuAbsenceCondition
    condition = AnyPsuAbsenceCondition()
    assert condition.is_match({'psu_info': psu_info})

    psu = chassis.get_all_psus()[0]
    psu.presence = True
    psu_info.collect(chassis)
    assert not condition.is_match({'psu_info': psu_info})


def test_all_psu_absence_condition():
    chassis = MockChassis()
    chassis.make_psu_absence()
    psu = MockPsu()
    psu_list = chassis.get_all_psus()
    psu_list.append(psu)
    psu_info = PsuInfo()
    psu_info.collect(chassis)

    from sonic_platform.thermal_conditions import AllPsuAbsenceCondition
    condition = AllPsuAbsenceCondition()
    assert not condition.is_match({'psu_info': psu_info})

    psu.presence = False
    psu_info.collect(chassis)
    assert condition.is_match({'psu_info': psu_info})


def test_all_fan_presence_condition():
    chassis = MockChassis()
    chassis.make_psu_absence()
    psu = MockPsu()
    psu_list = chassis.get_all_psus()
    psu_list.append(psu)
    psu_info = PsuInfo()
    psu_info.collect(chassis)

    from sonic_platform.thermal_conditions import AllPsuPresenceCondition
    condition = AllPsuPresenceCondition()
    assert not condition.is_match({'psu_info': psu_info})

    psu_list[0].presence = True
    psu_info.collect(chassis)
    assert condition.is_match({'psu_info': psu_info})


def test_load_set_fan_speed_action():
    from sonic_platform.thermal_actions import SetAllFanSpeedAction
    action = SetAllFanSpeedAction()
    json_str = '{\"speed\": \"50\"}'
    json_obj = json.loads(json_str)
    action.load_from_json(json_obj)
    assert action.speed == 50

    json_str = '{\"speed\": \"-1\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

    json_str = '{\"speed\": \"101\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

    json_str = '{\"invalid\": \"101\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)


@patch('sonic_platform.thermal.Thermal.set_cooling_level', MagicMock())
def test_execute_set_fan_speed_action():
    chassis = MockChassis()
    chassis.get_all_fan_drawers().append(MockFanDrawer())
    fan_list = chassis.get_all_fan_drawers()[0].get_all_fans()
    fan_list.append(MockFan())
    fan_list.append(MockFan())
    fan_info = FanInfo()
    fan_info.collect(chassis)

    Thermal.expect_cooling_level = None
    from sonic_platform.thermal_actions import SetAllFanSpeedAction
    action = SetAllFanSpeedAction()
    action.speed = 20
    action.execute({'fan_info': fan_info})
    assert Thermal.expect_cooling_level == 2


def test_load_duplicate_condition():
    from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
    with open(os.path.join(test_path, 'duplicate_condition.json')) as f:
        json_obj = json.load(f)
        policy = ThermalPolicy()
        with pytest.raises(Exception):
            policy.load_from_json(json_obj)

def test_load_duplicate_action():
    from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
    with open(os.path.join(test_path, 'duplicate_action.json')) as f:
        json_obj = json.load(f)
        policy = ThermalPolicy()
        with pytest.raises(Exception):
            policy.load_from_json(json_obj)

def test_load_empty_condition():
    from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
    with open(os.path.join(test_path, 'empty_condition.json')) as f:
        json_obj = json.load(f)
        policy = ThermalPolicy()
        with pytest.raises(Exception):
            policy.load_from_json(json_obj)

def test_load_empty_action():
    from sonic_platform_base.sonic_thermal_control.thermal_policy import ThermalPolicy
    with open(os.path.join(test_path, 'empty_action.json')) as f:
        json_obj = json.load(f)
        policy = ThermalPolicy()
        with pytest.raises(Exception):
            policy.load_from_json(json_obj)

def test_load_policy_with_same_conditions():
    from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
    class MockThermalManager(ThermalManagerBase):
        pass

    with pytest.raises(Exception):
        MockThermalManager.load(os.path.join(test_path, 'policy_with_same_conditions.json'))

def test_dynamic_minimum_table_data():
    from sonic_platform.device_data import DEVICE_DATA
    for platform, platform_data in DEVICE_DATA.items():
        if 'thermal' in platform_data and 'minimum_table' in platform_data['thermal']:
            minimum_table = platform_data['thermal']['minimum_table']
            check_minimum_table_data(platform, minimum_table)

def check_minimum_table_data(platform, minimum_table):
    valid_dir = ['p2c', 'c2p', 'unk']
    valid_trust_state = ['trust', 'untrust']

    for category, data in minimum_table.items():
        key_data = category.split('_')
        assert key_data[0] in valid_dir
        assert key_data[1] in valid_trust_state

        data_list = [(value, key) for key, value in data.items()]
        data_list.sort(key=lambda x : x[0])

        previous_edge = None
        previous_cooling_level = None
        for item in data_list:
            cooling_level = item[0]
            range_str = item[1]

            ranges = range_str.split(':')
            low = int(ranges[0])
            high = int(ranges[1])
            assert low < high

            if previous_edge is None:
                assert low == -127
            else:
                assert low - previous_edge == 1, '{}-{}-{} error, item={}'.format(platform, key_data[0], key_data[1], item)
            previous_edge = high

            assert 10 <= cooling_level <= 20
            if previous_cooling_level is not None:
                assert cooling_level > previous_cooling_level
            previous_cooling_level = cooling_level

@patch('sonic_platform.thermal.Thermal.monitor_asic_themal_zone', MagicMock())
@patch('sonic_platform.device_data.DeviceDataManager.get_platform_name')
@patch('sonic_platform.thermal.Thermal.get_min_allowed_cooling_level_by_thermal_zone')
@patch('sonic_platform.thermal.Thermal.get_min_amb_temperature')
@patch('sonic_platform.thermal.Thermal.check_module_temperature_trustable')
def test_thermal_recover_policy(mock_check_trustable, mock_get_min_amb, moc_get_min_allowed, mock_platform_name):
    from sonic_platform.thermal_infos import ChassisInfo
    from sonic_platform.thermal_actions import ThermalRecoverAction
    chassis = MockChassis()
    mock_platform_name.return_value = 'invalid'
    info = ChassisInfo()
    info._chassis = chassis
    thermal_info_dict = {ChassisInfo.INFO_NAME: info}

    Thermal.expect_cooling_level = None
    action = ThermalRecoverAction()
    moc_get_min_allowed.return_value = 2
    action.execute(thermal_info_dict)
    assert Thermal.expect_cooling_level == 6
    Thermal.last_set_cooling_level = Thermal.expect_cooling_level

    Thermal.expect_cooling_level = None
    mock_platform_name.return_value = 'x86_64-mlnx_msn2700-r0'
    mock_check_trustable.return_value = 'trust'
    mock_get_min_amb.return_value = 29999
    moc_get_min_allowed.return_value = None
    action.execute(thermal_info_dict)
    assert Thermal.expect_cooling_level is None

    moc_get_min_allowed.return_value = 4
    action.execute(thermal_info_dict)
    assert Thermal.expect_cooling_level == 4
    Thermal.last_set_cooling_level = Thermal.expect_cooling_level

    mock_check_trustable.return_value = 'untrust'
    mock_get_min_amb.return_value = 31001
    action.execute(thermal_info_dict)
    assert Thermal.expect_cooling_level == 5


@patch('sonic_platform.thermal.Thermal.set_cooling_state')
@patch('sonic_platform.utils.read_int_from_file')
def test_monitor_asic_themal_zone(mock_read_int, mock_set_cooling_state):
    mock_read_int.side_effect = [111000, 105000]
    Thermal.monitor_asic_themal_zone()
    assert Thermal.expect_cooling_state == MAX_COOLING_LEVEL
    Thermal.commit_cooling_level({})
    mock_set_cooling_state.assert_called_with(MAX_COOLING_LEVEL)
    mock_read_int.reset()
    mock_read_int.side_effect = [104000, 105000]
    Thermal.monitor_asic_themal_zone()
    assert Thermal.expect_cooling_state is None


def test_set_expect_cooling_level():
    Thermal.set_expect_cooling_level(5)
    assert Thermal.expect_cooling_level == 5

    Thermal.set_expect_cooling_level(3)
    assert Thermal.expect_cooling_level == 5

    Thermal.set_expect_cooling_level(10)
    assert Thermal.expect_cooling_level == 10


@patch('sonic_platform.thermal.Thermal.commit_cooling_level', MagicMock())
@patch('sonic_platform.thermal_conditions.AnyFanFaultCondition.is_match')
@patch('sonic_platform.thermal_manager.ThermalManager._collect_thermal_information')
@patch('sonic_platform.thermal.Thermal.set_expect_cooling_level')
def test_run_policy(mock_expect, mock_collect_info, mock_match, thermal_manager):
    chassis = MockChassis()
    mock_collect_info.side_effect = Exception('')
    thermal_manager.run_policy(chassis)
    mock_expect.assert_called_with(MAX_COOLING_LEVEL)

    mock_collect_info.side_effect = None
    mock_expect.reset_mock()
    mock_match.side_effect = Exception('')
    thermal_manager.run_policy(chassis)
    mock_expect.assert_called_with(MAX_COOLING_LEVEL)

    thermal_manager.stop()
    mock_expect.reset_mock()
    thermal_manager.run_policy(chassis)
    assert mock_expect.call_count == 0

