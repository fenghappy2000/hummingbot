

from .MyAvdaContext import MyAvdaContext
from dataclasses import dataclass
import logging


@dataclass
class MyAvdaImpl:
	# logger
	_logger: logging.Logger = logging.getLogger("MyAvdaImpl")

	ctx: MyAvdaContext = None

	def OnStart(self, timestamp: float):
		pass

	def OnUpdate(self, timestamp: float):
		pass

	def OnStop(self, timestamp: float):
		pass
#
