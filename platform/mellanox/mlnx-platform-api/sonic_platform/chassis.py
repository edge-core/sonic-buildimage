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
    from sonic_platform.watchdog import get_watchdog
    from os import listdir
    from os.path import isfile, join
    import re
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

MLNX_NUM_PSU = 2

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

    

