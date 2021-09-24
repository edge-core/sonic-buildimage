TEST_DATA = [ 
    [
        "DHCPv6_Helpers",
        {
            "config_db": {
                "DHCP_RELAY": {
                    "Vlan1000": {
                        "dhcpv6_servers": [
                            "fc02:2000::1",
                            "fc02:2000::2"
                        ],
                        "dhcpv6_option|rfc6939_support": "true"
                    }
                }
            },
        },
    ],
]
