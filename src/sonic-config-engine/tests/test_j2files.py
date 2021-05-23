import filecmp
import json
import os
import shutil
import subprocess

from unittest import TestCase
import tests.common_utils as utils


class TestJ2Files(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = utils.PYTHON_INTERPRETTER + ' ' + os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.simple_minigraph = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_mvrf_minigraph = os.path.join(self.test_dir, 't0-sample-graph-mvrf.xml')
        self.pc_minigraph = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.t0_7050cx3_port_config = os.path.join(self.test_dir, 't0_7050cx3_d48c8_port_config.ini')
        self.t1_mlnx_minigraph = os.path.join(self.test_dir, 't1-sample-graph-mlnx.xml')
        self.mlnx_port_config = os.path.join(self.test_dir, 'sample-port-config-mlnx.ini')
        self.dell6100_t0_minigraph = os.path.join(self.test_dir, 'sample-dell-6100-t0-minigraph.xml')
        self.arista7050_t0_minigraph = os.path.join(self.test_dir, 'sample-arista-7050-t0-minigraph.xml')
        self.multi_asic_minigraph = os.path.join(self.test_dir, 'multi_npu_data', 'sample-minigraph.xml')
        self.multi_asic_port_config = os.path.join(self.test_dir, 'multi_npu_data', 'sample_port_config-0.ini')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print('CMD: sonic-cfggen ' + argument)
        output = subprocess.check_output(self.script_file + ' ' + argument, shell=True)

        if utils.PY3x:
            output = output.decode()

        return output

    def run_diff(self, file1, file2):
        return subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

    def test_interfaces(self):
        interfaces_template = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'interfaces', 'interfaces.j2')
        argument = '-m ' + self.t0_minigraph + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'interfaces'), self.output_file))

        argument = '-m ' + self.t0_mvrf_minigraph + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'mvrf_interfaces'), self.output_file))

    def test_ports_json(self):
        ports_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ports.json.j2')
        argument = '-m ' + self.simple_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ports_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'ports.json'), self.output_file))

    def test_dhcp_relay(self):
        # Test generation of wait_for_intf.sh
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'wait_for_intf.sh.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'wait_for_intf.sh'), self.output_file))

        # Test generation of docker-dhcp-relay.supervisord.conf
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'docker-dhcp-relay.supervisord.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'docker-dhcp-relay.supervisord.conf'), self.output_file))

    def test_lldp(self):
        lldpd_conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-lldp', 'lldpd.conf.j2')

        expected_mgmt_ipv4 = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'lldp_conf', 'lldpd-ipv4-iface.conf')
        expected_mgmt_ipv6 = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'lldp_conf', 'lldpd-ipv6-iface.conf')
        expected_mgmt_ipv4_and_ipv6 = expected_mgmt_ipv4

        # Test generation of lldpd.conf if IPv4 and IPv6 management interfaces exist
        mgmt_iface_ipv4_and_ipv6_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv4_and_ipv6.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv4_and_ipv6_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(expected_mgmt_ipv4_and_ipv6, self.output_file))

        # Test generation of lldpd.conf if management interface IPv4 only exist
        mgmt_iface_ipv4_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv4.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv4_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(expected_mgmt_ipv4, self.output_file))

        # Test generation of lldpd.conf if Management interface IPv6 only exist
        mgmt_iface_ipv6_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv6.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv6_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(expected_mgmt_ipv6, self.output_file))

    def test_bgpd_quagga(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-quagga', 'bgpd.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        original_filename = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'bgpd_quagga.conf')
        r = filecmp.cmp(original_filename, self.output_file)
        diff_output = self.run_diff(original_filename, self.output_file) if not r else ""
        self.assertTrue(r, "Diff:\n" + diff_output)

    def test_zebra_quagga(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-quagga', 'zebra.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'zebra_quagga.conf'), self.output_file))

    def test_ipinip(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ipinip_file + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'ipinip.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_l2switch_template(self):
        argument = '-k Mellanox-SN2700 --preset l2 -p ' + self.t0_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l2switch.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

        template_dir = os.path.join(self.test_dir, '..', 'data', 'l2switch.j2')
        argument = '-t ' + template_dir + ' -k Mellanox-SN2700 -p ' + self.t0_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

    def test_l2switch_template_dualtor(self):
        extra_args = {
            "is_dualtor": True,
            "uplinks": [
                "Ethernet24", "Ethernet28", "Ethernet32", "Ethernet36",
                "Ethernet88", "Ethernet92", "Ethernet96", "Ethernet100"
            ],
            "downlinks": [
                "Ethernet0", "Ethernet4", "Ethernet8", "Ethernet12",
                "Ethernet16", "Ethernet20", "Ethernet40", "Ethernet44",
                "Ethernet48", "Ethernet52", "Ethernet56", "Ethernet60",
                "Ethernet64", "Ethernet68", "Ethernet72", "Ethernet76",
                "Ethernet80", "Ethernet84", "Ethernet104", "Ethernet108",
                "Ethernet112", "Ethernet116", "Ethernet120", "Ethernet124"
            ]
        }
        argument = '-a \'{}\' -k Arista-7050CX3-32S-D48C8 --preset l2 -p {}'.format(
            json.dumps(extra_args), self.t0_7050cx3_port_config
        )
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l2switch_dualtor.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)
        self.maxDiff = None
        self.assertEqual(sample_output_json, output_json)

    def test_qos_arista7050_render_template(self):
        arista_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'arista', 'x86_64-arista_7050_qx32s', 'Arista-7050-QX-32S')
        qos_file = os.path.join(arista_dir_path, 'qos.json.j2')
        port_config_ini_file = os.path.join(arista_dir_path, 'port_config.ini')

        # copy qos_config.j2 to the Arista 7050 directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, arista_dir_path)

        argument = '-m ' + self.arista7050_t0_minigraph + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        qos_config_file_new = os.path.join(arista_dir_path, 'qos_config.j2')
        os.remove(qos_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'qos-arista7050.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_qos_dell6100_render_template(self):
        dell_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'dell', 'x86_64-dell_s6100_c2538-r0', 'Force10-S6100')
        qos_file = os.path.join(dell_dir_path, 'qos.json.j2')
        port_config_ini_file = os.path.join(dell_dir_path, 'port_config.ini')

        # copy qos_config.j2 to the Dell S6100 directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, dell_dir_path)

        argument = '-m ' + self.dell6100_t0_minigraph + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        qos_config_file_new = os.path.join(dell_dir_path, 'qos_config.j2')
        os.remove(qos_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'qos-dell6100.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_buffers_dell6100_render_template(self):
        dell_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'dell', 'x86_64-dell_s6100_c2538-r0', 'Force10-S6100')
        buffers_file = os.path.join(dell_dir_path, 'buffers.json.j2')
        port_config_ini_file = os.path.join(dell_dir_path, 'port_config.ini')

        # copy buffers_config.j2 to the Dell S6100 directory to have all templates in one directory
        buffers_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'buffers_config.j2')
        shutil.copy2(buffers_config_file, dell_dir_path)

        argument = '-m ' + self.dell6100_t0_minigraph + ' -p ' + port_config_ini_file + ' -t ' + buffers_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        buffers_config_file_new = os.path.join(dell_dir_path, 'buffers_config.j2')
        os.remove(buffers_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'buffers-dell6100.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_ipinip_multi_asic(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.multi_asic_minigraph + ' -p ' + self.multi_asic_port_config + ' -t ' + ipinip_file  +  ' -n asic0 '  + ' > ' + self.output_file
        print(argument)
        self.run_script(argument) 
        sample_output_file = os.path.join(self.test_dir, 'multi_npu_data', utils.PYvX_DIR, 'ipinip.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_swss_switch_render_template(self):
        switch_template = os.path.join(
            self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent',
            'switch.json.j2'
        )
        constants_yml = os.path.join(
            self.test_dir, '..', '..', '..', 'files', 'image_config',
            'constants', 'constants.yml'
        )
        test_list = {
            "t1": {
                "graph": self.t1_mlnx_minigraph,
                "output": "t1-switch.json"
            },
            "t0": {
                "graph": self.t0_minigraph,
                "output": "t0-switch.json"
            },
        }
        for _, v in test_list.items():
            argument = " -m {} -y {} -t {} > {}".format(
                v["graph"], constants_yml, switch_template, self.output_file
            )
            sample_output_file = os.path.join(
                self.test_dir, 'sample_output', v["output"]
            )
            self.run_script(argument)
            assert filecmp.cmp(sample_output_file, self.output_file)

    def test_swss_switch_render_template_multi_asic(self):
        # verify the ECMP hash seed changes per namespace
        switch_template = os.path.join(
            self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent',
            'switch.json.j2'
        )
        constants_yml = os.path.join(
            self.test_dir, '..', '..', '..', 'files', 'image_config',
            'constants', 'constants.yml'
        )
        test_list = {
            "0": {
                "namespace_id": "1",
                "output": "t0-switch-masic1.json"
            },
            "1": {
                "namespace_id": "3",
                "output": "t0-switch-masic3.json"
            },
        }
        for _, v in test_list.items():
            os.environ["NAMESPACE_ID"] = v["namespace_id"]
            argument = " -m {} -y {} -t {} > {}".format(
                self.t1_mlnx_minigraph, constants_yml, switch_template,
                self.output_file
            )
            sample_output_file = os.path.join(
                self.test_dir, 'sample_output', v["output"]
            )
            self.run_script(argument)
            assert filecmp.cmp(sample_output_file, self.output_file)
        os.environ["NAMESPACE_ID"] = ""

    def test_ndppd_conf(self):
        conf_template = os.path.join(self.test_dir, "ndppd.conf.j2")
        vlan_interfaces_json = os.path.join(self.test_dir, "data", "ndppd", "vlan_interfaces.json")
        expected = os.path.join(self.test_dir, "sample_output", utils.PYvX_DIR, "ndppd.conf")

        argument = '-j {} -t {} > {}'.format(vlan_interfaces_json, conf_template, self.output_file)
        self.run_script(argument)
        assert filecmp.cmp(expected, self.output_file), self.run_diff(expected, self.output_file)

    def test_ntp_conf(self):
        conf_template = os.path.join(self.test_dir, "ntp.conf.j2")
        ntp_interfaces_json = os.path.join(self.test_dir, "data", "ntp", "ntp_interfaces.json")
        expected = os.path.join(self.test_dir, "sample_output", utils.PYvX_DIR, "ntp.conf")

        argument = '-j {} -t {} > {}'.format(ntp_interfaces_json, conf_template, self.output_file)
        self.run_script(argument)
        assert filecmp.cmp(expected, self.output_file), self.run_diff(expected, self.output_file)

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass
