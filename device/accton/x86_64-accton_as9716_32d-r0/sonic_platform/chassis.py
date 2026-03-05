#############################################################################
# Edgecore
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

import os
import sys
import logging
import time
import re

try:
    from sonic_platform_base.chassis_base import ChassisBase
    from .helper import APIHelper
    from .event import SfpEvent
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_FAN_TRAY = 6
NUM_FAN = 2
NUM_PSU = 2
NUM_THERMAL = 12
NUM_PORT = 32
PORT_START = 1
PORT_END = 32
QSFP_PORT_START = 1
QSFP_PORT_END = 32
NUM_COMPONENT = 7

# The platform path is different between the host (e.g., /usr/share/sonic/device/
# x86_64-accton_as9716_32d-r0/) and the pmon container (/usr/share/sonic/platform/).
# However, since the directory contents are identical, when the host updates
# /usr/share/sonic/device/x86_64-accton_as9716_32d-r0/platform_monitor_alarm, the
# pmon can retrieve the latest data from /usr/share/sonic/platform/platform_monitor_alarm.
HOST_PMONITOR_ALARM_FILE = "/usr/share/sonic/device/{}/platform_monitor_alarm"
PMON_PMONITOR_ALARM_FILE = "/usr/share/sonic/platform/platform_monitor_alarm"

HOST_REBOOT_CAUSE_PATH = "/host/reboot-cause/"
PMON_REBOOT_CAUSE_PATH = "/usr/share/sonic/platform/api_files/reboot-cause/"
REBOOT_CAUSE_FILE = "reboot-cause.txt"
PREV_REBOOT_CAUSE_FILE = "previous-reboot-cause.txt"
HOST_CHK_CMD = "which systemctl > /dev/null 2>&1"
SYSLED_FNODE = "/sys/class/leds/accton_as9716_32d_led::diag/brightness"
SYSLED_MODES = {
    "0" : "STATUS_LED_COLOR_OFF",
    "1" : "STATUS_LED_COLOR_GREEN",
    "2" : "STATUS_LED_COLOR_AMBER",
    "5" : "STATUS_LED_COLOR_GREEN_BLINK"
}

SFP_STATUS_INSERTED = '1'
I2C_MUX_RESET_PATH = "/sys/devices/platform/as9716_32d_ioport/i2c_mux_rst"

# Regex for PCI BDF
PCI_RE = re.compile(r"0000:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7]", re.I)

class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    # These constants are used in the get_all_optical_xcvr_down_state API
    # to represent the possible states of the transceivers and
    # the platform monitor state.
    PLATFORM_MONITOR_RED_ALARM = 4
    XCVR_DOWN_NOT_SUPPORTED = 0
    XCVR_DOWN_FALSE = 1
    XCVR_DOWN_TRUE = 2

    def __init__(self):
        ChassisBase.__init__(self)
        self._api_helper = APIHelper()
        self.is_host = self._api_helper.is_host()
        
        self.fan_dir = 1 # 1:AFI, 0:AFO
        self.config_data = {}

        self.__initialize_fan()
        self.__initialize_psu()
        self.__initialize_thermals()
        self.__initialize_components()
        self.__initialize_sfp()

        if os.getuid() != 0:
            return

        # Initialization of the syseeprom should only be performed with root privileges.
        try:
            self.__initialize_eeprom()
        except ImportError as e:
            raise ImportError(str(e) + "- required module not found")
        except IOError as e:
            raise IOError(str(e) + "- Failed to read eeprom")
        except Exception as e:
            print(str(e))
            raise e

        self.__initialize_watchdog()

    def __initialize_sfp(self):
        from sonic_platform.sfp import Sfp

        self.QSFP_PORT_START = QSFP_PORT_START
        self.QSFP_PORT_END = QSFP_PORT_END
        for index in range(0, PORT_END):
            if index in range(self.QSFP_PORT_START-1, self.QSFP_PORT_END):
                sfp_module = Sfp(index, 'QSFP')
            else:
                sfp_module = Sfp(index, 'SFP')
                
            self._sfp_list.append(sfp_module)

        self._sfpevent = SfpEvent(self._sfp_list)
        self.sfp_module_initialized = True

    def __initialize_fan(self):
        from sonic_platform.fan_drawer import FanDrawer
        for fant_index in range(NUM_FAN_TRAY):
            fandrawer = FanDrawer(fant_index)
            self._fan_drawer_list.append(fandrawer)
            self._fan_list.extend(fandrawer._fan_list)

        b2f_dir, f2b_dir = 0, 0
        for fan in self._fan_list:
            if fan.get_presence():
                direction = fan.get_direction()
                b2f_dir += direction == fan.FAN_DIRECTION_INTAKE
                f2b_dir += direction == fan.FAN_DIRECTION_EXHAUST
        self.fan_dir = b2f_dir >= f2b_dir # 1:AFI, 0:AFO


    def __initialize_psu(self):
        from sonic_platform.psu import Psu
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

    def __initialize_thermals(self):
        from sonic_platform.thermal import Thermal
        for index in range(0, NUM_THERMAL):
            thermal = Thermal(thermal_index=index, fan_dir=self.fan_dir)
            self._thermal_list.append(thermal)

    def __initialize_eeprom(self):
        from sonic_platform.eeprom import Tlv
        self._eeprom = Tlv()

    def __initialize_components(self):
        from sonic_platform.component import Component
        for index in range(0, NUM_COMPONENT):
            component = Component(index)
            self._component_list.append(component)

    def __initialize_watchdog(self):
        from sonic_platform.watchdog import Watchdog
        self._watchdog = Watchdog()
    

    def __is_host(self):
        return os.system(HOST_CHK_CMD) == 0

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return None

    def _get_i2c_master_list(self):
        """
        Retrieve all Intel SMBus controller BDFs (Bus:Device.Function) from the PCI bus.

        This method executes the `lspci -Dnn` command and scans its output
        to find Intel SMBus controllers. The BDF identifiers of all matching
        controllers are collected and returned.

        Returns:
            list[str]: A list of BDF strings corresponding to Intel SMBus
            controllers. Returns an empty list if no matching controllers are found.
        """
        cmd = ["lspci", "-Dnn"]
        result = self._api_helper.run_command_sync(cmd)
        output = result.stdout.strip()

        bdfs = []

        for line in output.splitlines():
            if "SMBus" in line and "Intel" in line:
                match = PCI_RE.search(line)
                if match:
                    bdfs.append(match.group(0))

        return bdfs

    def _reset_i2c_master_post(self):
        """
        Run post-reset cleanup and install commands for Intel I2C master.

        Executes a series of commands required after resetting the I2C master.
        Raises RuntimeError if any command fails.
        """
        reset_post_cmds = [
            "sudo accton_as9716_32d_util.py clean",
            "sudo accton_as9716_32d_util.py install"
        ]

        for cmd in reset_post_cmds:
            self._api_helper.run_command_sync(cmd, shell=True)

    def reset_i2c_master(self):
        """
        Reset all detected Intel SMBus controllers.

        Executes reset commands for each detected controller and runs
        post-reset cleanup/install commands to ensure proper I2C master state.

        Raises:
            RuntimeError: If any reset command fails.
        """
        reset_cmds = [
            "sudo setpci -s {bdf} 40.B=09:09",
            "sudo sh -c 'echo 1 > /sys/bus/pci/devices/{bdf}/remove'",
            "sudo sh -c 'echo 1 > /sys/bus/pci/rescan'"
        ]

        bdfs = self._get_i2c_master_list()

        if not bdfs:
            return


        exception = None
        for bdf in bdfs:
            for cmd in reset_cmds:
                formatted_cmd = cmd.format(bdf=bdf)
                try:
                    self._api_helper.run_command_sync(formatted_cmd, shell=True)
                except RuntimeError as e:
                    if exception is None:
                        exception = e

        # Execute post-reset once after all commands succeed
        self._reset_i2c_master_post()

        if exception:
            raise exception

    def get_all_i2c_list(self):
        """
        Combines I2C device lists from various components.

        Retrieves I2C device lists from multiple sources (Fan, PSU, SFP),
        and combines them into a single list.

        Returns:
            list: A combined list of all I2C devices.
        """
        i2c_list = []
        for obj in (self._psu_list + self._sfp_list):
            data = obj.get_i2c_list()
            if data is not None:
                i2c_list.extend(data)

        return i2c_list

    def get_all_i2c_region_list(self):
        """
        Groups all I2C devices by their region.

        Retrieves the list of all I2C devices, checks for the 'region' key in each device,
        and organizes them into a dictionary where the key is the region, and the value 
        is a list of devices in that region.

        Returns:
            dict: A dictionary mapping regions to their respective list of devices.
        """
        i2c_list = self.get_all_i2c_list()

        regions = {}
        for device in i2c_list:
            region = device.get('region', None)
            if region is not None:
                if region not in regions:
                    regions[region] = []
                del device['region']
                regions[region].append(device)

        return regions

    def reset_i2c_mux(self):
        """
        Toggles the I2C MUX reset signal by writing 1 and then 0 to the reset path.

        Returns:
            bool: True if successful, otherwise the error result from the write operation.
        """
        ret = self._api_helper.write_txt_file(I2C_MUX_RESET_PATH, 1)
        if ret is not True:
            return ret

        time.sleep(0.2)
        ret = self._api_helper.write_txt_file(I2C_MUX_RESET_PATH, 0)
        time.sleep(0.2)

        return ret

    def representative_devices_get(self):
        exists = os.path.isfile("/sys/bus/i2c/devices/0-0056/eeprom")
        if (exists is True):
            eeprom_addr = "0x56"
        else:
            eeprom_addr = "0x57"

        candidate_list = [
            {'name': 'PCA9548(0x77)', 'bus': '0', 'device_addr': '0x77', 'register_addr': '0x0'},
            {'name': 'CPLD4', 'bus': '0', 'device_addr': '0x65', 'register_addr': '0x0'},
            {'name': 'EEPROM', 'bus': '0', 'device_addr': eeprom_addr, 'register_addr': '0x0'}
        ]

        return candidate_list

    def get_platform_service_list(self):
        platform_service_list = [
            'as9716-32d-platform-monitor-fan.service',
            'as9716-32d-platform-monitor-psu.service',
            'as9716-32d-platform-monitor.service'
        ]

        return platform_service_list

    def set_all_fan_full_speed(self):
        for fan in self._fan_list:
            fan.set_speed(100)

        return True

    def set_i2c_faulty_device(self, bus, addr, faulty):
        """
        Sets the faulty state for a device on the specified I2C bus and address.

        Args:
            bus (str): The I2C bus number.
            addr (str): The I2C device address.
            faulty (bool): True to mark the device as faulty, False otherwise.

        Returns:
            bool: True if the faulty state was set successfully, False otherwise.
        """
        ret = False
        data_list = self.get_all_i2c_list()

        entry = next(
            (e for e in data_list if e['bus'] == bus and e['device_addr'] == addr), 
            None
        )
        if entry is None:
            return ret

        for obj in (self._psu_list + self._sfp_list):
            if obj.get_name() == entry['name']:
                ret = obj.set_faulty_device(faulty)
                break

        return ret

    def get_all_optical_xcvr_down_state(self):
        """
        Retrieve the down state of all optical transceivers.

        This function reads the platform monitor alarm file to determine the
        down state of all optical transceivers. The return value indicates
        the state of the transceivers:

        - 0: Not Support (The hardware model's thermal policy does not define 'all optical xcvr down state')
        - 1: False ('all optical xcvr down state' is not asserted)
        - 2: True ('all optical xcvr down state' is asserted)

        Returns:
            int: Status of the optical transceiver down state.
        """
        platform_monitor_alarm_path = PMON_PMONITOR_ALARM_FILE

        if self.is_host:
            platform = self._api_helper.get_platform()
            if platform is None:
                raise RuntimeError("Unable to retrieve onie_platform from /host/machine.conf")
            platform_monitor_alarm_path = HOST_PMONITOR_ALARM_FILE.format(platform)

        val = self._api_helper.read_txt_file(platform_monitor_alarm_path)
        if val is not None:
            try:
                if int(val, 10) == self.PLATFORM_MONITOR_RED_ALARM:
                    return self.XCVR_DOWN_TRUE
                return self.XCVR_DOWN_FALSE
            except ValueError as e:
                raise ValueError(f"Error converting value from {platform_monitor_alarm_path}: {e}")

        return self.XCVR_DOWN_NOT_SUPPORTED

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        
        return self._eeprom.get_modelstr()

    def get_presence(self):
        """
        Retrieves the presence of the Chassis
        Returns:
            bool: True if Chassis is present, False if not
        """
        return True
    
    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return True
    
    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.get_mac()

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self._eeprom.get_pn()
        
    def get_serial(self):
        """
        Retrieves the hardware serial number for the chassis
        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self._eeprom.get_serial()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.get_eeprom()

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

        reboot_cause_path = (HOST_REBOOT_CAUSE_PATH + REBOOT_CAUSE_FILE)
        sw_reboot_cause = self._api_helper.read_txt_file(
            reboot_cause_path) or "Unknown"


        return ('REBOOT_CAUSE_NON_HARDWARE', sw_reboot_cause)

    def get_change_event(self, timeout=0):
        # SFP event
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        status, sfp_event = self._sfpevent.get_sfp_event(timeout)

        return status, sfp_event

    def get_sfp(self, index):
        """
        Retrieves sfp represented by (1-based) index <index>
        Args:
            index: An integer, the index (1-based) of the sfp to retrieve.
            The index should be the sequence of a physical port in a chassis,
            starting from 1.
            For example, 1 for Ethernet0, 2 for Ethernet4 and so on.
        Returns:
            An object dervied from SfpBase representing the specified sfp
        """
        sfp = None
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        try:
            # The index will start from 1
            sfp = self._sfp_list[index-1]
        except IndexError:
            sys.stderr.write("SFP index {} out of range (1-{})\n".format(
                             index, len(self._sfp_list)))
        return sfp

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device. If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of entPhysicalContainedIn is '0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device or -1 if cannot determine the position
        """
        return -1

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False

        
    def initizalize_system_led(self):
        return True

    def get_status_led(self):
        val = self._api_helper.read_txt_file(SYSLED_FNODE)
        return SYSLED_MODES[val] if val in SYSLED_MODES else "UNKNOWN"

    def set_status_led(self, color):
        mode = None
        for key, val in SYSLED_MODES.items():
            if val == color:
                mode = key
                break
        if mode is None:
            return False
        else:
            return self._api_helper.write_txt_file(SYSLED_FNODE, mode)

    def get_revision(self):
        """
        Retrieves the hardware revision of the device

        Returns:
            string: Revision value of device
        """
        return self._eeprom.get_revisionstr()
