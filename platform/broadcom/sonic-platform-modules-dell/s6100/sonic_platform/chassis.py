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
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
    from sonic_platform.psu import Psu
    from sonic_platform.fan import Fan
    from eeprom import Eeprom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

MAX_S6100_FAN = 4
MAX_S6100_PSU = 2


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
          16: [8, 50], 17: [8, 51], 18: [8, 52], 19: [8, 53],
          20: [8, 54], 21: [8, 55], 22: [8, 56], 23: [8, 57],
          24: [8, 58], 25: [8, 59], 26: [8, 60], 27: [8, 61],
          28: [8, 62], 29: [8, 63], 30: [8, 64], 31: [8, 65],
          # IOM 3
          32: [7, 34], 33: [7, 35], 34: [7, 36], 35: [7, 37],
          36: [7, 38], 37: [7, 39], 38: [7, 40], 39: [7, 41],
          40: [7, 42], 41: [7, 43], 42: [7, 44], 43: [7, 45],
          44: [7, 46], 45: [7, 47], 46: [7, 48], 47: [7, 49],
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

    def get_name(self):
        """
        Retrieves the name of the device
        Returns:
            string: The name of the device
        """
        return self.sys_eeprom.modelstr()

    def get_presence(self):
        """
        Retrieves the presence of the device
        Returns:
            bool: True if device is present, False if not
        """
        return True

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self.sys_eeprom.part_number_str()

    def get_serial(self):
        """
        Retrieves the serial number of the device (Service tag)
        Returns:
            string: Serial number of device
        """
        return self.sys_eeprom.serial_str()

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
            A string containing the hardware serial number for this chassis.
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
