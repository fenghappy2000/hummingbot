

from .MyBaseTrailingIndicator import MyBaseTrailingIndicator
import numpy as np


class MyInstantVolatilityIndicator(MyBaseTrailingIndicator):
    def __init__(self, sampling_length: int = 30, processing_length: int = 15):
        import logging
        logging.getLogger().warning("fengjs: MyInstantVolatility: s[{}], p[{}]".format(sampling_length, processing_length))
        super().__init__(sampling_length, processing_length)

    def _indicator_calculation(self) -> float:
        # The standard deviation should be calculated between ticks and not with a mean of the whole buffer
        # Otherwise if the asset is trending, changing the length of the buffer would result in a greater volatility as more ticks would be further away from the mean
        # which is a nonsense result. If volatility of the underlying doesn't change in fact, changing the length of the buffer shouldn't change the result.
        np_sampling_buffer = self._sampling_buffer.get_as_numpy_array()
        vol = np.sqrt(np.sum(np.square(np.diff(np_sampling_buffer))) / np_sampling_buffer.size)
        return vol

    def _processing_calculation(self) -> float:
        # Only the last calculated volatlity, not an average of multiple past volatilities
        return self._processing_buffer.get_last_value()
#
