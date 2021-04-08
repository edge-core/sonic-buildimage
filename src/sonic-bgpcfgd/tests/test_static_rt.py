from unittest.mock import MagicMock, patch

from bgpcfgd.directory import Directory
from bgpcfgd.template import TemplateFabric
from bgpcfgd.managers_static_rt import StaticRouteMgr
from collections import Counter

def constructor():
    cfg_mgr = MagicMock()

    common_objs = {
        'directory': Directory(),
        'cfg_mgr':   cfg_mgr,
        'tf':        TemplateFabric(),
        'constants': {},
    }

    mgr = StaticRouteMgr(common_objs, "CONFIG_DB", "STATIC_ROUTE")
    assert len(mgr.static_routes) == 0

    return mgr

def set_del_test(mgr, op, args, expected_ret, expected_cmds):
    set_del_test.push_list_called = False
    def push_list(cmds):
        set_del_test.push_list_called = True
        assert Counter(cmds) == Counter(expected_cmds) # check if commands are expected (regardless of the order)
        max_del_idx = -1
        min_set_idx = len(cmds)
        for idx in range(len(cmds)):
            if cmds[idx].startswith('no') and idx > max_del_idx:
                max_del_idx = idx
            if not cmds[idx].startswith('no') and idx < min_set_idx:
                min_set_idx = idx
        assert max_del_idx < min_set_idx, "DEL command comes after SET command" # DEL commands should be done first
        return True
    mgr.cfg_mgr.push_list = push_list

    if op == "SET":
        ret = mgr.set_handler(*args)
        assert ret == expected_ret
    elif op == "DEL":
        mgr.del_handler(*args)
    else:
        assert False, "Wrong operation"

    if expected_cmds:
        assert set_del_test.push_list_called, "cfg_mgr.push_list wasn't called"
    else:
        assert not set_del_test.push_list_called, "cfg_mgr.push_list was called"

def test_set():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("10.1.0.0/24", {
            "nexthop": "10.0.0.57",
        }),
        True,
        [
            "ip route 10.1.0.0/24 10.0.0.57"
        ]
    )

def test_set_nhvrf():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|10.1.1.0/24", {
            "nexthop": "10.0.0.57",
            "ifname": "PortChannel0001",
            "distance": "10",
            "nexthop-vrf": "nh_vrf",
            "blackhole": "false",
        }),
        True,
        [
            "ip route 10.1.1.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf"
        ]
    )

def test_set_blackhole():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|10.1.2.0/24", {
            "nexthop": "10.0.0.57",
            "ifname": "PortChannel0001",
            "distance": "10",
            "nexthop-vrf": "nh_vrf",
            "blackhole": "true",
        }),
        True,
        [
            "ip route 10.1.2.0/24 blackhole 10"
        ]
    )

def test_set_vrf():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57",
            "ifname": "PortChannel0001",
            "distance": "10",
            "nexthop-vrf": "nh_vrf",
            "blackhole": "false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED"
        ]
    )

def test_set_ipv6():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|fc00:10::/64", {
            "nexthop": "fc00::72",
            "ifname": "PortChannel0001",
            "distance": "10",
            "nexthop-vrf": "",
            "blackhole": "false",
        }),
        True,
        [
            "ipv6 route fc00:10::/64 fc00::72 PortChannel0001 10"
        ]
    )

def test_set_nh_only():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 30 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_ifname_only():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_with_empty_ifname():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_with_empty_nh():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,,",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_del():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )
    set_del_test(
        mgr,
        "DEL",
        ("vrfRED|10.1.3.0/24",),
        True,
        [
            "no ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "no ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "no ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_same_route():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "40,50,60",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "no ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "no ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "no ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 40 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 50 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 60 nexthop-vrf default vrf vrfRED"
        ]
    )

def test_set_add_del_nh():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003",
            "distance": "10,20,30",
            "nexthop-vrf": "nh_vrf,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.57 PortChannel0001 10 nexthop-vrf nh_vrf vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.59 PortChannel0002 20 vrf vrfRED",
            "ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED"
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59,10.0.0.61,10.0.0.63",
            "ifname": "PortChannel0001,PortChannel0002,PortChannel0003,PortChannel0004",
            "distance": "10,20,30,30",
            "nexthop-vrf": "nh_vrf,,default,",
            "blackhole": "false,false,false,",
        }),
        True,
        [
            "ip route 10.1.3.0/24 10.0.0.63 PortChannel0004 30 vrf vrfRED",
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("vrfRED|10.1.3.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59",
            "ifname": "PortChannel0001,PortChannel0002",
            "distance": "10,20",
            "nexthop-vrf": "nh_vrf,",
            "blackhole": "false,false",
        }),
        True,
        [
            "no ip route 10.1.3.0/24 10.0.0.61 PortChannel0003 30 nexthop-vrf default vrf vrfRED",
            "no ip route 10.1.3.0/24 10.0.0.63 PortChannel0004 30 vrf vrfRED",
        ]
    )

def test_set_add_del_nh_ethernet():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|20.1.3.0/24", {
            "nexthop": "20.0.0.57,20.0.0.59,20.0.0.61",
            "ifname": "Ethernet4,Ethernet8,Ethernet12",
            "distance": "10,20,30",
            "nexthop-vrf": "default,,default",
            "blackhole": "false,false,false",
        }),
        True,
        [
            "ip route 20.1.3.0/24 20.0.0.57 Ethernet4 10 nexthop-vrf default",
            "ip route 20.1.3.0/24 20.0.0.59 Ethernet8 20",
            "ip route 20.1.3.0/24 20.0.0.61 Ethernet12 30 nexthop-vrf default"
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("default|20.1.3.0/24", {
            "nexthop": "20.0.0.57,20.0.0.59,20.0.0.61,20.0.0.63",
            "ifname": "Ethernet4,Ethernet8,Ethernet12,Ethernet16",
            "distance": "10,20,30,30",
            "nexthop-vrf": "default,,default,",
            "blackhole": "false,false,false,",
        }),
        True,
        [
            "ip route 20.1.3.0/24 20.0.0.63 Ethernet16 30",
        ]
    )
    set_del_test(
        mgr,
        "SET",
        ("default|20.1.3.0/24", {
            "nexthop": "20.0.0.57,20.0.0.59",
            "ifname": "Ethernet4,Ethernet8",
            "distance": "10,20",
            "nexthop-vrf": "default,",
            "blackhole": "false,false",
        }),
        True,
        [
            "no ip route 20.1.3.0/24 20.0.0.61 Ethernet12 30 nexthop-vrf default",
            "no ip route 20.1.3.0/24 20.0.0.63 Ethernet16 30",
        ]
    )

@patch('bgpcfgd.managers_static_rt.log_debug')
def test_set_no_action(mocked_log_debug):
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|10.1.1.0/24", {
            "nexthop": "10.0.0.57",
            "ifname": "PortChannel0001",
            "blackhole": "true",
        }),
        True,
        [
            "ip route 10.1.1.0/24 blackhole"
        ]
    )

    set_del_test(
        mgr,
        "SET",
        ("default|10.1.1.0/24", {
            "nexthop": "10.0.0.59",
            "ifname": "PortChannel0002",
            "blackhole": "true",
        }),
        True,
        []
    )
    mocked_log_debug.assert_called_with("Nothing to update for static route default|10.1.1.0/24")

@patch('bgpcfgd.managers_static_rt.log_debug')
def test_del_no_action(mocked_log_debug):
    mgr = constructor()
    set_del_test(
        mgr,
        "DEL",
        ("default|10.1.1.0/24",),
        True,
        []
    )
    mocked_log_debug.assert_called_with("Nothing to update for static route default|10.1.1.0/24")

def test_set_invalid_arg():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|10.1.1.0/24", {
            "nexthop": "10.0.0.57,10.0.0.59",
            "ifname": "PortChannel0001",
        }),
        False,
        []
    )

@patch('bgpcfgd.managers_static_rt.log_err')
def test_set_invalid_blackhole(mocked_log_err):
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("default|10.1.1.0/24", {
            "nexthop": "",
            "ifname": "",
            "blackhole": "false",
        }),
        True,
        []
    )
    mocked_log_err.assert_called_with("Mandatory attribute not found for nexthop")

def test_set_invalid_ipaddr():
    mgr = constructor()
    set_del_test(
        mgr,
        "SET",
        ("10.1.0.0/24", {
            "nexthop": "invalid_ipaddress",
        }),
        False,
        []
    )
