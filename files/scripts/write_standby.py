#!/usr/bin/env python3

import time

from sonic_py_common import logger as log
from swsscommon.swsscommon import ConfigDBConnector, DBConnector, FieldValuePairs, ProducerStateTable, SonicV2Connector
from swsscommon.swsscommon import APPL_DB 

logger = log.Logger('write_standby')

REDIS_SOCK_PATH = '/var/run/redis/redis.sock'


def create_fvs(**kwargs):
    return FieldValuePairs(list(kwargs.items()))

class MuxStateWriter(object):
    """
    Class used to write standby mux state to APP DB
    """

    def __init__(self):
        self.config_db_connector = None
        self.appl_db_connector = None
        self.asic_db_connector = None

    @property
    def config_db(self):
        """
        Returns config DB connector.
        Initializes the connector during the first call
        """
        if self.config_db_connector is None:
            self.config_db_connector = ConfigDBConnector()
            self.config_db_connector.connect()

        return self.config_db_connector

    @property
    def appl_db(self):
        """
        Returns the app DB connector.
        Initializes the connector during the first call
        """
        if self.appl_db_connector is None:
            self.appl_db_connector = DBConnector(APPL_DB, REDIS_SOCK_PATH, True)
        return self.appl_db_connector

    @property
    def asic_db(self):
        """
        Returns the ASIC DB connector.
        Initializes the connector during the first call
        """
        if self.asic_db_connector is None:
            self.asic_db_connector = SonicV2Connector()
            self.asic_db_connector.connect('ASIC_DB')

        return self.asic_db_connector

    @property
    def tunnel_name(self):
        """
        Returns the name of the IP-in-IP tunnel used for Dual ToR devices
        """
        return self.config_db.get_keys('TUNNEL')[0]

    @property
    def is_dualtor(self):
        """
        Checks if script is running on a dual ToR system
        """
        localhost_key = self.config_db.get_keys('DEVICE_METADATA')[0]
        metadata = self.config_db.get_entry('DEVICE_METADATA', localhost_key)

        return 'subtype' in metadata and 'dualtor' in metadata['subtype'].lower()

    def get_auto_mux_intfs(self):
        """
        Returns a list of all mux cable interfaces that are configured to auto-switch
        """
        all_intfs = self.config_db.get_table('MUX_CABLE')
        auto_intfs = [intf for intf, status in all_intfs.items()
                                if status['state'].lower() == 'auto']
        return auto_intfs

    def tunnel_exists(self):
        """
        Checks if the IP-in-IP tunnel has been written to ASIC DB
        """
        tunnel_key_pattern = 'ASIC_STATE:SAI_OBJECT_TYPE_TUNNEL:*'
        return len(self.asic_db.keys('ASIC_DB', tunnel_key_pattern)) > 0

    def wait_for_tunnel(self, interval=1, timeout=30):
        """
        Waits until the IP-in-IP tunnel has been created

        Returns:
            (bool) True if the tunnel has been created
                   False if the timeout period is exceeded
        """
        logger.log_info("Waiting for tunnel {} with timeout {} seconds".format(self.tunnel_name, timeout))
        start = time.time()
        curr_time = time.time()

        while not self.tunnel_exists() and curr_time - start < timeout:
            time.sleep(interval) 
            curr_time = time.time()

        # If we timed out, return False else return True
        return curr_time - start < timeout

    def apply_mux_config(self):
        """
        Writes standby mux state to APP DB for all mux interfaces
        """
        if not self.is_dualtor:
            # If not running on a dual ToR system, take no action
            return
        intfs = self.get_auto_mux_intfs()
        state = 'standby'
        if self.wait_for_tunnel():
            logger.log_warning("Applying {} state to interfaces {}".format(state, intfs))
            producer_state_table = ProducerStateTable(self.appl_db, 'MUX_CABLE_TABLE')
            fvs = create_fvs(state=state)

            for intf in intfs:
                producer_state_table.set(intf, fvs)
        else:
            logger.log_error("Timed out waiting for tunnel {}, mux state will not be written".format(self.tunnel_name))


if __name__ == '__main__':
    mux_writer = MuxStateWriter()
    mux_writer.apply_mux_config()
