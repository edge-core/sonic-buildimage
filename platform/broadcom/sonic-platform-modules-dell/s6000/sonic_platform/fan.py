#!/usr/bin/env python

########################################################################
# DellEMC S6000
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Fans' information which are available in the platform
#
########################################################################


try:
    import os
    import glob
    from sonic_platform_base.fan_base import FanBase
    from sonic_platform.eeprom import Eeprom
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


MAX_S6000_PSU_FAN_SPEED = 18000
MAX_S6000_FAN_SPEED = 19000


class Fan(FanBase):
    """DellEMC Platform-specific Fan class"""

    CPLD_DIR = "/sys/devices/platform/dell-s6000-cpld.0/"
    I2C_DIR = "/sys/class/i2c-adapter/"

    def __init__(self, fan_index, psu_fan=False, dependency=None):
        self.is_psu_fan = psu_fan
        self.is_driver_initialized = True

        if not self.is_psu_fan:
            # Fan is 1-based in DellEMC platforms
            self.index = fan_index + 1
            self.fan_presence_reg = "fan_prs"
            self.fan_led_reg = "fan{}_led".format(fan_index)
            self.get_fan_speed_reg = self.I2C_DIR + "i2c-11/11-0029/" +\
                    "fan{}_input".format(self.index)
            self.set_fan_speed_reg = self.I2C_DIR + "i2c-11/11-0029/" +\
                    "fan{}_target".format(self.index)
            self.eeprom = Eeprom(is_fan=True, fan_index=self.index)
            self.max_fan_speed = MAX_S6000_FAN_SPEED
            self.supported_led_color = ['off', 'green', 'amber']
        else:
            self.index = fan_index
            self.dependency = dependency
            self.set_fan_speed_reg = self.I2C_DIR +\
                    "i2c-1/1-005{}/fan1_target".format(10 - self.index)

            hwmon_dir = self.I2C_DIR +\
                    "i2c-1/1-005{}/hwmon/".format(10 - self.index)
            try:
                hwmon_node = os.listdir(hwmon_dir)[0]
            except OSError:
                hwmon_node = "hwmon*"
                self.is_driver_initialized = False

            self.get_fan_speed_reg = hwmon_dir + hwmon_node + '/fan1_input'
            self.max_fan_speed = MAX_S6000_PSU_FAN_SPEED

    def _get_cpld_register(self, reg_name):
        # On successful read, returns the value read from given
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'
        cpld_reg_file = self.CPLD_DIR + reg_name

        if (not os.path.isfile(cpld_reg_file)):
            return rv

        try:
           with open(cpld_reg_file, 'r') as fd:
                rv = fd.read()
        except:
            rv = 'ERR'

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def _set_cpld_register(self, reg_name, value):
        # On successful write, returns the value will be written on
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'
        cpld_reg_file = self.CPLD_DIR + reg_name

        if (not os.path.isfile(cpld_reg_file)):
            print "open error"
            return rv

        try:
           with open(cpld_reg_file, 'w') as fd:
                rv = fd.write(str(value))
        except:
            rv = 'ERR'

        return rv

    def _get_i2c_register(self, reg_file):
        # On successful read, returns the value read from given
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'

        if not self.is_driver_initialized:
            reg_file_path = glob.glob(reg_file)
            if len(reg_file_path):
                reg_file = reg_file_path[0]
                self._get_sysfs_path()
            else:
                return rv

        if (not os.path.isfile(reg_file)):
            return rv

        try:
            with open(reg_file, 'r') as fd:
                rv = fd.read()
        except:
            rv = 'ERR'

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def _set_i2c_register(self, reg_file, value):
        # On successful write, the value read will be written on
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'

        if (not os.path.isfile(reg_file)):
            return rv

        try:
            with open(reg_file, 'w') as fd:
                rv = fd.write(str(value))
        except:
            rv = 'ERR'

        return rv

    def _get_sysfs_path(self):
        fan_speed_reg = glob.glob(self.get_fan_speed_reg)

        if len(fan_speed_reg):
            self.get_fan_speed_reg = fan_speed_reg[0]
            self.is_driver_initialized = True

    def get_name(self):
        """
        Retrieves the name of the Fan

        Returns:
            string: The name of the Fan
        """
        if not self.is_psu_fan:
            return "Fan{}".format(self.index)
        else:
            return "PSU{} Fan".format(self.index)

    def get_presence(self):
        """
        Retrieves the presence of the Fan Unit

        Returns:
            bool: True if Fan is present, False if not
        """
        status = False
        if self.is_psu_fan:
            return self.dependency.get_presence()

        fan_presence = self._get_cpld_register(self.fan_presence_reg)
        if (fan_presence != 'ERR'):
            fan_presence = int(fan_presence,16) & self.index
            if fan_presence:
                status = True

        return status

    def get_model(self):
        """
        Retrieves the part number of the Fan

        Returns:
            string: Part number of Fan
        """
        if not self.is_psu_fan:
            return self.eeprom.get_part_number()
        else:
            return 'NA'

    def get_serial(self):
        """
        Retrieves the serial number of the Fan

        Returns:
            string: Serial number of Fan
        """
        # Sample Serial number format "US-01234D-54321-25A-0123-A00"
        if not self.is_psu_fan:
            return self.eeprom.get_serial_number()
        else:
            return 'NA'

    def get_status(self):
        """
        Retrieves the operational status of the Fan

        Returns:
            bool: True if Fan is operating properly, False if not
        """
        status = False
        fan_speed = self._get_i2c_register(self.get_fan_speed_reg)
        if (fan_speed != 'ERR'):
            if (int(fan_speed) > 14000):
                status = True

        return status

    def get_direction(self):
        """
        Retrieves the fan airflow direction

        Returns:
            A string, either FAN_DIRECTION_INTAKE or
            FAN_DIRECTION_EXHAUST depending on fan direction

        Notes:
            In DellEMC platforms,
            - Forward/Exhaust : Air flows from Port side to Fan side.
            - Reverse/Intake  : Air flows from Fan side to Port side.
        """
        if self.is_psu_fan:
            direction = {1: self.FAN_DIRECTION_EXHAUST, 2: self.FAN_DIRECTION_INTAKE,
                         3: self.FAN_DIRECTION_EXHAUST, 4: self.FAN_DIRECTION_INTAKE}
            fan_direction = self.dependency.eeprom.airflow_fan_type()
        else:
            direction = {1: self.FAN_DIRECTION_EXHAUST, 2: self.FAN_DIRECTION_INTAKE}
            fan_direction = self.eeprom.airflow_fan_type()

        return direction.get(fan_direction, self.FAN_DIRECTION_NOT_APPLICABLE)

    def get_speed(self):
        """
        Retrieves the speed of fan

        Returns:
            int: percentage of the max fan speed
        """
        fan_speed = self._get_i2c_register(self.get_fan_speed_reg)
        if (fan_speed != 'ERR') and self.get_presence():
            speed_in_rpm = int(fan_speed, 10)
            speed = (100 * speed_in_rpm)/self.max_fan_speed
        else:
            speed = 0

        return speed

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan

        Returns:
            An integer, the percentage of variance from target speed
            which is considered tolerable
        """
        if self.get_presence():
            # The tolerance value is fixed as 20% for all the DellEmc platform
            tolerance = 20
        else:
            tolerance = 0

        return tolerance

    def set_speed(self, speed):
        """
        Set fan speed to expected value
        Args:
            speed: An integer, the percentage of full fan speed to set
            fan to, in the range 0 (off) to 100 (full speed)
        Returns:
            bool: True if set success, False if fail.
        """
        fan_set = (speed * self.max_fan_speed)/ 100
        rv = self._set_i2c_register(self.set_fan_speed_reg , fan_set)
        if (rv != 'ERR'):
            return True
        else:
            return False

    def set_status_led(self, color):
        """
        Set led to expected color
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if set success, False if fail.
        """
        if self.is_psu_fan or (color not in self.supported_led_color):
            return False
        if(color == self.STATUS_LED_COLOR_AMBER):
            color = 'yellow'

        rv = self._set_cpld_register(self.fan_led_reg ,color)
        if (rv != 'ERR'):
            return True
        else:
            return False

    def get_status_led(self):
        """
        Gets the state of the fan status LED

        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings.
        """
        if self.is_psu_fan:
            # No LED available for PSU Fan
            return None

        fan_led = self._get_cpld_register(self.fan_led_reg)
        if (fan_led != 'ERR'):
            if (fan_led == 'yellow'):
                return self.STATUS_LED_COLOR_AMBER
            else:
                return fan_led
        else:
            return self.STATUS_LED_COLOR_OFF

    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan

        Returns:
            An integer, the percentage of full fan speed, in the range 0
            (off) to 100 (full speed)
        """
        return 79
