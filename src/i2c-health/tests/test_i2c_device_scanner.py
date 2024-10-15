import os
import sys
import json
import pytest
import subprocess


# TODO: Clean this up once we no longer need to support Python 2
if sys.version_info >= (3, 3):
    from unittest.mock import MagicMock, patch
else:
    from mock import MagicMock, patch

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
util_path = os.path.join(modules_path, "i2c_health_mgr")
sys.path.insert(0, modules_path)
sys.path.insert(0, util_path)

import i2c_devices_scanner
import i2c_device_entity

with open(os.path.join(test_path,"mock_i2c_region_list.json"), "r") as f:
    mock_i2c_region_list = json.load(f)

@patch('i2c_devices_scanner.platform_chassis', MagicMock())
def test_wrapper_i2c_region_list():
    i2c_devices_scanner.platform_chassis.get_all_i2c_region_list = MagicMock(return_value=mock_i2c_region_list)
    parsed_list = i2c_devices_scanner._wrapper_i2c_region_list()
    assert i2c_devices_scanner.platform_chassis.get_all_i2c_region_list.call_count == 1
    assert len(parsed_list) == 5
    for region_id in parsed_list:
        for pdata,mdata in zip(parsed_list[region_id], mock_i2c_region_list[region_id]):
            assert pdata.get_name() == mdata["name"]
            assert pdata.get_bus() == mdata["bus"]
            assert pdata.get_device_addr() == mdata["device_addr"]
            assert pdata.get_register_addr() == mdata["register_addr"]

    i2c_devices_scanner.platform_chassis.get_all_i2c_region_list.side_effect = NotImplementedError
    i2c_devices_scanner._wrapper_i2c_region_list()
    assert i2c_devices_scanner.platform_chassis.get_all_i2c_region_list.call_count == 2

    i2c_devices_scanner.platform_chassis = None
    assert i2c_devices_scanner._wrapper_i2c_region_list() == {}


@patch('i2c_devices_scanner.platform_chassis', MagicMock())
def test_wrapper_reset_i2c_mux():
    i2c_devices_scanner.platform_chassis.reset_i2c_mux = MagicMock()
    i2c_devices_scanner._wrapper_reset_i2c_mux()
    assert i2c_devices_scanner.platform_chassis.reset_i2c_mux.call_count  == 1

    i2c_devices_scanner.platform_chassis.reset_i2c_mux.side_effect = NotImplementedError
    i2c_devices_scanner._wrapper_reset_i2c_mux()
    assert i2c_devices_scanner.platform_chassis.reset_i2c_mux.call_count == 2


@patch('i2c_devices_scanner.platform_chassis', MagicMock())
def test_wrapper_set_i2c_faulty_device():
    i2c_devices_scanner.platform_chassis.set_i2c_faulty_device = MagicMock()
    i2c_devices_scanner._wrapper_set_i2c_faulty_device('01', '0x76', True)
    assert i2c_devices_scanner.platform_chassis.set_i2c_faulty_device.call_count  == 1

    i2c_devices_scanner._wrapper_set_i2c_faulty_device('01', '0x76', False)
    assert i2c_devices_scanner.platform_chassis.set_i2c_faulty_device.call_count  == 2

    i2c_devices_scanner.platform_chassis.set_i2c_faulty_device.side_effect = NotImplementedError
    i2c_devices_scanner._wrapper_set_i2c_faulty_device('01', '0x76', True)
    assert i2c_devices_scanner.platform_chassis.set_i2c_faulty_device.call_count == 3


@patch('subprocess.check_output', MagicMock())
def test_execute_os_cmd():
    subprocess.check_output.return_value=1
    ret = i2c_devices_scanner.execute_os_cmd('sudo i2cget -f -y 13 0x50 0x0')
    assert ret == True

    subprocess.check_output.side_effect=subprocess.CalledProcessError(1,'i2cget')
    ret = i2c_devices_scanner.execute_os_cmd('sudo i2cget -f -y 13 0x50 0x0')
    assert ret == False

'''
@patch('i2c_devices_scanner.platform_chassis', MagicMock())
@patch('i2c_devices_scanner._wrapper_platform_api_importer', MagicMock())
class TestI2CDevicesScanner:
    def test_i2c_faulty_devices_scan(self):
        i2c_devices_scanner.platform_chassis.get_all_i2c_region_list = MagicMock(
            return_value= {
                "77-2-72-2": [
                    {
                        "name": "Ethernet8",
                        "bus": "26",
                        "device_addr": "0x50",
                        "register_addr": "0x0"
                    }
                ]
            }
        )
        logger = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()

        # No i2c device hang
        task.i2c_device_checker = MagicMock(return_value=True)
        task.i2c_faulty_devices_scan()
        assert task.device_locked_list_dict == {}

        # Ethernet8 triggering i2c bus hang
        task.i2c_device_checker = MagicMock(return_value=False)
        task.i2c_faulty_devices_scan()
        assert len(task.device_locked_list_dict) == 1
        assert list(task.device_locked_list_dict.keys())[0] == '77-2-72-2'
        assert list(task.device_locked_list_dict.values())[0].get_name() == 'Ethernet8'

    def test_i2c_device_checker(self):
        i2c_devices_scanner.platform_chassis.get_all_i2c_region_list = MagicMock()
        logger = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()

        entity = i2c_device_entity.I2CDeviceEntity("Ethernet8", "26", "0x50", "0x0")
        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [True, True, True])
        ret = task.i2c_device_checker(entity)
        assert ret == True
        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [False, False, False])
        ret = task.i2c_device_checker(entity)
        assert ret == False
        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [False, True, True])
        ret = task.i2c_device_checker(entity)
        assert ret == True

    @patch('i2c_devices_scanner._wrapper_platform_api_importer', MagicMock())
    def test_reset_i2c_device_state(self):
        i2c_devices_scanner.platform_chassis.get_all_i2c_region_list = MagicMock()
        logger = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()

        data = i2c_device_entity.I2CDeviceEntity("Ethernet8", "26", "0x50", "0x0")
        task.device_locked_list_dict = {
            "77-2-72-2": data
        }
        task.reset_i2c_device_state(["77-2-72-2", data])
        assert "77-2-72-2" not in task.device_locked_list_dict

'''