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
import i2c_isolation_list_updater

@patch('subprocess.check_output', MagicMock())
def test_execute_os_cmd():
    subprocess.check_output.return_value=1
    ret = i2c_devices_scanner.execute_os_cmd('sudo i2cget -f -y 13 0x50 0x0')
    assert ret == True

    subprocess.check_output.side_effect=subprocess.CalledProcessError(1,'i2cget')
    ret = i2c_devices_scanner.execute_os_cmd('sudo i2cget -f -y 13 0x50 0x0')
    assert ret == False


class TestI2CDevicesScanner:
    def test_get_all_i2c_region_list(self):
        with open(os.path.join(test_path,"mock_i2c_region_list.json"), "r") as f:
            mock_i2c_region_list = json.load(f)
        logger = MagicMock()
        i2c_bus_checker = MagicMock()
        i2c_platform_api = MagicMock()
        i2c_platform_api.get_all_i2c_region_list = MagicMock(return_value=mock_i2c_region_list)
        i2c_devices_scanner.i2c_isolation_list_updater.I2CIsolationListUpdater = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger, i2c_bus_checker, i2c_platform_api)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()
        parsed_list = task.get_all_i2c_region_list()
        assert len(parsed_list) == 5
        for region_id in parsed_list:
            for pdata,mdata in zip(parsed_list[region_id], mock_i2c_region_list[region_id]):
                assert pdata.get_name() == mdata["name"]
                assert pdata.get_bus() == mdata["bus"]
                assert pdata.get_device_addr() == mdata["device_addr"]
                assert pdata.get_register_addr() == mdata["register_addr"]

    def test_i2c_faulty_devices_scan(self):
        logger = MagicMock()
        i2c_bus_checker = MagicMock()
        i2c_platform_api = MagicMock()
        i2c_devices_scanner.i2c_isolation_list_updater.I2CIsolationListUpdater = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger, i2c_bus_checker, i2c_platform_api)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()
        task.i2c_region_list_dict = {
            "77-2-72-2": [i2c_device_entity.I2CDeviceEntity("Ethernet8", "26", "0x50", "0x0")]
        }

        # No I2C device is locked
        task.i2c_faulty_device_checker = MagicMock(return_value=False)
        task.i2c_faulty_devices_scan()
        assert task.device_locked_list == []

        # Ethernet8 triggering I2C bus locked
        task.i2c_faulty_device_checker = MagicMock(return_value=True)
        task.i2c_faulty_devices_scan()
        assert len(task.device_locked_list) == 1
        assert task.device_locked_list[0] == '77-2-72-2'

    def test_i2c_faulty_device_checker(self):
        logger = MagicMock()
        i2c_bus_checker = MagicMock()
        i2c_platform_api = MagicMock()
        i2c_devices_scanner.i2c_isolation_list_updater.I2CIsolationListUpdater = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger, i2c_bus_checker, i2c_platform_api)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()
        entity = i2c_device_entity.I2CDeviceEntity("Ethernet8", "26", "0x50", "0x0")

        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [True])
        task.i2c_bus_checker.is_bus_lock = MagicMock(return_value=False)
        ret = task.i2c_faulty_device_checker(entity)
        assert ret == False

        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [False, False, True])
        task.i2c_bus_checker.is_bus_lock = MagicMock(return_value=False)
        ret = task.i2c_faulty_device_checker(entity)
        assert ret == False

        i2c_devices_scanner.execute_os_cmd = MagicMock(side_effect = [False, False, False])
        task.i2c_bus_checker.is_bus_lock = MagicMock(return_value=True)
        ret = task.i2c_faulty_device_checker(entity)
        assert ret == True

    def test_reset_i2c_region(self):
        logger = MagicMock()
        i2c_bus_checker = MagicMock()
        i2c_platform_api = MagicMock()
        i2c_devices_scanner.i2c_isolation_list_updater.I2CIsolationListUpdater = MagicMock()
        task = i2c_devices_scanner.I2CDevicesScanner(logger, i2c_bus_checker, i2c_platform_api)
        task.insert_i2c_region_from_isolation_list = MagicMock()
        task.remove_i2c_region_from_isolation_list = MagicMock()

        data = i2c_device_entity.I2CDeviceEntity("Ethernet8", "26", "0x50", "0x0")
        task.device_locked_list = ["77-2-72-2"]
        task.i2c_region_list_dict = {
            "77-2-72-2": [data]
        }
        task.device_locked_list = ['77-2-72-2']
        task.reset_i2c_region("77-2-72-2")
        assert "77-2-72-2" not in task.device_locked_list