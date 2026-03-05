#############################################################################
# Edgecore
#
# Component contains an implementation of SONiC Platform Base API and
# provides the components firmware management function
#
#############################################################################

import subprocess
import os
import json
import time
import re

try:
    from sonic_platform_base.component_base import ComponentBase
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

CPLD_ADDR_MAPPING = {
    "FPGA":  "19-0060",
    "CPLD1": "20-0061",
    "CPLD2": "21-0062",
    "CPLD3": "17-0066",
    "CPLD4": "0-0065"
}
SYSFS_PATH = "/sys/bus/i2c/devices/"
BIOS_VERSION_PATH = "/sys/class/dmi/id/bios_version"
SSD_VERSION_COMMAND = ["/usr/local/bin/ssdutil", "-v"]
COMPONENT_LIST= [
   ("FPGA", "FPGA "),
   ("CPLD1", "CPLD 1"),
   ("CPLD2", "CPLD 2"),
   ("CPLD3", "CPLD FAN"),
   ("CPLD4", "CPLD CPU"),
   ("BIOS", "Basic Input/Output System"),
   ("SSD", "Solid State Drive")
]

class Component(ComponentBase):
    """Platform-specific Component class"""

    DEVICE_TYPE = "component"

    def __init__(self, component_index=0):
        self._api_helper=APIHelper()
        ComponentBase.__init__(self)
        self.index = component_index
        self.name = self.get_name()

    def __run_command(self, command, timeout=None):
        """
        Run shell command with shell=False
        Args:
            command(list of strings): Shell command string in list format.
            timeout(float): The period in seconds after which to timeout.
        Returns:
            A tuple(status, output). Return(exitcode, output) of executing command.
        """
        try:
            output = subprocess.check_output(command, universal_newlines=True,
                    timeout=timeout, stderr=subprocess.STDOUT)
            status = 0
        except subprocess.CalledProcessError as ex:
            output = ex.output
            status = ex.returncode
        except Exception as ex:
            output = "{}".format(ex)
            status = -1

        if output[-1:] == '\n':
            output = output[:-1]

        return status, output

    def __get_bios_version(self):
        # Retrieves the BIOS firmware version
        try:
            with open(BIOS_VERSION_PATH, 'r') as fd:
                bios_version = fd.read()
                return bios_version.strip()
        except Exception as e:
            return None

    def __get_cpld_version(self):
        # Retrieves the CPLD firmware version
        cpld_version = dict()
        for cpld_name in CPLD_ADDR_MAPPING:
            try:
                cpld_path = "{}{}{}".format(SYSFS_PATH, CPLD_ADDR_MAPPING[cpld_name], '/version')
                cpld_version_raw= self._api_helper.read_txt_file(cpld_path)
                str= hex(int(cpld_version_raw,10))
                cpld_version[cpld_name] = "{}".format(str[2:])
            except Exception as e:
                print('Get exception when read cpld')
                cpld_version[cpld_name] = 'None'

        return cpld_version

    def __get_ssd_version(self):
        status, ssd_info = self.__run_command(SSD_VERSION_COMMAND)
        if status == 0:
            res_list = re.findall("Firmware     :\s*(.+?)\n", ssd_info)
            ssd_version = res_list[0] if len(res_list) > 0 else 'None'
        else:
            ssd_version = 'None'

        return ssd_version

    def get_name(self):
        """
        Retrieves the name of the component
         Returns:
            A string containing the name of the component
        """
        return COMPONENT_LIST[self.index][0]

    def get_description(self):
        """
        Retrieves the description of the component
            Returns:
            A string containing the description of the component
        """
        return COMPONENT_LIST[self.index][1]

    def get_firmware_version(self):
        """
        Retrieves the firmware version of module
        Returns:
            string: The firmware versions of the module
        """
        fw_version = None

        if self.name == "BIOS":
            fw_version = self.__get_bios_version()
        elif "CPLD" in self.name or "FPGA" in self.name:
            cpld_version = self.__get_cpld_version()
            fw_version = cpld_version.get(self.name)
        elif self.name == "SSD":
            fw_version = self.__get_ssd_version()

        return fw_version

    def install_firmware(self, image_path):
        """
        Install firmware to module
        Args:
            image_path: A string, path to firmware image
        Returns:
            A boolean, True if install successfully, False if not
        """
        ret = subprocess.call(["tar", "-C", "/tmp", "-xzf", image_path ] )
        if ret != 0 :
            print("Installation failed because of wrong image package")
            return False

        if  False == os.path.exists("/tmp/install.json") :
            print("Installation failed without jsonfile")
            return False

        ret=1
        input_file = open ('/tmp/install.json')
        json_array = json.load(input_file)
        for item in json_array:
            if item.get('id') == None or item.get('path') == None :
                continue
            if self.name == item['id'] and item['path'] and item.get('cpu'):
                print( "Find", item['id'], item['path'], item['cpu'] )
                ret = subprocess.call(["/tmp/run_install.sh", item['id'], item['path'], item['cpu'] ])
                if ret==0:
                    break
            elif self.name == item['id'] and item['path']:
                print( "Find", item['id'], item['path'] )
                ret = subprocess.call(["/tmp/run_install.sh", item['id'], item['path'] ])
                if ret==0:
                    break

        if ret==0:
            return True
        else :
            return False

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
        return 'N/A'

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return 'N/A'

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return True

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of
        entPhysicalContainedIn is'0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device
            or -1 if cannot determine the position
        """
        return -1

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False
