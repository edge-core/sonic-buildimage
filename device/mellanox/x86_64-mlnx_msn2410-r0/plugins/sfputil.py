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

class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""
    PORT_START = 0
    PORT_END = 55
    PORTS_IN_BLOCK = 56
    QSFP_PORT_START = 48
    EEPROM_OFFSET = 1

    _port_to_eeprom_mapping = {}

    db_sel = None
    db_sel_timeout = None
    db_sel_object = None
    db_sel_tbl = None
    state_db = None
    sfpd_status_tbl = None

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

    def __init__(self):
        eeprom_path = "/sys/class/i2c-adapter/i2c-2/2-0048/hwmon/hwmon7/qsfp{0}_eeprom"

        for x in range(0, self.port_end + 1):
            self._port_to_eeprom_mapping[x] = eeprom_path.format(x + self.EEPROM_OFFSET)

        SfpUtilBase.__init__(self)


    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        try:
            reg_file = open("/bsp/qsfp/qsfp%d_status" % (port_num+1))
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        content = reg_file.readline().rstrip()

        # content is a string with the qsfp status
        if content == "good":
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

        lpm = 'on' if lpmode else 'off'
        lpm_cmd = "docker exec syncd python /usr/share/sonic/platform/plugins/sfplpmset.py {} {}".format(port_num, lpm)
        sfp_port_names = self.physical_to_logical[port_num]

        # Get port admin status
        try:
            enabled_ports = subprocess.check_output("ip link show up", shell=True)
        except subprocess.CalledProcessError as e:
            print "Error! Unable to get ports status, err msg: {}".format(e.output)
            return False

        port_to_disable = []
        for port in sfp_port_names:
            if port in enabled_ports:
                port_to_disable.append(port)

        # Disable ports before LPM settings
        for port in port_to_disable:
            try:
                subprocess.check_output("ifconfig {} down".format(port), shell=True)
            except subprocess.CalledProcessError as e:
                print "Error! Unable to set admin status to DOWN for {}, rc = {}, err msg: {}".format(port, e.returncode, e.output)
                return False

        time.sleep(3)

        # Set LPM
        try:
            subprocess.check_output(lpm_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print "Error! Unable to set LPM for {}, rc = {}, err msg: {}".format(port_num, e.returncode, e.output)
            return False

        # Enable ports after LPM settings
        for port in port_to_disable:
            try:
                subprocess.check_output("ifconfig {} up".format(port), shell=True)
            except subprocess.CalledProcessError as e:
                print "Error! Unable to set admin status to UP for {}, rc = {}, err msg: {}".format(port, e.returncode, e.output)
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

        (state, c) = self.db_sel.select(timeout)
        if state == self.db_sel_timeout:
            status = True
        elif state != self.db_sel_object:
            status = False
        else:
            (key, op, fvp) = self.db_sel_tbl.pop()
            phy_port_dict[key] = op

        return status, phy_port_dict

