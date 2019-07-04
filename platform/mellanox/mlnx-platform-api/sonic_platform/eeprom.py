#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the eeprom information which are available in the platform
#
#############################################################################
import exceptions
import os
import sys
import re
from cStringIO import StringIO

try:
    from sonic_platform_base.sonic_eeprom import eeprom_tlvinfo
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

#
# CACHE_XXX stuffs are supposted to be moved to the base classes
# since they are common for all vendors
# they are defined in decode-syseeprom which might be removed in the future
# currently we just copy them here
#
CACHE_ROOT = '/var/cache/sonic/decode-syseeprom'
CACHE_FILE = 'syseeprom_cache'

#
# this is mlnx-specific
# should this be moved to chass.py or here, which better?
#
EEPROM_SYMLINK = "/var/run/hw-management/eeprom/vpd_info"

class Eeprom(eeprom_tlvinfo.TlvInfoDecoder):
    RETRIES = 3
    EEPROM_DECODE_HEADLINES = 6
    EEPROM_DECODE_MAXITEM = 3
    EEPROM_DECODE_OFFSET = 0
    EEPROM_DECODE_CONTENT = 2

    def __init__(self):
        for attempt in range(self.RETRIES):
            if not os.path.islink(EEPROM_SYMLINK):
                time.sleep(1)
            else:
                break  

        if not (os.path.exists(EEPROM_SYMLINK) \
                or os.path.isfile(os.path.join(CACHE_ROOT, CACHE_FILE))):
            log_error("Nowhere to read syseeprom from! No symlink or cache file found")
            raise RuntimeError("No syseeprom symlink or cache file found")

        self.eeprom_path = EEPROM_SYMLINK
        super(Eeprom, self).__init__(self.eeprom_path, 0, '', True)
        self._eeprom_loaded = False
        self._load_eeprom()
        self._eeprom_loaded = True

    def _load_eeprom(self):
        if not os.path.exists(CACHE_ROOT):
            try:
                os.makedirs(CACHE_ROOT)
            except:
                pass

        try:
            self.set_cache_name(os.path.join(CACHE_ROOT, CACHE_FILE))
        except:
            pass

        eeprom = self.read_eeprom()
        if eeprom is None :
            return 0

        try:
            self.update_cache(eeprom)
        except:
            pass

        self._base_mac = self.mgmtaddrstr(eeprom)
        if self._base_mac == None:
            self._base_mac = "Undefined."

        self._serial_str = self.serial_number_str(eeprom)
        if self._serial_str == None:
            self._serial_str = "Undefined."

        original_stdout = sys.stdout
        sys.stdout = StringIO()
        self.decode_eeprom(eeprom)
        decode_output = sys.stdout.getvalue()
        sys.stdout = original_stdout

        #parse decode_output into a dictionary
        decode_output.replace('\0', '')
        lines = decode_output.split('\n')
        lines = lines[self.EEPROM_DECODE_HEADLINES:]
        self._eeprom_info_dict = dict()

        for line in lines:
            try:
                match = re.search('(0x[0-9a-fA-F]{2})([\s]+[\S]+[\s]+)([\S]+)', line)
                if match is not None:
                    idx = match.group(1)
                    value = match.group(3).rstrip('\0')

                self._eeprom_info_dict[idx] = value
            except:
                pass

        return 0

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis

        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        if not self._eeprom_loaded:
            self._load_eeprom()
        return self._base_mac

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis

        Returns:
            A string containing the hardware serial number for this chassis.
        """
        if not self._eeprom_loaded:
            self._load_eeprom()
        return self._serial_str

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis

        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        if not self._eeprom_loaded:
            self._load_eeprom()
        return self._eeprom_info_dict
