import os
import sys
import traceback
from unittest import mock

from click.testing import CliRunner

import show.vlan as vlan
from utilities_common.db import Db

sys.path.insert(0, '../cli/show/plugins/')
import show_dhcp_relay


class TestVlanDhcpRelay(object):
    def test_plugin_registration(self):
        cli = mock.MagicMock()
        show_dhcp_relay.register(cli)
        assert 'DHCP Helper Address' in dict(vlan.VlanBrief.COLUMNS)

    def test_dhcp_relay_column_output(self):
        ctx = (
            ({'Vlan100': {'dhcp_servers': ['192.0.0.1', '192.168.0.2']}}, {}, {}),
            (),
        )
        assert show_dhcp_relay.get_dhcp_helper_address(ctx, 'Vlan100') == '192.0.0.1\n192.168.0.2'


