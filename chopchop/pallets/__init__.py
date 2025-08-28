from chopchop.client import Client


class Pallet:

    def __init__(self, client: Client):
        self._client = client

    def query_entries(self, module, func, at = None):
        entries = self._client.api.query_map(module, func, block_hash=at)
        return entries

    def query_entry(self, module, func, params, at = None):
        return self._client.api.query(module, func, params, block_hash=at)
