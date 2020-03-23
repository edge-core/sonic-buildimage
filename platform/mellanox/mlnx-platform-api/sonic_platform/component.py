#!/usr/bin/env python

#############################################################################
# Mellanox
#
# implementation of new platform api
#############################################################################
from __future__ import print_function
try:
    from sonic_platform_base.component_base import ComponentBase
    from sonic_device_util import get_machine_info
    from glob import glob
    import subprocess
    import io
    import os
    import re
    import sys
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

ZERO = '0'
NEWLINE = '\n'

class Component(ComponentBase):
    def __init__(self):
        self.name = None
        self.description = None
        self.image_ext_name = None


    def get_name(self):
        """
        Retrieves the name of the component

        Returns:
            A string containing the name of the component
        """
        return self.name


    def get_description(self):
        """
        Retrieves the description of the component

        Returns:
            A string containing the description of the component
        """
        return self.description


    @staticmethod
    def _read_generic_file(filename, len, ignore_errors=False):
        """
        Read a generic file, returns the contents of the file
        """
        result = None

        try:
            with io.open(filename, 'r') as fileobj:
                result = fileobj.read(len)
        except IOError as e:
            if not ignore_errors:
                raise RuntimeError("Failed to read file {} due to {}".format(filename, repr(e)))

        return result


    @staticmethod
    def _get_command_result(cmdline):
        try:
            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            rc = proc.wait()
            result = stdout.rstrip('\n')
            if rc != 0:
                raise RuntimeError("Failed to execute command {}, return code {}, message {}".format(cmdline, rc, stdout))

        except OSError as e:
            raise RuntimeError("Failed to execute command {} due to {}".format(cmdline, repr(e)))

        return result


    def _check_file_validity(self, image_path):
        # check whether the image file exists
        if not os.path.isfile(image_path):
            print("ERROR: File {} doesn't exist or is not a file".format(image_path))
            return False

        if self.image_ext_name is not None:
            name_list = os.path.splitext(image_path)
            if name_list[1] != self.image_ext_name:
                print("ERROR: Extend name of file {} is wrong. Image for {} should have extend name {}".format(image_path, self.name, self.image_ext_name))
                return False

        return True



class ComponentBIOS(Component):
    COMPONENT_NAME = 'BIOS'
    COMPONENT_DESCRIPTION = 'BIOS - Basic Input/Output System'
    COMPONENT_FIRMWARE_EXTENSION = '.rom'

    # To update BIOS requires the ONIE with version 5.2.0016 or upper
    ONIE_VERSION_PARSE_PATTERN = '[0-9]{4}\.[0-9]{2}-([0-9]+)\.([0-9]+)\.([0-9]+)'
    ONIE_VERSION_MAJOR_OFFSET = 1
    ONIE_VERSION_MINOR_OFFSET = 2
    ONIE_VERSION_RELEASE_OFFSET = 3
    ONIE_REQUIRED_MAJOR = '5'
    ONIE_REQUIRED_MINOR = '2'
    ONIE_REQUIRED_RELEASE = '0016'

    BIOS_VERSION_PARSE_PATTERN = 'OEM[\s]*Strings\n[\s]*String[\s]*1:[\s]*([0-9a-zA-Z_\.]*)'
    BIOS_PENDING_UPDATE_PATTERN = '([0-9A-Za-z_]*.rom)[\s]*\|[\s]*bios_update'

    ONIE_FW_UPDATE_CMD_ADD = '/usr/bin/onie-fw-update.sh add {}'
    ONIE_FW_UPDATE_CMD_REMOVE = '/usr/bin/onie-fw-update.sh remove {}'
    ONIE_FW_UPDATE_CMD_UPDATE = '/usr/bin/onie-fw-update.sh update'
    ONIE_FW_UPDATE_CMD_SHOW = '/usr/bin/onie-fw-update.sh show-pending'

    BIOS_QUERY_VERSION_COMMAND = 'dmidecode -t 11'

    def __init__(self):
        self.name = self.COMPONENT_NAME
        self.description = self.COMPONENT_DESCRIPTION
        self.image_ext_name = self.COMPONENT_FIRMWARE_EXTENSION


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
        try:
            bios_ver_str = self._get_command_result(self.BIOS_QUERY_VERSION_COMMAND)
            m = re.search(self.BIOS_VERSION_PARSE_PATTERN, bios_ver_str)
            result = m.group(1)
        except (AttributeError, RuntimeError) as e:
            raise RuntimeError("Failed to parse BIOS version due to {}".format(repr(e)))

        return result


    def _check_onie_version(self):
        # check ONIE version. To update ONIE requires version 5.2.0016 or later.
        try:
            machine_info = get_machine_info()
            onie_version_string = machine_info['onie_version']
            m = re.search(self.ONIE_VERSION_PARSE_PATTERN, onie_version_string)
            onie_major = m.group(self.ONIE_VERSION_MAJOR_OFFSET)
            onie_minor = m.group(self.ONIE_VERSION_MINOR_OFFSET)
            onie_release = m.group(self.ONIE_VERSION_RELEASE_OFFSET)
        except AttributeError as e:
            print("ERROR: Failed to parse ONIE version by {} from {} due to {}".format(
                                self.ONIE_VERSION_PARSE_PATTERN, machine_conf, repr(e)))
            return False

        if onie_major < self.ONIE_REQUIRED_MAJOR or onie_minor < self.ONIE_REQUIRED_MINOR or onie_release < self.ONIE_REQUIRED_RELEASE:
            print("ERROR: ONIE {}.{}.{} or later is required".format(self.ONIE_REQUIRED_MAJOR, self.ONIE_REQUIRED_MINOR, self.ONIE_REQUIRED_RELEASE))
            return False

        return True


    def install_firmware(self, image_path):
        """
        Installs firmware to the component

        Args:
            image_path: A string, path to firmware image

        Returns:
            A boolean, True if install was successful, False if not
        """
        # check ONIE version requirement
        if not self._check_onie_version():
            return False

        # check whether the file exists
        if not self._check_file_validity(image_path):
            return False

        # do the real work
        try:
            # check whether there has already been some images pending
            # if yes, remove them
            result = self._get_command_result(self.ONIE_FW_UPDATE_CMD_SHOW)
            pending_list = result.split("\n")
            for pending in pending_list:
                m = re.match(self.BIOS_PENDING_UPDATE_PATTERN, pending)
                if m is not None:
                    pending_image = m.group(1)
                    self._get_command_result(self.ONIE_FW_UPDATE_CMD_REMOVE.format(pending_image))
                    print("WARNING: Image {} which is already pending to upgrade has been removed".format(pending_image))

            result = subprocess.check_call(self.ONIE_FW_UPDATE_CMD_ADD.format(image_path).split())
            if result:
                return False
            result = subprocess.check_call(self.ONIE_FW_UPDATE_CMD_UPDATE.split())
            if result:
                return False
        except Exception as e:
            print("ERROR: Installing BIOS failed due to {}".format(repr(e)))
            return False

        print("INFO: Reboot is required to finish BIOS installation")
        return True



class ComponentCPLD(Component):
    COMPONENT_NAME = 'CPLD{}'
    COMPONENT_DESCRIPTION = 'CPLD - Complex Programmable Logic Device'
    COMPONENT_FIRMWARE_EXTENSION = '.vme'

    CPLD_NUMBER_FILE = '/var/run/hw-management/config/cpld_num'
    CPLD_PART_NUMBER_FILE = '/var/run/hw-management/system/cpld{}_pn'
    CPLD_VERSION_FILE = '/var/run/hw-management/system/cpld{}_version'
    CPLD_VERSION_MINOR_FILE = '/var/run/hw-management/system/cpld{}_version_minor'

    CPLD_NUMBER_MAX_LENGTH = 1
    CPLD_PART_NUMBER_MAX_LENGTH = 6
    CPLD_VERSION_MAX_LENGTH = 2
    CPLD_VERSION_MINOR_MAX_LENGTH = 2

    CPLD_PART_NUMBER_DEFAULT = ZERO
    CPLD_VERSION_MINOR_DEFAULT = ZERO

    CPLD_UPDATE_COMMAND = 'cpldupdate --dev {} {}'
    CPLD_INSTALL_SUCCESS_FLAG = 'PASS!'

    MST_DEVICE_PATTERN = '/dev/mst/mt[0-9]*_pci_cr0'

    def __init__(self, idx):
        self.idx = idx
        self.name = self.COMPONENT_NAME.format(self.idx)
        self.description = self.COMPONENT_DESCRIPTION
        self.image_ext_name = self.COMPONENT_FIRMWARE_EXTENSION


    def get_firmware_version(self):
        """
        Retrieves the firmware version of the component

        Returns:
            A string containing the firmware version of the component
        """

        part_number_file = self.CPLD_PART_NUMBER_FILE.format(self.idx)
        version_file = self.CPLD_VERSION_FILE.format(self.idx)
        version_minor_file = self.CPLD_VERSION_MINOR_FILE.format(self.idx)

        part_number = self._read_generic_file(part_number_file, self.CPLD_PART_NUMBER_MAX_LENGTH, True)
        version = self._read_generic_file(version_file, self.CPLD_VERSION_MAX_LENGTH)
        version_minor = self._read_generic_file(version_minor_file, self.CPLD_VERSION_MINOR_MAX_LENGTH, True)

        if part_number is None:
            part_number = self.CPLD_PART_NUMBER_DEFAULT

        if version_minor is None:
            version_minor = self.CPLD_VERSION_MINOR_DEFAULT

        part_number = part_number.rstrip(NEWLINE).zfill(self.CPLD_PART_NUMBER_MAX_LENGTH)
        version = version.rstrip(NEWLINE).zfill(self.CPLD_VERSION_MAX_LENGTH)
        version_minor = version_minor.rstrip(NEWLINE).zfill(self.CPLD_VERSION_MINOR_MAX_LENGTH)

        return "CPLD{}_REV{}{}".format(part_number, version, version_minor)


    def _get_mst_device(self):
        mst_dev_list = glob(self.MST_DEVICE_PATTERN)
        if mst_dev_list is None or len(mst_dev_list) != 1:
            return None
        return mst_dev_list


    def install_firmware(self, image_path):
        """
        Installs firmware to the component

        Args:
            image_path: A string, path to firmware image

        Returns:
            A boolean, True if install was successful, False if not

        Details:
            The command "cpldupdate" is provided to install CPLD. There are two ways to do it:
                1. To burn CPLD via gpio, which is faster but only supported on new systems, like Anaconda, ...
                2. To install CPLD via firmware, which is slower but supported on older systems.
                   This also requires the mst device designated.
            "cpldupdate --dev <devname> <vme_file>" has the logic of testing whether to update via gpio is supported,
            and if so then go this way, otherwise tries updating software via fw. So we take advantage of it to update the CPLD. 
            By doing so we don't have to mind whether to update via gpio supported, which belongs to hardware details.

            So the procedure should be:
                1. Test whether the file exists
                2. Fetch the mst device name
                3. Update CPLD via executing "cpldupdate --dev <devname> <vme_file>"
                4. Check the result
        """
        # check whether the image file exists
        if not self._check_file_validity(image_path):
            return False

        mst_dev_list = self._get_mst_device()
        if mst_dev_list is None:
            print("ERROR: Failed to get mst device which is required for CPLD updating or multiple device files matched")
            return False

        cmdline = self.CPLD_UPDATE_COMMAND.format(mst_dev_list[0], image_path)
        outputline = ""
        success_flag = False
        try:
            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
            while True:
                out = proc.stdout.read(1)

                if out == '' and proc.poll() != None:
                    break

                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()
                    outputline += out

                if (out == '\n' or out == '\r') and len(outputline):
                    m = re.search(self.CPLD_INSTALL_SUCCESS_FLAG, outputline)
                    if m and m.group(0) == self.CPLD_INSTALL_SUCCESS_FLAG:
                        success_flag = True

            if proc.returncode:
                print("ERROR: Upgrade CPLD failed, return code {}".format(proc.returncode))
                success_flag = False

        except OSError as e:
            raise RuntimeError("Failed to execute command {} due to {}".format(cmdline, repr(e)))

        if success_flag:
            print("INFO: Refresh or power cycle is required to finish CPLD installation")
        else:
            print("ERROR: Failed to install CPLD")

        return success_flag


    @classmethod
    def get_component_list(cls):
        component_list = [ ]

        cpld_number = cls._read_generic_file(cls.CPLD_NUMBER_FILE, cls.CPLD_NUMBER_MAX_LENGTH)
        cpld_number = cpld_number.rstrip(NEWLINE)

        for cpld_idx in xrange(1, int(cpld_number) + 1):
            component_list.append(cls(cpld_idx))

        return component_list
