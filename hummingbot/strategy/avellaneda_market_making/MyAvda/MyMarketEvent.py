

# import lines
from enum import Enum
from dataclasses import dataclass


# event type
class MyMEType(Enum):
    TRADE = 1


# market trade event
@dataclass
class MyMETrade:
    trading_pair: str = ""  # e[E]: (BTCUSDT)
    trade_type: int = 1  # e[m]: (true for SELL(2)): BUY(1)/SELL(2)/RANGE(3)
    trade_id: str = ""  # e[t]: Trade ID
    update_id: str = ""  # e[E]: Event time
    timestamp: float = 0  # update_id * 1e-3
    price: float = 0  # e[p]: Price
    amount: float = 0  # e[q]: Quantity
#
