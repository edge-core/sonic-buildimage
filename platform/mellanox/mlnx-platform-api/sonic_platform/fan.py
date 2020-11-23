#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the FANs status which are available in the platform
#
#############################################################################

import os.path
import subprocess

try:
    from sonic_platform_base.fan_base import FanBase
    from .utils import read_int_from_file, read_str_from_file, write_file
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

LED_ON = 1
LED_OFF = 0

PWM_MAX = 255

FAN_PATH = "/var/run/hw-management/thermal/"
LED_PATH = "/var/run/hw-management/led/"
CONFIG_PATH = "/var/run/hw-management/config"
# fan_dir isn't supported on Spectrum 1. It is supported on Spectrum 2 and later switches
FAN_DIR = "/var/run/hw-management/system/fan_dir"
COOLING_STATE_PATH = "/var/run/hw-management/thermal/cooling_cur_state"

# Platforms with unplugable FANs:
# 1. don't have fanX_status and should be treated as always present
platform_with_unplugable_fan = ['x86_64-mlnx_msn2010-r0', 'x86_64-mlnx_msn2100-r0']


class Fan(FanBase):
    """Platform-specific Fan class"""

    STATUS_LED_COLOR_ORANGE = "orange"
    min_cooling_level = 2
    MIN_VALID_COOLING_LEVEL = 1
    MAX_VALID_COOLING_LEVEL = 10
    # PSU fan speed vector
    PSU_FAN_SPEED = ['0x3c', '0x3c', '0x3c', '0x3c', '0x3c',
                     '0x3c', '0x3c', '0x46', '0x50', '0x5a', '0x64']

    def __init__(self, has_fan_dir, fan_index, drawer_index = 1, psu_fan = False, platform = None):
        # API index is starting from 0, Mellanox platform index is starting from 1
        self.index = fan_index + 1
        self.drawer_index = drawer_index + 1

        self.is_psu_fan = psu_fan
        self.always_presence = False if platform not in platform_with_unplugable_fan else True

        if not self.is_psu_fan:
            self.fan_speed_get_path = "fan{}_speed_get".format(self.index)
            self.fan_speed_set_path = "fan{}_speed_set".format(self.index)
            self.fan_presence_path = "fan{}_status".format(self.drawer_index)
            self.fan_max_speed_path = os.path.join(FAN_PATH, "fan{}_max".format(self.index))
            self.fan_min_speed_path = os.path.join(FAN_PATH, "fan{}_min".format(self.index))
            self._name = "fan{}".format(self.index)
        else:
            self.fan_speed_get_path = "psu{}_fan1_speed_get".format(self.index)
            self.fan_presence_path = "psu{}_fan1_speed_get".format(self.index)
            self._name = 'psu_{}_fan_{}'.format(self.index, 1)
            self.fan_max_speed_path = os.path.join(CONFIG_PATH, "psu_fan_max")
            self.fan_min_speed_path = os.path.join(CONFIG_PATH, "psu_fan_min")
            self.psu_i2c_bus_path = os.path.join(CONFIG_PATH, 'psu{0}_i2c_bus'.format(self.index))
            self.psu_i2c_addr_path = os.path.join(CONFIG_PATH, 'psu{0}_i2c_addr'.format(self.index))
            self.psu_i2c_command_path = os.path.join(CONFIG_PATH, 'fan_command')

        self.fan_status_path = "fan{}_fault".format(self.index)
        self.fan_green_led_path = "led_fan{}_green".format(self.drawer_index)
        self.fan_red_led_path = "led_fan{}_red".format(self.drawer_index)
        self.fan_orange_led_path = "led_fan{}_orange".format(self.drawer_index)
        self.fan_pwm_path = "pwm1"
        self.fan_led_cap_path = "led_fan{}_capability".format(self.drawer_index)
        if has_fan_dir:
            self.fan_dir = FAN_DIR
        else:
            self.fan_dir = None


    def get_direction(self):
        """
        Retrieves the fan's direction

        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction

        Notes:
            What Mellanox calls forward: 
            Air flows from fans side to QSFP side, for example: MSN2700-CS2F
            which means intake in community
            What Mellanox calls reverse:
            Air flow from QSFP side to fans side, for example: MSN2700-CS2R
            which means exhaust in community
            According to hw-mgmt:
                1 stands for forward, in other words intake
                0 stands for reverse, in other words exhaust
        """
        if not self.fan_dir or self.is_psu_fan or not self.get_presence():
            return self.FAN_DIRECTION_NOT_APPLICABLE

        try:
            with open(os.path.join(self.fan_dir), 'r') as fan_dir:
                fan_dir_bits = int(fan_dir.read().strip())
                fan_mask = 1 << self.drawer_index - 1
                if fan_dir_bits & fan_mask:
                    return self.FAN_DIRECTION_INTAKE
                else:
                    return self.FAN_DIRECTION_EXHAUST
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to read fan direction status to {}".format(repr(e)))


    def get_name(self):
        return self._name

    def get_status(self):
        """
        Retrieves the operational status of fan

        Returns:
            bool: True if fan is operating properly, False if not
        """
        status = 0
        if self.is_psu_fan:
            status = 0
        else:
            status = read_int_from_file(os.path.join(FAN_PATH, self.fan_status_path), 1)

        return status == 0

    def get_presence(self):
        """
        Retrieves the presence status of fan

        Returns:
            bool: True if fan is present, False if not
        """
        status = 0
        if self.is_psu_fan:
            if os.path.exists(os.path.join(FAN_PATH, self.fan_presence_path)):
                status = 1
            else:
                status = 0
        else:
            if self.always_presence:
                status = 1
            else:
                status = read_int_from_file(os.path.join(FAN_PATH, self.fan_presence_path), 0)

        return status == 1

    def get_speed(self):
        """
        Retrieves the speed of fan

        Returns:
            int: percentage of the max fan speed
        """
        speed = 0
        speed_in_rpm = read_int_from_file(os.path.join(FAN_PATH, self.fan_speed_get_path))

        max_speed_in_rpm = read_int_from_file(self.fan_max_speed_path)
        if max_speed_in_rpm == 0:
            return speed_in_rpm

        speed = 100*speed_in_rpm/max_speed_in_rpm
        if speed > 100:
            speed = 100

        return speed

    def get_target_speed(self):
        """
        Retrieves the expected speed of fan

        Returns:
            int: percentage of the max fan speed
        """
        if self.is_psu_fan:
            try:
                # Get PSU fan target speed according to current system cooling level
                cooling_level = self.get_cooling_level()
                return int(self.PSU_FAN_SPEED[cooling_level], 16)
            except Exception:
                return self.get_speed()

        pwm = read_int_from_file(os.path.join(FAN_PATH, self.fan_speed_set_path))
        return int(round(pwm*100.0/PWM_MAX))

    def set_speed(self, speed):
        """
        Set fan speed to expected value

        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 0 (off) to 100 (full speed)

        Returns:
            bool: True if set success, False if fail. 
        """
        status = True

        if self.is_psu_fan:
            if not self.get_presence():
                return False
            from .thermal import logger
            try:
                bus = read_str_from_file(self.psu_i2c_bus_path, raise_exception=True)
                addr = read_str_from_file(self.psu_i2c_addr_path, raise_exception=True)
                command = read_str_from_file(self.psu_i2c_command_path, raise_exception=True)
                speed = Fan.PSU_FAN_SPEED[int(speed / 10)]
                command = "i2cset -f -y {0} {1} {2} {3} wp".format(bus, addr, command, speed)
                subprocess.check_call(command, shell = True)
                return True
            except subprocess.CalledProcessError as ce:
                logger.log_error('Failed to call command {}, return code={}, command output={}'.format(ce.cmd, ce.returncode, ce.output))
                return False
            except Exception as e:
                logger.log_error('Failed to set PSU FAN speed - {}'.format(e))
                return False

        try:
            cooling_level = int(speed / 10)
            if cooling_level < self.min_cooling_level:
                cooling_level = self.min_cooling_level
                speed = self.min_cooling_level * 10
            self.set_cooling_level(cooling_level, cooling_level)
            pwm = int(round(PWM_MAX*speed/100.0))
            write_file(os.path.join(FAN_PATH, self.fan_speed_set_path), pwm, raise_exception=True)
        except (ValueError, IOError):
            status = False

        return status
    
    def _get_led_capability(self):
        cap_list = None
        try:
            with open(os.path.join(LED_PATH, self.fan_led_cap_path), 'r') as fan_led_cap:
                    caps = fan_led_cap.read()
                    cap_list = caps.split()
        except (ValueError, IOError):
            status = 0
        
        return cap_list

    def set_status_led(self, color):
        """
        Set led to expected color

        Args:
            color: A string representing the color with which to set the
                   fan module status LED

        Returns:
            bool: True if set success, False if fail. 
        """
        led_cap_list = self._get_led_capability()
        if led_cap_list is None:
            return False

        if self.is_psu_fan:
            # PSU fan led status is not able to set
            return False
        status = False
        try:
            if color == 'green':
                with open(os.path.join(LED_PATH, self.fan_green_led_path), 'w') as fan_led:
                    fan_led.write(str(LED_ON))
            elif color == 'red':
                # Some fan don't support red led but support orange led, in this case we set led to orange
                if 'red' in led_cap_list:
                    led_path = os.path.join(LED_PATH, self.fan_red_led_path)
                elif 'orange' in led_cap_list:
                    led_path = os.path.join(LED_PATH, self.fan_orange_led_path)
                else:
                    return False
                with open(led_path, 'w') as fan_led:
                    fan_led.write(str(LED_ON))

            elif color == 'off':
                with open(os.path.join(LED_PATH, self.fan_green_led_path), 'w') as fan_led:
                    fan_led.write(str(LED_OFF))

                with open(os.path.join(LED_PATH, self.fan_red_led_path), 'w') as fan_led:
                    fan_led.write(str(LED_OFF))
            else:
                status = False
        except (ValueError, IOError):
                    status = False
        return status

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan

        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        # The tolerance value is fixed as 50% for all the Mellanox platform
        return 50

    @classmethod
    def set_cooling_level(cls, level, cur_state):
        """
        Change cooling level. The input level should be an integer value [1, 10].
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
            # Reset FAN cooling level vector. According to low level team,
            # if we need set cooling level to X, we need first write a (10+X) 
            # to cooling_cur_state file to reset the cooling level vector.
            write_file(COOLING_STATE_PATH, level + 10, raise_exception=True)

            # We need set cooling level after resetting the cooling level vector 
            write_file(COOLING_STATE_PATH, cur_state, raise_exception=True)
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to set cooling level - {}".format(e))

    @classmethod
    def get_cooling_level(cls):
        try:
            return read_int_from_file(COOLING_STATE_PATH, raise_exception=True)
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to get cooling level - {}".format(e))

