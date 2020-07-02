from unittest import TestCase
import subprocess

class TestPfxFilter(TestCase):
    def test_comprehensive(self):
        # Generate output
        data_dir = "tests/data/pfx_filter"
        cmd = "./sonic-cfggen -j %s/param_1.json -t %s/tmpl_1.txt.j2 > /tmp/result_1.txt" % (data_dir, data_dir)
        subprocess.check_output(cmd, shell=True)
        # Compare outputs
        cmd = "diff -u tests/data/pfx_filter/result_1.txt /tmp/result_1.txt"
        try:
            res = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            assert False, "Wrong output. return code: %d, Diff: %s" % (e.returncode, e.output)
