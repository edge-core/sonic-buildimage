#!/usr/bin/env python

#############################################################################
# DELLEMC
#
# Module contains an implementation of SONiC Platform Base API and
# provides the platform information
#
#############################################################################

try:
    import os
    from sonic_platform_base.chassis_base import ChassisBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Chassis(ChassisBase):
    """
    DELLEMC Platform-specific Chassis class
    """

    HWMON_DIR = "/sys/devices/platform/SMF.512/hwmon/"
    HWMON_NODE = os.listdir(HWMON_DIR)[0]
    MAILBOX_DIR = HWMON_DIR + HWMON_NODE

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

    def _get_reboot_reason_smf_register(self):
        # Returns 0xAA on software reload
        # Returns 0xFF on power-cycle
        # Returns 0x01 on first-boot
        smf_mb_reg_reason = self._get_pmc_register('mb_poweron_reason')
        return int(smf_mb_reg_reason, 16)

    def _get_pmc_register(self, reg_name):
        rv = 'ERR'
        mb_reg_file = self.MAILBOX_DIR+'/'+reg_name

        if (not os.path.isfile(mb_reg_file)):
            print mb_reg_file,  'not found !'
            return rv

        try:
            with open(mb_reg_file, 'r') as fd:
                rv = fd.read()
        except Exception as error:
            logging.error("Unable to open ", mb_reg_file, "file !")

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        """
        reset_reason = int(self._get_pmc_register('smf_reset_reason'))
        power_reason = int(self._get_pmc_register('smf_poweron_reason'))
        smf_mb_reg_reason = self._get_reboot_reason_smf_register()

        if ((smf_mb_reg_reason == 0x01) and (power_reason == 0x11)):
            return (ChassisBase.REBOOT_CAUSE_NON_HARDWARE, None)

        # Reset_Reason = 11 ==> PowerLoss
        # So return the reboot reason from Last Power_Reason Dictionary
        # If Reset_Reason is not 11 return from Reset_Reason dictionary
        # Also check if power_reason, reset_reason are valid values by
        # checking key presence in dictionary else return
        # REBOOT_CAUSE_HARDWARE_OTHER as the Power_Reason and Reset_Reason
        # registers returned invalid data

        # In S6100, if Reset_Reason is not 11 and smf_mb_reg_reason
        # is ff or bb, then it is PowerLoss
        if (reset_reason == 11):
            if (power_reason in self.power_reason_dict):
                return (self.power_reason_dict[power_reason], None)
        else:
            if ((smf_mb_reg_reason == 0xbb) or (smf_mb_reg_reason == 0xff)):
                return (ChassisBase.REBOOT_CAUSE_POWER_LOSS, None)

            if (reset_reason in self.reset_reason_dict):
                return (self.reset_reason_dict[reset_reason], None)

        return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Invalid Reason")

