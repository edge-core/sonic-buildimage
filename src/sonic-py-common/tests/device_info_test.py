import os
import sys

# TODO: Remove this if/else block once we no longer support Python 2
if sys.version_info.major == 3:
    from unittest import mock
else:
    # Expect the 'mock' package for python 2
    # https://pypi.python.org/pypi/mock
    import mock

from sonic_py_common import device_info


# TODO: Remove this if/else block once we no longer support Python 2
if sys.version_info.major == 3:
    BUILTINS = "builtins"
else:
    BUILTINS = "__builtin__"

MACHINE_CONF_CONTENTS = """\
onie_version=2016.11-5.1.0008-9600
onie_vendor_id=33049
onie_machine_rev=0
onie_arch=x86_64
onie_config_version=1
onie_build_date="2017-04-26T11:01+0300"
onie_partition_type=gpt
onie_kernel_version=4.10.11
onie_firmware=auto
onie_switch_asic=mlnx
onie_skip_ethmgmt_macs=yes
onie_machine=mlnx_msn2700
onie_platform=x86_64-mlnx_msn2700-r0"""

EXPECTED_GET_MACHINE_INFO_RESULT = {
    'onie_arch': 'x86_64',
    'onie_skip_ethmgmt_macs': 'yes',
    'onie_platform': 'x86_64-mlnx_msn2700-r0',
    'onie_machine_rev': '0',
    'onie_version': '2016.11-5.1.0008-9600',
    'onie_machine': 'mlnx_msn2700',
    'onie_config_version': '1',
    'onie_partition_type': 'gpt',
    'onie_build_date': '"2017-04-26T11:01+0300"',
    'onie_switch_asic': 'mlnx',
    'onie_vendor_id': '33049',
    'onie_firmware': 'auto',
    'onie_kernel_version': '4.10.11'
}


class TestDeviceInfo(object):
    @classmethod
    def setup_class(cls):
        print("SETUP")

    def test_get_machine_info(self):
        with mock.patch("os.path.isfile") as mock_isfile:
            mock_isfile.return_value = True
            open_mocked = mock.mock_open(read_data=MACHINE_CONF_CONTENTS)
            with mock.patch("{}.open".format(BUILTINS), open_mocked):
                result = device_info.get_machine_info()
                assert result == EXPECTED_GET_MACHINE_INFO_RESULT
                open_mocked.assert_called_once_with("/host/machine.conf")

    def test_get_platform(self):
        with mock.patch("sonic_py_common.device_info.get_machine_info") as get_machine_info_mocked:
            get_machine_info_mocked.return_value = EXPECTED_GET_MACHINE_INFO_RESULT
            result = device_info.get_platform()
            assert result == "x86_64-mlnx_msn2700-r0"

    @classmethod
    def teardown_class(cls):
        print("TEARDOWN")
