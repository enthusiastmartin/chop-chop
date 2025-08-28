from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class Uniques(Pallet):

    MODULE_NAME = "Uniques"

    EXTRINSICS = {
    }

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def query_instances(self, collection_id) -> int:
        #return self.query_entry(self.MODULE_NAME, "Asset", [collection_id, 2])
        entries = self._client.api.query_map(self.MODULE_NAME, "Asset", [collection_id])
        positions = {}
        for entry in entries:
            instance_id = int(entry[0].value)
            owner = str(entry[1]["owner"])
            positions[instance_id] = owner

        return positions

    def query_owner(self, collection_id, instance_id) -> int:
        #return self.query_entry(self.MODULE_NAME, "Asset", [collection_id, 2])
        entry = self._client.api.query(self.MODULE_NAME, "Asset", [collection_id, instance_id])
        return entry["owner"].value
