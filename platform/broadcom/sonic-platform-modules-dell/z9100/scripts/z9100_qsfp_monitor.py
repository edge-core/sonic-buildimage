import os
import re
import signal
import subprocess
import sys
import imp
import syslog
import time
import os.path
import z9100_preemp_db
from sonic_sfp.bcmshell import bcmshell

SYSLOG_IDENTIFIER = "dell_qsfp_monitor"

HWSKU_KEY = 'DEVICE_METADATA.localhost.hwsku'
PLATFORM_KEY = 'DEVICE_METADATA.localhost.platform'
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
PLATFORM_SPECIFIC_CLASS_NAME = "SfpUtil"
PLATFORM_SPECIFIC_MODULE_NAME = "sfputil"

# Global platform-specific sfputil class instance
platform_sfputil = None

# Timer Value
DEFAULT_WAIT_FOR_SWSS_SYNCD = 45
MINIMUM_WAIT_FOR_BCM_SHELL = 3
MINIMUM_WAIT_FOR_SWSS_SYNCD = 5
MINIMUM_RETRY_FOR_SWSS_DB = 10


# ========================== Syslog wrappers ==========================
def log_debug(msg):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_DEBUG, msg)
    syslog.closelog()


def log_info(msg):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_INFO, msg)
    syslog.closelog()


def log_warning(msg):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_WARNING, msg)
    syslog.closelog()


def log_error(msg):
    syslog.openlog(SYSLOG_IDENTIFIER)
    syslog.syslog(syslog.LOG_ERR, msg)
    syslog.closelog()


# ========================== Signal Handling ==========================
def signal_handler(sig, frame):
    if sig == signal.SIGHUP:
        log_info("Caught SIGHUP - ignoring...")
        return
    elif sig == signal.SIGINT:
        log_info("Caught SIGINT - exiting...")
        sys.exit(128 + sig)
    elif sig == signal.SIGTERM:
        log_info("Caught SIGTERM - exiting...")
        sys.exit(128 + sig)
    else:
        log_warning("Caught unhandled signal '" + sig + "'")


class BcmShell(bcmshell):
    bcm_port_mapping = {}

    def port_mapping_populate(self):
        try:
            content = self.run("ps")
            count = 0
            for line in content.split("\n"):
                PSOutput = re.search(r"(?P<port_name>(xe|ce)\d+)"
                                     "\(\s*(?P<bcm_id>\d+)\).+\s+"
                                     "(?P<speed>\d+)G", line)
                if PSOutput is not None:
                    port = "Ethernet" + str(count)
                    self.bcm_port_mapping[port] = list()
                    self.bcm_port_mapping[port].append(
                            int(PSOutput.group("bcm_id")))
                    self.bcm_port_mapping[port].append(
                            PSOutput.group("port_name"))
                    speed = PSOutput.group("speed")
                    if ((speed == "100") or (speed == "40")):
                        lane_count = 4
                        count = count + 4
                    elif (speed == "50"):
                        lane_count = 2
                        count = count + 2
                    else:
                        lane_count = 1
                        count = count + 1
                    self.bcm_port_mapping[port].append(str(lane_count))
                    self.bcm_port_mapping[port].append(speed)
                    if (speed == "10"):
                        del self.bcm_port_mapping[port]
        except:
            log_error("Unable to read bcm port status")
            sys.exit(3)

    def execute_command(self, cmd):
        self.cmd(cmd)


class dell_qsfp_monitor(object):
    """
    Class which configures the preEmphasis Settings corresponding to
    optics inserted. This script will run only once after reload.
    Support Insertion/Removal of optics is not provided
    Attributes:
    """

    # Instantiate BCM Shell
    def __init__(self):
        self.bcm_shell = BcmShell()
        self.bcm_shell.port_mapping_populate()

    # For the given eeprom data, return the PreEmphasisDB to be used
    def get_preemphasis_db(self, port, eeprom_dict):
        preemphasis_db = {}

        if (eeprom_dict == {}):
            return z9100_preemp_db.preEmphasis_100g
        else:
            qsfp_identifier = eeprom_dict["Identifier"]
            cable_length = eeprom_dict["Length Cable Assembly(m)"]

        if (qsfp_identifier == "QSFP28"):
            if (cable_length == 0.75):
                preemphasis_db = z9100_preemp_db.preEmphasis_100g_dac_750mm
            elif (cable_length == 1):
                preemphasis_db = z9100_preemp_db.preEmphasis_100g_dac_1_0m
            elif (cable_length == 1.5):
                preemphasis_db = z9100_preemp_db.preEmphasis_100g_dac_1_5m
            elif (cable_length == 2):
                preemphasis_db = z9100_preemp_db.preEmphasis_100g_dac_2_0m
            elif (cable_length == 3):
                preemphasis_db = z9100_preemp_db.preEmphasis_100g_dac_3_0m
        elif (qsfp_identifier == "QSFP+"):
            preemphasis_db = z9100_preemp_db.preEmphasis_40g

        return preemphasis_db

    # For Given Port, Lane and PreEmp Register, retrive the value from
    # PreEmphasisDB which needs to be programmed into ASIC,
    # In case of Fanned-out ports, use the values from base port
    def get_preemphasis_value(self, port, bcm_hw_lane,
                              preemphasis_dict, preemp_idx):
        portIdStr = re.findall('\d+', port)
        portId = int(portIdStr[0])
        basePortId = (portId//4)*4
        portIndex = "Ethernet" + str(basePortId)
        value = preemphasis_dict[portIndex][bcm_hw_lane][preemp_idx]

        return value

    # For Given port, return bcmPortname (Ex:- ce21, xe4, ce0 )
    def get_bcm_port_name(self, port):
        if (self.bcm_shell.bcm_port_mapping == {}):
            log_error("bcm port mapping is null")
            sys.exit(3)
        bcm_port_name = self.bcm_shell.bcm_port_mapping[port][1]

        return bcm_port_name

    # Return the number of lanes for the port
    # (Ex:- 100G - 4, 50G - 2, 40G - 4)
    def get_lane_count(self, port):
        if (self.bcm_shell.bcm_port_mapping == {}):
            log_error("bcm port mapping is null")
            sys.exit(3)
        laneCntStr = self.bcm_shell.bcm_port_mapping[port][2]
        lane_count = int(laneCntStr)

        return lane_count

    # For Given port, return bcmPortname (Ex:- ce21, xe4, ce0 )
    def get_bcm_port_speed(self, port):
        if (self.bcm_shell.bcm_port_mapping == {}):
            log_error("bcm port mapping is null")
            sys.exit(3)
        bcm_port_speed = self.bcm_shell.bcm_port_mapping[port][3]

        return bcm_port_speed

    # For Given, Port and lane_id, return the hardware lane number
    def get_bcm_lane_info(self, port, lane_id):
        lane_count = self.get_lane_count(port)
        portIdStr = re.findall('\d+', port)
        portId = int(portIdStr[0])
        basePortId = (portId//4)*4
        portIndex = "Ethernet" + str(basePortId)
        if ((portId % 4) == 0):
            laneIndex = lane_id
        elif ((portId % 2) == 0):
            if (lane_count == 2):
                laneIndex = lane_id + 2
            else:
                laneIndex = (PortId - basePortId)
        else:
            laneIndex = (PortId - basePortId)

        return z9100_preemp_db.lane_mapping[portIndex][laneIndex]

    # Form the AMS_TX_AMP_CTL command string
    # "serdes_driver_current" config variable in BCM Chipset
    def form_bcm_phy_ams_cmd(self, port, preemphasis_dict):
        ams_idx = 0
        ams_cmd = list()

        bcm_port_name = self.get_bcm_port_name(port)
        lane_count = self.get_lane_count(port)
        for lane_id in range(lane_count):
            bcm_hw_lane = self.get_bcm_lane_info(port, lane_id)
            value = self.get_preemphasis_value(port, bcm_hw_lane,
                                               preemphasis_dict, ams_idx)
            ams_cmd_str = "phy " + bcm_port_name + " AMS_TX_CTL2r." + str(
                          bcm_hw_lane) + " AMS_TX_AMP_CTL" + "=" + hex(value)
            ams_cmd.append(ams_cmd_str)

        return ams_cmd

    # Form the TXFIR_POST command string
    # "serdes_preemphasis" Bits 23:16 config variable in BCM Chipset
    def form_bcm_phy_txfir_post_cmd(self, port, preemphasis_dict):
        txfir_post_idx = 1
        txfir_post_cmd = list()

        bcm_port_name = self.get_bcm_port_name(port)
        lane_count = self.get_lane_count(port)
        for lane_id in range(lane_count):
            bcm_hw_lane = self.get_bcm_lane_info(port, lane_id)
            value = self.get_preemphasis_value(port, bcm_hw_lane,
                                               preemphasis_dict,
                                               txfir_post_idx)
            txfir_post_str_p1 = "phy " + bcm_port_name + " CL93N72_UT_CTL2r."
            txfir_post_str_p2 = txfir_post_str_p1 + str(bcm_hw_lane)
            txfir_post_str_p3 = txfir_post_str_p2 + " CL93N72_TXFIR_POST"
            txfir_post_cmd_str = txfir_post_str_p3 + "=" + hex(value)
            txfir_post_cmd.append(txfir_post_cmd_str)

        return txfir_post_cmd

    # Form the TXFIR_MAIN command string
    # "serdes_preemphasis" Bits 15:8 config variable in BCM Chipset
    def form_bcm_phy_txfir_main_cmd(self, port, preemphasis_dict):
        txfir_main_idx = 2
        txfir_main_cmd = list()

        bcm_port_name = self.get_bcm_port_name(port)
        lane_count = self.get_lane_count(port)
        for lane_id in range(lane_count):
            bcm_hw_lane = self.get_bcm_lane_info(port, lane_id)
            value = self.get_preemphasis_value(port, bcm_hw_lane,
                                               preemphasis_dict,
                                               txfir_main_idx)
            txfir_main_str_p1 = "phy " + bcm_port_name + " CL93N72_UT_CTL3r."
            txfir_main_str_p2 = txfir_main_str_p1 + str(bcm_hw_lane)
            txfir_main_str_p3 = txfir_main_str_p2 + " CL93N72_TXFIR_MAIN"
            txfir_main_cmd_str = txfir_main_str_p3 + "=" + hex(value)
            txfir_main_cmd.append(txfir_main_cmd_str)

        return txfir_main_cmd

    # Form the TXFIR_PRE command string
    # "serdes_preemphasis" Bits 7:0 config variable in BCM Chipset
    def form_bcm_phy_txfir_pre_cmd(self, port, preemphasis_dict):
        txfir_pre_idx = 3
        txfir_pre_cmd = list()

        bcm_port_name = self.get_bcm_port_name(port)
        lane_count = self.get_lane_count(port)
        for lane_id in range(lane_count):
            bcm_hw_lane = self.get_bcm_lane_info(port, lane_id)
            value = self.get_preemphasis_value(port, bcm_hw_lane,
                                               preemphasis_dict,
                                               txfir_pre_idx)
            txfir_pre_str_p1 = "phy " + bcm_port_name + " CL93N72_UT_CTL2r."
            txfir_pre_str_p2 = txfir_pre_str_p1 + str(bcm_hw_lane)
            txfir_pre_str_p3 = txfir_pre_str_p2 + " CL93N72_TXFIR_PRE"
            txfir_pre_cmd_str = txfir_pre_str_p3 + "=" + hex(value)
            txfir_pre_cmd.append(txfir_pre_cmd_str)

        return txfir_pre_cmd

    # For the Given port and eeprom_dict, configure
    # the preemphasis settings. This invokes the bcmcmd and configures
    # the preemphasis settings for each lane in all the ports
    def preemphasis_set(self, port, eeprom_dict):
        preemphasis_dict = self.get_preemphasis_db(port, eeprom_dict)
        lane_count = self.get_lane_count(port)

        ams_cmd = self.form_bcm_phy_ams_cmd(port, preemphasis_dict)
        txfir_pre_cmd = self.form_bcm_phy_txfir_pre_cmd(port,
                                                        preemphasis_dict)
        txfir_post_cmd = self.form_bcm_phy_txfir_post_cmd(port,
                                                          preemphasis_dict)
        txfir_main_cmd = self.form_bcm_phy_txfir_main_cmd(port,
                                                          preemphasis_dict)
        for lane_id in range(lane_count):
                self.bcm_shell.execute_command(ams_cmd[lane_id])
                self.bcm_shell.execute_command(txfir_pre_cmd[lane_id])
                self.bcm_shell.execute_command(txfir_post_cmd[lane_id])
                self.bcm_shell.execute_command(txfir_main_cmd[lane_id])

        return 0

    # Loop through all the ports, read the eeprom and configure
    # PreEmphasis Values based on eeprom data
    def run(self):
        self.bcm_shell.bcm_port_mapping

        for logical_port in self.bcm_shell.bcm_port_mapping:
            eeprom_dict = get_eeprom_info_dict(logical_port)
            ret_val = self.preemphasis_set(logical_port, eeprom_dict)


# ============================= Functions =============================
# Populate Eeprom Info Dict
# Based on the existing sfputil infra
def get_eeprom_info_dict(logical_port_name):
    eeprom_info_dict = {}
    phy_port_list = logical_port_name_to_physical_port_list(logical_port_name)

    for physical_port in phy_port_list:
        if not platform_sfputil.get_presence(physical_port):
            return eeprom_info_dict
        eeprom_dict = platform_sfputil.get_eeprom_dict(physical_port)

        # Only print detected sfp ports for oneline
        if eeprom_dict is not None:
            eeprom_iface_dict = eeprom_dict.get('interface')
            eeprom_info_dict = eeprom_iface_dict.get('data')

    return eeprom_info_dict


# Returns platform and HW SKU
def get_platform_and_hwsku():
    try:
        proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-H', '-v', PLATFORM_KEY],
                                stdout=subprocess.PIPE,
                                shell=False,
                                stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        proc.wait()
        platform = stdout.rstrip('\n')

        proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-d', '-v', HWSKU_KEY],
                                stdout=subprocess.PIPE,
                                shell=False,
                                stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        proc.wait()
        hwsku = stdout.rstrip('\n')
    except OSError, e:
        raise OSError("Cannot detect platform")

    return (platform, hwsku)


def logical_port_name_to_physical_port_list(port_name):
    if port_name.startswith("Ethernet"):
        if platform_sfputil.is_logical_port(port_name):
            return platform_sfputil.get_logical_to_physical(port_name)
        else:
            print "Error: Invalid port '%s'" % port_name
            return None
    else:
        return [int(port_name)]


# Returns path to port config file
def get_path_to_port_config_file():
    # Get platform and hwsku
    (platform, hwsku) = get_platform_and_hwsku()

    # Load platform module from source
    platform_path = "/".join([PLATFORM_ROOT_PATH, platform])
    hwsku_path = "/".join([platform_path, hwsku])

    # First check for the presence of the new 'port_config.ini' file
    port_config_file_path = "/".join([hwsku_path, "port_config.ini"])
    if not os.path.isfile(port_config_file_path):
        # port_config.ini doesn't exist.
        # Try loading the legacy 'portmap.ini' file
        port_config_file_path = "/".join([hwsku_path, "portmap.ini"])

    return port_config_file_path


# Wait for bcmshell to be running
def check_bcm_shell_status():
    while (1):
        # Check if bcmshell is ready.
        # Execute ps command,
        # If bcmShell is not ready it raises exception
        # Wait till bcmcmd returns success
        cmd = "bcmcmd ps"
        try:
            result = subprocess.check_output(cmd, shell=True)
            return 0
        except subprocess.CalledProcessError as e:
            log_info("Waiting for bcmShell to get ready !!!")
            time.sleep(MINIMUM_WAIT_FOR_BCM_SHELL)
            continue
    return 0


# Wait for syncd to be running
def check_swss_sycnd_status():
    redis_db_cnt = 0
    while (1):
        # Check if syncd starts and redisDb populated
        # Wait till redis Db return valid output
        cmd_p1 = "docker exec -i swss bash -c "
        cmd_p2 = cmd_p1 + "\"echo -en \\\"SELECT 1\\\\nHLEN HIDDEN\\\" | "
        cmd = cmd_p2 + "redis-cli | sed -n 2p\""
        try:
            result = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            # Wait till swss is spawned
            log_info("Waiting for swss to spawn !!!")
            time.sleep(MINIMUM_WAIT_FOR_SWSS_SYNCD)
            continue
        if (result.rstrip() == "5"):
            # Check if bcm_shell server,client is ready
            ret = check_bcm_shell_status()
            return ret
        else:
            if (redis_db_cnt == MINIMUM_RETRY_FOR_SWSS_DB):
                log_error("Fail : RedisDb in swss not populated")
                sys.exit(2)

            # Wait till redisDb is populated
            log_info("Waiting for redisDb to be populated !!!")
            time.sleep(MINIMUM_WAIT_FOR_SWSS_SYNCD)
            redis_db_cnt = redis_db_cnt + 1
    return 0


# Loads platform specific sfputil module from source
def load_platform_sfputil():
    global platform_sfputil

    # Get platform and hwsku
    (platform, hwsku) = get_platform_and_hwsku()

    # Load platform module from source
    platform_path = "/".join([PLATFORM_ROOT_PATH, platform])
    hwsku_path = "/".join([platform_path, hwsku])

    try:
        module_file = "/".join([platform_path, "plugins",
                               PLATFORM_SPECIFIC_MODULE_NAME + ".py"])
        module = imp.load_source(PLATFORM_SPECIFIC_MODULE_NAME, module_file)
    except IOError, e:
        log_error("Failed to load platform module '%s': %s" %
                  (PLATFORM_SPECIFIC_MODULE_NAME, str(e)), True)
        return -1

    try:
        platform_sfputil_class = getattr(module, PLATFORM_SPECIFIC_CLASS_NAME)
        platform_sfputil = platform_sfputil_class()
    except AttributeError, e:
        log_error("Failed to instantiate '%s' class: %s" %
                  (PLATFORM_SPECIFIC_CLASS_NAME, str(e)), True)
        return -2

    return 0


def main():
    log_info("Starting up...")

    if not os.geteuid() == 0:
        log_error("Must be root to run this daemon")
        print "Error: Must be root to run this daemon"
        sys.exit(1)

    # Register our signal handlers
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Default Wait Time till SWSS spawns
    time.sleep(DEFAULT_WAIT_FOR_SWSS_SYNCD)

    err = check_swss_sycnd_status()
    if (err != 0):
        log_error("Error timeout for swss service spawn")
        sys.exit(3)

    # Use the existing sfputil infra to read the eeprom data of inserted Qsfps
    err = load_platform_sfputil()
    if (err != 0):
        sys.exit(2)

    # Load port info
    try:
        port_config_file_path = get_path_to_port_config_file()
        platform_sfputil.read_porttab_mappings(port_config_file_path)
    except Exception, e:
        log_error("Error reading port info (%s)" % str(e), True)
        sys.exit(3)

    # Instantiate Dell QSFP Monitor object
    dell_qsfpd = dell_qsfp_monitor()
    dell_qsfpd.run()

    log_info("QSFP Monitor Completed Successfully...")


if __name__ == "__main__":
    main()
