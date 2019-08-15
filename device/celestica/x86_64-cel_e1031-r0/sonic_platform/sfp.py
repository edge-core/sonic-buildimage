#!/usr/bin/env python

#############################################################################
# Celestica
#
# Sfp contains an implementation of SONiC Platform Base API and
# provides the sfp device status which are available in the platform
#
#############################################################################

import os
import time
import subprocess
import sonic_device_util
from ctypes import create_string_buffer

try:
    from swsssdk import ConfigDBConnector
    from sonic_platform_base.sfp_base import SfpBase
    from sonic_platform_base.sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Sfp(SfpBase, SfpUtilBase):
    """Platform-specific Sfp class"""

    PORT_START = 1
    PORT_END = 52
    port_to_i2c_mapping = {
        49: 15,
        50: 14,
        51: 17,
        52: 16
    }
    PRS_PATH = "/sys/devices/platform/e1031.smc/SFP/sfp_modabs"
    PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
    SFP_STATUS_CONTROL_OFFSET = 110
    SFP_STATUS_CONTROL_WIDTH = 1

    _port_to_eeprom_mapping = {}
    _sfp_port = range(49, PORT_END + 1)

    SFP_EEPROM_TYPE_KEY = "TypeOfTransceiver"
    SFP_EEPROM_HW_REV_KEY = "VendorRev"
    SFP_EEPROM_MF_NAME_KEY = "VendorName"
    SFP_EEPROM_MODEL_NAME_KEY = "VendorPN"
    SFP_EEPROM_SERIAL_KEY = "VendorSN"
    SFP_EEPROM_CONNECTOR_KEY = "Connector"
    SFP_EEPROM_ENCODE_KEY = "EncodingCodes"
    SFP_EEPROM_EXT_IDENT_KEY = "ExtIdentOfTypeOfTransceiver"
    SFP_EEPROM_CABLE_KEY = "LengthCable(UnitsOfm)"
    SFP_EEPROM_BIT_RATE_KEY = "NominalSignallingRate(UnitsOf100Mbd)"
    SFP_EEPROM_SPEC_COM_KEY = "Specification compliance"
    SFP_EEPROM_DATE_KEY = "VendorDataCode(YYYY-MM-DD Lot)"
    SFP_EEPROM_OUI_KEY = "VendorOUI"
    SFP_EEPROM_MON_DATA_KEY = "MonitorData"
    SFP_EEPROM_TEMP_KEY = "Temperature"
    SFP_EEPROM_VCC_KEY = "Vcc"
    SFP_EEPROM_RX_PWR_KEY = "RXPower"
    SFP_EEPROM_TX_PWR_KEY = "TXPower"
    SFP_EEPROM_TX_BS_KEY = "TXBias"
    SFP_EEPROM_STATUS_CON_KEY = "StatusControl"

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return []

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def _convert_string_to_num(self, value_str):
        if "-inf" in value_str:
            return 'N/A'
        elif "Unknown" in value_str:
            return 'N/A'
        elif 'dBm' in value_str:
            t_str = value_str.rstrip('dBm')
            return float(t_str)
        elif 'mA' in value_str:
            t_str = value_str.rstrip('mA')
            return float(t_str)
        elif 'C' in value_str:
            t_str = value_str.rstrip('C')
            return float(t_str)
        elif 'Volts' in value_str:
            t_str = value_str.rstrip('Volts')
            return float(t_str)
        else:
            return 'N/A'

    def get_low_power_mode(self, port_num):
        raise NotImplementedError

    def set_low_power_mode(self, port_num, lpmode):
        raise NotImplementedError

    def get_transceiver_change_event(self, timeout=0):
        raise NotImplementedError

    def __init__(self, sfp_index):
        # Init SfpUtilBase
        eeprom_path = '/sys/bus/i2c/devices/i2c-{0}/{0}-0050/eeprom'
        for x in range(self.PORT_START, self.PORT_END + 1):
            if x not in self._sfp_port:
                self.port_to_i2c_mapping[x] = None
            self.port_to_eeprom_mapping[x] = eeprom_path.format(
                self.port_to_i2c_mapping[x])
        self.read_porttab_mappings(self.__get_path_to_port_config_file())
        SfpUtilBase.__init__(self)

        # Init index
        self.index = sfp_index
        self.port_num = self.index + 1

    def __get_sysfsfile_eeprom(self):
        sysfsfile_eeprom = None
        sysfs_sfp_i2c_client_eeprom_path = self.port_to_eeprom_mapping[self.port_num]
        try:
            sysfsfile_eeprom = open(
                sysfs_sfp_i2c_client_eeprom_path, mode="r+b", buffering=0)
        except IOError:
            print("Error: reading sysfs file %s" %
                  sysfs_sfp_i2c_client_eeprom_path)
        return sysfsfile_eeprom

    def __get_path_to_port_config_file(self):
        # Get platform and hwsku
        machine_info = sonic_device_util.get_machine_info()
        platform = sonic_device_util.get_platform_info(machine_info)
        config_db = ConfigDBConnector()
        config_db.connect()
        data = config_db.get_table('DEVICE_METADATA')
        try:
            hwsku = data['localhost']['hwsku']
        except KeyError:
            hwsku = "Unknown"

        # Load platform module from source
        platform_path = "/".join([self.PLATFORM_ROOT_PATH, platform])
        hwsku_path = "/".join([platform_path, hwsku])

        # First check for the presence of the new 'port_config.ini' file
        port_config_file_path = "/".join([hwsku_path, "port_config.ini"])
        if not os.path.isfile(port_config_file_path):
            # port_config.ini doesn't exist. Try loading the legacy 'portmap.ini' file
            port_config_file_path = "/".join([hwsku_path, "portmap.ini"])

        return port_config_file_path

    def get_transceiver_info(self):
        """
        Retrieves transceiver info of this SFP
        Returns:
            A dict which contains following keys/values :
        ========================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        type                       |1*255VCHAR     |type of SFP
        hardwarerev                |1*255VCHAR     |hardware version of SFP
        serialnum                  |1*255VCHAR     |serial number of the SFP
        manufacturename            |1*255VCHAR     |SFP vendor name
        modelname                  |1*255VCHAR     |SFP model name
        Connector                  |1*255VCHAR     |connector information
        encoding                   |1*255VCHAR     |encoding information
        ext_identifier             |1*255VCHAR     |extend identifier
        ext_rateselect_compliance  |1*255VCHAR     |extended rateSelect compliance
        cable_length               |INT            |cable length in m
        nominal_bit_rate           |INT            |nominal bit rate by 100Mbs
        specification_compliance   |1*255VCHAR     |specification compliance
        vendor_date                |1*255VCHAR     |vendor date
        vendor_oui                 |1*255VCHAR     |vendor OUI
        ========================================================================
        """
        transceiver_info_dict = dict()
        # get eeprom data
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('interface'):
            transceiver_info_data = self.eeprom_dict['interface'].get('data')

            # set specification_compliance
            spec_com = transceiver_info_data.get(
                self.SFP_EEPROM_SPEC_COM_KEY, {})
            spec_com_str = "/".join(list(spec_com.values()))

            # set normal transceiver info
            transceiver_info_dict['type'] = transceiver_info_data.get(
                self.SFP_EEPROM_TYPE_KEY, 'N/A')
            transceiver_info_dict['hardwarerev'] = transceiver_info_data.get(
                self.SFP_EEPROM_HW_REV_KEY, 'N/A')
            transceiver_info_dict['manufacturename'] = transceiver_info_data.get(
                self.SFP_EEPROM_MF_NAME_KEY, 'N/A')
            transceiver_info_dict['modelname'] = transceiver_info_data.get(
                self.SFP_EEPROM_MODEL_NAME_KEY, 'N/A')
            transceiver_info_dict['serialnum'] = transceiver_info_data.get(
                self.SFP_EEPROM_SERIAL_KEY, 'N/A')
            transceiver_info_dict['Connector'] = transceiver_info_data.get(
                self.SFP_EEPROM_CONNECTOR_KEY, 'N/A')
            transceiver_info_dict['encoding'] = transceiver_info_data.get(
                self.SFP_EEPROM_ENCODE_KEY, 'N/A')
            transceiver_info_dict['ext_identifier'] = transceiver_info_data.get(
                self.SFP_EEPROM_EXT_IDENT_KEY, 'N/A')
            transceiver_info_dict['cable_length'] = transceiver_info_data.get(
                self.SFP_EEPROM_CABLE_KEY, 'N/A')
            transceiver_info_dict['nominal_bit_rate'] = transceiver_info_data.get(
                self.SFP_EEPROM_BIT_RATE_KEY, 'N/A')
            transceiver_info_dict['vendor_date'] = transceiver_info_data.get(
                self.SFP_EEPROM_DATE_KEY, 'N/A')
            transceiver_info_dict['vendor_oui'] = transceiver_info_data.get(
                self.SFP_EEPROM_OUI_KEY, 'N/A')
            transceiver_info_dict['ext_rateselect_compliance'] = "N/A"
            transceiver_info_dict['specification_compliance'] = spec_com_str or "N/A"

        return transceiver_info_dict

    def get_transceiver_bulk_status(self):
        """
        Retrieves transceiver bulk status of this SFP
        Returns:
            A dict which contains following keys/values :
        ========================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        RX LOS                     |BOOLEAN        |RX lost-of-signal status,
                                   |               |True if has RX los, False if not.
        TX FAULT                   |BOOLEAN        |TX fault status,
                                   |               |True if has TX fault, False if not.
        Reset status               |BOOLEAN        |reset status,
                                   |               |True if SFP in reset, False if not.
        LP mode                    |BOOLEAN        |low power mode status,
                                   |               |True in lp mode, False if not.
        TX disable                 |BOOLEAN        |TX disable status,
                                   |               |True TX disabled, False if not.
        TX disabled channel        |HEX            |disabled TX channles in hex,
                                   |               |bits 0 to 3 represent channel 0
                                   |               |to channel 3.
        Temperature                |INT            |module temperature in Celsius
        Voltage                    |INT            |supply voltage in mV
        TX bias                    |INT            |TX Bias Current in mA
        RX power                   |INT            |received optical power in mW
        TX power                   |INT            |TX output power in mW
        ========================================================================
        """
        transceiver_bulk_status_dict = dict()
        # get eeprom data
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('dom'):
            transceiver_dom_data = self.eeprom_dict['dom'].get('data', {})
            transceiver_dom_data_mmv = transceiver_dom_data.get(
                self.SFP_EEPROM_MON_DATA_KEY)

            # set normal transceiver bulk status
            transceiver_bulk_status_dict['temperature'] = transceiver_dom_data_mmv.get(
                self.SFP_EEPROM_TEMP_KEY, 'N/A')
            transceiver_bulk_status_dict['voltage'] = transceiver_dom_data_mmv.get(
                self.SFP_EEPROM_VCC_KEY, 'N/A')
            transceiver_bulk_status_dict['rx1power'] = transceiver_dom_data_mmv.get(
                self.SFP_EEPROM_RX_PWR_KEY, 'N/A')
            transceiver_bulk_status_dict['rx2power'] = "N/A"
            transceiver_bulk_status_dict['rx3power'] = "N/A"
            transceiver_bulk_status_dict['rx4power'] = "N/A"
            transceiver_bulk_status_dict['tx1bias'] = transceiver_dom_data_mmv.get(
                self.SFP_EEPROM_TX_BS_KEY, 'N/A')
            transceiver_bulk_status_dict['tx2bias'] = "N/A"
            transceiver_bulk_status_dict['tx3bias'] = "N/A"
            transceiver_bulk_status_dict['tx4bias'] = "N/A"
            transceiver_bulk_status_dict['tx1power'] = transceiver_dom_data_mmv.get(
                self.SFP_EEPROM_TX_PWR_KEY, 'N/A')
            transceiver_bulk_status_dict['tx2power'] = "N/A"
            transceiver_bulk_status_dict['tx3power'] = "N/A"
            transceiver_bulk_status_dict['tx4power'] = "N/A"

        for key in transceiver_bulk_status_dict:
            transceiver_bulk_status_dict[key] = self._convert_string_to_num(
                transceiver_bulk_status_dict[key])

        return transceiver_bulk_status_dict

    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        # SFP doesn't support this feature
        return NotImplementedError

    def get_rx_los(self):
        """
        Retrieves the RX LOS (lost-of-signal) status of SFP
        Returns:
            A Boolean, True if SFP has RX LOS, False if not.
            Note : RX LOS status is latched until a call to get_rx_los or a reset.
        """
        rx_los = False
        rx_los_key = "RXLOSState"
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('dom'):
            transceiver_dom_data = self.eeprom_dict['dom'].get('data', {})
            transceiver_dom_data_sc = transceiver_dom_data.get(
                self.SFP_EEPROM_STATUS_CON_KEY)
            state = transceiver_dom_data_sc.get(rx_los_key)
            rx_los = True if 'off' not in state.lower() else False
        return rx_los

    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP
        Returns:
            A Boolean, True if SFP has TX fault, False if not
            Note : TX fault status is lached until a call to get_tx_fault or a reset.
        """
        tx_fault = False
        tx_fault_key = "TXFaultState"
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('dom'):
            transceiver_dom_data = self.eeprom_dict['dom'].get('data', {})
            transceiver_dom_data_sc = transceiver_dom_data.get(
                self.SFP_EEPROM_STATUS_CON_KEY)
            state = transceiver_dom_data_sc.get(tx_fault_key)
            tx_fault = True if 'off' not in state.lower() else False
        return tx_fault

    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP
        Returns:
            A Boolean, True if tx_disable is enabled, False if disabled
        """
        tx_disable = False
        tx_disable_key = "TXDisableState"
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('dom'):
            transceiver_dom_data = self.eeprom_dict['dom'].get('data', {})
            transceiver_dom_data_sc = transceiver_dom_data.get(
                self.SFP_EEPROM_STATUS_CON_KEY)
            state = transceiver_dom_data_sc.get(tx_disable_key)
            tx_disable = True if 'off' not in state.lower() else False
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
        # SFP doesn't support this feature
        return NotImplementedError

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        # SFP doesn't support this feature
        return self.get_low_power_mode(self.port_num)

    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP
        Returns:
            A Boolean, True if power-override is enabled, False if disabled
        """
        # SFP doesn't support this feature
        return NotImplementedError

    def get_temperature(self):
        """
        Retrieves the temperature of this SFP
        Returns:
            An integer number of current temperature in Celsius
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        return transceiver_dom_info_dict.get("temperature", "N/A")

    def get_voltage(self):
        """
        Retrieves the supply voltage of this SFP
        Returns:
            An integer number of supply voltage in mV
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        return transceiver_dom_info_dict.get("voltage", "N/A")

    def get_tx_bias(self):
        """
        Retrieves the TX bias current of this SFP
        Returns:
            A list of four integer numbers, representing TX bias in mA
            for channel 0 to channel 4.
            Ex. ['110.09', '111.12', '108.21', '112.09']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        tx1_bs = transceiver_dom_info_dict.get("tx1bias", "N/A")
        return [tx1_bs, "N/A", "N/A", "N/A"]

    def get_rx_power(self):
        """
        Retrieves the received optical power for this SFP
        Returns:
            A list of four integer numbers, representing received optical
            power in mW for channel 0 to channel 4.
            Ex. ['1.77', '1.71', '1.68', '1.70']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        rx1_pw = transceiver_dom_info_dict.get("rx1power", "N/A")
        return [rx1_pw, "N/A", "N/A", "N/A"]

    def get_tx_power(self):
        """
        Retrieves the TX power of this SFP
        Returns:
            A list of four integer numbers, representing TX power in mW
            for channel 0 to channel 4.
            Ex. ['1.86', '1.86', '1.86', '1.86']
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        tx1_pw = transceiver_dom_info_dict.get("tx1power", "N/A")
        return [tx1_pw, "N/A", "N/A", "N/A"]

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        # SFP doesn't support this feature
        return NotImplementedError

    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels
        Args:
            tx_disable : A Boolean, True to enable tx_disable mode, False to disable
                         tx_disable mode.
        Returns:
            A boolean, True if tx_disable is set successfully, False if not
        """

        sysfsfile_eeprom = self.__get_sysfsfile_eeprom()
        status_control_raw = self._read_eeprom_specific_bytes(
            sysfsfile_eeprom, self.SFP_STATUS_CONTROL_OFFSET, self.SFP_STATUS_CONTROL_WIDTH)
        if status_control_raw is not None:
            tx_disable_bit = 0x80 if tx_disable else 0x7f
            status_control = int(status_control_raw[0], 16)
            tx_disable_ctl = (status_control | tx_disable_bit) if tx_disable else (
                status_control & tx_disable_bit)
            try:
                buffer = create_string_buffer(1)
                buffer[0] = chr(tx_disable_ctl)
                # Write to eeprom
                sysfsfile_eeprom.seek(self.SFP_STATUS_CONTROL_OFFSET)
                sysfsfile_eeprom.write(buffer[0])
            except IOError as e:
                print "Error: unable to open file: %s" % str(e)
                return False
            finally:
                if sysfsfile_eeprom is not None:
                    sysfsfile_eeprom.close()
                    time.sleep(0.01)
            return True
        return False

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
        # SFP doesn't support this feature
        return NotImplementedError

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override
        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        return self.set_low_power_mode(self.port_num, lpmode)

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
        return NotImplementedError

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return self.logical[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        if self.port_num not in self._sfp_port:
            return False

        status = 1
        try:
            with open(self.PRS_PATH, 'r') as port_status:
                status = int(port_status.read(), 16)
                status = (status >> (self.port_num - 49)) & 1
        except IOError:
            return False

        return status == 0

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        return transceiver_dom_info_dict.get("modelname", "N/A")

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_bulk_status()
        return transceiver_dom_info_dict.get("serialnum", "N/A")
