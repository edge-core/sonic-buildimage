"""
    Unit test cases for system health checker. The current test case contains:
        1. test_user_defined_checker mocks the output of a user defined checker and verify class UserDefinedChecker
        2. test_service_checker mocks the output of monit service and verify class ServiceChecker
        3. test_hardware_checker mocks the hardware status data in db and verify class HardwareChecker
    And there are class that are not covered by unit test. These class will be covered by sonic-mgmt regression test.
        1. HealthDaemon
        2. HealthCheckerManager
        3. Config
"""
import os
import sys
import swsssdk

from mock import Mock, MagicMock, patch
from sonic_py_common import device_info

from .mock_connector import MockConnector

swsssdk.SonicV2Connector = MockConnector

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)
from health_checker import utils
from health_checker.config import Config
from health_checker.hardware_checker import HardwareChecker
from health_checker.health_checker import HealthChecker
from health_checker.manager import HealthCheckerManager
from health_checker.service_checker import ServiceChecker
from health_checker.user_defined_checker import UserDefinedChecker

device_info.get_platform = MagicMock(return_value='unittest')


def test_user_defined_checker():
    utils.run_command = MagicMock(return_value='')

    checker = UserDefinedChecker('')
    checker.check(None)
    assert checker._info[str(checker)][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    checker.reset()
    assert len(checker._info) == 0

    utils.run_command = MagicMock(return_value='\n\n\n')
    checker.check(None)
    assert checker._info[str(checker)][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    valid_output = 'MyCategory\nDevice1:OK\nDevice2:Device2 is broken\n'
    utils.run_command = MagicMock(return_value=valid_output)
    checker.check(None)
    assert 'Device1' in checker._info
    assert 'Device2' in checker._info
    assert checker._info['Device1'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK
    assert checker._info['Device2'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK


def test_service_checker():
    return_value = ''

    def mock_run_command(cmd):
        if cmd == ServiceChecker.CHECK_MONIT_SERVICE_CMD:
            return 'active'
        else:
            return return_value

    utils.run_command = mock_run_command
    return_value = 'Monit 5.20.0 uptime: 3h 54m\n' \
                   'Service Name                     Status                      Type\n' \
                   'sonic                            Running                     System\n' \
                   'sonic1                           Not running                 System\n' \
                   'telemetry                        Does not exist              Process\n' \
                   'orchagent                        Running                     Process\n' \
                   'root-overlay                     Accessible                  Filesystem\n' \
                   'var-log                          Is not accessible           Filesystem\n' 
                   
    checker = ServiceChecker()
    config = Config()
    checker.check(config)
    assert 'sonic' in checker._info
    assert checker._info['sonic'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'sonic1' in checker._info
    assert checker._info['sonic1'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'orchagent' in checker._info
    assert checker._info['orchagent'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'telemetry' in checker._info
    assert checker._info['telemetry'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'root-overlay' in checker._info
    assert checker._info['root-overlay'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'var-log' in checker._info
    assert checker._info['var-log'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK


def test_hardware_checker():
    MockConnector.data.update({
        'TEMPERATURE_INFO|ASIC': {
            'temperature': '20',
            'high_threshold': '21'
        }
    })

    MockConnector.data.update({
        'FAN_INFO|fan1': {
            'presence': 'True',
            'status': 'True',
            'speed': '60',
            'speed_target': '60',
            'speed_tolerance': '20'
        },
        'FAN_INFO|fan2': {
            'presence': 'False',
            'status': 'True',
            'speed': '60',
            'speed_target': '60',
            'speed_tolerance': '20'
        },
        'FAN_INFO|fan3': {
            'presence': 'True',
            'status': 'False',
            'speed': '60',
            'speed_target': '60',
            'speed_tolerance': '20'
        },
        'FAN_INFO|fan4': {
            'presence': 'True',
            'status': 'True',
            'speed': '20',
            'speed_target': '60',
            'speed_tolerance': '20'
        }
    })

    MockConnector.data.update({
        'PSU_INFO|PSU 1': {
            'presence': 'True',
            'status': 'True',
            'temp': '55',
            'temp_threshold': '100',
            'voltage': '10',
            'voltage_min_threshold': '8',
            'voltage_max_threshold': '15',
        },
        'PSU_INFO|PSU 2': {
            'presence': 'False',
            'status': 'True',
            'temp': '55',
            'temp_threshold': '100',
            'voltage': '10',
            'voltage_min_threshold': '8',
            'voltage_max_threshold': '15',
        },
        'PSU_INFO|PSU 3': {
            'presence': 'True',
            'status': 'False',
            'temp': '55',
            'temp_threshold': '100',
            'voltage': '10',
            'voltage_min_threshold': '8',
            'voltage_max_threshold': '15',
        },
        'PSU_INFO|PSU 4': {
            'presence': 'True',
            'status': 'True',
            'temp': '101',
            'temp_threshold': '100',
            'voltage': '10',
            'voltage_min_threshold': '8',
            'voltage_max_threshold': '15',
        },
        'PSU_INFO|PSU 5': {
            'presence': 'True',
            'status': 'True',
            'temp': '55',
            'temp_threshold': '100',
            'voltage': '10',
            'voltage_min_threshold': '12',
            'voltage_max_threshold': '15',
        }
    })

    checker = HardwareChecker()
    config = Config()
    checker.check(config)

    assert 'ASIC' in checker._info
    assert checker._info['ASIC'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'fan1' in checker._info
    assert checker._info['fan1'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'fan2' in checker._info
    assert checker._info['fan2'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'fan3' in checker._info
    assert checker._info['fan3'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'fan4' in checker._info
    assert checker._info['fan4'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'PSU 1' in checker._info
    assert checker._info['PSU 1'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_OK

    assert 'PSU 2' in checker._info
    assert checker._info['PSU 2'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'PSU 3' in checker._info
    assert checker._info['PSU 3'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'PSU 4' in checker._info
    assert checker._info['PSU 4'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK

    assert 'PSU 5' in checker._info
    assert checker._info['PSU 5'][HealthChecker.INFO_FIELD_OBJECT_STATUS] == HealthChecker.STATUS_NOT_OK
