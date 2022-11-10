

from .MyAvdaContext import MyAvdaContext
from .MyAvdaContext import MyAvdaConfig
from .MyMarketEvent import MyProposal
from .MyMarketEvent import MyPriceSize
from .TrailingIndicators import MyInstantVolatility
from .TrailingIndicators import MyTradingIntensity
from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple, List, Optional
import logging


NaN = float("nan")
s_decimal_0 = Decimal(0)
s_decimal_zero = Decimal(0)
s_decimal_neg_one = Decimal(-1)
s_decimal_one = Decimal(1)


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

	_alpha: Decimal = None
	_kappa: Decimal = None

	_reservation_price: Decimal = s_decimal_zero
	_optimal_spread: Decimal = s_decimal_zero
	_optimal_ask: Decimal = s_decimal_zero
	_optimal_bid: Decimal = s_decimal_zero

	# public funcs
	def OnStart(self, timestamp: float):
		pass

	def OnUpdate(self, timestamp: float):
		self._current_timestamp = timestamp
		self.c_tick(timestamp)

	def OnStop(self, timestamp: float):
		pass

	# translated tool funs ################################################################
	def c_quantize_order_amount(self, trading_pair: str, amount: Decimal, price: Decimal = s_decimal_0) -> Decimal:
		"""
		Applies the trading rules to calculate the correct order amount for the market
		:param trading_pair: the token pair for which the order will be created
		:param amount: the intended amount for the order
		:param price: the intended price for the order
		:return: the quantized order amount after applying the trading rules
		"""
		# trading_rule = self._trading_rules[trading_pair]
		# quantized_amount: Decimal = super().quantize_order_amount(trading_pair, amount)

		if trading_pair != "BTC-USDT":
			raise Exception("Only support trading_pair=BTC-USDT")

		# BTC/USDT MinBTC =(0.00001)
		min_order_size: Decimal = Decimal(0.00001)
		# BTC/USDT MinUSDT=10
		min_notional_size: Decimal = Decimal(10)

		midPrice: Decimal = Decimal(self.ctx.GetMidPrice())

		quantized_amount: Decimal = amount

		# Check against min_order_size and min_notional_size. If not passing either check, return 0.
		if quantized_amount < min_order_size:
			return s_decimal_0

		if price == s_decimal_0:
			# current_price: Decimal = self.get_price(trading_pair, False)
			current_price: Decimal = midPrice
			notional_size = current_price * quantized_amount
		else:
			notional_size = price * quantized_amount

		# Add 1% as a safety factor in case the prices changed while making the order.
		# if notional_size < trading_rule.min_notional_size * Decimal("1.01"):
		if notional_size < min_notional_size * Decimal("1.01"):
			return s_decimal_0
		return quantized_amount

	def c_is_algorithm_ready(self) -> bool:
		volFull: bool = self.ctx.GetVolatility().is_sampling_buffer_full
		intFull: bool = self.ctx.GetIntensity().is_sampling_buffer_full
		return volFull and intFull

	def c_is_algorithm_changed(self) -> bool:
		volChanged: bool = self.ctx.GetVolatility().is_sampling_buffer_changed
		intChanged: bool = self.ctx.GetIntensity().is_sampling_buffer_changed
		return volChanged or intChanged

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

	def c_set_timers(self) -> None:
		next_cycle: float = self._current_timestamp + self.ctx.config.order_refresh_time
		if self._create_timestamp <= self._current_timestamp:
			self._create_timestamp = next_cycle
		if self._cancel_timestamp <= self._current_timestamp:
			self._cancel_timestamp = min(self._create_timestamp, next_cycle)

	def c_calculate_target_inventory(self) -> float:
		inventory_target_base: Decimal = Decimal(self.ctx.config.inventory_target_base_pct) / Decimal('100')

		price: float = self.ctx.GetMidPrice()
		base_asset_amount: float = self.ctx.GetBaseBalance()
		quote_asset_amount: float = self.ctx.GetQuoteBalance()
		# Base asset value in quote asset prices
		base_value: float = base_asset_amount * price
		# Total inventory value in quote asset prices
		inventory_value: float = base_value + quote_asset_amount

		# Target base asset value in quote asset prices
		target_inventory_value: float = inventory_value * float(inventory_target_base)
		# Target base asset amount
		target_inventory_amount: float = target_inventory_value / price
		# return market.c_quantize_order_amount(trading_pair, Decimal(str(target_inventory_amount)))
		target_inventory_amount = float(self.c_quantize_order_amount(self.ctx.config.trading_pair, Decimal(str(target_inventory_amount))))
		return target_inventory_amount

	def c_calculate_inventory(self) -> float:
		price: float = self.ctx.GetMidPrice()
		base_asset_amount: float = self.ctx.GetBaseBalance()
		quote_asset_amount: float = self.ctx.GetQuoteBalance()

		# Base asset value in quote asset prices
		base_value: float = base_asset_amount * price

		# Total inventory value in quote asset prices
		inventory_value_quote: float = base_value + quote_asset_amount

		# Total inventory value in base asset prices
		inventory_value_base: float = inventory_value_quote / price
		return inventory_value_base

	# Cancels active non-hanging orders if they are older than max age limit
	def c_cancel_active_orders_on_max_age_limit(self) -> None:
		pass

	def c_cancel_active_orders(self, proposal: MyProposal) -> None:
		if self._cancel_timestamp > self._current_timestamp:
			return
		if proposal is not None:
			pass
		self.c_set_timers()

	def c_calculate_reservation_price_and_optimal_spread(self) -> None:
		# Current mid price
		price: Decimal = Decimal(self.ctx.GetMidPrice())

		# The amount of stocks owned - q - has to be in relative units, not absolute, because changing the portfolio size shouldn't change the reservation price
		# The reservation price should concern itself only with the strategy performance, i.e. amount of stocks relative to the target
		inventory: Decimal = Decimal(str(self.c_calculate_inventory()))
		if inventory == 0:
			return

		#
		base_asset_amount: Decimal = Decimal(self.ctx.GetBaseBalance())
		q_target: Decimal = Decimal(str(self.c_calculate_target_inventory()))
		q: Decimal = (base_asset_amount - q_target) / inventory
		# Volatility has to be in absolute values (prices) because in calculation of reservation price it's not multiplied by the current price, therefore
		# it can't be a percentage. The result of the multiplication has to be an absolute price value because it's being subtracted from the current price
		vol: Decimal = Decimal(str(self.ctx.GetVolatility().current_value))

		gamma: Decimal = Decimal(self.ctx.config.risk_factor)
		if all((gamma, self._kappa)) and self._alpha != 0 and self._kappa > 0 and vol != 0:
			pass
		else:
			return
		# Avellaneda-Stoikov for an infinite timespan
		time_left_fraction: Decimal = Decimal(1)
		self._reservation_price = price - (q * gamma * vol * time_left_fraction)

		self._optimal_spread = gamma * vol * time_left_fraction
		self._optimal_spread += 2 * Decimal(1 + gamma / self._kappa).ln() / gamma

		min_spread: Decimal = price / Decimal(100) * Decimal(str(self.ctx.config.min_spread))

		max_limit_bid: Decimal = price - min_spread / 2
		min_limit_ask: Decimal = price + min_spread / 2

		self._optimal_ask = max(self._reservation_price + self._optimal_spread / 2, min_limit_ask)
		self._optimal_bid = min(self._reservation_price - self._optimal_spread / 2, max_limit_bid)

	def c_create_base_proposal(self) -> MyProposal:
		buySize: Decimal = self.c_quantize_order_amount(self.ctx.config.trading_pair, Decimal(self.ctx.config.order_amount))
		sellSize: Decimal = buySize
		buyOrder: MyPriceSize = MyPriceSize(self._optimal_bid, buySize)
		sellOrder: MyPriceSize = MyPriceSize(self._optimal_ask, sellSize)

		listBuy: List[MyPriceSize] = [buyOrder, ]
		listSell: List[MyPriceSize] = [sellOrder, ]
		proposal: MyProposal = MyProposal(listBuy, listSell)
		return proposal

	def c_apply_order_amount_eta_transformation(self, proposal: MyProposal) -> None:
		inventory: Decimal = Decimal(str(self.c_calculate_inventory()))
		if inventory == 0:
			return

		base_asset_amount: Decimal = Decimal(self.ctx.GetBaseBalance())
		q_target: Decimal = Decimal(str(self.c_calculate_target_inventory()))
		q: Decimal = (base_asset_amount - q_target) / inventory

		tradingPair: str = self.ctx.config.trading_pair
		eta: Decimal = Decimal(self.ctx.config.order_amount_shape_factor)
		# buys
		if len(proposal.buys) > 0:
			if q > 0:
				for i, proposed in enumerate(proposal.buys):
					buySize: Decimal = proposal.buys[i].size * Decimal.exp(-eta * q)
					proposal.buys[i].size = self.c_quantize_order_amount(tradingPair, buySize)
				# end for
				proposal.buys = [o for o in proposal.buys if o.size > 0]
		# sells
		if len(proposal.sells) > 0:
			if q < 0:
				for i, proposed in enumerate(proposal.sells):
					sellSize: Decimal = proposal.sells[i].size * Decimal.exp(eta * q)
					proposal.sells[i].size = self.c_quantize_order_amount(tradingPair, sellSize)
				# end for
				proposal.sells = [o for o in proposal.sells if o.size > 0]
		# end func

	def c_apply_order_price_modifiers(self, proposal: MyProposal) -> None:
		conf: MyAvdaConfig = self.ctx.config
		if conf.order_optimization_enabled:
			pass  # not support
		if conf.add_transaction_costs:
			pass  # not support

	def c_apply_budget_constraint(self, proposal: MyProposal) -> None:
		pass  # not support

	# test create order ok
	def c_to_create_orders(self, proposal: Optional[MyProposal]) -> bool:
		if proposal is None:
			return False

		timeOK: bool = self._create_timestamp < self._current_timestamp
		return timeOK

	# notify and reset timers if created
	def c_execute_orders_proposal(self, proposal: MyProposal) -> None:
		orders_created: bool = False
		if orders_created:
			self.c_set_timers()

	# translated ends funs ################################################################

	# for c_did_complete_order
	def MyLimitOrderComplete(self):
		# next create order time
		self._create_timestamp = self._current_timestamp + self.ctx.config.filled_order_delay
		# cancel time
		self._cancel_timestamp = min(self._cancel_timestamp, self._create_timestamp)

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
		proposal: Optional[MyProposal] = None
		# Trading is allowed
		if self._create_timestamp <= self._current_timestamp:
			# 1. Calculate reservation price and optimal spread from gamma, alpha, kappa and volatility
			self.c_calculate_reservation_price_and_optimal_spread()
			# 2. Check if calculated prices make sense
			if self._optimal_bid > 0 and self._optimal_ask > 0:
				# 3. Create base order proposals
				proposal = self.c_create_base_proposal()
				# 4. Apply functions that modify orders amount
				self.c_apply_order_amount_eta_transformation(proposal)
				# 5. Apply functions that modify orders price
				self.c_apply_order_price_modifiers(proposal)
				# 6. Apply budget constraint, i.e. can't buy/sell more than what you have.
				self.c_apply_budget_constraint(proposal)

				self.c_cancel_active_orders(proposal)

		# end Trading if
		if self.c_to_create_orders(proposal):
			self.c_execute_orders_proposal(proposal)
		# for warning
		test: bool = False
		if test:
			print(timestamp)

#
