#!/usr/bin/env python

#############################################################################
# Dell S6000
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
    import subprocess
    from sonic_eeprom import eeprom_base
    from sonic_eeprom import eeprom_tlvinfo
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


class board(eeprom_tlvinfo.TlvInfoDecoder):
    _TLV_INFO_MAX_LEN = 128
    _TLV_HDR_ENABLED = 0

    _TLV_BLOCK_NUMBER = 3
    _TLV_BLOCK_HDR_STRING = "\x3a\x29"

    _TLV_CODE_MFG = 0x20
    _TLV_CODE_SW  = 0x1f
    _TLV_CODE_MAC = 0x21

    def __init__(self, name, path, cpld_root, ro):
        self.eeprom_path = "/sys/class/i2c-adapter/i2c-10/10-0053/eeprom"
        super(board, self).__init__(self.eeprom_path, 0, '', True)

    def decode_eeprom(self, e):
        tlv_block_index = 0
        tlv_index = self.eeprom_start
        tlv_end = self._TLV_INFO_MAX_LEN

        print "TLV Name             Len Value"
        print "-------------------- --- -----"
        while tlv_block_index < self._TLV_BLOCK_NUMBER:
            if not self.is_valid_block(e[tlv_index:]):
                print "Invalid TLV field starting at EEPROM offset %d" % (tlv_index,)
                return
            print self.decoder(None, e[tlv_index:tlv_index + ord(e[tlv_index+2])])
            if not self.is_valid_block_checksum(e[tlv_index:tlv_index + ord(e[tlv_index+2])]):
                print "(*** checksum invalid)"
            tlv_index += ord(e[tlv_index+2])
            tlv_block_index += 1

    def is_valid_block(self, e):
        return (len(e) >= 8 and ord(e[2]) <= len(e) and \
               e[0:2] == self._TLV_BLOCK_HDR_STRING)

    def is_valid_block_checksum(self, e):
        crc = self.compute_dell_crc(e[:-2])
        tlv_crc = ord(e[-1]) << 8 | ord(e[-2])
        return crc == tlv_crc

    def decoder(self, s, t):
        ret = ""
        if ord(t[4]) == self._TLV_CODE_MFG:
            name = "PPID"
            value = t[6:8] + "-" + t[8:14] + "-" + t[14:19] + "-" + \
                    t[19:22] + "-" + t[22:26]
            ret += "%-20s %3d %s\n" % (name, 20, value)
            name = "DPN Rev"
            ret += "%-20s %3d %s\n" % (name, 3, t[26:29])
            name = "Service Tag"
            ret += "%-20s %3d %s\n" % (name, 7, t[29:36])
            name = "Part Number"
            ret += "%-20s %3d %s\n" % (name, 10, t[36:46])
            name = "Part Number Rev"
            ret += "%-20s %3d %s\n" % (name, 3, t[46:49])
            name = "Mfg Test Results"
            ret += "%-20s %3d %s" % (name, 2, t[49:51])
        if ord(t[4]) == self._TLV_CODE_SW:
            name = "Card ID"
            ret += "%-20s %3d 0x%s\n" % (name, 2, t[6:8].encode('hex'))
            name = "Module ID"
            ret += "%-20s %3d %s" % (name, 2, ord(t[8:9]))
        if ord(t[4]) == self._TLV_CODE_MAC:
            name = "Base MAC Address"
            value = ":".join([binascii.b2a_hex(T) for T in t[6:12]]).upper()
            ret += "%-20s %3d %s" % (name, 12, value)
        return ret

    def is_checksum_valid(self, e):
        # Checksum is already calculated before
        return (True, 0)

    def get_tlv_index(self, e, code):
        tlv_index = 0
        while tlv_index < len(e):
            if not self.is_valid_block(e[tlv_index:]):
                return (False, 0)
            if ord(e[tlv_index+4]) == code:
                if not self.is_valid_block_checksum(e[tlv_index:tlv_index + ord(e[tlv_index+2])]):
                    print "(*** checksum invalid)"
                return (True, tlv_index)
            tlv_index += ord(e[tlv_index+2])
        return (Flase, 0)

    def base_mac_addr(self, e):
        (is_valid, t) = self.get_tlv_index(e, self._TLV_CODE_MAC)
        if not is_valid:
            return "Bad base MAC address"
        return ":".join([binascii.b2a_hex(T) for T in e[t:][6:12]]).upper()

    def serial_number_str(self, e):
        ''' Return Service Tag '''
        (is_valid, t) = self.get_tlv_index(e, self._TLV_CODE_MFG)
        if not is_valid:
            return "Bad service tag"
        t = e[t:]
        return t[29:36]
