#!/usr/bin/env python

########################################################################
# DellEMC S6000
#
# Module contains platform specific implementation of SONiC Platform
# Base API and provides the EEPROMs' information.
#
# The different EEPROMs available are as follows:
# - System EEPROM : Contains Serial number, Service tag, Base MA
#                   address, etc. in ONIE TlvInfo EEPROM format.
# - PSU EEPROM : Contains Serial number, Part number, Service Tag,
#                PSU type, Revision.
# - Fan EEPROM : Contains Serial number, Part number, Service Tag,
#                Fan type, Number of Fans in Fantray, Revision.
########################################################################


try:
    import os
    from sonic_platform_base.sonic_eeprom.eeprom_base import EepromDecoder
    from sonic_platform_base.sonic_eeprom.eeprom_tlvinfo import TlvInfoDecoder
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


# PSU eeprom fields in format required by EepromDecoder
psu_eeprom_format = [
    ('PPID', 's', 20), ('DPN Rev', 's', 3), ('Service Tag', 's', 7),
    ('Part Number', 's', 10), ('Part Num Revision', 's', 3),
    ('Mfg Test', 's', 2), ('Redundant copy', 's', 83), ('PSU Type', 's', 1),
    ('Fab Rev', 's', 2)
    ]

# Fan eeprom fields in format required by EepromDecoder
fan_eeprom_format = [
    ('PPID', 's', 20), ('DPN Rev', 's', 3), ('Service Tag', 's', 7),
    ('Part Number', 's', 10), ('Part Num Revision', 's', 3),
    ('Mfg Test', 's', 2), ('Redundant copy', 's', 83),
    ('Number of Fans', 's', 1), ('Fan Type', 's', 1),
    ('Fab Rev', 's', 2)
    ]


class Eeprom(TlvInfoDecoder):
    """DellEMC Platform-specific EEPROM class"""

    I2C_DIR = "/sys/class/i2c-adapter/"

    def __init__(self, is_psu=False, psu_index=0, is_fan=False, fan_index=0):
        self.is_psu_eeprom = is_psu
        self.is_fan_eeprom = is_fan
        self.is_sys_eeprom = not (is_psu | is_fan)

        if self.is_sys_eeprom:
            self.start_offset = 0
            self.eeprom_path = self.I2C_DIR + "i2c-10/10-0053/eeprom"
            # System EEPROM is in ONIE TlvInfo EEPROM format
            super(Eeprom, self).__init__(self.eeprom_path,
                                         self.start_offset, '', True)
            self._load_system_eeprom()
        else:
            self.start_offset = 6
            if self.is_psu_eeprom:
                self.index = psu_index
                self.eeprom_path = self.I2C_DIR \
                    + "i2c-1/1-005{}/eeprom".format(2 - self.index)
                self.format = psu_eeprom_format
            else:
                self.index = fan_index
                self.eeprom_path = self.I2C_DIR \
                    + "i2c-11/11-005{}/eeprom".format(4 - self.index)
                self.format = fan_eeprom_format
            EepromDecoder.__init__(self, self.eeprom_path, self.format,
                                   self.start_offset, '', True)
            self._load_device_eeprom()

    def _load_system_eeprom(self):
        """
        Reads the system EEPROM and retrieves the values corresponding
        to the codes defined as per ONIE TlvInfo EEPROM format and fills
        them in a dictionary.
        """
        try:
            # Read System EEPROM as per ONIE TlvInfo EEPROM format.
            self.eeprom_data = self.read_eeprom()
        except:
            self.base_mac = 'NA'
            self.serial_number = 'NA'
            self.part_number = 'NA'
            self.model_str = 'NA'
            self.serial = 'NA'
            self.eeprom_tlv_dict = dict()
        else:
            eeprom = self.eeprom_data
            self.eeprom_tlv_dict = dict()

            if not self.is_valid_tlvinfo_header(eeprom):
                self.base_mac = 'NA'
                self.serial_number = 'NA'
                self.part_number = 'NA'
                self.model_str = 'NA'
                self.serial = 'NA'
                return

            total_length = (ord(eeprom[9]) << 8) | ord(eeprom[10])
            tlv_index = self._TLV_INFO_HDR_LEN
            tlv_end = self._TLV_INFO_HDR_LEN + total_length

            while (tlv_index + 2) < len(eeprom) and tlv_index < tlv_end:
                if not self.is_valid_tlv(eeprom[tlv_index:]):
                    break

                tlv = eeprom[tlv_index:tlv_index + 2
                             + ord(eeprom[tlv_index + 1])]
                code = "0x%02X" % (ord(tlv[0]))

                if ord(tlv[0]) == self._TLV_CODE_VENDOR_EXT:
                    value = str((ord(tlv[2]) << 24) | (ord(tlv[3]) << 16) |
                                (ord(tlv[4]) << 8) | ord(tlv[5]))
                    value += str(tlv[6:6 + ord(tlv[1])])
                else:
                    name, value = self.decoder(None, tlv)

                self.eeprom_tlv_dict[code] = value
                if ord(eeprom[tlv_index]) == self._TLV_CODE_CRC_32:
                    break

                tlv_index += ord(eeprom[tlv_index+1]) + 2

            self.base_mac = self.eeprom_tlv_dict.get(
                                "0x%X" % (self._TLV_CODE_MAC_BASE), 'NA')
            self.serial_number = self.eeprom_tlv_dict.get(
                                "0x%X" % (self._TLV_CODE_SERIAL_NUMBER), 'NA')
            self.part_number = self.eeprom_tlv_dict.get(
                                "0x%X" % (self._TLV_CODE_PART_NUMBER), 'NA')
            self.model_str = self.eeprom_tlv_dict.get(
                                "0x%X" % (self._TLV_CODE_PRODUCT_NAME), 'NA')
            self.serial = self.eeprom_tlv_dict.get(
                                "0x%X" % (self._TLV_CODE_SERVICE_TAG), 'NA')

    def _load_device_eeprom(self):
        """
        Reads the Fan/PSU EEPROM and retrieves the serial number and
        model number of the device.
        """
        try:
            # Read Fan/PSU EEPROM as per the specified format.
            self.eeprom_data = EepromDecoder.read_eeprom(self)
        except:
            self.serial_number = 'NA'
            self.part_number = 'NA'
            if self.is_psu_eeprom:
                self.psu_type = 'NA'
            else:
                self.fan_type = 'NA'
        else:
            (valid, data) = self._get_eeprom_field("PPID")
            if valid:
                ppid = data
                self.serial_number = (ppid[:2] + "-" + ppid[2:8] + "-"
                                      + ppid[8:13] + "-" + ppid[13:16]
                                      + "-" + ppid[16:])
                (valid, data) = self._get_eeprom_field("DPN Rev")
                if valid:
                    self.serial_number += "-" + data
            else:
                self.serial_number = 'NA'

            (valid, data) = self._get_eeprom_field("Part Number")
            if valid:
                self.part_number = data
            else:
                self.part_number = 'NA'

            if self.is_psu_eeprom:
                (valid, data) = self._get_eeprom_field("PSU Type")
                if valid:
                    self.psu_type = data
                else:
                    self.psu_type = 'NA'
            else:
                (valid, data) = self._get_eeprom_field("Fan Type")
                if valid:
                    self.fan_type = data
                else:
                    self.fan_type = 'NA'

    def _get_eeprom_field(self, field_name):
        """
        For a field name specified in the EEPROM format, returns the
        presence of the field and the value for the same.
        """
        field_start = 0
        for field in self.format:
            field_end = field_start + field[2]
            if field[0] == field_name:
                return (True, self.eeprom_data[field_start:field_end])
            field_start = field_end

        return (False, None)

    def serial_number_str(self):
        """
        Returns the serial number.
        """
        return self.serial_number

    def part_number_str(self):
        """
        Returns the part number.
        """
        return self.part_number

    def airflow_fan_type(self):
        """
        Returns the airflow fan type.
        """
        if self.is_psu_eeprom:
            return int(self.psu_type.encode('hex'), 16)
        else:
            return int(self.fan_type.encode('hex'), 16)

    # System EEPROM specific methods
    def base_mac_addr(self):
        """
        Returns the base MAC address found in the system EEPROM.
        """
        return self.base_mac

    def modelstr(self):
        """
        Returns the Model name.
        """
        return self.model_str

    def serial_str(self):
        """
        Returns the servicetag number.
        """
        return self.serial

    def system_eeprom_info(self):
        """
        Returns a dictionary, where keys are the type code defined in
        ONIE EEPROM format and values are their corresponding values
        found in the system EEPROM.
        """
        return self.eeprom_tlv_dict
