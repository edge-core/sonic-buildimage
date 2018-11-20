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
    from cStringIO import StringIO
    from sonic_eeprom import eeprom_base
    from sonic_eeprom import eeprom_tlvinfo
    import subprocess
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

class board(eeprom_tlvinfo.TlvInfoDecoder):

    _TLV_INFO_MAX_LEN = 256

    def __init__(self, name, path, cpld_root, ro):
        self.eeprom_path = "/bsp/eeprom/vpd_info"
        super(board, self).__init__(self.eeprom_path, 0, '', True)

    def decode_eeprom(self, e):
        original_stdout = sys.stdout
        sys.stdout = StringIO()
        eeprom_tlvinfo.TlvInfoDecoder.decode_eeprom(self, e)
        decode_output = sys.stdout.getvalue()
        sys.stdout = original_stdout
        print(decode_output.replace('\0', ''))
