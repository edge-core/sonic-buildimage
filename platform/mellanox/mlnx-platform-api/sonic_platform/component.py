#!/usr/bin/env python

#############################################################################
# Mellanox
#
# implementation of new platform api
#############################################################################

try:
    from sonic_platform_base.component_base import ComponentBase
    from glob import glob
    import subprocess
    import io
    import re
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

#components definitions
COMPONENT_BIOS = "BIOS"
COMPONENT_CPLD = "CPLD"

BIOS_QUERY_VERSION_COMMAND = 'dmidecode -t 11'
CPLD_VERSION_FILE_PATTERN = '/var/run/hw-management/system/cpld[0-9]_version'
CPLD_VERSION_MAX_LENGTH = 4

class Component(ComponentBase):
    def get_name(self):
        """
        Retrieves the name of the component

        Returns:
            A string containing the name of the component
        """
        return self.name


    def _read_generic_file(self, filename, len):
        """
        Read a generic file, returns the contents of the file
        """
        result = ''
        try:
            with io.open(filename, 'r') as fileobj:
                result = fileobj.read(len)
            return result
        except IOError as e:
            raise RuntimeError("Failed to read file {} due to {}".format(filename, repr(e)))


    def _get_command_result(self, cmdline):
        try:
            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            result = stdout.rstrip('\n')

        except OSError as e:
            raise RuntimeError("Failed to execute command {} due to {}".format(cmdline, repr(e)))

        return result


class ComponentBIOS(Component):
    BIOS_VERSION_PARSE_PATTERN = 'OEM[\s]*Strings\n[\s]*String[\s]*1:[\s]*([0-9a-zA-Z_\.]*)'


    def __init__(self):
        self.name = COMPONENT_BIOS


    def get_description(self):
        """
        Retrieves the description of the component

        Returns:
            A string containing the description of the component
        """
        return "BIOS - Basic Input/Output System"


    def get_firmware_version(self):
        """
        Retrieves the firmware version of the component

        Returns:
            A string containing the firmware version of the component

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
            m = re.search(self.BIOS_VERSION_PARSE_PATTERN, bios_ver_str)
            result = m.group(1)
        except AttributeError as e:
            raise RuntimeError("Failed to parse BIOS version by {} from {} due to {}".format(
                               self.BIOS_VERSION_PARSE_PATTERN, bios_ver_str, repr(e)))

        return result


class ComponentCPLD(Component):
    def __init__(self):
        self.name = COMPONENT_CPLD


    def get_description(self):
        """
        Retrieves the description of the component

        Returns:
            A string containing the description of the component
        """
        return "CPLD - includes all CPLDs in the switch"


    def get_firmware_version(self):
        """
        Retrieves the firmware version of the component

        Returns:
            A string containing the firmware version of the component
        """
        cpld_version_file_list = glob(CPLD_VERSION_FILE_PATTERN)
        cpld_version = ''
        if cpld_version_file_list is not None and cpld_version_file_list:
            cpld_version_file_list.sort()
            for version_file in cpld_version_file_list:
                version = self._read_generic_file(version_file, CPLD_VERSION_MAX_LENGTH)
                if not cpld_version == '':
                    cpld_version += '.'
                cpld_version += version.rstrip('\n')
        else:
            raise RuntimeError("Failed to get CPLD version files by matching {}".format(CPLD_VERSION_FILE_PATTERN))

        return cpld_version

