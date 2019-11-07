#!/usr/bin/env python

########################################################################
#
# DELLEMC S6100
#
# Abstract base class for implementing a platform-specific class with
# which to interact with a hardware watchdog module in SONiC
#
########################################################################

try:
    import os
    import struct
    import ctypes
    from sonic_platform_base.watchdog_base import WatchdogBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class _timespec(ctypes.Structure):
    _fields_ = [
            ('tv_sec', ctypes.c_long),
            ('tv_nsec', ctypes.c_long)
    ]

class Watchdog(WatchdogBase):
    """
    Abstract base class for interfacing with a hardware watchdog module
    """

    io_resource = '/dev/port'

    WD_STATUS_OFFSET = 0x207
    WD_TIMER_OFFSET = 0x206
    WD_ENABLE = 0
    WD_DISABLE = 1

    armed_time = 0
    timeout = 0
    CLOCK_MONOTONIC = 1

    def __init__(self):
        self._librt = ctypes.CDLL('librt.so.1', use_errno=True)
        self._clock_gettime = self._librt.clock_gettime
        self._clock_gettime.argtypes=[ctypes.c_int, ctypes.POINTER(_timespec)]

    def _io_reg_read(self, offset):
        """
        Read the resource file
        """
        fd = os.open(self.io_resource, os.O_RDONLY)
        if fd < 0:
            return -1

        if os.lseek(fd, offset, os.SEEK_SET) != offset:
            os.close(fd)
            return -1

        buf = os.read(fd, 1)
        reg_value = ord(buf)

        os.close(fd)
        return reg_value

    def _io_reg_write(self, offset, val):
        """
        Write in the resource file
        """
        fd = os.open(self.io_resource, os.O_RDWR)
        if fd < 0:
            return -1

        if os.lseek(fd, offset, os.SEEK_SET) != offset:
            os.close(fd)
            return -1

        ret = os.write(fd, struct.pack('B', val))
        if ret != 1:
            os.close(fd)
            return -1

        os.close(fd)
        return ret

    def _read_gpio_file(self, file_path):
        """
        Read the GPIO values
        """
        fd = os.open(file_path, os.O_RDONLY)
        read_str = os.read(fd, os.path.getsize(file_path))
        gpio_val = int(read_str, 16)
        os.close(fd)
        return gpio_val

    def _write_gpio_file(self, file_path, val):
        """
        Write the GPIO values
        """
        fd = os.open(file_path, os.O_RDWR)
        ret = os.write(fd, val)
        if ret < 0:
            os.close(fd)
            return -1

        os.close(fd)
        return 1

    def _get_time(self):
        """
        To get clock monotonic time
        """
        ts = _timespec()
        if self._clock_gettime(self.CLOCK_MONOTONIC, ctypes.pointer(ts)) != 0:
            errno_ = ctypes.get_errno()
            return 0
        return ts.tv_sec + ts.tv_nsec * 1e-9

    def arm(self, seconds):
        """
        Arm the hardware watchdog with a timeout of <seconds> seconds.
        If the watchdog is currently armed, calling this function will
        simply reset the timer to the provided value. If the underlying
        hardware does not support the value provided in <seconds>, this
        method should arm the watchdog with the *next greater*
        available value.

        Returns:
            An integer specifying the *actual* number of seconds the
            watchdog was armed with. On failure returns -1.
        """
        gpio = "/sys/devices/platform/dell_ich.0/sc_gp_lvl"
        timer_offset = -1
        if seconds <= 30:
            timer_offset = 1
            seconds = 30
        elif seconds > 30 and seconds <= 60:
            timer_offset = 2
            seconds = 60
        elif seconds > 60 and seconds <= 180:
            timer_offset = 3
            seconds = 180

        if timer_offset == -1:
            return -1
        if self._io_reg_read(self.WD_TIMER_OFFSET) != timer_offset:
            if self._io_reg_write(self.WD_TIMER_OFFSET, timer_offset) == -1:
                return -1
            self.disarm()

        if self.is_armed():
            gpio_val = self._read_gpio_file(gpio)
            high_val = gpio_val | (1 << 15)
            if self._write_gpio_file(gpio, hex(high_val)) != -1:
                low_val = high_val & 0xFFFF7FFF
                if self._write_gpio_file(gpio, hex(low_val)) != -1:
                    self.armed_time = self._get_time()
                    self.timeout = seconds
                    return seconds
        elif self._io_reg_write(self.WD_STATUS_OFFSET, self.WD_ENABLE) != -1:
            self.armed_time = self._get_time()
            self.timeout = seconds
            return seconds

        return -1

    def disarm(self):
        """
        Disarm the hardware watchdog

        Returns:
            A boolean, True if watchdog is disarmed successfully, False
            if not
        """
        if self._io_reg_write(self.WD_STATUS_OFFSET, self.WD_DISABLE) != -1:
            self.armed_time = 0
            self.timeout = 0
            return True

        return False

    def is_armed(self):
        """
        Retrieves the armed state of the hardware watchdog.

        Returns:
            A boolean, True if watchdog is armed, False if not
        """
        wd_status = self.WD_DISABLE
        wd_status = self._io_reg_read(self.WD_STATUS_OFFSET)
        if wd_status == self.WD_ENABLE:
            return True

        return False

    def get_remaining_time(self):
        """
        If the watchdog is armed, retrieve the number of seconds
        remaining on the watchdog timer

        Returns:
            An integer specifying the number of seconds remaining on
            their watchdog timer. If the watchdog is not armed, returns
            -1.

            S6100 doesnot have hardware support to show remaining time.
            Due to this limitation, this API is implemented in software.
            This API would return correct software time difference if it
            is called from the process which armed the watchdog timer.
            If this API called from any other process, it would return
            0. If the watchdog is not armed, this API would return -1.
        """
        if not self.is_armed():
            return -1

        if self.armed_time > 0 and self.timeout != 0:
            cur_time = self._get_time()
            if cur_time <= 0:
                return 0
            diff_time = int(cur_time - self.armed_time)
            if diff_time > self.timeout:
                return self.timeout
            else:
                return self.timeout - diff_time

        return 0

