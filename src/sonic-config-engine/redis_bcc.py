import jinja2

class RedisBytecodeCache(jinja2.BytecodeCache):
    """ A bytecode cache for jinja2 template that stores bytecode in Redis """

    REDIS_HASH = 'JINJA2_CACHE'

    def __init__(self, client):
        self._client = client
        try:
            self._client.connect(self._client.STATE_DB, retry_on=False)
        except Exception:
            self._client = None

    def load_bytecode(self, bucket):
        if self._client is None:
            return
        code = self._client.get(self._client.STATE_DB, self.REDIS_HASH, bucket.key)
        if code is not None:
            bucket.bytecode_from_string(code)

    def dump_bytecode(self, bucket):
        if self._client is None:
            return
        self._client.set(self._client.STATE_DB, self.REDIS_HASH, bucket.key, bucket.bytecode_to_string())

