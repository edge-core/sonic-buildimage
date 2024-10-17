class SonicV2Connector:

    def __init__(self, use_unix_socket_path=True, host='127.0.0.1'):
        self.STATE_DB = 'STATE_DB'
        self.data = {}

    def connect(self, db):
        pass

    def close(self, db):
        pass

    def get(self, db, table, field):
        table_data = self.data.get(table)
        if table_data is None:
            return "N/A"
        return table_data.get(field, "N/A")

    def set(self, db, table, field, value):
        fv = {field: value}
        self.data[table] = fv

    def delete(self, db, table):
        return self.data.pop(table)