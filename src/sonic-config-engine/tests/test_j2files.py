import filecmp
import os
import subprocess
import json

from unittest import TestCase

class TestJ2Files(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print 'CMD: sonic-cfggen ' + argument
        return subprocess.check_output(self.script_file + ' ' + argument, shell=True)

    def test_interfaces(self):
        interfaces_template = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'interfaces', 'interfaces.j2')
        argument = '-m "' + self.t0_minigraph + '" -p "' + self.t0_port_config + '" -t "' + interfaces_template + '"'
        output = self.run_script(argument) 

    def test_alias_map(self):
        alias_map_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-snmp-sv2', 'alias_map.j2')
        argument = '-m "' + self.t0_minigraph + '" -p "' + self.t0_port_config + '" -t "' + alias_map_template + '"'
        output = self.run_script(argument)
        data = json.loads(output)
        self.assertEqual(data["Ethernet4"], "fortyGigE0/4")        
        
    def test_teamd(self):
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -v "minigraph_portchannels.keys() | join(\' \')"'
        output = self.run_script(argument) # Mock the output via config.sh in docker-teamd
        pc_list = output.split()

        def test_render_teamd(self, pc):
            teamd_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-teamd', 'teamd.j2')
            sample_output_file = os.path.join(self.test_dir, 'sample_output',pc + '.conf')
            argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -a \'{\"pc\":\"' + pc + '\"}\' -t ' + teamd_file + ' > ' + self.output_file
            self.run_script(argument)
            assert filecmp.cmp(sample_output_file, self.output_file)

        for i in range(1, 5):
            pc_name = 'PortChannel0' + str(i)
            assert pc_name in pc_list
            test_render_teamd(self, pc_name)

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass
