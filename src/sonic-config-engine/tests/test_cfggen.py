from unittest import TestCase
import subprocess
import os

class TestCfgGen(TestCase):
    
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.sample_graph = os.path.join(self.test_dir, 'sample_graph.xml')
        self.sample_graph_t0 = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.sample_graph_simple = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.sample_graph_pc_test = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.sample_graph_bgp_speaker = os.path.join(self.test_dir, 't0-sample-bgp-speaker.xml')
        self.port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')

    def run_script(self, argument):
        print '\n    Running sonic-cfggen ' + argument
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
        argument = '-v minigraph_hwsku -m "' + self.sample_graph + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'Force10-Z9100')
    
    def test_print_data(self):
        argument = '-m "' + self.sample_graph + '" --print-data'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)
    
    def test_jinja_expression(self):
        argument = '-m "' + self.sample_graph + '" -v "minigraph_devices[minigraph_hostname][\'type\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'LeafRouter')
    
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

    def test_minigraph_acl(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v minigraph_acls'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'dataacl': {'IsMirror': False, 'AttachTo': ['Ethernet112', 'Ethernet116', 'Ethernet120', 'Ethernet124']}}")

    def test_minigraph_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v minigraph_interfaces'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[{'subnet': IPv4Network('10.0.0.58/31'), 'peer_addr': IPv4Address('10.0.0.59'), 'addr': IPv4Address('10.0.0.58'), 'mask': IPv4Address('255.255.255.254'), 'attachto': 'Ethernet0', 'prefixlen': 31}, {'subnet': IPv6Network('fc00::74/126'), 'peer_addr': IPv6Address('fc00::76'), 'addr': IPv6Address('fc00::75'), 'mask': '126', 'attachto': 'Ethernet0', 'prefixlen': 126}]")
        
    def test_minigraph_vlans(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v minigraph_vlans'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'Vlan1000': {'name': 'Vlan1000', 'members': ['Ethernet8'], 'vlanid': '1000'}}")

    def test_minigraph_vlan_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v minigraph_vlan_interfaces'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[{'prefixlen': 27, 'subnet': IPv4Network('192.168.0.0/27'), 'mask': IPv4Address('255.255.255.224'), 'addr': IPv4Address('192.168.0.1'), 'attachto': 'Vlan1000'}]")

    def test_minigraph_portchannels(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v minigraph_portchannels'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'name': 'PortChannel01', 'members': ['Ethernet4']}}")

    def test_minigraph_portchannels_more_member(self):
        argument = '-m "' + self.sample_graph_pc_test + '" -p "' + self.port_config + '" -v minigraph_portchannels'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'name': 'PortChannel01', 'members': ['Ethernet112', 'Ethernet116', 'Ethernet120', 'Ethernet124']}}")

    def test_minigraph_portchannel_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v minigraph_portchannel_interfaces'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[{'subnet': IPv4Network('10.0.0.56/31'), 'peer_addr': IPv4Address('10.0.0.57'), 'addr': IPv4Address('10.0.0.56'), 'mask': IPv4Address('255.255.255.254'), 'attachto': 'PortChannel01', 'prefixlen': 31}, {'subnet': IPv6Network('fc00::70/126'), 'peer_addr': IPv6Address('fc00::72'), 'addr': IPv6Address('fc00::71'), 'mask': '126', 'attachto': 'PortChannel01', 'prefixlen': 126}]")

    def test_minigraph_neighbors(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v minigraph_neighbors'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'Ethernet116': {'name': 'ARISTA02T1', 'port': 'Ethernet1/1'}, 'Ethernet124': {'name': 'ARISTA04T1', 'port': 'Ethernet1/1'}, 'Ethernet112': {'name': 'ARISTA01T1', 'port': 'Ethernet1/1'}, 'Ethernet120': {'name': 'ARISTA03T1', 'port': 'Ethernet1/1'}}")

    def test_minigraph_peers_with_range(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v minigraph_bgp_peers_with_range'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[{'name': 'BGPSLBPassive', 'ip_range': '10.10.10.10/26'}]")

    def test_minigraph_deployment_id(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v deployment_id'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "1")
