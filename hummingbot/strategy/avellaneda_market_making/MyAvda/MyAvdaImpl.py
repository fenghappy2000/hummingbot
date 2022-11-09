

from .MyAvdaContext import MyAvdaContext
from .TrailingIndicators import MyInstantVolatility
from .TrailingIndicators import MyTradingIntensity
from dataclasses import dataclass
import logging


@dataclass
class MyAvdaImpl:
	# logger
	_logger: logging.Logger = logging.getLogger("MyAvdaImpl")

	ctx: MyAvdaContext = None

	_last_sampling_timestamp: float = 0

	def OnStart(self, timestamp: float):
		pass

	def OnUpdate(self, timestamp: float):
		self.c_tick(timestamp)

	def OnStop(self, timestamp: float):
		pass

	def c_is_algorithm_ready(self) -> bool:
		volFull: bool = self.ctx.GetVolatility().is_sampling_buffer_full
		intFull: bool = self.ctx.GetIntensity().is_sampling_buffer_full
		return volFull and intFull

	def c_tick(self, timestamp: float):
		# collect market info
		self.c_collect_market_variables(timestamp)

		algReady: bool = self.c_is_algorithm_ready()
		if algReady:
			pass
		else:
			pass

	def c_collect_market_variables(self, timestamp: float):
		midPrice: float = self.ctx.GetMidPrice()

		self._last_sampling_timestamp = timestamp

		avgVol: MyInstantVolatility = self.ctx.GetVolatility()
		tradeInt: MyTradingIntensity = self.ctx.GetIntensity()

		avgVol.add_sample(midPrice)
		tradeInt.calculate(timestamp)
#
