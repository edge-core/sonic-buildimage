from unittest import TestCase
import subprocess
import os
import json
import ast

# Global Variable
PLATFORM_OUTPUT_FILE = "platform_output.json"

class TestCfgGenPlatformJson(TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.sample_graph_simple = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.platform_json = os.path.join(self.test_dir, 'sample_platform.json')
        self.hwsku_json = os.path.join(self.test_dir, 'sample_hwsku.json')

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

    def test_dummy_run(self):
        argument = ''
        output = self.run_script(argument)
        self.assertEqual(output, '')

    def test_print_data(self):
        argument = '-m "' + self.sample_graph_simple + '" --print-data'
        output = self.run_script(argument)
        self.assertTrue(len(output.strip()) > 0)

    # Check whether all interfaces present or not as per platform.json
    def test_platform_json_interfaces_keys(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.platform_json + '" -S "' + self.hwsku_json + '" -v "PORT.keys()"'
        output = self.run_script(argument)
        expected = "['Ethernet8', 'Ethernet9', 'Ethernet36', 'Ethernet98', 'Ethernet0', 'Ethernet6', 'Ethernet4', 'Ethernet109', 'Ethernet108', 'Ethernet18', 'Ethernet100', 'Ethernet34', 'Ethernet104', 'Ethernet106', 'Ethernet94', 'Ethernet126', 'Ethernet96', 'Ethernet124', 'Ethernet90', 'Ethernet91', 'Ethernet92', 'Ethernet93', 'Ethernet50', 'Ethernet51', 'Ethernet52', 'Ethernet53', 'Ethernet54', 'Ethernet99', 'Ethernet56', 'Ethernet113', 'Ethernet76', 'Ethernet74', 'Ethernet39', 'Ethernet72', 'Ethernet73', 'Ethernet70', 'Ethernet71', 'Ethernet32', 'Ethernet33', 'Ethernet16', 'Ethernet111', 'Ethernet10', 'Ethernet11', 'Ethernet12', 'Ethernet13', 'Ethernet58', 'Ethernet19', 'Ethernet59', 'Ethernet38', 'Ethernet78', 'Ethernet68', 'Ethernet14', 'Ethernet89', 'Ethernet88', 'Ethernet118', 'Ethernet119', 'Ethernet116', 'Ethernet114', 'Ethernet80', 'Ethernet112', 'Ethernet86', 'Ethernet110', 'Ethernet84', 'Ethernet31', 'Ethernet49', 'Ethernet48', 'Ethernet46', 'Ethernet30', 'Ethernet29', 'Ethernet40', 'Ethernet120', 'Ethernet28', 'Ethernet66', 'Ethernet60', 'Ethernet64', 'Ethernet44', 'Ethernet20', 'Ethernet79', 'Ethernet69', 'Ethernet24', 'Ethernet26']"

        self.assertEqual(sorted(output.strip()), sorted(expected))

    # Check specific Interface with it's proper configuration as per platform.json
    def test_platform_json_specific_ethernet_interfaces(self):

        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.platform_json + '" -S "' + self.hwsku_json  + '" -v "PORT[\'Ethernet8\']"'
        output = self.run_script(argument)
        expected = "{'index': '3', 'lanes': '8', 'description': 'Eth3/1', 'admin_status': 'up', 'mtu': '9100', 'alias': 'Eth3/1', 'pfc_asym': 'off', 'speed': '25000'}"
        self.assertEqual(output.strip(), expected)

        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.platform_json + '" -S "' + self.hwsku_json  + '" -v "PORT[\'Ethernet112\']"'
        output = self.run_script(argument)
        expected = "{'index': '29', 'lanes': '112', 'description': 'Eth29/1', 'admin_status': 'up', 'mtu': '9100', 'alias': 'Eth29/1', 'pfc_asym': 'off', 'speed': '25000'}"
        self.assertEqual(output.strip(), expected)

    # Check all Interface with it's proper configuration as per platform.json
    def test_platform_json_all_ethernet_interfaces(self):
        argument = '-m "' + self.sample_graph_simple + '" -p "' + self.platform_json + '" -S "' + self.hwsku_json  + '" -v "PORT"'
        output = self.run_script(argument)

        sample_file = os.path.join(self.test_dir, 'sample_output', PLATFORM_OUTPUT_FILE)
        fh = open(sample_file, 'rb')
        fh_data = json.load(fh)
        fh.close()

        output_dict = ast.literal_eval(output.strip())
        expected = ast.literal_eval(json.dumps(fh_data))
        self.assertDictEqual(output_dict, expected)
