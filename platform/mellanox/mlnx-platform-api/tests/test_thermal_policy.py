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
    assert fan_info.is_status_changed()

    fan_list = chassis.get_all_fans()
    fan_list[0].presence = True
    fan_info.collect(chassis)
    assert len(fan_info.get_absence_fans()) == 0
    assert len(fan_info.get_presence_fans()) == 1
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


def test_fan_policy(thermal_manager):
    chassis = MockChassis()
    chassis.make_fan_absence()
    chassis.fan_list.append(MockFan())
    thermal_manager.start_thermal_control_algorithm = MagicMock()
    thermal_manager.stop_thermal_control_algorithm = MagicMock()
    thermal_manager.run_policy(chassis)

    fan_list = chassis.get_all_fans()
    assert fan_list[1].speed == 100
    thermal_manager.stop_thermal_control_algorithm.assert_called_once()

    fan_list[0].presence = True
    thermal_manager.run_policy(chassis)
    thermal_manager.start_thermal_control_algorithm.assert_called_once()


def test_psu_policy(thermal_manager):
    chassis = MockChassis()
    chassis.make_psu_absence()
    chassis.fan_list.append(MockFan())
    thermal_manager.start_thermal_control_algorithm = MagicMock()
    thermal_manager.stop_thermal_control_algorithm = MagicMock()
    thermal_manager.run_policy(chassis)

    fan_list = chassis.get_all_fans()
    assert fan_list[0].speed == 100
    thermal_manager.stop_thermal_control_algorithm.assert_called_once()

    psu_list = chassis.get_all_psus()
    psu_list[0].presence = True
    thermal_manager.run_policy(chassis)
    thermal_manager.start_thermal_control_algorithm.assert_called_once()


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


