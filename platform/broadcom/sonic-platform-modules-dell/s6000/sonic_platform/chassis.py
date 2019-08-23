#!/usr/bin/env python

#############################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides the platform information
#
#############################################################################

try:
    import os
    import subprocess
    import re
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
    from sonic_platform.eeprom import Eeprom
    from sonic_platform.fan import Fan
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


MAX_S6000_FAN = 3

BIOS_QUERY_VERSION_COMMAND = "dmidecode -s system-version"
#components definitions
COMPONENT_BIOS = "BIOS"
COMPONENT_CPLD1 = "CPLD1"
COMPONENT_CPLD2 = "CPLD2"
COMPONENT_CPLD3 = "CPLD3"

CPLD1_VERSION = 'system_cpld_ver'
CPLD2_VERSION = 'master_cpld_ver'
CPLD3_VERSION = 'slave_cpld_ver'


class Chassis(ChassisBase):
    """
    DELLEMC Platform-specific Chassis class
    """
    CPLD_DIR = "/sys/devices/platform/dell-s6000-cpld.0"

    reset_reason_dict = {}
    reset_reason_dict[0xe] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE
    reset_reason_dict[0x6] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE

    def __init__(self):
        # Initialize SFP list
        PORT_START = 0
        PORT_END = 31
        EEPROM_OFFSET = 20
        PORTS_IN_BLOCK = (PORT_END + 1)

        # sfp.py will read eeprom contents and retrive the eeprom data.
        # It will also provide support sfp controls like reset and setting
        # low power mode.
        # We pass the eeprom path and sfp control path from chassis.py
        # So that sfp.py implementation can be generic to all platforms
        eeprom_base = "/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom"
        sfp_control = "/sys/devices/platform/dell-s6000-cpld.0/"
        for index in range(0, PORTS_IN_BLOCK):
            eeprom_path = eeprom_base.format(index + EEPROM_OFFSET)
            sfp_node = Sfp(index, 'QSFP', eeprom_path, sfp_control, index)
            self._sfp_list.append(sfp_node)

        self.sys_eeprom = Eeprom()
        for i in range(MAX_S6000_FAN):
            fan = Fan(i)
            self._fan_list.append(fan)

        # Initialize component list
        self._component_name_list.append(COMPONENT_BIOS)
        self._component_name_list.append(COMPONENT_CPLD1)
        self._component_name_list.append(COMPONENT_CPLD2)
        self._component_name_list.append(COMPONENT_CPLD3)

    def _get_cpld_register(self, reg_name):
        rv = 'ERR'
        mb_reg_file = self.CPLD_DIR+'/'+reg_name

        if (not os.path.isfile(mb_reg_file)):
            return rv

        try:
            with open(mb_reg_file, 'r') as fd:
                rv = fd.read()
        except Exception as error:
            rv = 'ERR'

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def get_name(self):
        """
        Retrieves the name of the chassis
        Returns:
            string: The name of the chassis
        """
        return self.sys_eeprom.modelstr()

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
        return self.sys_eeprom.part_number_str()

    def get_serial(self):
        """
        Retrieves the serial number of the chassis (Service tag)
        Returns:
            string: Serial number of chassis
        """
        return self.sys_eeprom.serial_str()

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
        return self.sys_eeprom.base_mac_addr()

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis

        Returns:
            A string containing the hardware serial number for this
            chassis.
        """
        return self.sys_eeprom.serial_number_str()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the
        chassis

        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their 
            corresponding values.
        """
        return self.sys_eeprom.system_eeprom_info()

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        """
        reset_reason = int(self._get_cpld_register('last_reboot_reason'),
                           base=16)

        # In S6000, We track the reboot reason by writing the reason in
        # NVRAM. Only Warmboot and Coldboot reason are supported here.

        if (reset_reason in self.reset_reason_dict):
            return (self.reset_reason_dict[reset_reason], None)

        return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Invalid Reason")

    def _get_command_result(self, cmdline):
        try:
            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE,
                                    shell=True, stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            result = stdout.rstrip('\n')
        except OSError:
            result = ''

        return result

    def _get_cpld_version(self,cpld_name):
        """
        Cpld Version
        """
        cpld_ver = int(self._get_cpld_register(cpld_name),16)
        return cpld_ver

    def get_firmware_version(self, component_name):
        """
        Retrieves platform-specific hardware/firmware versions for
        chassis componenets such as BIOS, CPLD, FPGA, etc.
        Args:
            component_name: A string, the component name.
        Returns:
            A string containing platform-specific component versions
        """
        if component_name in self._component_name_list :
            if component_name == COMPONENT_BIOS:
                return self._get_command_result(BIOS_QUERY_VERSION_COMMAND)
            elif component_name == COMPONENT_CPLD1:
                return self._get_cpld_version(CPLD1_VERSION)
            elif component_name == COMPONENT_CPLD2:
                return self._get_cpld_version(CPLD2_VERSION)
            elif component_name == COMPONENT_CPLD3:
                return self._get_cpld_version(CPLD3_VERSION)

        return None
