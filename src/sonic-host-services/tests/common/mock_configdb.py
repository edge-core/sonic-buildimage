class MockConfigDb(object):
    """
        Mock Config DB which responds to data tables requests and store updates to the data table
    """
    STATE_DB = None
    CONFIG_DB = None

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def set_config_db(test_config_db):
        MockConfigDb.CONFIG_DB = test_config_db

    @staticmethod
    def get_config_db():
        return MockConfigDb.CONFIG_DB

    def connect(self, wait_for_init=True, retry_on=True):
        pass

    def get(self, db_id, key, field):
        return MockConfigDb.CONFIG_DB[key][field]

    def get_entry(self, key, field):
        return MockConfigDb.CONFIG_DB[key][field]

    def set_entry(self, key, field, data):
        MockConfigDb.CONFIG_DB[key][field] = data

    def get_table(self, table_name):
        return MockConfigDb.CONFIG_DB[table_name]
