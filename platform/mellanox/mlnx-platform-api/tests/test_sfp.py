import os
import sys
import pytest
from mock import MagicMock
from .mock_platform import MockFan

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_py_common import device_info
from sonic_platform.sfp import SFP
from sonic_platform.chassis import Chassis


def mock_get_platform():
    return 'x86_64-mlnx_msn2410-r0'


def mock_read_eeprom_specific_bytes(self, offset, num_bytes):
    return None


def mock_get_sdk_handle(self):
    if not self.sdk_handle:
        self.sdk_handle = 1
    return self.sdk_handle

device_info.get_platform = mock_get_platform
SFP._read_eeprom_specific_bytes = mock_read_eeprom_specific_bytes
Chassis.get_sdk_handle = mock_get_sdk_handle


def test_sfp_partial_and_then_full_initialize():
    """
        Verify SFP initialization flow (partial and then full):
        1. get_sfp to tirgger a partial initialization
        2. get_sfp for another SPF module and verify the partial initialization isn't executed again
        3. get_all_sfps to trigger a full initialization
    """
    chassis = Chassis()

    # Fetch a sfp
    # This should trigger SFP modules be partial initialized
    sfp1 = chassis.get_sfp(1)
    # Verify the SFP list has been created
    assert len(chassis._sfp_list) == chassis.PORT_END + 1
    assert chassis.sfp_module_partial_initialized == True
    assert chassis.sfp_module_full_initialized == False

    # Fetch another SFP module
    sfp2 = chassis.get_sfp(2)
    # Verify the previous SFP module isn't changed
    assert sfp1 == chassis.get_sfp(1)

    # Fetch all SFP modules
    allsfp = chassis.get_all_sfps()
    # Verify sfp1 and sfp2 aren't changed
    assert sfp1 == chassis.get_sfp(1)
    assert sfp2 == chassis.get_sfp(2)
    # Verify the SFP has been fully initialized
    assert chassis.sfp_module_partial_initialized == True
    assert chassis.sfp_module_full_initialized == True


def test_sfp_full_initialize_without_partial():
    """
        Verify SFP initialization flow (full):
        1. get_all_sfps to trigger a full initialization
        2. get_sfp for a certain SFP module and verify the partial initialization isn't executed again
    """
    chassis = Chassis()

    # Fetch all SFP modules
    allsfp = chassis.get_all_sfps()
    # Verify the SFP has been fully initialized
    assert chassis.sfp_module_partial_initialized == True
    assert chassis.sfp_module_full_initialized == True
    for sfp in allsfp:
        assert sfp is not None

    # Verify when get_sfp is called, the SFP modules won't be initialized again
    sfp1 = allsfp[0]
    assert sfp1 == chassis.get_sfp(1)
