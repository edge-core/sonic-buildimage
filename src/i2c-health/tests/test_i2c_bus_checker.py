import os
import sys
import pytest
import logging
from mock import MagicMock, patch


if sys.version_info >= (3, 3):
    from unittest.mock import MagicMock, patch
else:
    from mock import MagicMock, patch


test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
util_path = os.path.join(modules_path, "i2c_health_mgr")
sys.path.insert(0, modules_path)
sys.path.insert(0, util_path)

from i2c_bus_checker import I2CBusChecker


@pytest.fixture
def mock_logger():
    return MagicMock()

@patch('i2c_bus_checker.subprocess.run')
@patch('i2c_bus_checker.I2CPlatformAPI')
def test_is_bus_lock_no(mock_platform_api, mock_subprocess_run, mock_logger):
    mock_platform_api.return_value.get_i2c_representative_dev_list.return_value = [
        {"name": "Device1", "bus": "12", "device_addr": "0x48", "register_addr": "0x00"},
        {"name": "Device2", "bus": "14", "device_addr": "0x1F", "register_addr": "0x00"}
    ]

    mock_subprocess_run.return_value.returncode = 0
    i2c_checker = I2CBusChecker(mock_logger)
    result = i2c_checker.is_bus_lock()

    assert result is False
    mock_logger.info.assert_called()

@patch('i2c_bus_checker.subprocess.run')
@patch('i2c_bus_checker.I2CPlatformAPI')
def test_is_bus_lock_yes(mock_platform_api, mock_subprocess_run, mock_logger):
    mock_platform_api.return_value.get_i2c_representative_dev_list.return_value = [
        {"name": "Device1", "bus": "12", "device_addr": "0x48", "register_addr": "0x00"},
        {"name": "Device2", "bus": "14", "device_addr": "0x1F", "register_addr": "0x00"}
    ]

    mock_subprocess_run.return_value.returncode = 1
    i2c_checker = I2CBusChecker(mock_logger)
    result = i2c_checker.is_bus_lock()

    assert result is True
    mock_logger.warning.assert_called_with('I2C bus lock!')

@patch('i2c_bus_checker.I2CPlatformAPI')
def test_i2c_representative_list_get(mock_platform_api, mock_logger):
    mock_platform_api.return_value.get_i2c_representative_dev_list.return_value = [
        {"name": "Device1", "bus": "12", "device_addr": "0x48", "register_addr": "0x00"},
        {"name": "Device2", "bus": "14", "device_addr": "0x1F", "register_addr": "0x00"}
    ]

    i2c_checker = I2CBusChecker(mock_logger)

    result = i2c_checker.i2c_representative_list_get()

    expected_result = [
        {"name": "Device1", "bus": "12", "device_addr": "0x48", "register_addr": "0x00"},
        {"name": "Device2", "bus": "14", "device_addr": "0x1F", "register_addr": "0x00"}
    ]

    assert result == expected_result

