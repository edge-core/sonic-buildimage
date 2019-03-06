# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    import subprocess
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

# parameters for DB connection 
REDIS_HOSTNAME = "localhost"
REDIS_PORT = 6379
REDIS_TIMEOUT_USECS = 0

# parameters for SFP presence
SFP_STATUS_INSERTED = '1'

GET_HWSKU_CMD = "sonic-cfggen -d -v DEVICE_METADATA.localhost.hwsku"

# magic code defnition for port number, qsfp port position of each hwsku
# port_position_tuple = (PORT_START, QSFP_PORT_START, PORT_END, PORT_IN_BLOCK, EEPROM_OFFSET)
hwsku_dict = {'ACS-MSN2700': 0, "LS-SN2700":0, 'ACS-MSN2740': 0, 'ACS-MSN2100': 1, 'ACS-MSN2410': 2, 'ACS-MSN2010': 3, 'ACS-MSN3700': 0, 'ACS-MSN3700C': 0, 'Mellanox-SN2700': 0, 'Mellanox-SN2700-D48C8': 0}
port_position_tuple_list = [(0, 0, 31, 32, 1), (0, 0, 15, 16, 1), (0, 48, 55, 56, 1),(0, 18, 21, 22, 1)]

class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""
    PORT_START = 0
    QSFP_PORT_START = 0
    PORT_END = 0
    PORTS_IN_BLOCK = 0
    EEPROM_OFFSET = 0

    _port_to_eeprom_mapping = {}

    db_sel = None
    db_sel_timeout = None
    db_sel_object = None
    db_sel_tbl = None
    state_db = None
    sfpd_status_tbl = None
    qsfp_sysfs_path = "/sys/devices/platform/i2c_mlxcpld.1/i2c-1/i2c-2/2-0048/"

    @property
    def port_start(self):
        return self.PORT_START

    @property
    def port_end(self):
        return self.PORT_END

    @property
    def qsfp_ports(self):
        return range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        return self._port_to_eeprom_mapping

    def get_port_position_tuple_by_sku_name(self):
        p = subprocess.Popen(GET_HWSKU_CMD, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        position_tuple = port_position_tuple_list[hwsku_dict[out.rstrip('\n')]]
        return position_tuple

    def __init__(self):
        port_position_tuple = self.get_port_position_tuple_by_sku_name()
        self.PORT_START = port_position_tuple[0]
        self.QSFP_PORT_START = port_position_tuple[1]
        self.PORT_END = port_position_tuple[2]
        self.PORTS_IN_BLOCK = port_position_tuple[3]
        self.EEPROM_OFFSET = port_position_tuple[4]

        for x in range(0, self.port_end + 1):
            self._port_to_eeprom_mapping[x] = self.qsfp_sysfs_path + "qsfp{}".format(x + self.EEPROM_OFFSET)

        SfpUtilBase.__init__(self)

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open(self.qsfp_sysfs_path + "qsfp{}_status".format(port_num + 1))
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # content is a string with the qsfp status
        if content == SFP_STATUS_INSERTED:
            return True

        return False

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        lpm_cmd = "docker exec syncd python /usr/share/sonic/platform/plugins/sfplpmget.py {}".format(port_num)

        try:
            output = subprocess.check_output(lpm_cmd, shell=True)
            if 'LPM ON' in output:
                return True
        except subprocess.CalledProcessError as e:
            print "Error! Unable to get LPM for {}, rc = {}, err msg: {}".format(port_num, e.returncode, e.output)
            return False

        return False

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        curr_lpmode = self.get_low_power_mode(port_num)
        if curr_lpmode == lpmode:
            return True

        # Compose LPM command
        lpm = 'on' if lpmode else 'off'
        lpm_cmd = "docker exec syncd python /usr/share/sonic/platform/plugins/sfplpmset.py {} {}".format(port_num, lpm)

        # Set LPM
        try:
            subprocess.check_output(lpm_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print "Error! Unable to set LPM for {}, rc = {}, err msg: {}".format(port_num, e.returncode, e.output)
            return False

        return True

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        lpm_cmd = "docker exec syncd python /usr/share/sonic/platform/plugins/sfpreset.py {}".format(port_num)

        try:
            subprocess.check_output(lpm_cmd, shell=True)
            return True
        except subprocess.CalledProcessError as e:
            print "Error! Unable to set LPM for {}, rc = {}, err msg: {}".format(port_num, e.returncode, e.output)
            return False

        return False

    def get_transceiver_change_event(self, timeout=0):
        phy_port_dict = {}
        status = True

        if self.db_sel == None:
            from swsscommon import swsscommon
            self.state_db = swsscommon.DBConnector(swsscommon.STATE_DB,
                                             REDIS_HOSTNAME,
                                             REDIS_PORT,
                                             REDIS_TIMEOUT_USECS)

            # Subscribe to state table for SFP change notifications
            self.db_sel = swsscommon.Select()
            self.db_sel_tbl = swsscommon.NotificationConsumer(self.state_db, 'TRANSCEIVER_NOTIFY')
            self.db_sel.addSelectable(self.db_sel_tbl)
            self.db_sel_timeout = swsscommon.Select.TIMEOUT
            self.db_sel_object = swsscommon.Select.OBJECT
            self.sfpd_status_tbl = swsscommon.Table(self.state_db, 'MLNX_SFPD_TASK')

        # Check the liveness of mlnx-sfpd, if it failed, return false
        keys = self.sfpd_status_tbl.getKeys()
        if 'LIVENESS' not in keys:
            return False, phy_port_dict

        if timeout:
            (state, c) = self.db_sel.select(timeout)
        else:
            (state, c) = self.db_sel.select()

        if state == self.db_sel_timeout:
            status = True
        elif state != self.db_sel_object:
            status = False
        else:
            (key, op, fvp) = self.db_sel_tbl.pop()
            phy_port_dict[key] = op

        return status, phy_port_dict

