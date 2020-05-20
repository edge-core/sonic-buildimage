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
    from sonic_platform_base.platform_base import PlatformBase
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
    from sonic_platform.psu import Psu
    from sonic_platform.fan import Fan
    from sonic_platform.module import Module
    from sonic_platform.thermal import Thermal
    from sonic_platform.component import Component
    from sonic_platform.watchdog import Watchdog
    from eeprom import Eeprom
    import time
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

MAX_S6100_MODULE = 4
MAX_S6100_FAN = 4
MAX_S6100_PSU = 2
MAX_S6100_THERMAL = 10
MAX_S6100_COMPONENT = 3


class Chassis(ChassisBase):
    """
    DELLEMC Platform-specific Chassis class
    """

    HWMON_DIR = "/sys/devices/platform/SMF.512/hwmon/"
    HWMON_NODE = os.listdir(HWMON_DIR)[0]
    MAILBOX_DIR = HWMON_DIR + HWMON_NODE
    POLL_INTERVAL = 1 # Poll interval in seconds

    reset_reason_dict = {}
    reset_reason_dict[11] = ChassisBase.REBOOT_CAUSE_POWER_LOSS
    reset_reason_dict[33] = ChassisBase.REBOOT_CAUSE_WATCHDOG
    reset_reason_dict[44] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE
    reset_reason_dict[55] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE
    reset_reason_dict[66] = ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER
    reset_reason_dict[77] = ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER

    power_reason_dict = {}
    power_reason_dict[11] = ChassisBase.REBOOT_CAUSE_POWER_LOSS
    power_reason_dict[22] = ChassisBase.REBOOT_CAUSE_THERMAL_OVERLOAD_CPU
    power_reason_dict[33] = ChassisBase.REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC
    power_reason_dict[44] = ChassisBase.REBOOT_CAUSE_INSUFFICIENT_FAN_SPEED

    def __init__(self):

        ChassisBase.__init__(self)
        # Initialize EEPROM
        self._eeprom = Eeprom()
        for i in range(MAX_S6100_MODULE):
            module = Module(i)
            self._module_list.append(module)
            self._sfp_list.extend(module._sfp_list)

        for i in range(MAX_S6100_FAN):
            fan = Fan(i)
            self._fan_list.append(fan)

        for i in range(MAX_S6100_PSU):
            psu = Psu(i)
            self._psu_list.append(psu)

        for i in range(MAX_S6100_THERMAL):
            thermal = Thermal(i)
            self._thermal_list.append(thermal)

        for i in range(MAX_S6100_COMPONENT):
            component = Component(i)
            self._component_list.append(component)

        self._watchdog = Watchdog()
        self._transceiver_presence = self._get_transceiver_presence()

    def _get_reboot_reason_smf_register(self):
        # In S6100, mb_poweron_reason register will
        # Returns 0xaa or 0xcc on software reload
        # Returns 0xff or 0xbb on power-cycle
        # Returns 0xdd on Watchdog
        # Returns 0xee on Thermal Shutdown
        # Returns 0x99 on Unknown reset
        smf_mb_reg_reason = self._get_pmc_register('mb_poweron_reason')
        return int(smf_mb_reg_reason, 16)

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

    def _get_register(self, reg_file):
        # On successful read, returns the value read from given
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'

        if (not os.path.isfile(reg_file)):
            return rv

        try:
            with open(reg_file, 'r') as fd:
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

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis

        Returns:
            A string containing the hardware serial number for this
            chassis.
        """
        return self._eeprom.serial_number_str()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.system_eeprom_info()

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
        smf_mb_reg_reason = self._get_reboot_reason_smf_register()

        if ((smf_mb_reg_reason == 0xbb) or (smf_mb_reg_reason == 0xff)):
            return (ChassisBase.REBOOT_CAUSE_POWER_LOSS, None)
        elif ((smf_mb_reg_reason == 0xaa) or (smf_mb_reg_reason == 0xcc)):
            return (ChassisBase.REBOOT_CAUSE_NON_HARDWARE, None)
        elif (smf_mb_reg_reason == 0xdd):
            return (ChassisBase.REBOOT_CAUSE_WATCHDOG, None)
        elif (smf_mb_reg_reason == 0xee):
            return (self.power_reason_dict[power_reason], None)
        elif (reset_reason == 66):
            return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER,
                    "Emulated Cold Reset")
        elif (reset_reason == 77):
            return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER,
                    "Emulated Warm Reset")
        else:
            return (ChassisBase.REBOOT_CAUSE_NON_HARDWARE, None)

        return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Invalid Reason")

    def _get_transceiver_presence(self):

        cpld2_modprs = self._get_register(
                    "/sys/class/i2c-adapter/i2c-14/14-003e/qsfp_modprs")
        cpld3_modprs = self._get_register(
                    "/sys/class/i2c-adapter/i2c-15/15-003e/qsfp_modprs")
        cpld4_modprs = self._get_register(
                    "/sys/class/i2c-adapter/i2c-16/16-003e/qsfp_modprs")
        cpld5_modprs = self._get_register(
                    "/sys/class/i2c-adapter/i2c-17/17-003e/qsfp_modprs")

        # If IOM is not present, register read will fail.
        # Handle the scenario gracefully
        if (cpld2_modprs == 'read error') or (cpld2_modprs == 'ERR'):
            cpld2_modprs = '0x0'
        if (cpld3_modprs == 'read error') or (cpld3_modprs == 'ERR'):
            cpld3_modprs = '0x0'
        if (cpld4_modprs == 'read error') or (cpld4_modprs == 'ERR'):
            cpld4_modprs = '0x0'
        if (cpld5_modprs == 'read error') or (cpld5_modprs == 'ERR'):
            cpld5_modprs = '0x0'

        # Make it contiguous
        transceiver_presence = (int(cpld2_modprs, 16) & 0xffff) |\
                               ((int(cpld4_modprs, 16) & 0xffff) << 16) |\
                               ((int(cpld3_modprs, 16) & 0xffff) << 32) |\
                               ((int(cpld5_modprs, 16) & 0xffff) << 48)

        return transceiver_presence

    def get_change_event(self, timeout=0):
        """
        Returns a nested dictionary containing all devices which have
        experienced a change at chassis level

        Args:
            timeout: Timeout in milliseconds (optional). If timeout == 0,
                this method will block until a change is detected.

        Returns:
            (bool, dict):
                - True if call successful, False if not;
                - A nested dictionary where key is a device type,
                  value is a dictionary with key:value pairs in the
                  format of {'device_id':'device_event'},
                  where device_id is the device ID for this device and
                        device_event,
                             status='1' represents device inserted,
                             status='0' represents device removed.
                  Ex. {'fan':{'0':'0', '2':'1'}, 'sfp':{'11':'0'}}
                      indicates that fan 0 has been removed, fan 2
                      has been inserted and sfp 11 has been removed.
        """
        port_dict = {}
        ret_dict = {'sfp': port_dict}
        forever = False

        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000) # Convert to secs
        else:
            return False, ret_dict # Incorrect timeout

        while True:
            if forever:
                timer = self.POLL_INTERVAL
            else:
                timer = min(timeout, self.POLL_INTERVAL)
                start_time = time.time()

            time.sleep(timer)
            cur_presence = self._get_transceiver_presence()

            # Update dict only if a change has been detected
            if cur_presence != self._transceiver_presence:
                changed_ports = self._transceiver_presence ^ cur_presence
                for port in range(self.get_num_sfps()):
                    # Mask off the bit corresponding to particular port
                    mask = 1 << port
                    if changed_ports & mask:
                        # qsfp_modprs 1 => optics is removed
                        if cur_presence & mask:
                            port_dict[port] = '0'
                        # qsfp_modprs 0 => optics is inserted
                        else:
                            port_dict[port] = '1'

                # Update current presence
                self._transceiver_presence = cur_presence
                break

            if not forever:
                elapsed_time = time.time() - start_time
                timeout = round(timeout - elapsed_time, 3)
                if timeout <= 0:
                    break

        return True, ret_dict
