#!/usr/bin/env python

import os.path
import subprocess
try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
       PsuBase.__init__(self)
       MAX_PSUS = 2

    def get_num_psus(self):
        MAX_PSUS = 2
        return MAX_PSUS

    def get_psu_status(self, index):
        if index is None:
           return False

        cmdstatus, psustatus = subprocess.getstatusoutput('i2cget -y 0 0x41 0xa') #need to verify the cpld register logic
        psustatus = int(psustatus, 16)
        if cmdstatus == 0:
            if index == 1:
                psustatus = psustatus&4
                if psustatus == 4 :
                    return True
            if index == 2:
                psustatus = psustatus&8
                if psustatus == 8 :
                    return True
        return False

    def get_psu_presence(self, index):
        if index is None:
            return False

        cmdstatus , psustatus = subprocess.getstatusoutput('i2cget -y 0 0x41 0xa') #need to verify the cpld register logic
        psustatus = int(psustatus, 16)
        if cmdstatus == 0:
            if index == 1:
                 psustatus = psustatus&1
                 if psustatus == 1 :
                     return True
            if index == 2:
                psustatus = psustatus&2
                if psustatus == 2 :
                    return True
        return False

