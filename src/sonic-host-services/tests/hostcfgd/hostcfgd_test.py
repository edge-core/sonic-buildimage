import os
import sys
import swsssdk

from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock

from .test_vectors import HOSTCFGD_TEST_VECTOR
from .mock_configdb import MockConfigDb

from pyfakefs.fake_filesystem_unittest import patchfs


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

    def __verify_fs(self, table):
        """
            verify filesystem changes made by hostcfgd.

            Checks whether systemd override configuration files
            were generated and Restart= for systemd unit is set
            correctly

            Args:
                table(dict): Current Config Db table

            Returns: Boolean wether test passed.
        """

        exp_dict = {
            "enabled": "always",
            "disabled": "no",
        }
        auto_restart_conf = os.path.join(hostcfgd.FeatureHandler.SYSTEMD_SERVICE_CONF_DIR, "auto_restart.conf")

        for feature in table:
            auto_restart = table[feature].get("auto_restart", "disabled")
            with open(auto_restart_conf.format(feature)) as conf:
                conf = conf.read().strip()
            assert conf == "[Service]\nRestart={}".format(exp_dict[auto_restart])


    @parameterized.expand(HOSTCFGD_TEST_VECTOR)
    @patchfs
    def test_hostcfgd(self, test_name, test_data, fs):
        """
            Test hostcfd daemon initialization

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """
        fs.add_real_paths(swsssdk.__path__)  # add real path of swsssdk for database_config.json
        fs.create_dir(hostcfgd.FeatureHandler.SYSTEMD_SYSTEM_DIR)
        MockConfigDb.set_config_db(test_data["config_db"])
        with mock.patch("hostcfgd.subprocess") as mocked_subprocess:
            host_config_daemon = hostcfgd.HostConfigDaemon()
            host_config_daemon.feature_handler.update_all_features_config()
            assert self.__verify_table(
                MockConfigDb.get_config_db()["FEATURE"],
                test_data["expected_config_db"]["FEATURE"]
            ), "Test failed for test data: {0}".format(test_data)
            mocked_subprocess.check_call.assert_has_calls(test_data["expected_subprocess_calls"], any_order=True)

            self.__verify_fs(test_data["config_db"]["FEATURE"])

    def test_feature_config_parsing(self):
        swss_feature = hostcfgd.Feature('swss', {
            'state': 'enabled',
            'auto_restart': 'enabled',
            'has_timer': 'True',
            'has_global_scope': 'False',
            'has_per_asic_scope': 'True',
        })

        assert swss_feature.name == 'swss'
        assert swss_feature.state == 'enabled'
        assert swss_feature.auto_restart == 'enabled'
        assert swss_feature.has_timer
        assert not swss_feature.has_global_scope
        assert swss_feature.has_per_asic_scope

    def test_feature_config_parsing_defaults(self):
        swss_feature = hostcfgd.Feature('swss', {
            'state': 'enabled',
        })

        assert swss_feature.name == 'swss'
        assert swss_feature.state == 'enabled'
        assert swss_feature.auto_restart == 'disabled'
        assert not swss_feature.has_timer
        assert swss_feature.has_global_scope
        assert not swss_feature.has_per_asic_scope
