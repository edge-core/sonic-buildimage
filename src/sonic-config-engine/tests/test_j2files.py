import filecmp
import os
import subprocess
import json
import shutil

from unittest import TestCase

class TestJ2Files(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.simple_minigraph = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_mvrf_minigraph = os.path.join(self.test_dir, 't0-sample-graph-mvrf.xml')
        self.pc_minigraph = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.t1_mlnx_minigraph = os.path.join(self.test_dir, 't1-sample-graph-mlnx.xml')
        self.mlnx_port_config = os.path.join(self.test_dir, 'sample-port-config-mlnx.ini')
        self.dell6100_t0_minigraph = os.path.join(self.test_dir, 'sample-dell-6100-t0-minigraph.xml')
        self.arista7050_t0_minigraph = os.path.join(self.test_dir, 'sample-arista-7050-t0-minigraph.xml')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print('CMD: sonic-cfggen ' + argument)
        return subprocess.check_output(self.script_file + ' ' + argument, shell=True)

    def run_diff(self, file1, file2):
        return subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

    def test_interfaces(self):
        interfaces_template = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'interfaces', 'interfaces.j2')
        argument = '-m ' + self.t0_minigraph + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'interfaces'), self.output_file))

        argument = '-m ' + self.t0_mvrf_minigraph + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'mvrf_interfaces'), self.output_file))

    def test_ports_json(self):
        ports_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ports.json.j2')
        argument = '-m ' + self.simple_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ports_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'ports.json'), self.output_file))

    def test_dhcp_relay(self):
        # Test generation of wait_for_intf.sh
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'wait_for_intf.sh.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'wait_for_intf.sh'), self.output_file))

        # Test generation of docker-dhcp-relay.supervisord.conf
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'docker-dhcp-relay.supervisord.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'docker-dhcp-relay.supervisord.conf'), self.output_file))

    def test_lldp(self):
        lldpd_conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-lldp', 'lldpd.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + lldpd_conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'lldpd.conf'), self.output_file))

    def test_bgpd_quagga(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-quagga', 'bgpd.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        original_filename = os.path.join(self.test_dir, 'sample_output', 'bgpd_quagga.conf')
        r = filecmp.cmp(original_filename, self.output_file)
        diff_output = self.run_diff(original_filename, self.output_file) if not r else ""
        self.assertTrue(r, "Diff:\n" + diff_output)

    def test_zebra_quagga(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-quagga', 'zebra.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'zebra_quagga.conf'), self.output_file))

    def test_ipinip(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ipinip_file + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'ipinip.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_l2switch_template(self):
        argument = '-k Mellanox-SN2700 -t ' + os.path.join(self.test_dir, '../data/l2switch.j2') + ' -p ' + self.t0_port_config + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'l2switch.json')

        self.assertTrue(filecmp.cmp(sample_output_file, self.output_file))

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

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'qos-arista7050.json')
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

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'qos-dell6100.json')
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

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'buffers-dell6100.json')
        assert filecmp.cmp(sample_output_file, self.output_file)

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass
