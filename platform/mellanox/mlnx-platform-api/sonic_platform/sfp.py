#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the FANs status which are available in the platform
#
#############################################################################

try:
    import os
    import subprocess
    import time
    from sonic_platform_base.sfp_base import SfpBase
    from sonic_platform_base.sonic_eeprom import eeprom_dts
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472InterfaceId
    from sonic_platform_base.sonic_sfp.sff8472 import sff8472Dom
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom
    from sonic_platform_base.sonic_sfp.inf8628 import inf8628InterfaceId
    from sonic_platform_base.sonic_sfp.qsfp_dd import qsfp_dd_InterfaceId
    from sonic_platform_base.sonic_sfp.qsfp_dd import qsfp_dd_Dom
    from sonic_py_common.logger import Logger
    from python_sdk_api.sxd_api import *
    from python_sdk_api.sx_api import *

except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

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
XCVR_EXT_SPECIFICATION_COMPLIANCE_OFFSET = 64
XCVR_EXT_SPECIFICATION_COMPLIANCE_WIDTH = 1
XCVR_VENDOR_SN_OFFSET = 68
XCVR_VENDOR_SN_WIDTH = 16
XCVR_VENDOR_DATE_OFFSET = 84
XCVR_VENDOR_DATE_WIDTH = 8
XCVR_DOM_CAPABILITY_OFFSET = 92
XCVR_DOM_CAPABILITY_WIDTH = 2

# definitions of the offset and width for values in XCVR_QSFP_DD info eeprom
XCVR_EXT_TYPE_OFFSET_QSFP_DD = 72
XCVR_EXT_TYPE_WIDTH_QSFP_DD = 2
XCVR_CONNECTOR_OFFSET_QSFP_DD = 75
XCVR_CONNECTOR_WIDTH_QSFP_DD = 1
XCVR_CABLE_LENGTH_OFFSET_QSFP_DD = 74
XCVR_CABLE_LENGTH_WIDTH_QSFP_DD = 1
XCVR_HW_REV_OFFSET_QSFP_DD = 36
XCVR_HW_REV_WIDTH_QSFP_DD = 2
XCVR_VENDOR_DATE_OFFSET_QSFP_DD = 54
XCVR_VENDOR_DATE_WIDTH_QSFP_DD = 8
XCVR_DOM_CAPABILITY_OFFSET_QSFP_DD = 2
XCVR_DOM_CAPABILITY_WIDTH_QSFP_DD = 1
XCVR_MEDIA_TYPE_OFFSET_QSFP_DD = 85
XCVR_MEDIA_TYPE_WIDTH_QSFP_DD = 1
XCVR_FIRST_APPLICATION_LIST_OFFSET_QSFP_DD = 86
XCVR_FIRST_APPLICATION_LIST_WIDTH_QSFP_DD = 32
XCVR_SECOND_APPLICATION_LIST_OFFSET_QSFP_DD = 351
XCVR_SECOND_APPLICATION_LIST_WIDTH_QSFP_DD = 28

# to improve performance we retrieve all eeprom data via a single ethtool command
# in function get_transceiver_info and get_transceiver_bulk_status
# XCVR_INTERFACE_DATA_SIZE stands for the max size to be read
# this variable is only used by get_transceiver_info.
# please be noted that each time some new value added to the function 
# we should make sure that it falls into the area 
# [XCVR_INTERFACE_DATA_START, XCVR_INTERFACE_DATA_SIZE] or
# adjust XCVR_INTERFACE_MAX_SIZE to contain the new data
# It's same for [QSFP_DOM_BULK_DATA_START, QSFP_DOM_BULK_DATA_SIZE] and
# [SFP_DOM_BULK_DATA_START, SFP_DOM_BULK_DATA_SIZE] which are used by
# get_transceiver_bulk_status
XCVR_INTERFACE_DATA_START = 0
XCVR_INTERFACE_DATA_SIZE = 92
SFP_MODULE_ADDRA2_OFFSET = 256
SFP_MODULE_THRESHOLD_OFFSET = 0
SFP_MODULE_THRESHOLD_WIDTH = 56

QSFP_DOM_BULK_DATA_START = 22
QSFP_DOM_BULK_DATA_SIZE = 36
SFP_DOM_BULK_DATA_START = 96
SFP_DOM_BULK_DATA_SIZE = 10

QSFP_DD_DOM_BULK_DATA_START = 14
QSFP_DD_DOM_BULK_DATA_SIZE = 4

# definitions of the offset for values in OSFP info eeprom
OSFP_TYPE_OFFSET = 0
OSFP_VENDOR_NAME_OFFSET = 129
OSFP_VENDOR_PN_OFFSET = 148
OSFP_HW_REV_OFFSET = 164
OSFP_VENDOR_SN_OFFSET = 166

# definitions of the offset for values in QSFP_DD info eeprom
QSFP_DD_TYPE_OFFSET = 0
QSFP_DD_VENDOR_NAME_OFFSET = 1
QSFP_DD_VENDOR_PN_OFFSET = 20
QSFP_DD_VENDOR_SN_OFFSET = 38
QSFP_DD_VENDOR_OUI_OFFSET = 17

#definitions of the offset and width for values in DOM info eeprom
QSFP_DOM_REV_OFFSET = 1
QSFP_DOM_REV_WIDTH = 1
QSFP_TEMPE_OFFSET = 22
QSFP_TEMPE_WIDTH = 2
QSFP_VOLT_OFFSET = 26
QSFP_VOLT_WIDTH = 2
QSFP_VERSION_COMPLIANCE_OFFSET = 1
QSFP_VERSION_COMPLIANCE_WIDTH = 2
QSFP_CHANNL_MON_OFFSET = 34
QSFP_CHANNL_MON_WIDTH = 16
QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH = 24
QSFP_CHANNL_DISABLE_STATUS_OFFSET = 86
QSFP_CHANNL_DISABLE_STATUS_WIDTH = 1
QSFP_CHANNL_RX_LOS_STATUS_OFFSET = 3
QSFP_CHANNL_RX_LOS_STATUS_WIDTH = 1
QSFP_CHANNL_TX_FAULT_STATUS_OFFSET = 4
QSFP_CHANNL_TX_FAULT_STATUS_WIDTH = 1
QSFP_CONTROL_OFFSET = 86
QSFP_CONTROL_WIDTH = 8
QSFP_MODULE_MONITOR_OFFSET = 0
QSFP_MODULE_MONITOR_WIDTH = 9
QSFP_POWEROVERRIDE_OFFSET = 93
QSFP_POWEROVERRIDE_WIDTH = 1
QSFP_POWEROVERRIDE_BIT = 0
QSFP_POWERSET_BIT = 1
QSFP_OPTION_VALUE_OFFSET = 192
QSFP_OPTION_VALUE_WIDTH = 4

QSFP_MODULE_UPPER_PAGE3_START = 384
QSFP_MODULE_THRESHOLD_OFFSET = 128
QSFP_MODULE_THRESHOLD_WIDTH = 24
QSFP_CHANNL_THRESHOLD_OFFSET = 176
QSFP_CHANNL_THRESHOLD_WIDTH = 24

SFP_TEMPE_OFFSET = 96
SFP_TEMPE_WIDTH = 2
SFP_VOLT_OFFSET = 98
SFP_VOLT_WIDTH = 2
SFP_CHANNL_MON_OFFSET = 100
SFP_CHANNL_MON_WIDTH = 6
SFP_CHANNL_STATUS_OFFSET = 110
SFP_CHANNL_STATUS_WIDTH = 1

QSFP_DD_TEMPE_OFFSET = 14
QSFP_DD_TEMPE_WIDTH = 2
QSFP_DD_VOLT_OFFSET = 16
QSFP_DD_VOLT_WIDTH = 2
QSFP_DD_TX_BIAS_OFFSET = 42
QSFP_DD_TX_BIAS_WIDTH = 16
QSFP_DD_RX_POWER_OFFSET = 58
QSFP_DD_RX_POWER_WIDTH = 16
QSFP_DD_TX_POWER_OFFSET = 26
QSFP_DD_TX_POWER_WIDTH = 16
QSFP_DD_CHANNL_MON_OFFSET = 154
QSFP_DD_CHANNL_MON_WIDTH = 48
QSFP_DD_CHANNL_DISABLE_STATUS_OFFSET = 86
QSFP_DD_CHANNL_DISABLE_STATUS_WIDTH = 1
QSFP_DD_CHANNL_RX_LOS_STATUS_OFFSET = 19
QSFP_DD_CHANNL_RX_LOS_STATUS_WIDTH = 1
QSFP_DD_CHANNL_TX_FAULT_STATUS_OFFSET = 7
QSFP_DD_CHANNL_TX_FAULT_STATUS_WIDTH = 1
QSFP_DD_MODULE_THRESHOLD_OFFSET = 0
QSFP_DD_MODULE_THRESHOLD_WIDTH = 72
QSFP_DD_CHANNL_STATUS_OFFSET = 26
QSFP_DD_CHANNL_STATUS_WIDTH = 1

# identifier value of xSFP module which is in the first byte of the EEPROM
# if the identifier value falls into SFP_TYPE_CODE_LIST the module is treated as a SFP module and parsed according to 8472
# for QSFP_TYPE_CODE_LIST the module is treated as a QSFP module and parsed according to 8436/8636
# Originally the type (SFP/QSFP) of each module is determined according to the SKU dictionary 
# where the type of each FP port is defined. The content of EEPROM is parsed according to its type.
# However, sometimes the SFP module can be fit in an adapter and then pluged into a QSFP port.
# In this case the EEPROM content is in format of SFP but parsed as QSFP, causing failure.
# To resolve that issue the type field of the xSFP module is also fetched so that we can know exectly what type the 
# module is. Currently only the following types are recognized as SFP/QSFP module. 
# Meanwhile, if the a module's identifier value can't be recognized, it will be parsed according to the SKU dictionary.
# This is because in the future it's possible that some new identifier value which is not regonized but backward compatible
# with the current format and by doing so it can be parsed as much as possible.
SFP_TYPE_CODE_LIST = [
    '03' # SFP/SFP+/SFP28
]
QSFP_TYPE_CODE_LIST = [
    '0d', # QSFP+ or later
    '11' # QSFP28 or later
]
QSFP_DD_TYPE_CODE_LIST = [
    '18' # QSFP-DD Double Density 8X Pluggable Transceiver
]

qsfp_cable_length_tup = ('Length(km)', 'Length OM3(2m)', 
                         'Length OM2(m)', 'Length OM1(m)',
                         'Length Cable Assembly(m)')

sfp_cable_length_tup = ('LengthSMFkm-UnitsOfKm', 'LengthSMF(UnitsOf100m)',
                        'Length50um(UnitsOf10m)', 'Length62.5um(UnitsOfm)',
                        'LengthCable(UnitsOfm)', 'LengthOM3(UnitsOf10m)')

sfp_compliance_code_tup = ('10GEthernetComplianceCode', 'InfinibandComplianceCode', 
                            'ESCONComplianceCodes', 'SONETComplianceCodes',
                            'EthernetComplianceCodes','FibreChannelLinkLength',
                            'FibreChannelTechnology', 'SFP+CableTechnology',
                            'FibreChannelTransmissionMedia','FibreChannelSpeed')

qsfp_compliance_code_tup = ('10/40G Ethernet Compliance Code', 'SONET Compliance codes',
                            'SAS/SATA compliance codes', 'Gigabit Ethernet Compliant codes',
                            'Fibre Channel link length/Transmitter Technology',
                            'Fibre Channel transmission media', 'Fibre Channel Speed')

SFP_PATH = "/var/run/hw-management/qsfp/"
SFP_TYPE = "SFP"
QSFP_TYPE = "QSFP"
OSFP_TYPE = "OSFP"
QSFP_DD_TYPE = "QSFP_DD"

#variables for sdk
REGISTER_NUM = 1
DEVICE_ID = 1
SWITCH_ID = 0
SX_PORT_ATTR_ARR_SIZE = 64

PMAOS_ASE = 1
PMAOS_EE = 1
PMAOS_E = 2
PMAOS_RST = 0
PMAOS_ENABLE = 1
PMAOS_DISABLE = 2

PMMP_LPMODE_BIT = 8
MCION_TX_DISABLE_BIT = 1

#on page 0
#i2c address 0x50
MCIA_ADDR_TX_CHANNEL_DISABLE = 86

MCIA_ADDR_POWER_OVERRIDE = 93
#power set bit
MCIA_ADDR_POWER_OVERRIDE_PS_BIT = 1
#power override bit
MCIA_ADDR_POWER_OVERRIDE_POR_BIT = 0

#on page 0
#i2c address 0x51
MCIA_ADDR_TX_DISABLE = 110
MCIA_ADDR_TX_DISABLE_BIT = 6

PORT_TYPE_NVE = 8
PORT_TYPE_OFFSET = 28
PORT_TYPE_MASK = 0xF0000000
NVE_MASK = PORT_TYPE_MASK & (PORT_TYPE_NVE << PORT_TYPE_OFFSET)

# Global logger class instance
logger = Logger()

class SFP(SfpBase):
    """Platform-specific SFP class"""

    def __init__(self, sfp_index, sfp_type):
        self.index = sfp_index + 1
        self.sfp_eeprom_path = "qsfp{}".format(self.index)
        self.sfp_status_path = "qsfp{}_status".format(self.index)
        self._detect_sfp_type(sfp_type)
        self.dom_tx_disable_supported = False
        self._dom_capability_detect()
        self.sdk_handle = None
        self.sdk_index = sfp_index


    #SDK initializing stuff
    def _initialize_sdk_handle(self):
        """
        reference: device\mellanox\<sku>\pulgins\sfpreset.py
        """
        rc, self.sdk_handle = sx_api_open(None)
        if (rc != SX_STATUS_SUCCESS):
            logger.log_warning("Failed to open api handle, please check whether SDK is running.")
            self.sdk_handle = None

        self.mypid = os.getpid()


    def _open_sdk(self):
        if self.sdk_handle is None:
            self._initialize_sdk_handle()

        rc = sxd_access_reg_init(self.mypid, None, 0)
        if rc != 0:
            logger.log_warning("Failed to initializing register access, please check that SDK is running.")
            return False

        return True


    def _close_sdk(self):
        rc = sxd_access_reg_deinit()
        if rc != 0:
            logger.log_warning("Failed to deinitializing register access.")
            #no further actions here


    def _init_sx_meta_data(self):
        meta = sxd_reg_meta_t()
        meta.dev_id = DEVICE_ID
        meta.swid = SWITCH_ID
        return meta


    def get_presence(self):
        """
        Retrieves the presence of the device

        Returns:
            bool: True if device is present, False if not
        """
        presence = False
        ethtool_cmd = "ethtool -m sfp{} hex on offset 0 length 1 2>/dev/null".format(self.index)
        try:
            proc = subprocess.Popen(ethtool_cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            result = stdout.rstrip('\n')
            if result != '':
                presence = True

        except OSError, e:
            raise OSError("Cannot detect sfp")

        return presence


    # Read out any bytes from any offset
    def _read_eeprom_specific_bytes(self, offset, num_bytes):
        eeprom_raw = []
        ethtool_cmd = "ethtool -m sfp{} hex on offset {} length {}".format(self.index, offset, num_bytes)
        try:
            output = subprocess.check_output(ethtool_cmd, shell=True)
            output_lines = output.splitlines()
            first_line_raw = output_lines[0]
            if "Offset" in first_line_raw:
                for line in output_lines[2:]:
                    line_split = line.split()
                    eeprom_raw = eeprom_raw + line_split[1:]
        except subprocess.CalledProcessError as e:
            return None

        return eeprom_raw


    def _detect_sfp_type(self, sfp_type):
        eeprom_raw = []
        eeprom_raw = self._read_eeprom_specific_bytes(XCVR_TYPE_OFFSET, XCVR_TYPE_WIDTH)
        if eeprom_raw:
            if eeprom_raw[0] in SFP_TYPE_CODE_LIST:
                self.sfp_type = SFP_TYPE
            elif eeprom_raw[0] in QSFP_TYPE_CODE_LIST:
                self.sfp_type = QSFP_TYPE
            elif eeprom_raw[0] in QSFP_DD_TYPE_CODE_LIST:
                self.sfp_type = QSFP_DD_TYPE
            else:
                # we don't regonize this identifier value, treat the xSFP module as the default type
                self.sfp_type = sfp_type
                logger.log_info("Identifier value of {} module {} is {} which isn't regonized and will be treated as default type ({})".format(
                    sfp_type, self.index, eeprom_raw[0], sfp_type
                ))
        else:
            # eeprom_raw being None indicates the module is not present.
            # in this case we treat it as the default type according to the SKU
            self.sfp_type = sfp_type


    def _dom_capability_detect(self):
        if not self.get_presence():
            self.dom_supported = False
            self.dom_temp_supported = False
            self.dom_volt_supported = False
            self.dom_rx_power_supported = False
            self.dom_tx_bias_power_supported = False
            self.dom_tx_power_supported = False
            self.calibration = 0
            return

        if self.sfp_type == QSFP_TYPE:
            self.calibration = 1
            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                self.dom_supported = False
            offset = 128

            # QSFP capability byte parse, through this byte can know whether it support tx_power or not.
            # TODO: in the future when decided to migrate to support SFF-8636 instead of SFF-8436,
            # need to add more code for determining the capability and version compliance
            # in SFF-8636 dom capability definitions evolving with the versions.
            qsfp_dom_capability_raw = self._read_eeprom_specific_bytes((offset + XCVR_DOM_CAPABILITY_OFFSET), XCVR_DOM_CAPABILITY_WIDTH)
            if qsfp_dom_capability_raw is not None:
                qsfp_version_compliance_raw = self._read_eeprom_specific_bytes(QSFP_VERSION_COMPLIANCE_OFFSET, QSFP_VERSION_COMPLIANCE_WIDTH)
                qsfp_version_compliance = int(qsfp_version_compliance_raw[0], 16)
                dom_capability = sfpi_obj.parse_qsfp_dom_capability(qsfp_dom_capability_raw, 0)
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
                qsfp_option_value_raw = self._read_eeprom_specific_bytes(QSFP_OPTION_VALUE_OFFSET, QSFP_OPTION_VALUE_WIDTH)
                if qsfp_option_value_raw is not None:
                    optional_capability = sfpd_obj.parse_option_params(qsfp_option_value_raw, 0)
                    self.dom_tx_disable_supported = optional_capability['data']['TxDisable']['value'] == 'On'
                dom_status_indicator = sfpd_obj.parse_dom_status_indicator(qsfp_version_compliance_raw, 1)
                self.qsfp_page3_available = dom_status_indicator['data']['FlatMem']['value'] == 'Off'
            else:
                self.dom_supported = False
                self.dom_temp_supported = False
                self.dom_volt_supported = False
                self.dom_rx_power_supported = False
                self.dom_tx_power_supported = False
                self.calibration = 0
                self.qsfp_page3_available = False

        elif self.sfp_type == QSFP_DD_TYPE:
            sfpi_obj = qsfp_dd_InterfaceId()
            if sfpi_obj is None:
                self.dom_supported = False

            offset = 0
            # two types of QSFP-DD cable types supported: Copper and Optical.
            qsfp_dom_capability_raw = self._read_eeprom_specific_bytes((offset + XCVR_DOM_CAPABILITY_OFFSET_QSFP_DD), XCVR_DOM_CAPABILITY_WIDTH_QSFP_DD)
            if qsfp_dom_capability_raw is not None:
                self.dom_temp_supported = True
                self.dom_volt_supported = True
                dom_capability = sfpi_obj.parse_qsfp_dom_capability(qsfp_dom_capability_raw, 0)
                if dom_capability['data']['Flat_MEM']['value'] == 'Off':
                    self.dom_supported = True
                    self.second_application_list = True
                    self.dom_rx_power_supported = True
                    self.dom_tx_power_supported = True
                    self.dom_tx_bias_power_supported = True
                    self.dom_thresholds_supported = True
                    #currently set to False becasue Page 11h is not supported by FW
                    self.dom_rx_tx_power_bias_supported = False
                else:
                    self.dom_supported = False
                    self.second_application_list = False
                    self.dom_rx_power_supported = False
                    self.dom_tx_power_supported = False
                    self.dom_tx_bias_power_supported = False
                    self.dom_thresholds_supported = False
                    self.dom_rx_tx_power_bias_supported = False
            else:
                self.dom_supported = False
                self.dom_temp_supported = False
                self.dom_volt_supported = False
                self.dom_rx_power_supported = False
                self.dom_tx_power_supported = False
                self.dom_tx_bias_power_supported = False
                self.dom_thresholds_supported = False
                self.dom_rx_tx_power_bias_supported = False

        elif self.sfp_type == SFP_TYPE:
            sfpi_obj = sff8472InterfaceId()
            if sfpi_obj is None:
                return None
            sfp_dom_capability_raw = self._read_eeprom_specific_bytes(XCVR_DOM_CAPABILITY_OFFSET, XCVR_DOM_CAPABILITY_WIDTH)
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
                self.dom_tx_disable_supported = (int(sfp_dom_capability_raw[1], 16) & 0x40 != 0)
        else:
            self.dom_supported = False
            self.dom_temp_supported = False
            self.dom_volt_supported = False
            self.dom_rx_power_supported = False
            self.dom_tx_power_supported = False


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


    def get_transceiver_info(self):
        """
        Retrieves transceiver info of this SFP

        Returns:
            A dict which contains following keys/values :
        ================================================================================
        keys                       |Value Format   |Information	
        ---------------------------|---------------|----------------------------
        type                       |1*255VCHAR     |type of SFP
        hardware_rev               |1*255VCHAR     |hardware version of SFP
        serial                     |1*255VCHAR     |serial number of the SFP
        manufacturer               |1*255VCHAR     |SFP vendor name
        model                      |1*255VCHAR     |SFP model name
        connector                  |1*255VCHAR     |connector information
        encoding                   |1*255VCHAR     |encoding information
        ext_identifier             |1*255VCHAR     |extend identifier
        ext_rateselect_compliance  |1*255VCHAR     |extended rateSelect compliance
        cable_length               |INT            |cable length in m
        mominal_bit_rate           |INT            |nominal bit rate by 100Mbs
        specification_compliance   |1*255VCHAR     |specification compliance
        vendor_date                |1*255VCHAR     |vendor date
        vendor_oui                 |1*255VCHAR     |vendor OUI
        application_advertisement  |1*255VCHAR     |supported applications advertisement
        ================================================================================
        """
        transceiver_info_dict = {}
        compliance_code_dict = {}

        # ToDo: OSFP tranceiver info parsing not fully supported.
        # in inf8628.py lack of some memory map definition
        # will be implemented when the inf8628 memory map ready
        if self.sfp_type == OSFP_TYPE:
            offset = 0
            vendor_rev_width = XCVR_HW_REV_WIDTH_OSFP

            sfpi_obj = inf8628InterfaceId()
            if sfpi_obj is None:
                return None

            sfp_type_raw = self._read_eeprom_specific_bytes((offset + OSFP_TYPE_OFFSET), XCVR_TYPE_WIDTH)
            if sfp_type_raw is not None:
                sfp_type_data = sfpi_obj.parse_sfp_type(sfp_type_raw, 0)
            else:
                return None

            sfp_vendor_name_raw = self._read_eeprom_specific_bytes((offset + OSFP_VENDOR_NAME_OFFSET), XCVR_VENDOR_NAME_WIDTH)
            if sfp_vendor_name_raw is not None:
                sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_vendor_name_raw, 0)
            else:
                return None

            sfp_vendor_pn_raw = self._read_eeprom_specific_bytes((offset + OSFP_VENDOR_PN_OFFSET), XCVR_VENDOR_PN_WIDTH)
            if sfp_vendor_pn_raw is not None:
                sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_vendor_pn_raw, 0)
            else:
                return None

            sfp_vendor_rev_raw = self._read_eeprom_specific_bytes((offset + OSFP_HW_REV_OFFSET), vendor_rev_width)
            if sfp_vendor_rev_raw is not None:
                sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_vendor_rev_raw, 0)
            else:
                return None

            sfp_vendor_sn_raw = self._read_eeprom_specific_bytes((offset + OSFP_VENDOR_SN_OFFSET), XCVR_VENDOR_SN_WIDTH)
            if sfp_vendor_sn_raw is not None:
                sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_vendor_sn_raw, 0)
            else:
                return None

            transceiver_info_dict['type'] = sfp_type_data['data']['type']['value']
            transceiver_info_dict['manufacturer'] = sfp_vendor_name_data['data']['Vendor Name']['value']
            transceiver_info_dict['model'] = sfp_vendor_pn_data['data']['Vendor PN']['value']
            transceiver_info_dict['hardware_rev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value']
            transceiver_info_dict['serial'] = sfp_vendor_sn_data['data']['Vendor SN']['value']
            transceiver_info_dict['vendor_oui'] = 'N/A'
            transceiver_info_dict['vendor_date'] = 'N/A'
            transceiver_info_dict['connector'] = 'N/A'
            transceiver_info_dict['encoding'] = 'N/A'
            transceiver_info_dict['ext_identifier'] = 'N/A'
            transceiver_info_dict['ext_rateselect_compliance'] = 'N/A'
            transceiver_info_dict['cable_type'] = 'N/A'
            transceiver_info_dict['cable_length'] = 'N/A'
            transceiver_info_dict['specification_compliance'] = 'N/A'
            transceiver_info_dict['nominal_bit_rate'] = 'N/A'
            transceiver_info_dict['application_advertisement'] = 'N/A'

        elif self.sfp_type == QSFP_TYPE:
            offset = 128
            vendor_rev_width = XCVR_HW_REV_WIDTH_QSFP
            cable_length_width = XCVR_CABLE_LENGTH_WIDTH_QSFP
            interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_QSFP
            sfp_type = 'QSFP'

            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                print("Error: sfp_object open failed")
                return None

        elif self.sfp_type == QSFP_DD_TYPE:
            offset = 128

            sfpi_obj = qsfp_dd_InterfaceId()
            if sfpi_obj is None:
                print("Error: sfp_object open failed")
                return None

            sfp_type_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_TYPE_OFFSET), XCVR_TYPE_WIDTH)
            if sfp_type_raw is not None:
                sfp_type_data = sfpi_obj.parse_sfp_type(sfp_type_raw, 0)
            else:
                return None

            sfp_vendor_name_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_VENDOR_NAME_OFFSET), XCVR_VENDOR_NAME_WIDTH)
            if sfp_vendor_name_raw is not None:
                sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_vendor_name_raw, 0)
            else:
                return None

            sfp_vendor_pn_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_VENDOR_PN_OFFSET), XCVR_VENDOR_PN_WIDTH)
            if sfp_vendor_pn_raw is not None:
                sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_vendor_pn_raw, 0)
            else:
                return None

            sfp_vendor_rev_raw = self._read_eeprom_specific_bytes((offset + XCVR_HW_REV_OFFSET_QSFP_DD), XCVR_HW_REV_WIDTH_QSFP_DD)
            if sfp_vendor_rev_raw is not None:
                sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_vendor_rev_raw, 0)
            else:
                return None

            sfp_vendor_sn_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_VENDOR_SN_OFFSET), XCVR_VENDOR_SN_WIDTH)
            if sfp_vendor_sn_raw is not None:
                sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_vendor_sn_raw, 0)
            else:
                return None

            sfp_vendor_oui_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_VENDOR_OUI_OFFSET), XCVR_VENDOR_OUI_WIDTH)
            if sfp_vendor_oui_raw is not None:
                sfp_vendor_oui_data = sfpi_obj.parse_vendor_oui(sfp_vendor_oui_raw, 0)
            else:
                return None

            sfp_vendor_date_raw = self._read_eeprom_specific_bytes((offset + XCVR_VENDOR_DATE_OFFSET_QSFP_DD), XCVR_VENDOR_DATE_WIDTH_QSFP_DD)
            if sfp_vendor_date_raw is not None:
                sfp_vendor_date_data = sfpi_obj.parse_vendor_date(sfp_vendor_date_raw, 0)
            else:
                return None

            sfp_connector_raw = self._read_eeprom_specific_bytes((offset + XCVR_CONNECTOR_OFFSET_QSFP_DD), XCVR_CONNECTOR_WIDTH_QSFP_DD)
            if sfp_connector_raw is not None:
                sfp_connector_data = sfpi_obj.parse_connector(sfp_connector_raw, 0)
            else:
                return None

            sfp_ext_identifier_raw = self._read_eeprom_specific_bytes((offset + XCVR_EXT_TYPE_OFFSET_QSFP_DD), XCVR_EXT_TYPE_WIDTH_QSFP_DD)
            if sfp_ext_identifier_raw is not None:
                sfp_ext_identifier_data = sfpi_obj.parse_ext_iden(sfp_ext_identifier_raw, 0)
            else:
                return None

            sfp_cable_len_raw = self._read_eeprom_specific_bytes((offset + XCVR_CABLE_LENGTH_OFFSET_QSFP_DD), XCVR_CABLE_LENGTH_WIDTH_QSFP_DD)
            if sfp_cable_len_raw is not None:
                sfp_cable_len_data = sfpi_obj.parse_cable_len(sfp_cable_len_raw, 0)
            else:
                return None
            
            sfp_media_type_raw = self._read_eeprom_specific_bytes(XCVR_MEDIA_TYPE_OFFSET_QSFP_DD, XCVR_MEDIA_TYPE_WIDTH_QSFP_DD)
            if sfp_media_type_raw is not None:
                sfp_media_type_dict = sfpi_obj.parse_media_type(sfp_media_type_raw, 0)
                if sfp_media_type_dict is None:
                    return None

                host_media_list = ""
                sfp_application_type_first_list = self._read_eeprom_specific_bytes((XCVR_FIRST_APPLICATION_LIST_OFFSET_QSFP_DD), XCVR_FIRST_APPLICATION_LIST_WIDTH_QSFP_DD)
                if self.second_application_list:
                    possible_application_count = 15
                    sfp_application_type_second_list = self._read_eeprom_specific_bytes((XCVR_SECOND_APPLICATION_LIST_OFFSET_QSFP_DD), XCVR_SECOND_APPLICATION_LIST_WIDTH_QSFP_DD)
                    if sfp_application_type_first_list is not None and sfp_application_type_second_list is not None:
                        sfp_application_type_list = sfp_application_type_first_list + sfp_application_type_second_list
                    else:
                        return None
                else:
                    possible_application_count = 8
                    if sfp_application_type_first_list is not None:
                        sfp_application_type_list = sfp_application_type_first_list
                    else:
                        return None

                for i in range(0, possible_application_count):
                    if sfp_application_type_list[i * 4] == 'ff':
                        break
                    host_electrical, media_interface = sfpi_obj.parse_application(sfp_media_type_dict, sfp_application_type_list[i * 4], sfp_application_type_list[i * 4 + 1])
                    host_media_list = host_media_list + host_electrical + ' - ' + media_interface + '\n\t\t\t\t   '
            else:
                return None

            transceiver_info_dict['type'] = str(sfp_type_data['data']['type']['value'])
            transceiver_info_dict['manufacturer'] = str(sfp_vendor_name_data['data']['Vendor Name']['value'])
            transceiver_info_dict['model'] = str(sfp_vendor_pn_data['data']['Vendor PN']['value'])
            transceiver_info_dict['hardware_rev'] = str(sfp_vendor_rev_data['data']['Vendor Rev']['value'])
            transceiver_info_dict['serial'] = str(sfp_vendor_sn_data['data']['Vendor SN']['value'])
            transceiver_info_dict['vendor_oui'] = str(sfp_vendor_oui_data['data']['Vendor OUI']['value'])
            transceiver_info_dict['vendor_date'] = str(sfp_vendor_date_data['data']['VendorDataCode(YYYY-MM-DD Lot)']['value'])
            transceiver_info_dict['connector'] = str(sfp_connector_data['data']['Connector']['value'])
            transceiver_info_dict['encoding'] = "Not supported for CMIS cables"
            transceiver_info_dict['ext_identifier'] = str(sfp_ext_identifier_data['data']['Extended Identifier']['value'])
            transceiver_info_dict['ext_rateselect_compliance'] = "Not supported for CMIS cables"
            transceiver_info_dict['specification_compliance'] = "Not supported for CMIS cables"
            transceiver_info_dict['cable_type'] = "Length Cable Assembly(m)"
            transceiver_info_dict['cable_length'] = str(sfp_cable_len_data['data']['Length Cable Assembly(m)']['value'])
            transceiver_info_dict['nominal_bit_rate'] = "Not supported for CMIS cables"
            transceiver_info_dict['application_advertisement'] = host_media_list

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

        if self.sfp_type != QSFP_DD_TYPE:
            sfp_interface_bulk_raw = self._read_eeprom_specific_bytes(offset + XCVR_INTERFACE_DATA_START, XCVR_INTERFACE_DATA_SIZE)
            if sfp_interface_bulk_raw is None:
                return None

            start = XCVR_INTFACE_BULK_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + interface_info_bulk_width
            sfp_interface_bulk_data = sfpi_obj.parse_sfp_info_bulk(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_VENDOR_NAME_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + XCVR_VENDOR_NAME_WIDTH
            sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_VENDOR_PN_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + XCVR_VENDOR_PN_WIDTH
            sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_HW_REV_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + vendor_rev_width
            sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_VENDOR_SN_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + XCVR_VENDOR_SN_WIDTH
            sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_VENDOR_OUI_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + XCVR_VENDOR_OUI_WIDTH
            sfp_vendor_oui_data = sfpi_obj.parse_vendor_oui(sfp_interface_bulk_raw[start : end], 0)

            start = XCVR_VENDOR_DATE_OFFSET - XCVR_INTERFACE_DATA_START
            end = start + XCVR_VENDOR_DATE_WIDTH
            sfp_vendor_date_data = sfpi_obj.parse_vendor_date(sfp_interface_bulk_raw[start : end], 0)

            transceiver_info_dict['type'] = sfp_interface_bulk_data['data']['type']['value']
            transceiver_info_dict['manufacturer'] = sfp_vendor_name_data['data']['Vendor Name']['value']
            transceiver_info_dict['model'] = sfp_vendor_pn_data['data']['Vendor PN']['value']
            transceiver_info_dict['hardware_rev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value']
            transceiver_info_dict['serial'] = sfp_vendor_sn_data['data']['Vendor SN']['value']
            transceiver_info_dict['vendor_oui'] = sfp_vendor_oui_data['data']['Vendor OUI']['value']
            transceiver_info_dict['vendor_date'] = sfp_vendor_date_data['data']['VendorDataCode(YYYY-MM-DD Lot)']['value']
            transceiver_info_dict['connector'] = sfp_interface_bulk_data['data']['Connector']['value']
            transceiver_info_dict['encoding'] = sfp_interface_bulk_data['data']['EncodingCodes']['value']
            transceiver_info_dict['ext_identifier'] = sfp_interface_bulk_data['data']['Extended Identifier']['value']
            transceiver_info_dict['ext_rateselect_compliance'] = sfp_interface_bulk_data['data']['RateIdentifier']['value']
            transceiver_info_dict['application_advertisement'] = 'N/A'

            if self.sfp_type == QSFP_TYPE:
                for key in qsfp_cable_length_tup:
                    if key in sfp_interface_bulk_data['data']:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])

                for key in qsfp_compliance_code_tup:
                    if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']                
                sfp_ext_specification_compliance_raw = self._read_eeprom_specific_bytes(offset + XCVR_EXT_SPECIFICATION_COMPLIANCE_OFFSET, XCVR_EXT_SPECIFICATION_COMPLIANCE_WIDTH)
                if sfp_ext_specification_compliance_raw is not None:
                    sfp_ext_specification_compliance_data = sfpi_obj.parse_ext_specification_compliance(sfp_ext_specification_compliance_raw[0 : 1], 0)
                    if sfp_ext_specification_compliance_data['data']['Extended Specification compliance']['value'] != "Unspecified":
                        compliance_code_dict['Extended Specification compliance'] = sfp_ext_specification_compliance_data['data']['Extended Specification compliance']['value']
                transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)
                
                transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['Nominal Bit Rate(100Mbs)']['value'])
            else:
                for key in sfp_cable_length_tup:
                    if key in sfp_interface_bulk_data['data']:
                        transceiver_info_dict['cable_type'] = key
                        transceiver_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])

                for key in sfp_compliance_code_tup:
                    if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                        compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
                transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)

                transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['NominalSignallingRate(UnitsOf100Mbd)']['value'])
    
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
        transceiver_dom_info_dict = {}

        dom_info_dict_keys = ['temperature',    'voltage',
                              'rx1power',       'rx2power',
                              'rx3power',       'rx4power',
                              'rx5power',       'rx6power',
                              'rx7power',       'rx8power',
                              'tx1bias',        'tx2bias',
                              'tx3bias',        'tx4bias',
                              'tx5bias',        'tx6bias',
                              'tx7bias',        'tx8bias',
                              'tx1power',       'tx2power',
                              'tx3power',       'tx4power',
                              'tx5power',       'tx6power',
                              'tx7power',       'tx8power'
                             ]
        transceiver_dom_info_dict = dict.fromkeys(dom_info_dict_keys, 'N/A')

        if self.sfp_type == OSFP_TYPE:
            pass

        elif self.sfp_type == QSFP_TYPE:
            if not self.dom_supported:
                return transceiver_dom_info_dict

            offset = 0
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return transceiver_dom_info_dict

            dom_data_raw = self._read_eeprom_specific_bytes((offset + QSFP_DOM_BULK_DATA_START), QSFP_DOM_BULK_DATA_SIZE)
            if dom_data_raw is None:
                return transceiver_dom_info_dict

            if self.dom_temp_supported:
                start = QSFP_TEMPE_OFFSET - QSFP_DOM_BULK_DATA_START
                end = start + QSFP_TEMPE_WIDTH
                dom_temperature_data = sfpd_obj.parse_temperature(dom_data_raw[start : end], 0)
                temp = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
                if temp is not None:
                    transceiver_dom_info_dict['temperature'] = temp

            if self.dom_volt_supported:
                start = QSFP_VOLT_OFFSET - QSFP_DOM_BULK_DATA_START
                end = start + QSFP_VOLT_WIDTH
                dom_voltage_data = sfpd_obj.parse_voltage(dom_data_raw[start : end], 0)
                volt = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
                if volt is not None:
                    transceiver_dom_info_dict['voltage'] = volt

            start = QSFP_CHANNL_MON_OFFSET - QSFP_DOM_BULK_DATA_START
            end = start + QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH
            dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_data_raw[start : end], 0)

            if self.dom_tx_power_supported:
                transceiver_dom_info_dict['tx1power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TX1Power']['value'])
                transceiver_dom_info_dict['tx2power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TX2Power']['value'])
                transceiver_dom_info_dict['tx3power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TX3Power']['value'])
                transceiver_dom_info_dict['tx4power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TX4Power']['value'])

            if self.dom_rx_power_supported:
                transceiver_dom_info_dict['rx1power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['RX1Power']['value'])
                transceiver_dom_info_dict['rx2power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['RX2Power']['value'])
                transceiver_dom_info_dict['rx3power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['RX3Power']['value'])
                transceiver_dom_info_dict['rx4power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['RX4Power']['value'])

            transceiver_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TX1Bias']['value']
            transceiver_dom_info_dict['tx2bias'] = dom_channel_monitor_data['data']['TX2Bias']['value']
            transceiver_dom_info_dict['tx3bias'] = dom_channel_monitor_data['data']['TX3Bias']['value']
            transceiver_dom_info_dict['tx4bias'] = dom_channel_monitor_data['data']['TX4Bias']['value']

        elif self.sfp_type == QSFP_DD_TYPE:

            offset = 0
            sfpd_obj = qsfp_dd_Dom()
            if sfpd_obj is None:
                return transceiver_dom_info_dict

            dom_data_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_DOM_BULK_DATA_START), QSFP_DD_DOM_BULK_DATA_SIZE)
            if dom_data_raw is None:
                return transceiver_dom_info_dict

            if self.dom_temp_supported:
                start = QSFP_DD_TEMPE_OFFSET - QSFP_DD_DOM_BULK_DATA_START
                end = start + QSFP_DD_TEMPE_WIDTH
                dom_temperature_data = sfpd_obj.parse_temperature(dom_data_raw[start : end], 0)
                temp = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
                if temp is not None:
                    transceiver_dom_info_dict['temperature'] = temp

            if self.dom_volt_supported:
                start = QSFP_DD_VOLT_OFFSET - QSFP_DD_DOM_BULK_DATA_START
                end = start + QSFP_DD_VOLT_WIDTH
                dom_voltage_data = sfpd_obj.parse_voltage(dom_data_raw[start : end], 0)
                volt = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
                if volt is not None:
                    transceiver_dom_info_dict['voltage'] = volt

            if self.dom_rx_tx_power_bias_supported:
                # page 11h
                dom_data_raw = self._read_eeprom_specific_bytes((QSFP_DD_CHANNL_MON_OFFSET), QSFP_DD_CHANNL_MON_WIDTH)
                if dom_data_raw is None:
                    return transceiver_dom_info_dict
                dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_data_raw, 0)

                if self.dom_tx_power_supported:
                    transceiver_dom_info_dict['tx1power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX1Power']['value']))
                    transceiver_dom_info_dict['tx2power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX2Power']['value']))
                    transceiver_dom_info_dict['tx3power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX3Power']['value']))
                    transceiver_dom_info_dict['tx4power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX4Power']['value']))
                    transceiver_dom_info_dict['tx5power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX5Power']['value']))
                    transceiver_dom_info_dict['tx6power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX6Power']['value']))
                    transceiver_dom_info_dict['tx7power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX7Power']['value']))
                    transceiver_dom_info_dict['tx8power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['TX8Power']['value']))

                if self.dom_rx_power_supported:
                    transceiver_dom_info_dict['rx1power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX1Power']['value']))
                    transceiver_dom_info_dict['rx2power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX2Power']['value']))
                    transceiver_dom_info_dict['rx3power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX3Power']['value']))
                    transceiver_dom_info_dict['rx4power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX4Power']['value']))
                    transceiver_dom_info_dict['rx5power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX5Power']['value']))
                    transceiver_dom_info_dict['rx6power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX6Power']['value']))
                    transceiver_dom_info_dict['rx7power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX7Power']['value']))
                    transceiver_dom_info_dict['rx8power'] = str(self._convert_string_to_num(dom_channel_monitor_data['data']['RX8Power']['value']))

                if self.dom_tx_bias_power_supported:
                    transceiver_dom_info_dict['tx1bias'] = str(dom_channel_monitor_data['data']['TX1Bias']['value'])
                    transceiver_dom_info_dict['tx2bias'] = str(dom_channel_monitor_data['data']['TX2Bias']['value'])
                    transceiver_dom_info_dict['tx3bias'] = str(dom_channel_monitor_data['data']['TX3Bias']['value'])
                    transceiver_dom_info_dict['tx4bias'] = str(dom_channel_monitor_data['data']['TX4Bias']['value'])
                    transceiver_dom_info_dict['tx5bias'] = str(dom_channel_monitor_data['data']['TX5Bias']['value'])
                    transceiver_dom_info_dict['tx6bias'] = str(dom_channel_monitor_data['data']['TX6Bias']['value'])
                    transceiver_dom_info_dict['tx7bias'] = str(dom_channel_monitor_data['data']['TX7Bias']['value'])
                    transceiver_dom_info_dict['tx8bias'] = str(dom_channel_monitor_data['data']['TX8Bias']['value'])

            return transceiver_dom_info_dict

        else:
            if not self.dom_supported:
                return transceiver_dom_info_dict

            offset = 256
            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return transceiver_dom_info_dict
            sfpd_obj._calibration_type = self.calibration

            dom_data_raw = self._read_eeprom_specific_bytes((offset + SFP_DOM_BULK_DATA_START), SFP_DOM_BULK_DATA_SIZE)

            start = SFP_TEMPE_OFFSET - SFP_DOM_BULK_DATA_START
            end = start + SFP_TEMPE_WIDTH
            dom_temperature_data = sfpd_obj.parse_temperature(dom_data_raw[start: end], 0)

            start = SFP_VOLT_OFFSET - SFP_DOM_BULK_DATA_START
            end = start + SFP_VOLT_WIDTH
            dom_voltage_data = sfpd_obj.parse_voltage(dom_data_raw[start: end], 0)

            start = SFP_CHANNL_MON_OFFSET - SFP_DOM_BULK_DATA_START
            end = start + SFP_CHANNL_MON_WIDTH
            dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_data_raw[start: end], 0)

            transceiver_dom_info_dict['temperature'] = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
            transceiver_dom_info_dict['voltage'] = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
            transceiver_dom_info_dict['rx1power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['RXPower']['value'])
            transceiver_dom_info_dict['tx1bias'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TXBias']['value'])
            transceiver_dom_info_dict['tx1power'] = self._convert_string_to_num(dom_channel_monitor_data['data']['TXPower']['value'])

        return transceiver_dom_info_dict


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
        transceiver_dom_threshold_info_dict = {}

        dom_info_dict_keys = ['temphighalarm',    'temphighwarning',
                              'templowalarm',     'templowwarning',
                              'vcchighalarm',     'vcchighwarning',
                              'vcclowalarm',      'vcclowwarning',
                              'rxpowerhighalarm', 'rxpowerhighwarning',
                              'rxpowerlowalarm',  'rxpowerlowwarning',
                              'txpowerhighalarm', 'txpowerhighwarning',
                              'txpowerlowalarm',  'txpowerlowwarning',
                              'txbiashighalarm',  'txbiashighwarning',
                              'txbiaslowalarm',   'txbiaslowwarning'
                             ]
        transceiver_dom_threshold_info_dict = dict.fromkeys(dom_info_dict_keys, 'N/A')

        if self.sfp_type == OSFP_TYPE:
            pass

        elif self.sfp_type == QSFP_TYPE:
            if not self.dom_supported or not self.qsfp_page3_available:
                return transceiver_dom_threshold_info_dict

            # Dom Threshold data starts from offset 384
            # Revert offset back to 0 once data is retrieved
            offset = QSFP_MODULE_UPPER_PAGE3_START
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return transceiver_dom_threshold_info_dict

            dom_module_threshold_raw = self._read_eeprom_specific_bytes((offset + QSFP_MODULE_THRESHOLD_OFFSET), QSFP_MODULE_THRESHOLD_WIDTH)
            if dom_module_threshold_raw is None:
                return transceiver_dom_threshold_info_dict

            dom_module_threshold_data = sfpd_obj.parse_module_threshold_values(dom_module_threshold_raw, 0)

            dom_channel_threshold_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_THRESHOLD_OFFSET),
                                      QSFP_CHANNL_THRESHOLD_WIDTH)
            if dom_channel_threshold_raw is None:
                return transceiver_dom_threshold_info_dict
            dom_channel_threshold_data = sfpd_obj.parse_channel_threshold_values(dom_channel_threshold_raw, 0)

            # Threshold Data
            transceiver_dom_threshold_info_dict['temphighalarm'] = dom_module_threshold_data['data']['TempHighAlarm']['value']
            transceiver_dom_threshold_info_dict['temphighwarning'] = dom_module_threshold_data['data']['TempHighWarning']['value']
            transceiver_dom_threshold_info_dict['templowalarm'] = dom_module_threshold_data['data']['TempLowAlarm']['value']
            transceiver_dom_threshold_info_dict['templowwarning'] = dom_module_threshold_data['data']['TempLowWarning']['value']
            transceiver_dom_threshold_info_dict['vcchighalarm'] = dom_module_threshold_data['data']['VccHighAlarm']['value']
            transceiver_dom_threshold_info_dict['vcchighwarning'] = dom_module_threshold_data['data']['VccHighWarning']['value']
            transceiver_dom_threshold_info_dict['vcclowalarm'] = dom_module_threshold_data['data']['VccLowAlarm']['value']
            transceiver_dom_threshold_info_dict['vcclowwarning'] = dom_module_threshold_data['data']['VccLowWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighalarm'] = dom_channel_threshold_data['data']['RxPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighwarning'] = dom_channel_threshold_data['data']['RxPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowalarm'] = dom_channel_threshold_data['data']['RxPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowwarning'] = dom_channel_threshold_data['data']['RxPowerLowWarning']['value']
            transceiver_dom_threshold_info_dict['txbiashighalarm'] = dom_channel_threshold_data['data']['TxBiasHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiashighwarning'] = dom_channel_threshold_data['data']['TxBiasHighWarning']['value']
            transceiver_dom_threshold_info_dict['txbiaslowalarm'] = dom_channel_threshold_data['data']['TxBiasLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiaslowwarning'] = dom_channel_threshold_data['data']['TxBiasLowWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerhighalarm'] = dom_channel_threshold_data['data']['TxPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerhighwarning'] = dom_channel_threshold_data['data']['TxPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerlowalarm'] = dom_channel_threshold_data['data']['TxPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerlowwarning'] = dom_channel_threshold_data['data']['TxPowerLowWarning']['value']

        elif self.sfp_type == QSFP_DD_TYPE:
            if not self.dom_supported:
                return transceiver_dom_threshold_info_dict

            if not self.dom_thresholds_supported:
                return transceiver_dom_threshold_info_dict

            sfpd_obj = qsfp_dd_Dom()
            if sfpd_obj is None:
                return transceiver_dom_threshold_info_dict

            # page 02
            offset = 384
            dom_module_threshold_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_MODULE_THRESHOLD_OFFSET), QSFP_DD_MODULE_THRESHOLD_WIDTH)
            if dom_module_threshold_raw is None:
                return transceiver_dom_threshold_info_dict

            dom_module_threshold_data = sfpd_obj.parse_module_threshold_values(dom_module_threshold_raw, 0)

            # Threshold Data
            transceiver_dom_threshold_info_dict['temphighalarm'] = dom_module_threshold_data['data']['TempHighAlarm']['value']
            transceiver_dom_threshold_info_dict['temphighwarning'] = dom_module_threshold_data['data']['TempHighWarning']['value']
            transceiver_dom_threshold_info_dict['templowalarm'] = dom_module_threshold_data['data']['TempLowAlarm']['value']
            transceiver_dom_threshold_info_dict['templowwarning'] = dom_module_threshold_data['data']['TempLowWarning']['value']
            transceiver_dom_threshold_info_dict['vcchighalarm'] = dom_module_threshold_data['data']['VccHighAlarm']['value']
            transceiver_dom_threshold_info_dict['vcchighwarning'] = dom_module_threshold_data['data']['VccHighWarning']['value']
            transceiver_dom_threshold_info_dict['vcclowalarm'] = dom_module_threshold_data['data']['VccLowAlarm']['value']
            transceiver_dom_threshold_info_dict['vcclowwarning'] = dom_module_threshold_data['data']['VccLowWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighalarm'] = dom_module_threshold_data['data']['RxPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighwarning'] = dom_module_threshold_data['data']['RxPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowalarm'] = dom_module_threshold_data['data']['RxPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowwarning'] = dom_module_threshold_data['data']['RxPowerLowWarning']['value']
            transceiver_dom_threshold_info_dict['txbiashighalarm'] = dom_module_threshold_data['data']['TxBiasHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiashighwarning'] = dom_module_threshold_data['data']['TxBiasHighWarning']['value']
            transceiver_dom_threshold_info_dict['txbiaslowalarm'] = dom_module_threshold_data['data']['TxBiasLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiaslowwarning'] = dom_module_threshold_data['data']['TxBiasLowWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerhighalarm'] = dom_module_threshold_data['data']['TxPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerhighwarning'] = dom_module_threshold_data['data']['TxPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerlowalarm'] = dom_module_threshold_data['data']['TxPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerlowwarning'] = dom_module_threshold_data['data']['TxPowerLowWarning']['value']

        else:
            offset = SFP_MODULE_ADDRA2_OFFSET

            if not self.dom_supported:
                return transceiver_dom_threshold_info_dict

            sfpd_obj = sff8472Dom(None, self.calibration)
            if sfpd_obj is None:
                return transceiver_dom_threshold_info_dict

            dom_module_threshold_raw = self._read_eeprom_specific_bytes((offset + SFP_MODULE_THRESHOLD_OFFSET),
                                         SFP_MODULE_THRESHOLD_WIDTH)
            if dom_module_threshold_raw is not None:
                dom_module_threshold_data = sfpd_obj.parse_alarm_warning_threshold(dom_module_threshold_raw, 0)
            else:
                return transceiver_dom_threshold_info_dict

            # Threshold Data
            transceiver_dom_threshold_info_dict['temphighalarm'] = dom_module_threshold_data['data']['TempHighAlarm']['value']
            transceiver_dom_threshold_info_dict['templowalarm'] = dom_module_threshold_data['data']['TempLowAlarm']['value']
            transceiver_dom_threshold_info_dict['temphighwarning'] = dom_module_threshold_data['data']['TempHighWarning']['value']
            transceiver_dom_threshold_info_dict['templowwarning'] = dom_module_threshold_data['data']['TempLowWarning']['value']
            transceiver_dom_threshold_info_dict['vcchighalarm'] = dom_module_threshold_data['data']['VoltageHighAlarm']['value']
            transceiver_dom_threshold_info_dict['vcclowalarm'] = dom_module_threshold_data['data']['VoltageLowAlarm']['value']
            transceiver_dom_threshold_info_dict['vcchighwarning'] = dom_module_threshold_data['data']['VoltageHighWarning']['value']
            transceiver_dom_threshold_info_dict['vcclowwarning'] = dom_module_threshold_data['data']['VoltageLowWarning']['value']
            transceiver_dom_threshold_info_dict['txbiashighalarm'] = dom_module_threshold_data['data']['BiasHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiaslowalarm'] = dom_module_threshold_data['data']['BiasLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiashighwarning'] = dom_module_threshold_data['data']['BiasHighWarning']['value']
            transceiver_dom_threshold_info_dict['txbiaslowwarning'] = dom_module_threshold_data['data']['BiasLowWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerhighalarm'] = dom_module_threshold_data['data']['TXPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerlowalarm'] = dom_module_threshold_data['data']['TXPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txpowerhighwarning'] = dom_module_threshold_data['data']['TXPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['txpowerlowwarning'] = dom_module_threshold_data['data']['TXPowerLowWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighalarm'] = dom_module_threshold_data['data']['RXPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowalarm'] = dom_module_threshold_data['data']['RXPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighwarning'] = dom_module_threshold_data['data']['RXPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowwarning'] = dom_module_threshold_data['data']['RXPowerLowWarning']['value']

        return transceiver_dom_threshold_info_dict


    def get_reset_status(self):
        """
        Retrieves the reset status of SFP

        Returns:
            A Boolean, True if reset enabled, False if disabled

        for QSFP, originally I would like to make use of Initialization complete flag bit
        which is at Page a0 offset 6 bit 0 to test whether reset is complete. 
        However as unit testing was carried out I find this approach may fail because:
            1. we make use of ethtool to read data on I2C bus rather than to read directly
            2. ethtool is unable to access I2C during QSFP module being reset
        In other words, whenever the flag is able to be retrived, the value is always be 1
        As a result, it doesn't make sense to retrieve that flag. Just treat successfully 
        retrieving data as "data ready".
        for SFP it seems that there is not flag indicating whether reset succeed. However,
        we can also do it in the way for QSFP.
        """
        if not self.dom_supported:
            return False

        if self.sfp_type == OSFP_TYPE:
            return False
        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            sfpd_obj = sff8436Dom()
            dom_module_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_MODULE_MONITOR_OFFSET), QSFP_MODULE_MONITOR_WIDTH)

            if dom_module_monitor_raw is not None:
                return True
            else:
                return False
        elif self.sfp_type == SFP_TYPE:
            offset = 0
            sfpd_obj = sff8472Dom()
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_STATUS_OFFSET), SFP_CHANNL_STATUS_WIDTH)

            if dom_channel_monitor_raw is not None:
                return True
            else:
                return False
        elif self.sfp_type == QSFP_DD_TYPE:
            offset = 0
            sfpd_obj = qsfp_dd_InterfaceId()
            dom_channel_status_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_CHANNL_STATUS_OFFSET), QSFP_DD_CHANNL_STATUS_WIDTH)

            if dom_channel_status_raw is None:
                return False

            dom_channel_status_data = sfpd_obj.parse_dom_channel_status(dom_channel_status_raw, 0)
            return dom_channel_status_data['data']['Status']['value'] == 'On'

    def get_rx_los(self):
        """
        Retrieves the RX LOS (lost-of-signal) status of SFP

        Returns:
            A Boolean, True if SFP has RX LOS, False if not.
            Note : RX LOS status is latched until a call to get_rx_los or a reset.
        """
        if not self.dom_supported:
            return None

        rx_los_list = []
        if self.sfp_type == OSFP_TYPE:
            return None
        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_RX_LOS_STATUS_OFFSET), QSFP_CHANNL_RX_LOS_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                rx_los_data = int(dom_channel_monitor_raw[0], 16)
                rx_los_list.append(rx_los_data & 0x01 != 0)
                rx_los_list.append(rx_los_data & 0x02 != 0)
                rx_los_list.append(rx_los_data & 0x04 != 0)
                rx_los_list.append(rx_los_data & 0x08 != 0)

        elif self.sfp_type == QSFP_DD_TYPE:
            # page 11h
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_CHANNL_RX_LOS_STATUS_OFFSET), QSFP_DD_CHANNL_RX_LOS_STATUS_WIDTH)
                if dom_channel_monitor_raw is not None:
                    rx_los_data = int(dom_channel_monitor_raw[0], 8)
                    rx_los_list.append(rx_los_data & 0x01 != 0)
                    rx_los_list.append(rx_los_data & 0x02 != 0)
                    rx_los_list.append(rx_los_data & 0x04 != 0)
                    rx_los_list.append(rx_los_data & 0x08 != 0)
                    rx_los_list.append(rx_los_data & 0x10 != 0)
                    rx_los_list.append(rx_los_data & 0x20 != 0)
                    rx_los_list.append(rx_los_data & 0x40 != 0)
                    rx_los_list.append(rx_los_data & 0x80 != 0)

        else:
            offset = 256
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_STATUS_OFFSET), SFP_CHANNL_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                rx_los_data = int(dom_channel_monitor_raw[0], 16)
                rx_los_list.append(rx_los_data & 0x02 != 0)
            else:
                return None
        return rx_los_list


    def get_tx_fault(self):
        """
        Retrieves the TX fault status of SFP

        Returns:
            A Boolean, True if SFP has TX fault, False if not
            Note : TX fault status is lached until a call to get_tx_fault or a reset.
        """
        if not self.dom_supported:
            return None

        tx_fault_list = []
        if self.sfp_type == OSFP_TYPE:
            return None
        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_TX_FAULT_STATUS_OFFSET), QSFP_CHANNL_TX_FAULT_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                tx_fault_data = int(dom_channel_monitor_raw[0], 16)
                tx_fault_list.append(tx_fault_data & 0x01 != 0)
                tx_fault_list.append(tx_fault_data & 0x02 != 0)
                tx_fault_list.append(tx_fault_data & 0x04 != 0)
                tx_fault_list.append(tx_fault_data & 0x08 != 0)

        elif self.sfp_type == QSFP_DD_TYPE:
            return None
            # page 11h
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_CHANNL_TX_FAULT_STATUS_OFFSET), QSFP_DD_CHANNL_TX_FAULT_STATUS_WIDTH)
                if dom_channel_monitor_raw is not None:
                    tx_fault_data = int(dom_channel_monitor_raw[0], 8)
                    tx_fault_list.append(tx_fault_data & 0x01 != 0)
                    tx_fault_list.append(tx_fault_data & 0x02 != 0)
                    tx_fault_list.append(tx_fault_data & 0x04 != 0)
                    tx_fault_list.append(tx_fault_data & 0x08 != 0)
                    tx_fault_list.append(tx_fault_data & 0x10 != 0)
                    tx_fault_list.append(tx_fault_data & 0x20 != 0)
                    tx_fault_list.append(tx_fault_data & 0x40 != 0)
                    tx_fault_list.append(tx_fault_data & 0x80 != 0)

        else:
            offset = 256
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_STATUS_OFFSET), SFP_CHANNL_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                tx_fault_data = int(dom_channel_monitor_raw[0], 16)
                tx_fault_list.append(tx_fault_data & 0x04 != 0)
            else:
                return None
        return tx_fault_list


    def get_tx_disable(self):
        """
        Retrieves the tx_disable status of this SFP

        Returns:
            A Boolean, True if tx_disable is enabled, False if disabled

        for QSFP, the disable states of each channel which are the lower 4 bits in byte 85 page a0
        for SFP, the TX Disable State and Soft TX Disable Select is ORed as the tx_disable status returned
                 These two bits are bit 7 & 6 in byte 110 page a2 respectively
        """
        if not self.dom_supported:
            return None

        tx_disable_list = []
        if self.sfp_type == OSFP_TYPE:
            return None
        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_DISABLE_STATUS_OFFSET), QSFP_CHANNL_DISABLE_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                tx_disable_data = int(dom_channel_monitor_raw[0], 16)
                tx_disable_list.append(tx_disable_data & 0x01 != 0)
                tx_disable_list.append(tx_disable_data & 0x02 != 0)
                tx_disable_list.append(tx_disable_data & 0x04 != 0)
                tx_disable_list.append(tx_disable_data & 0x08 != 0)

        elif self.sfp_type == QSFP_DD_TYPE:
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_CHANNL_DISABLE_STATUS_OFFSET), QSFP_DD_CHANNL_DISABLE_STATUS_WIDTH)
                if dom_channel_monitor_raw is not None:
                    tx_disable_data = int(dom_channel_monitor_raw[0], 16)
                    tx_disable_list.append(tx_disable_data & 0x01 != 0)
                    tx_disable_list.append(tx_disable_data & 0x02 != 0)
                    tx_disable_list.append(tx_disable_data & 0x04 != 0)
                    tx_disable_list.append(tx_disable_data & 0x08 != 0)
                    tx_disable_list.append(tx_disable_data & 0x10 != 0)
                    tx_disable_list.append(tx_disable_data & 0x20 != 0)
                    tx_disable_list.append(tx_disable_data & 0x40 != 0)
                    tx_disable_list.append(tx_disable_data & 0x80 != 0)

        else:
            offset = 256
            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_STATUS_OFFSET), SFP_CHANNL_STATUS_WIDTH)
            if dom_channel_monitor_raw is not None:
                tx_disable_data = int(dom_channel_monitor_raw[0], 16)
                tx_disable_list.append(tx_disable_data & 0xC0 != 0)
            else:
                return None
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
        if self.sfp_type == QSFP_TYPE:
            if self._open_sdk():
                # Get MCION
                mcion = ku_mcion_reg()
                mcion.module = self.sdk_index
                meta = self._init_sx_meta_data()
                meta.access_cmd = SXD_ACCESS_CMD_GET

                rc = sxd_access_reg_mcion(mcion, meta, REGISTER_NUM, None, None)
                self._close_sdk()

                if rc != SXD_STATUS_SUCCESS:
                    logger.log_warning("sxd_access_reg_mcion getting failed, rc = %d" % rc)
                    return None

                # Get low power mode status
                lpm_mask = 1 << 8
                lpm_status = (lpm_mask & mcion.module_status_bits) != 0

                return lpm_status
        else:
            return NotImplementedError


    def get_power_override(self):
        """
        Retrieves the power-override status of this SFP

        Returns:
            A Boolean, True if power-override is enabled, False if disabled
        """
        if self.sfp_type == QSFP_TYPE:
            offset = 0
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return False

            dom_control_raw = self._read_eeprom_specific_bytes((offset + QSFP_CONTROL_OFFSET), QSFP_CONTROL_WIDTH)
            if dom_control_raw is not None:
                dom_control_data = sfpd_obj.parse_control_bytes(dom_control_raw, 0)
                return ('On' == dom_control_data['data']['PowerOverride'])
        else:
            return NotImplementedError


    def get_temperature(self):
        """
        Retrieves the temperature of this SFP

        Returns:
            An integer number of current temperature in Celsius
        """
        if not self.dom_supported:
            return None
        if self.sfp_type == QSFP_TYPE:
            offset = 0
            offset_xcvr = 128

            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            if self.dom_temp_supported:
                dom_temperature_raw = self._read_eeprom_specific_bytes((offset + QSFP_TEMPE_OFFSET), QSFP_TEMPE_WIDTH)
                if dom_temperature_raw is not None:
                    dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
                    temp = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
                    return temp
                else:
                    return None
            else:
                return None

        elif self.sfp_type == QSFP_DD_TYPE:
            offset = 0

            sfpd_obj = qsfp_dd_Dom()
            if sfpd_obj is None:
                return None

            if self.dom_temp_supported:
                dom_temperature_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_TEMPE_OFFSET), QSFP_DD_TEMPE_WIDTH)
                if dom_temperature_raw is not None:
                    dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
                    temp = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
                    return temp
            return None

        else:
            offset = 256
            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None
            sfpd_obj._calibration_type = 1

            dom_temperature_raw = self._read_eeprom_specific_bytes((offset + SFP_TEMPE_OFFSET), SFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
                temp = self._convert_string_to_num(dom_temperature_data['data']['Temperature']['value'])
                return temp
            else:
                return None


    def get_voltage(self):
        """
        Retrieves the supply voltage of this SFP

        Returns:
            An integer number of supply voltage in mV
        """
        if not self.dom_supported:
            return None
        if self.sfp_type == QSFP_TYPE:
            offset = 0
            offset_xcvr = 128
            
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            if self.dom_volt_supported:
                dom_voltage_raw = self._read_eeprom_specific_bytes((offset + QSFP_VOLT_OFFSET), QSFP_VOLT_WIDTH)
                if dom_voltage_raw is not None:
                    dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
                    voltage = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
                    return voltage
                else:
                    return None
            return None

        if self.sfp_type == QSFP_DD_TYPE:
            offset = 128        

            sfpd_obj = qsfp_dd_Dom()
            if sfpd_obj is None:
                return None

            if self.dom_volt_supported:
                dom_voltage_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_VOLT_OFFSET), QSFP_DD_VOLT_WIDTH)
                if dom_voltage_raw is not None:
                    dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
                    voltage = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
                    return voltage
            return None

        else:
            offset = 256

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            sfpd_obj._calibration_type = self.calibration

            dom_voltage_raw = self._read_eeprom_specific_bytes((offset + SFP_VOLT_OFFSET), SFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
                voltage = self._convert_string_to_num(dom_voltage_data['data']['Vcc']['value'])
                return voltage
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
        tx_bias_list = []
        if self.sfp_type == QSFP_TYPE:
            offset = 0
            offset_xcvr = 128
            
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
            if dom_channel_monitor_raw is not None:
                dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_channel_monitor_raw, 0)
                tx_bias_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX1Bias']['value']))
                tx_bias_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX2Bias']['value']))
                tx_bias_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX3Bias']['value']))
                tx_bias_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX4Bias']['value']))
        
        elif self.sfp_type == QSFP_DD_TYPE:
            # page 11h
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                sfpd_obj = qsfp_dd_Dom()
                if sfpd_obj is None:
                    return None

                if dom_tx_bias_power_supported:
                    dom_tx_bias_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_TX_BIAS_OFFSET), QSFP_DD_TX_BIAS_WIDTH)
                    if dom_tx_bias_raw is not None:
                        dom_tx_bias_data = sfpd_obj.parse_dom_tx_bias(dom_tx_bias_raw, 0)
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX1Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX2Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX3Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX4Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX5Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX6Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX7Bias']['value']))
                        tx_bias_list.append(self._convert_string_to_num(dom_tx_bias_data['data']['TX8Bias']['value']))

        else:
            offset = 256

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None
            sfpd_obj._calibration_type = self.calibration

            if self.dom_supported:
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_MON_OFFSET), SFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                    tx_bias_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TXBias']['value']))
                else:
                    return None
            else:
                return None

        return tx_bias_list


    def get_rx_power(self):
        """
        Retrieves the received optical power for this SFP

        Returns:
            A list of four integer numbers, representing received optical
            power in mW for channel 0 to channel 4.
            Ex. ['1.77', '1.71', '1.68', '1.70']
        """
        rx_power_list = []
        if self.sfp_type == OSFP_TYPE:
            # OSFP not supported on our platform yet.
            return None

        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            offset_xcvr = 128
            
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            if self.dom_rx_power_supported:
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_channel_monitor_raw, 0)
                    rx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['RX1Power']['value']))
                    rx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['RX2Power']['value']))
                    rx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['RX3Power']['value']))
                    rx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['RX4Power']['value']))
                else:
                    return None
            else:
                return None

        elif self.sfp_type == QSFP_DD_TYPE:
            # page 11
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                sfpd_obj = qsfp_dd_Dom()
                if sfpd_obj is None:
                    return None

                if self.dom_rx_power_supported:
                    dom_rx_power_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_RX_POWER_OFFSET), QSFP_DD_RX_POWER_WIDTH)
                    if dom_rx_power_raw is not None:
                        dom_rx_power_data = sfpd_obj.parse_dom_rx_power(dom_rx_power_raw, 0)
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX1Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX2Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX3Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX4Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX5Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX6Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX7Power']['value']))
                        rx_power_list.append(self._convert_string_to_num(dom_rx_power_data['data']['RX8Power']['value']))

        else:
            offset = 256

            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            if self.dom_supported:
                sfpd_obj._calibration_type = self.calibration

                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_MON_OFFSET), SFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                    rx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['RXPower']['value']))
                else:
                    return None
            else:
                return None
        return rx_power_list


    def get_tx_power(self):
        """
        Retrieves the TX power of this SFP

        Returns:
            A list of four integer numbers, representing TX power in mW
            for channel 0 to channel 4.
            Ex. ['1.86', '1.86', '1.86', '1.86']
        """
        tx_power_list = []
        if self.sfp_type == OSFP_TYPE:
            # OSFP not supported on our platform yet.
            return None

        elif self.sfp_type == QSFP_TYPE:
            offset = 0
            offset_xcvr = 128

            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            if self.dom_tx_power_supported:
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_channel_monitor_raw, 0)
                    tx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX1Power']['value']))
                    tx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX2Power']['value']))
                    tx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX3Power']['value']))
                    tx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TX4Power']['value']))
                else:
                    return None
            else:
                return None

        elif self.sfp_type == QSFP_DD_TYPE:
            return None
            # page 11
            if self.dom_rx_tx_power_bias_supported:
                offset = 128
                sfpd_obj = qsfp_dd_Dom()
                if sfpd_obj is None:
                    return None

                if self.dom_tx_power_supported:
                    dom_tx_power_raw = self._read_eeprom_specific_bytes((offset + QSFP_DD_TX_POWER_OFFSET), QSFP_DD_TX_POWER_WIDTH)
                    if dom_tx_power_raw is not None:
                        dom_tx_power_data = sfpd_obj.parse_dom_tx_power(dom_tx_power_raw, 0)
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX1Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX2Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX3Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX4Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX5Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX6Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX7Power']['value']))
                        tx_power_list.append(self._convert_string_to_num(dom_tx_power_data['data']['TX8Power']['value']))

        else:
            offset = 256
            sfpd_obj = sff8472Dom()
            if sfpd_obj is None:
                return None

            if self.dom_supported:
                sfpd_obj._calibration_type = self.calibration

                dom_channel_monitor_raw = self._read_eeprom_specific_bytes((offset + SFP_CHANNL_MON_OFFSET), SFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                    tx_power_list.append(self._convert_string_to_num(dom_channel_monitor_data['data']['TXPower']['value']))
                else:
                    return None
            else:
                return None
        return tx_power_list


    def reset(self):
        """
        Reset SFP and return all user module settings to their default state.

        Returns:
            A boolean, True if successful, False if not

        refer plugins/sfpreset.py
        """
        handle = self._open_sdk()
        if handle is None:
            return False

        # Get PMAOS
        pmaos = ku_pmaos_reg()
        pmaos.module = self.sdk_index
        meta = self._init_sx_meta_data()
        meta.access_cmd = SXD_ACCESS_CMD_GET

        rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
        if rc != SXD_STATUS_SUCCESS:
            logger.log_warning("sxd_access_reg_pmaos getting failed, rc = %d" % rc)
            self._close_sdk()
            return None

        # Reset SFP
        pmaos.rst = 1
        meta.access_cmd = SXD_ACCESS_CMD_SET
        rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
        if rc != SXD_STATUS_SUCCESS:
            logger.log_warning("sxd_access_reg_pmaos setting failed, rc = %d" % rc)

        self._close_sdk()
        return rc == SXD_STATUS_SUCCESS


    def _write_i2c_via_mcia(self, page, i2caddr, address, data, mask):
        handle = self._open_sdk()
        if handle is None:
            return False

        mcia = ku_mcia_reg()

        meta = self._init_sx_meta_data()
        meta.access_cmd = SXD_ACCESS_CMD_GET

        mcia.module = self.sdk_index
        mcia.page_number = page
        mcia.i2c_device_address = i2caddr
        mcia.device_address = address
        mcia.size = 1
        rc = sxd_access_reg_mcia(mcia, meta, REGISTER_NUM, None, None)
        if rc != SXD_STATUS_SUCCESS:
            logger.log_warning("sxd_access_reg_mcia getting failed, rc = %d" % rc)
            self._close_sdk()
            return False

        original_data = (mcia.dword_0 >> 24) & 0x000000FF
        updated_data = original_data & (~mask)
        updated_data |= (data & mask)

        mcia.dword_0 = (updated_data << 24) & 0xFF000000
        meta.access_cmd = SXD_ACCESS_CMD_SET
        rc = sxd_access_reg_mcia(mcia, meta, REGISTER_NUM, None, None)
        if rc != SXD_STATUS_SUCCESS:
            logger.log_warning("sxd_access_reg_mcia setting failed, rc = %d" % rc)

        self._close_sdk()
        return rc == SXD_STATUS_SUCCESS


    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels

        Args:
            tx_disable : A Boolean, True to enable tx_disable mode, False to disable
                         tx_disable mode.

        Returns:
            A boolean, True if tx_disable is set successfully, False if not

        for SFP, make use of bit 6 of byte at (offset 110, a2h (i2c addr 0x51)) to disable/enable tx
        for QSFP, set all channels to disable/enable tx
        """
        if self.sfp_type == SFP_TYPE:
            if self.dom_tx_disable_supported:
                handle = self._open_sdk()
                if handle is None:
                    return False

                tx_disable_mask = 1 << MCIA_ADDR_TX_DISABLE_BIT
                if tx_disable:
                    tx_disable_bit = tx_disable_mask
                else:
                    tx_disable_bit = 0

                return self._write_i2c_via_mcia(2, 0x51, MCIA_ADDR_TX_DISABLE, tx_disable_bit, tx_disable_mask)
            else:
                return False
        elif self.sfp_type == QSFP_TYPE:
            if self.dom_tx_disable_supported:
                channel_mask = 0x0f
                if tx_disable:
                    disable_flag = channel_mask
                else:
                    disable_flag = 0

                return self._write_i2c_via_mcia(0, 0x50, MCIA_ADDR_TX_CHANNEL_DISABLE, disable_flag, channel_mask)
            else:
                return False
        else:
            return NotImplementedError


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

        QSFP: page a0, address 86, lower 4 bits
        """
        if self.sfp_type == QSFP_TYPE:
            if self.dom_tx_disable_supported:
                channel_mask = 1 << channel
                if disable:
                    disable_flag = channel_mask
                else:
                    disable_flag = 0

                return self._write_i2c_via_mcia(0, 0x50, MCIA_ADDR_TX_CHANNEL_DISABLE, disable_flag, channel_mask)
            else:
                return False
        else:
            return NotImplementedError


    def is_nve(self, port):
        return (port & NVE_MASK) != 0


    def is_port_admin_status_up(self, log_port):
        oper_state_p = new_sx_port_oper_state_t_p()
        admin_state_p = new_sx_port_admin_state_t_p()
        module_state_p = new_sx_port_module_state_t_p()
        rc = sx_api_port_state_get(self.sdk_handle, log_port, oper_state_p, admin_state_p, module_state_p)
        assert rc == SXD_STATUS_SUCCESS, "sx_api_port_state_get failed, rc = %d" % rc

        admin_state = sx_port_admin_state_t_p_value(admin_state_p)
        if admin_state == SX_PORT_ADMIN_STATUS_UP:
            return True
        else:
            return False


    def set_port_admin_status_by_log_port(self, log_port, admin_status):
        rc = sx_api_port_state_set(self.sdk_handle, log_port, admin_status)
        assert rc == SX_STATUS_SUCCESS, "sx_api_port_state_set failed, rc = %d" % rc


    # Get all the ports related to the sfp, if port admin status is up, put it to list
    def get_log_ports(self):
        port_attributes_list = new_sx_port_attributes_t_arr(SX_PORT_ATTR_ARR_SIZE)
        port_cnt_p = new_uint32_t_p()
        uint32_t_p_assign(port_cnt_p, SX_PORT_ATTR_ARR_SIZE)

        rc = sx_api_port_device_get(self.sdk_handle, DEVICE_ID , SWITCH_ID, port_attributes_list,  port_cnt_p)
        assert rc == SX_STATUS_SUCCESS, "sx_api_port_device_get failed, rc = %d" % rc

        port_cnt = uint32_t_p_value(port_cnt_p)
        log_port_list = []
        for i in range(0, port_cnt):
            port_attributes = sx_port_attributes_t_arr_getitem(port_attributes_list, i)
            if self.is_nve(int(port_attributes.log_port)) == False \
            and port_attributes.port_mapping.module_port == self.sdk_index \
            and self.is_port_admin_status_up(port_attributes.log_port):
                log_port_list.append(port_attributes.log_port)

        return log_port_list


    def _set_sfp_admin_status_raw(self, admin_status):
        # Get PMAOS
        pmaos = ku_pmaos_reg()
        pmaos.module = self.sdk_index
        meta = self._init_sx_meta_data()
        meta.access_cmd = SXD_ACCESS_CMD_GET
        rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
        assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

        # Set admin status to PMAOS
        pmaos.ase = PMAOS_ASE
        pmaos.ee = PMAOS_EE
        pmaos.e = PMAOS_E
        pmaos.rst = PMAOS_RST
        if admin_status == SX_PORT_ADMIN_STATUS_DOWN:
            pmaos.admin_status = PMAOS_DISABLE
        else:
            pmaos.admin_status = PMAOS_ENABLE

        meta.access_cmd = SXD_ACCESS_CMD_SET
        rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
        assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc


    def _set_lpmode_raw(self, lpmode):
        # Get PMMP
        pmmp = ku_pmmp_reg()
        pmmp.module = self.sdk_index
        meta = self._init_sx_meta_data()
        meta.access_cmd = SXD_ACCESS_CMD_GET
        rc = sxd_access_reg_pmmp(pmmp, meta, REGISTER_NUM, None, None)
        assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmmp failed, rc = %d" % rc

        # Set low power mode status
        lpm_mask = 1 << PMMP_LPMODE_BIT
        if lpmode:
            pmmp.eeprom_override = pmmp.eeprom_override | lpm_mask
        else:
            pmmp.eeprom_override = pmmp.eeprom_override & (~lpm_mask)

        meta.access_cmd = SXD_ACCESS_CMD_SET
        rc = sxd_access_reg_pmmp(pmmp, meta, REGISTER_NUM, None, None)

        return rc


    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP

        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override

        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        handle = self._open_sdk()
        if handle is None:
            return False
        try:
            log_port_list = self.get_log_ports()
            for log_port in log_port_list:
                self.set_port_admin_status_by_log_port(log_port, SX_PORT_ADMIN_STATUS_DOWN)
            self._set_sfp_admin_status_raw(SX_PORT_ADMIN_STATUS_DOWN)

            result = self._set_lpmode_raw(lpmode)

            self._set_sfp_admin_status_raw(SX_PORT_ADMIN_STATUS_UP)
            for log_port in log_port_list:
                self.set_port_admin_status_by_log_port(log_port, SX_PORT_ADMIN_STATUS_DOWN)

            return result == SXD_STATUS_SUCCESS
        except:
            logger.log_warning("set_lpmode failed due to some SDK failure")
            self._close_sdk()
            return False


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
        if self.sfp_type == QSFP_TYPE:
            power_override_bit = 0
            if power_override:
                power_override_bit |= 1 << MCIA_ADDR_POWER_OVERRIDE_POR_BIT
            power_set_bit = 0
            if power_set:
                power_set_bit |= 1 << MCIA_ADDR_POWER_OVERRIDE_PS_BIT
            power_override_mask = 1 << MCIA_ADDR_POWER_OVERRIDE_PS_BIT | 1 << MCIA_ADDR_POWER_OVERRIDE_POR_BIT

            return self._write_i2c_via_mcia(0, 0x50, MCIA_ADDR_POWER_OVERRIDE, power_set_bit|power_override_bit, power_override_mask)
        else:
            return NotImplementedError
