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
        self.sample_device_desc = os.path.join(self.test_dir, 'device.xml')
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
    
    def test_device_desc(self):
        argument = '-v "DEVICE_METADATA[\'localhost\'][\'hwsku\']" -M "' + self.sample_device_desc + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'ACS-MSN2700')

    def test_device_desc_mgmt_ip(self):
        argument = '-v "MGMT_INTERFACE.keys()[0]" -M "' + self.sample_device_desc + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "('eth0', '10.0.1.5/28')")

    def test_minigraph_sku(self):
        argument = '-v "DEVICE_METADATA[\'localhost\'][\'hwsku\']" -m "' + self.sample_graph + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'Force10-Z9100')
    
    def test_print_data(self):
        argument = '-m "' + self.sample_graph + '" --print-data'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)
    
    def test_jinja_expression(self):
        argument = '-m "' + self.sample_graph + '" -v "DEVICE_METADATA[\'localhost\'][\'type\']"'
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
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v ACL_TABLE'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'dataacl': {'type': 'L3', 'policy_desc': 'dataacl', 'ports': ['Ethernet112', 'Ethernet116', 'Ethernet120', 'Ethernet124']}}")

    def test_minigraph_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v \'INTERFACE.keys()\''
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Ethernet0', '10.0.0.58/31'), ('Ethernet0', 'FC00::75/126')]")
        
    def test_minigraph_vlans(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v VLAN'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'Vlan1000': {'members': ['Ethernet8'], 'vlanid': '1000'}}")

    def test_minigraph_vlan_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "VLAN_INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Vlan1000', '192.168.0.1/27')]")

    def test_minigraph_portchannels(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v PORTCHANNEL'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'members': ['Ethernet4']}}")

    def test_minigraph_portchannels_more_member(self):
        argument = '-m "' + self.sample_graph_pc_test + '" -p "' + self.port_config + '" -v PORTCHANNEL'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'members': ['Ethernet112', 'Ethernet116', 'Ethernet120', 'Ethernet124']}}")

    def test_minigraph_portchannel_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "PORTCHANNEL_INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('PortChannel01', 'FC00::71/126'), ('PortChannel01', '10.0.0.56/31')]")

    def test_minigraph_neighbors(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v "DEVICE_NEIGHBOR[\'ARISTA01T1\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'mgmt_addr': None, 'hwsku': 'Arista', 'lo_addr': None, 'local_port': 'Ethernet112', 'type': 'LeafRouter', 'port': 'Ethernet1/1'}")

    def test_minigraph_bgp(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v "BGP_NEIGHBOR[\'10.0.0.59\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'rrclient': '0', 'local_addr': '10.0.0.58', 'asn': '64600', 'name': 'ARISTA02T1'}")

    def test_minigraph_peers_with_range(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v BGP_PEER_RANGE.values\(\)'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[{'name': 'BGPSLBPassive', 'ip_range': ['10.10.10.10/26', '100.100.100.100/26']}]")

    def test_minigraph_deployment_id(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v "DEVICE_METADATA[\'localhost\'][\'deployment_id\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "1")

    def test_minigraph_ethernet_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "PORT[\'Ethernet8\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'alias': 'fortyGigE0/8', 'speed': '40000'}")
