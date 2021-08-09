from unittest.mock import call

"""
    caclmgrd dhcp test vector
"""
CACLMGRD_DHCP_TEST_VECTOR = [
    [
        "Active_Present",
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
        },
    ],
    [
        "Active_Absent",
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
        },
    ],
    [
        "Standby_Present",
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
        },
    ],
    [
        "Standby_Absent",
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
        },
    ],
    [
        "Unknown_Present",
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
        },
    ],
    [
        "Uknown_Absent",
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
        },
    ],
]
