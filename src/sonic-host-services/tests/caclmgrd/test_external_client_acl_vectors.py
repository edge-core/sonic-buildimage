from unittest.mock import call

"""
    caclmgrd test external_client_acl vector
"""
EXTERNAL_CLIENT_ACL_TEST_VECTOR = [
    [
        "Test for EXTERNAL_CLIENT_ACL with no dest port configured.",
        {
            "config_db": {
                "ACL_TABLE": {
                    "EXTERNAL_CLIENT_ACL": {
                        "stage": "INGRESS",
                        "type": "CTRLPLANE",
                        "services": [
                            "EXTERNAL_CLIENT"
                        ]
                    }
                },
                "ACL_RULE": {
                    "EXTERNAL_CLIENT_ACL|DEFAULT_RULE": {
                        "ETHER_TYPE": "2048",
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "1"
                    },
                    "EXTERNAL_CLIENT_ACL|RULE_1": {
                        "PACKET_ACTION": "ACCEPT",
                        "PRIORITY": "9998",
                        "SRC_IP": "20.0.0.55/32"
                    },
                },
                "DEVICE_METADATA": {
                    "localhost": {
                    }
                },
                "FEATURE": {},
            },
            "return": [
            ],
        }
    ],
    [
        "Test single IPv4 dst port + src ip for EXTERNAL_CLIENT_ACL",
        {
            "config_db": {
                "ACL_TABLE": {
                    "EXTERNAL_CLIENT_ACL": {
                        "stage": "INGRESS",
                        "type": "CTRLPLANE",
                        "services": [
                            "EXTERNAL_CLIENT"
                        ]
                    }
                },
                "ACL_RULE": {
                    "EXTERNAL_CLIENT_ACL|DEFAULT_RULE": {
                        "ETHER_TYPE": "2048",
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "1"
                    },
                    "EXTERNAL_CLIENT_ACL|RULE_1": {
                        "L4_DST_PORT": "8081",
                        "PACKET_ACTION": "ACCEPT",
                        "PRIORITY": "9998",
                        "SRC_IP": "20.0.0.55/32"
                    },
                },
                "DEVICE_METADATA": {
                    "localhost": {
                    }
                },
                "FEATURE": {},
            },
            "return": [
                "iptables -A INPUT -p tcp -s 20.0.0.55/32 --dport 8081 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 8081 -j DROP"
            ],
        }
    ],
    [
        "Test IPv4 dst port range + src ip forEXTERNAL_CLIENT_ACL",
        {
            "config_db": {
                "ACL_TABLE": {
                    "EXTERNAL_CLIENT_ACL": {
                        "stage": "INGRESS",
                        "type": "CTRLPLANE",
                        "services": [
                            "EXTERNAL_CLIENT"
                        ]
                    }
                },
                "ACL_RULE": {
                    "EXTERNAL_CLIENT_ACL|DEFAULT_RULE": {
                        "ETHER_TYPE": "2048",
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "1"
                    },
                    "EXTERNAL_CLIENT_ACL|RULE_1": {
                        "L4_DST_PORT_RANGE": "8081-8083",
                        "PACKET_ACTION": "ACCEPT",
                        "PRIORITY": "9998",
                        "SRC_IP": "20.0.0.55/32"
                    },
                },
                "DEVICE_METADATA": {
                    "localhost": {
                    }
                },
                "FEATURE": {},
            },
            "return": [
                "iptables -A INPUT -p tcp -s 20.0.0.55/32 --dport 8081 -j ACCEPT",
                "iptables -A INPUT -p tcp -s 20.0.0.55/32 --dport 8082 -j ACCEPT",
                "iptables -A INPUT -p tcp -s 20.0.0.55/32 --dport 8083 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 8081 -j DROP",
                "iptables -A INPUT -p tcp --dport 8082 -j DROP",
                "iptables -A INPUT -p tcp --dport 8083 -j DROP",
            ],
        }
    ],
    [
        "Test IPv6 single dst port range + src ip forEXTERNAL_CLIENT_ACL",
        {
            "config_db": {
                "ACL_TABLE": {
                    "EXTERNAL_CLIENT_ACL": {
                        "stage": "INGRESS",
                        "type": "CTRLPLANE",
                        "services": [
                            "EXTERNAL_CLIENT"
                        ]
                    }
                },
                "ACL_RULE": {
                    "EXTERNAL_CLIENT_ACL|DEFAULT_RULE": {
                        "ETHER_TYPE": "2048",
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "1"
                    },
                    "EXTERNAL_CLIENT_ACL|RULE_1": {
                        "L4_DST_PORT": "8081",
                        "PACKET_ACTION": "ACCEPT",
                        "PRIORITY": "9998",
                        "SRC_IP": "2001::2/128"
                    },
                },
                "DEVICE_METADATA": {
                    "localhost": {
                    }
                },
                "FEATURE": {},
            },
            "return": [
                "iptables -A INPUT -p tcp -s 2001::2/128 --dport 8081 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 8081 -j DROP"
            ],
        }
    ],
    [
        "Test IPv6 dst port range + src ip forEXTERNAL_CLIENT_ACL",
        {
            "config_db": {
                "ACL_TABLE": {
                    "EXTERNAL_CLIENT_ACL": {
                        "stage": "INGRESS",
                        "type": "CTRLPLANE",
                        "services": [
                            "EXTERNAL_CLIENT"
                        ]
                    }
                },
                "ACL_RULE": {
                    "EXTERNAL_CLIENT_ACL|DEFAULT_RULE": {
                        "ETHER_TYPE": "2048",
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "1"
                    },
                    "EXTERNAL_CLIENT_ACL|RULE_1": {
                        "L4_DST_PORT_RANGE": "8081-8083",
                        "PACKET_ACTION": "ACCEPT",
                        "PRIORITY": "9998",
                        "SRC_IP": "2001::2/128"
                    },
                },
                "DEVICE_METADATA": {
                    "localhost": {
                    }
                },
                "FEATURE": {},
            },
            "return": [
                "iptables -A INPUT -p tcp -s 2001::2/128 --dport 8081 -j ACCEPT",
                "iptables -A INPUT -p tcp -s 2001::2/128 --dport 8082 -j ACCEPT",
                "iptables -A INPUT -p tcp -s 2001::2/128 --dport 8083 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 8081 -j DROP",
                "iptables -A INPUT -p tcp --dport 8082 -j DROP",
                "iptables -A INPUT -p tcp --dport 8083 -j DROP",
            ],
        }
    ]
]
