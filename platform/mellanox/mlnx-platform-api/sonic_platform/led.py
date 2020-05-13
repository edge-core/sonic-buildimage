import os


class Led(object):
    STATUS_LED_COLOR_GREEN = 'green'
    STATUS_LED_COLOR_RED = 'red'
    STATUS_LED_COLOR_ORANGE = 'orange'
    STATUS_LED_COLOR_OFF = 'off'

    LED_ON = '1'
    LED_OFF = '0'

    LED_PATH = "/var/run/hw-management/led/"

    def set_status(self, color):
        led_cap_list = self.get_capability()
        if led_cap_list is None:
            return False

        status = False
        try:
            if color == Led.STATUS_LED_COLOR_GREEN:
                with open(self.get_green_led_path(), 'w') as led:
                    led.write(Led.LED_ON)
                    status = True
            elif color == Led.STATUS_LED_COLOR_RED:
                # Some led don't support red led but support orange led, in this case we set led to orange
                if Led.STATUS_LED_COLOR_RED in led_cap_list:
                    led_path = self.get_red_led_path()
                elif Led.STATUS_LED_COLOR_ORANGE in led_cap_list:
                    led_path = self.get_orange_led_path()
                else:
                    return False

                with open(led_path, 'w') as led:
                    led.write(Led.LED_ON)
                    status = True
            elif color == Led.STATUS_LED_COLOR_OFF:
                if Led.STATUS_LED_COLOR_GREEN in led_cap_list:
                    with open(self.get_green_led_path(), 'w') as led:
                        led.write(Led.LED_OFF)
                if Led.STATUS_LED_COLOR_RED in led_cap_list:
                    with open(self.get_red_led_path(), 'w') as led:
                        led.write(Led.LED_OFF)
                if Led.STATUS_LED_COLOR_ORANGE in led_cap_list:
                    with open(self.get_orange_led_path(), 'w') as led:
                        led.write(Led.LED_OFF)

                status = True
            else:
                status = False
        except (ValueError, IOError):
            status = False

        return status

    def get_status(self):
        led_cap_list = self.get_capability()
        if led_cap_list is None:
            return Led.STATUS_LED_COLOR_OFF

        try:
            with open(self.get_green_led_path(), 'r') as led:
                if Led.LED_OFF != led.read().rstrip('\n'):
                    return Led.STATUS_LED_COLOR_GREEN

            if Led.STATUS_LED_COLOR_RED in led_cap_list:
                with open(self.get_red_led_path(), 'r') as led:
                    if Led.LED_OFF != led.read().rstrip('\n'):
                        return Led.STATUS_LED_COLOR_RED
            if Led.STATUS_LED_COLOR_ORANGE in led_cap_list:
                with open(self.get_orange_led_path(), 'r') as led:
                    if Led.LED_OFF != led.read().rstrip('\n'):
                        return Led.STATUS_LED_COLOR_RED
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to read led status due to {}".format(repr(e)))

        return Led.STATUS_LED_COLOR_OFF

    def get_capability(self):
        cap_list = None
        try:
            with open(self.get_led_cap_path(), 'r') as led_cap:
                caps = led_cap.read()
                cap_list = caps.split()
        except (ValueError, IOError):
            pass
        
        return cap_list

    def get_green_led_path(self):
        pass

    def get_red_led_path(self):
        pass

    def get_orange_led_path(self):
        pass

    def get_led_cap_path(self):
        pass

 
class FanLed(Led):
    LED_PATH = "/var/run/hw-management/led/"

    def __init__(self, index):
        if index is not None:
            self._green_led_path = os.path.join(Led.LED_PATH, "led_fan{}_green".format(index))
            self._red_led_path = os.path.join(Led.LED_PATH, "led_fan{}_red".format(index))
            self._orange_led_path = os.path.join(Led.LED_PATH, "led_fan{}_orange".format(index))
            self._led_cap_path = os.path.join(Led.LED_PATH, "led_fan{}_capability".format(index))
        else:
            self._green_led_path = os.path.join(Led.LED_PATH, "led_fan_green")
            self._red_led_path = os.path.join(Led.LED_PATH, "led_fan_red")
            self._orange_led_path = os.path.join(Led.LED_PATH, "led_fan_orange")
            self._led_cap_path = os.path.join(Led.LED_PATH, "led_fan_capability")

        self.set_status(Led.STATUS_LED_COLOR_GREEN)

    def get_green_led_path(self):
        return self._green_led_path

    def get_red_led_path(self):
        return self._red_led_path

    def get_orange_led_path(self):
        return self._orange_led_path

    def get_led_cap_path(self):
        return self._led_cap_path


class PsuLed(Led):
    def __init__(self, index):
        if index is not None:
            self._green_led_path = os.path.join(Led.LED_PATH, "led_psu{}_green".format(index))
            self._red_led_path = os.path.join(Led.LED_PATH, "led_psu{}_red".format(index))
            self._orange_led_path = os.path.join(Led.LED_PATH, "led_psu{}_orange".format(index))
            self._led_cap_path = os.path.join(Led.LED_PATH, "led_psu{}_capability".format(index))
        else:
            self._green_led_path = os.path.join(Led.LED_PATH, "led_psu_green")
            self._red_led_path = os.path.join(Led.LED_PATH, "led_psu_red")
            self._orange_led_path = os.path.join(Led.LED_PATH, "led_psu_orange")
            self._led_cap_path = os.path.join(Led.LED_PATH, "led_psu_capability")
            
        self.set_status(Led.STATUS_LED_COLOR_GREEN)

    def get_green_led_path(self):
        return self._green_led_path

    def get_red_led_path(self):
        return self._red_led_path

    def get_orange_led_path(self):
        return self._orange_led_path

    def get_led_cap_path(self):
        return self._led_cap_path


class SharedLed(object):
    LED_PRIORITY = {
        Led.STATUS_LED_COLOR_RED: 0,
        Led.STATUS_LED_COLOR_GREEN: 1
    }

    def __init__(self, led):
        self._led = led
        self._virtual_leds = []

    def add_virtual_leds(self, led):
        self._virtual_leds.append(led)

    def update_status_led(self):
        target_color = Led.STATUS_LED_COLOR_GREEN
        for virtual_led in self._virtual_leds:
            if SharedLed.LED_PRIORITY[virtual_led.get_led_color()] < SharedLed.LED_PRIORITY[target_color]:
                target_color = virtual_led.get_led_color()

        return self._led.set_status(target_color)

    def get_status(self):
        return self._led.get_status()


class ComponentFaultyIndicator(object):
    def __init__(self, shared_led):
        self._color = Led.STATUS_LED_COLOR_GREEN
        self._shared_led = shared_led
        self._shared_led.add_virtual_leds(self)

    def set_status(self, color):
        self._color = color
        return self._shared_led.update_status_led()

    def get_led_color(self):
        return self._color

    def get_status(self):
        return self._shared_led.get_status()
