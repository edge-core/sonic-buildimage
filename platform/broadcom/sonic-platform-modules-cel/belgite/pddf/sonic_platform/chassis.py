#############################################################################
# PDDF
# Module contains an implementation of SONiC Chassis API
#
#############################################################################
import os

try:
    from sonic_platform_pddf_base.pddf_chassis import PddfChassis
    from sonic_platform_pddf_base.pddf_eeprom import PddfEeprom
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform.fan_drawer import FanDrawer
    from sonic_platform.watchdog import Watchdog
    import sys
    import subprocess
    from sonic_py_common import device_info
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_COMPONENT = 3
FAN_DIRECTION_FILE_PATH = "/var/fan_direction"

class Chassis(PddfChassis):
    """
    PDDF Platform-specific Chassis class
    """

    def __init__(self, pddf_data=None, pddf_plugin_data=None):

        PddfChassis.__init__(self, pddf_data, pddf_plugin_data)
        vendor_ext = self._eeprom.vendor_ext_str()
        with open(FAN_DIRECTION_FILE_PATH, "w+") as f:
            f.write(vendor_ext)
        (self.platform, self.hwsku) = device_info.get_platform_and_hwsku()

        self.__initialize_components()

    def __initialize_components(self):
        from sonic_platform.component import Component
        for index in range(0, NUM_COMPONENT):
            component = Component(index)
            self._component_list.append(component)

    # Provide the functions/variables below for which implementation is to be overwritten

    def initizalize_system_led(self):
        return True

    def get_sfp(self, index):
        """
        Retrieves sfp represented by (1-based) index <index>
        For Quanta the index in sfputil.py starts from 1, so override
        Args:
            index: An integer, the index (1-based) of the sfp to retrieve.
            The index should be the sequence of a physical port in a chassis,
            starting from 1.
        Returns:
            An object dervied from SfpBase representing the specified sfp
        """
        sfp = None

        try:
            if index == 0:
                raise IndexError
            sfp = self._sfp_list[index - 1]
        except IndexError:
            sys.stderr.write("override: SFP index {} out of range (1-{})\n".format(
                index, len(self._sfp_list)))

        return sfp

    def get_watchdog(self):
        """
        Retreives hardware watchdog device on this chassis
        Returns:
            An object derived from WatchdogBase representing the hardware
            watchdog device
        """
        if self._watchdog is None:
            self._watchdog = Watchdog()

        return self._watchdog

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
        hw_reboot_cause = ""
        with open("/sys/devices/platform/cpld_wdt/reason", "r") as f:
            hw_reboot_cause = f.read().strip()

        if hw_reboot_cause == "0x77":
            reboot_cause = self.REBOOT_CAUSE_WATCHDOG
            description = 'Hardware Watchdog Reset'
        elif hw_reboot_cause == "0x66":
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'GPIO Request Warm Reset'
        elif hw_reboot_cause == "0x55":
            reboot_cause = self.REBOOT_CAUSE_HARDWARE_OTHER
            description = 'CPU Cold Reset'
        elif hw_reboot_cause == "0x44":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = 'CPU Warm Reset'
        elif hw_reboot_cause == "0x33":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = 'Soft-Set Cold Reset'
        elif hw_reboot_cause == "0x22":
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = 'Soft-Set Warm Reset'
        elif hw_reboot_cause == "0x11":
            reboot_cause = self.REBOOT_CAUSE_POWER_LOSS
            description = 'Power Loss'			
        else:
            reboot_cause = self.REBOOT_CAUSE_NON_HARDWARE
            description = 'Unkown Reason'

        return (reboot_cause, description)	
		
    def get_serial(self):
        return self._eeprom.serial_number_str()
		
    def get_revision(self):
        return self._eeprom.revision_str()
		
    @staticmethod
    def get_position_in_parent():
        return -1
		
    @staticmethod
    def is_replaceable():
        return True
		
    def get_base_mac(self):
        return self._eeprom.base_mac_addr()
		
    def get_system_eeprom_info(self):
        return self._eeprom.system_eeprom_info()

    def get_name(self):
        return self.modelstr()

    def get_model(self):
        return self._eeprom.part_number_str()

    def set_status_led(self, color):
        color_dict = {
            'green': "STATUS_LED_COLOR_GREEN",
            'red': "STATUS_LED_COLOR_AMBER",
            'amber': "STATUS_LED_COLOR_AMBER",
            'off': "STATUS_LED_COLOR_OFF"
        }
        return self.set_system_led("SYS_LED", color_dict.get(color, "off"))

    def get_status_led(self):
        return self.get_system_led("SYS_LED")
        
