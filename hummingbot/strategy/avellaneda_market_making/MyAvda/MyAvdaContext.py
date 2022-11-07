

# import lines
from .MyMarketEvent import *
# from decimal import Decimal
from dataclasses import dataclass
import logging


# avda config, => AvellanedaMarketMakingConfigMap
@dataclass
class MyAvdaConfig:
	# execution_timeframe_mode = InfiniteModel
	order_amount: float = 0.002  # BTC(0.002)/0
	order_optimization_enabled: bool = True  # True/True
	risk_factor: float = 0.8  # 0.8/1.0
	order_amount_shape_factor: float = 0  # 0/0
	min_spread: float = 0  # 0/0
	order_refresh_time: float = 30  # 30/60
	max_order_age: float = 1800.  # 1800/1800
	order_refresh_tolerance_pct: float = 0  # 0/0
	filled_order_delay: float = 5  # 5/60
	inventory_target_base_pct: float = 50  # 50/50
	add_transaction_costs: bool = False  # False/False
	volatility_buffer_size: int = 60  # 60/200
	trading_intensity_buffer_size: int = 60  # 60/200
	order_level_mode: int = 1  # 1/1
	level_distances: float = 0  # 0/0
	# order_override = None
	# hanging_orders_mode = IgnoreHangingOrdersModel
	should_wait_order_cancel_confirmation: bool = True  # True/True


# avda core interface class
@dataclass
class MyAvdaContext:
	# logger
	_logger: logging.Logger = logging.getLogger(__name__)

	def OnStart(self, timestamp: float):
		self._logger.warning("fengjs: MyAvdaContext.OnStart() ts[{}]".format(timestamp))

	def OnUpdate(self, timestamp: float):
		self._logger.warning("fengjs: MyAvdaContext.OnUpdate() ts[{}]".format(timestamp))

	def OnStop(self, timestamp: float):
		self._logger.warning("fengjs: MyAvdaContext.OnStop() ts[{}]".format(timestamp))

	def InputEventTrade(self, ev: MyMETrade):
		self._logger.warning("fengjs: MyAvdaContext.InputEventTrade()")

	def InputEventMidPrice(self, ev: MyMEMidPrice):
		self._logger.warning("fengjs: MyAvdaContext.InputEventMidPrice()")

	def InputEventLastPrice(self, ev: MyMELastPrice):
		self._logger.warning("fengjs: MyAvdaContext.InputEventLastPrice()")

	def InputEventBalance(self, ev: MyMEBalance):
		self._logger.warning("fengjs: MyAvdaContext.InputEventBalance()")
#
