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
    from sonic_platform.psu import Psu
    from sonic_platform.fan import Fan
    from sonic_platform.fan import FAN_PATH
    from sonic_platform.sfp import SFP
    from sonic_platform.watchdog import get_watchdog
    from os import listdir
    from os.path import isfile, join
    import re
    import subprocess
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

MLNX_NUM_PSU = 2

GET_HWSKU_CMD = "sonic-cfggen -d -v DEVICE_METADATA.localhost.hwsku"

# magic code defnition for port number, qsfp port position of each hwsku
# port_position_tuple = (PORT_START, QSFP_PORT_START, PORT_END, PORT_IN_BLOCK, EEPROM_OFFSET)
hwsku_dict = {'ACS-MSN2700': 0, "LS-SN2700":0, 'ACS-MSN2740': 0, 'ACS-MSN2100': 1, 'ACS-MSN2410': 2, 'ACS-MSN2010': 3, 'ACS-MSN3700': 0, 'ACS-MSN3700C': 0, 'Mellanox-SN2700': 0, 'Mellanox-SN2700-D48C8': 0}
port_position_tuple_list = [(0, 0, 31, 32, 1), (0, 0, 15, 16, 1), (0, 48, 55, 56, 1),(0, 18, 21, 22, 1)]

class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        ChassisBase.__init__(self)

        # Initialize PSU list
        for index in range(MLNX_NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

        # Initialize watchdog
        self._watchdog = get_watchdog()
        
        # Initialize FAN list
        multi_rotor_in_drawer = False
        num_of_fan, num_of_drawer = self._extract_num_of_fans_and_fan_drawers()
        multi_rotor_in_drawer = num_of_fan > num_of_drawer

        for index in range(num_of_fan):
            if multi_rotor_in_drawer:
                fan = Fan(index, index/2)
            else:
                fan = Fan(index, index)
            self._fan_list.append(fan)

        # Initialize SFP list
        port_position_tuple = self._get_port_position_tuple_by_sku_name()
        self.PORT_START = port_position_tuple[0]
        self.QSFP_PORT_START = port_position_tuple[1]
        self.PORT_END = port_position_tuple[2]
        self.PORTS_IN_BLOCK = port_position_tuple[3]
        
        for index in range(self.PORT_START, self.PORT_END + 1):
            if index in range(QSFP_PORT_START, self.PORTS_IN_BLOCK + 1):
                sfp_module = SFP(index, 'QSFP')
            else:
                sfp_module = SFP(index, 'SFP')
            self._sfp_list.append(sfp_module)

    def _extract_num_of_fans_and_fan_drawers(self):
        num_of_fan = 0
        num_of_drawer = 0
        for f in listdir(FAN_PATH):
            if isfile(join(FAN_PATH, f)):
                match_obj = re.match('fan(\d+)_speed_get', f)
                if match_obj != None:
                    if int(match_obj.group(1)) > num_of_fan:
                        num_of_fan = int(match_obj.group(1))
                else:
                    match_obj = re.match('fan(\d+)_status', f)
                    if match_obj != None and int(match_obj.group(1)) > num_of_drawer:
                        num_of_drawer = int(match_obj.group(1))

        return num_of_fan, num_of_drawer

    def _get_port_position_tuple_by_sku_name(self):
        p = subprocess.Popen(GET_HWSKU_CMD, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        position_tuple = port_position_tuple_list[hwsku_dict[out.rstrip('\n')]]
        return position_tuple

    

