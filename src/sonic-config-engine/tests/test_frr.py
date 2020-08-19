from unittest import TestCase
import subprocess
import os
import filecmp


class TestCfgGen(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.output_file = os.path.join(self.test_dir, 'output')

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass


    def run_script(self, argument, check_stderr=False):
#        print '\n    Running sonic-cfggen ' + argument
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

    def run_case(self, template, target):
        template_dir = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-fpm-frr', "frr")
        conf_template = os.path.join(template_dir, template)
        constants = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'constants', 'constants.yml')
        cmd_args = self.t0_minigraph, self.t0_port_config, constants, conf_template, template_dir, self.output_file
        cmd = "-m %s -p %s -y %s -t %s -T %s > %s" % cmd_args
        self.run_script(cmd)

        original_filename = os.path.join(self.test_dir, 'sample_output', target)
        r = filecmp.cmp(original_filename, self.output_file)
        diff_output = self.run_diff(original_filename, self.output_file) if not r else ""

        return r, "Diff:\n" + diff_output


    def test_config_frr(self):
        self.assertTrue(*self.run_case('frr.conf.j2', 'frr.conf'))

    def test_bgpd_frr(self):
        self.assertTrue(*self.run_case('bgpd/bgpd.conf.j2', 'bgpd_frr.conf'))

    def test_zebra_frr(self):
        self.assertTrue(*self.run_case('zebra/zebra.conf.j2', 'zebra_frr.conf'))

    def test_staticd_frr(self):
        self.assertTrue(*self.run_case('staticd/staticd.conf.j2', 'staticd_frr.conf'))

