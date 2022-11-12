

# import lines
from MyAvda.MyAvdaContext import MyAvdaContext
from MyAvda.MyMarketEvent import MyMETrade, MyProposal, MyPriceSize
from dataclasses import dataclass
from typing import List, Optional

import time


@dataclass
class MyASController:
    _SampleNumSec: int = 60
    _AvdaCtx: MyAvdaContext = MyAvdaContext()

    def RunMain(self):
        print("hello: sample num[{}]".format(self._SampleNumSec))
        tsStart: float = time.time()
        self._AvdaCtx.OnStart(tsStart)

        # 0. first get market price
        midPrice: float = 19000
        lastPrice: float = 19001
        baseBalance: float = 10
        quoteBalance: float = 10

        run: bool = True
        while run:
            tsUpdate: float = time.time()

            # 1. pass market to context
            self._AvdaCtx.SetMidPrice(midPrice)
            self._AvdaCtx.SetLastPrice(lastPrice)
            self._AvdaCtx.SetBaseBalance(baseBalance)
            self._AvdaCtx.SetQuoteBalance(quoteBalance)

            # 2. call ctx update
            self._AvdaCtx.OnUpdate(tsUpdate)

            # 3. check if algorithom ready
            myprop: MyProposal = self._AvdaCtx.GetMyProposal()
            if myprop is None:
                # not ready, just continue
                pass
            else:
                # 4. ready, use myprop to create order
                listBuy: List[MyPriceSize] = myprop.buys
                listSell: List[MyPriceSize] = myprop.sells

                buy0: Optional[MyPriceSize] = None
                sell0: Optional[MyPriceSize] = None
                if len(listBuy) > 0:
                    buy0 = listBuy[0]
                    print("CreateBuyOrder: price[{}], size[{}]".format(buy0.price, buy0.size))

            # update every second
            time.sleep(1)

            # simulate get data from market
            timeDelta: float = tsUpdate - tsStart
            midPrice = midPrice + (0.1 * timeDelta)
            lastPrice = lastPrice + (0.1 * timeDelta)
            baseBalance = baseBalance + (0.1 * timeDelta)
            quoteBalance = quoteBalance + (0.1 * timeDelta)

            # simulate trade event
            self.SimulateRecvTradeEvent(tsUpdate + 1, timeDelta)
            # end while
        # out while
        print("out while")

    def SimulateRecvTradeEvent(self, tsNow: float, delta: float):
        ev: MyMETrade = MyMETrade()

        ev.trading_pair = str("BTC-USDT")
        ev.trade_type = int("1")
        ev.trade_id = str("0")
        ev.update_id = str("0")
        ev.timestamp = float(tsNow)
        ev.price = float(19002 + (0.1 * delta))
        ev.amount = float(0.1 * delta)

        self._AvdaCtx.InputEventTrade(ev)


if __name__ == "__main__":
    asCtrler: MyASController = MyASController()
    asCtrler.RunMain()

