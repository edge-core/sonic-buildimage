import filecmp
import os
import subprocess
import json
import shutil

from unittest import TestCase

class TestJ2FilesT2ChassisFe(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.t2_chassis_fe_minigraph = os.path.join(self.test_dir, 't2-chassis-fe-graph.xml')
        self.t2_chassis_fe_vni_minigraph = os.path.join(self.test_dir, 't2-chassis-fe-graph-vni.xml')
        self.t2_chassis_fe_pc_minigraph = os.path.join(self.test_dir, 't2-chassis-fe-graph-pc.xml')
        self.t2_chassis_fe_port_config = os.path.join(self.test_dir, 't2-chassis-fe-port-config.ini')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print 'CMD: sonic-cfggen ' + argument
        return subprocess.check_output(self.script_file + ' ' + argument, shell=True)

    # Test zebra.conf in FRR docker for a T2 chassis frontend (fe)
    def test_t2_chassis_fe_zebra_frr(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', 'zebra.conf.j2')
        argument = '-m ' + self.t2_chassis_fe_minigraph + ' -p ' + self.t2_chassis_fe_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 't2-chassis-fe-zebra.conf'), self.output_file))

    # Test zebra.conf in FRR docker for a T2 chassis frontend (fe) switch with port channel interfaces
    def test_t2_chassis_fe_pc_zebra_frr(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', 'zebra.conf.j2')
        argument = '-m ' + self.t2_chassis_fe_pc_minigraph + ' -p ' + self.t2_chassis_fe_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 't2-chassis-fe-pc-zebra.conf'), self.output_file))

    # Test zebra.conf in FRR docker for a T2 chassis frontend (fe) switch with specified VNI
    def test_t2_chassis_fe_pc_zebra_frr(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', 'zebra.conf.j2')
        argument = '-m ' + self.t2_chassis_fe_vni_minigraph + ' -p ' + self.t2_chassis_fe_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 't2-chassis-fe-vni-zebra.conf'), self.output_file))

    # Test bgpd.conf in FRR docker for a T2 chassis frontend (fe)
    def test_t2_chassis_frontend_bgpd_frr(self):
        conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', 'bgpd.conf.j2')
        argument = '-m ' + self.t2_chassis_fe_minigraph + ' -p ' + self.t2_chassis_fe_port_config + ' -t ' + conf_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(filecmp.cmp(os.path.join(self.test_dir, 'sample_output', 't2-chassis-fe-bgpd.conf'), self.output_file))

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass


