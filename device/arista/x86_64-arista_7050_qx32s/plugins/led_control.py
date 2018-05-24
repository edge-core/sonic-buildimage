#!/usr/bin/env python
#
# led_control.py
# 
# Platform-specific LED control functionality for SONiC
#

try:
    from sonic_led.led_control_base import LedControlBase
except ImportError, e:
    raise ImportError (str(e) + " - required module not found")


class LedControl(LedControlBase):
    """Platform specific LED control class"""

    SONIC_PORT_NAME_PREFIX = "Ethernet"

    LED_SYSFS_PATH_BREAKOUT_CAPABLE = "/sys/class/leds/qsfp{0}_{1}/brightness"
    LED_SYSFS_PATH_NO_BREAKOUT = "/sys/class/leds/qsfp{0}/brightness"

    QSFP_BREAKOUT_START_IDX = 1
    QSFP_BREAKOUT_END_IDX = 24
    QSFP_NO_BREAKOUT_START_IDX = 25
    QSFP_NO_BREAKOUT_END_IDX = 32

    LED_QSFP_OFFSET = 4

    LED_COLOR_OFF = 0
    LED_COLOR_GREEN = 1
    LED_COLOR_YELLOW = 2

    # Helper method to map SONiC port name to Arista QSFP index
    def _port_name_to_qsfp_index(self, port_name):
        # Strip "Ethernet" off port name
        if not port_name.startswith(self.SONIC_PORT_NAME_PREFIX):
            return -1

        sonic_port_num = int(port_name[len(self.SONIC_PORT_NAME_PREFIX):])

        # SONiC port nums are 0-based and increment by 4
        # Arista QSFP indices are 1-based and increment by 1
        return ((sonic_port_num/4) + 1)

    # Concrete implementation of port_link_state_change() method
    def port_link_state_change(self, port, state):
        qsfp_index = self._port_name_to_qsfp_index(port)
        
        # Ignore invalid QSFP indices
        if qsfp_index <= 0:
            return

        # QSFP indices 1-24 are breakout-capable and have four LEDs, and each LED indicate one lane.
        # whereas indices 25-32 are not breakout-capable, and only have one
        if qsfp_index <= self.QSFP_BREAKOUT_END_IDX:
            # assuming 40G, then we need to control four lanes
            led_sysfs_paths = [ self.LED_SYSFS_PATH_BREAKOUT_CAPABLE.format(qsfp_index + self.LED_QSFP_OFFSET, i) for i in range(1, 5) ]
        else:
            led_sysfs_paths = [ self.LED_SYSFS_PATH_NO_BREAKOUT.format(qsfp_index + self.LED_QSFP_OFFSET) ]

        for led_sysfs_path in led_sysfs_paths:
            led_file = open(led_sysfs_path, "w")

            if state == "up":
                led_file.write("%d" % self.LED_COLOR_GREEN)
            else:
                led_file.write("%d" % self.LED_COLOR_OFF)

            led_file.close()

    # Constructor
    def __init__(self):
        # Initialize all front-panel status LEDs to green
        with open("/sys/class/leds/status/brightness", "w") as f:
            f.write("1")
        with open("/sys/class/leds/fan_status/brightness", "w") as f:
            f.write("1")
        with open("/sys/class/leds/psu1/brightness", "w") as f:
            f.write("1")
        with open("/sys/class/leds/psu2/brightness", "w") as f:
            f.write("1")

        # Initialize: Turn all front panel QSFP LEDs off
        for qsfp_index in range(self.QSFP_BREAKOUT_START_IDX, self.QSFP_BREAKOUT_END_IDX + 1):
            for lane in range(1, 5):
                led_sysfs_path = self.LED_SYSFS_PATH_BREAKOUT_CAPABLE.format(qsfp_index + self.LED_QSFP_OFFSET, lane)
                with open(led_sysfs_path, 'w') as led_file:
                    led_file.write("%d" % self.LED_COLOR_OFF)

        for qsfp_index in range(self.QSFP_NO_BREAKOUT_START_IDX, self.QSFP_NO_BREAKOUT_END_IDX + 1):
            led_sysfs_path = self.LED_SYSFS_PATH_NO_BREAKOUT.format(qsfp_index + self.LED_QSFP_OFFSET)
            with open(led_sysfs_path, 'w') as led_file:
                led_file.write("%d" % self.LED_COLOR_OFF)
