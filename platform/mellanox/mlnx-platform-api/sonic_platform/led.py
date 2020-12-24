class Led(object):
    LED_PATH = "/var/run/hw-management/led/"
    LED_ON = '1'
    LED_OFF = '0'
    LED_BLINK = '50'
    STATUS_LED_COLOR_GREEN = 'green'
    STATUS_LED_COLOR_GREEN_BLINK = 'green_blink'
    STATUS_LED_COLOR_RED = 'red'
    STATUS_LED_COLOR_RED_BLINK = 'red_blink'
    STATUS_LED_COLOR_ORANGE = 'orange'
    STATUS_LED_COLOR_ORANGE_BLINK = 'orange_blink'
    STATUS_LED_COLOR_OFF = 'off'


class SharedLed(object):
    LED_PRIORITY = {
        Led.STATUS_LED_COLOR_RED: 0,
        Led.STATUS_LED_COLOR_GREEN: 1
    }

    def __init__(self):
        self._virtual_leds = []
        self._target_color = Led.STATUS_LED_COLOR_GREEN

    def add_virtual_leds(self, led):
        self._virtual_leds.append(led)

    def update_status_led(self):
        target_color = Led.STATUS_LED_COLOR_GREEN
        for virtual_led in self._virtual_leds:
            try:
                if SharedLed.LED_PRIORITY[virtual_led.get_led_color()] < SharedLed.LED_PRIORITY[target_color]:
                    target_color = virtual_led.get_led_color()
            except KeyError:
                return False
        self._target_color = target_color
        return True

    def get_status(self):
        return self._target_color


class ComponentFaultyIndicator(object):
    def __init__(self, shared_led):
        self._color = Led.STATUS_LED_COLOR_GREEN
        self._shared_led = shared_led
        self._shared_led.add_virtual_leds(self)

    def set_status(self, color):
        current_color = self._color
        self._color = color
        if self._shared_led.update_status_led():
            return True
        else:
            self._color = current_color
            return False

    def get_led_color(self):
        return self._color

    def get_status(self):
        return self._shared_led.get_status()
