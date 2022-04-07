import os
import sys
import swsscommon as swsscommon_package
from swsscommon import swsscommon

from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from unittest import TestCase, mock

from .test_vectors import HOSTCFGD_TEST_VECTOR, HOSTCFG_DAEMON_CFG_DB
from tests.common.mock_configdb import MockConfigDb, MockDBConnector

from pyfakefs.fake_filesystem_unittest import patchfs
from deepdiff import DeepDiff
from unittest.mock import call

test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, 'scripts')
sys.path.insert(0, modules_path)

# Load the file under test
hostcfgd_path = os.path.join(scripts_path, 'hostcfgd')
hostcfgd = load_module_from_source('hostcfgd', hostcfgd_path)
hostcfgd.ConfigDBConnector = MockConfigDb
hostcfgd.DBConnector = MockDBConnector
hostcfgd.Table = mock.Mock()


class TestHostcfgd(TestCase):
    """
        Test hostcfd daemon - feature
    """
    def __verify_table(self, table, feature_state_table, expected_table):
        """
            verify config db tables

            Compares Config DB table (FEATURE) with expected output table.
            Verifies that State DB table (FEATURE) is updated.

            Args:
                table(dict): Current Config Db table
                feature_state_table(Mock): Mocked State DB FEATURE table
                expected_table(dict): Expected Config Db table

            Returns:
                None
        """
        ddiff = DeepDiff(table, expected_table, ignore_order=True)
        print('DIFF:', ddiff)

        def get_state(cfg_state):
            """ Translates CONFIG DB state field into STATE DB state field """
            if cfg_state == 'always_disabled':
                return 'disabled'
            elif cfg_state == 'always_enabled':
                return 'enabled'
            else:
                return cfg_state

        feature_state_table.set.assert_has_calls([
            mock.call(feature, [('state', get_state(table[feature]['state']))]) for feature in table
        ])
        return True if not ddiff else False

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
            'enabled': 'always',
            'disabled': 'no',
        }
        auto_restart_conf = os.path.join(hostcfgd.FeatureHandler.SYSTEMD_SERVICE_CONF_DIR, 'auto_restart.conf')

        for feature in table:
            auto_restart = table[feature].get('auto_restart', 'disabled')
            with open(auto_restart_conf.format(feature)) as conf:
                conf = conf.read().strip()
            assert conf == '[Service]\nRestart={}'.format(exp_dict[auto_restart])


    @parameterized.expand(HOSTCFGD_TEST_VECTOR)
    @patchfs
    def test_hostcfgd_feature_handler(self, test_name, test_data, fs):
        """
            Test feature config capability in the hostcfd

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """
        fs.add_real_paths(swsscommon_package.__path__)  # add real path of swsscommon for database_config.json
        fs.create_dir(hostcfgd.FeatureHandler.SYSTEMD_SYSTEM_DIR)
        MockConfigDb.set_config_db(test_data['config_db'])
        feature_state_table_mock = mock.Mock()
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = test_data['popen_attributes']
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock

            # Initialize Feature Handler
            device_config = {}
            device_config['DEVICE_METADATA'] = MockConfigDb.CONFIG_DB['DEVICE_METADATA']
            feature_handler = hostcfgd.FeatureHandler(MockConfigDb(), feature_state_table_mock, device_config)

            # sync the state field and Handle Feature Updates
            features = MockConfigDb.CONFIG_DB['FEATURE']
            feature_handler.sync_state_field(features)
            for key, fvs in features.items():
                feature_handler.handle(key, 'SET', fvs)

            # Verify if the updates are properly updated
            assert self.__verify_table(
                MockConfigDb.get_config_db()['FEATURE'],
                feature_state_table_mock,
                test_data['expected_config_db']['FEATURE']
            ), 'Test failed for test data: {0}'.format(test_data)
            mocked_subprocess.check_call.assert_has_calls(test_data['expected_subprocess_calls'], any_order=True)

            self.__verify_fs(test_data['config_db']['FEATURE'])

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


class TesNtpCfgd(TestCase):
    """
        Test hostcfd daemon - NtpCfgd
    """
    def setUp(self):
        MockConfigDb.CONFIG_DB['NTP'] = {'global': {'vrf': 'mgmt', 'src_intf': 'eth0'}}
        MockConfigDb.CONFIG_DB['NTP_SERVER'] = {'0.debian.pool.ntp.org': {}}

    def tearDown(self):
        MockConfigDb.CONFIG_DB = {}

    def test_ntp_global_update_with_no_servers(self):
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock

            ntpcfgd = hostcfgd.NtpCfg()
            ntpcfgd.ntp_global_update('global', MockConfigDb.CONFIG_DB['NTP']['global'])

            mocked_subprocess.check_call.assert_not_called()

    def test_ntp_global_update_ntp_servers(self):
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock

            ntpcfgd = hostcfgd.NtpCfg()
            ntpcfgd.ntp_global_update('global', MockConfigDb.CONFIG_DB['NTP']['global'])
            ntpcfgd.ntp_server_update('0.debian.pool.ntp.org', 'SET')
            mocked_subprocess.check_call.assert_has_calls([call('systemctl restart ntp-config', shell=True)])

    def test_loopback_update(self):
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock

            ntpcfgd = hostcfgd.NtpCfg()
            ntpcfgd.ntp_global = MockConfigDb.CONFIG_DB['NTP']['global']
            ntpcfgd.ntp_servers.add('0.debian.pool.ntp.org')

            ntpcfgd.handle_ntp_source_intf_chg('eth0')
            mocked_subprocess.check_call.assert_has_calls([call('systemctl restart ntp-config', shell=True)])


class TestHostcfgdDaemon(TestCase):

    def setUp(self):
        MockConfigDb.set_config_db(HOSTCFG_DAEMON_CFG_DB)

    def tearDown(self):
        MockConfigDb.CONFIG_DB = {}

    @patchfs
    def test_feature_events(self, fs):
        fs.create_dir(hostcfgd.FeatureHandler.SYSTEMD_SYSTEM_DIR)
        MockConfigDb.event_queue = [('FEATURE', 'dhcp_relay'),
                                ('FEATURE', 'mux'),
                                ('FEATURE', 'telemetry')]
        daemon = hostcfgd.HostConfigDaemon()
        daemon.register_callbacks()
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock
            try:
                daemon.start()
            except TimeoutError:
                pass
            expected = [call('sudo systemctl daemon-reload', shell=True),
                        call('sudo systemctl unmask dhcp_relay.service', shell=True),
                        call('sudo systemctl enable dhcp_relay.service', shell=True),
                        call('sudo systemctl start dhcp_relay.service', shell=True),
                        call('sudo systemctl daemon-reload', shell=True),
                        call('sudo systemctl unmask mux.service', shell=True),
                        call('sudo systemctl enable mux.service', shell=True),
                        call('sudo systemctl start mux.service', shell=True),
                        call('sudo systemctl daemon-reload', shell=True),
                        call('sudo systemctl unmask telemetry.service', shell=True),
                        call('sudo systemctl unmask telemetry.timer', shell=True),
                        call('sudo systemctl enable telemetry.timer', shell=True),
                        call('sudo systemctl start telemetry.timer', shell=True)]
            mocked_subprocess.check_call.assert_has_calls(expected)

            # Change the state to disabled
            MockConfigDb.CONFIG_DB['FEATURE']['telemetry']['state'] = 'disabled'
            MockConfigDb.event_queue = [('FEATURE', 'telemetry')]
            try:
                daemon.start()
            except TimeoutError:
                pass
            expected = [call('sudo systemctl stop telemetry.timer', shell=True),
                        call('sudo systemctl disable telemetry.timer', shell=True),
                        call('sudo systemctl mask telemetry.timer', shell=True),
                        call('sudo systemctl stop telemetry.service', shell=True),
                        call('sudo systemctl disable telemetry.timer', shell=True),
                        call('sudo systemctl mask telemetry.timer', shell=True)]
            mocked_subprocess.check_call.assert_has_calls(expected)

    def test_loopback_events(self):
        MockConfigDb.set_config_db(HOSTCFG_DAEMON_CFG_DB)
        MockConfigDb.event_queue = [('NTP', 'global'),
                                  ('NTP_SERVER', '0.debian.pool.ntp.org'),
                                  ('LOOPBACK_INTERFACE', 'Loopback0|10.184.8.233/32')]
        daemon = hostcfgd.HostConfigDaemon()
        daemon.register_callbacks()
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock
            try:
                daemon.start()
            except TimeoutError:
                pass
            expected = [call('systemctl restart ntp-config', shell=True),
            call('iptables -t mangle --append PREROUTING -p tcp --tcp-flags SYN SYN -d 10.184.8.233 -j TCPMSS --set-mss 1460', shell=True),
            call('iptables -t mangle --append POSTROUTING -p tcp --tcp-flags SYN SYN -s 10.184.8.233 -j TCPMSS --set-mss 1460', shell=True)]
            mocked_subprocess.check_call.assert_has_calls(expected, any_order=True)

    def test_kdump_event(self):
        MockConfigDb.set_config_db(HOSTCFG_DAEMON_CFG_DB)
        daemon = hostcfgd.HostConfigDaemon()
        daemon.register_callbacks()
        MockConfigDb.event_queue = [('KDUMP', 'config')]
        with mock.patch('hostcfgd.subprocess') as mocked_subprocess:
            popen_mock = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            popen_mock.configure_mock(**attrs)
            mocked_subprocess.Popen.return_value = popen_mock
            try:
                daemon.start()
            except TimeoutError:
                pass
            expected = [call('sonic-kdump-config --disable', shell=True),
                        call('sonic-kdump-config --num_dumps 3', shell=True),
                        call('sonic-kdump-config --memory 0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M', shell=True)]
            mocked_subprocess.check_call.assert_has_calls(expected, any_order=True)
