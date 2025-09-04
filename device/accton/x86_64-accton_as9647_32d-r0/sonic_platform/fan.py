#############################################################################
# Edgecore
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################

try:
    from sonic_platform_base.fan_base import FanBase
    from sonic_platform import platform
    from .helper import APIHelper
    from .thermal import logger
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PSU_FAN_MAX_RPM = 30000 # Taken from SPEC FSH082-610G Rev A12 at "9. Fans Control Requirement"
TRAY_FRONT_FAN_MAX_RPM = 31000
TRAY_REAR_FAN_MAX_RPM = 28000

# The tolerance was set to 15% RPM to cover the worst-case deviation of 13.15% RPM,
# which occurs at the minimum fan speed of 40% RPM.
TRAY_FANSPEED_TOLERANCE = 15

FP_FAN_LED_FILE = "/sys/class/leds/as9647_32d_led::fan/brightness"
CPLD_I2C_PATH = "/sys/bus/i2c/devices/10-0066/fan"
FAN_LED_MODE = CPLD_I2C_PATH + "_led_mode"
FAN_PERCENTAGE = CPLD_I2C_PATH + "_duty_cycle_percentage"
FAN_REQUESTED_PERCENTAGE = "/tmp/fan_requested_rpm_percentage"
FAN_CONFIGURED_PERCENTAGE = "/tmp/fan_configured_rpm_percentage"
PSU_I2C_PATH ="/sys/bus/i2c/devices/{}-00{}/"
PSU_HWMON_I2C_MAPPING = {
    0: {
        "num": 3,
        "addr": "59"
    },
    1: {
        "num": 2,
        "addr": "58"
    },
}

PSU_CPLD_I2C_MAPPING = {
    0: {
        "num": 3,
        "addr": "51"
    },
    1: {
        "num": 2,
        "addr": "50"
    },
}

LED_DEBUG_MODE_OFF = "0"
LED_DEBUG_MODE_ON = "1"

# Format: PWM DC Percentage, # PWM Code
FAN_PWM_CODE_SPEED_LIST = [
    0.0,    # 0
    31.25,  # 1
    31.25,  # 2
    31.25,  # 3
    31.25,  # 4
    37.5,   # 5
    43.75,  # 6
    50.0,   # 7
    56.25,  # 8
    62.5,   # 9
    68.75,  # 10
    75.0,   # 11
    81.25,  # 12
    87.5,   # 13
    93.75,  # 14
    100.0   # 15
]

class Fan(FanBase):
    """Platform-specific Fan class"""
    
    MIN_VALID_COOLING_LEVEL = 1
    MAX_VALID_COOLING_LEVEL = 10
    min_cooling_level = 2
    current_cooling_level = min_cooling_level

    def __init__(self, fan_tray_index, fan_index=0, is_psu_fan=False, psu_index=0):
        # Front panel fan LED
        self.SYSFANLED_MODES = {
            "0" : self.STATUS_LED_COLOR_OFF,
            "1" : self.STATUS_LED_COLOR_GREEN,
            "3" : self.STATUS_LED_COLOR_AMBER
        }
        # Fan drawer status LED
        self.FANLED_MODES = {
            "3" : self.STATUS_LED_COLOR_OFF,
            "2" : self.STATUS_LED_COLOR_GREEN,
            "1" : self.STATUS_LED_COLOR_RED
        }

        self._api_helper=APIHelper()
        self.fan_index = fan_index
        self.fan_tray_index = fan_tray_index
        self.is_psu_fan = is_psu_fan
        if self.is_psu_fan:
            self.psu_index = psu_index
            self.psu_i2c_num = PSU_HWMON_I2C_MAPPING[self.psu_index]['num']
            self.psu_i2c_addr = PSU_HWMON_I2C_MAPPING[self.psu_index]['addr']
            self.psu_hwmon_path = PSU_I2C_PATH.format(
                self.psu_i2c_num, self.psu_i2c_addr)

            self.psu_i2c_num = PSU_CPLD_I2C_MAPPING[self.psu_index]['num']
            self.psu_i2c_addr = PSU_CPLD_I2C_MAPPING[self.psu_index]['addr']
            self.psu_cpld_path = PSU_I2C_PATH.format(
                self.psu_i2c_num, self.psu_i2c_addr)

        FanBase.__init__(self)

    def get_name(self):
        """
        Retrieves fan name
        Returns:
            A string with fan name either from fan tray or from psu
        """
        if self.is_psu_fan:
            fan_name = "PSU {} fan {}".format(self.psu_index+1, self.fan_index)
        else:
            fan_name = "FanTray {} fan {}".format(self.fan_tray_index, self.fan_index)

        return fan_name

    def get_model(self):
        """
        Retrieves the fan model
        Returns:
            string: The model of the device

        """
        return "R40W12BGNL9-07T17"

    def get_serial(self):
        """
        Retrieves the fan serial
        Returns:
            string: The serial of the device

        """
        return "N/A"

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return True

    def get_direction(self):
        """
        Retrieves the direction of fan
        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        if not self.is_psu_fan:
            dir_str = "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index+1, '_direction')
            val = self._api_helper.read_txt_file(dir_str)
            if val is not None:
                if val == '0': #F2B
                    direction = self.FAN_DIRECTION_EXHAUST
                else:
                    direction = self.FAN_DIRECTION_INTAKE
            else:
                direction = self.FAN_DIRECTION_EXHAUST

        else: #For PSU
            direction = self.FAN_DIRECTION_EXHAUST # FIX_ME

        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        """
        speed = 0
        if self.is_psu_fan:
            psu_fan_path= "{}{}".format(self.psu_hwmon_path, 'psu_fan1_speed_rpm')
            fan_speed_rpm = self._api_helper.read_txt_file(psu_fan_path)
            if fan_speed_rpm is not None:
                speed = (int(fan_speed_rpm, 10)) * 100 / PSU_FAN_MAX_RPM
                if speed > 100:
                    speed = 100
            else:
                return 0

        elif self.get_presence():
            if 0 == self.fan_index:
                speed_rpm = "_front_speed_rpm"
            else:
                speed_rpm = "_rear_speed_rpm"
            speed = self._api_helper.read_txt_file(
                "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index + 1, speed_rpm))
            if speed is None:
                return 0

            speed_max_rpm = TRAY_FRONT_FAN_MAX_RPM
            if self.fan_index == 1:
                speed_max_rpm = TRAY_REAR_FAN_MAX_RPM
            speed = (int(speed, 10)) * 100 / speed_max_rpm
            if speed > 100:
                speed = 100

        return int(speed)

    def get_target_speed(self):
        """
        Retrieves the target (requested) speed of the fan.
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        """
        if self.is_psu_fan:
            return 100
        elif self.get_presence():
            speed = 100
            try:
                speed = int(self._api_helper.read_txt_file(FAN_REQUESTED_PERCENTAGE))
            except:
                pass
            return speed
        else:
            return None

    def get_configured_speed(self):
        """
        Retrieves the configured speed of the fan.
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        Notes:
            This is a platform-specific function and does not belong to the base class.
            This function was created to check speed tolerances against the configured
            speed supported by the fan, rather than the requested target speed.
        """
        if self.is_psu_fan:
            return 100
        elif self.get_presence():
            speed = 100
            try:
                speed = int(self._api_helper.read_txt_file(FAN_CONFIGURED_PERCENTAGE))
            except:
                pass
            return speed
        else:
            return None

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        tolerance = TRAY_FANSPEED_TOLERANCE
        if self.is_psu_fan:
            tolerance = 100

        return tolerance

    def is_under_speed(self):
        """
        Calculates whether the fan speed falls below the low-speed threshold tolerance

        This function checks whether the current fan speed is below the allowed
        tolerance relative to the target/configured fan speed.
        This function uses the target fan speed for PSU fans and the configured
        hardware-supported fan speed for all other fans.

        Returns:
            A boolean, True if fan speed is under the low threshold, False if not
        """
        speed = self.get_speed()
        tolerance = self.get_speed_tolerance()
        if self.is_psu_fan:
            target_speed = self.get_target_speed()
        else:
            target_speed = self.get_configured_speed()

        for param, value in (('speed', speed), ('target speed', target_speed), ('speed tolerance', tolerance)):
            if not isinstance(value, int):
                raise TypeError(f'Fan {param} is not an integer value: {param}={value}')
            if value < 0 or value > 100:
                raise ValueError(f'Fan {param} is not a valid percentage value: {param}={value}')

        return speed * 100 < target_speed * (100 - tolerance)

    def is_over_speed(self):
        """
        Calculates whether the fan speed exceeds the high-speed threshold tolerance

        This function checks whether the current fan speed exceeds the allowed
        tolerance relative to the target/configured fan speed.
        This function uses the target fan speed for PSU fans and the configured
        hardware-supported fan speed for all other fans.

        Returns:
            A boolean, True if fan speed is over the high threshold, False if not
        """
        speed = self.get_speed()
        tolerance = self.get_speed_tolerance()
        if self.is_psu_fan:
            target_speed = self.get_target_speed()
        else:
            target_speed = self.get_configured_speed()

        for param, value in (('speed', speed), ('target speed', target_speed), ('speed tolerance', tolerance)):
            if not isinstance(value, int):
                raise TypeError(f'Fan {param} is not an integer value: {param}={value}')
            if value < 0 or value > 100:
                raise ValueError(f'Fan {param} is not a valid percentage value: {param}={value}')

        return speed * 100 > target_speed * (100 + tolerance)

    def set_speed(self, speed):
        """
        Sets the fan speed
        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 0 (off) to 100 (full speed)
        Returns:
            A boolean, True if speed is set successfully, False if not
        Notes:
            This function accepts a speed value in RPM percentage and converts
            it to a PWM percentage for the fan driver.

            The fan driver configures the fan speed based on predefined speed steps.

            The configured fan speed is converted from PWM to RPM, the difference
            between the configured and measured RPM is then calculated and compared
            against the allowed RPM tolerance.

            The equations for converting between RPM percentage and PWM percentage are:
                For front fan:
                    RPM_Value = (279 * PWM_Percentage) + 3100
                    RPM_Percentage = (RPM_Value / 31000) * 100
                For rear fan:
                    RPM Value = 252 * PWM Percentage + 2800
                    RPM_Percentage = (RPM_Value / 28000) * 100

            Since this function now accepts fan speed as a RPM percentage and the
            thermal control logic uses increments of 10%, the valid input range
            is 40% - 100%, as fan speeds below 40% are non-linear. This range is not
            enforced here, as it is already handled by the fan driver.
            The minimum RPM percentage of 40% is equivalent to PWM percentage of 33%.
        """

        if not self.is_psu_fan and self.get_presence():
            if self.fan_index == 0:
                speed_rpm_max = TRAY_FRONT_FAN_MAX_RPM
                slope = 279
                intercept = 3100
            else:
                speed_rpm_max = TRAY_REAR_FAN_MAX_RPM
                slope = 252
                intercept = 2800

            # Calculation Flow: Requested RPM → Requested PWM → PWM Code → Actual PWM → Actual RPM
            req_rpm_speed_perc = int(speed)
            req_rpm_speed_val = int(req_rpm_speed_perc * speed_rpm_max / 100)
            req_pwm_speed_perc = int((req_rpm_speed_val - intercept) / slope)
            req_pwm_code = int(req_pwm_speed_perc * 100 / 625) - 1
            cfg_pwm_speed_perc = FAN_PWM_CODE_SPEED_LIST[req_pwm_code]
            cfg_rpm_speed_val = int(cfg_pwm_speed_perc * slope + intercept)
            cfg_rpm_speed_perc = int(cfg_rpm_speed_val / speed_rpm_max * 100)
            sts1 = self._api_helper.write_txt_file(FAN_PERCENTAGE, req_pwm_speed_perc)
            sts2 = self._api_helper.write_txt_file(FAN_REQUESTED_PERCENTAGE, req_rpm_speed_perc)
            sts3 = self._api_helper.write_txt_file(FAN_CONFIGURED_PERCENTAGE, cfg_rpm_speed_perc)
            return sts1 and sts2 and sts3

        return False

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        Notes:
            The following notes are applicable only to fans that are not related to the PSU.
            This function handle the fan drawer LED status, not the fan LED status.
            This fan drawer LED status is managed by default in auto mode via the fan CPLD.
            It can be controlled by software only when the `fan drawer LED mode` is set to
            debug mode.
            This function also manages the front panel fan LED status based on the status of
            all fan drawer LEDs.
        """
        if not self.is_psu_fan:
            sts1 = False

            # This code is executed when the `fan drawer LED mode` is set to debug mode.
            led_mode = self._api_helper.read_txt_file(FAN_LED_MODE)
            if led_mode == LED_DEBUG_MODE_ON:
                filename = "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index + 1, '_led')
                for key, val in self.FANLED_MODES.items():
                    if val == color:
                        sts1 = self._api_helper.write_txt_file(filename, key)
            else:
                sts1 = True

            # Set the front panel fan LED based on the status of all fan drawer LEDs
            fp_led_color = 'green'
            fans = platform.Platform().get_chassis().get_all_fans()
            for fan in fans:
                if fan.get_status_led() == 'red':
                    # Force `amber` instead of `red` since there is no option for 'red' in hardware
                    fp_led_color = 'amber'
            sts2 = self.set_front_panel_status_led(fp_led_color)

            return sts1 and sts2
        else:
            if self.get_presence():
                platform_chassis = platform.Platform().get_chassis()
                psu = platform_chassis.get_psu(self.psu_index)
                return psu.set_status_led(color)
            else:
                return False

    def get_status_led(self):
        """
        Gets the state of the fan module status LED
        Args:
            No
        Returns:
            string: representing the color with which is the status of
                   fan modules
        Notes:
            The following notes are applicable only to fans that are not related to the PSU.
            This function read the fan drawer LED status, not the fan LED status.
            This fan drawer LED status is managed by default in auto mode via the fan CPLD.
            It can be controlled by software only when the `fan drawer LED mode` is set to
            debug mode.
            This fanction implements the fan drawer LED status to ensure the correct hardware
            LED indication is displayed via the `show platform fan` command.
        """
        if not self.is_psu_fan:
            filename = "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index + 1, '_led')
            key = self._api_helper.read_txt_file(filename)
            return self.FANLED_MODES.get(key, 'N/A')
        else:
            platform_chassis = platform.Platform().get_chassis()
            psu = platform_chassis.get_psu(self.psu_index)
            return psu.get_status_led()

    def set_front_panel_status_led(self, color):
        """
        Sets the state of the front panel fan status LED
        Args:
            color: A string representing the color with which to set the
                   fan drawer status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        for key, val in self.SYSFANLED_MODES.items():
            if val == color:
                return self._api_helper.write_txt_file(FP_FAN_LED_FILE, key)
        return False

    def get_presence(self):
        """
        Retrieves the presence of the FAN
        Returns:
            bool: True if FAN is present, False if not
        """
        if self.is_psu_fan:
            present_path = "{}{}".format(self.psu_cpld_path, 'psu_present')
        else:
            present_path = "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index + 1, '_present')

        val = self._api_helper.read_txt_file(present_path)
        if val is not None:
            return int(val, 10) == 1
        else:
            return False

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if self.is_psu_fan:
            psu_fan_path = "{}{}".format(self.psu_hwmon_path, 'psu_fan1_speed_rpm')
            val = self._api_helper.read_txt_file(psu_fan_path)
            if val is not None:
                return int(val, 10) != 0
            else:
                return False
        else:
            path = "{}{}{}".format(CPLD_I2C_PATH, self.fan_tray_index + 1, '_fault')
            val = self._api_helper.read_txt_file(path)
            if val is not None:
                return int(val, 10) == 0
            else:
                return False

    @classmethod
    def get_cooling_level(cls):
        """
        Class method
        Returns:
            int: Current cooling level in range 1..10, means cooling level number * 10%
        """
        return cls.current_cooling_level

    @classmethod
    def set_cooling_level(cls, level, cur_state):
        """
        Changes cooling level. The input level should be an integer value 1..10.
        1 means 10%, 2 means 20%, 10 means 100%.
        """
        if not isinstance(level, int):
            raise RuntimeError("Failed to set cooling level, input parameter must be integer")

        if level < cls.MIN_VALID_COOLING_LEVEL or level > cls.MAX_VALID_COOLING_LEVEL:
            raise RuntimeError("Failed to set cooling level, level value must be in range [{}, {}], got {}".format(
                cls.MIN_VALID_COOLING_LEVEL,
                cls.MAX_VALID_COOLING_LEVEL,
                level
                ))
        try:
            from sonic_platform import platform
            platform_chassis = platform.Platform().get_chassis()
            if platform_chassis is not None:
                cls.current_cooling_level = level
                fans_num = platform_chassis.get_num_fans()
                for fan_ins in platform_chassis.get_all_fans():
                    fan_ins.set_speed(level * 10)
            else:
                logger.log_error("Fan: Chassis is not available !")
            # See on top of thermal.py how to enable log_debug
            logger.log_debug("Fan:set_cooling_level: {} x10%".format(str(level)))
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to set cooling level - {}".format(e))

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        Returns:
            integer: The 1-based relative physical position in parent device
        """
        if self.is_psu_fan:
            return (self.psu_index + 1)
        else:
            return (self.fan_index + 1)
