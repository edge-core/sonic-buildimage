#!/usr/bin/env python

try:
    import time
    from sonic_sfp.sfputilbase import *
    import sys
    import os
    import string
    from ctypes import create_string_buffer
    # sys.path.append('/usr/local/bin')
    # import sfp_detect
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


qfx5210_qsfp_cable_length_tup = ('Length(km)', 'Length OM3(2m)',
                          'Length OM2(m)', 'Length OM1(m)',
                          'Length Cable Assembly(m)')
  
qfx5210_sfp_cable_length_tup = ('LengthSMFkm-UnitsOfKm', 'LengthSMF(UnitsOf100m)',
                        'Length50um(UnitsOf10m)', 'Length62.5um(UnitsOfm)',
                        'LengthCable(UnitsOfm)', 'LengthOM3(UnitsOf10m)')

qfx5210_sfp_compliance_code_tup = ('10GEthernetComplianceCode', 'InfinibandComplianceCode',
                             'ESCONComplianceCodes', 'SONETComplianceCodes',
                             'EthernetComplianceCodes','FibreChannelLinkLength',
                             'FibreChannelTechnology', 'SFP+CableTechnology',
                             'FibreChannelTransmissionMedia','FibreChannelSpeed')

qfx5210_qsfp_compliance_code_tup = ('10/40G Ethernet Compliance Code', 'SONET Compliance codes',
                             'SAS/SATA compliance codes', 'Gigabit Ethernet Compliant codes',
                             'Fibre Channel link length/Transmitter Technology',
                             'Fibre Channel transmission media', 'Fibre Channel Speed')



class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    _port_start = 0
    _port_end = 63
    ports_in_block = 64
    cmd = '/var/run/sfppresence' 
    _port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
        61 : 25,
        62 : 26,
        63 : 27,
        64 : 28,
        55 : 29,
        56 : 30,
        53 : 31,
        54 : 32,
        9  : 33,
        10 : 34,
        11 : 35,
        12 : 36,
        1  : 37,
        2  : 38,
        3  : 39,
        4  : 40,
        6  : 41,
        5  : 42,
        8  : 43,
        7  : 44,
        13 : 45,
        14 : 46,
        15 : 47,
        16 : 48,
        17 : 49,
        18 : 50,
        19 : 51,
        20 : 52,
        25 : 53,
        26 : 54,
        27 : 55,
        28 : 56,
        29 : 57,
        30 : 58,
        31 : 59,
        32 : 60,
        21 : 61,
        22 : 62,
        23 : 63,
        24 : 64,
        41 : 65,
        42 : 66,
        43 : 67,
        44 : 68,
        33 : 69,
        34 : 70,
        35 : 71,
        36 : 72,
        45 : 73,
        46 : 74,
        47 : 75,
        48 : 76,
        37 : 77,
        38 : 78,
        39 : 79,
        40 : 80,
        57 : 81,
        58 : 82,
        59 : 83,
        60 : 84,
        49 : 85,
        50 : 86,
        51 : 87,
        52 : 88,}

    port_to_sysfs_map = [
        '/sys/bus/i2c/devices/37-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/38-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/39-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/40-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/42-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/41-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/44-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/43-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/33-0050/sfp_is_present',
        '/sys/bus/i2c/devices/34-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/35-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/36-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/45-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/46-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/47-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/48-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/49-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/50-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/51-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/52-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/61-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/62-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/63-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/64-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/53-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/54-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/55-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/56-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/57-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/58-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/59-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/60-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/69-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/70-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/71-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/72-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/77-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/78-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/79-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/80-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/65-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/66-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/67-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/68-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/73-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/74-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/75-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/76-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/85-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/86-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/87-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/88-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/31-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/32-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/29-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/30-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/81-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/82-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/83-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/84-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/25-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/26-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/27-0050/sfp_is_present', 
        '/sys/bus/i2c/devices/28-0050/sfp_is_present'

        ]
        # sys.path.append('/usr/local/bin')
    _qsfp_ports = range(0, ports_in_block + 1)


    def __init__(self):
        eeprom_path = '/sys/bus/i2c/devices/{0}-0050/sfp_eeprom'
        for x in range(0, self._port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x+1])
            self._port_to_eeprom_mapping[x] = port_eeprom_path
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False
	path = "/sys/bus/i2c/devices/19-0060/module_reset_{0}"
        port_ps = path.format(port_num+1)
          
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        #HW will clear reset after set.
        reg_file.seek(0)
        reg_file.write('1')
        reg_file.close()
        return True
        
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = "/sys/bus/i2c/devices/{0}-0050/sfp_is_present"
        port_ps = path.format(self.port_to_i2c_mapping[port_num+1])

          
        try:
            reg_file = open(port_ps)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        reg_value = reg_file.readline().rstrip()
        if reg_value == '1':
            return True

        return False

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end
	
    @property
    def qsfp_ports(self):
        return range(0, self.ports_in_block + 1)

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping

    #  Writing to a file from a list
    def write_to_file(self, file_name, from_list):
        try:
            fp1 = open(file_name, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        for i in from_list:
            fp1.write(i)
            fp1.write('\n')

        fp1.close()
        return True

     
     # Reading from a file to a list
    def read_from_file(self, file_name):
        try:
            fp = open(file_name, 'r')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

	to_list = fp.readlines()
	to_list = [x.rstrip() for x in to_list]
	fp.close()
	return to_list
    
    def sfp_detect(self):
        x = 0
        ret_dict = {}
        defl_dict = {}
        current_sfp_values = [0] * 64
        previous_sfp_values = [0] * 64

        if not os.path.isfile(self.cmd):
            pass
        else:
            if (self.read_from_file(self.cmd) == False):
                return False, defl_dict
            else:
                previous_sfp_values = self.read_from_file(self.cmd)

         # Read the current values from sysfs
        for x in range(len(self.port_to_sysfs_map)):
            try:
                reg_file = open(self.port_to_sysfs_map[x], 'r')
            except IOError as e:
                print "Error: unable to open file: %s" % str(e)
                return False, defl_dict

	    sfp_present = reg_file.readline().rstrip()
            reg_file.close()
            current_sfp_values[x] = sfp_present
	    if (current_sfp_values[x] != previous_sfp_values[x]):
	    	ret_dict.update({x:current_sfp_values[x]})

        if(self.write_to_file(self.cmd, current_sfp_values) == True):
            return True, ret_dict
        else:
            return False, defl_dict

    def get_transceiver_change_event(self):
        time.sleep(3)
        return self.sfp_detect()

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        try:
            eeprom = None

            if not self.get_presence(port_num):
                return False

            eeprom = open(self.port_to_eeprom_mapping[port_num], "rb")
            eeprom.seek(93)
            lpmode = ord(eeprom.read(1))

            if ((lpmode & 0x3) == 0x3):
                return True # Low Power Mode if "Power override" bit is 1 and "Power set" bit is 1
            else:
                return False # High Power Mode if one of the following conditions is matched:
                             # 1. "Power override" bit is 0
                             # 2. "Power override" bit is 1 and "Power set" bit is 0 
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    def set_low_power_mode(self, port_num, lpmode): 
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        try:
            eeprom = None

            if not self.get_presence(port_num):
                return False # Port is not present, unable to set the eeprom

            # Fill in write buffer
            regval = 0x3 if lpmode else 0x1 # 0x3:Low Power Mode, 0x1:High Power Mode
            buffer = create_string_buffer(1)
            buffer[0] = chr(regval)

            # Write to eeprom
            eeprom = open(self.port_to_eeprom_mapping[port_num], "r+b")
            eeprom.seek(93)
            eeprom.write(buffer[0])
            return True
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if eeprom is not None:
                eeprom.close()
                time.sleep(0.01)

    # Read out SFP type, vendor name, PN, REV, SN from eeprom.
    def get_transceiver_info_dict(self, port_num):
        transceiver_info_dict = {}
        compliance_code_dict = {}

        # ToDo: OSFP tranceiver info parsing not fully supported.
        # in inf8628.py lack of some memory map definition
        # will be implemented when the inf8628 memory map ready
        if port_num in self.osfp_ports:
            offset = 0
            vendor_rev_width = XCVR_HW_REV_WIDTH_OSFP

            sfpi_obj = inf8628InterfaceId()
            if sfpi_obj is None:
                print("Error: sfp_object open failed")
                return None

            file_path = self._get_port_eeprom_path(port_num, self.IDENTITY_EEPROM_ADDR)
            if not self._sfp_eeprom_present(file_path, 0):
                print("Error, file not exist %s" % file_path)
                return None

            try:
                sysfsfile_eeprom = open(file_path, mode="rb", buffering=0)
            except IOError:
                print("Error: reading sysfs file %s" % file_path)
                return None

            sfp_type_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + OSFP_TYPE_OFFSET), XCVR_TYPE_WIDTH)
            if sfp_type_raw is not None:
                sfp_type_data = sfpi_obj.parse_sfp_type(sfp_type_raw, 0)
            else:
                return None

            sfp_vendor_name_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + OSFP_VENDOR_NAME_OFFSET), XCVR_VENDOR_NAME_WIDTH)
            if sfp_vendor_name_raw is not None:
                sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_vendor_name_raw, 0)
            else:
                return None

            sfp_vendor_pn_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + OSFP_VENDOR_PN_OFFSET), XCVR_VENDOR_PN_WIDTH)
            if sfp_vendor_pn_raw is not None:
                sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_vendor_pn_raw, 0)
            else:
                return None

            sfp_vendor_rev_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + OSFP_HW_REV_OFFSET), vendor_rev_width)
            if sfp_vendor_rev_raw is not None:
                sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_vendor_rev_raw, 0)
            else:
                return None

            sfp_vendor_sn_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + OSFP_VENDOR_SN_OFFSET), XCVR_VENDOR_SN_WIDTH)
            if sfp_vendor_sn_raw is not None:
                sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_vendor_sn_raw, 0)
            else:
                return None

            try:
                sysfsfile_eeprom.close()
            except IOError:
                print("Error: closing sysfs file %s" % file_path)
                return None

            transceiver_info_dict['type'] = sfp_type_data['data']['type']['value']
            transceiver_info_dict['type_abbrv_name'] = sfp_type_data['data']['type_abbrv_name']['value']
            transceiver_info_dict['manufacturename'] = sfp_vendor_name_data['data']['Vendor Name']['value']
            transceiver_info_dict['modelname'] = sfp_vendor_pn_data['data']['Vendor PN']['value']
            transceiver_info_dict['hardwarerev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value']
            transceiver_info_dict['serialnum'] = sfp_vendor_sn_data['data']['Vendor SN']['value']
            # Below part is added to avoid fail the xcvrd, shall be implemented later
            transceiver_info_dict['vendor_oui'] = 'N/A'
            transceiver_info_dict['vendor_date'] = 'N/A'
            transceiver_info_dict['Connector'] = 'N/A'
            transceiver_info_dict['encoding'] = 'N/A'
            transceiver_info_dict['ext_identifier'] = 'N/A'
            transceiver_info_dict['ext_rateselect_compliance'] = 'N/A'
            transceiver_info_dict['cable_type'] = 'N/A'
            transceiver_info_dict['cable_length'] = 'N/A'
            transceiver_info_dict['specification_compliance'] = 'N/A'
            transceiver_info_dict['nominal_bit_rate'] = 'N/A'

        else:
            if port_num in self.qsfp_ports:
                offset = 128
                vendor_rev_width = XCVR_HW_REV_WIDTH_QSFP
                cable_length_width = XCVR_CABLE_LENGTH_WIDTH_QSFP
                interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_QSFP
                sfp_type = 'QSFP'

                sfpi_obj = sff8436InterfaceId()
                if sfpi_obj is None:
                    print("Error: sfp_object open failed")
                    return None

            else:
                offset = 0
                vendor_rev_width = XCVR_HW_REV_WIDTH_SFP
                cable_length_width = XCVR_CABLE_LENGTH_WIDTH_SFP
                interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_SFP
                sfp_type = 'SFP'

                sfpi_obj = sff8472InterfaceId()
                if sfpi_obj is None:
                    print("Error: sfp_object open failed")
                    return None

            file_path = self._get_port_eeprom_path(port_num, self.IDENTITY_EEPROM_ADDR)
            if not self._sfp_eeprom_present(file_path, 0):
                print("Error, file not exist %s" % file_path)
                return None

            try:
                sysfsfile_eeprom = open(file_path, mode="rb", buffering=0)
            except IOError:
                print("Error: reading sysfs file %s" % file_path)
                return None

            sfp_interface_bulk_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_INTFACE_BULK_OFFSET), interface_info_bulk_width)
            if sfp_interface_bulk_raw is not None:
                sfp_interface_bulk_data = sfpi_obj.parse_sfp_info_bulk(sfp_interface_bulk_raw, 0)
            else:
                return None

            sfp_vendor_name_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_VENDOR_NAME_OFFSET), XCVR_VENDOR_NAME_WIDTH)
            if sfp_vendor_name_raw is not None:
                sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_vendor_name_raw, 0)
            else:
                return None

            sfp_vendor_pn_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_VENDOR_PN_OFFSET), XCVR_VENDOR_PN_WIDTH)
            if sfp_vendor_pn_raw is not None:
                sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_vendor_pn_raw, 0)
            else:
                return None

            sfp_vendor_rev_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_HW_REV_OFFSET), vendor_rev_width)
            if sfp_vendor_rev_raw is not None:
                sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_vendor_rev_raw, 0)
            else:
                return None

            sfp_vendor_sn_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_VENDOR_SN_OFFSET), XCVR_VENDOR_SN_WIDTH)
            if sfp_vendor_sn_raw is not None:
                sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_vendor_sn_raw, 0)
            else:
                return None

            sfp_vendor_oui_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_VENDOR_OUI_OFFSET), XCVR_VENDOR_OUI_WIDTH)
            if sfp_vendor_oui_raw is not None:
                sfp_vendor_oui_data = sfpi_obj.parse_vendor_oui(sfp_vendor_oui_raw, 0)
            else:
                return None

            sfp_vendor_date_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + XCVR_VENDOR_DATE_OFFSET), XCVR_VENDOR_DATE_WIDTH)
            if sfp_vendor_date_raw is not None:
                sfp_vendor_date_data = sfpi_obj.parse_vendor_date(sfp_vendor_date_raw, 0)
            else:
                return None

            try:
                sysfsfile_eeprom.close()
            except IOError:
                print("Error: closing sysfs file %s" % file_path)
                return None

            transceiver_info_dict['type'] = sfp_interface_bulk_data['data']['type']['value']
            transceiver_info_dict['type_abbrv_name'] = sfp_interface_bulk_data['data']['type_abbrv_name']['value']
            transceiver_info_dict['manufacturename'] = sfp_vendor_name_data['data']['Vendor Name']['value']
            transceiver_info_dict['modelname'] = sfp_vendor_pn_data['data']['Vendor PN']['value']
            transceiver_info_dict['hardwarerev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value']
            transceiver_info_dict['serialnum'] = sfp_vendor_sn_data['data']['Vendor SN']['value']
            transceiver_info_dict['vendor_oui'] = sfp_vendor_oui_data['data']['Vendor OUI']['value']
            transceiver_info_dict['vendor_date'] = sfp_vendor_date_data['data']['VendorDataCode(YYYY-MM-DD Lot)']['value']
            transceiver_info_dict['Connector'] = sfp_interface_bulk_data['data']['Connector']['value']
            transceiver_info_dict['encoding'] = sfp_interface_bulk_data['data']['EncodingCodes']['value']
            transceiver_info_dict['ext_identifier'] = sfp_interface_bulk_data['data']['Extended Identifier']['value']
            transceiver_info_dict['ext_rateselect_compliance'] = sfp_interface_bulk_data['data']['RateIdentifier']['value']
            if sfp_type == 'QSFP':
                for key in qfx5210_qsfp_cable_length_tup:
                    if key in sfp_interface_bulk_data['data']:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])
                        break
                    else:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = 'N/A'

                for key in qfx5210_qsfp_compliance_code_tup:
                    if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
                transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)
               
                if sfp_interface_bulk_data['data'].has_key('Nominal Bit Rate(100Mbs)'):
                    transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['Nominal Bit Rate(100Mbs)']['value'])
                else:    
                    transceiver_info_dict['nominal_bit_rate'] = 'N/A'
            else:
                for key in qfx5210_sfp_cable_length_tup:
                    if key in sfp_interface_bulk_data['data']:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])
                    else:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = 'N/A'
 
                for key in qfx5210_sfp_compliance_code_tup:
                    if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
                transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)

                if sfp_interface_bulk_data['data'].has_key('NominalSignallingRate(UnitsOf100Mbd)'):
                    transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['NominalSignallingRate(UnitsOf100Mbd)']['value'])
                else:    
                    transceiver_info_dict['nominal_bit_rate'] = 'N/A'
                #transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['NominalSignallingRate(UnitsOf100Mbd)']['value'])
 
        return transceiver_info_dict

    def get_transceiver_dom_info_dict(self, port_num):
        transceiver_dom_info_dict = {}

        if port_num in self.osfp_ports:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            transceiver_dom_info_dict['temperature'] = 'N/A'
            transceiver_dom_info_dict['voltage'] = 'N/A'
            transceiver_dom_info_dict['rx1power'] = 'N/A'
            transceiver_dom_info_dict['rx2power'] = 'N/A'
            transceiver_dom_info_dict['rx3power'] = 'N/A'
            transceiver_dom_info_dict['rx4power'] = 'N/A'
            transceiver_dom_info_dict['tx1bias'] = 'N/A'
            transceiver_dom_info_dict['tx2bias'] = 'N/A'
            transceiver_dom_info_dict['tx3bias'] = 'N/A'
            transceiver_dom_info_dict['tx4bias'] = 'N/A'
            transceiver_dom_info_dict['tx1power'] = 'N/A'
            transceiver_dom_info_dict['tx2power'] = 'N/A'
            transceiver_dom_info_dict['tx3power'] = 'N/A'
            transceiver_dom_info_dict['tx4power'] = 'N/A'

        elif port_num in self.qsfp_ports:
            offset = 0
            offset_xcvr = 128
            file_path = self._get_port_eeprom_path(port_num, self.IDENTITY_EEPROM_ADDR)
            if not self._sfp_eeprom_present(file_path, 0):
                return None

            try:
                sysfsfile_eeprom = open(file_path, mode="rb", buffering=0)
            except IOError:
                print("Error: reading sysfs file %s" % file_path)
                return None

            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                return None

            # QSFP capability byte parse, through this byte can know whether it support tx_power or not.
            # TODO: in the future when decided to migrate to support SFF-8636 instead of SFF-8436,
            # need to add more code for determining the capability and version compliance
            # in SFF-8636 dom capability definitions evolving with the versions.
            qsfp_dom_capability_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset_xcvr + XCVR_DOM_CAPABILITY_OFFSET), XCVR_DOM_CAPABILITY_WIDTH)
            if qsfp_dom_capability_raw is not None:
                qspf_dom_capability_data = sfpi_obj.parse_qsfp_dom_capability(qsfp_dom_capability_raw, 0)
            else:
                return None

            dom_temperature_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + QSFP_TEMPE_OFFSET), QSFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
            else:
                return None

            dom_voltage_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + QSFP_VOLT_OFFSET), QSFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
            else:
                return None

            qsfp_dom_rev_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + QSFP_DOM_REV_OFFSET), QSFP_DOM_REV_WIDTH)
            if qsfp_dom_rev_raw is not None:
                qsfp_dom_rev_data = sfpd_obj.parse_sfp_dom_rev(qsfp_dom_rev_raw, 0)
            else:
                return None

            transceiver_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            transceiver_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']

            # The tx_power monitoring is only available on QSFP which compliant with SFF-8636
            # and claimed that it support tx_power with one indicator bit.
            dom_channel_monitor_data = {}
            qsfp_dom_rev = qsfp_dom_rev_data['data']['dom_rev']['value']
            qsfp_tx_power_support = qspf_dom_capability_data['data']['Tx_power_support']['value']
            if (qsfp_dom_rev[0:8] != 'SFF-8636' or (qsfp_dom_rev[0:8] == 'SFF-8636' and qsfp_tx_power_support != 'on')):
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                else:
                    return None

                transceiver_dom_info_dict['tx1power'] = 'N/A'
                transceiver_dom_info_dict['tx2power'] = 'N/A'
                transceiver_dom_info_dict['tx3power'] = 'N/A'
                transceiver_dom_info_dict['tx4power'] = 'N/A'
            else:
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_channel_monitor_raw, 0)
                else:
                    return None

                transceiver_dom_info_dict['tx1power'] = dom_channel_monitor_data['data']['TX1Power']['value']
                transceiver_dom_info_dict['tx2power'] = dom_channel_monitor_data['data']['TX2Power']['value']
                transceiver_dom_info_dict['tx3power'] = dom_channel_monitor_data['data']['TX3Power']['value']
                transceiver_dom_info_dict['tx4power'] = dom_channel_monitor_data['data']['TX4Power']['value']

            try:
                sysfsfile_eeprom.close()
            except IOError:
                print("Error: closing sysfs file %s" % file_path)
                return None

            transceiver_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            transceiver_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']
            transceiver_dom_info_dict['rx1power'] = dom_channel_monitor_data['data']['RX1Power']['value']
            transceiver_dom_info_dict['rx2power'] = dom_channel_monitor_data['data']['RX2Power']['value']
            transceiver_dom_info_dict['rx3power'] = dom_channel_monitor_data['data']['RX3Power']['value']
            transceiver_dom_info_dict['rx4power'] = dom_channel_monitor_data['data']['RX4Power']['value']
            transceiver_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TX1Bias']['value']
            transceiver_dom_info_dict['tx2bias'] = dom_channel_monitor_data['data']['TX2Bias']['value']
            transceiver_dom_info_dict['tx3bias'] = dom_channel_monitor_data['data']['TX3Bias']['value']
            transceiver_dom_info_dict['tx4bias'] = dom_channel_monitor_data['data']['TX4Bias']['value']

        else:
            offset = 256
            file_path = self._get_port_eeprom_path(port_num, self.DOM_EEPROM_ADDR)
            if not self._sfp_eeprom_present(file_path, 0):
                return None

            try:
                sysfsfile_eeprom = open(file_path, mode="rb", buffering=0)
            except IOError:
                print("Error: reading sysfs file %s" % file_path)
                return None

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            dom_temperature_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + SFP_TEMPE_OFFSET), SFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
            else:
                return None

            dom_voltage_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + SFP_VOLT_OFFSET), SFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
            else:
                return None

            dom_channel_monitor_raw = self._read_eeprom_specific_bytes(sysfsfile_eeprom, (offset + SFP_CHANNL_MON_OFFSET), SFP_CHANNL_MON_WIDTH)
            if dom_channel_monitor_raw is not None:
                dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
            else:
                return None

            try:
                sysfsfile_eeprom.close()
            except IOError:
                print("Error: closing sysfs file %s" % file_path)
                return None

            transceiver_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            transceiver_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']
            transceiver_dom_info_dict['rx1power'] = dom_channel_monitor_data['data']['RXPower']['value']
            transceiver_dom_info_dict['rx2power'] = 'N/A'
            transceiver_dom_info_dict['rx3power'] = 'N/A'
            transceiver_dom_info_dict['rx4power'] = 'N/A'
            transceiver_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TXBias']['value']
            transceiver_dom_info_dict['tx2bias'] = 'N/A'
            transceiver_dom_info_dict['tx3bias'] = 'N/A'
            transceiver_dom_info_dict['tx4bias'] = 'N/A'
            transceiver_dom_info_dict['tx1power'] = dom_channel_monitor_data['data']['TXPower']['value']
            transceiver_dom_info_dict['tx2power'] = 'N/A'
            transceiver_dom_info_dict['tx3power'] = 'N/A'
            transceiver_dom_info_dict['tx4power'] = 'N/A'

        return transceiver_dom_info_dict
