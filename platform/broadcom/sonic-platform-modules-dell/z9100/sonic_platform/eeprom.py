#!/usr/bin/env python

#############################################################################
# DellEmc Z9100
#
# Platform and model specific eeprom subclass, inherits from the base class,
# and provides the followings:
# - the eeprom format definition
# - specific encoder/decoder if there is special need
#############################################################################

try:
    from sonic_eeprom import eeprom_tlvinfo
    import binascii
except ImportError, e:
    raise ImportError(str(e) + "- required module not found")


class Eeprom(eeprom_tlvinfo.TlvInfoDecoder):

    def __init__(self):
        self.eeprom_path = "/sys/class/i2c-adapter/i2c-2/2-0050/eeprom"
        super(Eeprom, self).__init__(self.eeprom_path, 0, '', True)
        try:
            self.eeprom_data = self.read_eeprom()
        except:
            self.eeprom_data = "N/A"
            raise RuntimeError("Eeprom is not Programmed")

    def serial_number_str(self):
        (is_valid, results) = self.get_tlv_field(
                         self.eeprom_data, self._TLV_CODE_SERIAL_NUMBER)
        if not is_valid:
            return "N/A"
        return results[2]

    def base_mac_addr(self):
        (is_valid, t) = self.get_tlv_field(
                          self.eeprom_data, self._TLV_CODE_MAC_BASE)
        if not is_valid or t[1] != 6:
            return super(TlvInfoDecoder, self).switchaddrstr(e)

        return ":".join([binascii.b2a_hex(T) for T in t[2]])

    def modelstr(self):
        (is_valid, results) = self.get_tlv_field(
                        self.eeprom_data, self._TLV_CODE_PRODUCT_NAME)
        if not is_valid:
            return "N/A"

        return results[2]

    def part_number_str(self):
        (is_valid, results) = self.get_tlv_field(
                    self.eeprom_data, self._TLV_CODE_PART_NUMBER)
        if not is_valid:
            return "N/A"

        return results[2]

    def serial_str(self):
        (is_valid, results) = self.get_tlv_field(
                    self.eeprom_data, self._TLV_CODE_SERVICE_TAG)
        if not is_valid:
            return "N/A"

        return results[2]

    def revision_str(self):
        (is_valid, results) = self.get_tlv_field(
                    self.eeprom_data, self._TLV_CODE_DEVICE_VERSION)
        if not is_valid:
            return "N/A"

        return results[2]

