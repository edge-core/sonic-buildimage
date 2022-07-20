from unittest.mock import call
import subprocess

"""
    caclmgrd soc test vector
"""
CACLMGRD_SOC_TEST_VECTOR = [
    [
        "SOC_SESSION_TEST",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
                "MUX_CABLE": {
                    "Ethernet4": {
                        "cable_type": "active-active",
                        "soc_ipv4": "192.168.1.0/32",
                    }
                },
                "LOOPBACK_INTERFACE": {
                    "Loopback3|10.10.10.10/32": {
                        "NULL": "NULL",
                    }
                },
                "FEATURE": {
                },
            },
            "expected_subprocess_calls": [
                call("iptables -t nat -A POSTROUTING --destination 192.168.1.0/32 -j SNAT --to-source 10.10.10.10",shell=True, universal_newlines=True, stdout=-1)
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
        }
    ]
]
