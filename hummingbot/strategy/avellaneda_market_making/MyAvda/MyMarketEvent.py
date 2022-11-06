

# import lines
from enum import Enum
from dataclasses import dataclass


# event type
class MyMEType(Enum):
    TRADE = 1
    MID_PRICE = 2
    LAST_PRICE = 3
    BALANCE = 4


# market trade event
@dataclass
class MyMETrade:
    trading_pair: str = ""  # e[E]: (BTCUSDT)
    trade_type: int = 1  # e[m]: (true for SELL(2)): BUY(1)/SELL(2)/RANGE(3)
    trade_id: str = ""  # e[t]: Trade ID
    update_id: str = ""  # e[E]: Event time
    price: float = 0  # e[p]: Price
    amount: float = 0  # e[q]: Quantity


# market mid-price update
@dataclass
class MyMEMidPrice:
    trading_pair: str = ""  #
    price: float = 0  # new price


# market last-price update
@dataclass
class MyMELastPrice:
    trading_pair: str = ""  #
    price: float = 0  # new price


# account balance update, from outboundAccountPosition
@dataclass
class MyMEBalance:
    asset: str = ""  # e[a]: BTC, USDT
    free: float = 0  # e[f]: free_balance
    total: float = 0  # e[f] + e[l]:  total_balance
#
