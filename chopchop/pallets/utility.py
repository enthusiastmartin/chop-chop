from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class Utility(Pallet):

    MODULE_NAME = "Utility"

    EXTRINSICS = {
        "batch": "batch",
        "batch_all": "batch_all",
    }
        
    def batch(self, who, calls, wait_for_result=True):
        call = create_call(client=self._client,
            module="Utility",
            func="batch",
            params={
                "calls": calls,
            },
        )

        return submit_extrinsic(self._client, who, call, wait_for_result)


    def batch_all(self, who, calls, wait_for_result=True):
        call = create_call(client=self._client,
            module="Utility",
            func="batch_all",
            params={
                "calls": calls,
            },
        )

        return submit_extrinsic(self._client, who, call, wait_for_result)


    def create_dispatch_as_call(self, who, call):
        call = create_call(client=self._client,
                           module="Utility",
                           func="dispatch_as",
                           params={
                               "as_origin": {"system" : {"Signed" : who}},
                               "call": call,
                           },
                           )
        return call

    def create_force_batch(self, calls):
        call = create_call(client=self._client,
                           module="Utility",
                           func="force_batch",
                           params={
                               "calls": calls,
                           },
                           )
        return call


