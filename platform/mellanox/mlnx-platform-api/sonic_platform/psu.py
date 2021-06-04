#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs status which are available in the platform
#
#############################################################################

try:
    import os.path
    from sonic_platform_base.psu_base import PsuBase
    from sonic_py_common.logger import Logger
    from sonic_platform.fan import Fan
    from sonic_platform.led import Led
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

psu_list = []

PSU_CURRENT = "current"
PSU_VOLTAGE = "voltage"
PSU_POWER = "power"

# SKUs with unplugable PSUs:
# 1. don't have psuX_status and should be treated as always present
# 2. don't have voltage, current and power values
platform_dict_with_unplugable_psu = ['x86_64-mlnx_msn2010-r0', 'x86_64-mlnx_msn2100-r0']

# in most SKUs the file psuX_curr, psuX_volt and psuX_power contain current, voltage and power data respectively. 
# but there are exceptions which will be handled by the following dictionary
platform_dict_psu = {'x86_64-mlnx_msn3420-r0':1, 'x86_64-mlnx_msn3700-r0': 1, 'x86_64-mlnx_msn3700c-r0': 1, 'x86_64-mlnx_msn3800-r0': 1, 'x86_64-mlnx_msn4600c-r0':1, 'x86_64-mlnx_msn4700-r0': 1}
psu_profile_list = [
    # default filename convention
    {
        PSU_CURRENT : "power/psu{}_curr",
        PSU_VOLTAGE : "power/psu{}_volt",
        PSU_POWER : "power/psu{}_power"
    },
    # for 3420, 3700, 3700c, 3800, 4600c, 4700
    {
        PSU_CURRENT : "power/psu{}_curr",
        PSU_VOLTAGE : "power/psu{}_volt_out2",
        PSU_POWER : "power/psu{}_power"
    }
]

class Psu(PsuBase):
    """Platform-specific Psu class"""
    def __init__(self, psu_index, platform):
        global psu_list
        PsuBase.__init__(self)
        # PSU is 1-based on Mellanox platform
        self.index = psu_index + 1
        psu_list.append(self.index)
        self.psu_path = "/var/run/hw-management/"
        psu_oper_status = "thermal/psu{}_pwr_status".format(self.index)
        #psu_oper_status should always be present for all SKUs
        self.psu_oper_status = os.path.join(self.psu_path, psu_oper_status)
        self._name = "PSU {}".format(psu_index + 1)

        if platform in platform_dict_psu:
            filemap = psu_profile_list[platform_dict_psu[platform]]
        else:
            filemap = psu_profile_list[0]

        if platform in platform_dict_with_unplugable_psu:
            self.always_presence = True
            self.psu_voltage = None
            self.psu_current = None
            self.psu_power = None
            self.psu_presence = None
        else:
            self.always_presence = False
            psu_voltage = filemap[PSU_VOLTAGE].format(self.index)
            psu_voltage = os.path.join(self.psu_path, psu_voltage)
            self.psu_voltage = psu_voltage

            psu_current = filemap[PSU_CURRENT].format(self.index)
            psu_current = os.path.join(self.psu_path, psu_current)
            self.psu_current = psu_current

            psu_power = filemap[PSU_POWER].format(self.index)
            psu_power = os.path.join(self.psu_path, psu_power)
            self.psu_power = psu_power

            psu_presence = "thermal/psu{}_status".format(self.index)
            psu_presence = os.path.join(self.psu_path, psu_presence)
            self.psu_presence = psu_presence

        # unplugable PSU has no FAN
        if platform not in platform_dict_with_unplugable_psu:
            fan = Fan(False, psu_index, psu_index, True)
            self._fan_list.append(fan)

        self.psu_green_led_path = "led_psu_green"
        self.psu_red_led_path = "led_psu_red"
        self.psu_orange_led_path = "led_psu_orange"
        self.psu_led_cap_path = "led_psu_capability"


    def get_name(self):
        return self._name


    def _read_generic_file(self, filename, len):
        """
        Read a generic file, returns the contents of the file
        """
        result = 0
        try:
            if not os.path.exists(filename):
                return result
            with open(filename, 'r') as fileobj:
                result = int(fileobj.read().strip())
        except Exception as e:
            logger.log_info("Fail to read file {} due to {}".format(filename, repr(e)))
        return result

    def get_powergood_status(self):
        """
        Retrieves the operational status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is operating properly, False if not
        """
        status = self._read_generic_file(os.path.join(self.psu_path, self.psu_oper_status), 0)

        return status == 1

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is present, False if not
        """
        if self.always_presence:
            return self.always_presence
        else:
            status = self._read_generic_file(self.psu_presence, 0)
            return status == 1

    def get_voltage(self):
        """
        Retrieves current PSU voltage output

        Returns:
            A float number, the output voltage in volts, 
            e.g. 12.1 
        """
        if self.psu_voltage is not None and self.get_powergood_status():
            voltage = self._read_generic_file(self.psu_voltage, 0)
            return float(voltage) / 1000
        else:
            return None

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU

        Returns:
            A float number, the electric current in amperes, e.g 15.4
        """
        if self.psu_current is not None and self.get_powergood_status():
            amperes = self._read_generic_file(self.psu_current, 0)
            return float(amperes) / 1000
        else:
            return None

    def get_power(self):
        """
        Retrieves current energy supplied by PSU

        Returns:
            A float number, the power in watts, e.g. 302.6
        """
        if self.psu_power is not None and self.get_powergood_status():
            power = self._read_generic_file(self.psu_power, 0)
            return float(power) / 1000000
        else:
            return None


    def _get_led_capability(self):
        cap_list = None
        try:
            with open(os.path.join(Led.LED_PATH, self.psu_led_cap_path), 'r') as psu_led_cap:
                    caps = psu_led_cap.read()
                    cap_list = caps.split()
        except (ValueError, IOError):
            pass
        
        return cap_list


    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED

        Args:
            color: A string representing the color with which to set the
                   PSU status LED

        Returns:
            bool: True if status LED state is set successfully, False if not

        Notes:
            Only one led for all PSUs.
        """
        led_cap_list = self._get_led_capability()
        if led_cap_list is None:
            return False

        status = False
        try:
            if color == Led.STATUS_LED_COLOR_GREEN:
                with open(os.path.join(Led.LED_PATH, self.psu_green_led_path), 'w') as psu_led:
                    psu_led.write(Led.LED_ON)
                    status = True
            elif color == Led.STATUS_LED_COLOR_RED:
                # Some fan don't support red led but support orange led, in this case we set led to orange
                if Led.STATUS_LED_COLOR_RED in led_cap_list:
                    led_path = os.path.join(Led.LED_PATH, self.psu_red_led_path)
                elif Led.STATUS_LED_COLOR_ORANGE in led_cap_list:
                    led_path = os.path.join(Led.LED_PATH, self.psu_orange_led_path)
                else:
                    return False
                with open(led_path, 'w') as psu_led:
                    psu_led.write(Led.LED_ON)
                    status = True
            else:
                status = False
        except (ValueError, IOError):
            status = False

        return status


    def get_status_led(self):
        """
        Gets the state of the PSU status LED

        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        led_cap_list = self._get_led_capability()
        if led_cap_list is None:
            return Led.STATUS_LED_COLOR_OFF

        try:
            with open(os.path.join(Led.LED_PATH, self.psu_green_led_path), 'r') as psu_led:
                if Led.LED_OFF != psu_led.read().rstrip('\n'):
                    return Led.STATUS_LED_COLOR_GREEN
            if Led.STATUS_LED_COLOR_RED in led_cap_list:
                with open(os.path.join(Led.LED_PATH, self.psu_red_led_path), 'r') as psu_led:
                    if Led.LED_OFF != psu_led.read().rstrip('\n'):
                        return Led.STATUS_LED_COLOR_RED
            if Led.STATUS_LED_COLOR_ORANGE in led_cap_list:
                with open(os.path.join(Led.LED_PATH, self.psu_orange_led_path), 'r') as psu_led:
                    if Led.LED_OFF != psu_led.read().rstrip('\n'):
                        return Led.STATUS_LED_COLOR_RED
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to read led status for psu due to {}".format(repr(e)))

        return Led.STATUS_LED_COLOR_OFF


    def get_power_available_status(self):
        """
        Gets the power available status

        Returns:
            True if power is present and power on. 
            False and "absence of PSU" if power is not present.
            False and "absence of power" if power is present but not power on.
        """
        if not self.get_presence():
            return False, "absence of PSU"
        elif not self.get_powergood_status():
            return False, "absence of power"
        else:
            return True, ""

