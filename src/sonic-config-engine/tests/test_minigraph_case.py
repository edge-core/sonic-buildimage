import os
import subprocess
import ipaddr as ipaddress

import tests.common_utils as utils

from unittest import TestCase
import minigraph

class TestCfgGenCaseInsensitive(TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.sample_graph = os.path.join(self.test_dir, 'simple-sample-graph-case.xml')
        self.sample_resource_graph = os.path.join(self.test_dir, 'sample-graph-resource-type.xml')
        self.sample_subintf_graph = os.path.join(self.test_dir, 'sample-graph-subintf.xml')
        self.sample_simple_device_desc = os.path.join(self.test_dir, 'simple-sample-device-desc.xml')
        self.sample_simple_device_desc_ipv6_only = os.path.join(self.test_dir, 'simple-sample-device-desc-ipv6-only.xml')
        self.port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')

    def run_script(self, argument, check_stderr=False):
        print '\n    Running sonic-cfggen ' + argument
        if check_stderr:
            output = subprocess.check_output(self.script_file + ' ' + argument, stderr=subprocess.STDOUT, shell=True)
        else:
            output = subprocess.check_output(self.script_file + ' ' + argument, shell=True)

        linecount = output.strip().count('\n')
        if linecount <= 0:
            print '    Output: ' + output.strip()
        else:
            print '    Output: ({0} lines, {1} bytes)'.format(linecount + 1, len(output))
        return output

    def test_dummy_run(self):
        argument = ''
        output = self.run_script(argument)
        self.assertEqual(output, '')

    def test_minigraph_sku(self):
        argument = '-v "DEVICE_METADATA[\'localhost\'][\'hwsku\']" -m "' + self.sample_graph + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'Force10-S6000')

    def test_print_data(self):
        argument = '-m "' + self.sample_graph + '" --print-data'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)

    def test_jinja_expression(self):
        argument = '-m "' + self.sample_graph + '" -v "DEVICE_METADATA[\'localhost\'][\'type\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'ToRRouter')

    def test_additional_json_data(self):
        argument = '-a \'{"key1":"value1"}\' -v key1'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1')

    def test_read_yaml(self):
        argument = '-v yml_item -y ' + os.path.join(self.test_dir, 'test.yml')
        output = self.run_script(argument)
        self.assertEqual(output.strip(), '[\'value1\', \'value2\']')

    def test_render_template(self):
        argument = '-y ' + os.path.join(self.test_dir, 'test.yml') + ' -t ' + os.path.join(self.test_dir, 'test.j2')
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1\nvalue2')

#     everflow portion is not used
#     def test_minigraph_everflow(self):
#         argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v MIRROR_SESSION'
#         output = self.run_script(argument)
#         self.assertEqual(output.strip(), "{'everflow0': {'src_ip': '10.1.0.32', 'dst_ip': '10.0.100.1'}}")

    def test_minigraph_interfaces(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v \'INTERFACE.keys()\''
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Ethernet0', '10.0.0.58/31'), 'Ethernet0', ('Ethernet0', 'FC00::75/126')]")

    def test_minigraph_vlans(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v VLAN'
        output = self.run_script(argument)
        expected = {
            'Vlan1000': {
                'alias': 'ab1',
                'dhcp_servers': [
                    '192.0.0.1',
                    '192.0.0.2'
                    ],
                'dhcpv6_servers': [
                    'fc02:2000::1',
                    'fc02:2000::2'
                    ],
                'vlanid': '1000',
                'members': ['Ethernet8']
                },
            'Vlan2000': {
                'alias': 'ab2',
                'dhcp_servers': [
                    '192.0.0.3',
                    '192.0.0.4'],
                'members': ['Ethernet4'],
                'dhcpv6_servers': [
                    'fc02:2000::3',
                    'fc02:2000::4'],
                'vlanid': '2000'
                }
            }

        self.assertEqual(
            utils.to_dict(output.strip()),
            expected
        )

    def test_minigraph_vlan_members(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v VLAN_MEMBER'
        output = self.run_script(argument)
        expected = {
                       'Vlan1000|Ethernet8': {'tagging_mode': 'untagged'},
                       'Vlan2000|Ethernet4': {'tagging_mode': 'untagged'}
                   }
        self.assertEqual(
                utils.to_dict(output.strip()),
                expected
        )

    def test_minigraph_vlan_interfaces(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "VLAN_INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Vlan1000', '192.168.0.1/27'), 'Vlan1000']")

    def test_minigraph_portchannels(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v PORTCHANNEL'
        output = self.run_script(argument)
        self.assertEqual(
            utils.to_dict(output.strip()),
            utils.to_dict("{'PortChannel01': {'admin_status': 'up', 'min_links': '1', 'members': ['Ethernet4'], 'mtu': '9100'}}")
        )

    def test_minigraph_console_port(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v CONSOLE_PORT'
        output = self.run_script(argument)
        self.assertEqual(
            utils.to_dict(output.strip()),
            utils.to_dict("{'1': {'baud_rate': '9600', 'remote_device': 'managed_device', 'flow_control': 1}}"))

    def test_minigraph_deployment_id(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "DEVICE_METADATA[\'localhost\'][\'deployment_id\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "1")

    def test_minigraph_neighbor_metadata(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "DEVICE_NEIGHBOR_METADATA"'
        output = self.run_script(argument)
        self.assertEqual(
            utils.to_dict(output.strip()),
            utils.to_dict("{'switch-01t1': {'lo_addr': '10.1.0.186/32', 'mgmt_addr': '10.7.0.196/26', 'hwsku': 'Force10-S6000', 'type': 'LeafRouter', 'deployment_id': '2'}}")
        )

#     everflow portion is not used
#     def test_metadata_everflow(self):
#         argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "MIRROR_SESSION"'
#         output = self.run_script(argument)
#         self.assertEqual(output.strip(), "{'everflow0': {'src_ip': '10.1.0.32', 'dst_ip': '10.0.100.1'}}")

    def test_metadata_tacacs(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "TACPLUS_SERVER"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'10.0.10.7': {'priority': '1', 'tcp_port': '49'}, '10.0.10.8': {'priority': '1', 'tcp_port': '49'}}")

    def test_minigraph_mgmt_port(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "MGMT_PORT"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'eth0': {'alias': 'eth0', 'admin_status': 'up', 'speed': '1000'}}")

    def test_metadata_ntp(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "NTP_SERVER"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'10.0.10.1': {}, '10.0.10.2': {}}")

    def test_minigraph_vnet(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "VNET"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "")

    def test_minigraph_vxlan(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "VXLAN_TUNNEL"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "")

    def test_minigraph_bgp_mon(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "BGP_MONITORS"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{}")

    def test_minigraph_mirror_dscp(self):
        result = minigraph.parse_xml(self.sample_graph, port_config_file=self.port_config)
        self.assertTrue('EVERFLOW_DSCP' in result['ACL_TABLE'])
        everflow_dscp_entry = result['ACL_TABLE']['EVERFLOW_DSCP']

        self.assertEqual(everflow_dscp_entry['type'], 'MIRROR_DSCP')
        self.assertEqual(everflow_dscp_entry['stage'], 'ingress')
        expected_ports = ['PortChannel01', 'Ethernet12', 'Ethernet8', 'Ethernet0']
        self.assertEqual(
            everflow_dscp_entry['ports'].sort(),
            expected_ports.sort()
        )

    def test_parse_device_desc_xml_mgmt_interface(self):
        # Regular device_desc.xml with both IPv4 and IPv6 mgmt address
        result = minigraph.parse_device_desc_xml(self.sample_simple_device_desc)
        mgmt_intf = result['MGMT_INTERFACE']
        self.assertEqual(len(mgmt_intf.keys()), 2)
        self.assertTrue(('eth0', '10.0.0.100/24') in mgmt_intf.keys())
        self.assertTrue(('eth0', 'FC00:1::32/64') in mgmt_intf.keys())
        self.assertTrue(ipaddress.IPAddress('10.0.0.1') == mgmt_intf[('eth0', '10.0.0.100/24')]['gwaddr'])
        self.assertTrue(ipaddress.IPAddress('fc00:1::1') == mgmt_intf[('eth0', 'FC00:1::32/64')]['gwaddr'])

        # Special device_desc.xml with IPv6 mgmt address only
        result = minigraph.parse_device_desc_xml(self.sample_simple_device_desc_ipv6_only)
        mgmt_intf = result['MGMT_INTERFACE']
        self.assertEqual(len(mgmt_intf.keys()), 1)
        self.assertTrue(('eth0', 'FC00:1::32/64') in mgmt_intf.keys())
        self.assertTrue(ipaddress.IPAddress('fc00:1::1') == mgmt_intf[('eth0', 'FC00:1::32/64')]['gwaddr'])

    def test_dhcp_table(self):
            argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v "DHCP_RELAY"'
            expected = {
                'Vlan1000': {
                    'dhcpv6_servers': [
                        "fc02:2000::1",
                        "fc02:2000::2"
                    ]
                },
                'Vlan2000': {
                    'dhcpv6_servers': [
                        "fc02:2000::3",
                        "fc02:2000::4"
                    ]
                }
            }
            output = self.run_script(argument)
            self.assertEqual(
                utils.to_dict(output.strip()),
                expected
            )