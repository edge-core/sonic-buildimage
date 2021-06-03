#############################################################################
# PDDF
# Module contains an implementation of SONiC Chassis API
#
#############################################################################

try:
    import time
    import subprocess
    from sonic_platform_pddf_base.pddf_chassis import PddfChassis
    from rgutil.logutil import Logger
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PORT_START = 0
PORT_END = 55
PORTS_IN_BLOCK = 56

logger = Logger("CHASSIS", syslog=True)

class Chassis(PddfChassis):
    """
    PDDF Platform-specific Chassis class
    """

    SFP_STATUS_INSERTED = "1"
    SFP_STATUS_REMOVED = "0"
    port_dict = {}

    def __init__(self, pddf_data=None, pddf_plugin_data=None):
        PddfChassis.__init__(self, pddf_data, pddf_plugin_data)

        self.enable_read = "i2cset -f -y 2 0x35 0x2a 0x01"
        self.disable_read = "i2cset -f -y 2 0x35 0x2a 0x00"
        self.enable_write = "i2cset -f -y 2 0x35 0x2b 0x00"
        self.disable_write = "i2cset -f -y 2 0x35 0x2b 0x01"
        self.enable_erase = "i2cset -f -y 2 0x35 0x2c 0x01"
        self.disable_erase = "i2cset -f -y 2 0x35 0x2c 0x00"
        self.read_value = "i2cget -f -y 2 0x35 0x25"
        self.write_value = "i2cset -f -y 2 0x35 0x21 0x0a"

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        Returns:
            A tuple (string, string) where the first element is a string
            containing the cause of the previous reboot. This string must be
            one of the predefined strings in this class. If the first string
            is "REBOOT_CAUSE_HARDWARE_OTHER", the second string can be used
            to pass a description of the reboot cause.
        """
        try:
            is_power_loss = False
            # enable read
            subprocess.getstatusoutput(self.disable_write)
            subprocess.getstatusoutput(self.enable_read)
            ret, log = subprocess.getstatusoutput(self.read_value)
            if ret == 0 and "0x0a" in log:
                is_power_loss = True

            # erase i2c and e2
            subprocess.getstatusoutput(self.enable_erase)
            time.sleep(1)
            subprocess.getstatusoutput(self.disable_erase)
            # clear data
            subprocess.getstatusoutput(self.enable_write)
            subprocess.getstatusoutput(self.disable_read)
            subprocess.getstatusoutput(self.disable_write)
            subprocess.getstatusoutput(self.enable_read)
            # enable write and set data
            subprocess.getstatusoutput(self.enable_write)
            subprocess.getstatusoutput(self.disable_read)
            subprocess.getstatusoutput(self.write_value)
            if is_power_loss:
                return(self.REBOOT_CAUSE_POWER_LOSS, None)
        except Exception as e:
            logger.error(str(e))

        return (self.REBOOT_CAUSE_NON_HARDWARE, None)

    def get_change_event(self, timeout=0):
        change_event_dict = {"fan": {}, "sfp": {}}
        sfp_status, sfp_change_dict = self.get_transceiver_change_event(timeout)
        change_event_dict["sfp"] = sfp_change_dict
        if sfp_status is True:
            return True, change_event_dict

        return False, {}

    def get_transceiver_change_event(self, timeout=0):
        start_time = time.time()
        currernt_port_dict = {}
        forever = False

        if timeout == 0:
            forever = True
        elif timeout > 0:
            timeout = timeout / float(1000)  # Convert to secs
        else:
            print("get_transceiver_change_event:Invalid timeout value", timeout)
            return False, {}

        end_time = start_time + timeout
        if start_time > end_time:
            print(
                "get_transceiver_change_event:" "time wrap / invalid timeout value",
                timeout,
            )
            return False, {}  # Time wrap or possibly incorrect timeout

        while timeout >= 0:
            # Check for OIR events and return updated port_dict
            for index in range(PORT_START, PORTS_IN_BLOCK):
                if self._sfp_list[index].get_presence():
                    currernt_port_dict[index] = self.SFP_STATUS_INSERTED
                else:
                    currernt_port_dict[index] = self.SFP_STATUS_REMOVED
            if currernt_port_dict == self.port_dict:
                if forever:
                    time.sleep(1)
                else:
                    timeout = end_time - time.time()
                    if timeout >= 1:
                        time.sleep(1)  # We poll at 1 second granularity
                    else:
                        if timeout > 0:
                            time.sleep(timeout)
                        return True, {}
            else:
                # Update reg value
                self.port_dict = currernt_port_dict
                print(self.port_dict)
                return True, self.port_dict
        print("get_transceiver_change_event: Should not reach here.")
        return False, {}
