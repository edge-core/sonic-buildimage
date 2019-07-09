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
        self.sample_graph_metadata = os.path.join(self.test_dir, 'simple-sample-graph-metadata.xml')
        self.sample_graph_pc_test = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.sample_graph_bgp_speaker = os.path.join(self.test_dir, 't0-sample-bgp-speaker.xml')
        self.sample_device_desc = os.path.join(self.test_dir, 'device.xml')
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

    def test_var_json_data(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" --var-json VLAN_MEMBER'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), '{\n    "Vlan1000|Ethernet8": {\n        "tagging_mode": "untagged"\n    }\n}')

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
        output = self.run_script(argument, True)
        self.assertEqual(output.strip(), "Warning: Ignoring Control Plane ACL NTP_ACL without type\n"
                                         "Warning: ignore interface 'fortyGigE0/2' as it is not in the port_config.ini\n"
                                         "Warning: ignore interface 'fortyGigE0/2' in DEVICE_NEIGHBOR as it is not in the port_config.ini\n"
                                         "{'DATAACL': {'type': 'L3', 'policy_desc': 'DATAACL', 'ports': ['PortChannel01', 'PortChannel02', 'PortChannel03', 'PortChannel04']}, "
                                         "'NTP_ACL': {'services': ['NTP'], 'type': 'CTRLPLANE', 'policy_desc': 'NTP_ACL'}, "
                                         "'EVERFLOW': {'type': 'MIRROR', 'policy_desc': 'EVERFLOW', 'ports': ['PortChannel01', 'PortChannel02', 'PortChannel03', 'PortChannel04', 'Ethernet24', 'Ethernet40', 'Ethernet20', 'Ethernet44', 'Ethernet48', 'Ethernet28', 'Ethernet96', 'Ethernet92', 'Ethernet76', 'Ethernet72', 'Ethernet52', 'Ethernet80', 'Ethernet56', 'Ethernet32', 'Ethernet16', 'Ethernet36', 'Ethernet12', 'Ethernet60', 'Ethernet8', 'Ethernet4', 'Ethernet0', 'Ethernet64', 'Ethernet68', 'Ethernet84', 'Ethernet88', 'Ethernet108', 'Ethernet104', 'Ethernet100']}, "
                                         "'ROUTER_PROTECT': {'services': ['SSH', 'SNMP'], 'type': 'CTRLPLANE', 'policy_desc': 'ROUTER_PROTECT'}, "
                                         "'SNMP_ACL': {'services': ['SNMP'], 'type': 'CTRLPLANE', 'policy_desc': 'SNMP_ACL'}, "
                                         "'SSH_ACL': {'services': ['SSH'], 'type': 'CTRLPLANE', 'policy_desc': 'SSH_ACL'}, "
                                         "'EVERFLOWV6': {'type': 'MIRRORV6', 'policy_desc': 'EVERFLOWV6', 'ports': ['PortChannel01', 'PortChannel02', 'PortChannel03', 'PortChannel04', 'Ethernet24', 'Ethernet40', 'Ethernet20', 'Ethernet44', 'Ethernet48', 'Ethernet28', 'Ethernet96', 'Ethernet92', 'Ethernet76', 'Ethernet72', 'Ethernet52', 'Ethernet80', 'Ethernet56', 'Ethernet32', 'Ethernet16', 'Ethernet36', 'Ethernet12', 'Ethernet60', 'Ethernet8', 'Ethernet4', 'Ethernet0', 'Ethernet64', 'Ethernet68', 'Ethernet84', 'Ethernet88', 'Ethernet108', 'Ethernet104', 'Ethernet100']}}")

    def test_minigraph_everflow(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v MIRROR_SESSION'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'everflow0': {'src_ip': '10.1.0.32', 'dst_ip': '2.2.2.2'}}")

    def test_minigraph_mgmt_ports(self):
        argument = '-m "' + self.sample_graph + '" -p "' + self.port_config + '" -v MGMT_PORT'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'eth0': {'alias': 'Management0', 'admin_status': 'up'}}")

    def test_minigraph_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Ethernet0', '10.0.0.58/31'), 'Ethernet0', ('Ethernet0', 'FC00::75/126')]")

    def test_minigraph_vlans(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v VLAN'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'Vlan1000': {'alias': 'ab1', 'dhcp_servers': ['192.0.0.1', '192.0.0.2'], 'vlanid': '1000'}}")

    def test_minigraph_vlan_members(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v VLAN_MEMBER'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{('Vlan1000', 'Ethernet8'): {'tagging_mode': 'untagged'}}")

    def test_minigraph_vlan_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "VLAN_INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('Vlan1000', '192.168.0.1/27'), 'Vlan1000']")

    def test_minigraph_portchannels(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v PORTCHANNEL'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'admin_status': 'up', 'min_links': '1', 'members': ['Ethernet4'], 'mtu': '9100'}}")

    def test_minigraph_portchannel_with_more_member(self):
        argument = '-m "' + self.sample_graph_pc_test + '" -p "' + self.port_config + '" -v PORTCHANNEL'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'PortChannel01': {'admin_status': 'up', 'min_links': '3', 'members': ['Ethernet112', 'Ethernet116', 'Ethernet120', 'Ethernet124'], 'mtu': '9100'}}")

    def test_minigraph_portchannel_members(self):
        argument = '-m "' + self.sample_graph_pc_test + '" -p "' + self.port_config + '" -v "PORTCHANNEL_MEMBER.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "[('PortChannel01', 'Ethernet120'), ('PortChannel01', 'Ethernet116'), ('PortChannel01', 'Ethernet124'), ('PortChannel01', 'Ethernet112')]")

    def test_minigraph_portchannel_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "PORTCHANNEL_INTERFACE.keys()"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "['PortChannel01', ('PortChannel01', '10.0.0.56/31'), ('PortChannel01', 'FC00::71/126')]")

    def test_minigraph_neighbors(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v "DEVICE_NEIGHBOR[\'Ethernet124\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'name': 'ARISTA04T1', 'port': 'Ethernet1/1'}")

    def test_minigraph_extra_neighbors(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v DEVICE_NEIGHBOR'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), \
                "{'Ethernet116': {'name': 'ARISTA02T1', 'port': 'Ethernet1/1'}, "
                "'Ethernet124': {'name': 'ARISTA04T1', 'port': 'Ethernet1/1'}, "
                "'Ethernet112': {'name': 'ARISTA01T1', 'port': 'Ethernet1/1'}, "
                "'Ethernet120': {'name': 'ARISTA03T1', 'port': 'Ethernet1/1'}}")

    def test_minigraph_port_description(self):
        argument = '-m "' + self.sample_graph_t0 + '" -p "' + self.port_config + '" -v "PORT[\'Ethernet124\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'lanes': '101,102,103,104', 'description': 'ARISTA04T1:Ethernet1/1', 'pfc_asym': 'off', 'mtu': '9100', 'alias': 'fortyGigE0/124', 'admin_status': 'up'}")

    def test_minigraph_bgp(self):
        argument = '-m "' + self.sample_graph_bgp_speaker + '" -p "' + self.port_config + '" -v "BGP_NEIGHBOR[\'10.0.0.59\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'rrclient': 0, 'name': 'ARISTA02T1', 'local_addr': '10.0.0.58', 'nhopself': 0, 'holdtime': '180', 'asn': '64600', 'keepalive': '60'}")

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
        self.assertEqual(output.strip(), "{'lanes': '37,38,39,40', 'description': 'Interface description', 'pfc_asym': 'off', 'mtu': '9100', 'alias': 'fortyGigE0/8', 'admin_status': 'up', 'speed': '1000'}")
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "PORT[\'Ethernet12\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'lanes': '33,34,35,36', 'fec': 'rs', 'mtu': '9100', 'alias': 'fortyGigE0/12', 'pfc_asym': 'off', 'speed': '100000', 'description': 'Interface description'}")

    def test_minigraph_extra_ethernet_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "PORT"'
        output = self.run_script(argument)

        self.assertEqual(output.strip(), \
            "{'Ethernet8': {'lanes': '37,38,39,40', 'description': 'Interface description', 'pfc_asym': 'off', 'mtu': '9100', 'alias': 'fortyGigE0/8', 'admin_status': 'up', 'speed': '1000'}, "
            "'Ethernet0': {'lanes': '29,30,31,32', 'description': 'fortyGigE0/0', 'pfc_asym': 'off', 'mtu': '9100', 'alias': 'fortyGigE0/0', 'admin_status': 'up', 'speed': '10000'}, "
            "'Ethernet4': {'lanes': '25,26,27,28', 'description': 'fortyGigE0/4', 'pfc_asym': 'off', 'mtu': '9100', 'alias': 'fortyGigE0/4', 'admin_status': 'up', 'speed': '25000'}, "
            "'Ethernet108': {'alias': 'fortyGigE0/108', 'pfc_asym': 'off', 'lanes': '81,82,83,84', 'description': 'fortyGigE0/108', 'mtu': '9100'}, "
            "'Ethernet100': {'alias': 'fortyGigE0/100', 'pfc_asym': 'off', 'lanes': '125,126,127,128', 'description': 'fortyGigE0/100', 'mtu': '9100'}, "
            "'Ethernet104': {'alias': 'fortyGigE0/104', 'pfc_asym': 'off', 'lanes': '85,86,87,88', 'description': 'fortyGigE0/104', 'mtu': '9100'}, "
            "'Ethernet68': {'alias': 'fortyGigE0/68', 'pfc_asym': 'off', 'lanes': '69,70,71,72', 'description': 'fortyGigE0/68', 'mtu': '9100'}, "
            "'Ethernet96': {'alias': 'fortyGigE0/96', 'pfc_asym': 'off', 'lanes': '121,122,123,124', 'description': 'fortyGigE0/96', 'mtu': '9100'}, "
            "'Ethernet124': {'alias': 'fortyGigE0/124', 'pfc_asym': 'off', 'lanes': '101,102,103,104', 'description': 'fortyGigE0/124', 'mtu': '9100'}, "
            "'Ethernet92': {'alias': 'fortyGigE0/92', 'pfc_asym': 'off', 'lanes': '113,114,115,116', 'description': 'fortyGigE0/92', 'mtu': '9100'}, "
            "'Ethernet120': {'alias': 'fortyGigE0/120', 'pfc_asym': 'off', 'lanes': '97,98,99,100', 'description': 'fortyGigE0/120', 'mtu': '9100'}, "
            "'Ethernet52': {'alias': 'fortyGigE0/52', 'pfc_asym': 'off', 'lanes': '53,54,55,56', 'description': 'fortyGigE0/52', 'mtu': '9100'}, "
            "'Ethernet56': {'alias': 'fortyGigE0/56', 'pfc_asym': 'off', 'lanes': '61,62,63,64', 'description': 'fortyGigE0/56', 'mtu': '9100'}, "
            "'Ethernet76': {'alias': 'fortyGigE0/76', 'pfc_asym': 'off', 'lanes': '73,74,75,76', 'description': 'fortyGigE0/76', 'mtu': '9100'}, "
            "'Ethernet72': {'alias': 'fortyGigE0/72', 'pfc_asym': 'off', 'lanes': '77,78,79,80', 'description': 'fortyGigE0/72', 'mtu': '9100'}, "
            "'Ethernet64': {'alias': 'fortyGigE0/64', 'pfc_asym': 'off', 'lanes': '65,66,67,68', 'description': 'fortyGigE0/64', 'mtu': '9100'}, "
            "'Ethernet32': {'alias': 'fortyGigE0/32', 'pfc_asym': 'off', 'lanes': '9,10,11,12', 'description': 'fortyGigE0/32', 'mtu': '9100'}, "
            "'Ethernet16': {'alias': 'fortyGigE0/16', 'pfc_asym': 'off', 'lanes': '41,42,43,44', 'description': 'fortyGigE0/16', 'mtu': '9100'}, "
            "'Ethernet36': {'alias': 'fortyGigE0/36', 'pfc_asym': 'off', 'lanes': '13,14,15,16', 'description': 'fortyGigE0/36', 'mtu': '9100'}, "
            "'Ethernet12': {'lanes': '33,34,35,36', 'fec': 'rs', 'mtu': '9100', 'alias': 'fortyGigE0/12', 'pfc_asym': 'off', 'speed': '100000', 'description': 'Interface description'}, "
            "'Ethernet88': {'alias': 'fortyGigE0/88', 'pfc_asym': 'off', 'lanes': '117,118,119,120', 'description': 'fortyGigE0/88', 'mtu': '9100'}, "
            "'Ethernet116': {'alias': 'fortyGigE0/116', 'pfc_asym': 'off', 'lanes': '93,94,95,96', 'description': 'fortyGigE0/116', 'mtu': '9100'}, "
            "'Ethernet80': {'alias': 'fortyGigE0/80', 'pfc_asym': 'off', 'lanes': '105,106,107,108', 'description': 'fortyGigE0/80', 'mtu': '9100'}, "
            "'Ethernet112': {'alias': 'fortyGigE0/112', 'pfc_asym': 'off', 'lanes': '89,90,91,92', 'description': 'fortyGigE0/112', 'mtu': '9100'}, "
            "'Ethernet84': {'alias': 'fortyGigE0/84', 'pfc_asym': 'off', 'lanes': '109,110,111,112', 'description': 'fortyGigE0/84', 'mtu': '9100'}, "
            "'Ethernet48': {'alias': 'fortyGigE0/48', 'pfc_asym': 'off', 'lanes': '49,50,51,52', 'description': 'fortyGigE0/48', 'mtu': '9100'}, "
            "'Ethernet44': {'alias': 'fortyGigE0/44', 'pfc_asym': 'off', 'lanes': '17,18,19,20', 'description': 'fortyGigE0/44', 'mtu': '9100'}, "
            "'Ethernet40': {'alias': 'fortyGigE0/40', 'pfc_asym': 'off', 'lanes': '21,22,23,24', 'description': 'fortyGigE0/40', 'mtu': '9100'}, "
            "'Ethernet28': {'alias': 'fortyGigE0/28', 'pfc_asym': 'off', 'lanes': '1,2,3,4', 'description': 'fortyGigE0/28', 'mtu': '9100'}, "
            "'Ethernet60': {'alias': 'fortyGigE0/60', 'pfc_asym': 'off', 'lanes': '57,58,59,60', 'description': 'fortyGigE0/60', 'mtu': '9100'}, "
            "'Ethernet20': {'alias': 'fortyGigE0/20', 'pfc_asym': 'off', 'lanes': '45,46,47,48', 'description': 'fortyGigE0/20', 'mtu': '9100'}, "
            "'Ethernet24': {'alias': 'fortyGigE0/24', 'pfc_asym': 'off', 'lanes': '5,6,7,8', 'description': 'fortyGigE0/24', 'mtu': '9100'}}")

    def test_metadata_everflow(self):
        argument = '-m "' + self.sample_graph_metadata + '" -p "' + self.port_config + '" -v "MIRROR_SESSION"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'everflow0': {'src_ip': '10.1.0.32', 'dst_ip': '10.0.100.1'}}")

    def test_metadata_tacacs(self):
        argument = '-m "' + self.sample_graph_metadata + '" -p "' + self.port_config + '" -v "TACPLUS_SERVER"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'10.0.10.7': {'priority': '1', 'tcp_port': '49'}, '10.0.10.8': {'priority': '1', 'tcp_port': '49'}}")

    def test_metadata_ntp(self):
        argument = '-m "' + self.sample_graph_metadata + '" -p "' + self.port_config + '" -v "NTP_SERVER"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "{'10.0.10.1': {}, '10.0.10.2': {}}")

    def test_minigraph_vnet(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "VNET"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "")

    def test_minigraph_vxlan(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.port_config + '" -v "VXLAN_TUNNEL"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), "")
