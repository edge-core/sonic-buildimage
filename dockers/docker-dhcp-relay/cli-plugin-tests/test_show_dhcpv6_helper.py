import pytest
import sys
import os
sys.path.append('../cli/show/plugins/')
import show_dhcp_relay as show
from click.testing import CliRunner
from swsscommon import swsscommon
from mock_config import TEST_DATA
from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import patchfs

try:
    sys.path.insert(0, '../../../src/sonic-host-services/tests/common')
    from mock_configdb import MockConfigDb
    swsscommon.ConfigDBConnector = MockConfigDb 
except KeyError:
    pass
    
expected_table = """\
--------  ------------
Vlan1000  fc02:2000::1
          fc02:2000::2
--------  ------------
"""

DBCONFIG_PATH = '/var/run/redis/sonic-db/database_config.json'

class TestDhcpRelayHelper(object):

    @parameterized.expand(TEST_DATA)
    @patchfs
    def test_show_dhcpv6_helper(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) 
        MockConfigDb.set_config_db(test_data["config_db"])
        runner = CliRunner()
        config_db = MockConfigDb()
        table = config_db.get_table("DHCP_RELAY")
        result = show.get_data(table, "Vlan1000")
        assert result == expected_table

