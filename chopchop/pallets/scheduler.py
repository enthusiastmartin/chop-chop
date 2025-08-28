from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class Scheduler(Pallet):
    MODULE_NAME = "Scheduler"

    EXTRINSICS = {
        "schedule_after": "schedule_after",
    }

    def schedule_after(self, who, after, call, maybe_periodic=None, priority=0, wait_for_result=True):
        call_data = create_call(self._client,
                               self.MODULE_NAME,
                               self.EXTRINSICS["schedule_after"],
                               params={
                                   "after": after,
                                   "maybe_periodic": maybe_periodic,
                                   "priority": priority,
                                   "call": call,
                               })

        return submit_extrinsic(self._client, who, call_data, wait_for_result)

    def create_schedule_after_call(self, after, call, maybe_periodic=None, priority=0):
        return create_call(self._client,
                          self.MODULE_NAME,
                          self.EXTRINSICS["schedule_after"],
                          params={
                              "after": after,
                              "maybe_periodic": maybe_periodic,
                              "priority": priority,
                              "call": call,
                          })