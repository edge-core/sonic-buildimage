import os
import sys

from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock

class TestCaclmgrdNamespaceDockerIP(TestCase):
    """
        Test caclmgrd Namespace docker management IP
    """
    def setUp(self):
        test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        modules_path = os.path.dirname(test_path)
        scripts_path = os.path.join(modules_path, "scripts")
        sys.path.insert(0, modules_path)
        caclmgrd_path = os.path.join(scripts_path, 'caclmgrd')
        self.caclmgrd = load_module_from_source('caclmgrd', caclmgrd_path)
        self.maxDiff = None

    def test_caclmgrd_namespace_docker_ip(self):
        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ip = mock.MagicMock(return_value=[])
        self.caclmgrd.ControlPlaneAclManager.get_namespace_mgmt_ipv6 = mock.MagicMock(return_value=[])
        with mock.patch('sonic_py_common.multi_asic.get_all_namespaces',
                return_value={'front_ns': ['asic0'], 'back_ns': ['asic1'], 'fabric_ns': ['asic2']}):
            caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")
            self.assertTrue('asic0' in caclmgrd_daemon.namespace_docker_mgmt_ip)
            self.assertTrue('asic1' in caclmgrd_daemon.namespace_docker_mgmt_ip)
            self.assertTrue('asic2' in caclmgrd_daemon.namespace_docker_mgmt_ip)
            self.assertListEqual(caclmgrd_daemon.namespace_docker_mgmt_ip['asic0'], [])
