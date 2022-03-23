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
import os
import sys
if sys.version_info.major == 3:
    from unittest import mock
else:
    import mock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.sfp import SFP, SX_PORT_MODULE_STATUS_INITIALIZING, SX_PORT_MODULE_STATUS_PLUGGED, SX_PORT_MODULE_STATUS_UNPLUGGED, SX_PORT_MODULE_STATUS_PLUGGED_WITH_ERROR, SX_PORT_MODULE_STATUS_PLUGGED_DISABLED
from sonic_platform.chassis import Chassis

class TestSfp:
    @mock.patch('sonic_platform.device_data.DeviceDataManager.get_linecard_count', mock.MagicMock(return_value=8))
    @mock.patch('sonic_platform.device_data.DeviceDataManager.get_linecard_max_port_count')
    def test_sfp_index(self, mock_max_port):
        sfp = SFP(0)
        assert sfp.sdk_index == 0
        assert sfp.index == 1

        mock_max_port.return_value = 16
        sfp = SFP(sfp_index=0, slot_id=1, linecard_port_count=16, lc_name='LINE-CARD1')
        assert sfp.sdk_index == 0
        assert sfp.index == 1

        sfp = SFP(sfp_index=5, slot_id=3, linecard_port_count=16, lc_name='LINE-CARD1')
        assert sfp.sdk_index == 5
        assert sfp.index == 38

        sfp = SFP(sfp_index=1, slot_id=1, linecard_port_count=4, lc_name='LINE-CARD1')
        assert sfp.sdk_index == 1
        assert sfp.index == 5

    @mock.patch('sonic_platform.sfp.SFP.read_eeprom', mock.MagicMock(return_value=None))
    @mock.patch('sonic_platform.sfp.SFP._get_error_code')
    @mock.patch('sonic_platform.chassis.Chassis.get_num_sfps', mock.MagicMock(return_value=2))
    def test_sfp_get_error_status(self, mock_get_error_code):
        chassis = Chassis()

        # Fetch an SFP module to test
        sfp = chassis.get_sfp(1)

        description_dict = sfp._get_error_description_dict()
        for error in description_dict.keys():
            mock_get_error_code.return_value = (SX_PORT_MODULE_STATUS_PLUGGED_WITH_ERROR, error)
            description = sfp.get_error_description()

            assert description == description_dict[error]

        mock_get_error_code.return_value = (SX_PORT_MODULE_STATUS_PLUGGED_WITH_ERROR, -1)
        description = sfp.get_error_description()
        assert description == "Unknown error (-1)"

        expected_description_list = [
            (SX_PORT_MODULE_STATUS_INITIALIZING, "Initializing"),
            (SX_PORT_MODULE_STATUS_PLUGGED, "OK"),
            (SX_PORT_MODULE_STATUS_UNPLUGGED, "Unplugged"),
            (SX_PORT_MODULE_STATUS_PLUGGED_DISABLED, "Disabled")
        ]
        for oper_code, expected_description in expected_description_list:
            mock_get_error_code.return_value = (oper_code, -1)
            description = sfp.get_error_description()

            assert description == expected_description
