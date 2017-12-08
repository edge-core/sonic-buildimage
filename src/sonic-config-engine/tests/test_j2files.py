import filecmp
import os
import subprocess
import json

from unittest import TestCase

class TestJ2Files(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.simple_minigraph = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.pc_minigraph = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.t1_mlnx_minigraph = os.path.join(self.test_dir, 't1-sample-graph-mlnx.xml')
        self.mlnx_port_config = os.path.join(self.test_dir, 'sample-port-config-mlnx.ini')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print 'CMD: sonic-cfggen ' + argument
        return subprocess.check_output(self.script_file + ' ' + argument, shell=True)

    def test_interfaces(self):
        interfaces_template = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'interfaces', 'interfaces.j2')
        argument = '-m ' + self.t0_minigraph + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'interfaces'), self.output_file))

    def test_alias_map(self):
        alias_map_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-snmp-sv2', 'alias_map.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + alias_map_template
        output = self.run_script(argument)
        data = json.loads(output)
        self.assertEqual(data["Ethernet4"], "fortyGigE0/4")

    def test_ports_json(self):
        ports_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ports.json.j2')
        argument = '-m ' + self.simple_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ports_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'ports.json'), self.output_file))

    def test_lldp(self):
        lldpd_conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-lldp-sv2', 'lldpd.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + lldpd_conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 'lldpd.conf'), self.output_file))

    def test_teamd(self):

        def test_render_teamd(self, pc, minigraph, sample_output):
            teamd_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-teamd', 'teamd.j2')
            argument = '-m ' + minigraph + ' -p ' + self.t0_port_config + ' -a \'{\"pc\":\"' + pc + '\",\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + teamd_file + ' > ' + self.output_file
            self.run_script(argument)
            self.assertTrue(filecmp.cmp(sample_output, self.output_file))

        # Test T0 minigraph
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -v "PORTCHANNEL.keys() | join(\' \') if PORTCHANNEL"'
        output = self.run_script(argument) # Mock the output via config.sh in docker-teamd
        pc_list = output.split()

        for i in range(1, 5):
            pc_name = 'PortChannel0' + str(i)
            self.assertTrue(pc_name in pc_list)
            sample_output = os.path.join(self.test_dir, 'sample_output', 't0_sample_output', pc_name + '.conf')
            test_render_teamd(self, pc_name, self.t0_minigraph, sample_output)

        # Test port channel test minigraph
        argument = '-m ' + self.pc_minigraph + ' -p ' + self.t0_port_config + ' -v "PORTCHANNEL.keys() | join(\' \') if PORTCHANNEL"'
        output = self.run_script(argument) # Mock the output via config.sh in docker-teamd
        pc_list = output.split()

        pc_name = 'PortChannel01'
        self.assertTrue(pc_name in pc_list)
        sample_output = os.path.join(self.test_dir, 'sample_output', 'pc_sample_output', pc_name + '.conf')
        test_render_teamd(self, pc_name, self.pc_minigraph, sample_output)

    def test_ipinip(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ipinip_file + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'ipinip.json')

        assert filecmp.cmp(sample_output_file, self.output_file)

    def test_msn27xx_32ports_buffers(self):
        buffer_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'msn27xx.32ports.buffers.json.j2')
        argument = '-m ' + self.t1_mlnx_minigraph + ' -p ' + self.mlnx_port_config + ' -t ' + buffer_file + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', 'msn27.32ports.json')

        self.assertTrue(filecmp.cmp(sample_output_file, self.output_file))


    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass
