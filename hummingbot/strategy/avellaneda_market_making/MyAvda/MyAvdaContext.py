

# import lines
from .MyMarketEvent import *
from dataclasses import dataclass


# avda core interface class
@dataclass
class MyAvdaContext:
	def InputEventTrade(self, ev: MyMETrade):
		pass

	def InputEventMidPrice(self, ev: MyMEMidPrice):
		pass

	def InputEventLastPrice(self, ev: MyMELastPrice):
		pass

	def InputEventBalance(self, ev: MyMEBalance):
		pass
#
