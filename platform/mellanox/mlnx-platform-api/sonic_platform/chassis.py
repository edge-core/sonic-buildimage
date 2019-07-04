#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

import sys

try:
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.psu import Psu
    from sonic_platform.fan import Fan
    from sonic_platform.fan import FAN_PATH
    from sonic_platform.sfp import SFP
    from sonic_platform.watchdog import get_watchdog
    from sonic_daemon_base.daemon_base import Logger
    from eeprom import Eeprom
    from os import listdir
    from os.path import isfile, join
    import io
    import re
    import subprocess
    import syslog
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

MLNX_NUM_PSU = 2

GET_HWSKU_CMD = "sonic-cfggen -d -v DEVICE_METADATA.localhost.hwsku"

EEPROM_CACHE_ROOT = '/var/cache/sonic/decode-syseeprom'
EEPROM_CACHE_FILE = 'syseeprom_cache'

HWMGMT_SYSTEM_ROOT = '/var/run/hw-management/system/'

#reboot cause related definitions
REBOOT_CAUSE_ROOT = HWMGMT_SYSTEM_ROOT

REBOOT_CAUSE_POWER_LOSS_FILE = 'reset_main_pwr_fail'
REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC_FILE = 'reset_asic_thermal'
REBOOT_CAUSE_WATCHDOG_FILE = 'reset_hotswap_or_wd'
REBOOT_CAUSE_MLNX_FIRMWARE_RESET = 'reset_fw_reset'

REBOOT_CAUSE_FILE_LENGTH = 1

#version retrieving related definitions
CPLD_VERSION_ROOT = HWMGMT_SYSTEM_ROOT

CPLD1_VERSION_FILE = 'cpld1_version'
CPLD2_VERSION_FILE = 'cpld2_version'
CPLD_VERSION_MAX_LENGTH = 4

FW_QUERY_VERSION_COMMAND = 'mlxfwmanager --query'
BIOS_QUERY_VERSION_COMMAND = 'dmidecode -t 11'

#components definitions
COMPONENT_BIOS = "BIOS"
COMPONENT_FIRMWARE = "ASIC-FIRMWARE"
COMPONENT_CPLD1 = "CPLD1"
COMPONENT_CPLD2 = "CPLD2"

# Global logger class instance
SYSLOG_IDENTIFIER = "mlnx-chassis"
logger = Logger(SYSLOG_IDENTIFIER)

# magic code defnition for port number, qsfp port position of each hwsku
# port_position_tuple = (PORT_START, QSFP_PORT_START, PORT_END, PORT_IN_BLOCK, EEPROM_OFFSET)
hwsku_dict = {'ACS-MSN2700': 0, "LS-SN2700":0, 'ACS-MSN2740': 0, 'ACS-MSN2100': 1, 'ACS-MSN2410': 2, 'ACS-MSN2010': 3, 'ACS-MSN3700': 0, 'ACS-MSN3700C': 0, 'Mellanox-SN2700': 0, 'Mellanox-SN2700-D48C8': 0}
port_position_tuple_list = [(0, 0, 31, 32, 1), (0, 0, 15, 16, 1), (0, 48, 55, 56, 1),(0, 18, 21, 22, 1)]

class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        super(Chassis, self).__init__()

        # Initialize PSU list
        for index in range(MLNX_NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

        # Initialize watchdog
        self._watchdog = get_watchdog()

        # Initialize FAN list
        multi_rotor_in_drawer = False
        num_of_fan, num_of_drawer = self._extract_num_of_fans_and_fan_drawers()
        multi_rotor_in_drawer = num_of_fan > num_of_drawer

        for index in range(num_of_fan):
            if multi_rotor_in_drawer:
                fan = Fan(index, index/2)
            else:
                fan = Fan(index, index)
            self._fan_list.append(fan)

        # Initialize SFP list
        port_position_tuple = self._get_port_position_tuple_by_sku_name()
        self.PORT_START = port_position_tuple[0]
        self.QSFP_PORT_START = port_position_tuple[1]
        self.PORT_END = port_position_tuple[2]
        self.PORTS_IN_BLOCK = port_position_tuple[3]

        for index in range(self.PORT_START, self.PORT_END + 1):
            if index in range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1):
                sfp_module = SFP(index, 'QSFP')
            else:
                sfp_module = SFP(index, 'SFP')
            self._sfp_list.append(sfp_module)

        # Initialize EEPROM
        self.eeprom = Eeprom()

        # Initialize component list
        self._component_name_list.append(COMPONENT_BIOS)
        self._component_name_list.append(COMPONENT_FIRMWARE)
        self._component_name_list.append(COMPONENT_CPLD1)
        self._component_name_list.append(COMPONENT_CPLD2)

    def _extract_num_of_fans_and_fan_drawers(self):
        num_of_fan = 0
        num_of_drawer = 0
        for f in listdir(FAN_PATH):
            if isfile(join(FAN_PATH, f)):
                match_obj = re.match('fan(\d+)_speed_get', f)
                if match_obj != None:
                    if int(match_obj.group(1)) > num_of_fan:
                        num_of_fan = int(match_obj.group(1))
                else:
                    match_obj = re.match('fan(\d+)_status', f)
                    if match_obj != None and int(match_obj.group(1)) > num_of_drawer:
                        num_of_drawer = int(match_obj.group(1))

        return num_of_fan, num_of_drawer

    def _get_port_position_tuple_by_sku_name(self):
        p = subprocess.Popen(GET_HWSKU_CMD, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        position_tuple = port_position_tuple_list[hwsku_dict[out.rstrip('\n')]]
        return position_tuple

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis

        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self.eeprom.get_base_mac()

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis

        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self.eeprom.get_serial_number()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis

        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self.eeprom.get_system_eeprom_info()

    def _read_generic_file(self, filename, len):
        """
        Read a generic file, returns the contents of the file
        """
        result = ''
        try:
            fileobj = io.open(filename)
            result = fileobj.read(len)
            fileobj.close()
            return result
        except:
            logger.log_warning("Fail to read file {}, maybe it doesn't exist".format(filename))
            return ''

    def _verify_reboot_cause(self, filename):
        '''
        Open and read the reboot cause file in 
        /var/run/hwmanagement/system (which is defined as REBOOT_CAUSE_ROOT)
        If a reboot cause file doesn't exists, returns '0'.
        '''
        return bool(int(self._read_generic_file(join(REBOOT_CAUSE_ROOT, filename), REBOOT_CAUSE_FILE_LENGTH).rstrip('\n')))

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
        #read reboot causes files in the following order
        minor_cause = ''
        if self._verify_reboot_cause(REBOOT_CAUSE_POWER_LOSS_FILE):
            major_cause = self.REBOOT_CAUSE_POWER_LOSS
        elif self._verify_reboot_cause(REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC_FILE):
            major_cause = self.REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC
        elif self._verify_reboot_cause(REBOOT_CAUSE_WATCHDOG_FILE):
            major_cause = self.REBOOT_CAUSE_WATCHDOG
        else:
            major_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            if self._verify_reboot_cause(REBOOT_CAUSE_MLNX_FIRMWARE_RESET):
                minor_cause = "Reset by ASIC firmware"
            else:
                major_cause = self.REBOOT_CAUSE_NON_HARDWARE

        return major_cause, minor_cause

    def _get_cpld_version(self, version_file):
        cpld_version = self._read_generic_file(join(CPLD_VERSION_ROOT, version_file), CPLD_VERSION_MAX_LENGTH)
        return cpld_version.rstrip('\n')

    def _get_command_result(self, cmdline):
        try:
            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            result = stdout.rstrip('\n')

        except OSError, e:
            result = ''

        return result

    def _get_firmware_version(self):
        """
        firmware version is retrieved via command 'mlxfwmanager --query'
        which should return result in the following convention
            admin@mtbc-sonic-01-2410:~$ sudo mlxfwmanager --query
            Querying Mellanox devices firmware ...

            Device #1:
            ----------

            Device Type:      Spectrum
            Part Number:      MSN2410-CxxxO_Ax_Bx
            Description:      Spectrum based 25GbE/100GbE 1U Open Ethernet switch with ONIE; 48 SFP28 ports; 8 QSFP28 ports; x86 dual core; RoHS6
            PSID:             MT_2860111033
            PCI Device Name:  /dev/mst/mt52100_pci_cr0
            Base MAC:         98039bf3f500
            Versions:         Current        Available     
                FW         ***13.2000.1140***N/A           

            Status:           No matching image found

        By using regular expression '(Versions:.*\n[\s]+FW[\s]+)([\S]+)',
        we can extrace the version which is marked with *** in the above context
        """
        fw_ver_str = self._get_command_result(FW_QUERY_VERSION_COMMAND)
        try: 
            m = re.search('(Versions:.*\n[\s]+FW[\s]+)([\S]+)', fw_ver_str)
            result = m.group(2)
        except :
            result = ''

        return result

    def _get_bios_version(self):
        """
        BIOS version is retrieved via command 'dmidecode -t 11'
        which should return result in the following convention
            # dmidecode 3.0
            Getting SMBIOS data from sysfs.
            SMBIOS 2.7 present.

            Handle 0x0022, DMI type 11, 5 bytes
            OEM Strings
                    String 1:*0ABZS017_02.02.002*
                    String 2: To Be Filled By O.E.M.

        By using regular expression 'OEM[\s]*Strings\n[\s]*String[\s]*1:[\s]*([0-9a-zA-Z_\.]*)'
        we can extrace the version string which is marked with * in the above context
        """
        bios_ver_str = self._get_command_result(BIOS_QUERY_VERSION_COMMAND)
        try:
            m = re.search('OEM[\s]*Strings\n[\s]*String[\s]*1:[\s]*([0-9a-zA-Z_\.]*)', bios_ver_str)
            result = m.group(1)
        except:
            result = ''

        return result

    def get_firmware_version(self, component_name):
        """
        Retrieves platform-specific hardware/firmware versions for chassis
        componenets such as BIOS, CPLD, FPGA, etc.
        Args:
            component_name: A string, the component name.

        Returns:
            A string containing platform-specific component versions
        """
        if component_name in self._component_name_list :
            if component_name == COMPONENT_BIOS:
                return self._get_bios_version()
            elif component_name == COMPONENT_CPLD1:
                return self._get_cpld_version(CPLD1_VERSION_FILE)
            elif component_name == COMPONENT_CPLD2:
                return self._get_cpld_version(CPLD2_VERSION_FILE)
            elif component_name == COMPONENT_FIRMWARE:
                return self._get_firmware_version()

        return None
