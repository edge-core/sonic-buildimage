import os
import subprocess


from app.config import ConfigMgr
from .test_templates import compress_comments, write_result


TEMPLATE_PATH = os.path.abspath('../../dockers/docker-fpm-frr/frr')
DATA_PATH = "tests/data/sonic-cfggen/"
CONSTANTS_PATH = os.path.abspath('../../files/image_config/constants/constants.yml')


def run_test(name, template_path, json_path, match_path):
    template_path = os.path.join(TEMPLATE_PATH, template_path)
    json_path = os.path.join(DATA_PATH, json_path)
    cfggen = os.path.abspath("../sonic-config-engine/sonic-cfggen")
    command = [cfggen, "-T", TEMPLATE_PATH, "-t", template_path, "-y", json_path]
    p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert p.returncode == 0, "sonic-cfggen for %s test returned %d code. stderr='%s'" % (name, p.returncode, stderr)
    raw_generated_result = stdout
    assert "None" not in raw_generated_result, "Test %s" % name
    canonical_generated_result = ConfigMgr.to_canonical(raw_generated_result)
    match_path = os.path.join(DATA_PATH, match_path)
    # only for development write_result(match_path, raw_generated_result)
    with open(match_path) as result_fp:
        raw_saved_result = result_fp.read()
    canonical_saved_result = ConfigMgr.to_canonical(raw_saved_result)
    assert canonical_saved_result == canonical_generated_result, "Test %s" % name


def test_bgpd_main_conf_base():
    run_test("Base bgpd.main.conf.j2",
             "bgpd/bgpd.main.conf.j2",
             "bgpd.main.conf.j2/base.json",
             "bgpd.main.conf.j2/base.conf")

def test_bgpd_main_conf_comprehensive():
    run_test("Comprehensive bgpd.main.conf.j2",
             "bgpd/bgpd.main.conf.j2",
             "bgpd.main.conf.j2/all.json",
             "bgpd.main.conf.j2/all.conf")

def test_bgpd_main_conf_defaults():
    run_test("Defaults bgpd.main.conf.j2",
             "bgpd/bgpd.main.conf.j2",
             "bgpd.main.conf.j2/defaults.json",
             "bgpd.main.conf.j2/defaults.conf")

def test_tsa_isolate():
    run_test("tsa/bgpd.tsa.isolate.conf.j2",
             "bgpd/tsa/bgpd.tsa.isolate.conf.j2",
             "tsa/isolate.json",
             "tsa/isolate.conf")

def test_tsa_unisolate():
    run_test("tsa/bgpd.tsa.unisolate.conf.j2",
             "bgpd/tsa/bgpd.tsa.unisolate.conf.j2",
             "tsa/unisolate.json",
             "tsa/unisolate.conf")

def test_common_daemons():
    run_test("daemons.common.conf.j2",
             "common/daemons.common.conf.j2",
             "common/daemons.common.conf.json",
             "common/daemons.common.conf")

def test_common_functions():
    run_test("functions.conf.j2",
             "common/functions.conf.j2",
             "common/functions.conf.json",
             "common/functions.conf")

def test_staticd_default_route():
    run_test("staticd.default_route.conf.j2",
             "staticd/staticd.default_route.conf.j2",
             "staticd/staticd.default_route.conf.json",
             "staticd/staticd.default_route.conf")

def test_staticd():
    run_test("staticd.conf.j2",
             "staticd/staticd.conf.j2",
             "staticd/staticd.conf.json",
             "staticd/staticd.conf")

def test_zebra_interfaces():
    run_test("zebra.interfaces.conf.j2",
             "zebra/zebra.interfaces.conf.j2",
             "zebra/interfaces.json",
             "zebra/interfaces.conf")

def test_zebra_set_src():
    run_test("zebra.set_src.conf.j2",
             "zebra/zebra.set_src.conf.j2",
             "zebra/set_src.json",
             "zebra/set_src.conf")

def test_zebra():
    run_test("zebra.conf.j2",
             "zebra/zebra.conf.j2",
             "zebra/zebra.conf.json",
             "zebra/zebra.conf")

def test_isolate():
    run_test("isolate.j2",
             "isolate.j2",
             "isolate/isolate.json",
             "isolate/isolate")

def test_unisolate():
    run_test("unisolate.j2",
             "unisolate.j2",
             "isolate/unisolate.json",
             "isolate/unisolate")

def test_frr_conf():
    run_test("frr.conf.j2",
             "frr.conf.j2",
             "frr.conf.j2/all.json",
             "frr.conf.j2/all.conf")

def test_l3vpn_base():
    run_test("bgpd spine_chassis_frontend_router.conf.j2",
             "bgpd/bgpd.spine_chassis_frontend_router.conf.j2",
             "bgpd.spine_chassis_frontend_router.conf.j2/base.json",
             "bgpd.spine_chassis_frontend_router.conf.j2/base.conf")

def test_bgp_conf_all():
    run_test("bgpd/bgpd.conf",
             "bgpd/bgpd.conf.j2",
             "bgpd.conf.j2/all.json",
             "bgpd.conf.j2/all.conf")
