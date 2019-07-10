#!/usr/bin/env python

########################################################################
# DellEMC
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Fans' information which are available in the platform
#
########################################################################


try:
    import os
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


MAX_S6100_PSU_FAN_SPEED = 18000
MAX_S6100_FAN_SPEED = 16000


class Fan(FanBase):
    """DellEMC Platform-specific FAN class"""

    HWMON_DIR = "/sys/devices/platform/SMF.512/hwmon/"
    HWMON_NODE = os.listdir(HWMON_DIR)[0]
    MAILBOX_DIR = HWMON_DIR + HWMON_NODE

    def __init__(self, fan_index, psu_fan=False):
        self.is_psu_fan = psu_fan
        if not self.is_psu_fan:
            # Fan is 1-based in DellEMC platforms
            self.index = fan_index + 1
            self.get_fan_speed_reg = "fan{}_input".format(2*self.index - 1)
            self.max_fan_speed = MAX_S6100_FAN_SPEED
        else:
            # PSU Fan index starts from 11
            self.index = fan_index + 10
            self.get_fan_speed_reg = "fan{}_input".format(self.index)
            self.max_fan_speed = MAX_S6100_PSU_FAN_SPEED

