from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    symbol: str
    name: str
    initial_price: float
    decimals: int
    asset_id: Optional[int]
