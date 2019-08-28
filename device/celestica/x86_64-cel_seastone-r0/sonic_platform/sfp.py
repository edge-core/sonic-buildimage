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
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Sfp(SfpBase, SfpUtilBase):
    """Platform-specific Sfp class"""

    # Port number
    PORT_START = 1
    PORT_END = 32
    PORTS_IN_BLOCK = 32

    # Offset for values in QSFP info eeprom
    QSFP_CONTROL_OFFSET = 86
    QSFP_CONTROL_WIDTH = 8
    QSFP_CHANNL_RX_LOS_STATUS_OFFSET = 3
    QSFP_CHANNL_RX_LOS_STATUS_WIDTH = 1
    QSFP_CHANNL_TX_FAULT_STATUS_OFFSET = 4
    QSFP_CHANNL_TX_FAULT_STATUS_WIDTH = 1
    QSFP_POWEROVERRIDE_OFFSET = 93
    QSFP_POWEROVERRIDE_WIDTH = 1

    # Key for values in QSFP eeprom dict
    QSFP_EEPROM_TYPE_KEY = "Identifier"
    QSFP_EEPROM_HW_REV_KEY = "Vendor Rev"
    QSFP_EEPROM_MF_NAME_KEY = "Vendor Name"
    QSFP_EEPROM_MODEL_NAME_KEY = "Vendor PN"
    QSFP_EEPROM_SERIAL_KEY = "Vendor SN"
    QSFP_EEPROM_CONNECTOR_KEY = "Connector"
    QSFP_EEPROM_ENCODE_KEY = "Encoding"
    QSFP_EEPROM_EXT_IDENT_KEY = "Extended Identifier"
    QSFP_EEPROM_EXT_RATE_KEY = "Extended RateSelect Compliance"
    QSFP_EEPROM_CABLE_KEY = "Length(km)"
    QSFP_EEPROM_BIT_RATE_KEY = "Nominal Bit Rate(100Mbs)"
    QSFP_EEPROM_SPEC_COM_KEY = "Specification compliance"
    QSFP_EEPROM_DATE_KEY = "Vendor Date Code(YYYY-MM-DD Lot)"
    QSFP_EEPROM_OUI_KEY = "Vendor OUI"

    # Path to QSFP sysfs
    RESET_PATH = "/sys/devices/platform/dx010_cpld/qsfp_reset"
    LP_PATH = "/sys/devices/platform/dx010_cpld/qsfp_lpmode"
    PRS_PATH = "/sys/devices/platform/dx010_cpld/qsfp_modprs"
    PLATFORM_ROOT_PATH = "/usr/share/sonic/device"
    PMON_HWSKU_PATH = "/usr/share/sonic/hwsku"
    PLATFORM = "x86_64-cel_seastone-r0"
    HWSKU = "Seastone-DX010"
    HOST_CHK_CMD = "docker > /dev/null 2>&1"

    _port_to_eeprom_mapping = {}

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return range(self.PORT_START, self.PORTS_IN_BLOCK + 1)

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
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open(self.LP_PATH, "r")
            content = reg_file.readline().rstrip()
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Determind if port_num start from 1 or 0
        bit_index = port_num - 1 if self.port_start == 1 else port_num

        # Mask off the bit corresponding to our port
        mask = (1 << bit_index)

        # LPMode is active high
        if reg_value & mask == 0:
            return False

        return True

    def set_low_power_mode(self, port_num, lpmode):
        try:
            reg_file = open(self.LP_PATH, "r+")
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        content = reg_file.readline().rstrip()

        # content is a string containing the hex representation of the register
        reg_value = int(content, 16)

        # Determind if port_num start from 1 or 0
        bit_index = port_num - 1 if self.port_start == 1 else port_num

        # Mask off the bit corresponding to our port
        mask = (1 << bit_index)
        # LPMode is active high; set or clear the bit accordingly
        reg_value = reg_value | mask if lpmode else reg_value & ~mask

        # Convert our register value back to a hex string and write back
        content = hex(reg_value).strip('L')

        reg_file.seek(0)
        reg_file.write(content)
        reg_file.close()

        return True

    def get_transceiver_change_event(self, timeout=0):
        raise NotImplementedError

    def __init__(self, sfp_index):
        # Init SfpUtilBase
        eeprom_path = '/sys/bus/i2c/devices/i2c-{0}/{0}-0050/eeprom'

        for x in range(self.PORT_START, self.PORT_END + 1):
            if self.port_start == 1:
                self._port_to_eeprom_mapping[x] = eeprom_path.format(
                    (x - 1) + 26)
            else:
                self._port_to_eeprom_mapping[x] = eeprom_path.format(x + 26)

        self.__read_porttab()
        SfpUtilBase.__init__(self)

        # Init index
        self.index = sfp_index
        self.port_num = self.index + 1

    def __read_porttab(self):
        try:
            self.read_porttab_mappings(self.__get_path_to_port_config_file())
        except:
            pass

    def __is_host(self):
        return os.system(self.HOST_CHK_CMD) == 0

    def __get_path_to_port_config_file(self):
        platform_path = "/".join([self.PLATFORM_ROOT_PATH, self.PLATFORM])
        hwsku_path = "/".join([platform_path, self.HWSKU]
                              ) if self.__is_host() else self.PMON_HWSKU_PATH
        return "/".join([hwsku_path, "port_config.ini"])

    def __read_eeprom_specific_bytes(self, offset, num_bytes):
        sysfsfile_eeprom = None
        eeprom_raw = None
        sysfs_sfp_i2c_client_eeprom_path = self.port_to_eeprom_mapping[self.port_num]
        try:
            sysfsfile_eeprom = open(
                sysfs_sfp_i2c_client_eeprom_path, mode="rb", buffering=0)
        except IOError:
            print("Error: reading sysfs file %s" %
                  sysfs_sfp_i2c_client_eeprom_path)
        finally:
            if sysfsfile_eeprom:
                eeprom_raw = self._read_eeprom_specific_bytes(
                    sysfsfile_eeprom, offset, num_bytes)
                sysfsfile_eeprom.close()
        return eeprom_raw

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
                self.QSFP_EEPROM_SPEC_COM_KEY, {})
            spec_com_str = "/".join(list(spec_com.values()))

            # set normal transceiver info
            transceiver_info_dict['type'] = transceiver_info_data.get(
                self.QSFP_EEPROM_TYPE_KEY, 'N/A')
            transceiver_info_dict['hardwarerev'] = transceiver_info_data.get(
                self.QSFP_EEPROM_HW_REV_KEY, 'N/A')
            transceiver_info_dict['manufacturename'] = transceiver_info_data.get(
                self.QSFP_EEPROM_MF_NAME_KEY, 'N/A')
            transceiver_info_dict['modelname'] = transceiver_info_data.get(
                self.QSFP_EEPROM_MODEL_NAME_KEY, 'N/A')
            transceiver_info_dict['serialnum'] = transceiver_info_data.get(
                self.QSFP_EEPROM_SERIAL_KEY, 'N/A')
            transceiver_info_dict['Connector'] = transceiver_info_data.get(
                self.QSFP_EEPROM_CONNECTOR_KEY, 'N/A')
            transceiver_info_dict['encoding'] = transceiver_info_data.get(
                self.QSFP_EEPROM_ENCODE_KEY, 'N/A')
            transceiver_info_dict['ext_identifier'] = transceiver_info_data.get(
                self.QSFP_EEPROM_EXT_IDENT_KEY, 'N/A')
            transceiver_info_dict['ext_rateselect_compliance'] = transceiver_info_data.get(
                self.QSFP_EEPROM_EXT_RATE_KEY, 'N/A')
            transceiver_info_dict['cable_length'] = transceiver_info_data.get(
                self.QSFP_EEPROM_CABLE_KEY, 'N/A')
            transceiver_info_dict['vendor_date'] = transceiver_info_data.get(
                self.QSFP_EEPROM_DATE_KEY, 'N/A')
            transceiver_info_dict['vendor_oui'] = transceiver_info_data.get(
                self.QSFP_EEPROM_OUI_KEY, 'N/A')
            transceiver_info_dict['nominal_bit_rate'] = transceiver_info_data.get(
                self.QSFP_EEPROM_BIT_RATE_KEY, 'N/A')
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
        transceiver_dom_info_dict = dict()
        self.eeprom_dict = self.get_eeprom_dict(self.port_num)
        if self.eeprom_dict and self.eeprom_dict.get('dom'):
            transceiver_dom_data = self.eeprom_dict['dom'].get('data', {})
            transceiver_dom_data_mmv = transceiver_dom_data.get(
                "ModuleMonitorValues")
            transceiver_dom_data_cmv = transceiver_dom_data.get(
                "ChannelMonitorValues")
            transceiver_dom_info_dict['temperature'] = transceiver_dom_data_mmv.get(
                'Temperature', 'N/A')
            transceiver_dom_info_dict['voltage'] = transceiver_dom_data_mmv.get(
                'Vcc', 'N/A')
            transceiver_dom_info_dict['rx1power'] = transceiver_dom_data_cmv.get(
                'RX1Power', 'N/A')
            transceiver_dom_info_dict['rx2power'] = transceiver_dom_data_cmv.get(
                'RX2Power', 'N/A')
            transceiver_dom_info_dict['rx3power'] = transceiver_dom_data_cmv.get(
                'RX3Power', 'N/A')
            transceiver_dom_info_dict['rx4power'] = transceiver_dom_data_cmv.get(
                'RX4Power', 'N/A')
            transceiver_dom_info_dict['tx1bias'] = transceiver_dom_data_cmv.get(
                'TX1Bias', 'N/A')
            transceiver_dom_info_dict['tx2bias'] = transceiver_dom_data_cmv.get(
                'TX2Bias', 'N/A')
            transceiver_dom_info_dict['tx3bias'] = transceiver_dom_data_cmv.get(
                'TX3Bias', 'N/A')
            transceiver_dom_info_dict['tx4bias'] = transceiver_dom_data_cmv.get(
                'TX4Bias', 'N/A')
            transceiver_dom_info_dict['tx1power'] = transceiver_dom_data_cmv.get(
                'TX1Power', 'N/A')
            transceiver_dom_info_dict['tx2power'] = transceiver_dom_data_cmv.get(
                'TX2Power', 'N/A')
            transceiver_dom_info_dict['tx3power'] = transceiver_dom_data_cmv.get(
                'TX3Power', 'N/A')
            transceiver_dom_info_dict['tx4power'] = transceiver_dom_data_cmv.get(
                'TX4Power', 'N/A')

        for key in transceiver_dom_info_dict:
            transceiver_dom_info_dict[key] = self._convert_string_to_num(
                transceiver_dom_info_dict[key])

        return transceiver_dom_info_dict

    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        try:
            reg_file = open(self.RESET_PATH, "r")
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        content = reg_file.readline().rstrip()
        reg_value = int(content, 16)
        bin_format = bin(reg_value)[2:].zfill(32)
        return bin_format[::-1][self.index] == '0'

    def get_rx_los(self):
        """
        Retrieves the RX LOS (lost-of-signal) status of SFP
        Returns:
            A Boolean, True if SFP has RX LOS, False if not.
            Note : RX LOS status is latched until a call to get_rx_los or a reset.
        """
        rx_los_list = []
        dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
            self.QSFP_CHANNL_RX_LOS_STATUS_OFFSET, self.QSFP_CHANNL_RX_LOS_STATUS_WIDTH) if self.get_presence() else None
        if dom_channel_monitor_raw is not None:
            rx_los_data = int(dom_channel_monitor_raw[0], 16)
            rx_los_list.append(rx_los_data & 0x01 != 0)
            rx_los_list.append(rx_los_data & 0x02 != 0)
            rx_los_list.append(rx_los_data & 0x04 != 0)
            rx_los_list.append(rx_los_data & 0x08 != 0)
        return rx_los_list

    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP
        Returns:
            A Boolean, True if SFP has TX fault, False if not
            Note : TX fault status is lached until a call to get_tx_fault or a reset.
        """
        tx_fault_list = []
        dom_channel_monitor_raw = self.__read_eeprom_specific_bytes(
            self.QSFP_CHANNL_TX_FAULT_STATUS_OFFSET, self.QSFP_CHANNL_TX_FAULT_STATUS_WIDTH) if self.get_presence() else None
        if dom_channel_monitor_raw is not None:
            tx_fault_data = int(dom_channel_monitor_raw[0], 16)
            tx_fault_list.append(tx_fault_data & 0x01 != 0)
            tx_fault_list.append(tx_fault_data & 0x02 != 0)
            tx_fault_list.append(tx_fault_data & 0x04 != 0)
            tx_fault_list.append(tx_fault_data & 0x08 != 0)
        return tx_fault_list

    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP
        Returns:
            A Boolean, True if tx_disable is enabled, False if disabled
        """
        tx_disable_list = []

        sfpd_obj = sff8436Dom()
        if sfpd_obj is None:
            return False

        dom_control_raw = self.__read_eeprom_specific_bytes(
            self.QSFP_CONTROL_OFFSET, self.QSFP_CONTROL_WIDTH) if self.get_presence() else None
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

    def get_tx_disable_channel(self):
        """
        Retrieves the TX disabled channels in this SFP
        Returns:
            A hex of 4 bits (bit 0 to bit 3 as channel 0 to channel 3) to represent
            TX channels which have been disabled in this SFP.
            As an example, a returned value of 0x5 indicates that channel 0
            and channel 2 have been disabled.
        """
        tx_disable_list = self.get_tx_disable()
        if tx_disable_list is None:
            return 0
        tx_disabled = 0
        for i in range(len(tx_disable_list)):
            if tx_disable_list[i]:
                tx_disabled |= 1 << i
        return tx_disabled

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        return self.get_low_power_mode(self.port_num)

    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP
        Returns:
            A Boolean, True if power-override is enabled, False if disabled
        """
        power_override = False

        offset = 0
        sfpd_obj = sff8436Dom()
        if sfpd_obj is None:
            return False

        dom_control_raw = self.__read_eeprom_specific_bytes(
            self.QSFP_CONTROL_OFFSET, self.QSFP_CONTROL_WIDTH) if self.get_presence() else None
        if dom_control_raw is not None:
            dom_control_data = sfpd_obj.parse_control_bytes(dom_control_raw, 0)
            power_override = (
                'On' == dom_control_data['data']['PowerOverride']['value'])

        return power_override

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
        tx2_bs = transceiver_dom_info_dict.get("tx2bias", "N/A")
        tx3_bs = transceiver_dom_info_dict.get("tx3bias", "N/A")
        tx4_bs = transceiver_dom_info_dict.get("tx4bias", "N/A")
        return [tx1_bs, tx2_bs, tx3_bs, tx4_bs] if transceiver_dom_info_dict else []

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
        rx2_pw = transceiver_dom_info_dict.get("rx2power", "N/A")
        rx3_pw = transceiver_dom_info_dict.get("rx3power", "N/A")
        rx4_pw = transceiver_dom_info_dict.get("rx4power", "N/A")
        return [rx1_pw, rx2_pw, rx3_pw, rx4_pw] if transceiver_dom_info_dict else []

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
        tx2_pw = transceiver_dom_info_dict.get("tx2power", "N/A")
        tx3_pw = transceiver_dom_info_dict.get("tx3power", "N/A")
        tx4_pw = transceiver_dom_info_dict.get("tx4power", "N/A")
        return [tx1_pw, tx2_pw, tx3_pw, tx4_pw] if transceiver_dom_info_dict else []

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        # Check for invalid port_num

        try:
            reg_file = open(self.RESET_PATH, "r+")
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        content = reg_file.readline().rstrip()

        # File content is a string containing the hex representation of the
        # register
        reg_value = int(content, 16)

        # Determind if port_num start from 1 or 0
        bit_index = self.port_num - 1 if self.port_start == 1 else self.port_num

        # Mask off the bit corresponding to our port
        mask = (1 << bit_index)

        # ResetL is active low
        reg_value = reg_value & ~mask

        # Convert our register value back to a hex string and write back
        reg_file.seek(0)
        reg_file.write(hex(reg_value).rstrip('L'))
        reg_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        # Flip the bit back high and write back to the register to take port out of reset
        try:
            reg_file = open(self.RESET_PATH, "w")
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        reg_value = reg_value | mask
        reg_file.seek(0)
        reg_file.write(hex(reg_value).rstrip('L'))
        reg_file.close()

        return True

    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels
        Args:
            tx_disable : A Boolean, True to enable tx_disable mode, False to disable
                         tx_disable mode.
        Returns:
            A boolean, True if tx_disable is set successfully, False if not
        """
        sysfsfile_eeprom = None
        try:
            tx_disable_ctl = 0xf if tx_disable else 0x0
            buffer = create_string_buffer(1)
            buffer[0] = chr(tx_disable_ctl)
            # Write to eeprom
            sysfsfile_eeprom = open(
                self.port_to_eeprom_mapping[self.port_num], "r+b")
            sysfsfile_eeprom.seek(self.QSFP_CONTROL_OFFSET)
            sysfsfile_eeprom.write(buffer[0])
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if sysfsfile_eeprom is not None:
                sysfsfile_eeprom.close()
                time.sleep(0.01)
        return True

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
        sysfsfile_eeprom = None
        try:
            channel_state = self.get_tx_disable_channel()
            tx_enable_mask = [0xe, 0xd, 0xb, 0x7]
            tx_disable_mask = [0x1, 0x3, 0x7, 0xf]
            tx_disable_ctl = channel_state | tx_disable_mask[
                channel] if disable else channel_state & tx_enable_mask[channel]
            buffer = create_string_buffer(1)
            buffer[0] = chr(tx_disable_ctl)
            # Write to eeprom
            sysfsfile_eeprom = open(
                self.port_to_eeprom_mapping[self.port_num], "r+b")
            sysfsfile_eeprom.seek(self.QSFP_CONTROL_OFFSET)
            sysfsfile_eeprom.write(buffer[0])
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if sysfsfile_eeprom is not None:
                sysfsfile_eeprom.close()
                time.sleep(0.01)
        return True

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
            sysfsfile_eeprom = open(
                self.port_to_eeprom_mapping[self.port_num], "r+b")
            sysfsfile_eeprom.seek(self.QSFP_POWEROVERRIDE_OFFSET)
            sysfsfile_eeprom.write(buffer[0])
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False
        finally:
            if sysfsfile_eeprom is not None:
                sysfsfile_eeprom.close()
                time.sleep(0.01)
        return True

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
        try:
            reg_file = open(self.PRS_PATH, "r")
        except IOError as e:
            print("Error: unable to open file: %s" % str(e))
            return False

        content = reg_file.readline().rstrip()
        reg_value = int(content, 16)

        # Determind if port_num start from 1 or 0
        bit_index = self.port_num - 1 if self.port_start == 1 else self.port_num

        # Mask off the bit corresponding to our port
        mask = (1 << bit_index)

        # ModPrsL is active low
        if reg_value & mask == 0:
            return True

        return False

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_info()
        return transceiver_dom_info_dict.get("modelname", "N/A")

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        transceiver_dom_info_dict = self.get_transceiver_info()
        return transceiver_dom_info_dict.get("serialnum", "N/A")
