#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
chain interperter module.

The objective of this module is to provide the ChainInterpret class which is a chain object which
includes the knowledge of which chain correspond to which parameter name.
"""
import numpy as np
from collections import Iterable


class ChainsInterpret(np.ndarray):

    __err_shapeinput__ = "Shape of input_array should be <= 3."
    __err_dimarrlparam__ = "Last dim of input_array have the same dimension than l_param_names."

    def __new__(cls, input_array, param_names):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        if len(input_array.shape) > 3:
            raise ValueError(cls.__err_shapeinput__)
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.__paramname_idx = dict((n, i) for i, n in enumerate(param_names))
        if len(param_names) != obj.shape[-1]:
            raise ValueError(cls.__err_dimarrlparam__)
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.__paramname_idx = getattr(obj, 'paramname_idx', None)

    def __getitem__(self, indexing):
        if isinstance(indexing, str):
            idx = self.paramname_idx[indexing]
            indexing = (..., idx)
        if isinstance(indexing, tuple):
            if isinstance(indexing[-1], str):
                ll = list(indexing[:-1])
                ll.append(self.paramname_idx[indexing[-1]])
                indexing = list(ll)
            elif isinstance(indexing[-1], Iterable):
                if isinstance(indexing[-1][0], str):
                    ll = list(indexing[:-1])
                    ll.append([self.paramname_idx[parname] for parname in indexing[-1]])
                    indexing = list(ll)
        return super(ChainsInterpret, self).__getitem__(tuple(indexing))

    @property
    def paramname_idx(self):
        """Return the list of parameters names."""
        return self.__paramname_idx

    @property
    def flatchain(self):
        """
        A shortcut for accessing chain flattened along the zeroth (walker)
        axis.
        """
        s = self.shape
        return self.reshape(s[0] * s[1], s[2])

    @property
    def dim(self):
        """Return the number of parameters."""
        if len(self.shape) == 3:
            return self.shape[-1]
        else:
            return 1
