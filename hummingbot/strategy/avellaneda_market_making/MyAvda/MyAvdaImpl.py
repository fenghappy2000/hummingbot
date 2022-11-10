

from .MyAvdaContext import MyAvdaContext
from .TrailingIndicators import MyInstantVolatility
from .TrailingIndicators import MyTradingIntensity
from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple
import logging


@dataclass
class MyAvdaImpl:
	# logger
	_logger: logging.Logger = logging.getLogger("MyAvdaImpl")

	ctx: MyAvdaContext = None

	_current_timestamp: float = 0  # TimeIterator.current_timestamp

	_last_sampling_timestamp: float = 0
	_cancel_timestamp: float = 0
	_create_timestamp: float = 0
	_last_timestamp: float = 0
	_ticks_to_be_ready: int = -1

	_alpha: object = None
	_kappa: object = None

	# public funcs
	def OnStart(self, timestamp: float):
		pass

	def OnUpdate(self, timestamp: float):
		self._current_timestamp = timestamp
		self.c_tick(timestamp)

	def OnStop(self, timestamp: float):
		pass

	def c_is_algorithm_ready(self) -> bool:
		volFull: bool = self.ctx.GetVolatility().is_sampling_buffer_full
		intFull: bool = self.ctx.GetIntensity().is_sampling_buffer_full
		return volFull and intFull

	def c_is_algorithm_changed(self) -> bool:
		volChanged: bool = self.ctx.GetVolatility().is_sampling_buffer_changed
		intChanged: bool = self.ctx.GetIntensity().is_sampling_buffer_changed
		return volChanged or intChanged

	# called every tick(default 1 second)
	def c_tick(self, timestamp: float):
		try:
			# collect market info
			self.c_collect_market_variables(timestamp)

			algReady: bool = self.c_is_algorithm_ready()
			if algReady:
				if self._create_timestamp <= self._current_timestamp:
					# Measure order book liquidity
					self.c_measure_order_book_liquidity()

				# self._hanging_orders_tracker.process_tick()
				self.c_cancel_active_orders_on_max_age_limit()

				self.process_tick(timestamp)
			else:
				algChanged: bool = self.c_is_algorithm_changed()
				if algChanged:
					self._ticks_to_be_ready -= 1
		finally:
			self._last_timestamp = timestamp

	# process
	def process_tick(self, timestamp: float):
		pass

	# translate from pyx
	def c_collect_market_variables(self, timestamp: float):
		midPrice: float = self.ctx.GetMidPrice()

		self._last_sampling_timestamp = timestamp

		avgVol: MyInstantVolatility = self.ctx.GetVolatility()
		tradeInt: MyTradingIntensity = self.ctx.GetIntensity()

		avgVol.add_sample(midPrice)
		tradeInt.calculate(timestamp)

	def c_measure_order_book_liquidity(self) -> None:
		tradeInt: MyTradingIntensity = self.ctx.GetIntensity()
		akPair: Tuple[float, float] = tradeInt.current_value
		self._alpha = Decimal(akPair[0])
		self._kappa = Decimal(akPair[1])

	def c_set_timers(self):
		next_cycle: float = self._current_timestamp + self.ctx.config.order_refresh_time
		if self._create_timestamp <= self._current_timestamp:
			self._create_timestamp = next_cycle
		if self._cancel_timestamp <= self._current_timestamp:
			self._cancel_timestamp = min(self._create_timestamp, next_cycle)

	# Cancels active non-hanging orders if they are older than max age limit
	def c_cancel_active_orders_on_max_age_limit(self):
		pass

	def c_cancel_active_orders(self):
		if self._cancel_timestamp > self._current_timestamp:
			return
		self.c_set_timers()

	# for c_did_complete_order
	def MyLimitOrderComplete(self):
		# next create order time
		self._create_timestamp = self._current_timestamp + self.ctx.config.filled_order_delay
		# cancel time
		self._cancel_timestamp = min(self._cancel_timestamp, self._create_timestamp)
#
