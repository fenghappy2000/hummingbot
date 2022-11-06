

# import lines
from .MyAvdaContext import MyAvdaContext
from dataclasses import dataclass


# simulator in humbot frwk, for data check with avstg
@dataclass
class MyHBSimulator:
    _AvdaCtx: MyAvdaContext = MyAvdaContext()

    def OnStart(self, timestamp: float):
        self._AvdaCtx.OnStart(timestamp)
        pass

    def OnUpdate(self, timestamp: float):
        self._AvdaCtx.OnUpdate(timestamp)
        pass

    def OnStop(self, timestamp: float):
        self._AvdaCtx.OnStop(timestamp)
        pass
#
