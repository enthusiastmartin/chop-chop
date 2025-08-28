from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class Balances(Pallet):
    MODULE_NAME = "Balances"

    EXTRINSICS = {
        "transfer": "transfer",
        "set_balance": "set_balance",
    }

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

    def create_set_balance(self, dest, currency_id, amount, wait_for_result=True):
        call = create_call(self._client, 
                "Balances" if currency_id == 0 else "Tokens",
                self.EXTRINSICS["set_balance"], 
                params={
                    "who": dest,
                    "currency_id": currency_id,
                    "new_free": amount,
                    "new_reserved": 0
                    })
        
        return create_call(client=self._client,
            module="Sudo",
            func="sudo",
            params={
                "call": call.value,
            },
        )

    def query_account_balance(self, account) -> int:
        return self.query_entry("System", "Account", params=[account]).value["data"]["free"]
