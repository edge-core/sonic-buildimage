import os


class Led(object):
    STATUS_LED_COLOR_GREEN = 'green'
    STATUS_LED_COLOR_GREEN_BLINK = 'green_blink'
    STATUS_LED_COLOR_RED = 'red'
    STATUS_LED_COLOR_RED_BLINK = 'red_blink'
    STATUS_LED_COLOR_ORANGE = 'orange'
    STATUS_LED_COLOR_ORANGE_BLINK = 'orange_blink'
    STATUS_LED_COLOR_OFF = 'off'

    LED_ON = '1'
    LED_OFF = '0'
    LED_BLINK = '50'

    LED_PATH = "/var/run/hw-management/led/"

    def set_status(self, color):
        led_cap_list = self.get_capability()
        if led_cap_list is None:
            return False

        status = False
        try:
            self._stop_blink(led_cap_list)
            blink_pos = color.find('blink')
            if blink_pos != -1:
                return self._set_status_blink(color, blink_pos, led_cap_list)

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

    def _set_status_blink(self, color, blink_pos, led_cap_list):
        if color not in led_cap_list:
            if color == Led.STATUS_LED_COLOR_RED_BLINK and Led.STATUS_LED_COLOR_ORANGE_BLINK in led_cap_list:
                color = Led.STATUS_LED_COLOR_ORANGE_BLINK
            elif color == Led.STATUS_LED_COLOR_ORANGE_BLINK and Led.STATUS_LED_COLOR_RED_BLINK in led_cap_list:
                color = Led.STATUS_LED_COLOR_RED_BLINK
            else:
                return False

        if Led.STATUS_LED_COLOR_GREEN_BLINK == color:
            self._set_led_blink_status(self.get_green_led_delay_on_path(), self.get_green_led_delay_off_path(), Led.LED_BLINK)
        elif Led.STATUS_LED_COLOR_RED_BLINK == color:
            self._set_led_blink_status(self.get_red_led_delay_on_path(), self.get_red_led_delay_off_path(), Led.LED_BLINK)
        elif Led.STATUS_LED_COLOR_ORANGE_BLINK == color:
            self._set_led_blink_status(self.get_orange_led_delay_on_path(), self.get_orange_led_delay_off_path(), Led.LED_BLINK)
        else:
            return False

        return True

    def _stop_blink(self, led_cap_list):
        try:
            if Led.STATUS_LED_COLOR_GREEN_BLINK in led_cap_list:
                self._set_led_blink_status(self.get_green_led_delay_on_path(), self.get_green_led_delay_off_path(), Led.LED_OFF)
            if Led.STATUS_LED_COLOR_RED_BLINK in led_cap_list:
                self._set_led_blink_status(self.get_red_led_delay_on_path(), self.get_red_led_delay_off_path(), Led.LED_OFF)
            if Led.STATUS_LED_COLOR_ORANGE_BLINK in led_cap_list:
                self._set_led_blink_status(self.get_orange_led_delay_on_path(), self.get_orange_led_delay_off_path(), Led.LED_OFF)
        except Exception as e:
            return

    def _set_led_blink_status(self, delay_on_file, delay_off_file, value):
        with open(delay_on_file, 'w') as led:
            led.write(value)
        with open(delay_off_file, 'w') as led:
            led.write(value)

    def get_status(self):
        led_cap_list = self.get_capability()
        if led_cap_list is None:
            return Led.STATUS_LED_COLOR_OFF

        try:
            blink_status = self._get_blink_status(led_cap_list)
            if blink_status is not None:
                return blink_status

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

    def _get_blink_status(self, led_cap_list):
        try:
            if Led.STATUS_LED_COLOR_GREEN_BLINK in led_cap_list:
                if self._is_led_blinking(self.get_green_led_delay_on_path(), self.get_green_led_delay_off_path()):
                    return Led.STATUS_LED_COLOR_GREEN_BLINK
            if Led.STATUS_LED_COLOR_RED_BLINK in led_cap_list:
                if self._is_led_blinking(self.get_red_led_delay_on_path(), self.get_red_led_delay_off_path()):
                    return Led.STATUS_LED_COLOR_RED_BLINK
            if Led.STATUS_LED_COLOR_ORANGE_BLINK in led_cap_list:
                if self._is_led_blinking(self.get_orange_led_delay_on_path(), self.get_orange_led_delay_off_path()):
                    return Led.STATUS_LED_COLOR_ORANGE_BLINK
        except Exception as e:
            return None

        return None

    def _is_led_blinking(self, delay_on_file, delay_off_file):
        with open(delay_on_file, 'r') as led:
            delay_on = led.read().rstrip('\n')
        with open(delay_off_file, 'r') as led:
            delay_off = led.read().rstrip('\n')
        return delay_on != Led.LED_OFF and delay_off != Led.LED_OFF

    def get_capability(self):
        cap_list = None
        try:
            with open(self.get_led_cap_path(), 'r') as led_cap:
                caps = led_cap.read()
                cap_list = set(caps.split())
        except (ValueError, IOError):
            pass
        
        return cap_list

    def get_green_led_path(self):
        pass

    def get_green_led_delay_off_path(self):
        return '{}_delay_off'.format(self.get_green_led_path())

    def get_green_led_delay_on_path(self):
        return '{}_delay_on'.format(self.get_green_led_path())

    def get_red_led_path(self):
        pass

    def get_red_led_delay_off_path(self):
        return '{}_delay_off'.format(self.get_red_led_path())

    def get_red_led_delay_on_path(self):
        return '{}_delay_on'.format(self.get_red_led_path())

    def get_orange_led_path(self):
        pass

    def get_orange_led_delay_off_path(self):
        return '{}_delay_off'.format(self.get_orange_led_path())

    def get_orange_led_delay_on_path(self):
        return '{}_delay_on'.format(self.get_orange_led_path())

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


class SystemLed(Led):
    def __init__(self):
        self._green_led_path = os.path.join(Led.LED_PATH, "led_status_green")
        self._red_led_path = os.path.join(Led.LED_PATH, "led_status_red")
        self._orange_led_path = os.path.join(Led.LED_PATH, "led_status_orange")
        self._led_cap_path = os.path.join(Led.LED_PATH, "led_status_capability")

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
