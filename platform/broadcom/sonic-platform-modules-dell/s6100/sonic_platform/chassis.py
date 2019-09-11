#!/usr/bin/env python

#############################################################################
# DELLEMC S6100
#
# Module contains an implementation of SONiC Platform Base API and
# provides the platform information
#
#############################################################################

try:
    import os
    import sys
    import click
    import subprocess
    import glob
    import sonic_device_util
    from commands import getstatusoutput
    from sonic_platform_base.platform_base import PlatformBase
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
    from sonic_platform.psu import Psu
    from sonic_platform.fan import Fan
    from eeprom import Eeprom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


MAX_S6100_FAN = 4
MAX_S6100_PSU = 2

BIOS_QUERY_VERSION_COMMAND = "dmidecode -s system-version"
#components definitions
COMPONENT_BIOS = "BIOS"
SWITCH_CPLD = "CPLD"
SMF_FPGA = "FPGA1"


class Chassis(ChassisBase):
    """
    DELLEMC Platform-specific Chassis class
    """

    HWMON_DIR = "/sys/devices/platform/SMF.512/hwmon/"
    HWMON_NODE = os.listdir(HWMON_DIR)[0]
    MAILBOX_DIR = HWMON_DIR + HWMON_NODE

    PORT_START = 0
    PORT_END = 63
    PORTS_IN_BLOCK = (PORT_END + 1)
    IOM1_PORT_START = 0
    IOM2_PORT_START = 16
    IOM3_PORT_START = 32
    IOM4_PORT_START = 48

    PORT_I2C_MAPPING = {}
    # 0th Index = i2cLine, 1st Index = EepromIdx in i2cLine
    EEPROM_I2C_MAPPING = {
          # IOM 1
           0: [6, 66],  1: [6, 67],  2: [6, 68],  3: [6, 69],
           4: [6, 70],  5: [6, 71],  6: [6, 72],  7: [6, 73],
           8: [6, 74],  9: [6, 75], 10: [6, 76], 11: [6, 77],
          12: [6, 78], 13: [6, 79], 14: [6, 80], 15: [6, 81],
          # IOM 2
          16: [8, 34], 17: [8, 35], 18: [8, 36], 19: [8, 37],
          20: [8, 38], 21: [8, 39], 22: [8, 40], 23: [8, 41],
          24: [8, 42], 25: [8, 43], 26: [8, 44], 27: [8, 45],
          28: [8, 46], 29: [8, 47], 30: [8, 48], 31: [8, 49],
          # IOM 3
          32: [7, 50], 33: [7, 51], 34: [7, 52], 35: [7, 53],
          36: [7, 54], 37: [7, 55], 38: [7, 56], 39: [7, 57],
          40: [7, 58], 41: [7, 59], 42: [7, 60], 43: [7, 61],
          44: [7, 62], 45: [7, 63], 46: [7, 64], 47: [7, 65],
          # IOM 4
          48: [9, 18], 49: [9, 19], 50: [9, 20], 51: [9, 21],
          52: [9, 22], 53: [9, 23], 54: [9, 24], 55: [9, 25],
          56: [9, 26], 57: [9, 27], 58: [9, 28], 59: [9, 29],
          60: [9, 30], 61: [9, 31], 62: [9, 32], 63: [9, 33]
      }

    reset_reason_dict = {}
    reset_reason_dict[11] = ChassisBase.REBOOT_CAUSE_POWER_LOSS
    reset_reason_dict[33] = ChassisBase.REBOOT_CAUSE_WATCHDOG
    reset_reason_dict[44] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE
    reset_reason_dict[55] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE

    power_reason_dict = {}
    power_reason_dict[11] = ChassisBase.REBOOT_CAUSE_POWER_LOSS
    power_reason_dict[22] = ChassisBase.REBOOT_CAUSE_THERMAL_OVERLOAD_CPU
    power_reason_dict[33] = ChassisBase.REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC
    power_reason_dict[44] = ChassisBase.REBOOT_CAUSE_INSUFFICIENT_FAN_SPEED

    def __init__(self):

        ChassisBase.__init__(self)
        # Initialize EEPROM
        self.sys_eeprom = Eeprom()
        for i in range(MAX_S6100_FAN):
            fan = Fan(i)
            self._fan_list.append(fan)

        for i in range(MAX_S6100_PSU):
            psu = Psu(i)
            self._psu_list.append(psu)

        # Initialize component list
        self._component_name_list.append(COMPONENT_BIOS)
        self._component_name_list.append(SWITCH_CPLD)
        self._component_name_list.append(SMF_FPGA)

        self._populate_port_i2c_mapping()

        # sfp.py will read eeprom contents and retrive the eeprom data.
        # It will also provide support sfp controls like reset and setting
        # low power mode.
        # We pass the eeprom path and sfp control path from chassis.py
        # So that sfp.py implementation can be generic to all platforms
        eeprom_base = "/sys/class/i2c-adapter/i2c-{0}/i2c-{1}/{1}-0050/eeprom"
        sfp_ctrl_base = "/sys/class/i2c-adapter/i2c-{0}/{0}-003e/"
        for index in range(0, self.PORTS_IN_BLOCK):
            eeprom_path = eeprom_base.format(self.EEPROM_I2C_MAPPING[index][0],
                                             self.EEPROM_I2C_MAPPING[index][1])
            sfp_control = sfp_ctrl_base.format(self.PORT_I2C_MAPPING[index])
            sfp_node = Sfp(index, 'QSFP', eeprom_path, sfp_control, index)
            self._sfp_list.append(sfp_node)

    def _populate_port_i2c_mapping(self):
        # port_num and i2c match
        for port_num in range(0, self.PORTS_IN_BLOCK):
            if((port_num >= self.IOM1_PORT_START) and
                    (port_num < self.IOM2_PORT_START)):
                i2c_line = 14
            elif((port_num >= self.IOM2_PORT_START) and
                    (port_num < self.IOM3_PORT_START)):
                i2c_line = 16
            elif((port_num >= self.IOM3_PORT_START) and
                    (port_num <self.IOM4_PORT_START)):
                i2c_line = 15
            elif((port_num >= self.IOM4_PORT_START) and
                    (port_num < self.PORTS_IN_BLOCK)):
                i2c_line = 17
            self.PORT_I2C_MAPPING[port_num] = i2c_line

    def _get_pmc_register(self, reg_name):
        # On successful read, returns the value read from given
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'
        mb_reg_file = self.MAILBOX_DIR + '/' + reg_name

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

    # Run bash command and print output to stdout
    def run_command(self, command):
        click.echo(click.style("Command: ", fg='cyan') +
                   click.style(command, fg='green'))

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()

        click.echo(out)

        if proc.returncode != 0:
            sys.exit(proc.returncode)

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
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """

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

        reset_reason = int(self._get_pmc_register('smf_reset_reason'))
        power_reason = int(self._get_pmc_register('smf_poweron_reason'))

        # Reset_Reason = 11 ==> PowerLoss
        # So return the reboot reason from Last Power_Reason Dictionary
        # If Reset_Reason is not 11 return from Reset_Reason dictionary
        # Also check if power_reason, reset_reason are valid values by
        # checking key presence in dictionary else return
        # REBOOT_CAUSE_HARDWARE_OTHER as the Power_Reason and Reset_Reason
        # registers returned invalid data
        if (reset_reason == 11):
            if (power_reason in self.power_reason_dict):
                return (self.power_reason_dict[power_reason], None)
        else:
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

    def _get_cpld_version(self):
        io_resource = "/dev/port"
        CPLD1_VERSION_ADDR = 0x100

        fd = os.open(io_resource, os.O_RDONLY)
        if (fd < 0):
            return 'NA'
        if (os.lseek(fd, CPLD1_VERSION_ADDR, os.SEEK_SET)
            != CPLD1_VERSION_ADDR):
            return 'NA'

        buf = os.read(fd, 1)
        cpld_version = ord(buf)
        os.close(fd)

        return "%d.%d" % (((cpld_version & 0xF0) >> 4), cpld_version & 0xF)

    def _get_fpga_version(self):
        fpga_ver = float(self._get_pmc_register('smf_firmware_ver'))
        return fpga_ver

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
            elif component_name == SWITCH_CPLD:
                return self._get_cpld_version()
            elif component_name == SMF_FPGA:
                return self._get_fpga_version()

        return None

    def install_component_firmware(self, component_name, image_path):

        bios_image = None
        bios_version = "3.25.0."
        bios_file_name = "S6100*BIOS*"
        flashrom = "/usr/local/bin/flashrom"
        PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
        machine_info = sonic_device_util.get_machine_info()
        platform = sonic_device_util.get_platform_info(machine_info)
        platform_path = "/".join([PLATFORM_ROOT_PATH, platform, "bin"])

        warning = """
        ********************************************************************
        * Warning - Upgrading BIOS is inherently risky and should only be  *
        * attempted when necessary.  A failure at this upgrade may cause   *
        * a board RMA.  Proceed with caution !                             *
        ********************************************************************
        """

        if component_name in self._component_name_list:
            if component_name == self._component_name_list[0]:  # BIOS

                # current BIOS version
                current_bios_version = self.get_firmware_version("BIOS")

                # Construct BIOS image path
                if image_path is not None:
                    image_path = image_path + platform_path
                    for name in glob.glob(
                                    os.path.join(image_path, bios_file_name)):
                        bios_image = image_path = name

                if not bios_image:
                    print "BIOS image file not found:", image_path
                    return False

                # Extract BIOS image version
                bios_image = os.path.basename(bios_image)
                bios_image = bios_image.strip('S6100-BIOS-')
                bios_image_version = bios_image.strip('.bin')

                if bios_image_version.startswith(bios_version):
                    bios_image_minor = bios_image_version.replace(
                                                bios_image_version[:7], '')
                    if bios_image_minor.startswith("2"):
                        bios_image_minor = bios_image_minor.split("-")[1]

                if current_bios_version.startswith(bios_version):
                    current_bios_minor = current_bios_version.replace(
                                                current_bios_version[:7], '')
                    if current_bios_minor.startswith("2"):
                        current_bios_minor = current_bios_minor.split("-")[1]

                # BIOS version check
                if bios_image_minor > current_bios_minor:

                    print warning
                    prompt_text = "New BIOS image " + bios_image_version + \
                        " available to install, continue?"
                    yes = click.confirm(prompt_text)

                elif current_bios_minor > bios_image_minor:

                    print warning
                    prompt_text = "Do you want to downgrade BIOS image from " \
                        + current_bios_version + " to " + \
                        bios_image_version + " continue?"

                    yes = click.confirm(prompt_text)

                else:
                    print("BIOS is already with {} latest version".format(
                        current_bios_version))
                    return True

                if yes:
                    command = flashrom + " -p" + " internal" + " -w " + \
                                         image_path
                    self.run_command(command)

            elif component_name == self._component_name_list[1]:  # CPLD1
                return False

            elif component_name == self._component_name_list[2]:  # SMF
                return False
        else:
            print "Invalid component Name:", component_name

        return True


