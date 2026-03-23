#############################################################################
#
# Module contains an implementation of SONiC Platform Base API and
# provides access to fan CPLD watchdog
#
#############################################################################

try:
    from sonic_platform_base.watchdog_base import WatchdogBase
    from .helper import APIHelper
    from .thermal import logger
except ImportError as e:
    raise ImportError("%s - required module not found" % e)

WD_ERROR = -1
WD_ENABLE = 1
WD_DISABLE = 0
WD_MAX_PWM = 15 # Represent 100% PWM
WD_MAX_TIMEOUT_SEC = 255

class Watchdog(WatchdogBase):
    """
    Platform-specific watchdog class for interfacing with the fan CPLD watchdog
    """

    def __init__(self):
        self._api_helper = APIHelper()

    def _run_i2cset_cmd(self, bus, addr, reg, data):
        cmd = "i2cset -f -y {} {} {} {}".format(bus, addr, reg, data)
        sts, res = self._api_helper.run_command(cmd)
        if not (sts and res == ''):
            logger.log_error("Failed to run i2cset command: {}".format(cmd))
            return False
        return True

    def _run_i2cget_cmd(self, bus, addr, reg):
        cmd = "i2cget -f -y {} {} {}".format(bus, addr, reg)
        sts, res = self._api_helper.run_command(cmd)
        if not sts:
            logger.log_error("Failed to run i2cget command: {}".format(cmd))
            return None
        return res

    def arm(self, seconds):
        ret_sts = WD_ERROR
        if seconds <= 0:
            return ret_sts
        if seconds > WD_MAX_TIMEOUT_SEC:
            logger.log_error("Invalid timeout ({}), must be ≤{}. Timeout forced to {}.".format(
                seconds, WD_MAX_TIMEOUT_SEC, WD_MAX_TIMEOUT_SEC))
            seconds = WD_MAX_TIMEOUT_SEC
        sts1 = self._run_i2cset_cmd('10', '0x66', '0x32', f'0x{WD_MAX_PWM:02X}') # Set max PWM
        sts2 = self._run_i2cset_cmd('10', '0x66', '0x33', f'0x{WD_ENABLE:02X}') # Enable WD
        sts3 = self._run_i2cset_cmd('10', '0x66', '0x31', f'0x{seconds:02X}') # Set timeout
        if all([sts1, sts2, sts3]):
            ret_sts = seconds
        return ret_sts

    def disarm(self):
        self._run_i2cset_cmd('10', '0x66', '0x33', f'0x{WD_DISABLE:02X}') # Disable WD
        return True

    def is_armed(self):
        armed = False
        try:
            armed = int(self._run_i2cget_cmd('10', '0x66', '0x33'), 16) == WD_ENABLE
        except (ValueError, TypeError) as e:
            logger.log_error("Failed to check if watchdog is armed: {}".format(e))
        return armed

    def get_remaining_time(self):
        remaining_time = WD_ERROR
        if self.is_armed():
            try:
                remaining_time = int(self._run_i2cget_cmd('10', '0x66', '0x31'), 16)
            except (ValueError, TypeError) as e:
                logger.log_error("Failed to get remaining time: {}".format(e))
        return remaining_time
