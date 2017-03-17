from unittest import TestCase
import subprocess
import os

class TestCfgGen(TestCase):
    
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.sample_graph = os.path.join(self.test_dir, 'sample_graph.xml')

    def run_script(self, argument):
        print '\n    Running sonic-cfggen ' + argument
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
    
    def test_minigraph_sku(self):
        argument = '-v minigraph_hwsku -m "' + self.sample_graph + '"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'Force10-Z9100')
    
    def test_print_data(self):
        argument = '-m "' + self.sample_graph + '" --print-data'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)
    
    def test_jinja_expression(self):
        argument = '-m "' + self.sample_graph + '" -v "minigraph_devices[minigraph_hostname][\'type\']"'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'LeafRouter')
    
    def test_print_alias_mapping(self):
        argument = '-s'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)
    
    def test_additional_json_data(self):
        argument = '-a \'{"key1":"value1"}\' -v key1'
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1')

    def test_read_yaml(self):
        argument = '-v yml_item -y ' + os.path.join(self.test_dir, 'test.yml')
        output = self.run_script(argument)
        self.assertEqual(output.strip(), '[\'value1\', \'value2\']')
    
    def test_render_template(self):
        argument = '-y ' + os.path.join(self.test_dir, 'test.yml') + ' -t' + os.path.join(self.test_dir, 'test.j2')
        output = self.run_script(argument)
        self.assertEqual(output.strip(), 'value1\nvalue2')

