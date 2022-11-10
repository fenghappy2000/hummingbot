

# import lines
from enum import Enum
from dataclasses import dataclass
from typing import List
from decimal import Decimal


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


class MyPriceSize:
    def __init__(self, price: Decimal, size: Decimal):
        self.price: Decimal = price
        self.size: Decimal = size

    def __repr__(self):
        return f"[ p: {self.price} s: {self.size} ]"


class MyProposal:
    def __init__(self, buys: List[MyPriceSize], sells: List[MyPriceSize]):
        self.buys: List[MyPriceSize] = buys
        self.sells: List[MyPriceSize] = sells

    def __repr__(self):
        return f"{len(self.buys)} buys: {', '.join([str(o) for o in self.buys])} " \
               f"{len(self.sells)} sells: {', '.join([str(o) for o in self.sells])}"

#
