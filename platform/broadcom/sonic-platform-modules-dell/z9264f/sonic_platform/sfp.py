#!/usr/bin/env python

#############################################################################
# DELLEMC
#
# Module contains an implementation of SONiC Platform Base API and
# provides the platform information
#
#############################################################################

try:
    import os
    import time
    import struct
    import sys
    import getopt
    import select
    import mmap
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform_base.sfp_base import SfpBase
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472InterfaceId
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472Dom
    from sonic_platform_base.sonic_sfp.sff8472 import sffbase

except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PAGE_OFFSET = 0
KEY_OFFSET = 1
KEY_WIDTH = 2
FUNC_NAME = 3

QSFP_INFO_OFFSET = 128
QSFP_DOM_OFFSET = 0
QSFP_DOM_OFFSET1 = 384

SFP_INFO_OFFSET = 0
SFP_DOM_OFFSET = 256

SFP_STATUS_CONTROL_OFFSET = 110
SFP_STATUS_CONTROL_WIDTH = 7
SFP_TX_DISABLE_HARD_BIT = 7
SFP_TX_DISABLE_SOFT_BIT = 6

qsfp_cable_length_tup = ('Length(km)', 'Length OM3(2m)', 'Length OM2(m)',
                    'Length OM1(m)', 'Length Cable Assembly(m)')

qsfp_compliance_code_tup = (
    '10/40G Ethernet Compliance Code',
    'SONET Compliance codes',
    'SAS/SATA compliance codes',
    'Gigabit Ethernet Compliant codes',
    'Fibre Channel link length/Transmitter Technology',
    'Fibre Channel transmission media',
    'Fibre Channel Speed')

sfp_cable_length_tup = ('LengthSMFkm-UnitsOfKm', 'LengthSMF(UnitsOf100m)',
                        'Length50um(UnitsOf10m)', 'Length62.5um(UnitsOfm)',
                        'LengthOM3(UnitsOf10m)', 'LengthCable(UnitsOfm)')

sfp_compliance_code_tup = ('10GEthernetComplianceCode', 'InfinibandComplianceCode',
                           'ESCONComplianceCodes', 'SONETComplianceCodes',
                           'EthernetComplianceCodes', 'FibreChannelLinkLength',
                           'FibreChannelTechnology', 'SFP+CableTechnology',
                           'FibreChannelTransmissionMedia', 'FibreChannelSpeed')

info_dict_keys = ['type', 'hardware_rev', 'serial',
                  'manufacturer', 'model', 'connector',
                  'encoding', 'ext_identifier', 'ext_rateselect_compliance',
                  'cable_type', 'cable_length', 'nominal_bit_rate',
                  'specification_compliance', 'type_abbrv_name','vendor_date', 'vendor_oui']

dom_dict_keys = ['rx_los',       'tx_fault',   'reset_status',
                 'power_lpmode', 'tx_disable', 'tx_disable_channel',
                 'temperature',  'voltage',    'rx1power',
                 'rx2power',     'rx3power',   'rx4power',
                 'tx1bias',      'tx2bias',    'tx3bias',
                 'tx4bias',      'tx1power',   'tx2power',
                 'tx3power',     'tx4power']

threshold_dict_keys = ['temphighalarm',    'temphighwarning',
                       'templowalarm',     'templowwarning',
                       'vcchighalarm',     'vcchighwarning',
                       'vcclowalarm',      'vcclowwarning',
                       'rxpowerhighalarm', 'rxpowerhighwarning',
                       'rxpowerlowalarm',  'rxpowerlowwarning',
                       'txpowerhighalarm', 'txpowerhighwarning',
                       'txpowerlowalarm',  'txpowerlowwarning',
                       'txbiashighalarm',  'txbiashighwarning',
                       'txbiaslowalarm',   'txbiaslowwarning']

sff8436_parser = {
     'reset_status': [QSFP_DOM_OFFSET,   2,  1, 'parse_dom_status_indicator'],
           'rx_los': [QSFP_DOM_OFFSET,   3,  1, 'parse_dom_tx_rx_los'],
         'tx_fault': [QSFP_DOM_OFFSET,   4,  1, 'parse_dom_tx_fault'],
       'tx_disable': [QSFP_DOM_OFFSET,  86,  1, 'parse_dom_tx_disable'],
     'power_lpmode': [QSFP_DOM_OFFSET,  93,  1, 'parse_dom_power_control'],
   'power_override': [QSFP_DOM_OFFSET,  93,  1, 'parse_dom_power_control'],
      'Temperature': [QSFP_DOM_OFFSET,  22,  2, 'parse_temperature'],
          'Voltage': [QSFP_DOM_OFFSET,  26,  2, 'parse_voltage'],
   'ChannelMonitor': [QSFP_DOM_OFFSET,  34, 16, 'parse_channel_monitor_params'],
   'ChannelMonitor_TxPower': 
                     [QSFP_DOM_OFFSET,  34, 24, 'parse_channel_monitor_params_with_tx_power'],

       'cable_type': [QSFP_INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
     'cable_length': [QSFP_INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
        'connector': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
             'type': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
         'encoding': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
   'ext_identifier': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'ext_rateselect_compliance':
                     [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'nominal_bit_rate': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'specification_compliance':
                     [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
  'type_abbrv_name': [QSFP_INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
     'manufacturer': [QSFP_INFO_OFFSET, 20, 16, 'parse_vendor_name'],
       'vendor_oui': [QSFP_INFO_OFFSET, 37,  3, 'parse_vendor_oui'],
            'model': [QSFP_INFO_OFFSET, 40, 16, 'parse_vendor_pn'],
     'hardware_rev': [QSFP_INFO_OFFSET, 56,  2, 'parse_vendor_rev'],
           'serial': [QSFP_INFO_OFFSET, 68, 16, 'parse_vendor_sn'],
      'vendor_date': [QSFP_INFO_OFFSET, 84,  8, 'parse_vendor_date'],
   'dom_capability': [QSFP_INFO_OFFSET, 92,  1, 'parse_qsfp_dom_capability'],
          'dom_rev': [QSFP_DOM_OFFSET,   1,  1, 'parse_sfp_dom_rev'],
  'ModuleThreshold': [QSFP_DOM_OFFSET1, 128, 24, 'parse_module_threshold_values'],
 'ChannelThreshold': [QSFP_DOM_OFFSET1, 176, 16, 'parse_channel_threshold_values'],
}

sff8472_parser = {
      'Temperature': [SFP_DOM_OFFSET,  96,  2, 'parse_temperature'],
          'Voltage': [SFP_DOM_OFFSET,  98,  2, 'parse_voltage'],
   'ChannelMonitor': [SFP_DOM_OFFSET,  100, 6, 'parse_channel_monitor_params'],

       'cable_type': [SFP_INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
     'cable_length': [SFP_INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
        'connector': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
             'type': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
         'encoding': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
   'ext_identifier': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
 'ext_rateselect_compliance':
                     [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
 'nominal_bit_rate': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
 'specification_compliance':
                     [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
  'type_abbrv_name': [SFP_INFO_OFFSET,  0, 21, 'parse_sfp_info_bulk'],
     'manufacturer': [SFP_INFO_OFFSET, 20, 16, 'parse_vendor_name'],
       'vendor_oui': [SFP_INFO_OFFSET,  37, 3, 'parse_vendor_oui'],
            'model': [SFP_INFO_OFFSET, 40, 16, 'parse_vendor_pn'],
     'hardware_rev': [SFP_INFO_OFFSET, 56,  4, 'parse_vendor_rev'],
           'serial': [SFP_INFO_OFFSET, 68, 16, 'parse_vendor_sn'],
      'vendor_date': [SFP_INFO_OFFSET, 84,  8, 'parse_vendor_date'],
  'ModuleThreshold': [SFP_DOM_OFFSET,   0, 56, 'parse_alarm_warning_threshold'],
}


class Sfp(SfpBase):
    """
    DELLEMC Platform-specific Sfp class
    """
    BASE_RES_PATH = "/sys/bus/pci/devices/0000:04:00.0/resource0"
    OIR_FD_PATH = "/sys/bus/pci/devices/0000:04:00.0/port_msi"

    def __init__(self, index, sfp_type, eeprom_path):
        SfpBase.__init__(self)
        self.sfp_type = sfp_type
        self.index = index
        self.eeprom_path = eeprom_path
        self.qsfpInfo = sff8436InterfaceId()
        self.qsfpDomInfo = sff8436Dom()
        self.sfpInfo = sff8472InterfaceId()
        self.sfpDomInfo = sff8472Dom(None,1)

    def pci_mem_read(self, mm, offset):
        mm.seek(offset)
        read_data_stream = mm.read(4)
        reg_val = struct.unpack('I', read_data_stream)
        mem_val = str(reg_val)[1:-2]
        # print "reg_val read:%x"%reg_val
        return mem_val

    def pci_mem_write(self, mm, offset, data):
        mm.seek(offset)
        # print "data to write:%x"%data
        mm.write(struct.pack('I', data))

    def pci_set_value(self, resource, val, offset):
        fd = os.open(resource, os.O_RDWR)
        mm = mmap.mmap(fd, 0)
        val = self.pci_mem_write(mm, offset, val)
        mm.close()
        os.close(fd)
        return val

    def pci_get_value(self, resource, offset):
        fd = os.open(resource, os.O_RDWR)
        mm = mmap.mmap(fd, 0)
        val = self.pci_mem_read(mm, offset)
        mm.close()
        os.close(fd)
        return val

    def _read_eeprom_bytes(self, eeprom_path, offset, num_bytes):
        eeprom_raw = []
        try:
            eeprom = open(eeprom_path, mode="rb", buffering=0)
        except IOError:
            return None

        for i in range(0, num_bytes):
            eeprom_raw.append("0x00")

        try:
            eeprom.seek(offset)
            raw = eeprom.read(num_bytes)
        except IOError:
            eeprom.close()
            return None

        try:
            for n in range(0, num_bytes):
                eeprom_raw[n] = hex(ord(raw[n]))[2:].zfill(2)
        except BaseException:
            eeprom.close()
            return None

        eeprom.close()
        return eeprom_raw

    def _get_eeprom_data(self, eeprom_key):
        eeprom_data = None
        page_offset = None

        if(self.sfp_type == 'QSFP'):
            page_offset = sff8436_parser[eeprom_key][PAGE_OFFSET]
            eeprom_data_raw = self._read_eeprom_bytes(
                self.eeprom_path,
                (sff8436_parser[eeprom_key][PAGE_OFFSET] +
                 sff8436_parser[eeprom_key][KEY_OFFSET]),
                 sff8436_parser[eeprom_key][KEY_WIDTH])
            if (eeprom_data_raw is not None):
                # Offset 128 is used to retrieve sff8436InterfaceId Info
                # Offset 0 is used to retrieve sff8436Dom Info
                if (page_offset == 128):
                    if ( self.qsfpInfo is None):
                        return None
                    eeprom_data = getattr(
                        self.qsfpInfo, sff8436_parser[eeprom_key][FUNC_NAME])(
                        eeprom_data_raw, 0)
                else:
                    if ( self.qsfpDomInfo is None):
                        return None
                    eeprom_data = getattr(
                        self.qsfpDomInfo, sff8436_parser[eeprom_key][FUNC_NAME])(
                        eeprom_data_raw, 0)
        else:
            page_offset = sff8472_parser[eeprom_key][PAGE_OFFSET]
            eeprom_data_raw = self._read_eeprom_bytes(
                self.eeprom_path,
                (sff8472_parser[eeprom_key][PAGE_OFFSET] +
                 sff8472_parser[eeprom_key][KEY_OFFSET]),
                 sff8472_parser[eeprom_key][KEY_WIDTH])
            if (eeprom_data_raw is not None):
                # Offset 0 is used to retrieve sff8472InterfaceId Info
                # Offset 256 is used to retrieve sff8472Dom Info
                if (page_offset == 0):
                    if ( self.sfpInfo is None):
                        return None
                    eeprom_data = getattr(
                        self.sfpInfo, sff8472_parser[eeprom_key][FUNC_NAME])(
                        eeprom_data_raw, 0)
                else:
                    if ( self.sfpDomInfo is None):
                        return None
                    eeprom_data = getattr(
                        self.sfpDomInfo, sff8472_parser[eeprom_key][FUNC_NAME])(
                        eeprom_data_raw, 0)

        return eeprom_data

    def get_transceiver_info(self):
        """
        Retrieves transceiver info of this SFP
        """
        transceiver_info_dict = {}
        compliance_code_dict = {}
        transceiver_info_dict = dict.fromkeys(info_dict_keys, 'N/A')
        # BaseInformation
        iface_data = self._get_eeprom_data('type')
        if (iface_data is not None):
            connector = iface_data['data']['Connector']['value']
            encoding = iface_data['data']['EncodingCodes']['value']
            ext_id = iface_data['data']['Extended Identifier']['value']
            rate_identifier = iface_data['data']['RateIdentifier']['value']
            identifier = iface_data['data']['type']['value']
            type_abbrv_name=iface_data['data']['type_abbrv_name']['value']
            if(self.sfp_type == 'QSFP'):
                bit_rate = str(
                    iface_data['data']['Nominal Bit Rate(100Mbs)']['value'])
                for key in qsfp_compliance_code_tup:
                    if key in iface_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = iface_data['data']['Specification compliance']['value'][key]['value']
                for key in qsfp_cable_length_tup:
                    if key in iface_data['data']:
                        cable_type = key
                        cable_length = str(iface_data['data'][key]['value'])
            else:
                bit_rate = str(
                    iface_data['data']['NominalSignallingRate(UnitsOf100Mbd)']['value'])
                for key in sfp_compliance_code_tup:
                    if key in iface_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = iface_data['data']['Specification compliance']['value'][key]['value']
                for key in sfp_cable_length_tup:
                    if key in iface_data['data']:
                        cable_type = key
                        cable_length = str(iface_data['data'][key]['value'])
        else:
            return transceiver_info_dict

        # Vendor Date
        vendor_date_data = self._get_eeprom_data('vendor_date')
        if (vendor_date_data is not None):
            vendor_date = vendor_date_data['data']['VendorDataCode(YYYY-MM-DD Lot)']['value']
        else:
            return transceiver_info_dict

        # Vendor Name
        vendor_name_data = self._get_eeprom_data('manufacturer')
        if (vendor_name_data is not None):
            vendor_name = vendor_name_data['data']['Vendor Name']['value']
        else:
            return transceiver_info_dict

        # Vendor OUI
        vendor_oui_data = self._get_eeprom_data('vendor_oui')
        if (vendor_oui_data is not None):
            vendor_oui = vendor_oui_data['data']['Vendor OUI']['value']
        else:
            return transceiver_info_dict

        # Vendor PN
        vendor_pn_data = self._get_eeprom_data('model')
        if (vendor_pn_data is not None):
            vendor_pn = vendor_pn_data['data']['Vendor PN']['value']
        else:
            return transceiver_info_dict

        # Vendor Revision
        vendor_rev_data = self._get_eeprom_data('hardware_rev')
        if (vendor_rev_data is not None):
            vendor_rev = vendor_rev_data['data']['Vendor Rev']['value']
        else:
            return transceiver_info_dict

        # Vendor Serial Number
        vendor_sn_data = self._get_eeprom_data('serial')
        if (vendor_sn_data is not None):
            vendor_sn = vendor_sn_data['data']['Vendor SN']['value']
        else:
            return transceiver_info_dict

        # Fill The Dictionary and return
        transceiver_info_dict['type'] = identifier
        transceiver_info_dict['hardware_rev'] = vendor_rev
        transceiver_info_dict['serial'] = vendor_sn
        transceiver_info_dict['manufacturer'] = vendor_name
        transceiver_info_dict['model'] = vendor_pn
        transceiver_info_dict['connector'] = connector
        transceiver_info_dict['encoding'] = encoding
        transceiver_info_dict['ext_identifier'] = ext_id
        transceiver_info_dict['ext_rateselect_compliance'] = rate_identifier
        transceiver_info_dict['cable_type'] = cable_type
        transceiver_info_dict['cable_length'] = cable_length
        transceiver_info_dict['nominal_bit_rate'] = bit_rate
        transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)
        transceiver_info_dict['vendor_date'] = vendor_date
        transceiver_info_dict['vendor_oui'] = vendor_oui
        transceiver_info_dict['type_abbrv_name']=type_abbrv_name

        return transceiver_info_dict

    def get_transceiver_threshold_info(self):
        """
        Retrieves transceiver threshold info of this SFP
        """
        transceiver_dom_threshold_dict = {}
        transceiver_dom_threshold_dict = dict.fromkeys(
                threshold_dict_keys, 'N/A')

        # Module Threshold
        module_threshold_data = self._get_eeprom_data('ModuleThreshold')
        if (self.sfp_type == 'QSFP'):
            # Channel Threshold
            channel_threshold_data = self._get_eeprom_data('ChannelThreshold')

            if (channel_threshold_data is not None and module_threshold_data is not None):
                transceiver_dom_threshold_dict['temphighalarm'] = module_threshold_data['data']['TempHighAlarm']['value']
                transceiver_dom_threshold_dict['temphighwarning'] = module_threshold_data['data']['TempHighWarning']['value']
                transceiver_dom_threshold_dict['templowalarm'] = module_threshold_data['data']['TempLowAlarm']['value']
                transceiver_dom_threshold_dict['templowwarning'] = module_threshold_data['data']['TempLowWarning']['value']
                transceiver_dom_threshold_dict['vcchighalarm'] = module_threshold_data['data']['VccHighAlarm']['value']
                transceiver_dom_threshold_dict['vcchighwarning'] = module_threshold_data['data']['VccHighWarning']['value']
                transceiver_dom_threshold_dict['vcclowalarm'] = module_threshold_data['data']['VccLowAlarm']['value']
                transceiver_dom_threshold_dict['vcclowwarning'] = module_threshold_data['data']['VccLowWarning']['value']
                transceiver_dom_threshold_dict['rxpowerhighalarm'] = channel_threshold_data['data']['RxPowerHighAlarm']['value']
                transceiver_dom_threshold_dict['rxpowerhighwarning'] = channel_threshold_data['data']['RxPowerHighWarning']['value']
                transceiver_dom_threshold_dict['rxpowerlowalarm'] = channel_threshold_data['data']['RxPowerLowAlarm']['value']
                transceiver_dom_threshold_dict['rxpowerlowwarning'] = channel_threshold_data['data']['RxPowerLowWarning']['value']
                transceiver_dom_threshold_dict['txbiashighalarm'] = channel_threshold_data['data']['TxBiasHighAlarm']['value']
                transceiver_dom_threshold_dict['txbiashighwarning'] = channel_threshold_data['data']['TxBiasHighWarning']['value']
                transceiver_dom_threshold_dict['txbiaslowalarm'] = channel_threshold_data['data']['TxBiasLowAlarm']['value']
                transceiver_dom_threshold_dict['txbiaslowwarning'] = channel_threshold_data['data']['TxBiasLowWarning']['value']

            else:
                return transceiver_dom_threshold_dict
        else:
            #SFP
            if (module_threshold_data is not None):
                #Threshold Data
                transceiver_dom_threshold_dict['temphighalarm'] = module_threshold_data['data']['TempHighAlarm']['value']
                transceiver_dom_threshold_dict['templowalarm'] = module_threshold_data['data']['TempLowAlarm']['value']
                transceiver_dom_threshold_dict['temphighwarning'] = module_threshold_data['data']['TempHighWarning']['value']
                transceiver_dom_threshold_dict['templowwarning'] = module_threshold_data['data']['TempLowWarning']['value']
                transceiver_dom_threshold_dict['vcchighalarm'] = module_threshold_data['data']['VoltageHighAlarm']['value']
                transceiver_dom_threshold_dict['vcclowalarm'] = module_threshold_data['data']['VoltageLowAlarm']['value']
                transceiver_dom_threshold_dict['vcchighwarning'] = module_threshold_data['data']['VoltageHighWarning']['value']
                transceiver_dom_threshold_dict['vcclowwarning'] = module_threshold_data['data']['VoltageLowWarning']['value']
                transceiver_dom_threshold_dict['txbiashighalarm'] = module_threshold_data['data']['BiasHighAlarm']['value']
                transceiver_dom_threshold_dict['txbiaslowalarm'] = module_threshold_data['data']['BiasLowAlarm']['value']
                transceiver_dom_threshold_dict['txbiashighwarning'] = module_threshold_data['data']['BiasHighWarning']['value']
                transceiver_dom_threshold_dict['txbiaslowwarning'] = module_threshold_data['data']['BiasLowWarning']['value']
                transceiver_dom_threshold_dict['txpowerhighalarm'] = module_threshold_data['data']['TXPowerHighAlarm']['value']
                transceiver_dom_threshold_dict['txpowerlowalarm'] = module_threshold_data['data']['TXPowerLowAlarm']['value']
                transceiver_dom_threshold_dict['txpowerhighwarning'] = module_threshold_data['data']['TXPowerHighWarning']['value']
                transceiver_dom_threshold_dict['txpowerlowwarning'] = module_threshold_data['data']['TXPowerLowWarning']['value']
                transceiver_dom_threshold_dict['rxpowerhighalarm'] = module_threshold_data['data']['RXPowerHighAlarm']['value']
                transceiver_dom_threshold_dict['rxpowerlowalarm'] = module_threshold_data['data']['RXPowerLowAlarm']['value']
                transceiver_dom_threshold_dict['rxpowerhighwarning'] = module_threshold_data['data']['RXPowerHighWarning']['value']
                transceiver_dom_threshold_dict['rxpowerlowwarning'] = module_threshold_data['data']['RXPowerLowWarning']['value']
            else:
                return transceiver_dom_threshold_dict

        return transceiver_dom_threshold_dict

    def get_transceiver_bulk_status(self):
        """
        Retrieves transceiver bulk status of this SFP
        """
        tx_bias_list = []
        rx_power_list = []
        transceiver_dom_dict = {}
        transceiver_dom_dict = dict.fromkeys(dom_dict_keys, 'N/A')

        # RxLos
        rx_los = self.get_rx_los()

        # TxFault
        tx_fault = self.get_tx_fault()

        # ResetStatus
        reset_state = self.get_reset_status()

        # LowPower Mode
        lp_mode = self.get_lpmode()

        # TxDisable
        tx_disable = self.get_tx_disable()

        # TxDisable Channel
        tx_disable_channel = self.get_tx_disable_channel()

        # Temperature
        temperature = self.get_temperature()

        # Voltage
        voltage = self.get_voltage()

        # Channel Monitor
        tx_power_list = self.get_tx_power()

        # tx bias
        tx_bias_list = self.get_tx_bias()

        # rx power
        rx_power_list = self.get_rx_power()

        if (len(tx_bias_list) != 0):
            transceiver_dom_dict['tx1bias'] = tx_bias_list[0]
            transceiver_dom_dict['tx2bias'] = tx_bias_list[1]
            transceiver_dom_dict['tx3bias'] = tx_bias_list[2]
            transceiver_dom_dict['tx4bias'] = tx_bias_list[3]

        if (len(rx_power_list) != 0):
            transceiver_dom_dict['rx1power'] = rx_power_list[0]
            transceiver_dom_dict['rx2power'] = rx_power_list[1]
            transceiver_dom_dict['rx3power'] = rx_power_list[2]
            transceiver_dom_dict['rx4power'] = rx_power_list[3]

        if (len(tx_power_list) != 0):
            transceiver_dom_dict['tx1power'] = tx_power_list[0]
            transceiver_dom_dict['tx2power'] = tx_power_list[1]
            transceiver_dom_dict['tx3power'] = tx_power_list[2]
            transceiver_dom_dict['tx4power'] = tx_power_list[3]

        transceiver_dom_dict['rx_los'] = rx_los
        transceiver_dom_dict['tx_fault'] = tx_fault
        transceiver_dom_dict['reset_status'] = reset_state
        transceiver_dom_dict['power_lpmode'] = lp_mode
        transceiver_dom_dict['tx_disable'] = tx_disable
        transceiver_dom_dict['tx_disable_channel'] = tx_disable_channel
        transceiver_dom_dict['temperature'] = temperature
        transceiver_dom_dict['voltage'] = voltage

        return transceiver_dom_dict

    def get_name(self):
        """
        Retrieves the name of the sfp
        Returns : QSFP or QSFP+ or QSFP28
        """

        iface_data = self._get_eeprom_data('type')
        if (iface_data is not None):
            identifier = iface_data['data']['type']['value']
        else:
            return None

        return identifier

    def get_presence(self):
        """
        Retrieves the presence of the sfp
        Returns : True if sfp is present and false if it is absent
        """
        # Check for invalid port_num

        # Port offset starts with 0x4004
        port_offset = 16388 + ((self.index-1) * 16)

        status = self.pci_get_value(self.BASE_RES_PATH, port_offset)
        reg_value = int(status)

        # Absence of status throws error
        if (reg_value == ""):
            return False

        # Mask off 4th bit for presence
        if(self.sfp_type == 'QSFP'):
            mask = (1 << 4)

        # Mask off 1st bit for presence 65,66
        if (self.sfp_type == 'SFP'):
            mask =  (1 << 0)
        # ModPrsL is active low
        if reg_value & mask == 0:
            return True

        return False

    def get_model(self):
        """
        Retrieves the model number (or part number) of the sfp
        """
        vendor_pn_data = self._get_eeprom_data('model')
        if (vendor_pn_data is not None):
            vendor_pn = vendor_pn_data['data']['Vendor PN']['value']
        else:
            return None

        return vendor_pn

    def get_serial(self):
        """
        Retrieves the serial number of the sfp
        """
        vendor_sn_data = self._get_eeprom_data('serial')
        if (vendor_sn_data is not None):
            vendor_sn = vendor_sn_data['data']['Vendor SN']['value']
        else:
            return None

        return vendor_sn

    def get_reset_status(self):
        """
        Retrives the reset status of SFP
        """
        reset_status = False
        if (self.sfp_type == 'QSFP'):
            # Port offset starts with 0x4000
            port_offset = 16384 + ((self.index-1) * 16)

            status = self.pci_get_value(self.BASE_RES_PATH, port_offset)
            reg_value = int(status)

            # Absence of status throws error
            if (reg_value == ""):
                return reset_status

            # Mask off 4th bit for reset status
            mask = (1 << 4)

            if ((reg_value & mask) == 0):
                reset_status = True
            else:
                reset_status = False

        return reset_status

    def get_rx_los(self):
        """
        Retrieves the RX LOS (lost-of-signal) status of SFP
        """
        rx_los = None
        rx_los_list = []
        if (self.sfp_type == 'QSFP'):
            rx_los_data = self._get_eeprom_data('rx_los')
            if (rx_los_data is not None):
                rx_los = rx_los_data['data']['Rx1LOS']['value']
                if (rx_los is 'On'):
                    rx_los_list.append(True)
                else:
                    rx_los_list.append(False)
                rx_los = rx_los_data['data']['Rx2LOS']['value']
                if (rx_los is 'On'):
                    rx_los_list.append(True)
                else:
                    rx_los_list.append(False)
                rx_los = rx_los_data['data']['Rx3LOS']['value']
                if (rx_los is 'On'):
                    rx_los_list.append(True)
                else:
                    rx_los_list.append(False)
                rx_los = rx_los_data['data']['Rx4LOS']['value']
                if (rx_los is 'On'):
                    rx_los_list.append(True)
                else:
                    rx_los_list.append(False)

                if (rx_los_list[0] and rx_los_list[1]
                        and rx_los_list[2] and rx_los_list[3]):
                    rx_los = True
                else:
                    rx_los = False
        else:
            rx_los_data = self._read_eeprom_bytes(self.eeprom_path, SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
            if (rx_los_data is not None):
                data = int(rx_los_data[0], 16)
                rx_los = (sffbase().test_bit(data, 1) != 0)

        return rx_los

    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP
        """
        tx_fault = None
        tx_fault_list = []
        if (self.sfp_type == 'QSFP'):
            tx_fault_data = self._get_eeprom_data('tx_fault')
            if (tx_fault_data is not None):
                tx_fault = tx_fault_data['data']['Tx1Fault']['value']
                if (tx_fault is 'On'):
                    tx_fault_list.append(True)
                else:
                    tx_fault_list.append(False)
                tx_fault = tx_fault_data['data']['Tx2Fault']['value']
                if (tx_fault is 'On'):
                    tx_fault_list.append(True)
                else:
                    tx_fault_list.append(False)
                tx_fault = tx_fault_data['data']['Tx3Fault']['value']
                if (tx_fault is 'On'):
                    tx_fault_list.append(True)
                else:
                    tx_fault_list.append(False)
                tx_fault = tx_fault_data['data']['Tx4Fault']['value']
                if (tx_fault is 'On'):
                    tx_fault_list.append(True)
                else:
                    tx_fault_list.append(False)

                if (tx_fault_list[0] and tx_fault_list[1]
                        and tx_fault_list[2] and tx_fault_list[3]):
                    tx_fault = True
                else:
                    tx_fault = False

        else:
            tx_fault_data = self._read_eeprom_bytes(self.eeprom_path, SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
            if (tx_fault_data is not None):
                data = int(tx_fault_data[0], 16)
                tx_fault = (sffbase().test_bit(data, 2) != 0)

        return tx_fault

    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP
        """
        tx_disable = None
        tx_disable_list = []
        if (self.sfp_type == 'QSFP'):
            tx_disable_data = self._get_eeprom_data('tx_disable')
            if (tx_disable_data is not None):
                tx_disable = tx_disable_data['data']['Tx1Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(True)
                else:
                    tx_disable_list.append(False)
                tx_disable = tx_disable_data['data']['Tx2Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(True)
                else:
                    tx_disable_list.append(False)
                tx_disable = tx_disable_data['data']['Tx3Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(True)
                else:
                    tx_disable_list.append(False)
                tx_disable = tx_disable_data['data']['Tx4Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(True)
                else:
                    tx_disable_list.append(False)

                if (tx_disable_list[0] and tx_disable_list[1]
                        and tx_disable_list[2] and tx_disable_list[3]):
                    tx_disable = True
                else:
                    tx_disable = False

        else:
            tx_disable_data = self._read_eeprom_bytes(self.eeprom_path, SFP_STATUS_CONTROL_OFFSET, SFP_STATUS_CONTROL_WIDTH)
            if (tx_disable_data is not None):
                data = int(tx_disable_data[0], 16)
                tx_disable_hard = (sffbase().test_bit(data, SFP_TX_DISABLE_HARD_BIT) != 0)
                tx_disable_soft = (sffbase().test_bit(data, SFP_TX_DISABLE_SOFT_BIT) != 0)
                tx_disable = tx_disable_hard | tx_disable_soft


        return tx_disable

    def get_tx_disable_channel(self):
        """
        Retrieves the TX disabled channels in this SFP
        """
        tx_disable = None
        tx_disable_list = []
        tx_disable_channel = 0

        if (self.sfp_type == 'QSFP'):
            tx_disable_data = self._get_eeprom_data('tx_disable')
            if (tx_disable_data is not None):
                tx_disable = tx_disable_data['data']['Tx1Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(1)
                else:
                    tx_disable_list.append(0)
                tx_disable = tx_disable_data['data']['Tx2Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(1)
                else:
                    tx_disable_list.append(0)
                tx_disable = tx_disable_data['data']['Tx3Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(1)
                else:
                    tx_disable_list.append(0)
                tx_disable = tx_disable_data['data']['Tx4Disable']['value']
                if (tx_disable is 'On'):
                    tx_disable_list.append(1)
                else:
                    tx_disable_list.append(0)

                bit4 = int(tx_disable_list[3]) * 8
                bit3 = int(tx_disable_list[2]) * 4
                bit2 = int(tx_disable_list[1]) * 2
                bit1 = int(tx_disable_list[0]) * 1

                tx_disable_channel = hex(bit4 + bit3 + bit2 + bit1)

        return tx_disable_channel

    def get_lpmode(self):
        """
        Retrieves the lpmode(low power mode) of this SFP
        """
        lpmode_state = False
        if (self.sfp_type == 'QSFP'):

            # Port offset starts with 0x4000
            port_offset = 16384 + ((self.index-1) * 16)

            status = self.pci_get_value(self.BASE_RES_PATH, port_offset)
            reg_value = int(status)

            # Absence of status throws error
            if (reg_value == ""):
                return lpmode_state

            # Mask off 6th bit for lpmode
            mask = (1 << 6)

            # LPMode is active high
            if reg_value & mask == 0:
                lpmode_state = False
            else:
                lpmode_state = True

        return lpmode_state

    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP
        """
        power_override_state = False

        if (self.sfp_type == 'QSFP'):
            power_override_data = self._get_eeprom_data('power_override')
            if (power_override_data is not None):
                power_override = power_override_data['data']['PowerOverRide']['value']
                if (power_override is 'On'):
                    power_override_state = True
                else:
                    power_override_state = False

        return power_override_state

    def get_temperature(self):
        """
        Retrieves the temperature of this SFP
        """
        temperature = None

        temperature_data = self._get_eeprom_data('Temperature')
        if (temperature_data is not None):
            temperature = temperature_data['data']['Temperature']['value']

        return temperature

    def get_voltage(self):
        """
        Retrieves the supply voltage of this SFP
        """
        voltage = None

        voltage_data = self._get_eeprom_data('Voltage')
        if (voltage_data is not None):
            voltage = voltage_data['data']['Vcc']['value']

        return voltage

    def get_tx_bias(self):
        """
        Retrieves the TX bias current of this SFP
        """
        tx_bias = None
        tx_bias_list = []

        tx_bias_data = self._get_eeprom_data('ChannelMonitor')
        if (tx_bias_data is not None):
            if (self.sfp_type == 'QSFP'):
                tx_bias = tx_bias_data['data']['TX1Bias']['value']
                tx_bias_list.append(tx_bias)
                tx_bias = tx_bias_data['data']['TX2Bias']['value']
                tx_bias_list.append(tx_bias)
                tx_bias = tx_bias_data['data']['TX3Bias']['value']
                tx_bias_list.append(tx_bias)
                tx_bias = tx_bias_data['data']['TX4Bias']['value']
                tx_bias_list.append(tx_bias)
            else:
                tx1_bias = tx_bias_data['data']['TXBias']['value']
                return [tx1_bias, "N/A", "N/A", "N/A"]

        return tx_bias_list

    def get_rx_power(self):
        """
        Retrieves the received optical power for this SFP
        """
        rx_power = None
        rx_power_list = []

        rx_power_data = self._get_eeprom_data('ChannelMonitor')
        if (rx_power_data is not None):
            if (self.sfp_type == 'QSFP'):
                rx_power = rx_power_data['data']['RX1Power']['value']
                rx_power_list.append(rx_power)
                rx_power = rx_power_data['data']['RX2Power']['value']
                rx_power_list.append(rx_power)
                rx_power = rx_power_data['data']['RX3Power']['value']
                rx_power_list.append(rx_power)
                rx_power = rx_power_data['data']['RX4Power']['value']
                rx_power_list.append(rx_power)
            else:
                rx1_pw = rx_power_data['data']['RXPower']['value']
                return [rx1_pw, "N/A", "N/A", "N/A"]

        return rx_power_list

    def get_tx_power(self):
        """
        Retrieves the TX power of this SFP
        """
        tx_power_list = []
        if(self.sfp_type == 'QSFP'):
            # QSFP capability byte parse, through this byte can know whether it support tx_power or not.
            # TODO: in the future when decided to migrate to support SFF-8636 instead of SFF-8436,
            # need to add more code for determining the capability and version compliance
            # in SFF-8636 dom capability definitions evolving with the versions.
            qspf_dom_capability_data = self._get_eeprom_data('dom_capability')
            qsfp_dom_rev_data = self._get_eeprom_data('dom_rev')
            if (qspf_dom_capability_data is not None and qsfp_dom_rev_data is not None):
                qsfp_dom_rev = qsfp_dom_rev_data['data']['dom_rev']['value']
                qsfp_tx_power_support = qspf_dom_capability_data['data']['Tx_power_support']['value']
            else:
                return tx_power_list

            # The tx_power monitoring is only available on QSFP which compliant with SFF-8636
            # and claimed that it support tx_power with one indicator bit.
            if (qsfp_dom_rev[0:8] != 'SFF-8636' or (qsfp_dom_rev[0:8] == 'SFF-8636' and qsfp_tx_power_support != 'on')):
                return tx_power_list
            else:
                channel_monitor_data = self._get_eeprom_data('ChannelMonitor_TxPower')
                if (channel_monitor_data is not None):
                    tx1_pw = channel_monitor_data['data']['TX1Power']['value']
                    tx2_pw = channel_monitor_data['data']['TX2Power']['value']
                    tx3_pw = channel_monitor_data['data']['TX3Power']['value']
                    tx4_pw = channel_monitor_data['data']['TX4Power']['value']
                else:
                    return tx_power_list

        else:
            channel_monitor_data = self._get_eeprom_data('ChannelMonitor')
            if (channel_monitor_data is not None):
                tx1_pw = channel_monitor_data['data']['TXPower']['value'] 
                tx2_pw = 'N/A'
                tx3_pw = 'N/A'
                tx4_pw = 'N/A'
            else:
                return tx_power_list

        tx_power_list.append(tx1_pw)
        tx_power_list.append(tx2_pw)
        tx_power_list.append(tx3_pw)
        tx_power_list.append(tx4_pw)

        return tx_power_list

    def reset(self):
        """
        Reset the SFP and returns all user settings to their default state
        """
        if (self.sfp_type == 'QSFP'):
            # Port offset starts with 0x4000
            port_offset = 16384 + ((self.index-1) * 16)

            status = self.pci_get_value(self.BASE_RES_PATH, port_offset)
            reg_value = int(status)

            # Absence of status throws error
            if (reg_value == ""):
                return False

            # Mask off 4th bit for reset
            mask = (1 << 4)

            # ResetL is active low
            reg_value = reg_value & ~mask

            # Convert our register value back to a hex string and write back
            status = self.pci_set_value(self.BASE_RES_PATH, reg_value, port_offset)

            # Sleep 1 second to allow it to settle
            time.sleep(1)

            reg_value = reg_value | mask

            # Convert our register value back to a hex string and write back
            status = self.pci_set_value(self.BASE_RES_PATH, reg_value, port_offset)

            return True

        else:
            return False

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode(low power mode) of this SFP
        """
        if (self.sfp_type == 'QSFP'):
            # Port offset starts with 0x4000
            port_offset = 16384 + ((self.index-1) * 16)

            status = self.pci_get_value(self.BASE_RES_PATH, port_offset)
            reg_value = int(status)

            # Absence of status throws error
            if (reg_value == ""):
                return False

            # Mask off 6th bit for lowpower mode
            mask = (1 << 6)

            # LPMode is active high; set or clear the bit accordingly
            if lpmode is True:
                reg_value = reg_value | mask
            else:
                reg_value = reg_value & ~mask

            # Convert our register value back to a hex string and write back
            status = self.pci_set_value(self.BASE_RES_PATH, reg_value, port_offset)

            return True

        else:
            return False

    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels
        """
        return False

    def tx_disable_channel(self, channel, disable):
        """
        Sets the tx_disable for specified SFP channels
        """
        return False

    def tx_disable_channel(self, channel, disable):
        """
        Sets the tx_disable for specified SFP channels
        """
        return False

    def set_power_override(self, power_override, power_set):
        """
        Sets SFP power level using power_override and power_set
        """
        return False

    def get_status(self):
        """
        Retrieves the operational status of the device
        """
        reset = self.get_reset_status()

        if (reset == True):
            status = False
        else:
            status = True

        return status
