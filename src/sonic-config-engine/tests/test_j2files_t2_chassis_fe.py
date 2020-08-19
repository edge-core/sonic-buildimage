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

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass

    def run_script(self, argument):
        print('CMD: sonic-cfggen ' + argument)
        return subprocess.check_output(self.script_file + ' ' + argument, shell=True)

    def run_diff(self, file1, file2):
        return subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

    def run_case(self, minigraph, template, target):
        template_dir = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', "frr")
        conf_template = os.path.join(template_dir, template)
        constants = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'constants', 'constants.yml')
        cmd_args = minigraph, self.t2_chassis_fe_port_config, constants, conf_template, template_dir, self.output_file
        cmd = "-m %s -p %s -y %s -t %s -T %s > %s" % cmd_args
        self.run_script(cmd)

        original_filename = os.path.join(self.test_dir, 'sample_output', target)
        r = filecmp.cmp(original_filename, self.output_file)
        diff_output = self.run_diff(original_filename, self.output_file) if not r else ""

        return r, "Diff:\n" + diff_output

    # Test zebra.conf in FRR docker for a T2 chassis frontend (fe)
    def test_t2_chassis_fe_zebra_frr(self):
        self.assertTrue(*self.run_case(self.t2_chassis_fe_minigraph, 'zebra/zebra.conf.j2', 't2-chassis-fe-zebra.conf'))

    # Test zebra.conf in FRR docker for a T2 chassis frontend (fe) switch with specified VNI
    def test_t2_chassis_fe_vni_zebra_frr(self):
        self.assertTrue(*self.run_case(self.t2_chassis_fe_vni_minigraph, 'zebra/zebra.conf.j2', 't2-chassis-fe-vni-zebra.conf'))

    # Test bgpd.conf in FRR docker for a T2 chassis frontend (fe)
    def test_t2_chassis_frontend_bgpd_frr(self):
        self.assertTrue(*self.run_case(self.t2_chassis_fe_minigraph, 'bgpd/bgpd.conf.j2', 't2-chassis-fe-bgpd.conf'))

