from collections import defaultdict
from dataclasses import dataclass

from chopchop.client import Client, create_call, submit_extrinsic
from chopchop.pallets import Pallet
from chopchop.pallets.balances import Balances
from chopchop.pallets.tokens import Tokens

from typing import List, Dict, Optional

@dataclass
class Asset:
    symbol: str
    name: str
    initial_price: float
    decimals: int
    asset_id: Optional[int]


@dataclass
class InitParams:
    hdx_amount: int
    stable_amount: int
    hdx_weight: int
    stable_weight: int
    hdx_price: int
    stable_price: int

@dataclass
class AssetState:
    reserve: int
    hub_reserve: int
    shares: int
    protocol_shares: int
    cap: int
    tradability: int
    asset_id: Optional[int]

    @staticmethod
    def from_entry(asset_id: int, entry: dict) -> "AssetState":
        return AssetState(entry["reserve"], entry["hub_reserve"],
                          entry["shares"],
                          entry["protocol_shares"],
                          entry["cap"],
                          entry["tradable"],
                          asset_id)


def convert_usd_price_to_initial_price_for_omnipool(price: float) -> int:
    dai_price_in_lrna = 0.045
    price_in_lrna = dai_price_in_lrna * price
    one = pow(10 ,  18)
    return int(price_in_lrna * one)


@dataclass
class Position:
    asset_id: int
    amount: int
    shares: int
    price: int

    @staticmethod
    def from_entry(entry: dict) -> "Position":
        return Position(entry["asset_id"], entry["amount"],
                        entry["shares"],
                        entry["price"])


class Omnipool(Pallet):
    ACCOUNT = "7L53bUTBbfuj14UpdCNPwmgzzHSsrsTWBHX5pys32mVWM3C1"

    MODULE_NAME = "Omnipool"

    ASSET_STATE_STORAGE = "Assets"

    EXTRINSICS = {
        "add_token": "add_token",
        "init_call": "initialize_pool",
        "add_liquidity": "add_liquidity",
        "remove_liquidity": "remove_liquidity",
        "sell": "sell",
        "buy": "buy",
        "set_asset_tradable_state": "set_asset_tradable_state",
        "remove_token": "remove_token",
    }

    def __init__(self, client: Client):
        super().__init__(client)
        self._balances = Balances(self._client)
        self._tokens = Tokens(self._client)

    def create_add_token_call(self, who, asset_id, initial_price, cap ):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["add_token"], params={
            "asset": asset_id,
            "initial_price": initial_price,
            "weight_cap": cap,
            "position_owner": who,
        })

        return create_call(client=self._client,
                           module="Sudo",
                           func="sudo",
                           params={
                               "call": call.value,
                           },
                           )


    def add_token_call(self, who, asset: Asset):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["add_token"], params={
            "asset": asset.asset_id,
            "initial_price": convert_usd_price_to_initial_price_for_omnipool(float(asset.initial_price)),
            "weight_cap": 1_000_000,
            "position_owner": who,
        })

        return create_call(client=self._client,
                           module="Sudo",
                           func="sudo",
                           params={
                               "call": call.value,
                           },
                           )

    def init_call(self, who, params:InitParams ):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["init_call"], params={
            "stable_asset_price": params.stable_price,
            "native_asset_price": params.hdx_price,
            "stable_weight_cap": params.stable_weight,
            "native_weight_cap": params.hdx_weight,
        })

        return create_call(client=self._client,
                           module="Sudo",
                           func="sudo",
                           params={
                               "call": call.value,
                           },
                           )


    def add_liquidity(self, who, asset, amount, wait_for_result=True):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["add_liquidity"], params={
            "asset": asset,
            "amount": amount,
        })

        return submit_extrinsic(self._client, who, call, wait_for_result)

    def add_liquidity_call(self, asset, amount):
        return create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["add_liquidity"], params={
            "asset": asset,
            "amount": amount,
        })


    def remove_liquidity(self, who, position_id, share_amount, wait_for_result=True):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["remove_liquidity"], params={
            "position_id": position_id,
            "amount": share_amount,
        })

        return submit_extrinsic(self._client, who, call, wait_for_result)
    def remove_liquidity_call(self, position_id, share_amount):
        return create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["remove_liquidity"], params={
            "position_id": position_id,
            "amount": share_amount,
        })

    def sell(self, who, asset_in, asset_out, amount, limit, wait_for_result=True):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["sell"], params={
            "asset_in": asset_in,
            "asset_out": asset_out,
            "amount": amount,
            "min_buy_amount": limit
        })

        return submit_extrinsic(self._client, who, call, wait_for_result)
    def sell_call(self, asset_in, asset_out, amount, limit, wait_for_result=True):
        return create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["sell"], params={
            "asset_in": asset_in,
            "asset_out": asset_out,
            "amount": amount,
            "min_buy_amount": limit
        })


    def buy(self, who, asset_in, asset_out, amount, limit, wait_for_result=True):
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["buy"], params={
            "asset_in": asset_in,
            "asset_out": asset_out,
            "amount": amount,
            "max_sell_amount": limit
        })
        return submit_extrinsic(self._client, who, call, wait_for_result)

    def asset_states(self, at = None) -> List[AssetState]:
        entries = self.query_entries(self.MODULE_NAME, self.ASSET_STATE_STORAGE, at=at)

        states = []

        for asset_id, entry in entries:
            if asset_id == 0:
                reserve = self._balances.query_account_balance(self.ACCOUNT)
            else:
                reserve = self._tokens.query_account_balance(self.ACCOUNT, asset_id)
            entry = entry.value.copy()
            entry["reserve"] = reserve
            states.append(AssetState.from_entry(asset_id, entry))
        return states

    def asset_state(self, asset_id) -> AssetState:
        entry = self.query_entry(self.MODULE_NAME, self.ASSET_STATE_STORAGE, params=[asset_id])
        if asset_id == 0:
            reserve = self._balances.query_account_balance(self.ACCOUNT)
        else:
            reserve = self._tokens.query_account_balance(self.ACCOUNT, asset_id)
        entry = entry.value.copy()
        entry["reserve"] = reserve
        return AssetState.from_entry(asset_id, entry)

    def assets_hub_reserve(self) -> int:
        states = self.asset_states()

        return sum(state.hub_reserve for state in states)

    def account_hub_reserve(self) -> int:
        return self._tokens.query_account_balance(self.ACCOUNT, 1)

    def retrieve_positions(self) -> Dict[int, AssetState]:
        entries = self.query_entries(self.MODULE_NAME, "Positions")

        return {position_id.value: Position.from_entry(entry.value) for position_id, entry in entries}

    def positions_with_owner(self, owners) :
        positions = self.retrieve_positions()

        output = defaultdict(list)
        for (position_id, position)  in positions.items():
            owner = owners[position_id]
            output[(owner,position.asset_id)].append((position_id,position))

        return output

    def set_asset_tradable_state_call(self, asset_id, state):
        """Create a call to set asset's tradable state."""
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["set_asset_tradable_state"], params={
            "asset_id": asset_id,
            "state": {"bits": state},
        })
        return call

    def remove_token_call(self, asset_id, beneficiary="13UVJyLnbVp9RBZYFwFGyDvVd1y27Tt8tkntv6Q7JVPhFsTB"):
        """Create a call to remove token from Omnipool.
        
        Args:
            asset_id: The asset ID to remove
            beneficiary: The beneficiary account (defaults to Treasury)
        """
        call = create_call(self._client, self.MODULE_NAME, self.EXTRINSICS["remove_token"], params={
            "asset_id": asset_id,
            "beneficiary": beneficiary,
        })
        return call


