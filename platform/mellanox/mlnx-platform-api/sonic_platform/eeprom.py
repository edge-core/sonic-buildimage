#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the eeprom information which are available in the platform
#
#############################################################################
import os
import time

from sonic_py_common.logger import Logger

try:
    from sonic_platform_base.sonic_eeprom import eeprom_tlvinfo
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

from .utils import default_return

logger = Logger()

#
# this is mlnx-specific
# should this be moved to chass.py or here, which better?
#
EEPROM_SYMLINK = "/var/run/hw-management/eeprom/vpd_info"

class Eeprom(eeprom_tlvinfo.TlvInfoDecoder):
    RETRIES = 3

    def __init__(self):
        for attempt in range(self.RETRIES):
            if not os.path.islink(EEPROM_SYMLINK):
                time.sleep(1)
            else:
                break  

        if not os.path.exists(EEPROM_SYMLINK):
            logger.log_error("Nowhere to read syseeprom from! No symlink or cache file found")
            raise RuntimeError("No syseeprom symlink or cache file found")

        self.eeprom_path = EEPROM_SYMLINK
        super(Eeprom, self).__init__(self.eeprom_path, 0, '', True)
        self._eeprom_info_dict = None

    @default_return(return_value='Undefined.')
    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis

        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._get_eeprom_value(self._TLV_CODE_MAC_BASE)
        
    @default_return(return_value='Undefined.')
    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis

        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self._get_eeprom_value(self._TLV_CODE_SERIAL_NUMBER)

    @default_return(return_value='Undefined.')
    def get_product_name(self):
        """
        Retrieves the hardware product name for the chassis

        Returns:
            A string containing the hardware product name for this chassis.
        """
        return self._get_eeprom_value(self._TLV_CODE_PRODUCT_NAME)

    @default_return(return_value='Undefined.')
    def get_part_number(self):
        """
        Retrieves the hardware part number for the chassis

        Returns:
            A string containing the hardware part number for this chassis.
        """
        return self._get_eeprom_value(self._TLV_CODE_PART_NUMBER)

    @default_return({})
    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis

        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        if self._eeprom_info_dict is None:
            self._eeprom_info_dict = {}

            # Try get from DB first
            db_initialized = self._redis_hget('EEPROM_INFO|State', 'Initialized')
            if db_initialized == '1':
                code = self._TLV_CODE_PRODUCT_NAME
                while code <= self._TLV_CODE_SERVICE_TAG:
                    value = self._redis_hget('EEPROM_INFO|{}'.format(hex(code)), 'Value')
                    if value:
                        self._eeprom_info_dict[hex(code)] = value
                    code += 1

                # Handle vendor extension TLV
                vendor_extension_tlv_code = hex(self._TLV_CODE_VENDOR_EXT)
                try:
                    vendor_extension_num = int(self._redis_hget('EEPROM_INFO|{}'.format(vendor_extension_tlv_code), 'Num_vendor_ext'))
                except (ValueError, TypeError):
                    vendor_extension_num = 0

                if vendor_extension_num != 0:
                    for i in range(vendor_extension_num):
                        value = self._redis_hget('EEPROM_INFO|{}'.format(vendor_extension_tlv_code), 'Value_{}'.format(i))
                        if value:
                            if vendor_extension_tlv_code not in self._eeprom_info_dict:
                                self._eeprom_info_dict[vendor_extension_tlv_code] = [value]
                            else:
                                self._eeprom_info_dict[vendor_extension_tlv_code].append(value)
            
                # Get CRC 
                value = self._redis_hget('EEPROM_INFO|{}'.format(hex(self._TLV_CODE_CRC_32)), 'Value')
                if value:
                    self._eeprom_info_dict[hex(self._TLV_CODE_CRC_32)] = value
            else:
                eeprom = self.read_eeprom()
                visitor = EepromContentVisitor(self._eeprom_info_dict)
                self.visit_eeprom(eeprom, visitor)
        return self._eeprom_info_dict

    def _get_eeprom_value(self, code):
        """Helper function to help get EEPROM data by code

        Args:
            code (int): EEPROM TLV code

        Returns:
            str: value of EEPROM TLV
        """
        eeprom_info_dict = self.get_system_eeprom_info()
        return eeprom_info_dict[hex(code)]


class EepromContentVisitor(eeprom_tlvinfo.EepromDefaultVisitor):
    def __init__(self, content):
        self.content = content

    def visit_tlv(self, name, code, length, value):
        if code != Eeprom._TLV_CODE_VENDOR_EXT:
            self.content[hex(code)] = value.rstrip('\0')
        else:
            if value:
                value = value.rstrip('\0')
                if value:
                    code = hex(code)
                    if code not in self.content:
                        self.content[code] = [value]
                    else:
                        self.content[code].append(value)

