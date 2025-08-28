from chopchop.client import Client, create_call
from chopchop.pallets import Pallet


class OmnipoolWLM(Pallet):

    MODULE_NAME = "OmnipoolWarehouseLM"

    EXTRINSICS = {
    }

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def get_deposit_positions(self, asset_id):
        entries = self.query_entries(self.MODULE_NAME, "Deposit")
        positions = []
        for entry in entries:
            deposit_id= int(entry[0].value)
            amm_pool_id= entry[1]["amm_pool_id"]
            farms= entry[1]["yield_farm_entries"]
            if amm_pool_id == asset_id:
                positions.append((deposit_id, farms))

        return positions


class OmnipoolLM(Pallet):

    MODULE_NAME = "OmnipoolLiquidityMining"

    EXTRINSICS = {
    }

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def create_exit_farm_call(self, deposit_id, farm_ids):
        return create_call(self._client, self.MODULE_NAME, "exit_farms", params={
            "deposit_id": deposit_id,
            "yield_farm_ids": [farm_ids],
        })

    def get_omnipool_position_id(self, deposit_id) -> int:
        entry = self._client.api.query(self.MODULE_NAME, "OmniPositionId", [deposit_id])
        return entry.value
