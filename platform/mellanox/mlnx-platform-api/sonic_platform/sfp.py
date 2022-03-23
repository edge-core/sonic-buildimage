#
# Copyright (c) 2019-2021 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the FANs status which are available in the platform
#
#############################################################################

try:
    import subprocess
    import os
    from sonic_platform_base.sonic_eeprom import eeprom_dts
    from sonic_py_common.logger import Logger
    from . import utils
    from .device_data import DeviceDataManager
    from sonic_platform_base.sonic_xcvr.sfp_optoe_base import SfpOptoeBase

except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

try:
    # python_sdk_api does not support python3 for now. Daemons like thermalctld or psud
    # also import this file without actually use the sdk lib. So we catch the ImportError
    # and ignore it here. Meanwhile, we have to trigger xcvrd using python2 now because it
    # uses the sdk lib.
    from python_sdk_api.sxd_api import *
    from python_sdk_api.sx_api import *
except ImportError as e:
    pass

try:
    if os.environ["PLATFORM_API_UNIT_TESTING"] == "1":
        # Unable to import SDK constants under unit test
        # Define them here
        SX_PORT_MODULE_STATUS_INITIALIZING = 0
        SX_PORT_MODULE_STATUS_PLUGGED = 1
        SX_PORT_MODULE_STATUS_UNPLUGGED = 2
        SX_PORT_MODULE_STATUS_PLUGGED_WITH_ERROR = 3
        SX_PORT_MODULE_STATUS_PLUGGED_DISABLED = 4
except KeyError:
    pass


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
PORT_TYPE_CPU = 4
PORT_TYPE_OFFSET = 28
PORT_TYPE_MASK = 0xF0000000
NVE_MASK = PORT_TYPE_MASK & (PORT_TYPE_NVE << PORT_TYPE_OFFSET)
CPU_MASK = PORT_TYPE_MASK & (PORT_TYPE_CPU << PORT_TYPE_OFFSET)

# parameters for SFP presence
SFP_STATUS_INSERTED = '1'

# Global logger class instance
logger = Logger()


# SDK initializing stuff, called from chassis
def initialize_sdk_handle():
    rc, sdk_handle = sx_api_open(None)
    if (rc != SX_STATUS_SUCCESS):
        logger.log_warning("Failed to open api handle, please check whether SDK is running.")
        sdk_handle = None

    return sdk_handle


def deinitialize_sdk_handle(sdk_handle):
    if sdk_handle is not None:
        rc = sx_api_close(sdk_handle)
        if (rc != SX_STATUS_SUCCESS):
            logger.log_warning("Failed to close api handle.")

        return rc == SXD_STATUS_SUCCESS
    else:
         logger.log_warning("Sdk handle is none")
         return False


class SdkHandleContext(object):
    def __init__(self):
        self.sdk_handle = None

    def __enter__(self):
        self.sdk_handle = initialize_sdk_handle()
        return self.sdk_handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        deinitialize_sdk_handle(self.sdk_handle)


class SFP(SfpOptoeBase):
    """Platform-specific SFP class"""
    shared_sdk_handle = None
    SFP_MLNX_ERROR_DESCRIPTION_LONGRANGE_NON_MLNX_CABLE = 'Long range for non-Mellanox cable or module'
    SFP_MLNX_ERROR_DESCRIPTION_ENFORCE_PART_NUMBER_LIST = 'Enforce part number list'
    SFP_MLNX_ERROR_DESCRIPTION_PMD_TYPE_NOT_ENABLED = 'PMD type not enabled'
    SFP_MLNX_ERROR_DESCRIPTION_PCIE_POWER_SLOT_EXCEEDED = 'PCIE system power slot exceeded'
    SFP_MLNX_ERROR_DESCRIPTION_RESERVED = 'Reserved'

    SFP_MLNX_ERROR_BIT_LONGRANGE_NON_MLNX_CABLE = 0x00010000
    SFP_MLNX_ERROR_BIT_ENFORCE_PART_NUMBER_LIST = 0x00020000
    SFP_MLNX_ERROR_BIT_PMD_TYPE_NOT_ENABLED = 0x00040000
    SFP_MLNX_ERROR_BIT_PCIE_POWER_SLOT_EXCEEDED = 0x00080000
    SFP_MLNX_ERROR_BIT_RESERVED = 0x80000000

    def __init__(self, sfp_index, slot_id=0, linecard_port_count=0, lc_name=None):
        super(SFP, self).__init__()

        if slot_id == 0: # For non-modular chassis
            self.index = sfp_index + 1
            self.sdk_index = sfp_index

            from .thermal import initialize_sfp_thermal
            self._thermal_list = initialize_sfp_thermal(sfp_index)
        else: # For modular chassis
            # (slot_id % MAX_LC_CONUNT - 1) * MAX_PORT_COUNT + (sfp_index + 1) * (MAX_PORT_COUNT / LC_PORT_COUNT)
            max_linecard_count = DeviceDataManager.get_linecard_count()
            max_linecard_port_count = DeviceDataManager.get_linecard_max_port_count()
            self.index = (slot_id % max_linecard_count - 1) * max_linecard_port_count + sfp_index * (max_linecard_port_count / linecard_port_count) + 1
            self.sdk_index = sfp_index

            from .thermal import initialize_linecard_sfp_thermal
            self._thermal_list = initialize_linecard_sfp_thermal(lc_name, slot_id, sfp_index)

        self.slot_id = slot_id

    @property
    def sdk_handle(self):
        if not SFP.shared_sdk_handle:
            SFP.shared_sdk_handle = initialize_sdk_handle()
            if not SFP.shared_sdk_handle:
                logger.log_error('Failed to open SDK handle')
        return SFP.shared_sdk_handle

    def reinit(self):
        """
        Re-initialize this SFP object when a new SFP inserted
        :return:
        """
        self.refresh_xcvr_api()

    def get_presence(self):
        """
        Retrieves the presence of the device

        Returns:
            bool: True if device is present, False if not
        """
        eeprom_raw = self.read_eeprom(0, 1)

        return eeprom_raw is not None

    # Read out any bytes from any offset
    def read_eeprom(self, offset, num_bytes):
        eeprom_raw = []
        ethtool_cmd = "ethtool -m sfp{} hex on offset {} length {}".format(self.index, offset, num_bytes)
        try:
            output = subprocess.check_output(ethtool_cmd,
                                             shell=True,
                                             universal_newlines=True)
            output_lines = output.splitlines()
            first_line_raw = output_lines[0]
            if "Offset" in first_line_raw:
                for line in output_lines[2:]:
                    line_split = line.split()
                    eeprom_raw = eeprom_raw + line_split[1:]
        except subprocess.CalledProcessError as e:
            return None

        eeprom_raw = list(map(lambda h: int(h, base=16), eeprom_raw))
        return bytearray(eeprom_raw)

    @classmethod
    def mgmt_phy_mod_pwr_attr_get(cls, power_attr_type, sdk_handle, sdk_index, slot_id):
        sx_mgmt_phy_mod_pwr_attr_p = new_sx_mgmt_phy_mod_pwr_attr_t_p()
        sx_mgmt_phy_mod_pwr_attr = sx_mgmt_phy_mod_pwr_attr_t()
        sx_mgmt_phy_mod_pwr_attr.power_attr_type = power_attr_type
        sx_mgmt_phy_mod_pwr_attr_t_p_assign(sx_mgmt_phy_mod_pwr_attr_p, sx_mgmt_phy_mod_pwr_attr)
        module_id_info = sx_mgmt_module_id_info_t()
        module_id_info.slot_id = slot_id
        module_id_info.module_id = sdk_index
        try:
            rc = sx_mgmt_phy_module_pwr_attr_get(sdk_handle, module_id_info, sx_mgmt_phy_mod_pwr_attr_p)
            assert SX_STATUS_SUCCESS == rc, "sx_mgmt_phy_module_pwr_attr_get failed {}".format(rc)
            sx_mgmt_phy_mod_pwr_attr = sx_mgmt_phy_mod_pwr_attr_t_p_value(sx_mgmt_phy_mod_pwr_attr_p)
            pwr_mode_attr = sx_mgmt_phy_mod_pwr_attr.pwr_mode_attr
            return pwr_mode_attr.admin_pwr_mode_e, pwr_mode_attr.oper_pwr_mode_e
        finally:
            delete_sx_mgmt_phy_mod_pwr_attr_t_p(sx_mgmt_phy_mod_pwr_attr_p)

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP

        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        if utils.is_host():
            # To avoid performance issue,
            # call class level method to avoid initialize the whole sonic platform API
            get_lpmode_code = 'from sonic_platform import sfp;\n' \
                              'with sfp.SdkHandleContext() as sdk_handle:' \
                              'print(sfp.SFP._get_lpmode(sdk_handle, {}, {}))'.format(self.sdk_index, self.slot_id)
            lpm_cmd = "docker exec pmon python3 -c \"{}\"".format(get_lpmode_code)
            try:
                output = subprocess.check_output(lpm_cmd, shell=True, universal_newlines=True)
                return 'True' in output
            except subprocess.CalledProcessError as e:
                print("Error! Unable to get LPM for {}, rc = {}, err msg: {}".format(self.sdk_index, e.returncode, e.output))
                return False
        else:
            return self._get_lpmode(self.sdk_handle, self.sdk_index, self.slot_id)

    @classmethod
    def _get_lpmode(cls, sdk_handle, sdk_index, slot_id):
        """Class level method to get low power mode.

        Args:
            sdk_handle: SDK handle
            sdk_index (integer): SDK port index
            slot_id (integer): Slot ID

        Returns:
            [boolean]: True if low power mode is on else off
        """
        _, oper_pwr_mode = cls.mgmt_phy_mod_pwr_attr_get(SX_MGMT_PHY_MOD_PWR_ATTR_PWR_MODE_E, sdk_handle, sdk_index, slot_id)
        return oper_pwr_mode == SX_MGMT_PHY_MOD_PWR_MODE_LOW_E

    def reset(self):
        """
        Reset SFP and return all user module settings to their default state.

        Returns:
            A boolean, True if successful, False if not

        refer plugins/sfpreset.py
        """
        if utils.is_host():
            # To avoid performance issue,
            # call class level method to avoid initialize the whole sonic platform API
            reset_code = 'from sonic_platform import sfp;\n' \
                         'with sfp.SdkHandleContext() as sdk_handle:' \
                         'print(sfp.SFP._reset(sdk_handle, {}, {}))' \
                         .format(self.sdk_index, self.slot_id)
            reset_cmd = "docker exec pmon python3 -c \"{}\"".format(reset_code)

            try:
                output = subprocess.check_output(reset_cmd, shell=True, universal_newlines=True)
                return 'True' in output
            except subprocess.CalledProcessError as e:
                print("Error! Unable to set LPM for {}, rc = {}, err msg: {}".format(self.sdk_index, e.returncode, e.output))
                return False
        else:
            return self._reset(self.sdk_handle, self.sdk_index, self.slot_id)

    @classmethod
    def _reset(cls, sdk_handle, sdk_index, slot_id):
        module_id_info = sx_mgmt_module_id_info_t()
        module_id_info.slot_id = slot_id
        module_id_info.module_id = sdk_index
        rc = sx_mgmt_phy_module_reset(sdk_handle, module_id_info)
        if rc != SX_STATUS_SUCCESS:
            logger.log_error("Error occurred when resetting SFP module {}, slot {}, error code {}".format(sdk_index, slot_id, rc))

        return rc == SX_STATUS_SUCCESS


    @classmethod
    def is_nve(cls, port):
        return (port & NVE_MASK) != 0


    @classmethod
    def is_cpu(cls, port):
        return (port & CPU_MASK) != 0


    @classmethod
    def is_port_admin_status_up(cls, sdk_handle, log_port):
        oper_state_p = new_sx_port_oper_state_t_p()
        admin_state_p = new_sx_port_admin_state_t_p()
        module_state_p = new_sx_port_module_state_t_p()
        rc = sx_api_port_state_get(sdk_handle, log_port, oper_state_p, admin_state_p, module_state_p)
        assert rc == SXD_STATUS_SUCCESS, "sx_api_port_state_get failed, rc = %d" % rc

        admin_state = sx_port_admin_state_t_p_value(admin_state_p)

        delete_sx_port_oper_state_t_p(oper_state_p)
        delete_sx_port_admin_state_t_p(admin_state_p)
        delete_sx_port_module_state_t_p(module_state_p)

        return admin_state == SX_PORT_ADMIN_STATUS_UP


    @classmethod
    def set_port_admin_status_by_log_port(cls, sdk_handle, log_port, admin_status):
        rc = sx_api_port_state_set(sdk_handle, log_port, admin_status)
        if SX_STATUS_SUCCESS != rc:
            logger.log_error("sx_api_port_state_set failed, rc = %d" % rc)

        return SX_STATUS_SUCCESS == rc


    @classmethod
    def get_logical_ports(cls, sdk_handle, sdk_index, slot_id):
        # Get all the ports related to the sfp, if port admin status is up, put it to list
        port_attributes_list = new_sx_port_attributes_t_arr(SX_PORT_ATTR_ARR_SIZE)
        port_cnt_p = new_uint32_t_p()
        uint32_t_p_assign(port_cnt_p, SX_PORT_ATTR_ARR_SIZE)

        rc = sx_api_port_device_get(sdk_handle, DEVICE_ID , SWITCH_ID, port_attributes_list,  port_cnt_p)
        assert rc == SX_STATUS_SUCCESS, "sx_api_port_device_get failed, rc = %d" % rc

        port_cnt = uint32_t_p_value(port_cnt_p)
        log_port_list = []
        for i in range(0, port_cnt):
            port_attributes = sx_port_attributes_t_arr_getitem(port_attributes_list, i)
            if not cls.is_nve(int(port_attributes.log_port)) \
               and not cls.is_cpu(int(port_attributes.log_port)) \
               and port_attributes.port_mapping.module_port == sdk_index \
               and port_attributes.port_mapping.slot == slot_id \
               and cls.is_port_admin_status_up(sdk_handle, port_attributes.log_port):
                log_port_list.append(port_attributes.log_port)

        delete_sx_port_attributes_t_arr(port_attributes_list)
        delete_uint32_t_p(port_cnt_p)
        return log_port_list


    @classmethod
    def mgmt_phy_mod_pwr_attr_set(cls, sdk_handle, sdk_index, slot_id, power_attr_type, admin_pwr_mode):
        result = False
        sx_mgmt_phy_mod_pwr_attr = sx_mgmt_phy_mod_pwr_attr_t()
        sx_mgmt_phy_mod_pwr_mode_attr = sx_mgmt_phy_mod_pwr_mode_attr_t()
        sx_mgmt_phy_mod_pwr_attr.power_attr_type = power_attr_type
        sx_mgmt_phy_mod_pwr_mode_attr.admin_pwr_mode_e = admin_pwr_mode
        sx_mgmt_phy_mod_pwr_attr.pwr_mode_attr = sx_mgmt_phy_mod_pwr_mode_attr
        sx_mgmt_phy_mod_pwr_attr_p = new_sx_mgmt_phy_mod_pwr_attr_t_p()
        sx_mgmt_phy_mod_pwr_attr_t_p_assign(sx_mgmt_phy_mod_pwr_attr_p, sx_mgmt_phy_mod_pwr_attr)
        module_id_info = sx_mgmt_module_id_info_t()
        module_id_info.slot_id = slot_id
        module_id_info.module_id = sdk_index
        try:
            rc = sx_mgmt_phy_module_pwr_attr_set(sdk_handle, SX_ACCESS_CMD_SET, module_id_info, sx_mgmt_phy_mod_pwr_attr_p)
            if SX_STATUS_SUCCESS != rc:
                logger.log_error("Error occurred when setting power mode for SFP module {}, slot {}, error code {}".format(sdk_index, slot_id, rc))
                result = False
            else:
                result = True
        finally:
            delete_sx_mgmt_phy_mod_pwr_attr_t_p(sx_mgmt_phy_mod_pwr_attr_p)

        return result


    @classmethod
    def _set_lpmode_raw(cls, sdk_handle, sdk_index, slot_id, ports, attr_type, power_mode):
        result = False
        # Check if the module already works in the same mode
        admin_pwr_mode, oper_pwr_mode = cls.mgmt_phy_mod_pwr_attr_get(attr_type, sdk_handle, sdk_index, slot_id)
        if (power_mode == SX_MGMT_PHY_MOD_PWR_MODE_LOW_E and oper_pwr_mode == SX_MGMT_PHY_MOD_PWR_MODE_LOW_E) \
           or (power_mode == SX_MGMT_PHY_MOD_PWR_MODE_AUTO_E and admin_pwr_mode == SX_MGMT_PHY_MOD_PWR_MODE_AUTO_E):
            return True
        try:
            # Bring the port down
            for port in ports:
                cls.set_port_admin_status_by_log_port(sdk_handle, port, SX_PORT_ADMIN_STATUS_DOWN)
            # Set the desired power mode
            result = cls.mgmt_phy_mod_pwr_attr_set(sdk_handle, sdk_index, slot_id, attr_type, power_mode)
        finally:
            # Bring the port up
            for port in ports:
                cls.set_port_admin_status_by_log_port(sdk_handle, port, SX_PORT_ADMIN_STATUS_UP)

        return result


    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP

        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override

        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        if utils.is_host():
            # To avoid performance issue,
            # call class level method to avoid initialize the whole sonic platform API
            set_lpmode_code = 'from sonic_platform import sfp;\n' \
                              'with sfp.SdkHandleContext() as sdk_handle:' \
                              'print(sfp.SFP._set_lpmode({}, sdk_handle, {}, {}))' \
                              .format('True' if lpmode else 'False', self.sdk_index, self.slot_id)
            lpm_cmd = "docker exec pmon python3 -c \"{}\"".format(set_lpmode_code)

            # Set LPM
            try:
                output = subprocess.check_output(lpm_cmd, shell=True, universal_newlines=True)
                return 'True' in output
            except subprocess.CalledProcessError as e:
                print("Error! Unable to set LPM for {}, rc = {}, err msg: {}".format(self.sdk_index, e.returncode, e.output))
                return False
        else:
            return self._set_lpmode(lpmode, self.sdk_handle, self.sdk_index, self.slot_id)


    @classmethod
    def _set_lpmode(cls, lpmode, sdk_handle, sdk_index, slot_id):
        log_port_list = cls.get_logical_ports(sdk_handle, sdk_index, slot_id)
        sdk_lpmode = SX_MGMT_PHY_MOD_PWR_MODE_LOW_E if lpmode else SX_MGMT_PHY_MOD_PWR_MODE_AUTO_E
        cls._set_lpmode_raw(sdk_handle,
                            sdk_index,
                            slot_id,
                            log_port_list,
                            SX_MGMT_PHY_MOD_PWR_ATTR_PWR_MODE_E,
                            sdk_lpmode)
        logger.log_info("{} low power mode for module {}, slot {}".format("Enabled" if lpmode else "Disabled", sdk_index, slot_id))
        return True

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return True

    def _get_error_code(self):
        """
        Get error code of the SFP module

        Returns:
            The error code fetch from SDK API
        """
        module_id_info_list = new_sx_mgmt_module_id_info_t_arr(1)
        module_info_list = new_sx_mgmt_phy_module_info_t_arr(1)

        module_id_info = sx_mgmt_module_id_info_t()
        module_id_info.slot_id = 0
        module_id_info.module_id = self.sdk_index
        sx_mgmt_module_id_info_t_arr_setitem(module_id_info_list, 0, module_id_info)

        rc = sx_mgmt_phy_module_info_get(self.sdk_handle, module_id_info_list, 1, module_info_list)
        assert SX_STATUS_SUCCESS == rc, "sx_mgmt_phy_module_info_get failed, error code {}".format(rc)

        mod_info = sx_mgmt_phy_module_info_t_arr_getitem(module_info_list, 0)
        return mod_info.module_state.oper_state, mod_info.module_state.error_type

    @classmethod
    def _get_error_description_dict(cls):
        return {0: cls.SFP_ERROR_DESCRIPTION_POWER_BUDGET_EXCEEDED,
                1: cls.SFP_MLNX_ERROR_DESCRIPTION_LONGRANGE_NON_MLNX_CABLE,
                2: cls.SFP_ERROR_DESCRIPTION_I2C_STUCK,
                3: cls.SFP_ERROR_DESCRIPTION_BAD_EEPROM,
                4: cls.SFP_MLNX_ERROR_DESCRIPTION_ENFORCE_PART_NUMBER_LIST,
                5: cls.SFP_ERROR_DESCRIPTION_UNSUPPORTED_CABLE,
                6: cls.SFP_ERROR_DESCRIPTION_HIGH_TEMP,
                7: cls.SFP_ERROR_DESCRIPTION_BAD_CABLE,
                8: cls.SFP_MLNX_ERROR_DESCRIPTION_PMD_TYPE_NOT_ENABLED,
                12: cls.SFP_MLNX_ERROR_DESCRIPTION_PCIE_POWER_SLOT_EXCEEDED,
                255: cls.SFP_MLNX_ERROR_DESCRIPTION_RESERVED
        }

    def get_error_description(self):
        """
        Get error description

        Args:
            error_code: The error code returned by _get_error_code

        Returns:
            The error description
        """
        oper_status, error_code = self._get_error_code()
        if oper_status == SX_PORT_MODULE_STATUS_INITIALIZING:
            error_description = self.SFP_STATUS_INITIALIZING
        elif oper_status == SX_PORT_MODULE_STATUS_PLUGGED:
            error_description = self.SFP_STATUS_OK
        elif oper_status == SX_PORT_MODULE_STATUS_UNPLUGGED:
            error_description = self.SFP_STATUS_UNPLUGGED
        elif oper_status == SX_PORT_MODULE_STATUS_PLUGGED_DISABLED:
            error_description = self.SFP_STATUS_DISABLED
        elif oper_status == SX_PORT_MODULE_STATUS_PLUGGED_WITH_ERROR:
            error_description_dict = self._get_error_description_dict()
            if error_code in error_description_dict:
                error_description = error_description_dict[error_code]
            else:
                error_description = "Unknown error ({})".format(error_code)
        else:
            error_description = "Unknow SFP module status ({})".format(oper_status)
        return error_description
