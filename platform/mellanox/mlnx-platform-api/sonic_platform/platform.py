#!/usr/bin/env python

#############################################################################
# Mellanox
#
# implementation of new platform api
#############################################################################

try:
    from sonic_platform_base.platform_base import PlatformBase
    from sonic_platform.chassis import Chassis
    from . import utils
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

class Platform(PlatformBase):
    def __init__(self):
        PlatformBase.__init__(self)
        self._chassis = Chassis()
        self._chassis.initialize_psu()
        self._chassis.initialize_eeprom()
        if utils.is_host():
            self._chassis.initialize_components()
            self._chassis.initizalize_system_led()
        else:
            self._chassis.initialize_fan()
            self._chassis.initialize_thermals()
