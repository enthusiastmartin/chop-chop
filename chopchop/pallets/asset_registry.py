from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet


class AssetRegistry(Pallet):
    
    MODULE_NAME = "AssetRegistry"
    
    EXTRINSICS = {
        "update": "update",
    }
    
    def __init__(self, client: Client):
        super().__init__(client)
    
    def update_call(self, asset_id, name=None, asset_type=None, existential_deposit=None, 
                   xcm_rate_limit=None, is_sufficient=None, symbol=None, decimals=None, location=None):
        """Create a call to update registered asset.
        
        Args:
            asset_id: u32 - The asset ID to update
            name: Option<Bytes> - Asset name (None to keep unchanged)
            asset_type: Option<PalletAssetRegistryAssetType> - Asset type (None to keep unchanged)
            existential_deposit: Option<u128> - Minimum balance required (None to keep unchanged)
            xcm_rate_limit: Option<u128> - XCM rate limit (None to keep unchanged)
            is_sufficient: Option<bool> - Whether asset is sufficient (None to keep unchanged)
            symbol: Option<Bytes> - Asset symbol (None to keep unchanged)
            decimals: Option<u8> - Asset decimals (None to keep unchanged)
            location: Option<HydradxRuntimeXcmAssetLocation> - Asset location (None to keep unchanged)
        """
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["update"], params={
            "asset_id": asset_id,
            "name": name,
            "asset_type": asset_type,
            "existential_deposit": existential_deposit,
            "xcm_rate_limit": xcm_rate_limit,
            "is_sufficient": is_sufficient,
            "symbol": symbol,
            "decimals": decimals,
            "location": location,
        })
        return call
    
    def get_asset_details(self, asset_id):
        """Query current asset details from the registry.
        
        Args:
            asset_id: u32 - The asset ID to query
            
        Returns:
            Asset details dictionary or None if not found
        """
        try:
            result = self._client.api.query("AssetRegistry", "Assets", [asset_id])
            if result.value:
                return result.value
            return None
        except Exception as e:
            print(f"Error querying asset {asset_id}: {e}")
            return None
