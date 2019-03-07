#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Platform and model specific eeprom subclass, inherits from the base class,
# and provides the followings:
# - the eeprom format definition
# - specific encoder/decoder if there is special need
#############################################################################

try:
    import exceptions
    import binascii
    import time
    import optparse
    import warnings
    import os
    import sys
    import syslog
    from cStringIO import StringIO
    from sonic_eeprom import eeprom_base
    from sonic_eeprom import eeprom_tlvinfo
    import subprocess
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

SYSLOG_IDENTIFIER = "eeprom.py"
EEPROM_SYMLINK = "/var/run/hw-management/eeprom/vpd_info"
CACHE_FILE = "/var/cache/sonic/decode-syseeprom/syseeprom_cache"

def log_error(msg):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_ERR, msg)
    syslog.closelog()

class board(eeprom_tlvinfo.TlvInfoDecoder):

    _TLV_INFO_MAX_LEN = 256
    RETRIES = 5

    def __init__(self, name, path, cpld_root, ro):
        for attempt in range(self.RETRIES):
            if not os.path.islink(EEPROM_SYMLINK):
                time.sleep(1)
            else:
                break  
                      
        if not (os.path.exists(EEPROM_SYMLINK) or os.path.isfile(CACHE_FILE)):
            log_error("Nowhere to read syseeprom from! No symlink or cache file found")
            raise RuntimeError("No syseeprom symlink or cache file found")

        self.eeprom_path = EEPROM_SYMLINK
        super(board, self).__init__(self.eeprom_path, 0, '', True)

    def decode_eeprom(self, e):
        original_stdout = sys.stdout
        sys.stdout = StringIO()
        eeprom_tlvinfo.TlvInfoDecoder.decode_eeprom(self, e)
        decode_output = sys.stdout.getvalue()
        sys.stdout = original_stdout
        print(decode_output.replace('\0', ''))
