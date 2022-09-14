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
        SX_PORT_ADMIN_STATUS_UP = True
        SX_PORT_ADMIN_STATUS_DOWN = False
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

RJ45_TYPE = "RJ45"

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

# SFP constants
SFP_PAGE_SIZE = 256
SFP_UPPER_PAGE_OFFSET = 128
SFP_VENDOR_PAGE_START = 640

BYTES_IN_DWORD = 4

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

class MlxregManager:
    def __init__(self, mst_pci_device, slot_id, sdk_index):
        self.mst_pci_device = mst_pci_device
        self.slot_id = slot_id
        self.sdk_index = sdk_index

    def construct_dword(self, write_buffer):
        if len(write_buffer) == 0:
            return None

        used_bytes_in_dword = len(write_buffer) % BYTES_IN_DWORD

        res = "dword[0]=0x"
        for idx, x in enumerate(write_buffer):
            word = hex(x)[2:]

            if (idx > 0) and (idx % BYTES_IN_DWORD) == 0:
                res += ",dword[{}]=0x".format(str((idx + 1)//BYTES_IN_DWORD))
            res += word.zfill(2)

        if used_bytes_in_dword > 0:
            res += (BYTES_IN_DWORD - used_bytes_in_dword) * "00"
        return res

    def write_mlxreg_eeprom(self, num_bytes, dword, device_address, page):
        if not dword:
            return False

        try:
            cmd = "mlxreg -d /dev/mst/{} --reg_name MCIA --indexes \
                    slot_index={},module={},device_address={},page_number={},i2c_device_address=0x50,size={},bank_number=0 \
                    --set {} -y".format(self.mst_pci_device, self.slot_id, self.sdk_index, device_address, page, num_bytes, dword)
            subprocess.check_call(cmd, shell=True, universal_newlines=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            logger.log_error("Error! Unable to write data dword={} for {} port, page {} offset {}, rc = {}, err msg: {}".format(dword, self.sdk_index, page, device_address, e.returncode, e.output))
            return False
        return True

    def read_mlxred_eeprom(self, offset, page, num_bytes):
        try:
            cmd = "mlxreg -d /dev/mst/{} --reg_name MCIA --indexes \
                    slot_index={},module={},device_address={},page_number={},i2c_device_address=0x50,size={},bank_number=0 \
                    --get".format(self.mst_pci_device, self.slot_id, self.sdk_index, offset, page, num_bytes)
            result = subprocess.check_output(cmd, universal_newlines=True, shell=True)
        except subprocess.CalledProcessError as e:
            logger.log_error("Error! Unable to read data for {} port, page {} offset {}, rc = {}, err msg: {}".format(self.sdk_index, page, offset, e.returncode, e.output))
            return None
        return result

    def parse_mlxreg_read_output(self, read_output, num_bytes):
        if not read_output:
            return None

        res = ""
        dword_num = num_bytes // BYTES_IN_DWORD
        used_bytes_in_dword = num_bytes % BYTES_IN_DWORD
        arr = [value for value in read_output.split('\n') if value[0:5] == "dword"]
        for i in range(dword_num):
            dword = arr[i].split()[2]
            res += dword[2:]

        if used_bytes_in_dword > 0:
            # Cut needed info and insert into final hex string
            # Example: 3 bytes : 0x12345600
            #                      ^    ^
            dword = arr[dword_num].split()[2]
            res += dword[2 : 2 + used_bytes_in_dword * 2]

        return bytearray.fromhex(res) if res else None

class SdkHandleContext(object):
    def __init__(self):
        self.sdk_handle = None

    def __enter__(self):
        self.sdk_handle = initialize_sdk_handle()
        return self.sdk_handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        deinitialize_sdk_handle(self.sdk_handle)


class NvidiaSFPCommon(SfpOptoeBase):
    def __init__(self, sfp_index):
        super(NvidiaSFPCommon, self).__init__()
        self.index = sfp_index + 1
        self.sdk_index = sfp_index

    @property
    def sdk_handle(self):
        if not SFP.shared_sdk_handle:
            SFP.shared_sdk_handle = initialize_sdk_handle()
            if not SFP.shared_sdk_handle:
                logger.log_error('Failed to open SDK handle')
        return SFP.shared_sdk_handle

    @classmethod
    def _get_module_info(self, sdk_handle, sdk_index):
        """
        Get error code of the SFP module

        Returns:
            The error code fetch from SDK API
        """
        module_id_info_list = new_sx_mgmt_module_id_info_t_arr(1)
        module_info_list = new_sx_mgmt_phy_module_info_t_arr(1)

        module_id_info = sx_mgmt_module_id_info_t()
        module_id_info.slot_id = 0
        module_id_info.module_id = sdk_index
        sx_mgmt_module_id_info_t_arr_setitem(module_id_info_list, 0, module_id_info)

        rc = sx_mgmt_phy_module_info_get(sdk_handle, module_id_info_list, 1, module_info_list)
        assert SX_STATUS_SUCCESS == rc, "sx_mgmt_phy_module_info_get failed, error code {}".format(rc)

        mod_info = sx_mgmt_phy_module_info_t_arr_getitem(module_info_list, 0)
        return mod_info.module_state.oper_state, mod_info.module_state.error_type


class SFP(NvidiaSFPCommon):
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

    def __init__(self, sfp_index, sfp_type=None, slot_id=0, linecard_port_count=0, lc_name=None):
        super(SFP, self).__init__(sfp_index)
        self._sfp_type = sfp_type

        if slot_id == 0: # For non-modular chassis
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
        self.mst_pci_device = self.get_mst_pci_device()

    # get MST PCI device name
    def get_mst_pci_device(self):
        device_name = None
        try:
            device_name = subprocess.check_output("ls /dev/mst/ | grep pciconf", universal_newlines=True, shell=True).strip()
        except subprocess.CalledProcessError as e:
            logger.log_error("Failed to find mst PCI device rc={} err.msg={}".format(e.returncode, e.output))
        return device_name

    '''
    @property
    def sdk_handle(self):
        if not SFP.shared_sdk_handle:
            SFP.shared_sdk_handle = initialize_sdk_handle()
            if not SFP.shared_sdk_handle:
                logger.log_error('Failed to open SDK handle')
        return SFP.shared_sdk_handle
    '''

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
    def _read_eeprom_specific_bytes(self, offset, num_bytes):
        if offset + num_bytes > SFP_VENDOR_PAGE_START:
            logger.log_error("Error mismatch between page size and bytes to read (offset: {} num_bytes: {}) ".format(offset, num_bytes))
            return None

        eeprom_raw = []
        ethtool_cmd = "ethtool -m sfp{} hex on offset {} length {}".format(self.index, offset, num_bytes)
        try:
            output = subprocess.check_output(ethtool_cmd,
                                             shell=True,
                                             universal_newlines=True,
                                             stderr=subprocess.PIPE)
            output_lines = output.splitlines()
            first_line_raw = output_lines[0]
            if "Offset" in first_line_raw:
                for line in output_lines[2:]:
                    line_split = line.split()
                    eeprom_raw = eeprom_raw + line_split[1:]
        except subprocess.CalledProcessError as e:
            logger.log_notice("Failed to get EEPROM data for sfp {}: {}".format(self.index, e.stderr))
            return None

        eeprom_raw = list(map(lambda h: int(h, base=16), eeprom_raw))
        return bytearray(eeprom_raw)

    # read eeprom specfic bytes beginning from offset with size as num_bytes
    def read_eeprom(self, offset, num_bytes):
        """
        Read eeprom specfic bytes beginning from a random offset with size as num_bytes
        Returns:
            bytearray, if raw sequence of bytes are read correctly from the offset of size num_bytes
            None, if the read_eeprom fails
        Example:
            mlxreg -d /dev/mst/mt52100_pciconf0 --reg_name MCIA --indexes slot_index=0,module=1,device_address=148,page_number=0,i2c_device_address=0x50,size=16,bank_number=0 -g
            Sending access register...
            Field Name            | Data
            ===================================
            status                | 0x00000000
            slot_index            | 0x00000000
            module                | 0x00000001
            l                     | 0x00000000
            device_address        | 0x00000094
            page_number           | 0x00000000
            i2c_device_address    | 0x00000050
            size                  | 0x00000010
            bank_number           | 0x00000000
            dword[0]              | 0x43726564
            dword[1]              | 0x6f202020
            dword[2]              | 0x20202020
            dword[3]              | 0x20202020
            dword[4]              | 0x00000000
            dword[5]              | 0x00000000
            ....
        16 bytes to read from dword -> 0x437265646f2020202020202020202020 -> Credo
        """
        # recalculate offset and page. Use 'ethtool' if there is no need to read vendor pages
        if offset < SFP_VENDOR_PAGE_START:
            return self._read_eeprom_specific_bytes(offset, num_bytes)
        else:
            page = (offset - SFP_PAGE_SIZE) // SFP_UPPER_PAGE_OFFSET + 1
            # calculate offset per page
            device_address = (offset - SFP_PAGE_SIZE) % SFP_UPPER_PAGE_OFFSET + SFP_UPPER_PAGE_OFFSET

        if not self.mst_pci_device:
            return None

        mlxreg_mngr = MlxregManager(self.mst_pci_device, self.slot_id, self.sdk_index)
        read_output = mlxreg_mngr.read_mlxred_eeprom(device_address, page, num_bytes)
        return mlxreg_mngr.parse_mlxreg_read_output(read_output, num_bytes)

    # write eeprom specfic bytes beginning from offset with size as num_bytes
    def write_eeprom(self, offset, num_bytes, write_buffer):
        """
        write eeprom specfic bytes beginning from a random offset with size as num_bytes
        and write_buffer as the required bytes
        Returns:
            Boolean, true if the write succeeded and false if it did not succeed.
        Example:
            mlxreg -d /dev/mst/mt52100_pciconf0 --reg_name MCIA --indexes slot_index=0,module=1,device_address=154,page_number=5,i2c_device_address=0x50,size=1,bank_number=0 --set dword[0]=0x01000000 -y
        """
        if num_bytes != len(write_buffer):
            logger.log_error("Error mismatch between buffer length and number of bytes to be written")
            return False

        # recalculate offset and page
        if offset < SFP_PAGE_SIZE:
            page = 0
            device_address = offset
        else:
            page = (offset - SFP_PAGE_SIZE) // SFP_UPPER_PAGE_OFFSET + 1
            # calculate offset per page
            device_address = (offset - SFP_PAGE_SIZE) % SFP_UPPER_PAGE_OFFSET + SFP_UPPER_PAGE_OFFSET

        if not self.mst_pci_device:
            return False

        mlxreg_mngr = MlxregManager(self.mst_pci_device, self.slot_id, self.sdk_index)
        dword = mlxreg_mngr.construct_dword(write_buffer)
        return mlxreg_mngr.write_mlxreg_eeprom(num_bytes, dword, device_address, page)

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
    def _fetch_port_status(cls, sdk_handle, log_port):
        oper_state_p = new_sx_port_oper_state_t_p()
        admin_state_p = new_sx_port_admin_state_t_p()
        module_state_p = new_sx_port_module_state_t_p()
        rc = sx_api_port_state_get(sdk_handle, log_port, oper_state_p, admin_state_p, module_state_p)
        assert rc == SXD_STATUS_SUCCESS, "sx_api_port_state_get failed, rc = %d" % rc

        admin_state = sx_port_admin_state_t_p_value(admin_state_p)
        oper_state = sx_port_oper_state_t_p_value(oper_state_p)

        delete_sx_port_oper_state_t_p(oper_state_p)
        delete_sx_port_admin_state_t_p(admin_state_p)
        delete_sx_port_module_state_t_p(module_state_p)

        return oper_state, admin_state


    @classmethod
    def is_port_admin_status_up(cls, sdk_handle, log_port):
        _, admin_state = cls._fetch_port_status(sdk_handle, log_port);
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
            error_code: The error code returned by _get_module_info

        Returns:
            The error description
        """
        oper_status, error_code = self._get_module_info(self.sdk_handle, self.sdk_index)
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


class RJ45Port(NvidiaSFPCommon):
    """class derived from SFP, representing RJ45 ports"""

    def __init__(self, sfp_index):
        super(RJ45Port, self).__init__(sfp_index)
        self.sfp_type = RJ45_TYPE

    @classmethod
    def _get_presence(cls, sdk_handle, sdk_index):
        """Class level method to get low power mode.

        Args:
            sdk_handle: SDK handle
            sdk_index (integer): SDK port index
            slot_id (integer): Slot ID

        Returns:
            [boolean]: True if low power mode is on else off
        """
        oper_status, _ = cls._get_module_info(sdk_handle, sdk_index)
        return print(oper_status == SX_PORT_MODULE_STATUS_PLUGGED)

    def get_presence(self):
        """
        Retrieves the presence of the device
        For RJ45 ports, it always return True

        Returns:
            bool: True if device is present, False if not
        """
        if utils.is_host():
            # To avoid performance issue,
            # call class level method to avoid initialize the whole sonic platform API
            get_presence_code = 'from sonic_platform import sfp;\n' \
                              'with sfp.SdkHandleContext() as sdk_handle:' \
                              'print(sfp.RJ45Port._get_presence(sdk_handle, {}))'.format(self.sdk_index)
            presence_cmd = "docker exec pmon python3 -c \"{}\"".format(get_presence_code)
            try:
                output = subprocess.check_output(presence_cmd, shell=True, universal_newlines=True)
                return 'True' in output
            except subprocess.CalledProcessError as e:
                print("Error! Unable to get presence for {}, rc = {}, err msg: {}".format(self.sdk_index, e.returncode, e.output))
                return False
        else:
            oper_status, _ = self._get_module_info(self.sdk_handle, self.sdk_index);
            return (oper_status == SX_PORT_MODULE_STATUS_PLUGGED)

    def get_transceiver_info(self):
        """
        Retrieves transceiver info of this port.
        For RJ45, all fields are N/A

        Returns:
            A dict which contains following keys/values :
        ================================================================================
        keys                       |Value Format   |Information
        ---------------------------|---------------|----------------------------
        type                       |1*255VCHAR     |type of SFP
        vendor_rev                 |1*255VCHAR     |vendor revision of SFP
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
        transceiver_info_keys = ['manufacturer',
                                 'model',
                                 'vendor_rev',
                                 'serial',
                                 'vendor_oui',
                                 'vendor_date',
                                 'connector',
                                 'encoding',
                                 'ext_identifier',
                                 'ext_rateselect_compliance',
                                 'cable_type',
                                 'cable_length',
                                 'specification_compliance',
                                 'nominal_bit_rate',
                                 'application_advertisement']
        transceiver_info_dict = dict.fromkeys(transceiver_info_keys, 'N/A')
        transceiver_info_dict['type'] = self.sfp_type

        return transceiver_info_dict

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP

        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        return False

    def reset(self):
        """
        Reset SFP and return all user module settings to their default state.

        Returns:
            A boolean, True if successful, False if not

        refer plugins/sfpreset.py
        """
        return False

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP

        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override

        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        return False

    def get_error_description(self):
        """
        Get error description

        Args:
            error_code: Always false on SN2201

        Returns:
            The error description
        """
        return False

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
        return False

    def read_eeprom(self, offset, num_bytes):
        return None

    def reinit(self):
        """
        Nothing to do for RJ45. Just provide it to avoid exception
        :return:
        """
        return
