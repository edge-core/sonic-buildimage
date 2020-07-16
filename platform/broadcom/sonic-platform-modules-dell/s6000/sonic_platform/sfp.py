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
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform_base.sfp_base import SfpBase
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


PAGE_OFFSET = 0
KEY_OFFSET = 1
KEY_WIDTH = 2
FUNC_NAME = 3

INFO_OFFSET = 128
DOM_OFFSET = 0
DOM_OFFSET1 = 384

cable_length_tup = ('Length(km)', 'Length OM3(2m)', 'Length OM2(m)',
                    'Length OM1(m)', 'Length Cable Assembly(m)')

compliance_code_tup = (
    '10/40G Ethernet Compliance Code',
    'SONET Compliance codes',
    'SAS/SATA compliance codes',
    'Gigabit Ethernet Compliant codes',
    'Fibre Channel link length/Transmitter Technology',
    'Fibre Channel transmission media',
    'Fibre Channel Speed')

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
     'reset_status': [DOM_OFFSET,   2,  1, 'parse_dom_status_indicator'],
           'rx_los': [DOM_OFFSET,   3,  1, 'parse_dom_tx_rx_los'],
         'tx_fault': [DOM_OFFSET,   4,  1, 'parse_dom_tx_fault'],
       'tx_disable': [DOM_OFFSET,  86,  1, 'parse_dom_tx_disable'],
     'power_lpmode': [DOM_OFFSET,  93,  1, 'parse_dom_power_control'],
   'power_override': [DOM_OFFSET,  93,  1, 'parse_dom_power_control'],
      'Temperature': [DOM_OFFSET,  22,  2, 'parse_temperature'],
          'Voltage': [DOM_OFFSET,  26,  2, 'parse_voltage'],
   'ChannelMonitor': [DOM_OFFSET,  34, 16, 'parse_channel_monitor_params'],

       'cable_type': [INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
     'cable_length': [INFO_OFFSET, -1, -1, 'parse_sfp_info_bulk'],
        'connector': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
             'type': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
         'encoding': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
   'ext_identifier': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'ext_rateselect_compliance':
                     [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'nominal_bit_rate': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
 'specification_compliance':
                     [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
  'type_abbrv_name': [INFO_OFFSET,  0, 20, 'parse_sfp_info_bulk'],
     'manufacturer': [INFO_OFFSET, 20, 16, 'parse_vendor_name'],
       'vendor_oui': [INFO_OFFSET,  37, 3, 'parse_vendor_oui'],
            'model': [INFO_OFFSET, 40, 16, 'parse_vendor_pn'],
     'hardware_rev': [INFO_OFFSET, 56,  2, 'parse_vendor_rev'],
           'serial': [INFO_OFFSET, 68, 16, 'parse_vendor_sn'],
      'vendor_date': [INFO_OFFSET, 84,  8, 'parse_vendor_date'],
  'ModuleThreshold': [DOM_OFFSET1, 128, 24, 'parse_module_threshold_values'],
 'ChannelThreshold': [DOM_OFFSET1, 176, 16, 'parse_channel_threshold_values'],
}


class Sfp(SfpBase):
    """
    DELLEMC Platform-specific Sfp class
    """

    def __init__(self, index, sfp_type, eeprom_path,
            sfp_control, sfp_ctrl_idx):
        SfpBase.__init__(self)
        self.sfp_type = sfp_type
        self.index = index
        self.eeprom_path = eeprom_path
        self.sfp_control = sfp_control
        self.sfp_ctrl_idx = sfp_ctrl_idx
        self.sfpInfo = sff8436InterfaceId()
        self.sfpDomInfo = sff8436Dom()

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

        if (self.sfpInfo is None):
            return None

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
                eeprom_data = getattr(
                    self.sfpInfo, sff8436_parser[eeprom_key][FUNC_NAME])(
                    eeprom_data_raw, 0)
            else:
                eeprom_data = getattr(
                    self.sfpDomInfo, sff8436_parser[eeprom_key][FUNC_NAME])(
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
            bit_rate = str(
                iface_data['data']['Nominal Bit Rate(100Mbs)']['value'])

            for key in compliance_code_tup:
                if key in iface_data['data']['Specification compliance']['value']:
                    compliance_code_dict[key] = iface_data['data']['Specification compliance']['value'][key]['value']
            for key in cable_length_tup:
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
            return None

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
        transceiver_info_dict['specification_compliance'] = str(
            compliance_code_dict)
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
        if (module_threshold_data is not None):
            tempHighAlarm = module_threshold_data['data']['TempHighAlarm']['value']
            tempLowAlarm = module_threshold_data['data']['TempLowAlarm']['value']
            tempHighWarn = module_threshold_data['data']['TempHighWarning']['value']
            tempLowWarn = module_threshold_data['data']['TempLowWarning']['value']
            vccHighAlarm = module_threshold_data['data']['VccHighAlarm']['value']
            vccLowAlarm = module_threshold_data['data']['VccLowAlarm']['value']
            vccHighWarn = module_threshold_data['data']['VccHighWarning']['value']
            vccLowWarn = module_threshold_data['data']['VccLowWarning']['value']
        else:
            return transceiver_dom_threshold_dict

        # Channel Threshold
        channel_threshold_data = self._get_eeprom_data('ChannelThreshold')
        if (channel_threshold_data is not None):
            rxPowerHighAlarm = channel_threshold_data['data']['RxPowerHighAlarm']['value']
            rxPowerLowAlarm = channel_threshold_data['data']['RxPowerLowAlarm']['value']
            rxPowerHighWarn = channel_threshold_data['data']['RxPowerHighWarning']['value']
            rxPowerLowWarn = channel_threshold_data['data']['RxPowerLowWarning']['value']
            txBiasHighAlarm = channel_threshold_data['data']['TxBiasHighAlarm']['value']
            txBiasLowAlarm = channel_threshold_data['data']['TxBiasLowAlarm']['value']
            txBiasHighWarn = channel_threshold_data['data']['TxBiasHighWarning']['value']
            txBiasLowWarn = channel_threshold_data['data']['TxBiasLowWarning']['value']
        else:
            return transceiver_dom_threshold_dict

        transceiver_dom_threshold_dict['temphighalarm'] = tempHighAlarm
        transceiver_dom_threshold_dict['templowalarm'] = tempLowAlarm
        transceiver_dom_threshold_dict['temphighwarning'] = tempHighWarn
        transceiver_dom_threshold_dict['templowwarning'] = tempLowWarn
        transceiver_dom_threshold_dict['vcchighalarm'] = vccHighAlarm
        transceiver_dom_threshold_dict['vcclowalarm'] = vccLowAlarm
        transceiver_dom_threshold_dict['vcchighwarning'] = vccHighWarn
        transceiver_dom_threshold_dict['vcclowwarning'] = vccLowWarn
        transceiver_dom_threshold_dict['rxpowerhighalarm'] = rxPowerHighAlarm
        transceiver_dom_threshold_dict['rxpowerlowalarm'] = rxPowerLowAlarm
        transceiver_dom_threshold_dict['rxpowerhighwarning'] = rxPowerHighWarn
        transceiver_dom_threshold_dict['rxpowerlowwarning'] = rxPowerLowWarn
        transceiver_dom_threshold_dict['txbiashighalarm'] = txBiasHighAlarm
        transceiver_dom_threshold_dict['txbiaslowalarm'] = txBiasLowAlarm
        transceiver_dom_threshold_dict['txbiashighwarning'] = txBiasHighWarn
        transceiver_dom_threshold_dict['txbiaslowwarning'] = txBiasLowWarn

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
        channel_monitor_data = self._get_eeprom_data('ChannelMonitor')
        if (channel_monitor_data is not None):
            tx_bias = channel_monitor_data['data']['TX1Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = channel_monitor_data['data']['TX2Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = channel_monitor_data['data']['TX3Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = channel_monitor_data['data']['TX4Bias']['value']
            tx_bias_list.append(tx_bias)
            rx_power = channel_monitor_data['data']['RX1Power']['value']
            rx_power_list.append(rx_power)
            rx_power = channel_monitor_data['data']['RX2Power']['value']
            rx_power_list.append(rx_power)
            rx_power = channel_monitor_data['data']['RX3Power']['value']
            rx_power_list.append(rx_power)
            rx_power = channel_monitor_data['data']['RX4Power']['value']
            rx_power_list.append(rx_power)
        else:
            return transceiver_dom_dict

        transceiver_dom_dict['rx_los'] = rx_los
        transceiver_dom_dict['tx_fault'] = tx_fault
        transceiver_dom_dict['reset_status'] = reset_state
        transceiver_dom_dict['power_lpmode'] = lp_mode
        transceiver_dom_dict['tx_disable'] = tx_disable
        transceiver_dom_dict['tx_disable_channel'] = tx_disable_channel
        transceiver_dom_dict['temperature'] = temperature
        transceiver_dom_dict['voltage'] = voltage
        transceiver_dom_dict['tx1bias'] = tx_bias_list[0]
        transceiver_dom_dict['tx2bias'] = tx_bias_list[1]
        transceiver_dom_dict['tx3bias'] = tx_bias_list[2]
        transceiver_dom_dict['tx4bias'] = tx_bias_list[3]
        transceiver_dom_dict['rx1power'] = rx_power_list[0]
        transceiver_dom_dict['rx2power'] = rx_power_list[1]
        transceiver_dom_dict['rx3power'] = rx_power_list[2]
        transceiver_dom_dict['rx4power'] = rx_power_list[3]

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
        """
        presence_ctrl = self.sfp_control + 'qsfp_modprs'
        try:
            reg_file = open(presence_ctrl)
        except IOError as e:
            return False

        reg_hex = reg_file.readline().rstrip()

        # content is a string containing the hex
        # representation of the register
        reg_value = int(reg_hex, 16)

        # Mask off the bit corresponding to our port
        mask = (1 << self.sfp_ctrl_idx)

        # ModPrsL is active low
        if ((reg_value & mask) == 0):
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
        Retrieves the reset status of SFP
        """
        reset_status = None
        reset_ctrl = self.sfp_control + 'qsfp_reset'
        try:
            reg_file = open(reset_ctrl, "r+")
        except IOError as e:
            return False

        reg_hex = reg_file.readline().rstrip()

        # content is a string containing the hex
        # representation of the register
        reg_value = int(reg_hex, 16)

        # Mask off the bit corresponding to our port
        index = self.sfp_ctrl_idx

        mask = (1 << index)

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

        return rx_los

    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP
        """
        tx_fault = None
        tx_fault_list = []

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

        return tx_fault

    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP
        """
        tx_disable = None
        tx_disable_list = []

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

        return tx_disable

    def get_tx_disable_channel(self):
        """
        Retrieves the TX disabled channels in this SFP
        """
        tx_disable = None
        tx_disable_list = []

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
        Retrieves the lpmode (low power mode) status of this SFP
        """
        lpmode_ctrl = self.sfp_control + 'qsfp_lpmode'
        try:
            reg_file = open(lpmode_ctrl, "r+")
        except IOError as e:
            return False

        reg_hex = reg_file.readline().rstrip()

        # content is a string containing the hex
        # representation of the register
        reg_value = int(reg_hex, 16)

        # Mask off the bit corresponding to our port
        index = self.sfp_ctrl_idx

        mask = (1 << index)

        if ((reg_value & mask) == 0):
            lpmode_state = False
        else:
            lpmode_state = True

        return lpmode_state

    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP
        """
        power_override_state = None

        # Reset Status
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
            tx_bias = tx_bias_data['data']['TX1Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = tx_bias_data['data']['TX2Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = tx_bias_data['data']['TX3Bias']['value']
            tx_bias_list.append(tx_bias)
            tx_bias = tx_bias_data['data']['TX4Bias']['value']
            tx_bias_list.append(tx_bias)

        return tx_bias_list

    def get_rx_power(self):
        """
        Retrieves the received optical power for this SFP
        """
        rx_power = None
        rx_power_list = []

        rx_power_data = self._get_eeprom_data('ChannelMonitor')
        if (rx_power_data is not None):
            rx_power = rx_power_data['data']['RX1Power']['value']
            rx_power_list.append(rx_power)
            rx_power = rx_power_data['data']['RX2Power']['value']
            rx_power_list.append(rx_power)
            rx_power = rx_power_data['data']['RX3Power']['value']
            rx_power_list.append(rx_power)
            rx_power = rx_power_data['data']['RX4Power']['value']
            rx_power_list.append(rx_power)

        return rx_power_list


    def get_tx_power(self):
        """
        Retrieves the TX power of this SFP
        """
        tx_power = None
        tx_power_list = []

        tx_power_list.append('-infdBm')
        tx_power_list.append('-infdBm')
        tx_power_list.append('-infdBm')
        tx_power_list.append('-infdBm')

        return tx_power_list

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        """
        reset_ctrl = self.sfp_control + 'qsfp_reset'
        try:
            # Open reset_ctrl in both read & write mode
            reg_file = open(reset_ctrl, "r+")
        except IOError as e:
            return False

        reg_hex = reg_file.readline().rstrip()
        reg_value = int(reg_hex, 16)

        # Mask off the bit corresponding to our port
        index = self.sfp_ctrl_idx

        # Mask off the bit corresponding to our port
        mask = (1 << index)

        # ResetL is active low
        reg_value = (reg_value & ~mask)

        # Convert our register value back to a
        # hex string and write back
        reg_file.seek(0)
        reg_file.write(hex(reg_value))
        reg_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        # Flip the bit back high and write back to the
        # register to take port out of reset
        try:
            reg_file = open(reset_ctrl, "w")
        except IOError as e:
            return False

        reg_value = reg_value | mask
        reg_file.seek(0)
        reg_file.write(hex(reg_value))
        reg_file.close()

        return True

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        """
        lpmode_ctrl = self.sfp_control + 'qsfp_lpmode'
        try:
            reg_file = open(lpmode_ctrl, "r+")
        except IOError as e:
            return False

        reg_hex = reg_file.readline().rstrip()

        # content is a string containing the hex
        # representation of the register
        reg_value = int(reg_hex, 16)

        # Mask off the bit corresponding to our port
        index = self.sfp_ctrl_idx

        mask = (1 << index)

        # LPMode is active high; set or clear the bit accordingly
        if lpmode is True:
            reg_value = (reg_value | mask)
        else:
            reg_value = (reg_value & ~mask)

        # Convert our register value back to a hex string and write back
        content = hex(reg_value)

        reg_file.seek(0)
        reg_file.write(content)
        reg_file.close()

        return True

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
