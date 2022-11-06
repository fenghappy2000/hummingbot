

# import lines
from .MyAvdaContext import MyAvdaContext
from dataclasses import dataclass


# simulator in humbot frwk, for data check with avstg
@dataclass
class MyHBSimulator:
    _AvdaCtx: MyAvdaContext = MyAvdaContext()


#
