#!/usr/bin/env python

#############################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides the platform information
#
#############################################################################

try:
    import os
    import time
    import datetime
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.sfp import Sfp
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Chassis(ChassisBase):
    """
    DELLEMC Platform-specific Chassis class
    """

    MAILBOX_DIR = "/sys/devices/platform/dell-s6000-cpld.0"

    sfp_control = ""
    PORT_START = 0
    PORT_END = 0
    reset_reason_dict = {}
    reset_reason_dict[0xe] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE
    reset_reason_dict[0x6] = ChassisBase.REBOOT_CAUSE_NON_HARDWARE

    def __init__(self):
        # Initialize SFP list
        self.PORT_START = 0
        self.PORT_END = 31
        EEPROM_OFFSET = 20
        PORTS_IN_BLOCK = (self.PORT_END + 1)

        # sfp.py will read eeprom contents and retrive the eeprom data.
        # It will also provide support sfp controls like reset and setting
        # low power mode.
        # We pass the eeprom path and sfp control path from chassis.py
        # So that sfp.py implementation can be generic to all platforms
        eeprom_base = "/sys/class/i2c-adapter/i2c-{0}/{0}-0050/eeprom"
        self.sfp_control = "/sys/devices/platform/dell-s6000-cpld.0/"

        for index in range(0, PORTS_IN_BLOCK):
            eeprom_path = eeprom_base.format(index + EEPROM_OFFSET)
            sfp_node = Sfp(index, 'QSFP', eeprom_path, self.sfp_control, index)
            self._sfp_list.append(sfp_node)

        # Get Transceiver status
        self.modprs_register = self._get_transceiver_status()

    def get_register(self, reg_name):
        rv = 'ERR'
        mb_reg_file = self.MAILBOX_DIR+'/'+reg_name

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

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        """
        reset_reason = int(self.get_register('last_reboot_reason'), base=16)

        # In S6000, We track the reboot reason by writing the reason in
        # NVRAM. Only Warmboot and Coldboot reason are supported here.

        if (reset_reason in self.reset_reason_dict):
            return (self.reset_reason_dict[reset_reason], None)

        return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Invalid Reason")

    def _get_transceiver_status(self):
        presence_ctrl = self.sfp_control + 'qsfp_modprs'
        try:
            reg_file = open(presence_ctrl)

        except IOError as e:
            return False

        content = reg_file.readline().rstrip()
        reg_file.close()

        return int(content, 16)

    def get_transceiver_change_event(self, timeout=0):
        """
        Returns a dictionary containing sfp changes which have
        experienced a change at chassis level
        """
        start_time = time.time()
        port_dict = {}
        port = self.PORT_START
        forever = False

        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000) # Convert to secs
        else:
            return False, {}
        end_time = start_time + timeout

        if (start_time > end_time):
            return False, {} # Time wrap or possibly incorrect timeout

        while (timeout >= 0):
            # Check for OIR events and return updated port_dict
            reg_value = self._get_transceiver_status()
            if (reg_value != self.modprs_register):
                changed_ports = (self.modprs_register ^ reg_value)
                while (port >= self.PORT_START and port <= self.PORT_END):
                    # Mask off the bit corresponding to our port
                    mask = (1 << port)
                    if (changed_ports & mask):
                        # ModPrsL is active low
                        if reg_value & mask == 0:
                            port_dict[port] = '1'
                        else:
                            port_dict[port] = '0'
                    port += 1

                # Update reg value
                self.modprs_register = reg_value
                return True, port_dict

            if forever:
                time.sleep(1)
            else:
                timeout = end_time - time.time()
                if timeout >= 1:
                    time.sleep(1) # We poll at 1 second granularity
                else:
                    if timeout > 0:
                        time.sleep(timeout)
                    return True, {}
        return False, {}

