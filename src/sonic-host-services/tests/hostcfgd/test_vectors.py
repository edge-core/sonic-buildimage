from unittest.mock import call

"""
    hostcfgd test vector
"""
HOSTCFGD_TEST_VECTOR = [
    [
        "DualTorCase",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "{% if 'subtype' in DEVICE_METADATA['localhost'] and DEVICE_METADATA['localhost']['subtype'] == 'DualToR' %}enabled{% else %}always_disabled{% endif %}"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_config_db": {
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "enabled"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_subprocess_calls": [
                call("sudo systemctl unmask dhcp_relay.service", shell=True),
                call("sudo systemctl enable dhcp_relay.service", shell=True),
                call("sudo systemctl start dhcp_relay.service", shell=True),
                call("sudo systemctl unmask mux.service", shell=True),
                call("sudo systemctl enable mux.service", shell=True),
                call("sudo systemctl start mux.service", shell=True),
                call("sudo systemctl unmask telemetry.service", shell=True),
                call("sudo systemctl unmask telemetry.timer", shell=True),
                call("sudo systemctl enable telemetry.timer", shell=True),
                call("sudo systemctl start telemetry.timer", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error')
            },
        },
    ],
    [
        "SingleToRCase",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "type": "ToR",
                    }
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "{% if 'subtype' in DEVICE_METADATA['localhost'] and DEVICE_METADATA['localhost']['subtype'] == 'DualToR' %}enabled{% else %}always_disabled{% endif %}"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_config_db": {
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "always_disabled"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_subprocess_calls": [
                call("sudo systemctl unmask dhcp_relay.service", shell=True),
                call("sudo systemctl enable dhcp_relay.service", shell=True),
                call("sudo systemctl start dhcp_relay.service", shell=True),
                call("sudo systemctl stop mux.service", shell=True),
                call("sudo systemctl disable mux.service", shell=True),
                call("sudo systemctl mask mux.service", shell=True),
                call("sudo systemctl unmask telemetry.service", shell=True),
                call("sudo systemctl unmask telemetry.timer", shell=True),
                call("sudo systemctl enable telemetry.timer", shell=True),
                call("sudo systemctl start telemetry.timer", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error')
            },
        },
    ],
    [
        "T1Case",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "type": "T1",
                    }
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "{% if 'subtype' in DEVICE_METADATA['localhost'] and DEVICE_METADATA['localhost']['subtype'] == 'DualToR' %}enabled{% else %}always_disabled{% endif %}"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_config_db": {
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "always_disabled"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_subprocess_calls": [
                call("sudo systemctl unmask dhcp_relay.service", shell=True),
                call("sudo systemctl enable dhcp_relay.service", shell=True),
                call("sudo systemctl start dhcp_relay.service", shell=True),
                call("sudo systemctl stop mux.service", shell=True),
                call("sudo systemctl disable mux.service", shell=True),
                call("sudo systemctl mask mux.service", shell=True),
                call("sudo systemctl unmask telemetry.service", shell=True),
                call("sudo systemctl unmask telemetry.timer", shell=True),
                call("sudo systemctl enable telemetry.timer", shell=True),
                call("sudo systemctl start telemetry.timer", shell=True),
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error')
            },
        },
    ],
    [
        "DualTorCaseWithNoSystemCalls",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "subtype": "DualToR",
                        "type": "ToRRouter",
                    }
                },
                "KDUMP": {
                    "config": {
                        "enabled": "false",
                        "num_dumps": "3",
                        "memory": "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M"
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "{% if 'subtype' in DEVICE_METADATA['localhost'] and DEVICE_METADATA['localhost']['subtype'] == 'DualToR' %}enabled{% else %}always_disabled{% endif %}"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_config_db": {
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
                    "mux": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "False",
                        "high_mem_alert": "disabled",
                        "set_owner": "local",
                        "state": "enabled"
                    },
                    "telemetry": {
                        "auto_restart": "enabled",
                        "has_global_scope": "True",
                        "has_per_asic_scope": "False",
                        "has_timer": "True",
                        "high_mem_alert": "disabled",
                        "set_owner": "kube",
                        "state": "enabled",
                        "status": "enabled"
                    },
                },
            },
            "expected_subprocess_calls": [
            ],
            "popen_attributes": {
                'communicate.return_value': ('enabled', 'error')
            },
        }
    ]
]
