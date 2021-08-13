########################################################################
# NOKIA IXS7215
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Components' (e.g., BIOS, CPLD, FPGA, etc.) available in
# the platform
#
########################################################################

try:
    import os
    import sys
    import subprocess
    import ntpath
    from sonic_platform_base.component_base import ComponentBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

smbus_present = 1
try:
    import smbus
except ImportError as e:
    smbus_present = 0

if sys.version_info[0] < 3:
    import commands as cmd
else:
    import subprocess as cmd


class Component(ComponentBase):
    """Nokia platform-specific Component class"""

    CHASSIS_COMPONENTS = [
        ["System-CPLD", "Used for managing SFPs, LEDs, PSUs and FANs "],
        ["U-Boot", "Performs initialization during booting"],
    ]
    CPLD_UPDATE_COMMAND = 'cp /usr/sbin/vme /tmp; cp {} /tmp; cd /tmp; ./vme {};'

    def __init__(self, component_index):
        self.index = component_index
        self.name = self.CHASSIS_COMPONENTS[self.index][0]
        self.description = self.CHASSIS_COMPONENTS[self.index][1]

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

    def _get_cpld_version(self, cpld_number):

        if smbus_present == 0:
            cmdstatus, cpld_version = cmd.getstatusoutput('sudo i2cget -y 0 0x41 0x2')
        else:
            bus = smbus.SMBus(0)
            DEVICE_ADDRESS = 0x41
            DEVICE_REG = 0x2
            cpld_version = str(bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG))

        return str(int(cpld_version, 16))

    def get_name(self):
        """
        Retrieves the name of the component

        Returns:
            A string containing the name of the component
        """
        return self.name

    def get_model(self):
        """
        Retrieves the part number of the component
        Returns:
            string: Part number of component
        """
        return 'NA'

    def get_serial(self):
        """
        Retrieves the serial number of the component
        Returns:
            string: Serial number of component
        """
        return 'NA'

    def get_presence(self):
        """
        Retrieves the presence of the component
        Returns:
            bool: True if  present, False if not
        """
        return True

    def get_status(self):
        """
        Retrieves the operational status of the component
        Returns:
            bool: True if component is operating properly, False if not
        """
        return True

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        Returns:
            integer: The 1-based relative physical position in parent
            device or -1 if cannot determine the position
        """
        return -1

    def is_replaceable(self):
        """
        Indicate whether component is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False

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
        if self.index == 0:
            return self._get_cpld_version(self.index)

        if self.index == 1:
            cmdstatus, uboot_version = cmd.getstatusoutput('grep --null-data U-Boot /dev/mtd0ro|head -1 | cut -d" " -f2-4')
            return uboot_version

    def install_firmware(self, image_path):
        """
        Installs firmware to the component

        Args:
            image_path: A string, path to firmware image

        Returns:
            A boolean, True if install was successful, False if not
        """
        image_name = ntpath.basename(image_path)
        print(" ixs7215 - install cpld {}".format(image_name))

        # check whether the image file exists
        if not os.path.isfile(image_path):
            print("ERROR: the cpld image {} doesn't exist ".format(image_path))
            return False

        cmdline = self.CPLD_UPDATE_COMMAND.format(image_path, image_name)

        success_flag = False

        try:
            subprocess.check_call(cmdline, stderr=subprocess.STDOUT, shell=True)
            success_flag = True
        except subprocess.CalledProcessError as e:
            print("ERROR: Failed to upgrade CPLD: rc={}".format(e.returncode))

        if success_flag:
            print("INFO: Refresh or power cycle is required to finish CPLD installation")

        return success_flag

