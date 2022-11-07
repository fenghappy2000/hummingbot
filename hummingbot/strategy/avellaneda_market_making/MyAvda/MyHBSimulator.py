

# import lines
from .MyAvdaContext import MyAvdaContext
from .MyMarketEvent import MyMETrade
from dataclasses import dataclass


# simulator in humbot frwk, for data check with avstg
@dataclass
class MyHBSimulator:
    _AvdaCtx: MyAvdaContext = MyAvdaContext()

    def OnStart(self, ts: float):
        self._AvdaCtx.OnStart(ts)

    def OnUpdate(self, ts: float, midPrice: float, lastPrice: float, baseBalance: float, quoteBalance: float):

        # 1. pass market data to ctx
        self._AvdaCtx.SetMidPrice(midPrice)
        self._AvdaCtx.SetLastPrice(lastPrice)
        self._AvdaCtx.SetBaseBalance(baseBalance)
        self._AvdaCtx.SetQuoteBalance(quoteBalance)

        # 2. call update
        self._AvdaCtx.OnUpdate(ts)

    def OnStop(self, ts: float):
        self._AvdaCtx.OnStop(ts)

    def ForwardTrade(self, trading_pair: str, trade_type: int, trade_id: str, update_id: str, timestamp: float, price: float, amount: float):
        ev: MyMETrade = MyMETrade()

        ev.trading_pair = str(trading_pair)
        ev.trade_type = int(trade_type)
        ev.trade_id = str(trade_id)
        ev.update_id = str(update_id)
        ev.timestamp = float(timestamp)
        ev.price = float(price)
        ev.amount = float(amount)

        self._AvdaCtx.InputEventTrade(ev)
#
