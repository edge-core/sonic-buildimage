import os
import sys

from swsscommon import swsscommon
from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock
from pyfakefs.fake_filesystem_unittest import patchfs

from .test_external_client_acl_vectors import EXTERNAL_CLIENT_ACL_TEST_VECTOR
from tests.common.mock_configdb import MockConfigDb


DBCONFIG_PATH = '/var/run/redis/sonic-db/database_config.json'


class TestCaclmgrdExternalClientAcl(TestCase):
    """
        Test caclmgrd EXTERNAL_CLIENT_ACL
    """
    def setUp(self):
        swsscommon.ConfigDBConnector = MockConfigDb
        test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        modules_path = os.path.dirname(test_path)
        scripts_path = os.path.join(modules_path, "scripts")
        sys.path.insert(0, modules_path)
        caclmgrd_path = os.path.join(scripts_path, 'caclmgrd')
        self.caclmgrd = load_module_from_source('caclmgrd', caclmgrd_path)

    @parameterized.expand(EXTERNAL_CLIENT_ACL_TEST_VECTOR)
    @patchfs
    def test_caclmgrd_external_client_acl(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        MockConfigDb.set_config_db(test_data["config_db"])
        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ip = mock.MagicMock()
        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ipv6 = mock.MagicMock()
        self.caclmgrd.ControlPlaneAclManager.generate_block_ip2me_traffic_iptables_commands = mock.MagicMock(return_value=[])
        self.caclmgrd.ControlPlaneAclManager.get_chain_list = mock.MagicMock(return_value=["INPUT", "FORWARD", "OUTPUT"])
        caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")

        iptables_rules_ret, _ = caclmgrd_daemon.get_acl_rules_and_translate_to_iptables_commands('')
        self.assertEqual(set(test_data["return"]).issubset(set(iptables_rules_ret)), True)
