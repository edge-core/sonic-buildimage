import importlib.machinery
import importlib.util
import filecmp
import shutil
import os
import sys
import subprocess
import re

from parameterized import parameterized
from unittest import TestCase, mock
from tests.hostcfgd.test_passwh_vectors import HOSTCFGD_TEST_PASSWH_VECTOR
from tests.common.mock_configdb import MockConfigDb, MockDBConnector

test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, "scripts")
src_path = os.path.dirname(modules_path)
templates_path = os.path.join(src_path, "sonic-host-services-data/templates")
output_path = os.path.join(test_path, "hostcfgd/output")
sample_output_path = os.path.join(test_path, "hostcfgd/sample_output")
sys.path.insert(0, modules_path)

# Load the file under test
hostcfgd_path = os.path.join(scripts_path, 'hostcfgd')
loader = importlib.machinery.SourceFileLoader('hostcfgd', hostcfgd_path)
spec = importlib.util.spec_from_loader(loader.name, loader)
hostcfgd = importlib.util.module_from_spec(spec)
loader.exec_module(hostcfgd)
sys.modules['hostcfgd'] = hostcfgd

# Mock swsscommon classes
hostcfgd.ConfigDBConnector = MockConfigDb
hostcfgd.DBConnector = MockDBConnector
hostcfgd.Table = mock.Mock()

AGE_DICT = { 'MAX_DAYS': {'REGEX_DAYS': r'^PASS_MAX_DAYS[ \t]*(?P<max_days>\d*)', 'DAYS': 'max_days', 'CHAGE_FLAG': '-M '},
            'WARN_DAYS': {'REGEX_DAYS': r'^PASS_WARN_AGE[ \t]*(?P<warn_days>\d*)', 'DAYS': 'warn_days', 'CHAGE_FLAG': '-W '}
            }

class TestHostcfgdPASSWH(TestCase):
    """
        Test hostcfd daemon - PASSWH
    """
    def run_diff(self, file1, file2):
        try:
            diff_out = subprocess.check_output('diff -ur {} {} || true'.format(file1, file2), shell=True)
            return diff_out
        except subprocess.CalledProcessError as err:
            syslog.syslog(syslog.LOG_ERR, "{} - failed: return code - {}, output:\n{}".format(err.cmd, err.returncode, err.output))
            return -1

    def get_passw_days(self, login_file, age_type):
        days_num = -1

        regex_days = AGE_DICT[age_type]['REGEX_DAYS']
        days_type = AGE_DICT[age_type]['DAYS']

        with open(login_file, 'r') as f:
            login_def_data = f.readlines()

        for line in login_def_data:
            m1 = re.match(regex_days, line)
            if m1:
                days_num = int(m1.group(days_type))
                break
        return days_num

    """
        Check different config
    """
    def check_config(self, test_name, test_data, config_name):
        t_path = templates_path
        op_path = output_path + "/" + test_name + "_" + config_name
        sop_path = sample_output_path + "/" +  test_name + "_" + config_name
        sop_path_common = sample_output_path + "/" +  test_name

        hostcfgd.PAM_PASSWORD_CONF_TEMPLATE = t_path + "/common-password.j2"
        hostcfgd.PAM_AUTH_CONF_TEMPLATE = t_path + "/common-auth-sonic.j2"
        hostcfgd.NSS_TACPLUS_CONF_TEMPLATE = t_path + "/tacplus_nss.conf.j2"
        hostcfgd.NSS_RADIUS_CONF_TEMPLATE = t_path + "/radius_nss.conf.j2"
        hostcfgd.PAM_RADIUS_AUTH_CONF_TEMPLATE = t_path + "/pam_radius_auth.conf.j2"
        hostcfgd.PAM_PASSWORD_CONF = op_path + "/common-password"
        hostcfgd.ETC_LOGIN_DEF = op_path + "/login.defs"
        hostcfgd.PAM_AUTH_CONF = op_path + "/common-auth-sonic"
        hostcfgd.NSS_TACPLUS_CONF = op_path + "/tacplus_nss.conf"
        hostcfgd.NSS_RADIUS_CONF = op_path + "/radius_nss.conf"
        hostcfgd.NSS_CONF = op_path + "/nsswitch.conf"
        hostcfgd.ETC_PAMD_SSHD = op_path + "/sshd"
        hostcfgd.ETC_PAMD_LOGIN = op_path + "/login"
        hostcfgd.RADIUS_PAM_AUTH_CONF_DIR = op_path + "/"

        shutil.rmtree(op_path, ignore_errors=True)
        os.mkdir(op_path)

        shutil.copyfile(sop_path_common + "/login.defs.old", op_path + "/login.defs")
        MockConfigDb.set_config_db(test_data[config_name])
        host_config_daemon = hostcfgd.HostConfigDaemon()

        try:
            passwh_table = host_config_daemon.config_db.get_table('PASSW_HARDENING')
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, "failed: get_table 'PASSW_HARDENING', exception={}".format(e))
            passwh_table = []

        host_config_daemon.passwcfg.load(passwh_table)


        diff_output = ""
        files_to_compare = ['common-password']

        # check output files exists
        for name in files_to_compare:
            if not os.path.isfile(sop_path + "/" + name):
                raise ValueError('filename: %s not exit' % (sop_path + "/" + name))
            if not os.path.isfile(op_path + "/" + name):
                raise ValueError('filename: %s not exit' % (op_path + "/" + name))

        # deep comparison
        match, mismatch, errors = filecmp.cmpfiles(sop_path, op_path, files_to_compare, shallow=False)

        if not match:
            for name in files_to_compare:
                diff_output += self.run_diff( sop_path + "/" + name,\
                    op_path + "/" + name).decode('utf-8')

        self.assertTrue(len(diff_output) == 0, diff_output)

        # compare age data in login.def file.
        out_passw_age_days = self.get_passw_days(op_path + "/login.defs", 'MAX_DAYS')
        sout_passw_age_days = self.get_passw_days(sop_path + "/login.defs", 'MAX_DAYS')
        out_passw_age_warn_days = self.get_passw_days(op_path + "/login.defs", 'WARN_DAYS')
        sout_passw_age_warn_days = self.get_passw_days(sop_path + "/login.defs", 'WARN_DAYS')

        self.assertEqual(out_passw_age_days, sout_passw_age_days)
        self.assertEqual(out_passw_age_warn_days, sout_passw_age_warn_days)

    @parameterized.expand(HOSTCFGD_TEST_PASSWH_VECTOR)
    def test_hostcfgd_passwh(self, test_name, test_data):
        """
            Test PASSWH hostcfd daemon initialization

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """

        self.check_config(test_name, test_data, "default_values")

    @parameterized.expand(HOSTCFGD_TEST_PASSWH_VECTOR)
    def test_hostcfgd_passwh_enable(self, test_name, test_data):
        """
            Test PASSWH hostcfd daemon initialization

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """

        self.check_config(test_name, test_data, "enable_feature")


    @parameterized.expand(HOSTCFGD_TEST_PASSWH_VECTOR)
    def test_hostcfgd_passwh_classes(self, test_name, test_data):
        """
            Test PASSWH hostcfd daemon initialization

            Args:
                test_name(str): test name
                test_data(dict): test data which contains initial Config Db tables, and expected results

            Returns:
                None
        """

        self.check_config(test_name, test_data, "enable_digits_class")