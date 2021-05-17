#!/usr/bin/env python

#############################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################
try:
    import sys
    import os
    import time
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.fan import Fan
    from sonic_platform.psu import Psu
    from sonic_platform.component import Component
    from sonic_platform.thermal import Thermal
    from sonic_platform.sfp import Sfp
    from sonic_platform.eeprom import Tlv
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_FAN = 14
NUM_PSU = 2
NUM_THERMAL = 7
NUM_SFP = 32
HOST_REBOOT_CAUSE_PATH = "/host/reboot-cause/"
PMON_REBOOT_CAUSE_PATH = "/usr/share/sonic/platform/api_files/reboot-cause/"
REBOOT_CAUSE_FILE = "reboot-cause.txt"
PREV_REBOOT_CAUSE_FILE = "previous-reboot-cause.txt"
COMPONENT_NAME_LIST = ["BIOS"]
HOST_CHK_CMD = "docker > /dev/null 2>&1"


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        super(Chassis, self).__init__()

        for fan_index in range(0, NUM_FAN):
            fan = Fan(fan_index)
            self._fan_list.append(fan)

        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

        for index in range(0, NUM_THERMAL):
            thermal = Thermal(index)
            self._thermal_list.append(thermal)

        for index in range(0, NUM_SFP):
            sfp_module = Sfp(index, 'QSFP-DD')
            self._sfp_list.append(sfp_module)
        self._component_name_list = COMPONENT_NAME_LIST
        self._eeprom = Tlv()
        self._transceiver_presence = self._get_sfp_presence()

    def __is_host(self):
        return os.system(HOST_CHK_CMD) == 0

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return None

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.get_mac()

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis
        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self._eeprom.get_serial()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.get_eeprom()

    def get_firmware_version(self, component_name):
        """
        Retrieves platform-specific hardware/firmware versions for chassis
        componenets such as BIOS, CPLD, FPGA, etc.
        Args:
            type: A string, component name

        Returns:
            A string containing platform-specific component versions
        """
        self.component = Component(component_name)
        if component_name not in self._component_name_list:
            return None
        return self.component.get_firmware_version()

    def install_component_firmware(self, component_name, image_path):
        """
        Install firmware to module
        Args:
            type: A string, component name.
            image_path: A string, path to firmware image.

        Returns:
            A boolean, True if install successfully, False if not
        """
        self.component = Component(component_name)
        if component_name not in self._component_name_list:
            return False
        return self.component.upgrade_firmware(image_path)

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot

        Returns:
            A tuple (string, string) where the first element is a string
            containing the cause of the previous reboot. This string must be
            one of the predefined strings in this class. If the first string
            is "REBOOT_CAUSE_HARDWARE_OTHER", the second string can be used
            to pass a description of the reboot cause.
        """

        reboot_cause_path = (HOST_REBOOT_CAUSE_PATH + REBOOT_CAUSE_FILE) if self.__is_host(
        ) else PMON_REBOOT_CAUSE_PATH + REBOOT_CAUSE_FILE
        sw_reboot_cause = self.__read_txt_file(
            reboot_cause_path) or "Unknown"

        if sw_reboot_cause != "Unknown":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = sw_reboot_cause
        else:
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'Unknown reason'

        return (reboot_cause, description)

    def get_sfp(self, index):
        sfp = None
        try:
            sfp = self._sfp_list[index]
        except IndexError:
            sys.stderr.write("SFP index {} out of range (0-{})\n".format(index, len(self._sfp_list)-1))

        return sfp

    def _get_sfp_presence(self):
        port_pres = {}
        for port in range(0, NUM_SFP):
            sfp = self._sfp_list[port]
            port_pres[port] = sfp.get_presence()

        return port_pres

    def get_change_event(self, timeout=0):
        port_dict = {}
        ret_dict = {'sfp': port_dict}
        forever = False
        change_event = False

        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000)
        else:
            return False, ret_dict #Incorrect timeout

        while True:
            if forever:
                timer = 1
            else:
                timer = min(timeout, 1)
                start_time = time.time()

            time.sleep(timer)
            cur_presence = self._get_sfp_presence()
            for port in range(0, NUM_SFP):
                if cur_presence[port] == 1:
                    port_dict[port] = '1'
                else:
                    port_dict[port] = '0'

                if cur_presence[port] != self._transceiver_presence[port]:
                    change_event = True

            self._transceiver_presence = cur_presence
            if change_event == True:
                break

            if not forever:
                elapsed_time = time.time() - start_time
                timeout = round(timeout - elapsed_time, 3)
                if timeout <= 0:
                    break

        for port in range(0, NUM_SFP):
            sfp = self._sfp_list[port]
            sfp.reinit()

        return True, ret_dict
