from bgpcfgd.directory import Directory
from bgpcfgd.template import TemplateFabric
from mock import MagicMock, patch
from copy import deepcopy
import swsscommon_test
import bgpcfgd

with patch.dict("sys.modules", swsscommon=swsscommon_test):
    from bgpcfgd.managers_bbr import BBRMgr

global_constants = {
    "bgp": {
        "allow_list": {
            "enabled": True,
            "default_pl_rules": {
                "v4": [ "deny 0.0.0.0/0 le 17" ],
                "v6": [
                    "deny 0::/0 le 59",
                    "deny 0::/0 ge 65"
                ]
            }
        }
    }
}

#@patch('bgpcfgd.managers_bbr.log_info')
#@patch('bgpcfgd.managers_bbr.log_err')
#@patch('bgpcfgd.managers_bbr.log_crit')
def test_constructor():#m1, m2, m3):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr':   cfg_mgr,
        'tf':        TemplateFabric(),
        'constants': {},
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    assert not m.enabled
    assert len(m.bbr_enabled_pgs) == 0
    assert m.directory.get("CONFIG_DB", "BGP_BBR", "status") == "disabled"

@patch('bgpcfgd.managers_bbr.log_info')
@patch('bgpcfgd.managers_bbr.log_crit')
def set_handler_common(key, value,
                       is_enabled, is_valid, has_no_push_cmd_errors,
                       mocked_log_crit, mocked_log_info):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': global_constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    m.enabled = is_enabled
    prepare_config_return_value = [
                               ["vtysh", "-c", "clear bgp peer-group PEER_V4 soft in"],
                               ["vtysh", "-c", "clear bgp peer-group PEER_V6 soft in"]
                           ]
    m._BBRMgr__set_prepare_config = MagicMock(return_value = prepare_config_return_value)
    m.cfg_mgr.push_list = MagicMock(return_value = has_no_push_cmd_errors)
    m._BBRMgr__restart_peers = MagicMock()
    res = m.set_handler(key, value)
    assert res, "Returns always True"
    if not is_enabled:
        mocked_log_info.assert_called_with('BBRMgr::BBR is disabled. Drop the request')
    else:
        if is_valid:
            m._BBRMgr__set_prepare_config.assert_called_once_with(value["status"])
            m.cfg_mgr.push_list.assert_called_once_with(prepare_config_return_value)
            if has_no_push_cmd_errors:
                m._BBRMgr__restart_peers.assert_called_once()
            else:
                mocked_log_crit.assert_called_with("BBRMgr::can't apply configuration")
                m._BBRMgr__restart_peers.assert_not_called()
        else:
            m._BBRMgr__set_prepare_config.assert_not_called()
            m.cfg_mgr.push_list.assert_not_called()
            m._BBRMgr__restart_peers.assert_not_called()

def test_set_handler_1():
    set_handler_common("anything", {}, False, False, True)

def test_set_handler_2():
    set_handler_common("anything", {}, True, False, True)

def test_set_handler_3():
    set_handler_common("all", {"status": "enabled"}, True, True, True)

def test_set_handler_4():
    set_handler_common("all", {"status": "enabled"}, True, True, False)

@patch('bgpcfgd.managers_bbr.log_err')
def test_del_handler(mocked_log_err):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': global_constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    m.del_handler("anything")
    mocked_log_err.assert_called_with("The 'BGP_BBR' table shouldn't be removed from the db")

@patch('bgpcfgd.managers_bbr.log_info')
@patch('bgpcfgd.managers_bbr.log_err')
def __init_common(constants,
                  expected_log_info, expected_log_err, expected_bbr_enabled_pgs, expected_status,
                  mocked_log_err, mocked_log_info):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr':   cfg_mgr,
        'tf':        TemplateFabric(),
        'constants': constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    m._BBRMgr__init()
    assert m.bbr_enabled_pgs == expected_bbr_enabled_pgs
    assert m.directory.get("CONFIG_DB", "BGP_BBR", "status") == expected_status
    if expected_status == "enabled":
        assert m.enabled
    else:
        assert not m.enabled
    if expected_log_err is not None:
        mocked_log_err.assert_called_with(expected_log_err)
    if expected_log_info is not None:
        mocked_log_info.assert_called_with(expected_log_info)

def test___init_1():
    __init_common({}, None, "BBRMgr::Disabled: 'bgp' key is not found in constants", {}, "disabled")

def test___init_2():
    constants = deepcopy(global_constants)
    __init_common(constants, "BBRMgr::Disabled: not enabled in the constants", None, {}, "disabled")

def test___init_3():
    constants = deepcopy(global_constants)
    constants["bgp"]["bbr"] = { "123" : False }
    __init_common(constants, "BBRMgr::Disabled: not enabled in the constants", None, {}, "disabled")

def test___init_4():
    constants = deepcopy(global_constants)
    constants["bgp"]["bbr"] = { "enabled" : False }
    __init_common(constants, "BBRMgr::Disabled: not enabled in the constants", None, {}, "disabled")

def test___init_5():
    constants = deepcopy(global_constants)
    constants["bgp"]["bbr"] = { "enabled" : True }
    __init_common(constants, "BBRMgr::Disabled: no BBR enabled peers", None, {}, "disabled")

def test___init_6():
    expected_bbr_entries = {
                "PEER_V4": ["ipv4"],
                "PEER_V6": ["ipv6"],
    }
    constants = deepcopy(global_constants)
    constants["bgp"]["bbr"] = { "enabled" : True }
    constants["bgp"]["peers"] = {
        "general": {
            "bbr": expected_bbr_entries,
        }
    }
    __init_common(constants, 'BBRMgr::Initialized and enabled', None, expected_bbr_entries, "enabled")

@patch('bgpcfgd.managers_bbr.log_info')
def read_pgs_common(constants, expected_log_info, expected_bbr_enabled_pgs, mocked_log_info):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    res = m._BBRMgr__read_pgs()
    assert res == expected_bbr_enabled_pgs
    if expected_log_info is not None:
        mocked_log_info.assert_called_with(expected_log_info)

def test___read_pgs_no_configuration():
    read_pgs_common(global_constants, "BBRMgr::no 'peers' was found in constants", {})

def test___read_pgs_parse_configuration():
    expected_bbr_entries = {
                "PEER_V4": ["ipv4", "ipv6"],
                "PEER_V6": ["ipv6"],
    }
    constants = deepcopy(global_constants)
    constants["bgp"]["peers"] = {
        "general": {
            "bbr": expected_bbr_entries,
        },
        "dynamic": {
            "123": {
                "PEER_V8": ["ipv10", "ipv20"],
            }
        }
    }
    read_pgs_common(constants, None, expected_bbr_entries)

@patch('bgpcfgd.managers_bbr.log_err')
def __set_validation_common(key, data, expected_log_err, expected_result, mocked_log_err):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': global_constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    res = m._BBRMgr__set_validation(key, data)
    assert res == expected_result
    if expected_log_err is not None:
        mocked_log_err.assert_called_with(expected_log_err)

def test___set_validation_1():
    __set_validation_common("all1", {}, "Invalid key 'all1' for table 'BGP_BBR'. Only key value 'all' is supported", False)

def test___set_validation_2():
    __set_validation_common("all", {"stat": "enabled"}, "Invalid value '{'stat': 'enabled'}' for table 'BGP_BBR', key 'all'. Key 'status' in data is expected", False)

def test___set_validation_3():
    __set_validation_common("all", {"status": "enabled1"}, "Invalid value '{'status': 'enabled1'}' for table 'BGP_BBR', key 'all'. Only 'enabled' and 'disabled' are supported", False)

def test___set_validation_4():
    __set_validation_common("all", {"status": "enabled"}, None, True)

def test___set_validation_5():
    __set_validation_common("all", {"status": "disabled"}, None, True)

def __set_prepare_config_common(status, bbr_enabled_pgs, expected_cmds):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': global_constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    m.directory.data = {"CONFIG_DB__DEVICE_METADATA":
        {
            "localhost": {
                "bgp_asn": "65500"
            }
        }
    }
    m.bbr_enabled_pgs = bbr_enabled_pgs
    cmds = m._BBRMgr__set_prepare_config(status)
    assert cmds == expected_cmds

def test___set_prepare_config_enabled():
    __set_prepare_config_common("enabled", {
                "PEER_V4": ["ipv4", "ipv6"],
                "PEER_V6": ["ipv6"],
        }, [
        'router bgp 65500',
        ' address-family ipv4',
        '  neighbor PEER_V4 allowas-in 1',
        ' address-family ipv6',
        '  neighbor PEER_V4 allowas-in 1',
        '  neighbor PEER_V6 allowas-in 1',
    ])

def test___set_prepare_config_disabled():
    __set_prepare_config_common("disabled", {
                "PEER_V4": ["ipv4", "ipv6"],
                "PEER_V6": ["ipv6"],
        }, [
        'router bgp 65500',
        ' address-family ipv4',
        '  no neighbor PEER_V4 allowas-in 1',
        ' address-family ipv6',
        '  no neighbor PEER_V4 allowas-in 1',
        '  no neighbor PEER_V6 allowas-in 1',
    ])

@patch('bgpcfgd.managers_bbr.log_crit')
def __restart_peers_common(run_command_results, run_command_expects, last_log_crit_message, mocked_log_crit):
    cfg_mgr = MagicMock()
    common_objs = {
        'directory': Directory(),
        'cfg_mgr': cfg_mgr,
        'tf': TemplateFabric(),
        'constants': global_constants,
    }
    m = BBRMgr(common_objs, "CONFIG_DB", "BGP_BBR")
    m.bbr_enabled_pgs = {
        "PEER_V4": ["ipv4", "ipv6"],
        "PEER_V6": ["ipv6"],
    }
    def run_command_mock(cmd):
        assert cmd == run_command_expects[run_command_mock.run]
        res = run_command_results[run_command_mock.run]
        run_command_mock.run += 1
        return res
    run_command_mock.run = 0
    bgpcfgd.managers_bbr.run_command = run_command_mock
        #lambda cmd: (0, "", "")
    m._BBRMgr__restart_peers()
    if last_log_crit_message is not None:
        mocked_log_crit.assert_called_with(last_log_crit_message)

def test___restart_peers_1():
    __restart_peers_common([(0, "", ""), (0, "", "")],
                           [
                               ["vtysh", "-c", "clear bgp peer-group PEER_V4 soft in"],
                               ["vtysh", "-c", "clear bgp peer-group PEER_V6 soft in"]
                           ],
                           None)

def test___restart_peers_2():
    __restart_peers_common([(1, "out1", "err1"), (0, "", "")],
                           [
                               ["vtysh", "-c", "clear bgp peer-group PEER_V4 soft in"],
                               ["vtysh", "-c", "clear bgp peer-group PEER_V6 soft in"]
                           ],
                           "BBRMgr::Can't restart bgp peer-group 'PEER_V4'. rc='1', out='out1', err='err1'")
