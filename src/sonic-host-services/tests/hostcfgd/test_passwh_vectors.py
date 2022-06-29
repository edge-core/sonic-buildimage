"""
    hostcfgd test password hardening vector
"""
HOSTCFGD_TEST_PASSWH_VECTOR = [
    [
        "PASSWORD_HARDENING",
        {
            "default_values":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "disabled",
                        "expiration": "180",
                        "expiration_warning": "15",
                        "history_cnt": "10",
                        "len_min": "8",
                        "reject_user_passw_match": "True",
                        "lower_class": "True",
                        "upper_class": "True",
                        "digits_class": "True",
                        "special_class": "True"
                    }
                },
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
                }
            },
            "enable_feature":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "enabled",
                        "expiration": "180",
                        "expiration_warning": "15",
                        "history_cnt": "10",
                        "len_min": "8",
                        "reject_user_passw_match": "True",
                        "lower_class": "True",
                        "upper_class": "True",
                        "digits_class": "True",
                        "special_class": "True"
                    }
                },
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
                }
            },
            "enable_digits_class":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "enabled",
                        "expiration": "0",
                        "expiration_warning": "0",
                        "history_cnt": "0",
                        "len_min": "8",
                        "reject_user_passw_match": "False",
                        "lower_class": "False",
                        "upper_class": "False",
                        "digits_class": "True",
                        "special_class": "False"
                    }
                },
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
                }
            },
            "enable_lower_class":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "enabled",
                        "expiration": "0",
                        "expiration_warning": "0",
                        "history_cnt": "0",
                        "len_min": "8",
                        "reject_user_passw_match": "False",
                        "lower_class": "True",
                        "upper_class": "False",
                        "digits_class": "False",
                        "special_class": "False"
                    }
                },
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
            },
            "enable_upper_class":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "enabled",
                        "expiration": "0",
                        "expiration_warning": "0",
                        "history_cnt": "0",
                        "len_min": "8",
                        "reject_user_passw_match": "False",
                        "lower_class": "False",
                        "upper_class": "True",
                        "digits_class": "False",
                        "special_class": "False"
                    }
                },
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
                }
            },
            "enable_special_class":{
                "PASSW_HARDENING": {
                    "POLICIES":{
                        "state": "enabled",
                        "expiration": "0",
                        "expiration_warning": "0",
                        "history_cnt": "0",
                        "len_min": "8",
                        "reject_user_passw_match": "False",
                        "lower_class": "False",
                        "upper_class": "False",
                        "digits_class": "False",
                        "special_class": "True"
                    }
                },
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
                }
            }
        }
    ]
]
