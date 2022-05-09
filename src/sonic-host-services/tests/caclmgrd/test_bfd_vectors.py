from unittest.mock import call
import subprocess

"""
    caclmgrd bfd test vector
"""
CACLMGRD_BFD_TEST_VECTOR = [
    [
        "BFD_SESSION_TEST",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
            },
            "expected_subprocess_calls": [
                call("iptables -I INPUT 2 -p udp -m multiport --dports 3784,4784 -j ACCEPT", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -I INPUT 2 -p udp -m multiport --dports 3784,4784 -j ACCEPT", shell=True, universal_newlines=True, stdout=subprocess.PIPE)
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
        }
    ]
]
