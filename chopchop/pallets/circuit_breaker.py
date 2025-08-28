from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class CircuitBreaker(Pallet):
    
    MODULE_NAME = "CircuitBreaker"
    
    EXTRINSICS = {
        "set_remove_liquidity_limit": "set_remove_liquidity_limit",
    }
    
    def __init__(self, client: Client):
        super().__init__(client)
    
    def set_remove_liquidity_limit_call(self, asset_id, liquidity_limit=None):
        """Create a call to set remove liquidity limit for an asset.
        
        Args:
            asset_id: The asset ID to set limit for
            liquidity_limit: Option<(u32, u32)> - None to remove limit, or tuple for limits
        """
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["set_remove_liquidity_limit"], params={
            "asset_id": asset_id,
            "liquidity_limit": liquidity_limit,  # None removes the limit
        })
        return call
