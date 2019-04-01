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
    from sonic_platform_api.psu import Psu
    from sonic_platform_api.watchdog import get_watchdog
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

