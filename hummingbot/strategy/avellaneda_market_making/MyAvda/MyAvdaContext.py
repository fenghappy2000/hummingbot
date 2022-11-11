

# import lines
from .MyMarketEvent import *
# from decimal import Decimal
from dataclasses import dataclass
import logging

from .TrailingIndicators.MyInstantVolatility import MyInstantVolatilityIndicator
from .TrailingIndicators.MyTradingIntensity import MyTradingIntensityIndicator

from .MyAvdaImpl import MyAvdaImpl


# avda config, => AvellanedaMarketMakingConfigMap
@dataclass
class MyAvdaConfig:
	# execution_timeframe_mode = InfiniteModel
	trading_pair: str = "BTC-USDT"
	order_amount: float = 0.002  # BTC(0.002)/0
	order_optimization_enabled: bool = True  # True/True
	risk_factor: float = 0.8  # 0.8/1.0
	order_amount_shape_factor: float = 0  # 0/0
	min_spread: float = 0  # 0/0
	order_refresh_time: float = 5  # 30/60
	max_order_age: float = 1800.  # 1800/1800
	order_refresh_tolerance_pct: float = 0  # 0/0
	filled_order_delay: float = 0.1  # 0.1/60
	inventory_target_base_pct: float = 50  # 50/50
	add_transaction_costs: bool = False  # False/False
	volatility_buffer_size: int = 30  # 60/200
	trading_intensity_buffer_size: int = 30  # 60/200
	order_level_mode: int = 1  # 1/1
	level_distances: float = 0  # 0/0
	# order_override = None
	# hanging_orders_mode = IgnoreHangingOrdersModel
	should_wait_order_cancel_confirmation: bool = True  # True/True


# avda core interface class
@dataclass
class MyAvdaContext:
	# logger
	_logger: logging.Logger = logging.getLogger()

	# config
	config: MyAvdaConfig = MyAvdaConfig()

	# private data for market
	_MidPrice: float = 0
	_LastPrice: float = 0
	_BaseBalance: float = 0
	_QuoteBalance: float = 0

	# calc props
	_AvgVolatility: MyInstantVolatilityIndicator = None
	_TradingIntensity: MyTradingIntensityIndicator = None

	# implement
	_AvdaImpl: MyAvdaImpl = None

	# public funcs
	def OnStart(self, timestamp: float):
		self._logger.setLevel(logging.DEBUG)

		self._logger.warning("fengjs: MyAvdaContext.OnStart() ts[{}]".format(timestamp))
		conf: MyAvdaConfig = self.config

		self._AvgVolatility = MyInstantVolatilityIndicator(sampling_length=conf.volatility_buffer_size)
		self._TradingIntensity = MyTradingIntensityIndicator(sampling_length=conf.trading_intensity_buffer_size)
		self._TradingIntensity.ctx = self

		self._AvdaImpl = MyAvdaImpl()
		self._AvdaImpl.ctx = self

		# call impl start
		self._AvdaImpl.OnStart(timestamp)

	def OnUpdate(self, timestamp: float):
		logIt: bool = False
		if logIt:
			line: str = "fengjs: MyAvdaContext.OnUpdate() ts[{}], M[{}], L[{}], B[{}], Q[{}]".format(
				timestamp, self._MidPrice, self._LastPrice, self._BaseBalance, self._QuoteBalance)
			self._logger.warning(line)

		# call impl update
		self._AvdaImpl.OnUpdate(timestamp)

	def OnStop(self, timestamp: float):
		self._logger.warning("fengjs: MyAvdaContext.OnStop() ts[{}]".format(timestamp))

		# call impl stop
		self._AvdaImpl.OnStop(timestamp)

	# trade event
	def InputEventTrade(self, ev: MyMETrade):
		line: str = "fengjs: MyAvdaContext.InputEventTrade(pair:{}, type:{}, tid:{}, uid:{}, ts:{}, prc:{}, amt:{})".format(
			ev.trading_pair, ev.trade_type, ev.trade_id, ev.update_id, ev.timestamp, ev.price, ev.amount)
		self._logger.warning(line)
		self._TradingIntensity.register_trade(ev)

	# mid price
	def GetMidPrice(self): return self._MidPrice

	def SetMidPrice(self, price: float):
		# self._logger.warning("fengjs: MyAvdaContext.SetMidPrice({})".format(price))
		self._MidPrice = price

	# last price
	def SetLastPrice(self, price: float):
		# self._logger.warning("fengjs: MyAvdaContext.SetLastPrice({})".format(price))
		self._LastPrice = price

	# btc
	def GetBaseBalance(self): return self._BaseBalance

	def SetBaseBalance(self, balance: float):
		# self._logger.warning("fengjs: MyAvdaContext.SetBaseBalance({})".format(balance))
		self._BaseBalance = balance

	# usdt
	def GetQuoteBalance(self): return self._QuoteBalance

	def SetQuoteBalance(self, balance: float):
		# self._logger.warning("fengjs: MyAvdaContext.SetQuoteBalance({})".format(balance))
		self._QuoteBalance = balance

	# private functions #################################################################################
	def GetVolatility(self) -> MyInstantVolatilityIndicator: return self._AvgVolatility

	def GetIntensity(self) -> MyTradingIntensityIndicator: return self._TradingIntensity
#
