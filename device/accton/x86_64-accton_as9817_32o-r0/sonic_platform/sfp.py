#############################################################################
# Edgecore
#
# Sfp contains an implementation of SONiC Platform Base API and
# provides the sfp device status which are available in the platform
#
#############################################################################

try:
    import time
    from sonic_platform_base.sonic_xcvr.sfp_optoe_base import SfpOptoeBase
    from .helper import APIHelper
    from sonic_py_common.general import getstatusoutput_noshell
    from sonic_py_common import logger
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FPGA_PCIE_PATH = "/sys/devices/platform/as9817_32_fpga/"
EEPROM_PATH = '/sys/bus/i2c/devices/{}-00{}/eeprom'

SFP_MUX_I2C_BUS = '42'
SFP_MUX_I2C_ADDR = '0x1b'

log = logger.Logger()

class Sfp(SfpOptoeBase):
    """Platform-specific Sfp class"""

    # Port number
    PORT_START = 1
    PORT_END = 34

    SFP_TYPE_CODE_LIST = [
        0x03,  # SFP/SFP+/SFP28
        0x0b   # DWDM-SFP/SFP+
    ]
    QSFP_TYPE_CODE_LIST = [
        0x0c, # QSFP
        0x0d, # QSFP+ or later
        0x11, # QSFP28 or later
        0xe1  # QSFP28 EDFA
    ]
    QSFP_DD_TYPE_CODE_LIST = [
        0x18, # QSFP-DD Double Density 8X Pluggable Transceiver
        0x1E  # QSFP+ or later with CMIS
    ]
    OSFP_TYPE_CODE_LIST = [
        0x19  # OSFP
    ]

    SFP_TYPE = "SFP"
    QSFP_TYPE = "QSFP"
    OSFP_TYPE = "OSFP"
    QSFP_DD_TYPE = "QSFP_DD"

    UPDATE_DONE = "Done"
    EEPROM_DATA_NOT_READY = "eeprom not ready"
    UNKNOWN_SFP_TYPE_ID = "unknow sfp ID"

    SFP_MUX_DIR_CPU = 1
    SFP_MUX_DIR_FRONT = 2
    SFP_MUX_SPEED_1G = 1
    SFP_MUX_SPEED_10G = 2
    SFP_MUX_SPEED_25G = 3
    SFP_MUX_CHANNEL = {
        33 : [0, 1, 4, 5],# ['0x01', '0x02', '0x10', '0x20']
        34 : [2, 3, 6, 7] # ['0x04', '0x08', '0x40', '0x80']
    }

    _port_to_i2c_mapping = {
         1:2,   2:3,   3:4,   4:5,
         5:6,   6:7,   7:8,   8:9,
         9:10, 10:11, 11:12, 12:13,
        13:14, 14:15, 15:16, 16:17,
        17:18, 18:19, 19:20, 20:21,
        21:22, 22:23, 23:24, 24:25,
        25:26, 26:27, 27:28, 28:29,
        29:30, 30:31, 31:32, 32:33,
        33:34, 34:35,
    }

    _speed_dict = {
        1000  : SFP_MUX_SPEED_1G,
        10000 : SFP_MUX_SPEED_10G,
        25000 : SFP_MUX_SPEED_25G
    }

    def __init__(self, sfp_index=0, intf_name="Unknown"):
        SfpOptoeBase.__init__(self)
        self._api_helper=APIHelper()
        self.is_host = self._api_helper.is_host()

        # Init index
        self.port_num = sfp_index + 1
        self.index = self.port_num

        self.name = intf_name

        # Init eeprom path
        self.port_to_eeprom_mapping = {}
        for x in range(self.PORT_START, self.PORT_END + 1):
            self.port_to_eeprom_mapping[x] = EEPROM_PATH.format(
                self._port_to_i2c_mapping[x], "50")

        # SONiC will use 'sfp_type' for configuring the media type.
        self.sfp_type = self.QSFP_TYPE
        self.update_sfp_type()

    def get_eeprom_path(self):
        # print(self.port_to_eeprom_mapping[self.port_num])
        return self.port_to_eeprom_mapping[self.port_num]

    def get_reset_status(self):
        """
        Retrieves the reset status of SFP
        Returns:
            A Boolean, True if reset enabled, False if disabled
        """
        reset_path = "{}{}{}".format(FPGA_PCIE_PATH, 'module_reset_', self.port_num)

        val = self._api_helper.read_txt_file(reset_path)
        if val is not None:
            return int(val, 10) == 1

        return False

    def get_lpmode(self):
        """
        Retrieves the lpmode (low power mode) status of this SFP
        Returns:
            A Boolean, True if lpmode is enabled, False if disabled
        """
        if self.port_num > 32:
            # SFP doesn't support this feature
            return False

        if self.sfp_type in [self.QSFP_DD_TYPE, self.OSFP_TYPE]:
            api = self.get_xcvr_api()
            return api.get_lpmode()
        else:
            lpmode_path = "{}{}{}".format(FPGA_PCIE_PATH, '/module_lp_mode_', self.port_num)

            val=self._api_helper.read_txt_file(lpmode_path)
            if val is not None:
                return int(val, 10)==1

        return False

    def reset(self):
        """
        Reset SFP and return all user module settings to their default srate.
        Returns:
            A boolean, True if successful, False if not
        """
        if not self.get_presence():
            return False

        # Check for invalid port_num
        if self.port_num > 32:
            return False # SFP doesn't support this feature

        reset_path = "{}{}{}".format(FPGA_PCIE_PATH, 'module_reset_', self.port_num)
        ret = self._api_helper.write_txt_file(reset_path, 1)
        if ret is not True:
            return ret

        time.sleep(0.2)
        ret = self._api_helper.write_txt_file(reset_path, 0)
        time.sleep(0.2)

        return ret

    def set_lpmode(self, lpmode):
        """
        Sets the lpmode (low power mode) of SFP
        Args:
            lpmode: A Boolean, True to enable lpmode, False to disable it
            Note  : lpmode can be overridden by set_power_override
        Returns:
            A boolean, True if lpmode is set successfully, False if not
        """
        if not self.get_presence():
            return False

        if self.port_num > 32:
            return False # SFP doesn't support this feature

        if self.sfp_type in [self.QSFP_DD_TYPE, self.OSFP_TYPE]:
            api = self.get_xcvr_api()
            ret = api.set_lpmode(lpmode)
        else:
            lpmode_path = "{}{}{}".format(FPGA_PCIE_PATH, 'module_lp_mode_', self.port_num)

            if lpmode is True:
                ret = self._api_helper.write_txt_file(lpmode_path, 1) #enable lpmode
            else:
                ret = self._api_helper.write_txt_file(lpmode_path, 0) #disable lpmode

        return ret

    def tx_disable(self, tx_disable):
        """
        Disable SFP TX for all channels
        Args:
            tx_disable : A Boolean, True to enable tx_disable mode, False to disable
                         tx_disable mode.
        Returns:
            A boolean, True if tx_disable is set successfully, False if not
        """
        if not self.get_presence():
            return False

        if self.port_num < 33:
            api = self.get_xcvr_api()
            if api is None:
                return False

            ret = api.tx_disable(tx_disable)
        else:
            txdisable_path = "{}{}{}".format(FPGA_PCIE_PATH, 'module_tx_disable_', self.port_num)

            if tx_disable is True:
                ret = self._api_helper.write_txt_file(txdisable_path, 1) #enable tx_disable
            else:
                ret = self._api_helper.write_txt_file(txdisable_path, 0) #disable tx_disable

        return ret

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return self.name

    def get_presence(self):
        """
        Retrieves the presence of the device
        Returns:
            bool: True if device is present, False if not
        """
        present_path = "{}{}{}".format(FPGA_PCIE_PATH, '/module_present_', self.port_num)

        val = self._api_helper.read_txt_file(present_path)
        if val is not None:
            return int(val, 10)==1

        return False

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence()

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device. If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of entPhysicalContainedIn is '0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device or -1 if cannot determine the position
        """
        return self.port_num

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return True

    def update_sfp_type(self):
        """
        Updates the sfp type

        """
        if not self.get_presence():
            return self.EEPROM_DATA_NOT_READY

        ret = self.UPDATE_DONE
        eeprom_raw = []
        eeprom_raw = self.read_eeprom(0, 1)
        if eeprom_raw and hasattr(self,'sfp_type'):
            if eeprom_raw[0] in self.SFP_TYPE_CODE_LIST:
                self.sfp_type = self.SFP_TYPE
            elif eeprom_raw[0] in self.QSFP_TYPE_CODE_LIST:
                self.sfp_type = self.QSFP_TYPE
            elif eeprom_raw[0] in self.QSFP_DD_TYPE_CODE_LIST:
                self.sfp_type = self.QSFP_DD_TYPE
            elif eeprom_raw[0] in self.OSFP_TYPE_CODE_LIST:
                self.sfp_type = self.OSFP_TYPE
            else:
                ret = self.UNKNOWN_SFP_TYPE_ID
        else:
            ret = self.EEPROM_DATA_NOT_READY

        return ret

    def validate_eeprom_sfp(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(0, 96)
        if eeprom_raw is None:
            return False

        for i in range(0, 63):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[63]:
                return False

        checksum_test = 0
        for i in range(64, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 96)
        if eeprom_raw is None:
            return False

        for i in range(0, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        return True

    def validate_eeprom_qsfp(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(128, 96)
        if eeprom_raw is None:
            return None

        for i in range(0, 63):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[63]:
                return False

        checksum_test = 0
        for i in range(64, 95):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[95]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        return True

    def validate_eeprom_cmis(self):
        checksum_test = 0
        eeprom_raw = self.read_eeprom(128, 95)
        if eeprom_raw is None:
            return None

        for i in range(0, 94):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[94]:
                return False

        api = self.get_xcvr_api()
        if api is None:
            return False

        if api.is_flat_memory():
            return True

        checksum_test = 0
        eeprom_raw = self.read_eeprom(258, 126)
        if eeprom_raw is None:
            return None

        for i in range(0, 125):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[125]:
                return False

        checksum_test = 0
        eeprom_raw = self.read_eeprom(384, 128)
        if eeprom_raw is None:
            return None

        for i in range(0, 127):
            checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
        else:
            if checksum_test != eeprom_raw[127]:
                return False

        # CMIS_5.0 starts to support the checksum of page 04h
        cmis_rev = float(api.get_cmis_rev())
        if cmis_rev >= 5.0:
            checksum_test = 0
            eeprom_raw = self.read_eeprom(640, 128)
            if eeprom_raw is None:
                return None

            for i in range(0, 127):
                checksum_test = (checksum_test + eeprom_raw[i]) & 0xFF
            else:
                if checksum_test != eeprom_raw[127]:
                    return False

        return True

    def validate_eeprom(self):
        id_byte_raw = self.read_eeprom(0, 1)
        if id_byte_raw is None:
            return False

        id = id_byte_raw[0]
        if id in self.QSFP_TYPE_CODE_LIST:
            return self.validate_eeprom_qsfp()
        elif id in self.SFP_TYPE_CODE_LIST:
            return self.validate_eeprom_sfp()
        elif id in self.QSFP_DD_TYPE_CODE_LIST:
            return self.validate_eeprom_cmis()
        elif id in self.OSFP_TYPE_CODE_LIST:
            return self.validate_eeprom_cmis()
        else:
            return False

    def validate_temperature(self):
        temperature = self.get_temperature()
        if temperature is None:
            return False

        threshold_dict = self.get_transceiver_threshold_info()
        if threshold_dict is None:
            return False

        if isinstance(temperature, float) is not True:
            return True

        if isinstance(threshold_dict['temphighalarm'], float) is not True:
            return True

        return threshold_dict['temphighalarm'] > temperature

    def __get_error_description(self):
        if not self.get_presence():
            return self.SFP_STATUS_UNPLUGGED

        err_stat = self.SFP_STATUS_BIT_INSERTED

        status = self.validate_eeprom()
        if status is not True:
            err_stat = (err_stat | self.SFP_ERROR_BIT_BAD_EEPROM)

        status = self.validate_temperature()
        if status is not True:
            err_stat = (err_stat | self.SFP_ERROR_BIT_HIGH_TEMP)

        if err_stat is self.SFP_STATUS_BIT_INSERTED:
            return self.SFP_STATUS_OK
        else:
            err_desc = ''
            cnt = 0
            for key in self.SFP_ERROR_BIT_TO_DESCRIPTION_DICT:
                if (err_stat & key) != 0:
                    if cnt > 0:
                        err_desc = err_desc + "|"
                        cnt = cnt + 1
                    err_desc = err_desc + self.SFP_ERROR_BIT_TO_DESCRIPTION_DICT[key]

            return err_desc

    def get_error_description(self):
        """
        Retrives the error descriptions of the SFP module

        Returns:
            String that represents the current error descriptions of vendor specific errors
            In case there are multiple errors, they should be joined by '|',
            like: "Bad EEPROM|Unsupported cable"
        """
        if not self.get_presence():
            return self.SFP_STATUS_UNPLUGGED

        try:
            state =  super().get_error_description()
            if state is None:
                return self.SFP_STATUS_OK
            return state
        except NotImplementedError:
            return self.__get_error_description()

    def _set_i2c_register(self, bus=None, device=None, register=None, value=None):
        bus = bus or SFP_MUX_I2C_BUS
        device = device or SFP_MUX_I2C_ADDR
        if self.is_host:
            cmd = ['sudo', '/usr/sbin/i2cset', '-f', '-y', str(bus), str(device), str(register), str(value)]
        else: # Inside pmon container
            cmd = ['/usr/sbin/i2cset', '-f', '-y', str(bus), str(device), str(register), str(value)]
        status, output = getstatusoutput_noshell(cmd)
        if status != 0:
            log.log_error(f"Error setting {cmd}: {output}")
            return False
        return True

    def _set_register_sequence(self, register_values):
        for register, value in register_values:
            if not self._set_i2c_register(register=register, value=value):
                return False
        return True

    def _df810_txfir_set(self, offset, pre, main, post):
        channel = 1 << offset
        channel_val = f"0x{channel:02x}"

        main_sign = 0x80 if main > 0 else 0x40
        pre_sign, pre_val = (0x40, -pre) if pre <= 0 else (0x00, pre)
        post_sign, post_val = (0x40, -post) if post <= 0 else (0x00, post)

        main_val = f"0x{main | main_sign:02x}"
        pre_val = f"0x{pre_val | pre_sign:02x}"
        post_val = f"0x{post_val | post_sign:02x}"

        register_values = [
            ('0xff', '0x01'),
            ('0xfc', channel_val),
            ('0x3d', '0x80'), # Enable Pre- and Post-cursor FIR
            ('0x3d', '0x80'), # main-cursor sign
            ('0x3f', '0x40'), # post-cursor sign
            ('0x3e', '0x40'), # pre-cursor sign
            ('0x3d', main_val),
            ('0x3f', post_val),
            ('0x3e', pre_val)
        ]

        if not self._set_register_sequence(register_values):
            return False

    def _df810_cdr_bw_set(self, offset, param1, param2):
        channel = 1 << offset
        channel_val = f"0x{channel:02x}"

        param1_val = f"0x{param1:02x}"
        param2_val = f"0x{param2:02x}"
        register_values = [
            ('0xff', '0x01'),
            ('0xfc', channel_val),
            ('0x1c', param1_val),
            ('0x9e', param2_val),
            ('0x9', '0x8'),
            ('0xa', '0x40'),
        ]

        if not self._set_register_sequence(register_values):
            return False

    def _df810_cross_point(self):
        if not self._set_i2c_register(register="0xff", value="0x01"):
            return False

        for offset in self.SFP_MUX_CHANNEL[self.port_num]:
            channel_val = 1 << offset

            register_values = [
                ('0xfc', f'0x{channel_val:02x}'),
                ('0x95', '0x08'),
                ('0x96', '0x00'),
                ('0x96', '0x04'),
                ('0x96', '0x04'),
                ('0x96', '0x06'),
                ('0x96', '0x06'),
                ('0x0a', '0x0c'),
                ('0x0a', '0x00'),
                ('0x79', '0x11')
            ]

            if not self._set_register_sequence(register_values):
                return False

    def set_sfp_mux(self, is_front_port=True, cfg_speed=25000):
        """Set the SFP MUX configuration.

        Args:
            is_front_port (bool): Determines the direction of the MUX.
                                  True for FRONT, False for CPU.
            cfg_speed (int): The speed configuration in Mbps.

        Raises:
            ValueError: If the cfg_speed is not supported or if an invalid direction/speed is provided.

        Returns:
            bool: True if the operation succeeds, False otherwise.
        """
        # The MUX configuration is only for MGMT ports
        if self.port_num < 33:
            return False

        # Determine MUX direction
        direction = self.SFP_MUX_DIR_FRONT if is_front_port else self.SFP_MUX_DIR_CPU
        speed = self._speed_dict.get(cfg_speed)

        # Validate speed
        if speed is None:
            supported_speeds = ", ".join(map(str, self._speed_dict.keys()))
            raise ValueError(
                f"Error: Invalid speed {cfg_speed}."
                f"Supported speeds are: {supported_speeds}."
            )

        # Validate direction and speed compatibility
        if direction == self.SFP_MUX_DIR_CPU and speed != self.SFP_MUX_SPEED_10G:
            raise ValueError("Error: CPU direction only supports SFP_MUX_SPEED_10G.")

        # Enable df810 MUX
        if not self._set_i2c_register(device="0x72", register="0x00", value="0x01"):
            return False

        for offset in self.SFP_MUX_CHANNEL[self.port_num]:
            channel_val = 1 << offset

            # By default, these parametere are set to self.SFP_MUX_SPEED_25G.
            register_values = [
                ('0xfc', f'0x{channel_val:02x}'), # Select channel
                ('0xff', '0x01'), # Bit 1 = 1: Allows customer to write to all channels,
                                  # Bit 0 = 1: Enables SMBus access to the channels specified in register 0xFC.
                ('0x00', '0x04'), # Bit 2 = 1: Reset channel registers to power-up defaults.
                ('0x0a', '0x0c'), # Bit 3 = 1: Enable CDR Reset override.
                                  # Bit 2 = 1: CDR Reset override bit.
                ('0x2f', '0x54'), # Bit 5-3  : RATE, 25.78125 Gbps = 0x50
                                  # Bit 2 = 1: Enable the PPM to be used as a qualifier when performing Lock Detect.
                ('0x31', '0x40'), # Bit 6-5 = 10: adapt CTLE until optimal, then DFE, then CTLE again.
                ('0x1e', '0xe3'), # Bit 7-5 = 111: Output mode for when the CDR is not locked.
                                  #                For these values to take effect, Reg_0x09[5] must be set to 0, which is
                                  #                111: Mute (Default)
                                  # bit 1 = 1: Enable DFE taps 3-5. DFE_PD must also be set to 0.
                                  # bit 0 = 1: Normal operation. Enable PFD frequency detector.
                ('0x0a', '0x00')
            ]

            if speed == self.SFP_MUX_SPEED_1G:
                register_values[3:8] = [
                    ('0x31', '0x00'),  # adapt mode 0: no adaption
                    ('0x1e', '0x09'),  # puts device into RAW mode
                    ('0x2d', '0x38'),  # Enable EQ boost override
                    ('0x03', '0x00'),  # Set EQ boost value as 0
                    ('0x8e', '0x01')   # vga_sel_gain=1
                ]
                register_values.append(('0x13', '0xb0')) # set EQ gain to 1
            elif speed == self.SFP_MUX_SPEED_10G:
                register_values[4] = ('0x2f', '0x04')

            if not self._set_register_sequence(register_values):
                return False

        if direction == self.SFP_MUX_DIR_CPU: # Only support self.SFP_MUX_SPEED_10G
            if self.port_num == 33:
                self._df810_txfir_set(0, 0, 17, -2)
                self._df810_txfir_set(4, 0, 9, 0)
                self._df810_cdr_bw_set(4, 0x24, 0xfc)
            elif self.port_num == 34:
                self._df810_txfir_set(2, 0, 17, -2)
                self._df810_txfir_set(6, 0, 9, 0)
                self._df810_cdr_bw_set(6, 0x24, 0xfc)
        elif direction == self.SFP_MUX_DIR_FRONT:
            txfir_settings = {
                self.SFP_MUX_SPEED_1G: {
                    33: (1, 0, 11, 0),
                    34: (3, 0, 11, 0),
                },
                self.SFP_MUX_SPEED_10G: {
                    33: (1, 0, 15, -3),
                    34: (3, 0, 15, -3),
                },
                self.SFP_MUX_SPEED_25G: {
                    33: (1, -8, 22, 0),
                    34: (3, -8, 22, 0),
                }
            }
            self._df810_txfir_set(*txfir_settings[speed][self.port_num])

            self._df810_cross_point()

        # Disable df810 MUX
        if not self._set_i2c_register(device="0x72", register="0x00", value="0x00"):
            return False

        return True
