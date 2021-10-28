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


class MockSelect():

    event_queue = []

    @staticmethod
    def set_event_queue(Q):
        MockSelect.event_queue = Q

    @staticmethod
    def get_event_queue():
        return MockSelect.event_queue

    @staticmethod
    def reset_event_queue():
        MockSelect.event_queue = []

    def __init__(self):
        self.sub_map = {}
        self.TIMEOUT = "TIMEOUT"
        self.ERROR = "ERROR"

    def addSelectable(self, subscriber):
        self.sub_map[subscriber.table] = subscriber

    def select(self, TIMEOUT):
        if not MockSelect.get_event_queue():
            raise TimeoutError
        table, key = MockSelect.get_event_queue().pop(0)
        self.sub_map[table].nextKey(key)
        return "OBJECT", self.sub_map[table]


class MockSubscriberStateTable():

    FD_INIT = 0

    @staticmethod
    def generate_fd():
        curr = MockSubscriberStateTable.FD_INIT
        MockSubscriberStateTable.FD_INIT = curr + 1
        return curr

    @staticmethod
    def reset_fd():
        MockSubscriberStateTable.FD_INIT = 0

    def __init__(self, conn, table, pop, pri):
        self.fd = MockSubscriberStateTable.generate_fd()
        self.next_key = ''
        self.table = table

    def getFd(self):
        return self.fd

    def nextKey(self, key):
        self.next_key = key

    def pop(self):
        table = MockConfigDb.CONFIG_DB.get(self.table, {})
        if self.next_key not in table:
            op = "DEL"
            fvs = {}
        else:
            op = "SET"
            fvs = table.get(self.next_key, {})
        return self.next_key, op, fvs


class MockDBConnector():
    def __init__(self, db, val):
        pass
