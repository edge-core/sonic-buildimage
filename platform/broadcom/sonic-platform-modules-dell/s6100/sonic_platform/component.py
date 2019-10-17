#!/usr/bin/env python

########################################################################
# DELLEMC S6100
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Components' (e.g., BIOS, CPLD, FPGA, etc.) available in
# the platform
#
########################################################################

try:
    import os
    import subprocess
    from sonic_platform_base.component_base import ComponentBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

BIOS_QUERY_VERSION_COMMAND = "dmidecode -s system-version"


class Component(ComponentBase):
    """DellEMC Platform-specific Component class"""

    HWMON_DIR = "/sys/devices/platform/SMF.512/hwmon/"
    HWMON_NODE = os.listdir(HWMON_DIR)[0]
    MAILBOX_DIR = HWMON_DIR + HWMON_NODE

    CHASSIS_COMPONENTS = [
        ["BIOS", ("Performs initialization of hardware components during "
                  "booting")],
        ["CPLD", "Used for managing IO modules, SFP+ modules and system LEDs"],
        ["FPGA", ("Platform management controller for on-board temperature "
                  "monitoring, in-chassis power, Fan and LED control")]
    ]
    MODULE_COMPONENT = [
        "IOM{}-CPLD",
        "Used for managing QSFP+ modules ({0}-{1})"
    ]

    def __init__(self, component_index=0,
                 is_module=False, iom_index=0, i2c_line=0):

        self.is_module_component = is_module

        if self.is_module_component:
            self.index = iom_index
            self.name = self.MODULE_COMPONENT[0].format(self.index)
            self.description = self.MODULE_COMPONENT[1].format(
                               ((self.index - 1) * 16) + 1, self.index * 16)
            self.cpld_version_file = ("/sys/class/i2c-adapter/i2c-{0}/{0}-003e"
                                      "/iom_cpld_vers").format(i2c_line)
        else:
            self.index = component_index
            self.name = self.CHASSIS_COMPONENTS[self.index][0]
            self.description = self.CHASSIS_COMPONENTS[self.index][1]

    def _read_sysfs_file(self, sysfs_file):
        # On successful read, returns the value read from given
        # sysfs_file and on failure returns 'ERR'
        rv = 'ERR'

        if (not os.path.isfile(sysfs_file)):
            return rv

        try:
            with open(sysfs_file, 'r') as fd:
                rv = fd.read()
        except Exception as error:
            rv = 'ERR'

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def _get_command_result(self, cmdline):
        try:
            proc = subprocess.Popen(cmdline.split(), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            result = stdout.rstrip('\n')
        except OSError:
            result = None

        return result

    def _get_cpld_version(self):
        io_resource = "/dev/port"
        CPLD_VERSION_ADDR = 0x100

        fd = os.open(io_resource, os.O_RDONLY)
        if (fd < 0):
            return 'NA'

        if (os.lseek(fd, CPLD_VERSION_ADDR, os.SEEK_SET) != CPLD_VERSION_ADDR):
            os.close(fd)
            return 'NA'

        buf = os.read(fd, 1)
        cpld_version = str(ord(buf))
        os.close(fd)

        return cpld_version

    def _get_iom_cpld_version(self):
        ver_str = self._read_sysfs_file(self.cpld_version_file)
        if (ver_str != 'ERR'):
            if ver_str == 'read error':
                return 'NA'

            ver_str = ver_str.rstrip('\r\n')
            cpld_version = str(int(ver_str.split(':')[1], 16))
            return cpld_version
        else:
            return 'NA'

    def _get_fpga_version(self):
        fpga_ver_file = self.MAILBOX_DIR + '/smf_firmware_ver'
        fpga_ver = self._read_sysfs_file(fpga_ver_file)
        if (fpga_ver != 'ERR'):
            return fpga_ver
        else:
            return 'NA'

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

    def get_firmware_version(self):
        """
        Retrieves the firmware version of the component

        Returns:
            A string containing the firmware version of the component
        """
        if self.is_module_component:    # IOM CPLD
            return self._get_iom_cpld_version()
        else:
            if self.index == 0:         # BIOS
                bios_ver = self._get_command_result(BIOS_QUERY_VERSION_COMMAND)

                if not bios_ver:
                    return 'NA'
                else:
                    return bios_ver

            elif self.index == 1:       # SwitchCard CPLD
                return self._get_cpld_version()
            elif self.index == 2:       # FPGA
                return self._get_fpga_version()

    def install_firmware(self, image_path):
        """
        Installs firmware to the component

        Args:
            image_path: A string, path to firmware image

        Returns:
            A boolean, True if install was successful, False if not
        """
        return False
