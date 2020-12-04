#!/usr/bin/env python

try:
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
    from sonic_platform.psu import Psu
    from eeprom import Eeprom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

class Chassis(ChassisBase):
    """
    Platform-specific Chassis class
    """
    def __init__(self):
        ChassisBase.__init__(self)

        self._eeprom = Eeprom()

        for index in range(Sfp.port_start(), Sfp.port_end() + 1):
            sfp_node = Sfp(index)
            self._sfp_list.append(sfp_node)

        for i in range(1, Psu.get_num_psus() + 1):
            psu = Psu(i)
            self._psu_list.append(psu)

    def get_name(self):
        """
        Retrieves the name of the chassis
        Returns:
            string: The name of the chassis
        """
        return self._eeprom.modelstr()

    def get_presence(self):
        """
        Retrieves the presence of the chassis
        Returns:
            bool: True if chassis is present, False if not
        """
        return True

    def get_model(self):
        """
        Retrieves the model number (or part number) of the chassis
        Returns:
            string: Model/part number of chassis
        """
        return self._eeprom.part_number_str()

    def get_serial(self):
        """
        Retrieves the serial number of the chassis (Service tag)
        Returns:
            string: Serial number of chassis
        """
        return self._eeprom.serial_str()

    def get_sfp(self, index):
        """
        Retrieves sfp represented by (1-based) index <index>

        Args:
            index: An integer, the index (1-based) of the sfp to retrieve.
                   The index should be the sequence of a physical port in a chassis,
                   starting from 1.
                   For example, 0 for Ethernet0, 1 for Ethernet4 and so on.

        Returns:
            An object dervied from SfpBase representing the specified sfp
        """
        sfp = None

        try:
            sfp = self._sfp_list[index-1]
        except IndexError:
            sys.stderr.write("SFP index {} out of range (1-{})\n".format(
                             index, len(self._sfp_list)-1))
        return sfp

    def get_status(self):
        """
        Retrieves the operational status of the chassis
        Returns:
            bool: A boolean value, True if chassis is operating properly
            False if not
        """
        return True

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis

        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.base_mac_addr()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis

        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.system_eeprom_info()

    def get_change_event(self, timeout=0):
        ready, event_sfp = Sfp.get_transceiver_change_event(timeout)
        return ready, { 'sfp': event_sfp } if ready else {}
