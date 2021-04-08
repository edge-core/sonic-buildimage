import os
import sys
import swsssdk

from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock

from .test_vectors import HOSTCFGD_TEST_VECTOR
from .mock_configdb import MockConfigDb


swsssdk.ConfigDBConnector = MockConfigDb
test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, "scripts")
sys.path.insert(0, modules_path)

# Load the file under test
hostcfgd_path = os.path.join(scripts_path, 'hostcfgd')
hostcfgd = load_module_from_source('hostcfgd', hostcfgd_path)


class TestHostcfgd(TestCase):
    """
        Test hostcfd daemon - feature
    """
    def __verify_table(self, table, expected_table):
        """
            verify config db tables

            Compares Config DB table (FEATURE) with expected output table

            Args:
                table(dict): Current Config Db table
                expected_table(dict): Expected Config Db table

            Returns:
                None
        """
        is_equal = len(table) == len(expected_table)
        if is_equal:
            for key, fields in expected_table.items():
                is_equal = is_equal and key in table and len(fields) == len(table[key])
                if is_equal:
                    for field, value in fields.items():
                        is_equal = is_equal and value == table[key][field]
                        if not is_equal:
                            break;
                else:
                    break
        return is_equal

    @parameterized.expand(HOSTCFGD_TEST_VECTOR)
    def test_hostcfgd(self, test_name, test_data):
        """
            Test hostcfd daemon initialization

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """
        MockConfigDb.set_config_db(test_data["config_db"])
        with mock.patch("hostcfgd.subprocess") as mocked_subprocess:
            host_config_daemon = hostcfgd.HostConfigDaemon()
            host_config_daemon.update_all_feature_states()
            assert self.__verify_table(
                MockConfigDb.get_config_db()["FEATURE"],
                test_data["expected_config_db"]["FEATURE"]
            ), "Test failed for test data: {0}".format(test_data)
            mocked_subprocess.check_call.assert_has_calls(test_data["expected_subprocess_calls"], any_order=True)
