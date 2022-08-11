#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################
try:
    from sonic_platform_base.fan_base import FanBase
    from helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FAN_NAME_LIST = ["FAN-1F", "FAN-1R", "FAN-2F", "FAN-2R", "FAN-3F", "FAN-3R",
                 "FAN-4F", "FAN-4R", "FAN-5F", "FAN-5R", "FAN-6F", "FAN-6R", "FAN-7F", "FAN-7R"]

IPMI_OEM_NETFN = "0x3A"

IPMI_SET_FAN_SPEED_CMD = "0x26 {} {}"  # IPMI_OEM_NETFN + 0x26 + fan id: 0-7 + pwm:20-100
IPMI_AIR_FLOW_CMD = "0x62 {}"  # IPMI_OEM_NETFN + 0x62 + fan id: 0-7
IPMI_FAN_PRESENT_CMD = "0x26 0x03 {}"  # IPMI_OEM_NETFN + 0x26 + fan id: 0-7
IPMI_FAN_SPEED_CMD = "0x26 0x04 {}" # IPMI_OEM_NETFN + 0x26 + fan id: 0-7; RPM = readback value * 150
IPMI_FAN_TARGET_SPEED_CMD = "0x64 0x02 0x01 {}"  # IPMI_OEM_NETFN + 0x64 + fanboard id + r/w flag + REG

FAN_TARGET_SPEED_REG = ["0x22", "0x32", "0x42", "0x52", "0x62", "0x72",
                        "0x82"]  # FAN1-FAN2 FAN CPLD TARGET SPEED REGISTER

IPMI_SET_FAN_LED_CMD = "0x39 0x02 {} {}"  # IPMI_OEM_NETFN + 0x39 0x02 + fan led id: 4-0x0a + fan color: 0-2
IPMI_GET_FAN_LED_CMD = "0x39 0x01 {}"  # IPMI_OEM_NETFN + 0x39 0x01 + fan led id: 4-0x0a

IPMI_GET_PSU1_FAN_SPEED_CMD = "0x3e 0x06 0xb0 2 0x90"
IPMI_GET_PSU2_FAN_SPEED_CMD = "0x3e 0x06 0xb2 2 0x90"

IPMI_SET_PWM = "0x26 0x02 {} {}"
IPMI_FRU_PRINT_ID = "ipmitool fru print {}"
IPMI_SENSOR_LIST_CMD = "ipmitool sensor"
IPMI_FRU_MODEL_KEY = "Board Part Number"
IPMI_FRU_SERIAL_KEY = "Board Serial"

MAX_OUTLET = 30200
MAX_INLET = 32000
SPEED_TOLERANCE = 10

# IPMT_OEM_NETFN + 0x3E + {bus} + {8 bit address} + {read count} + 0x3B:PSU FAN SPEED REG
IPMI_PSU_TARGET_SPEED_CMD = "0x3E {} {} 1 0x3B"
PSU_I2C_BUS = "0x06"
PSU_I2C_ADDR = ["0xB0", "0xB2"]  # PSU1 and PSU2 I2C ADDR
PSU_FAN = "PSU{}_Fan"
PSU_MAX_RPM = 26500

FAN_FRONT = "Fan{}_Front"
FAN_REAR = "Fan{}_Rear"

FAN_LED_OFF_CMD = "0x00"
FAN_LED_GREEN_CMD = "0x01"
FAN_LED_RED_CMD = "0x02"
FAN1_LED_CMD = "0x04"

FAN1_FRU_ID = 6  # silverstoneX has no FAN FRU


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_tray_index, fan_index=0, is_psu_fan=False, psu_index=0):
        self.fan_index = fan_index
        self.fan_tray_index = fan_tray_index
        self.is_psu_fan = is_psu_fan
        if self.is_psu_fan:
            self.psu_index = psu_index
        self._api_helper = APIHelper()
        self.index = self.fan_tray_index * 2 + self.fan_index

    def get_direction(self):
        """
        Retrieves the direction of fan
        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        direction = self.FAN_DIRECTION_EXHAUST
        status, raw_flow = self._api_helper.ipmi_raw(
            IPMI_OEM_NETFN, IPMI_AIR_FLOW_CMD.format(hex(self.fan_tray_index)))
        if status and raw_flow == "01":
           direction = self.FAN_DIRECTION_INTAKE

        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        """
        if self.is_psu_fan:
            max_rpm = PSU_MAX_RPM
            if self.psu_index % 2 == 0:
                status, raw_ss_read = self._api_helper.ipmi_raw(IPMI_OEM_NETFN, IPMI_GET_PSU1_FAN_SPEED_CMD)
            else:
                status, raw_ss_read = self._api_helper.ipmi_raw(IPMI_OEM_NETFN, IPMI_GET_PSU2_FAN_SPEED_CMD)

            raw_ss_read_reverse = raw_ss_read.split()[::-1]
            data_high = ('{0:0{1}b}'.format(int(raw_ss_read_reverse[0], 16), len(raw_ss_read_reverse[0]) * 4))
            n_bin = data_high[:5]
            n = int(n_bin, 2)
            data_low = ('{0:0{1}b}'.format(int(raw_ss_read_reverse[1], 16), len((raw_ss_read_reverse[0]) * 4)))
            y_bin = data_high[-3:] + data_low
            y = int(y_bin, 2)
            rpm_speed = float(y * 2 ** n)
            speed = int(rpm_speed / max_rpm * 100)
        else:
            max_rpm = MAX_OUTLET if self.fan_index % 2 == 0 else MAX_INLET
            status, raw_ss_read = self._api_helper.ipmi_raw(IPMI_OEM_NETFN, IPMI_FAN_SPEED_CMD.format(hex(self.fan_tray_index)))
            if self.fan_index % 2 == 0:  # Front Speed
                ss_read = raw_ss_read.split()[0]
            else:
                ss_read = raw_ss_read.split()[1]    # Rear Speed
            rpm_speed = int(ss_read, 16)*150        # RPM = ss_read * 150
            speed = int(float(rpm_speed) / max_rpm * 100)
        return speed if speed <= 100 else rpm_speed

    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        Note:
            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use
        """
        if self.is_psu_fan is False:
            get_target_speed_cmd = IPMI_FAN_TARGET_SPEED_CMD.format(
                FAN_TARGET_SPEED_REG[self.fan_tray_index])  # raw speed: 0-255
            status, get_target_speed_res = self._api_helper.ipmi_raw(
                IPMI_OEM_NETFN, get_target_speed_cmd)
            target = int(round(float(int(get_target_speed_res, 16)) * 100 / 255))
        else:
            # PSU fan speed can be set and read, but it's not used for FCS by BMC in SilverstoneX, so value in PSU 0x3B register is random and it's meaningless to read back
            # get_target_speed_cmd = IPMI_PSU_TARGET_SPEED_CMD.format(PSU_I2C_BUS,
            #                                                         PSU_I2C_ADDR[self.psu_index])  # raw speed: 0-100
            # status, get_target_speed_res = self._api_helper.ipmi_raw(
            #     IPMI_OEM_NETFN, get_target_speed_cmd)
            # target = int(get_target_speed_res, 16)
            target = "N/A"
        return target

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        return SPEED_TOLERANCE

    def set_speed(self, speed):
        """
        Sets the fan speed
        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 20 (min speed) to 100 (full speed)
        Returns:
            A boolean, True if speed is set successfully, False if not
        Notes:
            pwm setting mode must set as Manual
            manual: ipmitool raw 0x3a 0x26 0x01 0x0
            auto: ipmitool raw 0x3a 0x26 0x01 0x1
        """
        # Force minimun speed as 20% as BMC suggests
        if float(speed) < 20:
            speed = 20
        fan_register_hex = hex(self.fan_tray_index)
        set_speed_cmd = IPMI_SET_PWM.format(fan_register_hex, speed)
        status, set_speed_res = self._api_helper.ipmi_raw(
            IPMI_OEM_NETFN, set_speed_cmd)
        return False if not status else True
        # return False  # not to set fan speed if BMC exists

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not

        Note:
           LED setting mode must set as Manual operation mode first when BMC exsits
           manual: ipmitool raw 0x3A 0x42 0x02 0x00
           auto: ipmitool raw 0x3A 0x42 0x02 0x01
        """
        led_cmd = {
            self.STATUS_LED_COLOR_GREEN: FAN_LED_GREEN_CMD,
            self.STATUS_LED_COLOR_RED: FAN_LED_RED_CMD,
            self.STATUS_LED_COLOR_OFF: FAN_LED_OFF_CMD
        }.get(color)

        fan_selector = hex(int(FAN1_LED_CMD, 16) + self.fan_tray_index)
        status, set_led = self._api_helper.ipmi_raw(
            IPMI_OEM_NETFN, IPMI_SET_FAN_LED_CMD.format(fan_selector, led_cmd))
        set_status_led = False if not status else True

        return set_status_led

    def get_status_led(self):
        """
        Gets the state of the fan status LED
        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above

        Note:
            STATUS_LED_COLOR_GREEN = "green"
            STATUS_LED_COLOR_AMBER = "amber"
            STATUS_LED_COLOR_RED = "red"
            STATUS_LED_COLOR_OFF = "off"
        """
        fan_selector = hex(int(FAN1_LED_CMD, 16) + self.fan_tray_index)
        status, hx_color = self._api_helper.ipmi_raw(
            IPMI_OEM_NETFN, IPMI_GET_FAN_LED_CMD.format(fan_selector))

        status_led = {
            "00": self.STATUS_LED_COLOR_OFF,
            "01": self.STATUS_LED_COLOR_GREEN,
            "02": self.STATUS_LED_COLOR_RED,
        }.get(hx_color, "Unknown")

        return status_led

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        fan_name = FAN_NAME_LIST[
            self.fan_tray_index * 2 + self.fan_index] if not self.is_psu_fan else "PSU-{} FAN-{}".format(
            self.psu_index + 1, self.fan_index + 1)

        return fan_name

    def get_presence(self):
        """
        Retrieves the presence of the FAN
        Returns:
            bool: True if FAN is present, False if not
        """
        presence = False
        status, raw_present = self._api_helper.ipmi_raw(
            IPMI_OEM_NETFN, IPMI_FAN_PRESENT_CMD.format(hex(self.index / 2)))

        if status and raw_present == "00":
            presence = True

        return presence

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        model = "Unknown"
        return model

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        serial = "Unknown"
        # ipmi_fru_idx = self.fan_tray_index + FAN1_FRU_ID
        # status, raw_model = self._api_helper.ipmi_fru_id(
        #    ipmi_fru_idx, IPMI_FRU_SERIAL_KEY)

        # fru_sr_list = raw_model.split()
        # if len(fru_sr_list) > 3:
        #    serial = fru_sr_list[3]

        return serial

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence() and self.get_speed() > 0

