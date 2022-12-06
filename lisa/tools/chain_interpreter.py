#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
chain interperter module.

The objective of this module is to provide the ChainInterpret class which is a chain object which
includes the knowledge of which chain correspond to which parameter name.
"""
import numpy as np
from collections.abc import Iterable
from collections import Counter


class ChainsInterpret(np.ndarray):

    __err_shapeinput__ = "Shape of input_array should be <= 3."
    __err_dimarrlparam__ = "Last dim of input_array must have the same dimension than l_param_names."

    def __new__(cls, input_array, param_names):
        # First, check if the size of the last dimension of input_array match the length of param_names
        assert input_array.shape[-1] == len(param_names), cls.__err_dimarrlparam__
        # Check if the same param_name appears several, because it would break the class
        cc = Counter(param_names)
        duplicated_p_names = {}
        for p_name, cnt in cc.items():
            if cnt > 1:
                duplicated_p_names[p_name] = cnt
        assert len(duplicated_p_names) == 0, f"There is repeated parameter names in param_names: {duplicated_p_names}"
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        if len(input_array.shape) > 3:
            raise ValueError(cls.__err_shapeinput__)
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj._paramname_idx = dict((n, i) for i, n in enumerate(param_names))
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self._paramname_idx = getattr(obj, 'paramname_idx', None)

    def __getitem__(self, indexing):
        new_param_idx = None
        if isinstance(indexing, str):
            idx = self.paramname_idx[indexing]
            indexing = (..., idx)
            new_param_idx = {indexing: idx}
        if isinstance(indexing, tuple):
            if isinstance(indexing[-1], str):
                ll = list(indexing[:-1])
                ll.append(self.paramname_idx[indexing[-1]])
                new_param_idx = {indexing[-1]: self.paramname_idx[indexing[-1]]}
                indexing = tuple(ll)
            elif isinstance(indexing[-1], Iterable):
                if isinstance(indexing[-1][0], str):
                    ll = list(indexing[:-1])
                    ll.append([self.paramname_idx[parname] for parname in indexing[-1]])
                    new_param_idx = {parname: self.paramname_idx[parname] for parname in indexing[-1]}
                    indexing = tuple(ll)
        # return super(ChainsInterpret, self).__getitem__(indexing)
        if new_param_idx is None:
            return super(ChainsInterpret, self).__getitem__(indexing)
        else:
            res = super(ChainsInterpret, self).__getitem__(indexing).copy()
            res._paramname_idx = new_param_idx
            return res

    @property
    def paramname_idx(self):
        """Return the list of parameters names."""
        return self._paramname_idx

    @property
    def param_names(self):
        """Return the list of parameters names."""
        return list(self._paramname_idx.keys())

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
