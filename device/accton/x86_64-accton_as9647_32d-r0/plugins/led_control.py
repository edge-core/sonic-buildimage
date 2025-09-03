#!/usr/bin/env python
#
# led_control.py
#
# Platform-specific LED control functionality for SONiC
#

try:
    from sonic_led.led_control_base import LedControlBase
    import sonic_platform.chassis
    import syslog
    import time
    from select import *
except ImportError as e:
    raise ImportError(str(e) + " - required module not found")

is_fan_all_OK = False
is_power_all_OK = False
is_thermal_high = False
is_thermal_crit_high = False

def logprint(str):
    syslog.openlog("ledctrl")
    syslog.syslog(syslog.LOG_INFO, str)
    syslog.closelog()

def system_led_check():
    global is_fan_all_OK, is_power_all_OK, is_thermal_high, is_thermal_crit_high
    is_fan_all_OK = True
    is_power_all_OK = True
    is_thermal_high = False
    is_thermal_crit_high = False

    for fan in sonic_platform.chassis.Chassis().get_all_fans():
        if fan.is_under_speed() or fan.is_over_speed():
            is_fan_all_OK = False

    for psu in sonic_platform.chassis.Chassis().get_all_psus():
        if not True == psu.get_status():
            is_power_all_OK = False

    for thermal in sonic_platform.chassis.Chassis().get_all_thermals():
        temperature = thermal.get_temperature()
        high_threshold = thermal.get_high_threshold()
        if temperature is not None and high_threshold is not None:
            if temperature > high_threshold:
                is_thermal_high = True

        # Duplicated logic from thermal policy condition `thermal.over.high_critical_threshold`
        if thermal.get_name() not in ["ASIC  average", "ASIC  maximum"]:
            high_critical_threshold = thermal.get_high_critical_threshold()
            if temperature is not None and high_critical_threshold is not None:
                if temperature > high_critical_threshold:
                    is_thermal_crit_high = True

    if is_fan_all_OK and is_power_all_OK and not is_thermal_high and not is_thermal_crit_high:
        sonic_platform.chassis.Chassis().set_status_led("STATUS_LED_COLOR_GREEN")
    else:
        sonic_platform.chassis.Chassis().set_status_led("STATUS_LED_COLOR_AMBER")

    print(sonic_platform.chassis.Chassis().get_status_led())
    return



def sysled_task():
    while True:
        system_led_check()
        time.sleep(5)

class LedControl(LedControlBase):
    """Platform specific LED control class"""

    # Concrete implementation of port_link_state_change() method
    def port_link_state_change(self, portname, state):
        logprint("port_link_state_change: {} = {}".format(portname, state))

    # Constructor
    def __init__(self):
        logprint("Start init LED")
        sonic_platform.chassis.Chassis().set_status_led("STATUS_LED_COLOR_GREEN")
        self.sysled = sonic_platform.chassis.Chassis().get_status_led()
        logprint("System LED state: {}".format(str(self.sysled)))
        logprint("Init LED done")
        sysled_task()
