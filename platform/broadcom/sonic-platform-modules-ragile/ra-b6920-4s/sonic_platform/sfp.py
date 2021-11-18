#!/usr/bin/env python

try:
    #from sonic_platform_pddf_base.pddf_sfp import *
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472InterfaceId
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472Dom
    from sonic_platform_pddf_base.pddf_sfp import PddfSfp
    from sonic_platform_pddf_base.pddf_sfp import SFP_VOLT_OFFSET
    from sonic_platform_pddf_base.pddf_sfp import SFP_VOLT_WIDTH
    from sonic_platform_pddf_base.pddf_sfp import SFP_CHANNL_MON_OFFSET
    from sonic_platform_pddf_base.pddf_sfp import SFP_CHANNL_MON_WIDTH
    from sonic_platform_pddf_base.pddf_sfp import SFP_TEMPE_OFFSET
    from sonic_platform_pddf_base.pddf_sfp import SFP_TEMPE_WIDTH
    from sonic_platform_pddf_base.pddf_sfp import QSFP_DOM_REV_OFFSET
    from sonic_platform_pddf_base.pddf_sfp import QSFP_DOM_REV_WIDTH
    from sonic_platform_pddf_base.pddf_sfp import QSFP_CHANNL_MON_OFFSET
    from sonic_platform_pddf_base.pddf_sfp import QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

XCVR_DOM_CAPABILITY_OFFSET = 92
XCVR_DOM_CAPABILITY_WIDTH = 2
QSFP_VERSION_COMPLIANCE_OFFSET = 1
QSFP_VERSION_COMPLIANCE_WIDTH = 2
QSFP_OPTION_VALUE_OFFSET = 192
QSFP_OPTION_VALUE_WIDTH = 4

class Sfp(PddfSfp):
    """
    PDDF Platform-Specific Sfp class
    """

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfSfp.__init__(self, index, pddf_data, pddf_plugin_data)
        self.dom_supported = False
        self.__dom_capability_detect()

    def __dom_capability_detect(self):
        self.dom_supported = False
        self.dom_temp_supported = False
        self.dom_volt_supported = False
        self.dom_rx_power_supported = False
        self.dom_tx_power_supported = False
        self.qsfp_page3_available = False
        self.calibration = 0
        if not self.get_presence():
            return

        if self.is_osfp_port:
            # Not implement
            return
        elif self.is_qsfp_port:
            self.calibration = 1
            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                self.dom_supported = False
            offset = 128

            # QSFP capability byte parse, through this byte can know whether it support tx_power or not.
            # TODO: in the future when decided to migrate to support SFF-8636 instead of SFF-8436,
            # need to add more code for determining the capability and version compliance
            # in SFF-8636 dom capability definitions evolving with the versions.
            qsfp_dom_capability_raw = self.__read_eeprom_specific_bytes(
                (offset + XCVR_DOM_CAPABILITY_OFFSET), XCVR_DOM_CAPABILITY_WIDTH)
            if qsfp_dom_capability_raw is not None:
                qsfp_version_compliance_raw = self.__read_eeprom_specific_bytes(
                    QSFP_VERSION_COMPLIANCE_OFFSET, QSFP_VERSION_COMPLIANCE_WIDTH)
                qsfp_version_compliance = int(
                    qsfp_version_compliance_raw[0], 16)
                dom_capability = sfpi_obj.parse_dom_capability(
                    qsfp_dom_capability_raw, 0)
                if qsfp_version_compliance >= 0x08:
                    self.dom_temp_supported = dom_capability['data']['Temp_support']['value'] == 'On'
                    self.dom_volt_supported = dom_capability['data']['Voltage_support']['value'] == 'On'
                    self.dom_rx_power_supported = dom_capability['data']['Rx_power_support']['value'] == 'On'
                    self.dom_tx_power_supported = dom_capability['data']['Tx_power_support']['value'] == 'On'
                else:
                    self.dom_temp_supported = True
                    self.dom_volt_supported = True
                    self.dom_rx_power_supported = dom_capability['data']['Rx_power_support']['value'] == 'On'
                    self.dom_tx_power_supported = True

                self.dom_supported = True
                self.calibration = 1
                sfpd_obj = sff8436Dom()
                if sfpd_obj is None:
                    return None
                qsfp_option_value_raw = self.__read_eeprom_specific_bytes(
                    QSFP_OPTION_VALUE_OFFSET, QSFP_OPTION_VALUE_WIDTH)
                if qsfp_option_value_raw is not None:
                    optional_capability = sfpd_obj.parse_option_params(
                        qsfp_option_value_raw, 0)
                    self.dom_tx_disable_supported = optional_capability[
                        'data']['TxDisable']['value'] == 'On'
                dom_status_indicator = sfpd_obj.parse_dom_status_indicator(
                    qsfp_version_compliance_raw, 1)
                self.qsfp_page3_available = dom_status_indicator['data']['FlatMem']['value'] == 'Off'
            else:
                self.dom_supported = False
                self.dom_temp_supported = False
                self.dom_volt_supported = False
                self.dom_rx_power_supported = False
                self.dom_tx_power_supported = False
                self.calibration = 0
                self.qsfp_page3_available = False
        else:
            sfpi_obj = sff8472InterfaceId()
            if sfpi_obj is None:
                return None
            sfp_dom_capability_raw = self.__read_eeprom_specific_bytes(
                XCVR_DOM_CAPABILITY_OFFSET, XCVR_DOM_CAPABILITY_WIDTH)
            if sfp_dom_capability_raw is not None:
                sfp_dom_capability = int(sfp_dom_capability_raw[0], 16)
                self.dom_supported = (sfp_dom_capability & 0x40 != 0)
                if self.dom_supported:
                    self.dom_temp_supported = True
                    self.dom_volt_supported = True
                    self.dom_rx_power_supported = True
                    self.dom_tx_power_supported = True
                    if sfp_dom_capability & 0x20 != 0:
                        self.calibration = 1
                    elif sfp_dom_capability & 0x10 != 0:
                        self.calibration = 2
                    else:
                        self.calibration = 0
                else:
                    self.dom_temp_supported = False
                    self.dom_volt_supported = False
                    self.dom_rx_power_supported = False
                    self.dom_tx_power_supported = False
                    self.calibration = 0
                self.dom_tx_disable_supported = (
                    int(sfp_dom_capability_raw[1], 16) & 0x40 != 0)

    # Provide the functions/variables below for which implementation is to be overwritten

    def __read_eeprom_specific_bytes(self, offset, num_bytes):
        eeprom_raw = []
        if not self.get_presence():
            return None
        for i in range(0, num_bytes):
            eeprom_raw.append("0x00")

        try:
            with open(self.eeprom_path, mode="rb", buffering=0) as eeprom:
                eeprom.seek(offset)
                raw = eeprom.read(num_bytes)
        except Exception as e:
            print("Error: Unable to open eeprom_path: %s" % (str(e)))
            return None

        try:
            if len(raw) == 0:
                return None
            for n in range(0, num_bytes):
                eeprom_raw[n] = hex(raw[n])[2:].zfill(2)
        except Exception as e:
            print("Error: Exception info: %s" % (str(e)))
            return None

        return eeprom_raw

    def get_transceiver_bulk_status(self):
        # check present status
        if not self.get_presence():
            return None
        self.__dom_capability_detect()

        xcvr_dom_info_dict = dict.fromkeys(self.dom_dict_keys, 'N/A')

        if self.is_osfp_port:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            pass
        elif self.is_qsfp_port:
            # QSFPs
            xcvr_dom_info_dict = super(Sfp, self).get_transceiver_bulk_status()

            # pddf_sfp "qsfp_tx_power_support != 'on'" is wrong

            offset = 0
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            qsfp_dom_rev_raw = self.__read_eeprom_specific_bytes((offset + QSFP_DOM_REV_OFFSET), QSFP_DOM_REV_WIDTH)
            if qsfp_dom_rev_raw is not None:
                qsfp_dom_rev_data = sfpd_obj.parse_sfp_dom_rev(qsfp_dom_rev_raw, 0)
            else:
                return None

            dom_channel_monitor_data = {}
            qsfp_dom_rev = qsfp_dom_rev_data['data']['dom_rev']['value']

            if (qsfp_dom_rev[0:8] == 'SFF-8636' and self.dom_tx_power_supported is True):
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
        else:
            # SFPs
            offset = 256
            if not self.dom_supported:
                return xcvr_dom_info_dict

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            sfpd_obj._calibration_type = self.calibration

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
        # check present status
        if not self.get_presence():
            return None
        self.__dom_capability_detect()

        xcvr_dom_threshold_info_dict = dict.fromkeys(self.threshold_dict_keys, 'N/A')

        if self.is_osfp_port:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            pass
        elif self.is_qsfp_port:
            # QSFPs
            if not self.dom_supported or not self.qsfp_page3_available:
                return xcvr_dom_threshold_info_dict

            return super(Sfp, self).get_transceiver_threshold_info()

        else:
            # SFPs
            if not self.dom_supported:
                return xcvr_dom_threshold_info_dict

            return super(Sfp, self).get_transceiver_threshold_info()

        return xcvr_dom_threshold_info_dict
