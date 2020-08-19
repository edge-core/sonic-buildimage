import unittest
from unittest import TestCase
import subprocess
import os
import json
import yaml
import shutil

SKU = 'multi-npu-01'
ASIC_SKU = 'multi-npu-asic'
NUM_ASIC = 4
HOSTNAME = 'multi_npu_platform_01'
DEVICE_TYPE = 'LeafRouter'

class TestMultiNpuCfgGen(TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.test_data_dir = os.path.join(self.test_dir,  'multi_npu_data')
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.sample_graph = os.path.join(self.test_data_dir, 'sample-minigraph.xml')
        self.port_config = []
        for asic in range(NUM_ASIC):
            self.port_config.append(os.path.join(self.test_data_dir, "sample_port_config-{}.ini".format(asic)))

    def run_script(self, argument, check_stderr=False):
        print('\n    Running sonic-cfggen ' + argument)
        if check_stderr:
            output = subprocess.check_output(self.script_file + ' ' + argument, stderr=subprocess.STDOUT, shell=True)
        else:
            output = subprocess.check_output(self.script_file + ' ' + argument, shell=True)

        linecount = output.strip().count('\n')
        if linecount <= 0:
            print('    Output: ' + output.strip())
        else:
            print('    Output: ({0} lines, {1} bytes)'.format(linecount + 1, len(output)))
        return output

    def run_diff(self, file1, file2):
        return subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

    def run_script_for_asic(self,argument,asic, port_config=None):
        argument = "{} -n asic{} ".format(argument, asic)
        if port_config:
            argument += "-p {}".format(port_config)
        output = self.run_script(argument)
        return output

    def test_dummy_run(self):
        argument = ''
        output = self.run_script(argument)
        self.assertEqual(output, '')

    def test_hwsku(self):
        argument = "-v \"DEVICE_METADATA[\'localhost\'][\'hwsku\']\" -m \"{}\"".format(self.sample_graph)
        output = self.run_script(argument)
        self.assertEqual(output.strip(), SKU)
        for asic in range(NUM_ASIC):
            output = self.run_script_for_asic(argument, asic)
            self.assertEqual(output.strip(), SKU)

    def test_print_data(self):
        argument = "-m \"{}\" --print-data".format(self.sample_graph)
        output = self.run_script(argument)
        self.assertGreater(len(output.strip()) , 0)
        for asic in range(NUM_ASIC):
            output = self.run_script_for_asic(argument, asic)
            self.assertGreater(len(output.strip()) , 0)

    def test_additional_json_data(self):
        argument = '-a \'{"key1":"value1"}\' -v key1'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1')
        for asic in range(NUM_ASIC):
            output = self.run_script_for_asic(argument, asic)
            self.assertEqual(output.strip(), 'value1')

    def test_read_yaml(self):
        argument = '-v yml_item -y ' + os.path.join(self.test_dir, 'test.yml')
        output = yaml.load(self.run_script(argument))
        self.assertListEqual(output, ['value1', 'value2'])
        for asic in range(NUM_ASIC):
            output = yaml.load(self.run_script_for_asic(argument, asic))
            self.assertListEqual(output, ['value1', 'value2'])

    def test_render_template(self):
        argument = '-y ' + os.path.join(self.test_dir, 'test.yml') + ' -t ' + os.path.join(self.test_dir, 'test.j2')
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1\nvalue2')
        for asic in range(NUM_ASIC):
            output = self.run_script_for_asic(argument, asic)
            self.assertEqual(output.strip(), 'value1\nvalue2')

    def test_metadata_tacacs(self):
        argument = '-m "' + self.sample_graph +  '" --var-json "TACPLUS_SERVER"'
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {'123.46.98.21': {'priority': '1', 'tcp_port': '49'}})
        #TACPLUS_SERVER not present in the asic configuration.
        for asic in range(NUM_ASIC):
            output = json.loads(self.run_script_for_asic(argument, asic, self.port_config[asic]))
            self.assertDictEqual(output, {})

    def test_metadata_ntp(self):
        argument = '-m "' + self.sample_graph  + '" --var-json "NTP_SERVER"'
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {'17.39.1.130': {}, '17.39.1.129': {}})
        #NTP data is present only in the host config
        for asic in range(NUM_ASIC):
            output = json.loads(self.run_script_for_asic(argument, asic, self.port_config[asic]))
            print("Log:asic{} sku {}".format(asic,output))
            self.assertDictEqual(output, {})

    def test_mgmt_port(self):
        argument = '-m "' + self.sample_graph +  '" --var-json "MGMT_PORT"'
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {'eth0': {'alias': 'eth0', 'admin_status': 'up'}})
        for asic in range(NUM_ASIC):
            output = json.loads(self.run_script_for_asic(argument, asic, self.port_config[asic]))
            self.assertDictEqual(output, {'eth0': {'alias': 'eth0', 'admin_status': 'up'}})

    def test_frontend_asic_portchannels(self):
        argument = "-m {} -p {} -n asic0 --var-json \"PORTCHANNEL\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'PortChannel0002': {'admin_status': 'up', 'min_links': '2', 'members': ['Ethernet0', 'Ethernet4'], 'mtu': '9100'},
            'PortChannel4001': {'admin_status': 'up', 'min_links': '2', 'members': ['Ethernet-BP0', 'Ethernet-BP4'], 'mtu': '9100'},
            'PortChannel4002': {'admin_status': 'up', 'min_links': '2', 'members': ['Ethernet-BP8', 'Ethernet-BP12'], 'mtu': '9100'}})

    def test_backend_asic_portchannels(self):
        argument = "-m {} -p {} -n asic3 --var-json \"PORTCHANNEL\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'PortChannel4013': {'admin_status': 'up', 'min_links': '2', 'members': ['Ethernet-BP384', 'Ethernet-BP388'], 'mtu': '9100'},
            'PortChannel4014': {'admin_status': 'up', 'min_links': '2', 'members': ['Ethernet-BP392', 'Ethernet-BP396'], 'mtu': '9100'}})

    def test_frontend_asic_portchannel_mem(self):
        argument = "-m {} -p {} -n asic0 --var-json \"PORTCHANNEL_MEMBER\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertListEqual(list(output.keys()), \
            ['PortChannel4002|Ethernet-BP8', 'PortChannel0002|Ethernet0', 'PortChannel0002|Ethernet4', 'PortChannel4002|Ethernet-BP12', 'PortChannel4001|Ethernet-BP0', 'PortChannel4001|Ethernet-BP4'])

    def test_backend_asic_portchannels_mem(self):
        argument = "-m {} -p {} -n asic3 --var-json \"PORTCHANNEL_MEMBER\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertListEqual(list(output.keys()), \
           ['PortChannel4013|Ethernet-BP384', 'PortChannel4014|Ethernet-BP392', 'PortChannel4014|Ethernet-BP396', 'PortChannel4013|Ethernet-BP388'])

    def test_frontend_asic_portchannel_intf(self):
        argument = "-m {} -p {} -n asic0 --var-json \"PORTCHANNEL_INTERFACE\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertListEqual(list(output.keys()), \
            ['PortChannel4001|10.1.0.1/31', 'PortChannel0002|FC00::1/126', 'PortChannel4002|10.1.0.3/31', 'PortChannel0002', 'PortChannel0002|10.0.0.0/31', 'PortChannel4001', 'PortChannel4002'])

    def test_backend_asic_portchannel_intf(self):
        argument = "-m {} -p {} -n asic3 --var-json \"PORTCHANNEL_INTERFACE\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertListEqual(list(output.keys()), \
            ['PortChannel4013', 'PortChannel4013|10.1.0.2/31', 'PortChannel4014', 'PortChannel4014|10.1.0.6/31'])

    def test_frontend_asic_ports(self):
        argument = "-m {} -p {} -n asic0 --var-json \"PORT\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
           {"Ethernet0": { "admin_status": "up",  "alias": "Ethernet1/1",  "asic_port_name": "Eth0-ASIC0",  "description": "01T2:Ethernet1",  "index": "0",  "lanes": "33,34,35,36",  "mtu": "9100",  "pfc_asym": "off",  "role": "Ext",  "speed": "40000" }, 
            "Ethernet4": { "admin_status": "up",  "alias": "Ethernet1/2",  "asic_port_name": "Eth1-ASIC0",  "description": "01T2:Ethernet2",  "index": "1",  "lanes": "29,30,31,32",  "mtu": "9100",  "pfc_asym": "off",  "role": "Ext",  "speed": "40000" }, 
            "Ethernet8": { "alias": "Ethernet1/3",  "asic_port_name": "Eth2-ASIC0",  "description": "Ethernet1/3",  "index": "2",  "lanes": "41,42,43,44",  "mtu": "9100",  "pfc_asym": "off",  "role": "Ext",  "speed": "40000" }, 
            "Ethernet12": { "alias": "Ethernet1/4",  "asic_port_name": "Eth3-ASIC0",  "description": "Ethernet1/4",  "index": "3",  "lanes": "37,38,39,40",  "mtu": "9100",  "pfc_asym": "off",  "role": "Ext",  "speed": "40000" }, 
            "Ethernet-BP0": { "admin_status": "up",  "alias": "Ethernet-BP0",  "asic_port_name": "Eth4-ASIC0",  "description": "ASIC2:Eth0-ASIC2",  "index": "0",  "lanes": "13,14,15,16",  "mtu": "9100",  "pfc_asym": "off",  "role": "Int",  "speed": "40000" }, 
            "Ethernet-BP4": { "admin_status": "up",  "alias": "Ethernet-BP4",  "asic_port_name": "Eth5-ASIC0",  "description": "ASIC2:Eth1-ASIC2",  "index": "1",  "lanes": "17,18,19,20",  "mtu": "9100",  "pfc_asym": "off",  "role": "Int",  "speed": "40000" }, 
            "Ethernet-BP8": { "admin_status": "up",  "alias": "Ethernet-BP8",  "asic_port_name": "Eth6-ASIC0",  "description": "ASIC3:Eth0-ASIC3",  "index": "2",  "lanes": "21,22,23,24",  "mtu": "9100",  "pfc_asym": "off",  "role": "Int",  "speed": "40000" }, 
            "Ethernet-BP12": { "admin_status": "up",  "alias": "Ethernet-BP12",  "asic_port_name": "Eth7-ASIC0",  "description": "ASIC3:Eth1-ASIC3",  "index": "3",  "lanes": "25,26,27,28",  "mtu": "9100",  "pfc_asym": "off",  "role": "Int",  "speed": "40000" }})
    
    def test_frontend_asic_device_neigh(self):
        argument = "-m {} -p {} -n asic0 --var-json \"DEVICE_NEIGHBOR\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'Ethernet0': {'name': '01T2', 'port': 'Ethernet1'},
            'Ethernet4': {'name': '01T2', 'port': 'Ethernet2'},
            'Ethernet-BP4': {'name': 'ASIC2', 'port': 'Eth1-ASIC2'},
            'Ethernet-BP12': {'name': 'ASIC3', 'port': 'Eth1-ASIC3'},
            'Ethernet-BP0': {'name': 'ASIC2', 'port': 'Eth0-ASIC2'},
            'Ethernet-BP8': {'name': 'ASIC3', 'port': 'Eth0-ASIC3'}})

    def test_frontend_asic_device_neigh_metadata(self):
        argument = "-m {} -p {} -n asic0 --var-json \"DEVICE_NEIGHBOR_METADATA\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'01T2': {'lo_addr': None, 'mgmt_addr': '89.139.132.40', 'hwsku': 'VM', 'type': 'SpineRouter'},
            'ASIC3': {'lo_addr': '0.0.0.0/0', 'mgmt_addr': '0.0.0.0/0', 'hwsku': 'multi-npu-asic', 'type': 'Asic'},
            'ASIC2': {'lo_addr': '0.0.0.0/0', 'mgmt_addr': '0.0.0.0/0', 'hwsku': 'multi-npu-asic', 'type': 'Asic'}})

    def test_backend_asic_device_neigh(self):
        argument = "-m {} -p {} -n asic3 --var-json \"DEVICE_NEIGHBOR\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'Ethernet-BP396': {'name': 'ASIC1', 'port': 'Eth7-ASIC1'},
            'Ethernet-BP384': {'name': 'ASIC0', 'port': 'Eth6-ASIC0'},
            'Ethernet-BP392': {'name': 'ASIC1', 'port': 'Eth6-ASIC1'},
            'Ethernet-BP388': {'name': 'ASIC0', 'port': 'Eth7-ASIC0'}})

    def test_backend_device_neigh_metadata(self):
        argument = "-m {} -p {} -n asic3 --var-json \"DEVICE_NEIGHBOR_METADATA\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'ASIC1': {'lo_addr': '0.0.0.0/0', 'mgmt_addr': '0.0.0.0/0', 'hwsku': 'multi-npu-asic', 'type': 'Asic'},
            'ASIC0': {'lo_addr': '0.0.0.0/0', 'mgmt_addr': '0.0.0.0/0', 'hwsku': 'multi-npu-asic', 'type': 'Asic'}})

    def test_frontend_bgp_neighbor(self):
        argument = "-m {} -p {} -n asic0 --var-json \"BGP_NEIGHBOR\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
            {'10.0.0.1': {'rrclient': 0, 'name': '01T2', 'local_addr': '10.0.0.0', 'nhopself': 0, 'holdtime': '10', 'asn': '65200', 'keepalive': '3'},
            '10.1.0.0': {'rrclient': 0, 'name': 'ASIC2', 'local_addr': '10.1.0.1', 'nhopself': 0, 'holdtime': '0', 'asn': '65100', 'keepalive': '0', 'admin_status': 'up'},
            'fc00::2': {'rrclient': 0, 'name': '01T2', 'local_addr': 'fc00::1', 'nhopself': 0, 'holdtime': '10', 'asn': '65200', 'keepalive': '3'},
            '10.1.0.2': {'rrclient': 0, 'name': 'ASIC3', 'local_addr': '10.1.0.3', 'nhopself': 0, 'holdtime': '0', 'asn': '65100', 'keepalive': '0', 'admin_status': 'up'}})

    def test_backend_asic_bgp_neighbor(self):
        argument = "-m {} -p {} -n asic3 --var-json \"BGP_NEIGHBOR\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, \
             {'10.1.0.7': {'rrclient': 0, 'name': 'ASIC1', 'local_addr': '10.1.0.6', 'nhopself': 0, 'holdtime': '0', 'asn': '65100', 'keepalive': '0', 'admin_status': 'up'},
             '10.1.0.3': {'rrclient': 0, 'name': 'ASIC0', 'local_addr': '10.1.0.2', 'nhopself': 0, 'holdtime': '0', 'asn': '65100', 'keepalive': '0', 'admin_status': 'up'}})

    def test_device_asic_metadata(self):
        argument = "-m {} --var-json DEVICE_METADATA".format(self.sample_graph)
        for asic in range(NUM_ASIC):
            output = json.loads(self.run_script_for_asic(argument, asic,self.port_config[asic]))
            asic_name  = "asic{}".format(asic)
            self.assertEqual(output['localhost']['hostname'], 'multi_npu_platform_01')
            self.assertEqual(output['localhost']['asic_name'], asic_name)
            self.assertEqual(output['localhost']['type'], DEVICE_TYPE)
            if asic == 0 or asic == 1:
                self.assertEqual(output['localhost']['sub_role'], 'FrontEnd')
            else:
                self.assertEqual(output['localhost']['sub_role'], 'BackEnd')

    def test_global_asic_acl(self):
        argument = "-m {} --var-json \"ACL_TABLE\"".format(self.sample_graph)
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {\
                             'DATAACL':   {'policy_desc': 'DATAACL',    'ports': ['PortChannel0002','PortChannel0008'], 'stage': 'ingress', 'type': 'L3'},
                             'EVERFLOW':  {'policy_desc': 'EVERFLOW',   'ports': ['PortChannel0002','PortChannel0008'], 'stage': 'ingress', 'type': 'MIRROR'},
                             'EVERFLOWV6':{'policy_desc': 'EVERFLOWV6', 'ports': ['PortChannel0002','PortChannel0008'], 'stage': 'ingress', 'type': 'MIRRORV6'},
                             'SNMP_ACL':  {'policy_desc': 'SNMP_ACL',    'services': ['SNMP'],        'stage': 'ingress', 'type': 'CTRLPLANE'},
                             'SSH_ONLY':  {'policy_desc': 'SSH_ONLY',    'services': ['SSH'],         'stage': 'ingress', 'type': 'CTRLPLANE'}})

    def test_front_end_asic_acl(self):
        argument = "-m {} -p {} -n asic0 --var-json \"ACL_TABLE\"".format(self.sample_graph, self.port_config[0])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {\
                             'DATAACL':   {'policy_desc': 'DATAACL',    'ports': ['PortChannel0002'], 'stage': 'ingress', 'type': 'L3'},
                             'EVERFLOW':  {'policy_desc': 'EVERFLOW',   'ports': ['PortChannel0002'], 'stage': 'ingress', 'type': 'MIRROR'},
                             'EVERFLOWV6':{'policy_desc': 'EVERFLOWV6', 'ports': ['PortChannel0002'], 'stage': 'ingress', 'type': 'MIRRORV6'},
                             'SNMP_ACL':  {'policy_desc': 'SNMP_ACL',    'services': ['SNMP'],        'stage': 'ingress', 'type': 'CTRLPLANE'},
                             'SSH_ONLY':  {'policy_desc': 'SSH_ONLY',    'services': ['SSH'],         'stage': 'ingress', 'type': 'CTRLPLANE'}})

    def test_back_end_asic_acl(self):
        argument = "-m {} -p {} -n asic3 --var-json \"ACL_TABLE\"".format(self.sample_graph, self.port_config[3])
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {})

    def test_loopback_intfs(self):
        argument = "-m {} --var-json \"LOOPBACK_INTERFACE\"".format(self.sample_graph)
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {\
                "Loopback0": {},
                "Loopback0|10.1.0.32/32": {},
                "Loopback0|FC00:1::32/128": {}})

        # The asic configuration should have 2 loopback interfaces
        argument = "-m {} -n asic0 --var-json \"LOOPBACK_INTERFACE\"".format(self.sample_graph)
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, { \
                             "Loopback0": {},
                             "Loopback4096": {},
                             "Loopback0|10.1.0.32/32": {},
                             "Loopback0|FC00:1::32/128": {},
                             "Loopback4096|8.0.0.0/32": {},
                             "Loopback4096|FD00:1::32/128": {}})

        argument = "-m {} -n asic3 --var-json \"LOOPBACK_INTERFACE\"".format(self.sample_graph)
        output = json.loads(self.run_script(argument))
        self.assertDictEqual(output, {\
                                      "Loopback0": {},
                                      "Loopback4096": {},
                                      "Loopback0|10.1.0.32/32": {},
                                      "Loopback0|FC00:1::32/128": {},
                                      "Loopback4096|8.0.0.5/32": {},
                                      "Loopback4096|FD00:4::32/128": {}})

    def test_buffers_multi_asic_template(self):
        build_root_dir = os.path.join(
            self.test_dir, "..", "..", ".."
        )
        # using Trident2 buffer configuration
        device_config_dir = os.path.join(
            build_root_dir,
            "device",
            "arista",
            "x86_64-arista_7050_qx32",
            "Arista-7050-QX32"
        )
        device_buffer_template = os.path.join(
            device_config_dir, "buffers.json.j2"
        )
        buffer_template = os.path.join(
            build_root_dir, "files", "build_templates", "buffers_config.j2"
        )
        port_config_ini_asic0 = os.path.join(
            self.test_data_dir, "sample_port_config-0.ini"
        )
        # asic0 - mix of front end and back end ports
        shutil.copy2(buffer_template, device_config_dir)
        argument = "-m {} -p {} -n asic0 -t {}".format(
            self.sample_graph, port_config_ini_asic0, device_buffer_template
        )
        output = json.loads(self.run_script(argument))
        os.remove(os.path.join(device_config_dir, "buffers_config.j2"))
        self.assertDictEqual(
            output['CABLE_LENGTH'],
            {
                'AZURE': {
                    'Ethernet8': '300m',
                    'Ethernet0': '300m',
                    'Ethernet4': '300m',
                    'Ethernet-BP4': '5m',
                    'Ethernet-BP0': '5m',
                    'Ethernet-BP12': '5m',
                    'Ethernet-BP8': '5m',
                    'Ethernet12': '300m'
                }
            }
        )
