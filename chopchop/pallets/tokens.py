from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class Tokens(Pallet):

    MODULE_NAME = "Tokens"

    EXTRINSICS = {
        "transfer": "transfer",
        "set_balance": "set_balance",
    }

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def transfer(self, who, dest, amount, wait_for_result=True):
        call = create_call(self._client,
                           self.MODULE_NAME,
                           self.EXTRINSICS["transfer"],
                           params={
                               "dest": dest,
                               "value": amount,
                           })

        return submit_extrinsic(self._client, who, call, wait_for_result)

    def set_balance(self, who, dest, amount, wait_for_result=True):
        raise NotImplementedError

    def query_account_balance(self, account, asset_id, at = None) -> int:
        return self.query_entry(self.MODULE_NAME, "Accounts", params=[account, asset_id], at=at)["free"]