import os
import sys
import pytest
import json
from mock import MagicMock
from .mock_platform import MockChassis, MockFan, MockPsu

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.thermal_manager import ThermalManager
from sonic_platform.thermal_infos import FanInfo, PsuInfo
from sonic_platform.fan import Fan
from sonic_platform.thermal import Thermal

Thermal.check_thermal_zone_temperature = MagicMock()
Thermal.set_thermal_algorithm_status = MagicMock()


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

    fan_list = chassis.get_all_fans()
    fan_list[0].presence = True
    fan_info.collect(chassis)
    assert len(fan_info.get_absence_fans()) == 0
    assert len(fan_info.get_presence_fans()) == 1
    assert len(fan_info.get_fault_fans()) == 0
    assert fan_info.is_status_changed()

    fan_list[0].status = False
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
    assert len(psu_info.get_absence_psus()) == 1
    assert len(psu_info.get_presence_psus()) == 0
    assert psu_info.is_status_changed()


def test_fan_policy(thermal_manager):
    chassis = MockChassis()
    chassis.make_fan_absence()
    chassis.fan_list.append(MockFan())
    thermal_manager.run_policy(chassis)

    fan_list = chassis.get_all_fans()
    assert fan_list[1].speed == 100
    Thermal.set_thermal_algorithm_status.assert_called_with(False, False)

    fan_list[0].presence = True
    Thermal.check_thermal_zone_temperature = MagicMock(return_value=True)
    thermal_manager.run_policy(chassis)
    Thermal.set_thermal_algorithm_status.assert_called_with(True, False)
    assert Thermal.check_thermal_zone_temperature.call_count == 2
    assert fan_list[0].speed == 60
    assert fan_list[1].speed == 60

    fan_list[0].status = False
    thermal_manager.run_policy(chassis)
    Thermal.set_thermal_algorithm_status.assert_called_with(False, False)

    fan_list[0].status = True
    Thermal.check_thermal_zone_temperature = MagicMock(return_value=False)
    thermal_manager.run_policy(chassis)
    Thermal.set_thermal_algorithm_status.assert_called_with(True, False)
    assert Thermal.check_thermal_zone_temperature.call_count == 2
    assert fan_list[0].speed == 100
    assert fan_list[1].speed == 100


def test_psu_policy(thermal_manager):
    chassis = MockChassis()
    chassis.make_psu_absence()
    chassis.fan_list.append(MockFan())
    thermal_manager.run_policy(chassis)

    fan_list = chassis.get_all_fans()
    assert fan_list[0].speed == 100
    Thermal.set_thermal_algorithm_status.assert_called_with(False, False)

    psu_list = chassis.get_all_psus()
    psu_list[0].presence = True
    thermal_manager.run_policy(chassis)
    Thermal.set_thermal_algorithm_status.assert_called_with(True, False)


def test_any_fan_absence_condition():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_conditions import AnyFanAbsenceCondition
    condition = AnyFanAbsenceCondition()
    assert condition.is_match({'fan_info': fan_info})

    fan = chassis.get_all_fans()[0]
    fan.presence = True
    fan_info.collect(chassis)
    assert not condition.is_match({'fan_info': fan_info})


def test_all_fan_absence_condition():
    chassis = MockChassis()
    chassis.make_fan_absence()
    fan = MockFan()
    fan_list = chassis.get_all_fans()
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
    fan_list = chassis.get_all_fans()
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
    fan = MockFan()
    fan_list = chassis.get_all_fans()
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
    fan = MockFan()
    fan_list = chassis.get_all_fans()
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


def test_execute_set_fan_speed_action():
    chassis = MockChassis()
    fan_list = chassis.get_all_fans()
    fan_list.append(MockFan())
    fan_list.append(MockFan())
    fan_info = FanInfo()
    fan_info.collect(chassis)

    from sonic_platform.thermal_actions import SetAllFanSpeedAction
    action = SetAllFanSpeedAction()
    action.speed = 99
    action.execute({'fan_info': fan_info})
    assert fan_list[0].speed == 99
    assert fan_list[1].speed == 99


def test_load_control_thermal_algo_action():
    from sonic_platform.thermal_actions import ControlThermalAlgoAction
    action = ControlThermalAlgoAction()
    json_str = '{\"status\": \"false\"}'
    json_obj = json.loads(json_str)
    action.load_from_json(json_obj)
    assert not action.status 

    json_str = '{\"status\": \"true\"}'
    json_obj = json.loads(json_str)
    action.load_from_json(json_obj)
    assert action.status 

    json_str = '{\"status\": \"invalid\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

    json_str = '{\"invalid\": \"true\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

def test_load_check_and_set_speed_action():
    from sonic_platform.thermal_actions import CheckAndSetAllFanSpeedAction
    action = CheckAndSetAllFanSpeedAction()
    json_str = '{\"speed\": \"40\"}'
    json_obj = json.loads(json_str)
    action.load_from_json(json_obj)
    assert action.speed == 40

    json_str = '{\"speed\": \"-1\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

    json_str = '{\"speed\": \"101\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

    json_str = '{\"invalid\": \"60\"}'
    json_obj = json.loads(json_str)
    with pytest.raises(ValueError):
        action.load_from_json(json_obj)

def test_execute_check_and_set_fan_speed_action():
    chassis = MockChassis()
    fan_list = chassis.get_all_fans()
    fan_list.append(MockFan())
    fan_list.append(MockFan())
    fan_info = FanInfo()
    fan_info.collect(chassis)
    Thermal.check_thermal_zone_temperature = MagicMock(return_value=True)

    from sonic_platform.thermal_actions import CheckAndSetAllFanSpeedAction
    action = CheckAndSetAllFanSpeedAction()
    action.speed = 99
    action.execute({'fan_info': fan_info})
    assert fan_list[0].speed == 99
    assert fan_list[1].speed == 99

    Thermal.check_thermal_zone_temperature = MagicMock(return_value=False)
    fan_list[0].speed = 100
    fan_list[1].speed = 100
    action.speed = 60
    action.execute({'fan_info': fan_info})
    assert fan_list[0].speed == 100
    assert fan_list[1].speed == 100

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

def test_dynamic_minimum_policy(thermal_manager):
    from sonic_platform.thermal_conditions import MinCoolingLevelChangeCondition
    from sonic_platform.thermal_actions import ChangeMinCoolingLevelAction
    from sonic_platform.thermal_infos import ChassisInfo
    from sonic_platform.thermal import Thermal
    from sonic_platform.fan import Fan
    ThermalManager.initialize()
    assert 'DynamicMinCoolingLevelPolicy' in thermal_manager._policy_dict
    policy = thermal_manager._policy_dict['DynamicMinCoolingLevelPolicy']
    assert MinCoolingLevelChangeCondition in policy.conditions
    assert ChangeMinCoolingLevelAction in policy.actions

    condition = policy.conditions[MinCoolingLevelChangeCondition]
    action = policy.actions[ChangeMinCoolingLevelAction]
    Thermal.check_module_temperature_trustable = MagicMock(return_value='trust')
    Thermal.get_min_amb_temperature = MagicMock(return_value=35000)
    assert condition.is_match(None)
    assert MinCoolingLevelChangeCondition.trust_state == 'trust'
    assert MinCoolingLevelChangeCondition.temperature == 35
    assert not condition.is_match(None)

    Thermal.check_module_temperature_trustable = MagicMock(return_value='untrust')
    assert condition.is_match(None)
    assert MinCoolingLevelChangeCondition.trust_state == 'untrust'

    Thermal.get_min_amb_temperature = MagicMock(return_value=25000)
    assert condition.is_match(None)
    assert MinCoolingLevelChangeCondition.temperature == 25

    chassis = MockChassis()
    chassis.platform_name = 'invalid'
    info = ChassisInfo()
    info._chassis = chassis
    thermal_info_dict = {ChassisInfo.INFO_NAME: info}
    Fan.get_cooling_level = MagicMock(return_value=5)
    Fan.set_cooling_level = MagicMock()
    action.execute(thermal_info_dict)
    assert Fan.min_cooling_level == 6
    Fan.set_cooling_level.assert_called_with(6, 6)
    Fan.set_cooling_level.call_count = 0

    chassis.platform_name = 'x86_64-mlnx_msn2700-r0'
    action.execute(thermal_info_dict)
    assert Fan.min_cooling_level == 3
    Fan.set_cooling_level.assert_called_with(3, 5)
