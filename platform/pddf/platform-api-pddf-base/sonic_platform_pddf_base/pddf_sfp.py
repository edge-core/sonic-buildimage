#!/usr/bin/env python

try:
    import time
    from ctypes import create_string_buffer
    from sonic_platform_base.sfp_base import SfpBase
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472InterfaceId
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472Dom
    from sonic_platform_base.sonic_sfp.sff8472 import sffbase
    from sonic_platform_base.sonic_sfp.inf8628 import inf8628InterfaceId
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

# definitions of the offset and width for values in XCVR info eeprom
XCVR_INTFACE_BULK_OFFSET = 0
XCVR_INTFACE_BULK_WIDTH_QSFP = 20
XCVR_INTFACE_BULK_WIDTH_SFP = 21
XCVR_TYPE_OFFSET = 0
XCVR_TYPE_WIDTH = 1
XCVR_EXT_TYPE_OFFSET = 1
XCVR_EXT_TYPE_WIDTH = 1
XCVR_CONNECTOR_OFFSET = 2
XCVR_CONNECTOR_WIDTH = 1
XCVR_COMPLIANCE_CODE_OFFSET = 3
XCVR_COMPLIANCE_CODE_WIDTH = 8
XCVR_ENCODING_OFFSET = 11
XCVR_ENCODING_WIDTH = 1
XCVR_NBR_OFFSET = 12
XCVR_NBR_WIDTH = 1
XCVR_EXT_RATE_SEL_OFFSET = 13
XCVR_EXT_RATE_SEL_WIDTH = 1
XCVR_CABLE_LENGTH_OFFSET = 14
XCVR_CABLE_LENGTH_WIDTH_QSFP = 5
XCVR_CABLE_LENGTH_WIDTH_SFP = 6
XCVR_VENDOR_NAME_OFFSET = 20
XCVR_VENDOR_NAME_WIDTH = 16
XCVR_VENDOR_OUI_OFFSET = 37
XCVR_VENDOR_OUI_WIDTH = 3
XCVR_VENDOR_PN_OFFSET = 40
XCVR_VENDOR_PN_WIDTH = 16
XCVR_HW_REV_OFFSET = 56
XCVR_HW_REV_WIDTH_OSFP = 2
XCVR_HW_REV_WIDTH_QSFP = 2
XCVR_HW_REV_WIDTH_SFP = 4
XCVR_VENDOR_SN_OFFSET = 68
XCVR_VENDOR_SN_WIDTH = 16
XCVR_VENDOR_DATE_OFFSET = 84
XCVR_VENDOR_DATE_WIDTH = 8
XCVR_DOM_CAPABILITY_OFFSET = 92
XCVR_DOM_CAPABILITY_WIDTH = 1

# definitions of the offset for values in OSFP info eeprom
OSFP_TYPE_OFFSET = 0
OSFP_VENDOR_NAME_OFFSET = 129
OSFP_VENDOR_PN_OFFSET = 148
OSFP_HW_REV_OFFSET = 164
OSFP_VENDOR_SN_OFFSET = 166

# definitions of the offset and width for values in DOM info eeprom
QSFP_DOM_REV_OFFSET = 1
QSFP_DOM_REV_WIDTH = 1
QSFP_TEMPE_OFFSET = 22
QSFP_TEMPE_WIDTH = 2
QSFP_VOLT_OFFSET = 26
QSFP_VOLT_WIDTH = 2
QSFP_CHANNL_MON_OFFSET = 34
QSFP_CHANNL_MON_WIDTH = 16
QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH = 24
QSFP_CONTROL_OFFSET = 86
QSFP_CONTROL_WIDTH = 8
QSFP_CHANNL_RX_LOS_STATUS_OFFSET = 3
QSFP_CHANNL_RX_LOS_STATUS_WIDTH = 1
QSFP_CHANNL_TX_FAULT_STATUS_OFFSET = 4
QSFP_CHANNL_TX_FAULT_STATUS_WIDTH = 1
QSFP_POWEROVERRIDE_OFFSET = 93
QSFP_POWEROVERRIDE_WIDTH = 1
QSFP_MODULE_THRESHOLD_OFFSET = 128
QSFP_MODULE_THRESHOLD_WIDTH = 24
QSFP_CHANNEL_THRESHOLD_OFFSET = 176
QSFP_CHANNEL_THRESHOLD_WIDTH = 16


SFP_TEMPE_OFFSET = 96
SFP_TEMPE_WIDTH = 2
SFP_VOLT_OFFSET = 98
SFP_VOLT_WIDTH = 2
SFP_CHANNL_MON_OFFSET = 100
SFP_CHANNL_MON_WIDTH = 6
SFP_MODULE_THRESHOLD_OFFSET = 0
SFP_MODULE_THRESHOLD_WIDTH = 40
SFP_CHANNL_THRESHOLD_OFFSET = 112
SFP_CHANNL_THRESHOLD_WIDTH = 2
SFP_STATUS_CONTROL_OFFSET = 110
SFP_STATUS_CONTROL_WIDTH = 1
SFP_TX_DISABLE_HARD_BIT = 7
SFP_TX_DISABLE_SOFT_BIT = 6


qsfp_cable_length_tup = ('Length(km)', 'Length OM3(2m)',
                         'Length OM2(m)', 'Length OM1(m)',
                         'Length Cable Assembly(m)')

sfp_cable_length_tup = ('LengthSMFkm-UnitsOfKm', 'LengthSMF(UnitsOf100m)',
                        'Length50um(UnitsOf10m)', 'Length62.5um(UnitsOfm)',
                        'LengthCable(UnitsOfm)', 'LengthOM3(UnitsOf10m)')

sfp_compliance_code_tup = ('10GEthernetComplianceCode', 'InfinibandComplianceCode',
                           'ESCONComplianceCodes', 'SONETComplianceCodes',
                           'EthernetComplianceCodes', 'FibreChannelLinkLength',
                           'FibreChannelTechnology', 'SFP+CableTechnology',
                           'FibreChannelTransmissionMedia', 'FibreChannelSpeed')

qsfp_compliance_code_tup = ('10/40G Ethernet Compliance Code', 'SONET Compliance codes',
                            'SAS/SATA compliance codes', 'Gigabit Ethernet Compliant codes',
                            'Fibre Channel link length/Transmitter Technology',
                            'Fibre Channel transmission media', 'Fibre Channel Speed')

PAGE_OFFSET = 0
KEY_OFFSET = 1
KEY_WIDTH = 2
FUNC_NAME = 3

INFO_OFFSET = 128
DOM_OFFSET = 0
DOM_OFFSET1 = 384


class PddfSfp(SfpBase):
    """
    PDDF generic Sfp class
    """

    pddf_obj = {}
    plugin_data = {}
    _port_to_eeprom_mapping = {}
    _port_start = 0
    _port_end = 0
    _port_to_type_mapping = {}
    _qsfp_ports = []
    _sfp_ports = []

    # Read out any bytes from any offset
    def __read_eeprom_specific_bytes(self, offset, num_bytes):
        sysfsfile_eeprom = None
        eeprom_raw = []
        for i in range(0, num_bytes):
            eeprom_raw.append("0x00")

        try:
            sysfsfile_eeprom = open(self.eeprom_path, mode="rb", buffering=0)
            sysfsfile_eeprom.seek(offset)
            raw = sysfsfile_eeprom.read(num_bytes)
            for n in range(0, num_bytes):
                eeprom_raw[n] = hex(ord(raw[n]))[2:].zfill(2)
        except Exception as e:
            print("Error: Unable to open eeprom_path: %s" % (str(e)))
        finally:
            if sysfsfile_eeprom:
                sysfsfile_eeprom.close()

        return eeprom_raw

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        if not pddf_data or not pddf_plugin_data:
            raise ValueError('PDDF JSON data error')

        self.pddf_obj = pddf_data
        self.plugin_data = pddf_plugin_data

        self.platform = self.pddf_obj.get_platform()

        # index is 0-based
        self._port_start = 0
        self._port_end = int(self.platform['num_ports'])
        if index < self._port_start or index >= self._port_end:
            print("Invalid port index %d" % index)
            return

        self.port_index = index+1
        self.device = 'PORT{}'.format(self.port_index)
        self.sfp_type = self.pddf_obj.get_device_type(self.device)
        self.is_qsfp_port = True if (self.sfp_type == 'QSFP' or self.sfp_type == 'QSFP28') else False
        self.is_osfp_port = True if (self.sfp_type == 'OSFP' or self.sfp_type == 'QSFP-DD') else False
        self.eeprom_path = self.pddf_obj.get_path(self.device, 'eeprom')

        self.info_dict_keys = ['type', 'hardware_rev', 'serial', 'manufacturer', 'model', 'connector', 'encoding',
                               'ext_identifier', 'ext_rateselect_compliance', 'cable_type', 'cable_length', 'nominal_bit_rate',
                               'specification_compliance', 'vendor_date', 'vendor_oui', 'application_advertisement']

        self.dom_dict_keys = ['rx_los', 'tx_fault', 'reset_status', 'power_lpmode', 'tx_disable', 'tx_disable_channel',
                              'temperature', 'voltage', 'rx1power', 'rx2power', 'rx3power', 'rx4power', 'tx1bias', 'tx2bias',
                              'tx3bias', 'tx4bias', 'tx1power', 'tx2power', 'tx3power', 'tx4power']

        self.threshold_dict_keys = ['temphighalarm', 'temphighwarning', 'templowalarm', 'templowwarning',
                                    'vcchighalarm', 'vcchighwarning', 'vcclowalarm', 'vcclowwarning', 'rxpowerhighalarm',
                                    'rxpowerhighwarning', 'rxpowerlowalarm', 'rxpowerlowwarning', 'txpowerhighalarm', 'txpowerhighwarning',
                                    'txpowerlowalarm', 'txpowerlowwarning', 'txbiashighalarm', 'txbiashighwarning', 'txbiaslowalarm',
                                    'txbiaslowwarning']

        SfpBase.__init__(self)

    def get_transceiver_info(self):
        """
        Retrieves transceiver info of this SFP
        Returns:
            A dict which contains following keys/values :
        ========================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        type                       |1*255VCHAR     |type of SFP
        hardware_rev                |1*255VCHAR     |hardware version of SFP
        serial                  |1*255VCHAR     |serial number of the SFP
        manufacturer            |1*255VCHAR     |SFP vendor name
        model                  |1*255VCHAR     |SFP model name
        connector                  |1*255VCHAR     |connector information
        encoding                   |1*255VCHAR     |encoding information
        ext_identifier             |1*255VCHAR     |extend identifier
        ext_rateselect_compliance  |1*255VCHAR     |extended rateSelect compliance
        cable_length               |INT            |cable length in m
        nominal_bit_rate           |INT            |nominal bit rate by 100Mbs
        specification_compliance   |1*255VCHAR     |specification compliance
        vendor_date                |1*255VCHAR     |vendor date
        vendor_oui                 |1*255VCHAR     |vendor OUI
        application_advertisement  |1*255VCHAR     |supported applications advertisement
        ========================================================================
        """
        # check present status
        if not self.get_presence():
            return None

        if self.is_osfp_port:
            sfpi_obj = inf8628InterfaceId()
            offset = 0
            type_offset = OSFP_TYPE_OFFSET
            vendor_rev_width = XCVR_HW_REV_WIDTH_OSFP
            hw_rev_offset = OSFP_HW_REV_OFFSET
            vendor_name_offset = OSFP_VENDOR_NAME_OFFSET
            vendor_pn_offset = OSFP_VENDOR_PN_OFFSET
            vendor_sn_offset = OSFP_VENDOR_SN_OFFSET
            interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_QSFP
            sfp_type = 'OSFP'

        elif self.is_qsfp_port:
            sfpi_obj = sff8436InterfaceId()
            offset = 128
            type_offset = XCVR_TYPE_OFFSET
            vendor_rev_width = XCVR_HW_REV_WIDTH_QSFP
            hw_rev_offset = XCVR_HW_REV_OFFSET
            vendor_name_offset = XCVR_VENDOR_NAME_OFFSET
            vendor_pn_offset = XCVR_VENDOR_PN_OFFSET
            vendor_sn_offset = XCVR_VENDOR_SN_OFFSET
            interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_QSFP
            sfp_type = 'QSFP'
        else:
            sfpi_obj = sff8472InterfaceId()
            offset = 0
            type_offset = XCVR_TYPE_OFFSET
            vendor_rev_width = XCVR_HW_REV_WIDTH_SFP
            hw_rev_offset = XCVR_HW_REV_OFFSET
            vendor_name_offset = XCVR_VENDOR_NAME_OFFSET
            vendor_pn_offset = XCVR_VENDOR_PN_OFFSET
            vendor_sn_offset = XCVR_VENDOR_SN_OFFSET
            interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_SFP
            sfp_type = 'SFP'

        if sfpi_obj is None:
            return None

        if self.is_osfp_port:
            sfp_type_raw = self.__read_eeprom_specific_bytes((offset + type_offset), XCVR_TYPE_WIDTH)
            if sfp_type_raw is not None:
                sfp_type_data = sfpi_obj.parse_sfp_type(sfp_type_raw, 0)
                sfp_type_abbrv_name = sfpi_obj.parse_sfp_type_abbrv_name(sfp_typ_raw, 0)
        else:
            sfp_interface_bulk_raw = self.__read_eeprom_specific_bytes(
                (offset + XCVR_INTFACE_BULK_OFFSET), interface_info_bulk_width)
            if sfp_interface_bulk_raw is not None:
                sfp_interface_bulk_data = sfpi_obj.parse_sfp_info_bulk(sfp_interface_bulk_raw, 0)

            sfp_vendor_oui_raw = self.__read_eeprom_specific_bytes(
                (offset + XCVR_VENDOR_OUI_OFFSET), XCVR_VENDOR_OUI_WIDTH)
            if sfp_vendor_oui_raw is not None:
                sfp_vendor_oui_data = sfpi_obj.parse_vendor_oui(sfp_vendor_oui_raw, 0)

            sfp_vendor_date_raw = self.__read_eeprom_specific_bytes(
                (offset + XCVR_VENDOR_DATE_OFFSET), XCVR_VENDOR_DATE_WIDTH)
            if sfp_vendor_date_raw is not None:
                sfp_vendor_date_data = sfpi_obj.parse_vendor_date(sfp_vendor_date_raw, 0)

        sfp_vendor_name_raw = self.__read_eeprom_specific_bytes(
            (offset + vendor_name_offset), XCVR_VENDOR_NAME_WIDTH)
        sfp_vendor_name_data = sfpi_obj.parse_vendor_name(
            sfp_vendor_name_raw, 0)

        sfp_vendor_pn_raw = self.__read_eeprom_specific_bytes(
            (offset + vendor_pn_offset), XCVR_VENDOR_PN_WIDTH)
        sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(
            sfp_vendor_pn_raw, 0)

        sfp_vendor_rev_raw = self.__read_eeprom_specific_bytes(
            (offset + hw_rev_offset), vendor_rev_width)
        sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(
            sfp_vendor_rev_raw, 0)

        sfp_vendor_sn_raw = self.__read_eeprom_specific_bytes(
            (offset + vendor_sn_offset), XCVR_VENDOR_SN_WIDTH)
        sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(
            sfp_vendor_sn_raw, 0)

        xcvr_info_dict = dict.fromkeys(self.info_dict_keys, 'N/A')
        compliance_code_dict = dict()

        if sfp_interface_bulk_data:
            xcvr_info_dict['type'] = sfp_interface_bulk_data['data']['type']['value']
            xcvr_info_dict['connector'] = sfp_interface_bulk_data['data']['Connector']['value']
            xcvr_info_dict['encoding'] = sfp_interface_bulk_data['data']['EncodingCodes']['value']
            xcvr_info_dict['ext_identifier'] = sfp_interface_bulk_data['data']['Extended Identifier']['value']
            xcvr_info_dict['ext_rateselect_compliance'] = sfp_interface_bulk_data['data']['RateIdentifier']['value']
            xcvr_info_dict['type_abbrv_name'] = sfp_interface_bulk_data['data']['type_abbrv_name']['value']
        else:
            xcvr_info_dict['type'] = sfp_type_data['data']['type']['value'] if sfp_type_data else 'N/A'
            xcvr_info_dict['type_abbrv_name'] = sfp_type_abbrv_name['data']['type_abbrv_name']['value'] if sfp_type_abbrv_name else 'N/A'

        xcvr_info_dict['manufacturer'] = sfp_vendor_name_data['data']['Vendor Name']['value'] if sfp_vendor_name_data else 'N/A'
        xcvr_info_dict['model'] = sfp_vendor_pn_data['data']['Vendor PN']['value'] if sfp_vendor_pn_data else 'N/A'
        xcvr_info_dict['hardware_rev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value'] if sfp_vendor_rev_data else 'N/A'
        xcvr_info_dict['serial'] = sfp_vendor_sn_data['data']['Vendor SN']['value'] if sfp_vendor_sn_data else 'N/A'
        xcvr_info_dict['vendor_oui'] = sfp_vendor_oui_data['data']['Vendor OUI']['value'] if sfp_vendor_oui_data else 'N/A'
        xcvr_info_dict['vendor_date'] = sfp_vendor_date_data['data'][
            'VendorDataCode(YYYY-MM-DD Lot)']['value'] if sfp_vendor_date_data else 'N/A'
        xcvr_info_dict['cable_type'] = "Unknown"
        xcvr_info_dict['cable_length'] = "Unknown"

        if sfp_type == 'QSFP':
            for key in qsfp_cable_length_tup:
                if key in sfp_interface_bulk_data['data']:
                    xcvr_info_dict['cable_type'] = key
                    xcvr_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])

            for key in qsfp_compliance_code_tup:
                if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                    compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
            xcvr_info_dict['specification_compliance'] = str(compliance_code_dict)

            nkey = 'Nominal Bit Rate(100Mbs)'
            if nkey in sfp_interface_bulk_data['data']:
                xcvr_info_dict['nominal_bit_rate'] = str(
                    sfp_interface_bulk_data['data']['Nominal Bit Rate(100Mbs)']['value'])
            else:
                xcvr_info_dict['nominal_bit_rate'] = 'N/A'
        elif sfp_type == 'OSFP':
            pass
        else:
            for key in sfp_cable_length_tup:
                if key in sfp_interface_bulk_data['data']:
                    xcvr_info_dict['cable_type'] = key
                    xcvr_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])

            for key in sfp_compliance_code_tup:
                if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                    compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
            xcvr_info_dict['specification_compliance'] = str(compliance_code_dict)

            xcvr_info_dict['nominal_bit_rate'] = str(
                sfp_interface_bulk_data['data']['NominalSignallingRate(UnitsOf100Mbd)']['value'])

        return xcvr_info_dict

    def get_transceiver_bulk_status(self):
        """
        Retrieves transceiver bulk status of this SFP
        Returns:
            A dict which contains following keys/values :
        ========================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        rx_los                     |BOOLEAN        |RX loss-of-signal status, True if has RX los, False if not.
        tx_fault                   |BOOLEAN        |TX fault status, True if has TX fault, False if not.
        reset_status               |BOOLEAN        |reset status, True if SFP in reset, False if not.
        lp_mode                    |BOOLEAN        |low power mode status, True in lp mode, False if not.
        tx_disable                 |BOOLEAN        |TX disable status, True TX disabled, False if not.
        tx_disabled_channel        |HEX            |disabled TX channels in hex, bits 0 to 3 represent channel 0
                                   |               |to channel 3.
        temperature                |INT            |module temperature in Celsius
        voltage                    |INT            |supply voltage in mV
        tx<n>bias                  |INT            |TX Bias Current in mA, n is the channel number,
                                   |               |for example, tx2bias stands for tx bias of channel 2.
        rx<n>power                 |INT            |received optical power in mW, n is the channel number,
                                   |               |for example, rx2power stands for rx power of channel 2.
        tx<n>power                 |INT            |TX output power in mW, n is the channel number,
                                   |               |for example, tx2power stands for tx power of channel 2.
        ========================================================================
        """
        # check present status
        if not self.get_presence():
            return None

        xcvr_dom_info_dict = dict.fromkeys(self.dom_dict_keys, 'N/A')

        if self.is_osfp_port:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            pass
        elif self.is_qsfp_port:
            # QSFPs
            offset = 0
            offset_xcvr = 128

            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                return None

            qsfp_dom_capability_raw = self.__read_eeprom_specific_bytes(
                (offset_xcvr + XCVR_DOM_CAPABILITY_OFFSET), XCVR_DOM_CAPABILITY_WIDTH)
            if qsfp_dom_capability_raw is not None:
                qspf_dom_capability_data = sfpi_obj.parse_qsfp_dom_capability(
                    qsfp_dom_capability_raw, 0)
            else:
                return None

            dom_temperature_raw = self.__read_eeprom_specific_bytes((offset + QSFP_TEMPE_OFFSET), QSFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
            else:
                return None

            dom_voltage_raw = self.__read_eeprom_specific_bytes((offset + QSFP_VOLT_OFFSET), QSFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
            else:
                return None

            qsfp_dom_rev_raw = self.__read_eeprom_specific_bytes((offset + QSFP_DOM_REV_OFFSET), QSFP_DOM_REV_WIDTH)
            if qsfp_dom_rev_raw is not None:
                qsfp_dom_rev_data = sfpd_obj.parse_sfp_dom_rev(qsfp_dom_rev_raw, 0)
            else:
                return None

            xcvr_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            xcvr_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']

            # The tx_power monitoring is only available on QSFP which compliant with SFF-8636
            # and claimed that it support tx_power with one indicator bit.
            dom_channel_monitor_data = {}
            qsfp_dom_rev = qsfp_dom_rev_data['data']['dom_rev']['value']
            qsfp_tx_power_support = qspf_dom_capability_data['data']['Tx_power_support']['value']
            if (qsfp_dom_rev[0:8] != 'SFF-8636' or (qsfp_dom_rev[0:8] == 'SFF-8636' and qsfp_tx_power_support != 'on')):
                dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
                    (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                else:
                    return None

                xcvr_dom_info_dict['tx1power'] = 'N/A'
                xcvr_dom_info_dict['tx2power'] = 'N/A'
                xcvr_dom_info_dict['tx3power'] = 'N/A'
                xcvr_dom_info_dict['tx4power'] = 'N/A'
            else:
                dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
                    (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(
                        dom_channel_monitor_raw, 0)
                else:
                    return None

                xcvr_dom_info_dict['tx1power'] = dom_channel_monitor_data['data']['TX1Power']['value']
                xcvr_dom_info_dict['tx2power'] = dom_channel_monitor_data['data']['TX2Power']['value']
                xcvr_dom_info_dict['tx3power'] = dom_channel_monitor_data['data']['TX3Power']['value']
                xcvr_dom_info_dict['tx4power'] = dom_channel_monitor_data['data']['TX4Power']['value']

            if dom_channel_monitor_raw:
                xcvr_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
                xcvr_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']
                xcvr_dom_info_dict['rx1power'] = dom_channel_monitor_data['data']['RX1Power']['value']
                xcvr_dom_info_dict['rx2power'] = dom_channel_monitor_data['data']['RX2Power']['value']
                xcvr_dom_info_dict['rx3power'] = dom_channel_monitor_data['data']['RX3Power']['value']
                xcvr_dom_info_dict['rx4power'] = dom_channel_monitor_data['data']['RX4Power']['value']
                xcvr_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TX1Bias']['value']
                xcvr_dom_info_dict['tx2bias'] = dom_channel_monitor_data['data']['TX2Bias']['value']
                xcvr_dom_info_dict['tx3bias'] = dom_channel_monitor_data['data']['TX3Bias']['value']
                xcvr_dom_info_dict['tx4bias'] = dom_channel_monitor_data['data']['TX4Bias']['value']

        else:
            # SFPs
            offset = 256

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            dom_temperature_raw = self.__read_eeprom_specific_bytes((offset + SFP_TEMPE_OFFSET), SFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
            else:
                return None

            dom_voltage_raw = self.__read_eeprom_specific_bytes((offset + SFP_VOLT_OFFSET), SFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
            else:
                return None

            dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
                (offset + SFP_CHANNL_MON_OFFSET), SFP_CHANNL_MON_WIDTH)
            if dom_channel_monitor_raw is not None:
                dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
            else:
                return None

            xcvr_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            xcvr_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']
            xcvr_dom_info_dict['rx1power'] = dom_channel_monitor_data['data']['RXPower']['value']
            xcvr_dom_info_dict['rx2power'] = 'N/A'
            xcvr_dom_info_dict['rx3power'] = 'N/A'
            xcvr_dom_info_dict['rx4power'] = 'N/A'
            xcvr_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TXBias']['value']
            xcvr_dom_info_dict['tx2bias'] = 'N/A'
            xcvr_dom_info_dict['tx3bias'] = 'N/A'
            xcvr_dom_info_dict['tx4bias'] = 'N/A'
            xcvr_dom_info_dict['tx1power'] = dom_channel_monitor_data['data']['TXPower']['value']
            xcvr_dom_info_dict['tx2power'] = 'N/A'
            xcvr_dom_info_dict['tx3power'] = 'N/A'
            xcvr_dom_info_dict['tx4power'] = 'N/A'

        xcvr_dom_info_dict['rx_los'] = self.get_rx_los()
        xcvr_dom_info_dict['tx_fault'] = self.get_tx_fault()
        xcvr_dom_info_dict['reset_status'] = self.get_reset_status()
        xcvr_dom_info_dict['lp_mode'] = self.get_lpmode()

        return xcvr_dom_info_dict

    def get_transceiver_threshold_info(self):
        """
        Retrieves transceiver threshold info of this SFP
        Returns:
            A dict which contains following keys/values :
        ========================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        temphighalarm              |FLOAT          |High Alarm Threshold value of temperature in Celsius.
        templowalarm               |FLOAT          |Low Alarm Threshold value of temperature in Celsius.
        temphighwarning            |FLOAT          |High Warning Threshold value of temperature in Celsius.
        templowwarning             |FLOAT          |Low Warning Threshold value of temperature in Celsius.
        vcchighalarm               |FLOAT          |High Alarm Threshold value of supply voltage in mV.
        vcclowalarm                |FLOAT          |Low Alarm Threshold value of supply voltage in mV.
        vcchighwarning             |FLOAT          |High Warning Threshold value of supply voltage in mV.
        vcclowwarning              |FLOAT          |Low Warning Threshold value of supply voltage in mV.
        rxpowerhighalarm           |FLOAT          |High Alarm Threshold value of received power in dBm.
        rxpowerlowalarm            |FLOAT          |Low Alarm Threshold value of received power in dBm.
        rxpowerhighwarning         |FLOAT          |High Warning Threshold value of received power in dBm.
        rxpowerlowwarning          |FLOAT          |Low Warning Threshold value of received power in dBm.
        txpowerhighalarm           |FLOAT          |High Alarm Threshold value of transmit power in dBm.
        txpowerlowalarm            |FLOAT          |Low Alarm Threshold value of transmit power in dBm.
        txpowerhighwarning         |FLOAT          |High Warning Threshold value of transmit power in dBm.
        txpowerlowwarning          |FLOAT          |Low Warning Threshold value of transmit power in dBm.
        txbiashighalarm            |FLOAT          |High Alarm Threshold value of tx Bias Current in mA.
        txbiaslowalarm             |FLOAT          |Low Alarm Threshold value of tx Bias Current in mA.
        txbiashighwarning          |FLOAT          |High Warning Threshold value of tx Bias Current in mA.
        txbiaslowwarning           |FLOAT          |Low Warning Threshold value of tx Bias Current in mA.
        ========================================================================
        """
        # check present status
        if not self.get_presence():
            return None

        xcvr_dom_threshold_info_dict = dict.fromkeys(self.threshold_dict_keys, 'N/A')

        if self.is_osfp_port:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            pass
        elif self.is_qsfp_port:
            # QSFPs
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            dom_thres_raw = self.__read_eeprom_specific_bytes(QSFP_MODULE_THRESHOLD_OFFSET, QSFP_MODULE_THRESHOLD_WIDTH)

            if dom_thres_raw:
                module_threshold_values = sfpd_obj.parse_module_threshold_values(
                    dom_thres_raw, 0)
                module_threshold_data = module_threshold_values.get('data')
                if module_threshold_data:
                    xcvr_dom_threshold_info_dict['temphighalarm'] = module_threshold_data['TempHighAlarm']['value']
                    xcvr_dom_threshold_info_dict['templowalarm'] = module_threshold_data['TempLowAlarm']['value']
                    xcvr_dom_threshold_info_dict['temphighwarning'] = module_threshold_data['TempHighWarning']['value']
                    xcvr_dom_threshold_info_dict['templowwarning'] = module_threshold_data['TempLowWarning']['value']
                    xcvr_dom_threshold_info_dict['vcchighalarm'] = module_threshold_data['VccHighAlarm']['value']
                    xcvr_dom_threshold_info_dict['vcclowalarm'] = module_threshold_data['VccLowAlarm']['value']
                    xcvr_dom_threshold_info_dict['vcchighwarning'] = module_threshold_data['VccHighWarning']['value']
                    xcvr_dom_threshold_info_dict['vcclowwarning'] = module_threshold_data['VccLowWarning']['value']

            dom_thres_raw = self.__read_eeprom_specific_bytes(
                QSFP_CHANNEL_THRESHOLD_OFFSET, QSFP_CHANNEL_THRESHOLD_WIDTH)
            if dom_thres_raw:
                channel_threshold_values = sfpd_obj.parse_channel_threshold_values(
                    dom_thres_raw, 0)
                channel_threshold_data = channel_threshold_values.get('data')
                if channel_threshold_data:
                    xcvr_dom_threshold_info_dict['rxpowerhighalarm'] = channel_threshold_data['RxPowerHighAlarm']['value']
                    xcvr_dom_threshold_info_dict['rxpowerlowalarm'] = channel_threshold_data['RxPowerLowAlarm']['value']
                    xcvr_dom_threshold_info_dict['rxpowerhighwarning'] = channel_threshold_data['RxPowerHighWarning']['value']
                    xcvr_dom_threshold_info_dict['rxpowerlowwarning'] = channel_threshold_data['RxPowerLowWarning']['value']
                    xcvr_dom_threshold_info_dict['txpowerhighalarm'] = "0.0dBm"
                    xcvr_dom_threshold_info_dict['txpowerlowalarm'] = "0.0dBm"
                    xcvr_dom_threshold_info_dict['txpowerhighwarning'] = "0.0dBm"
                    xcvr_dom_threshold_info_dict['txpowerlowwarning'] = "0.0dBm"
                    xcvr_dom_threshold_info_dict['txbiashighalarm'] = channel_threshold_data['TxBiasHighAlarm']['value']
                    xcvr_dom_threshold_info_dict['txbiaslowalarm'] = channel_threshold_data['TxBiasLowAlarm']['value']
                    xcvr_dom_threshold_info_dict['txbiashighwarning'] = channel_threshold_data['TxBiasHighWarning']['value']
                    xcvr_dom_threshold_info_dict['txbiaslowwarning'] = channel_threshold_data['TxBiasLowWarning']['value']

        else:
            # SFPs
            sfpd_obj = sff8472Dom()
            offset = 256
            eeprom_ifraw = self.__read_eeprom_specific_bytes(0, offset)
            sfpi_obj = sff8472InterfaceId(eeprom_ifraw)
            cal_type = sfpi_obj.get_calibration_type()
            sfpd_obj._calibration_type = cal_type

            dom_module_threshold_raw = self.__read_eeprom_specific_bytes(
                (offset + SFP_MODULE_THRESHOLD_OFFSET), SFP_MODULE_THRESHOLD_WIDTH)
            if dom_module_threshold_raw is not None:
                dom_module_threshold_data = sfpd_obj.parse_alarm_warning_threshold(
                    dom_module_threshold_raw, 0)

                xcvr_dom_threshold_info_dict['temphighalarm'] = dom_module_threshold_data['data']['TempHighAlarm']['value']
                xcvr_dom_threshold_info_dict['templowalarm'] = dom_module_threshold_data['data']['TempLowAlarm']['value']
                xcvr_dom_threshold_info_dict['temphighwarning'] = dom_module_threshold_data['data']['TempHighWarning']['value']
                xcvr_dom_threshold_info_dict['templowwarning'] = dom_module_threshold_data['data']['TempLowWarning']['value']
                xcvr_dom_threshold_info_dict['vcchighalarm'] = dom_module_threshold_data['data']['VoltageHighAlarm']['value']
                xcvr_dom_threshold_info_dict['vcclowalarm'] = dom_module_threshold_data['data']['VoltageLowAlarm']['value']
                xcvr_dom_threshold_info_dict['vcchighwarning'] = dom_module_threshold_data[
                    'data']['VoltageHighWarning']['value']
                xcvr_dom_threshold_info_dict['vcclowwarning'] = dom_module_threshold_data['data']['VoltageLowWarning']['value']
                xcvr_dom_threshold_info_dict['txbiashighalarm'] = dom_module_threshold_data['data']['BiasHighAlarm']['value']
                xcvr_dom_threshold_info_dict['txbiaslowalarm'] = dom_module_threshold_data['data']['BiasLowAlarm']['value']
                xcvr_dom_threshold_info_dict['txbiashighwarning'] = dom_module_threshold_data['data']['BiasHighWarning']['value']
                xcvr_dom_threshold_info_dict['txbiaslowwarning'] = dom_module_threshold_data['data']['BiasLowWarning']['value']
                xcvr_dom_threshold_info_dict['txpowerhighalarm'] = dom_module_threshold_data['data']['TXPowerHighAlarm']['value']
                xcvr_dom_threshold_info_dict['txpowerlowalarm'] = dom_module_threshold_data['data']['TXPowerLowAlarm']['value']
                xcvr_dom_threshold_info_dict['txpowerhighwarning'] = dom_module_threshold_data['data']['TXPowerHighWarning']['value']
                xcvr_dom_threshold_info_dict['txpowerlowwarning'] = dom_module_threshold_data['data']['TXPowerLowWarning']['value']
                xcvr_dom_threshold_info_dict['rxpowerhighalarm'] = dom_module_threshold_data['data']['RXPowerHighAlarm']['value']
                xcvr_dom_threshold_info_dict['rxpowerlowalarm'] = dom_module_threshold_data['data']['RXPowerLowAlarm']['value']
                xcvr_dom_threshold_info_dict['rxpowerhighwarning'] = dom_module_threshold_data['data']['RXPowerHighWarning']['value']
                xcvr_dom_threshold_info_dict['rxpowerlowwarning'] = dom_module_threshold_data['data']['RXPowerLowWarning']['value']

        return xcvr_dom_threshold_info_dict

    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        reset_status = None
        if not self.get_presence():
            return reset_status

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_reset')
        if not output:
            return False

        status = int(output['status'].rstrip())

        if status == 1:
            reset_status = True
        else:
            reset_status = False

        return reset_status

    def get_rx_los(self):
        """
        Retrieves the RX LOS (lost-of-signal) status of SFP
        Returns:
            A Boolean, True if SFP has RX LOS, False if not.
            Note : RX LOS status is latched until a call to get_rx_los or a reset.
        """
        rx_los = None
        if not self.get_presence():
            return rx_los

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_rxlos')

        if not output:
            # read the values from EEPROM
            if self.is_osfp_port:
                pass
            elif self.is_qsfp_port:
                rx_los_list = []
                dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
                    QSFP_CHANNL_RX_LOS_STATUS_OFFSET, QSFP_CHANNL_RX_LOS_STATUS_WIDTH) if self.get_presence() else None
                if dom_channel_monitor_raw is not None:
                    rx_los_data = int(dom_channel_monitor_raw[0], 16)
                    rx_los_list.append(rx_los_data & 0x01 != 0)
                    rx_los_list.append(rx_los_data & 0x02 != 0)
                    rx_los_list.append(rx_los_data & 0x04 != 0)
                    rx_los_list.append(rx_los_data & 0x08 != 0)
                    rx_los = rx_los_list[0] and rx_los_list[1] and rx_los_list[2] and rx_los_list[3]
            else:
                # SFP ports
                status_control_raw = self.__read_eeprom_specific_bytes(
                    SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
                if status_control_raw:
                    data = int(status_control_raw[0], 16)
                    rx_los = (sffbase().test_bit(data, 1) != 0)

        else:
            status = int(output['status'].rstrip())

            if status == 1:
                rx_los = True
            else:
                rx_los = False

        return rx_los

    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP
        Returns:
            A Boolean, True if SFP has TX fault, False if not
            Note : TX fault status is lached until a call to get_tx_fault or a reset.
        """
        tx_fault = None
        if not self.get_presence():
            return tx_fault

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_txfault')

        if not output:
            # read the values from EEPROM
            if self.is_osfp_port:
                pass
            elif self.is_qsfp_port:
                tx_fault_list = []
                dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
                    QSFP_CHANNL_TX_FAULT_STATUS_OFFSET, QSFP_CHANNL_TX_FAULT_STATUS_WIDTH) if self.get_presence() else None
                if dom_channel_monitor_raw is not None:
                    tx_fault_data = int(dom_channel_monitor_raw[0], 16)
                    tx_fault_list.append(tx_fault_data & 0x01 != 0)
                    tx_fault_list.append(tx_fault_data & 0x02 != 0)
                    tx_fault_list.append(tx_fault_data & 0x04 != 0)
                    tx_fault_list.append(tx_fault_data & 0x08 != 0)
                    tx_fault = tx_fault_list[0] and tx_fault_list[1] and tx_fault_list[2] and tx_fault_list[3]
            else:
                # SFP
                status_control_raw = self.__read_eeprom_specific_bytes(
                    SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
                if status_control_raw:
                    data = int(status_control_raw[0], 16)
                    tx_fault = (sffbase().test_bit(data, 2) != 0)
        else:
            status = int(output['status'].rstrip())

            if status == 1:
                tx_fault = True
            else:
                tx_fault = False

        return tx_fault

    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP
        Returns:
            A Boolean, True if tx_disable is enabled, False if disabled
        """
        tx_disable = False
        if not self.get_presence():
            return tx_disable

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_txdisable')

        if not output:
            # read the values from EEPROM
            if self.is_osfp_port:
                return tx_disable
            elif self.is_qsfp_port:
                tx_disable_list = []

                sfpd_obj = sff8436Dom()
                if sfpd_obj is None:
                    return False

                dom_control_raw = self.__read_eeprom_specific_bytes(
                    QSFP_CONTROL_OFFSET, QSFP_CONTROL_WIDTH) if self.get_presence() else None
                if dom_control_raw is not None:
                    dom_control_data = sfpd_obj.parse_control_bytes(dom_control_raw, 0)
                    tx_disable_list.append(
                        'On' == dom_control_data['data']['TX1Disable']['value'])
                    tx_disable_list.append(
                        'On' == dom_control_data['data']['TX2Disable']['value'])
                    tx_disable_list.append(
                        'On' == dom_control_data['data']['TX3Disable']['value'])
                    tx_disable_list.append(
                        'On' == dom_control_data['data']['TX4Disable']['value'])

                return tx_disable_list
            else:
                status_control_raw = self.__read_eeprom_specific_bytes(
                    SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
                if status_control_raw:
                    data = int(status_control_raw[0], 16)
                    tx_disable_hard = (sffbase().test_bit(
                        data, SFP_TX_DISABLE_HARD_BIT) != 0)
                    tx_disable_soft = (sffbase().test_bit(
                        data, SFP_TX_DISABLE_SOFT_BIT) != 0)
                    tx_disable = tx_disable_hard | tx_disable_soft

                return tx_disable
        else:
            status = int(output['status'].rstrip())

            if status == 1:
                tx_disable = True
            else:
                tx_disable = False

        return tx_disable

    def get_tx_disable_channel(self):
        """
        Retrieves the TX disabled channels in this SFP
        Returns:
            A hex of 4 bits (bit 0 to bit 3 as channel 0 to channel 3) to represent
            TX channels which have been disabled in this SFP.
            As an example, a returned value of 0x5 indicates that channel 0
            and channel 2 have been disabled.
        """
        if not self.get_presence():
            return 0

        if self.is_osfp_port:
            return 0
        elif self.is_qsfp_port:
            tx_disable_list = self.get_tx_disable()
            if tx_disable_list is None:
                return 0
            tx_disabled = 0
            for i in range(len(tx_disable_list)):
                if tx_disable_list[i]:
                    tx_disabled |= 1 << i
            return tx_disabled
        else:
            # SFP doesnt support this
            return 0

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        lpmode = False
        if not self.get_presence():
            return lpmode

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_lpmode')

        if not output:
            # Read from EEPROM
            if self.is_osfp_port:
                pass
            elif self.is_qsfp_port:
                try:
                    eeprom = None
                    ctype = self.get_connector_type()
                    if ctype in ['Copper pigtail', 'No separable connector']:
                        return False

                    eeprom = open(self.eeprom_path, "rb")
                    eeprom.seek(93)
                    status = ord(eeprom.read(1))

                    if ((status & 0x3) == 0x3):
                        # Low Power Mode if "Power override" bit is 1 and "Power set" bit is 1
                        lpmode = True
                    else:
                        # High Power Mode if one of the following conditions is matched:
                        # 1. "Power override" bit is 0
                        # 2. "Power override" bit is 1 and "Power set" bit is 0
                        lpmode = False
                except IOError as e:
                    print("Error: unable to open file: %s" % str(e))
                    return False
                finally:
                    if eeprom is not None:
                        eeprom.close()
                        time.sleep(0.01)
            else:
                # SFP
                pass
        else:
            status = int(output['status'].rstrip())

            if status == 1:
                lpmode = True
            else:
                lpmode = False

        return lpmode

    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP
        Returns:
            A Boolean, True if power-override is enabled, False if disabled
        """
        power_override = False
        if not self.get_presence():
            return power_override

        if self.is_osfp_port:
            pass
        elif self.is_qsfp_port:
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return False

            dom_control_raw = self.__read_eeprom_specific_bytes(
                QSFP_CONTROL_OFFSET, QSFP_CONTROL_WIDTH) if self.get_presence() else None
            if dom_control_raw is not None:
                dom_control_data = sfpd_obj.parse_control_bytes(dom_control_raw, 0)
                power_override = ('On' == dom_control_data['data']['PowerOverride']['value'])
        else:
            # SFP doesnt suppor this
            pass

        return power_override

    def get_temperature(self):
        """
        Retrieves the temperature of this SFP
        Returns:
            An integer number of current temperature in Celsius
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        if transceiver_dom_info_dict is not None:
            # returns None if temperature is not found in the dictionary
            return transceiver_dom_info_dict.get("temperature")
        else:
            return None

    def get_voltage(self):
        """
        Retrieves the supply voltage of this SFP
        Returns:
            An integer number of supply voltage in mV
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        # returns None if voltage is not found in the dictionary
        if transceiver_dom_info_dict is not None:
            return transceiver_dom_info_dict.get("voltage")
        else:
            return None

    def get_tx_bias(self):
        """
        Retrieves the TX bias current of this SFP
        Returns:
            A list of four integer numbers, representing TX bias in mA
            for channel 0 to channel 4.
            Ex. ['110.09', '111.12', '108.21', '112.09']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        if transceiver_dom_info_dict is not None:
            tx1_bs = transceiver_dom_info_dict.get("tx1bias", "N/A")
            tx2_bs = transceiver_dom_info_dict.get("tx2bias", "N/A")
            tx3_bs = transceiver_dom_info_dict.get("tx3bias", "N/A")
            tx4_bs = transceiver_dom_info_dict.get("tx4bias", "N/A")
            return [tx1_bs, tx2_bs, tx3_bs, tx4_bs] if transceiver_dom_info_dict else []
        else:
            return None

    def get_rx_power(self):
        """
        Retrieves the received optical power for this SFP
        Returns:
            A list of four integer numbers, representing received optical
            power in mW for channel 0 to channel 4.
            Ex. ['1.77', '1.71', '1.68', '1.70']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        if transceiver_dom_info_dict is not None:
            rx1_pw = transceiver_dom_info_dict.get("rx1power", "N/A")
            rx2_pw = transceiver_dom_info_dict.get("rx2power", "N/A")
            rx3_pw = transceiver_dom_info_dict.get("rx3power", "N/A")
            rx4_pw = transceiver_dom_info_dict.get("rx4power", "N/A")
            return [rx1_pw, rx2_pw, rx3_pw, rx4_pw] if transceiver_dom_info_dict else []
        else:
            return None

    def get_tx_power(self):
        """
        Retrieves the TX power of this SFP
        Returns:
            A list of four integer numbers, representing TX power in mW
            for channel 0 to channel 4.
            Ex. ['1.86', '1.86', '1.86', '1.86']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        if transceiver_dom_info_dict is not None:
            tx1_pw = transceiver_dom_info_dict.get("tx1power", "N/A")
            tx2_pw = transceiver_dom_info_dict.get("tx2power", "N/A")
            tx3_pw = transceiver_dom_info_dict.get("tx3power", "N/A")
            tx4_pw = transceiver_dom_info_dict.get("tx4power", "N/A")
            return [tx1_pw, tx2_pw, tx3_pw, tx4_pw]
        else:
            return None

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        status = False
        if not self.get_presence():
            return status

        device = 'PORT{}'.format(self.port_index)
        # TODO: Implement a wrapper set function to write the sequence
        path = self.pddf_obj.get_path(device, 'xcvr_reset')

        # TODO: put the optic based reset logic using EEPROM
        if path is None:
            pass
        else:
            try:
                f = open(path, 'r+')
            except IOError as e:
                return False

            try:
                f.seek(0)
                f.write('1')
                time.sleep(1)
                f.seek(0)
                f.write('0')

                f.close()
                status = True
            except IOError as e:
                status = False

        return status

    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels
        Args:
            tx_disable : A Boolean, True to enable tx_disable mode, False to disable
                         tx_disable mode.
        Returns:
            A boolean, True if tx_disable is set successfully, False if not
        """
        # find out a generic implementation of tx_disable for SFP, QSFP and OSFP
        status = False
        if not self.get_presence():
            return tx_disable

        device = 'PORT{}'.format(self.port_index)
        path = self.pddf_obj.get_path(device, 'xcvr_txdisable')

        # TODO: put the optic based reset logic using EEPROM
        if path is None:
            if self.is_osfp_port:
                pass
            elif self.is_qsfp_port:
                eeprom_f = None
                try:
                    txdisable_ctl = 0xf if tx_disable else 0x0
                    buf = create_string_buffer(1)
                    buf[0] = chr(txdisable_ctl)
                    # Write to eeprom
                    eeprom_f = open(self.eeprom_path, "r+b")
                    eeprom_f.seek(QSFP_CONTROL_OFFSET)
                    eeprom_f.write(buf[0])
                except IOError as e:
                    print("Error: unable to open file: %s" % str(e))
                    return False
                finally:
                    if eeprom_f is not None:
                        eeprom_f.close()
                        time.sleep(0.01)

                    status = True
            else:
                status_control_raw = self.__read_eeprom_specific_bytes(
                    SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
                if status_control_raw is not None:
                    # Set bit 6 for Soft TX Disable Select
                    # 01000000 = 64 and 10111111 = 191
                    txdisable_bit = 64 if tx_disable else 191
                    status_control = int(status_control_raw[0], 16)
                    txdisable_ctl = (status_control | txdisable_bit) if tx_disable else (
                        status_control & txdisable_bit)
                    try:
                        eeprom_f = open(self.eeprom_path, mode="r+b", buffering=0)
                        buf = create_string_buffer(1)
                        buf[0] = chr(txdisable_ctl)
                        # Write to eeprom
                        eeprom_f.seek(SFP_STATUS_CONTROL_OFFSET)
                        eeprom_f.write(buf[0])
                    except Exception as e:
                        print(("Error: unable to open file: %s" % str(e)))
                        return False
                    finally:
                        if eeprom_f:
                            eeprom_f.close()
                            time.sleep(0.01)
                        status = True
        else:
            try:
                f = open(path, 'r+')
            except IOError as e:
                return False

            try:
                if tx_disable:
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                status = True
            except IOError as e:
                status = False

        return status

    def tx_disable_channel(self, channel, disable):
        """
        Sets the tx_disable for specified SFP channels
        Args:
            channel : A hex of 4 bits (bit 0 to bit 3) which represent channel 0 to 3,
                      e.g. 0x5 for channel 0 and channel 2.
            disable : A boolean, True to disable TX channels specified in channel,
                      False to enable
        Returns:
            A boolean, True if successful, False if not
        """
        # TODO: find a implementation
        status = False
        if not self.get_presence():
            return status

        if self.is_osfp_port:
            pass
        elif self.is_qsfp_port:
            eeprom_f = None
            try:
                channel_state = self.get_tx_disable_channel()
                txdisable_ctl = (channel_state | channel) if disable else (channel_state & ~channel)
                buf = create_string_buffer(1)
                buf[0] = chr(txdisable_ctl)
                # Write to eeprom
                eeprom_f = open(self.eeprom_path, "r+b")
                eeprom_f.seek(QSFP_CONTROL_OFFSET)
                eeprom_f.write(buf[0])
            except IOError as e:
                print("Error: unable to open file: %s" % str(e))
                return False
            finally:
                if eeprom_f is not None:
                    eeprom_f.close()
                    time.sleep(0.01)
                status = True
        else:
            pass

        return status

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override
        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        status = False
        if not self.get_presence():
            return status

        device = 'PORT{}'.format(self.port_index)
        path = self.pddf_obj.get_path(device, 'xcvr_lpmode')

        # TODO: put the optic based reset logic using EEPROM
        if path is None:
            if self.is_osfp_port:
                pass
            elif self.is_qsfp_port:
                try:
                    eeprom_f = None
                    ctype = self.get_connector_type()
                    if ctype in ['Copper pigtail', 'No separable connector']:
                        return False

                    # Fill in write buffer
                    regval = 0x3 if lpmode else 0x1  # 0x3:Low Power Mode, 0x1:High Power Mode
                    buffer = create_string_buffer(1)
                    buffer[0] = chr(regval)

                    # Write to eeprom
                    eeprom_f = open(self.eeprom_path, "r+b")
                    eeprom_f.seek(93)
                    eeprom_f.write(buffer[0])
                    return True
                except IOError as e:
                    print("Error: unable to open file: %s" % str(e))
                    return False
                finally:
                    if eeprom_f is not None:
                        eeprom_f.close()
                        time.sleep(0.01)
            else:
                pass

        else:
            try:
                f = open(path, 'r+')
            except IOError as e:
                return False

            try:
                if lpmode:
                    f.write('1')
                else:
                    f.write('0')

                f.close()
                status = True
            except IOError as e:
                status = False

        return status

    def set_power_override(self, power_override, power_set):
        """
        Sets SFP power level using power_override and power_set
        Args:
            power_override :
                    A Boolean, True to override set_lpmode and use power_set
                    to control SFP power, False to disable SFP power control
                    through power_override/power_set and use set_lpmode
                    to control SFP power.
            power_set :
                    Only valid when power_override is True.
                    A Boolean, True to set SFP to low power mode, False to set
                    SFP to high power mode.
        Returns:
            A boolean, True if power-override and power_set are set successfully,
            False if not
        """
        status = False
        if not self.get_presence():
            return status

        if self.is_osfp_port:
            pass
        elif self.is_qsfp_port:
            try:
                power_override_bit = 0
                if power_override:
                    power_override_bit |= 1 << 0

                power_set_bit = 0
                if power_set:
                    power_set_bit |= 1 << 1

                buffer = create_string_buffer(1)
                buffer[0] = chr(power_override_bit | power_set_bit)
                # Write to eeprom
                eeprom_f = open(self.eeprom_path, "r+b")
                eeprom_f.seek(QSFP_POWEROVERRIDE_OFFSET)
                eeprom_f.write(buffer[0])
            except IOError as e:
                print("Error: unable to open file: %s" % str(e))
                return False
            finally:
                if eeprom_f is not None:
                    eeprom_f.close()
                    time.sleep(0.01)
                return True
        else:
            pass

        return status

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        # Name of the port/sfp ?
        return 'PORT{}'.format(self.port_index)

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        output = self.pddf_obj.get_attr_name_output(self.device, 'xcvr_present')
        if not output:
            return False

        mode = output['mode']
        modpres = output['status'].rstrip()
        if 'XCVR' in self.plugin_data:
            if 'xcvr_present' in self.plugin_data['XCVR']:
                ptype = self.sfp_type
                vtype = 'valmap-'+ptype
                if vtype in self.plugin_data['XCVR']['xcvr_present'][mode]:
                    vmap = self.plugin_data['XCVR']['xcvr_present'][mode][vtype]
                    if modpres in vmap:
                        return vmap[modpres]
                    else:
                        return False
        # if self.plugin_data doesn't specify anything regarding Transceivers
        if modpres == '1':
            return True

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_info()
        if transceiver_dom_info_dict is not None:
            return transceiver_dom_info_dict.get("model", "N/A")
        else:
            return None

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_info()
        if transceiver_dom_info_dict is not None:
            return transceiver_dom_info_dict.get("serial", "N/A")
        else:
            return None

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence() and self.get_transceiver_bulk_status()

    def get_connector_type(self):
        """
        Retrieves the device connector type
        Returns:
            enum: connector_code
        """
        transceiver_dom_info_dict = self.get_transceiver_info()
        if transceiver_dom_info_dict is not None:
            return transceiver_dom_info_dict.get("connector", "N/A")
        else:
            return None

    def get_transceiver_change_event(self):
        """
        TODO: This function need to be implemented
        when decide to support monitoring SFP(Xcvrd)
        on this platform.
        """
        raise NotImplementedError

    def dump_sysfs(self):
        return self.pddf_obj.cli_dump_dsysfs('xcvr')
