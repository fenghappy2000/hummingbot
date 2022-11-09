

from abc import ABC, abstractmethod

import numpy as np

from ..MyRingBuffer import MyRingBuffer


class MyBaseTrailingIndicator(ABC):

    def __init__(self, sampling_length: int = 30, processing_length: int = 15):
        self._sampling_buffer = MyRingBuffer(sampling_length)
        self._processing_buffer = MyRingBuffer(processing_length)
        self._samples_length = 0

    def add_sample(self, value: float):
        self._sampling_buffer.add_value(value)
        indicator_value = self._indicator_calculation()
        self._processing_buffer.add_value(indicator_value)

    @abstractmethod
    def _indicator_calculation(self) -> float:
        raise NotImplementedError

    def _processing_calculation(self) -> float:
        """
        Processing of the processing buffer to return final value.
        Default behavior is buffer average
        """
        return np.mean(self._processing_buffer.get_as_numpy_array())

    @property
    def current_value(self) -> float:
        return self._processing_calculation()

    @property
    def is_sampling_buffer_full(self) -> bool:
        return self._sampling_buffer.is_full

    @property
    def is_processing_buffer_full(self) -> bool:
        return self._processing_buffer.is_full

    @property
    def is_sampling_buffer_changed(self) -> bool:
        buffer_len = len(self._sampling_buffer.get_as_numpy_array())
        is_changed = self._samples_length != buffer_len
        self._samples_length = buffer_len
        return is_changed

    @property
    def sampling_length(self) -> int:
        return self._sampling_buffer.length

    @sampling_length.setter
    def sampling_length(self, value):
        self._sampling_buffer.length = value

    @property
    def processing_length(self) -> int:
        return self._processing_buffer.length

    @processing_length.setter
    def processing_length(self, value):
        self._processing_buffer.length = value
#
