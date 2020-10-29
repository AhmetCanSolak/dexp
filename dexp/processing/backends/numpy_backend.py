from abc import abstractmethod
from typing import Any

import numpy
import scipy

from dexp.processing.backends.backend import Backend


class NumpyBackend(Backend):

    def __init__(self):
        """ Instanciates a Numpy-based Image Processing backend

        """

    def close(self):
        #Nothing to do
        pass

    def to_numpy(self, array, dtype=None) -> numpy.ndarray:
        if dtype:
            array = array.astype(dtype, copy=False)
        return array

    def to_backend(self, array, dtype=None) -> Any:
        if dtype:
            array = array.astype(dtype, copy=False)
        return array

    def get_xp_module(self, array) -> Any:
        return numpy

    def get_sp_module(self, array) -> Any:
        return scipy














