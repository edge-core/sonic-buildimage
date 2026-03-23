
#!/usr/bin/env python
#
# led_control.py
#
# Platform-specific LED control functionality for SONiC
#
​
try:
    from sonic_led.led_control_base import LedControlBase
except ImportError as e:
    raise ImportError(str(e) + " - required module not found")
​
class LedControl(LedControlBase):
    """Platform specific LED control class"""
​
    def __init__(self):
        pass
​
    def port_link_state_change(self, portname, state):
        pass
