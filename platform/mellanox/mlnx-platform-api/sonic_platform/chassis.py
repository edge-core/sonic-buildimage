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
    from os.path import join
    import io
    import re
    import subprocess
    import syslog
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

HWMGMT_SYSTEM_ROOT = '/var/run/hw-management/system/'

#reboot cause related definitions
REBOOT_CAUSE_ROOT = HWMGMT_SYSTEM_ROOT

REBOOT_CAUSE_POWER_LOSS_FILE = 'reset_main_pwr_fail'
REBOOT_CAUSE_AUX_POWER_LOSS_FILE = 'reset_aux_pwr_or_ref'
REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC_FILE = 'reset_asic_thermal'
REBOOT_CAUSE_WATCHDOG_FILE = 'reset_hotswap_or_wd'
REBOOT_CAUSE_MLNX_FIRMWARE_RESET = 'reset_fw_reset'
REBOOT_CAUSE_LONG_PB = 'reset_long_pb'
REBOOT_CAUSE_SHORT_PB = 'reset_short_pb'

REBOOT_CAUSE_FILE_LENGTH = 1

# ========================== Syslog wrappers ==========================
SYSLOG_IDENTIFIER = "mlnx-chassis"
def log_warning(msg, also_print_to_console=False):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_WARNING, msg)
    syslog.closelog()


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        super(Chassis, self).__init__()

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
        except Exception as e:
            log_warning("Fail to read file {} due to {}".format(filename, repr(e)))
            return ''

    def _verify_reboot_cause(self, filename):
        '''
        Open and read the reboot cause file in 
        /var/run/hwmanagement/system (which is defined as REBOOT_CAUSE_ROOT)
        If a reboot cause file doesn't exists, returns '0'.
        '''
        try:
            return bool(int(self._read_generic_file(join(REBOOT_CAUSE_ROOT, filename), REBOOT_CAUSE_FILE_LENGTH).rstrip('\n')))
        except:
            return False

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
        elif self._verify_reboot_cause(REBOOT_CAUSE_AUX_POWER_LOSS_FILE):
            major_cause = self.REBOOT_CAUSE_POWER_LOSS
        elif self._verify_reboot_cause(REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC_FILE):
            major_cause = self.REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC
        elif self._verify_reboot_cause(REBOOT_CAUSE_WATCHDOG_FILE):
            major_cause = self.REBOOT_CAUSE_WATCHDOG
        else:
            major_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            if self._verify_reboot_cause(REBOOT_CAUSE_MLNX_FIRMWARE_RESET):
                minor_cause = "Reset by ASIC firmware"
            elif self._verify_reboot_cause(REBOOT_CAUSE_LONG_PB):
                minor_cause = "Reset by long press on power button"
            elif self._verify_reboot_cause(REBOOT_CAUSE_SHORT_PB):
                minor_cause = "Reset by short press on power button"
            else:
                major_cause = self.REBOOT_CAUSE_NON_HARDWARE

        return major_cause, minor_cause

