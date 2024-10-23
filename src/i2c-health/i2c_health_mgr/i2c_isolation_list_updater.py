from swsscommon.swsscommon import SonicV2Connector
from i2c_health_mgr import i2c_device_entity
from i2c_health_mgr.i2c_health_msgs import get_i2c_health_msg

I2C_ISOLATION_LIST_TABLE = 'I2C_ISOLATION_LIST|{}|{}'

class I2CIsolationListUpdater():
    def __init__(self, logger):
        self.logger=logger
        self.state_db = SonicV2Connector(use_unix_socket_path=True, host='127.0.0.1')
        self.state_db.connect(self.state_db.STATE_DB)

    def add_device_into_isolation_list(self, region_id, i2c_device_entity_list):
        """
        This function is used to add the i2c device into i2c isolation list in STATE DB
        """
        for entity in i2c_device_entity_list:
            try:
                table_key = I2C_ISOLATION_LIST_TABLE.format(region_id, entity.get_i2c_address_path())
                self.state_db.set(self.state_db.STATE_DB, table_key, 'device_name', entity.get_name())
            except:
                msg = get_i2c_health_msg(23)
                self.logger.log_error(msg.format(entity.get_name(), region_id, entity.get_i2c_address_path()))

    def remove_device_from_isolation_list(self, region_id, i2c_device_entity_list):
        """
        This function is used to remove the i2c device from i2c isolation list in STATE DB
        """
        for entity in i2c_device_entity_list:
            try:
                table_key = I2C_ISOLATION_LIST_TABLE.format(region_id, entity.get_i2c_address_path())
                self.state_db.delete(self.state_db.STATE_DB, table_key)
            except:
                msg = get_i2c_health_msg(24)
                self.logger.log_error(msg.format(entity.get_name(), region_id, entity.get_i2c_address_path()))
