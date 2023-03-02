import os
import sys

from swsscommon import swsscommon
from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock
from pyfakefs.fake_filesystem_unittest import patchfs

from .test_chassis_midplane_vectors import CACLMGRD_CHASSIS_MIDPLANE_TEST_VECTOR
from tests.common.mock_configdb import MockConfigDb


DBCONFIG_PATH = '/var/run/redis/sonic-db/database_config.json'


class TestCaclmgrdChassisMidplane(TestCase):
    """
        Test caclmgrd Chassis Midplane
    """
    def setUp(self):
        swsscommon.ConfigDBConnector = MockConfigDb
        test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        modules_path = os.path.dirname(test_path)
        scripts_path = os.path.join(modules_path, "scripts")
        sys.path.insert(0, modules_path)
        caclmgrd_path = os.path.join(scripts_path, 'caclmgrd')
        self.caclmgrd = load_module_from_source('caclmgrd', caclmgrd_path)
        self.maxDiff = None

    @parameterized.expand(CACLMGRD_CHASSIS_MIDPLANE_TEST_VECTOR)
    @patchfs
    def test_caclmgrd_chassis_midplane(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ip = mock.MagicMock()
        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ipv6 = mock.MagicMock()
        self.caclmgrd.ControlPlaneAclManager.check_chassis_midplane_interface_exist = mock.MagicMock(return_value=True)
        caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")
        ret = caclmgrd_daemon.generate_allow_internal_chasis_midplane_traffic('')
        self.assertListEqual(test_data["return"], ret)
