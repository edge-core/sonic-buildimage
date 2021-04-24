from unittest.mock import call

"""
    hostcfgd test radius vector
"""
HOSTCFGD_TEST_RADIUS_VECTOR = [
    [
        "RADIUS",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "hostname": "radius",
                    }
                },
                "FEATURE": {
                    "dhcp_relay": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled"
                    },
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
                        }
                },
                "AAA": {
                    "authentication": {
                        "login": "radius,local",
                        "debug": "True",
                    }
                },
                "RADIUS": {
                    "global": {
                        "nas_ip": "10.10.10.10",
                        "auth_port": "1645",
                        "auth_type": "mschapv2",
                        "retransmit": "2",
                        "timeout": "3",
                        "passkey": "pass",
                    }
                },
                "RADIUS_SERVER": {
                    "10.10.10.1": {
                        "auth_type": "pap",
                        "retransmit": "1",
                        "timeout": "1",
                        "passkey": "pass1",
                    },
                    "10.10.10.2": {
                        "auth_type": "chap",
                        "retransmit": "2",
                        "timeout": "2",
                        "passkey": "pass2",
                    }
                },
            },
            "expected_config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "hostname": "radius",
                    }
                },
                "FEATURE": {
                    "dhcp_relay": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled"
                    },
                },
                "AAA": {
                    "authentication": {
                        "login": "radius,local",
                        "debug": "True",
                    }
                },
                "RADIUS": {
                    "global": {
                        "nas_ip": "10.10.10.10",
                        "auth_port": "1645",
                        "auth_type": "mschapv2",
                        "retransmit": "2",
                        "timeout": "3",
                        "passkey": "pass",
                    }
                },
                "RADIUS_SERVER": {
                    "10.10.10.1": {
                        "auth_type": "pap",
                        "retransmit": "1",
                        "timeout": "1",
                        "passkey": "pass1",
                    },
                    "10.10.10.2": {
                        "auth_type": "chap",
                        "retransmit": "2",
                        "timeout": "2",
                        "passkey": "pass2",
                    }
                },
            },
            "expected_subprocess_calls": [
                call("service aaastatsd start", shell=True),
            ],
        }
    ],
    [
        "LOCAL",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "hostname": "local",
                    }
                },
                "FEATURE": {
                    "dhcp_relay": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled"
                    },
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
                        }
                },
                "AAA": {
                    "authentication": {
                        "login": "local",
                        "debug": "True",
                    }
                },
            },
            "expected_config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "hostname": "local",
                    }
                },
                "FEATURE": {
                    "dhcp_relay": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled"
                    },
                },
                "AAA": {
                    "authentication": {
                        "login": "local",
                        "debug": "True",
                    }
                },
            },
            "expected_subprocess_calls": [
                call("service aaastatsd start", shell=True),
            ],
        },
    ],
]
