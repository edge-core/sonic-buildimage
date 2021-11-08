from unittest.mock import call

"""
    caclmgrd dhcp test vector
"""
CACLMGRD_DHCP_TEST_VECTOR = [
    [
        "Active_Present_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "active"}),
                ("Ethernet8", {"state": "active"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --delete DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
                call("iptables --delete DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": None,
        },
    ],
    [
        "Active_Present_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "active"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
                call("iptables --delete DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": "0x67004",
        },
    ],
    [
        "Active_Absent_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "active"}),
                ("Ethernet8", {"state": "active"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": None,
        },
    ],
    [
        "Active_Absent_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "active"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": "0x67004",
        },
    ],
    [
        "Standby_Present_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "standby"}),
                ("Ethernet8", {"state": "standby"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": None,
        },
    ],
    [
        "Standby_Present_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "standby"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": "0x67004",
        },
    ],
    [
        "Standby_Absent_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "standby"}),
                ("Ethernet8", {"state": "standby"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --insert DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
                call("iptables --insert DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": None,
        },
    ],
    [
        "Standby_Absent_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "standby"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
                call("iptables --insert DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": "0x67004",
        },
    ],
    [
        "Unknown_Present_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "unknown"}),
                ("Ethernet8", {"state": "unknown"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --delete DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
                call("iptables --delete DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": None,
        },
    ],
    [
        "Unknown_Present_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "unknown"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
                call("iptables --delete DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
            "mark": "0x67004",
        },
    ],
    [
        "Uknown_Absent_Interface",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "unknown"}),
                ("Ethernet8", {"state": "unknown"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m physdev --physdev-in Ethernet4 -j DROP", shell=True),
                call("iptables --check DHCP -m physdev --physdev-in Ethernet8 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": None,
        },
    ],
    [
        "Uknown_Absent_Mark",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "mux_update": [
                ("Ethernet4", {"state": "unknown"}),
            ],
            "expected_subprocess_calls": [
                call("iptables --check DHCP -m mark --mark 0x67004 -j DROP", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 1,
            "mark": "0x67004",
        },
    ],
]
