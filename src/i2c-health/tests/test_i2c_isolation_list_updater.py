import pytest
import unittest
import sys
from i2c_health_mgr.i2c_isolation_list_updater import I2CIsolationListUpdater
from i2c_health_mgr.i2c_device_entity import I2CDeviceEntity

# TODO: Remove this if/else block once we no longer support Python 2
if sys.version_info.major == 3:
    from unittest import mock
else:
    # Expect the 'mock' package for python 2
    # https://pypi.python.org/pypi/mock
    import mock

from .mock_swsscommon import SonicV2Connector

class TestI2CBusHelper(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("i2c_health_mgr.i2c_isolation_list_updater.SonicV2Connector", new=SonicV2Connector)
        self.addCleanup(patcher.stop)
        self.mock_connector = patcher.start()

        self.mock_dbconnector = mock.Mock()
        self.i2c_isolation_list_updater = I2CIsolationListUpdater()

    def test_add_and_remove_single_device(self):
        mock_single_device = [I2CDeviceEntity("PSU_1", "1", "0x50", "0x00")]

        expect_result_add_single_device = {
            "I2C_ISOLATION_LIST|1|1-0050": {
                "device_name": "PSU_1"
            }
        }

        self.i2c_isolation_list_updater.add_device_into_isolation_list(1, mock_single_device)
        for key in expect_result_add_single_device.keys():
            for field, value in expect_result_add_single_device[key].items():
                assert value == self.i2c_isolation_list_updater.state_db.get(self.i2c_isolation_list_updater.state_db.STATE_DB, key, field)

        self.i2c_isolation_list_updater.remove_device_from_isolation_list(1, mock_single_device)
        for key in expect_result_add_single_device.keys():
            for field, value in expect_result_add_single_device[key].items():
                assert 'N/A' == self.i2c_isolation_list_updater.state_db.get(self.i2c_isolation_list_updater.state_db.STATE_DB, key, field)

    def test_add_and_remove_multiple_devices(self):
        mock_multiple_devices = [I2CDeviceEntity("PSU_1", "1", "0x50", "0x00"), I2CDeviceEntity("PSU_2", "2", "0x50", "0x00")]

        expect_result_add_multiple_devices = {
            "I2C_ISOLATION_LIST|1|1-0050": {
                "device_name": "PSU_1"
            },
            "I2C_ISOLATION_LIST|1|2-0050": {
                "device_name": "PSU_2"
            }
        }

        self.i2c_isolation_list_updater.add_device_into_isolation_list(1, mock_multiple_devices)
        for key in expect_result_add_multiple_devices.keys():
            for field, value in expect_result_add_multiple_devices[key].items():
                assert value == self.i2c_isolation_list_updater.state_db.get(self.i2c_isolation_list_updater.state_db.STATE_DB, key, field)

        self.i2c_isolation_list_updater.remove_device_from_isolation_list(1, mock_multiple_devices)
        for key in expect_result_add_multiple_devices.keys():
            for field, value in expect_result_add_multiple_devices[key].items():
                assert 'N/A' == self.i2c_isolation_list_updater.state_db.get(self.i2c_isolation_list_updater.state_db.STATE_DB, key, field)