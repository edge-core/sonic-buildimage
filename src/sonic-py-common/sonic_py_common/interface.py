"""
SONiC interface types and access functions.
"""

"""
 Dictionary of SONIC interface name prefixes. Each entry in the format
 "Human readable interface string":"Sonic interface prefix"
 Currently this is a static mapping, but in future could be stored as metadata in DB.
"""

SONIC_INTERFACE_PREFIXES = {
    "Ethernet-FrontPanel": "Ethernet",
    "PortChannel": "PortChannel",
    "Vlan": "Vlan",
    "Loopback": "Loopback",
    "Ethernet-Backplane": "Ethernet-BP"
}

VLAN_SUB_INTERFACE_SEPARATOR = '.'

def front_panel_prefix():
    """
    Retrieves the SONIC front panel interface name prefix.
    """
    return SONIC_INTERFACE_PREFIXES["Ethernet-FrontPanel"]

def backplane_prefix():
    """
    Retrieves the SONIC backplane interface name prefix.
    """
    return SONIC_INTERFACE_PREFIXES["Ethernet-Backplane"]

def portchannel_prefix():
    """
    Retrieves the SONIC PortChannel interface name prefix.
    """
    return SONIC_INTERFACE_PREFIXES["PortChannel"]

def vlan_prefix():
    """
    Retrieves the SONIC Vlan interface name prefix.
    """
    return SONIC_INTERFACE_PREFIXES["Vlan"]

def loopback_prefix():
    """
    Retrieves the SONIC Loopback interface name prefix.
    """
    return SONIC_INTERFACE_PREFIXES["Loopback"]

def get_interface_table_name(interface_name):
    """Get table name by interface_name prefix
    """
    if interface_name.startswith(front_panel_prefix()):
        if VLAN_SUB_INTERFACE_SEPARATOR in interface_name:
            return "VLAN_SUB_INTERFACE"
        return "INTERFACE"
    elif interface_name.startswith(portchannel_prefix()):
        if VLAN_SUB_INTERFACE_SEPARATOR in interface_name:
            return "VLAN_SUB_INTERFACE"
        return "PORTCHANNEL_INTERFACE"
    elif interface_name.startswith(vlan_prefix()):
        return "VLAN_INTERFACE"
    elif interface_name.startswith(loopback_prefix()):
        return "LOOPBACK_INTERFACE"
    else:
        return ""

def get_port_table_name(interface_name):
    """Get table name by port_name prefix
    """
    if interface_name.startswith(front_panel_prefix()):
        if VLAN_SUB_INTERFACE_SEPARATOR in interface_name:
            return "VLAN_SUB_INTERFACE"
        return "PORT"
    elif interface_name.startswith(portchannel_prefix()):
        if VLAN_SUB_INTERFACE_SEPARATOR in interface_name:
            return "VLAN_SUB_INTERFACE"
        return "PORTCHANNEL"
    elif interface_name.startswith(vlan_prefix()):
        return "VLAN_INTERFACE"
    elif interface_name.startswith(loopback_prefix()):
        return "LOOPBACK_INTERFACE"
    else:
        return ""
