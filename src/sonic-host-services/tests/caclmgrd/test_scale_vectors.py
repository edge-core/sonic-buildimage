from unittest.mock import call
import subprocess

"""
    caclmgrd bfd test vector
"""
CACLMGRD_SCALE_TEST_VECTOR = [
    [
        "SCALE_SESSION_TEST",
        {
            "config_db": {
                "DEVICE_METADATA": {
                    "localhost": {
                        "type": "ToRRouter",
                    }
                },
                "LOOPBACK_INTERFACE": {},
                "VLAN_INTERFACE": {},
                "MGMT_INTERFACE": {},
                "PORTCHANNEL_INTERFACE": {},
                "INTERFACE": {},
                "FEATURE": {},
                "ACL_RULE": {
                    "NTP_ACL|RULE_1": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9999",
                        "SRC_IPV6": "2001::2/128"
                    },
                    "NTP_ACL|RULE_2": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9998",
                        "SRC_IPV6": "2001::3/128"
                    },
                    "NTP_ACL|RULE_3": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9997",
                        "SRC_IPV6": "2001::4/128"
                    },
                    "NTP_ACL|RULE_4": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9996",
                        "SRC_IPV6": "2001::5/128"
                    },
                    "NTP_ACL|RULE_5": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9995",
                        "SRC_IPV6": "2001::6/128"
                    },
                    "NTP_ACL|RULE_6": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9994",
                        "SRC_IPV6": "2001::7/128"
                    },
                    "NTP_ACL|RULE_7": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9993",
                        "SRC_IPV6": "2001::8/128"
                    },
                    "NTP_ACL|RULE_8": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9992",
                        "SRC_IPV6": "2001::9/128"
                    },
                    "NTP_ACL|RULE_9": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9991",
                        "SRC_IPV6": "2001::10/128"
                    },
                    "NTP_ACL|RULE_10": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9990",
                        "SRC_IPV6": "2001::11/128"
                    },
                    "NTP_ACL|RULE_11": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9989",
                        "SRC_IPV6": "2001::12/128"
                    },
                    "NTP_ACL|RULE_12": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9988",
                        "SRC_IPV6": "2001::13/128"
                    },
                    "NTP_ACL|RULE_13": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9987",
                        "SRC_IPV6": "2001::14/128"
                    },
                    "NTP_ACL|RULE_14": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9986",
                        "SRC_IPV6": "2001::15/128"
                    },
                    "NTP_ACL|RULE_15": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9985",
                        "SRC_IPV6": "2001::16/128"
                    },
                    "NTP_ACL|RULE_16": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9984",
                        "SRC_IPV6": "2001::17/128"
                    },
                    "NTP_ACL|RULE_17": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9983",
                        "SRC_IPV6": "2001::18/128"
                    },
                    "NTP_ACL|RULE_18": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9982",
                        "SRC_IPV6": "2001::19/128"
                    },
                    "NTP_ACL|RULE_19": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9981",
                        "SRC_IPV6": "2001::20/128"
                    },
                    "NTP_ACL|RULE_20": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9980",
                        "SRC_IPV6": "2001::21/128"
                    },
                    "NTP_ACL|RULE_21": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9979",
                        "SRC_IPV6": "2001::22/128"
                    },
                    "NTP_ACL|RULE_22": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9978",
                        "SRC_IPV6": "2001::23/128"
                    },
                    "NTP_ACL|RULE_23": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9977",
                        "SRC_IPV6": "2001::24/128"
                    },
                    "NTP_ACL|RULE_24": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9976",
                        "SRC_IPV6": "2001::25/128"
                    },
                    "NTP_ACL|RULE_25": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9975",
                        "SRC_IPV6": "2001::26/128"
                    },
                    "NTP_ACL|RULE_26": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9974",
                        "SRC_IPV6": "2001::27/128"
                    },
                    "NTP_ACL|RULE_27": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9973",
                        "SRC_IPV6": "2001::28/128"
                    },
                    "NTP_ACL|RULE_28": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9972",
                        "SRC_IPV6": "2001::29/128"
                    },
                    "NTP_ACL|RULE_29": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9971",
                        "SRC_IPV6": "2001::30/128"
                    },
                    "NTP_ACL|RULE_30": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9970",
                        "SRC_IPV6": "2001::31/128"
                    },
                    "NTP_ACL|RULE_31": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9969",
                        "SRC_IPV6": "2001::32/128"
                    },
                    "NTP_ACL|RULE_32": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9968",
                        "SRC_IPV6": "2001::33/128"
                    },
                    "NTP_ACL|RULE_33": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9967",
                        "SRC_IPV6": "2001::34/128"
                    },
                    "NTP_ACL|RULE_34": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9966",
                        "SRC_IPV6": "2001::35/128"
                    },
                    "NTP_ACL|RULE_35": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9965",
                        "SRC_IPV6": "2001::36/128"
                    },
                    "NTP_ACL|RULE_36": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9964",
                        "SRC_IPV6": "2001::37/128"
                    },
                    "NTP_ACL|RULE_37": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9963",
                        "SRC_IPV6": "2001::38/128"
                    },
                    "NTP_ACL|RULE_38": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9962",
                        "SRC_IPV6": "2001::39/128"
                    },
                    "NTP_ACL|RULE_39": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9961",
                        "SRC_IPV6": "2001::40/128"
                    },
                    "NTP_ACL|RULE_40": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9960",
                        "SRC_IPV6": "2001::41/128"
                    },
                    "NTP_ACL|RULE_41": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9959",
                        "SRC_IPV6": "2001::42/128"
                    },
                    "NTP_ACL|RULE_42": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9958",
                        "SRC_IPV6": "2001::43/128"
                    },
                    "NTP_ACL|RULE_43": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9957",
                        "SRC_IPV6": "2001::44/128"
                    },
                    "NTP_ACL|RULE_44": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9956",
                        "SRC_IPV6": "2001::45/128"
                    },
                    "NTP_ACL|RULE_45": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9955",
                        "SRC_IPV6": "2001::46/128"
                    },
                    "NTP_ACL|RULE_46": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9954",
                        "SRC_IPV6": "2001::47/128"
                    },
                    "NTP_ACL|RULE_47": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9953",
                        "SRC_IPV6": "2001::48/128"
                    },
                    "NTP_ACL|RULE_48": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9952",
                        "SRC_IPV6": "2001::49/128"
                    },
                    "NTP_ACL|RULE_49": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9951",
                        "SRC_IPV6": "2001::50/128"
                    },
                    "NTP_ACL|RULE_50": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9950",
                        "SRC_IPV6": "2001::51/128"
                    },
                    "SNMP_ACL|RULE_1": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9999",
                        "SRC_IPV6": "2001::2/128"
                    },
                    "SNMP_ACL|RULE_2": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9998",
                        "SRC_IPV6": "2001::3/128"
                    },
                    "SNMP_ACL|RULE_3": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9997",
                        "SRC_IPV6": "2001::4/128"
                    },
                    "SNMP_ACL|RULE_4": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9996",
                        "SRC_IPV6": "2001::5/128"
                    },
                    "SNMP_ACL|RULE_5": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9995",
                        "SRC_IPV6": "2001::6/128"
                    },
                    "SNMP_ACL|RULE_6": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9994",
                        "SRC_IPV6": "2001::7/128"
                    },
                    "SNMP_ACL|RULE_7": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9993",
                        "SRC_IPV6": "2001::8/128"
                    },
                    "SNMP_ACL|RULE_8": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9992",
                        "SRC_IPV6": "2001::9/128"
                    },
                    "SNMP_ACL|RULE_9": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9991",
                        "SRC_IPV6": "2001::10/128"
                    },
                    "SNMP_ACL|RULE_10": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9990",
                        "SRC_IPV6": "2001::11/128"
                    },
                    "SNMP_ACL|RULE_11": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9989",
                        "SRC_IPV6": "2001::12/128"
                    },
                    "SNMP_ACL|RULE_12": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9988",
                        "SRC_IPV6": "2001::13/128"
                    },
                    "SNMP_ACL|RULE_13": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9987",
                        "SRC_IPV6": "2001::14/128"
                    },
                    "SNMP_ACL|RULE_14": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9986",
                        "SRC_IPV6": "2001::15/128"
                    },
                    "SNMP_ACL|RULE_15": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9985",
                        "SRC_IPV6": "2001::16/128"
                    },
                    "SNMP_ACL|RULE_16": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9984",
                        "SRC_IPV6": "2001::17/128"
                    },
                    "SNMP_ACL|RULE_17": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9983",
                        "SRC_IPV6": "2001::18/128"
                    },
                    "SNMP_ACL|RULE_18": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9982",
                        "SRC_IPV6": "2001::19/128"
                    },
                    "SNMP_ACL|RULE_19": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9981",
                        "SRC_IPV6": "2001::20/128"
                    },
                    "SNMP_ACL|RULE_20": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9980",
                        "SRC_IPV6": "2001::21/128"
                    },
                    "SNMP_ACL|RULE_21": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9979",
                        "SRC_IPV6": "2001::22/128"
                    },
                    "SNMP_ACL|RULE_22": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9978",
                        "SRC_IPV6": "2001::23/128"
                    },
                    "SNMP_ACL|RULE_23": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9977",
                        "SRC_IPV6": "2001::24/128"
                    },
                    "SNMP_ACL|RULE_24": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9976",
                        "SRC_IPV6": "2001::25/128"
                    },
                    "SNMP_ACL|RULE_25": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9975",
                        "SRC_IPV6": "2001::26/128"
                    },
                    "SNMP_ACL|RULE_26": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9974",
                        "SRC_IPV6": "2001::27/128"
                    },
                    "SNMP_ACL|RULE_27": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9973",
                        "SRC_IPV6": "2001::28/128"
                    },
                    "SNMP_ACL|RULE_28": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9972",
                        "SRC_IPV6": "2001::29/128"
                    },
                    "SNMP_ACL|RULE_29": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9971",
                        "SRC_IPV6": "2001::30/128"
                    },
                    "SNMP_ACL|RULE_30": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9970",
                        "SRC_IPV6": "2001::31/128"
                    },
                    "SNMP_ACL|RULE_31": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9969",
                        "SRC_IPV6": "2001::32/128"
                    },
                    "SNMP_ACL|RULE_32": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9968",
                        "SRC_IPV6": "2001::33/128"
                    },
                    "SNMP_ACL|RULE_33": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9967",
                        "SRC_IPV6": "2001::34/128"
                    },
                    "SNMP_ACL|RULE_34": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9966",
                        "SRC_IPV6": "2001::35/128"
                    },
                    "SNMP_ACL|RULE_35": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9965",
                        "SRC_IPV6": "2001::36/128"
                    },
                    "SNMP_ACL|RULE_36": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9964",
                        "SRC_IPV6": "2001::37/128"
                    },
                    "SNMP_ACL|RULE_37": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9963",
                        "SRC_IPV6": "2001::38/128"
                    },
                    "SNMP_ACL|RULE_38": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9962",
                        "SRC_IPV6": "2001::39/128"
                    },
                    "SNMP_ACL|RULE_39": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9961",
                        "SRC_IPV6": "2001::40/128"
                    },
                    "SNMP_ACL|RULE_40": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9960",
                        "SRC_IPV6": "2001::41/128"
                    },
                    "SNMP_ACL|RULE_41": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9959",
                        "SRC_IPV6": "2001::42/128"
                    },
                    "SNMP_ACL|RULE_42": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9958",
                        "SRC_IPV6": "2001::43/128"
                    },
                    "SNMP_ACL|RULE_43": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9957",
                        "SRC_IPV6": "2001::44/128"
                    },
                    "SNMP_ACL|RULE_44": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9956",
                        "SRC_IPV6": "2001::45/128"
                    },
                    "SNMP_ACL|RULE_45": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9955",
                        "SRC_IPV6": "2001::46/128"
                    },
                    "SNMP_ACL|RULE_46": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9954",
                        "SRC_IPV6": "2001::47/128"
                    },
                    "SNMP_ACL|RULE_47": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9953",
                        "SRC_IPV6": "2001::48/128"
                    },
                    "SNMP_ACL|RULE_48": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9952",
                        "SRC_IPV6": "2001::49/128"
                    },
                    "SNMP_ACL|RULE_49": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9951",
                        "SRC_IPV6": "2001::50/128"
                    },
                    "SNMP_ACL|RULE_50": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9950",
                        "SRC_IPV6": "2001::51/128"
                    },
                    "SSH_ONLY|RULE_1": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9999",
                        "SRC_IPV6": "2001::2/128"
                    },
                    "SSH_ONLY|RULE_2": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9998",
                        "SRC_IPV6": "2001::3/128"
                    },
                    "SSH_ONLY|RULE_3": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9997",
                        "SRC_IPV6": "2001::4/128"
                    },
                    "SSH_ONLY|RULE_4": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9996",
                        "SRC_IPV6": "2001::5/128"
                    },
                    "SSH_ONLY|RULE_5": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9995",
                        "SRC_IPV6": "2001::6/128"
                    },
                    "SSH_ONLY|RULE_6": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9994",
                        "SRC_IPV6": "2001::7/128"
                    },
                    "SSH_ONLY|RULE_7": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9993",
                        "SRC_IPV6": "2001::8/128"
                    },
                    "SSH_ONLY|RULE_8": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9992",
                        "SRC_IPV6": "2001::9/128"
                    },
                    "SSH_ONLY|RULE_9": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9991",
                        "SRC_IPV6": "2001::10/128"
                    },
                    "SSH_ONLY|RULE_10": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9990",
                        "SRC_IPV6": "2001::11/128"
                    },
                    "SSH_ONLY|RULE_11": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9989",
                        "SRC_IPV6": "2001::12/128"
                    },
                    "SSH_ONLY|RULE_12": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9988",
                        "SRC_IPV6": "2001::13/128"
                    },
                    "SSH_ONLY|RULE_13": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9987",
                        "SRC_IPV6": "2001::14/128"
                    },
                    "SSH_ONLY|RULE_14": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9986",
                        "SRC_IPV6": "2001::15/128"
                    },
                    "SSH_ONLY|RULE_15": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9985",
                        "SRC_IPV6": "2001::16/128"
                    },
                    "SSH_ONLY|RULE_16": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9984",
                        "SRC_IPV6": "2001::17/128"
                    },
                    "SSH_ONLY|RULE_17": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9983",
                        "SRC_IPV6": "2001::18/128"
                    },
                    "SSH_ONLY|RULE_18": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9982",
                        "SRC_IPV6": "2001::19/128"
                    },
                    "SSH_ONLY|RULE_19": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9981",
                        "SRC_IPV6": "2001::20/128"
                    },
                    "SSH_ONLY|RULE_20": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9980",
                        "SRC_IPV6": "2001::21/128"
                    },
                    "SSH_ONLY|RULE_21": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9979",
                        "SRC_IPV6": "2001::22/128"
                    },
                    "SSH_ONLY|RULE_22": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9978",
                        "SRC_IPV6": "2001::23/128"
                    },
                    "SSH_ONLY|RULE_23": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9977",
                        "SRC_IPV6": "2001::24/128"
                    },
                    "SSH_ONLY|RULE_24": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9976",
                        "SRC_IPV6": "2001::25/128"
                    },
                    "SSH_ONLY|RULE_25": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9975",
                        "SRC_IPV6": "2001::26/128"
                    },
                    "SSH_ONLY|RULE_26": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9974",
                        "SRC_IPV6": "2001::27/128"
                    },
                    "SSH_ONLY|RULE_27": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9973",
                        "SRC_IPV6": "2001::28/128"
                    },
                    "SSH_ONLY|RULE_28": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9972",
                        "SRC_IPV6": "2001::29/128"
                    },
                    "SSH_ONLY|RULE_29": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9971",
                        "SRC_IPV6": "2001::30/128"
                    },
                    "SSH_ONLY|RULE_30": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9970",
                        "SRC_IPV6": "2001::31/128"
                    },
                    "SSH_ONLY|RULE_31": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9969",
                        "SRC_IPV6": "2001::32/128"
                    },
                    "SSH_ONLY|RULE_32": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9968",
                        "SRC_IPV6": "2001::33/128"
                    },
                    "SSH_ONLY|RULE_33": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9967",
                        "SRC_IPV6": "2001::34/128"
                    },
                    "SSH_ONLY|RULE_34": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9966",
                        "SRC_IPV6": "2001::35/128"
                    },
                    "SSH_ONLY|RULE_35": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9965",
                        "SRC_IPV6": "2001::36/128"
                    },
                    "SSH_ONLY|RULE_36": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9964",
                        "SRC_IPV6": "2001::37/128"
                    },
                    "SSH_ONLY|RULE_37": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9963",
                        "SRC_IPV6": "2001::38/128"
                    },
                    "SSH_ONLY|RULE_38": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9962",
                        "SRC_IPV6": "2001::39/128"
                    },
                    "SSH_ONLY|RULE_39": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9961",
                        "SRC_IPV6": "2001::40/128"
                    },
                    "SSH_ONLY|RULE_40": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9960",
                        "SRC_IPV6": "2001::41/128"
                    },
                    "SSH_ONLY|RULE_41": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9959",
                        "SRC_IPV6": "2001::42/128"
                    },
                    "SSH_ONLY|RULE_42": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9958",
                        "SRC_IPV6": "2001::43/128"
                    },
                    "SSH_ONLY|RULE_43": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9957",
                        "SRC_IPV6": "2001::44/128"
                    },
                    "SSH_ONLY|RULE_44": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9956",
                        "SRC_IPV6": "2001::45/128"
                    },
                    "SSH_ONLY|RULE_45": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9955",
                        "SRC_IPV6": "2001::46/128"
                    },
                    "SSH_ONLY|RULE_46": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9954",
                        "SRC_IPV6": "2001::47/128"
                    },
                    "SSH_ONLY|RULE_47": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9953",
                        "SRC_IPV6": "2001::48/128"
                    },
                    "SSH_ONLY|RULE_48": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9952",
                        "SRC_IPV6": "2001::49/128"
                    },
                    "SSH_ONLY|RULE_49": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9951",
                        "SRC_IPV6": "2001::50/128"
                    },
                    "SSH_ONLY|RULE_50": {
                        "PACKET_ACTION": "DROP",
                        "PRIORITY": "9950",
                        "SRC_IPV6": "2001::51/128"
                    }
                },
                "ACL_TABLE": {
                "NTP_ACL": {
                    "policy_desc": "NTP_ACL",
                    "services": [
                        "NTP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                },
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                },
                "SSH_ONLY": {
                    "policy_desc": "SSH_ONLY",
                    "services": [
                        "SSH"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            },
            },
            "expected_subprocess_calls": [
                call("ip6tables -A INPUT -p udp -s 2001::2/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::3/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::4/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::5/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::6/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::7/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::8/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::9/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::10/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::11/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::12/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::13/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::14/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::15/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::16/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::17/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::18/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::19/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::20/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::21/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::22/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::23/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::24/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::25/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::26/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::27/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::28/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::29/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::30/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::31/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::32/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::33/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::34/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::35/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::36/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::37/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::38/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::39/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::40/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::41/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::42/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::43/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::44/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::45/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::46/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::47/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::48/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::49/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::50/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::51/128 --dport 123 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::2/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::2/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::3/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::3/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::4/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::4/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::5/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::5/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::6/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::6/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::7/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::7/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::8/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::8/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::9/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::9/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::10/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::10/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::11/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::11/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::12/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::12/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::13/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::13/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::14/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::14/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::15/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::15/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::16/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::16/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::17/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::17/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::18/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::18/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::19/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::19/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::20/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::20/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::21/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::21/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::22/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::22/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::23/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::23/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::24/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::24/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::25/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::25/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::26/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::26/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::27/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::27/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::28/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::28/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::29/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::29/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::30/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::30/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::31/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::31/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::32/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::32/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::33/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::33/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::34/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::34/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::35/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::35/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::36/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::36/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::37/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::37/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::38/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::38/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::39/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::39/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::40/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::40/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::41/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::41/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::42/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::42/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::43/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::43/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::44/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::44/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::45/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::45/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::46/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::46/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::47/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::47/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::48/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::48/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::49/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::49/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::50/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::50/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::51/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p udp -s 2001::51/128 --dport 161 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::2/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::3/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::4/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::5/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::6/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::7/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::8/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::9/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::10/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::11/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::12/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::13/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::14/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::15/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::16/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::17/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::18/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::19/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::20/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::21/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::22/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::23/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::24/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::25/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::26/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::27/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::28/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::29/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::30/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::31/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::32/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::33/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::34/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::35/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::36/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::37/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::38/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::39/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::40/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::41/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::42/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::43/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::44/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::45/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::46/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::47/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::48/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::49/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::50/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE),
                call("ip6tables -A INPUT -p tcp -s 2001::51/128 --dport 22 -j DROP", shell=True, universal_newlines=True, stdout=subprocess.PIPE)
            ],
            "popen_attributes": {
                'communicate.return_value': ('output', 'error'),
            },
            "call_rc": 0,
        }
    ]
]
