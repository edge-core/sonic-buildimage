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

from mock import MagicMock, patch

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform_base.sfp_base import SfpBase

class TestSfpEvent(object):
    @classmethod
    def setup_class(cls):
        os.environ["MLNX_PLATFORM_API_UNIT_TESTING"] = "1"

    @patch('select.select', MagicMock(return_value=([99], None, None)))
    def test_check_sfp_status(self):
        from sonic_platform.sfp_event import SDK_SFP_STATE_IN, SDK_SFP_STATE_OUT, SDK_SFP_STATE_ERR
        from sonic_platform.sfp_event import SDK_ERRORS_TO_ERROR_BITS, SDK_ERRORS_TO_DESCRIPTION, SDK_SFP_BLOCKING_ERRORS

        self.executor(SDK_SFP_STATE_IN, None, SfpBase.SFP_STATUS_BIT_INSERTED)
        self.executor(SDK_SFP_STATE_OUT, None, SfpBase.SFP_STATUS_BIT_REMOVED)
        for error_type, error_status in SDK_ERRORS_TO_ERROR_BITS.items():
            description = SDK_ERRORS_TO_DESCRIPTION.get(error_type)
            if error_type in SDK_SFP_BLOCKING_ERRORS:
                error_status |= SfpBase.SFP_ERROR_BIT_BLOCKING
            error_status |= SfpBase.SFP_STATUS_BIT_INSERTED
            self.executor(SDK_SFP_STATE_ERR, error_type, error_status, description)

    def executor(self, mock_module_state, mock_error_type, expect_status, description=None):
        from sonic_platform.sfp_event import sfp_event

        event = sfp_event()
        event.on_pmpe = MagicMock(return_value=(True, [0,1], mock_module_state, mock_error_type))
        port_change = {}
        error_dict = {}
        found = event.check_sfp_status(port_change, error_dict, 0)
        assert found
        expect_status_str = str(expect_status)
        assert 1 in port_change and port_change[1] == expect_status_str
        assert 2 in port_change and port_change[2] == expect_status_str
        if description:
            assert 1 in error_dict and error_dict[1] == description
            assert 2 in error_dict and error_dict[2] == description
