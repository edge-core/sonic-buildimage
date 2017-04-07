import filecmp
import os
import subprocess

from unittest import TestCase

class TestAcl(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.acl_script_file = os.path.join(self.test_dir, '..', 'translate_acl')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_minigraph_everflow = os.path.join(self.test_dir, 't0-sample-graph-everflow.xml')
        self.t0_acl = os.path.join(self.test_dir, 't0-sample-acl.json')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')

    def run_script(self, argument):
        print 'CMD: sonic-cfggen ' + argument
        output = ''
        try:
            output = subprocess.check_output(self.script_file + ' ' + argument, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, (p):
            print 'CalledProcessError: CMD:%s returncode:%s' % (p.cmd, p.returncode)
            print p.output
        return output

    def run_acl_script(self, argument):
        print 'CMD: translate_acl ' + argument
        output = ''
        try:
            output = subprocess.check_output(self.acl_script_file + ' ' + argument, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, (p):
            print 'CalledProcessError: CMD:%s returncode:%s' % (p.cmd, p.returncode)
            print p.output
        return output

    def test_translate_acl(self):
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -o ' + self.test_dir + ' ' + self.t0_acl
        self.run_acl_script(argument)
        for filename in ['rules_for_dataacl.json','table_dataacl.json']:
            sample_output_file = os.path.join(self.test_dir, 'sample_output', filename)
            output_file = os.path.join(self.test_dir, filename)
            assert filecmp.cmp(sample_output_file, output_file)

    def test_translate_everflow(self):
        argument = '-m ' + self.t0_minigraph_everflow + ' -p ' + self.t0_port_config + ' -o ' + self.test_dir + ' ' + self.t0_acl
        self.run_acl_script(argument)
        for filename in ['rules_for_everflow.json','table_everflow.json']:
            sample_output_file = os.path.join(self.test_dir, 'sample_output', filename)
            output_file = os.path.join(self.test_dir, filename)
            assert filecmp.cmp(sample_output_file, output_file)

    def tearDown(self):
        for filename in ['rules_for_dataacl.json','table_dataacl.json','rules_for_everflow.json','table_everflow.json']:
            try:
                os.remove(os.path.join(self.test_dir, filename))
            except OSError:
                pass
