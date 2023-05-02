from unittest.mock import call

"""
    caclmgrd chassis midplane test vector
"""
CACLMGRD_CHASSIS_MIDPLANE_TEST_VECTOR = [
    [
        "Allow chassis midlane traffic",
        {
            "return": [
                "iptables -A INPUT -s 1.0.0.33 -d 1.0.0.33 -j ACCEPT",
                "iptables -A INPUT -i eth1-midplane -j ACCEPT"
            ]
        }
    ]
]
