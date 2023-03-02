from unittest.mock import call

"""
    caclmgrd chassis midplane test vector
"""
CACLMGRD_CHASSIS_MIDPLANE_TEST_VECTOR = [
    [
        "Allow chassis midlane traffic",
        {
            "return": [
                "iptables -A INPUT -i eth1-midplane -j ACCEPT"
            ]
        }
    ]
]
