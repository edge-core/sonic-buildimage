class MockConfigDb(object):
    """
        Mock Config DB which responds to data tables requests and store updates to the data table
    """
    STATE_DB = None
    CONFIG_DB = None
    event_queue = []

    def __init__(self, **kwargs):
        self.handlers = {}

    @staticmethod
    def set_config_db(test_config_db):
        MockConfigDb.CONFIG_DB = test_config_db

    @staticmethod
    def deserialize_key(key, separator="|"):
        tokens = key.split(separator)
        if len(tokens) > 1:
            return tuple(tokens)
        else:
            return key

    @staticmethod
    def get_config_db():
        return MockConfigDb.CONFIG_DB

    def connect(self, wait_for_init=True, retry_on=True):
        pass

    def get(self, db_id, key, field):
        return MockConfigDb.CONFIG_DB[key][field]

    def get_entry(self, key, field):
        return MockConfigDb.CONFIG_DB[key][field]

    def mod_entry(self, key, field, data):
        existing_data = self.get_entry(key, field)
        existing_data.update(data)
        self.set_entry(key, field, existing_data)

    def set_entry(self, key, field, data):
        MockConfigDb.CONFIG_DB[key][field] = data

    def get_table(self, table_name):
        return MockConfigDb.CONFIG_DB[table_name]

    def subscribe(self, table_name, callback):
        self.handlers[table_name] = callback

    def listen(self, init_data_handler=None):
        for e in MockConfigDb.event_queue:
            self.handlers[e[0]](e[0], e[1], self.get_entry(e[0], e[1]))


class MockDBConnector():
    def __init__(self, db, val):
        pass
