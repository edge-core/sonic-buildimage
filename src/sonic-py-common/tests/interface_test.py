import os
import sys

from sonic_py_common import interface

class TestInterface(object):
    @classmethod
    def setup_class(cls):
        print("SETUP")

    def test_get_interface_table_name(self):
        result = interface.get_interface_table_name("Ethernet0")
        assert result == "INTERFACE"
        result = interface.get_interface_table_name("Ethernet0.100")
        assert result == "VLAN_SUB_INTERFACE"
        result = interface.get_interface_table_name("PortChannel0")
        assert result == "PORTCHANNEL_INTERFACE"
        result = interface.get_interface_table_name("PortChannel0.100")
        assert result == "VLAN_SUB_INTERFACE"
        result = interface.get_interface_table_name("Vlan100")
        assert result == "VLAN_INTERFACE"
        result = interface.get_interface_table_name("Loopback0")
        assert result == "LOOPBACK_INTERFACE"

    def test_get_port_table_name(self):
        result = interface.get_port_table_name("Ethernet0")
        assert result == "PORT"
        result = interface.get_port_table_name("Ethernet0.100")
        assert result == "VLAN_SUB_INTERFACE"
        result = interface.get_port_table_name("PortChannel0")
        assert result == "PORTCHANNEL"
        result = interface.get_port_table_name("PortChannel0.100")
        assert result == "VLAN_SUB_INTERFACE"
        result = interface.get_port_table_name("Vlan100")
        assert result == "VLAN_INTERFACE"
        result = interface.get_port_table_name("Loopback0")
        assert result == "LOOPBACK_INTERFACE"

    @classmethod
    def teardown_class(cls):
        print("TEARDOWN")
