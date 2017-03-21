#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Prior functions module.

This module is an update of Suzanne Aigrain's prior module. See copyright below:

    Copyright (C) 2016  Suzanne Aigrain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additions to this modules:
    - add Jeffreys prior, Susana Barros, 28 Sep 2016
    - add Sine prior, Susana Barros, 28 Sep 2016
    - add Metaclass Metaclass_PriorFunction, Olivier Demangeon, 6 Feb. 2017
    - add properties and check_mandatoryargs, Olivier Demangeon, 6 Feb. 2017
    - minor updates to deal with lims=None, Olivier Demangeon, 6 Feb. 2017
    - add create_logpdf for speed improvement, Olivier Demangeon, 6 Feb. 2017

@TODO:
"""

from __future__ import division

import math as mt
import numpy as np
from numpy import pi, inf
from scipy.stats import reciprocal

from ....tools.metaclasses import MandatoryReadOnlyAttr


class Metaclass_PriorFunction(MandatoryReadOnlyAttr):

    @property
    def all_args(cls):
        """Return the name of the prior type."""
        return cls.mandatory_args + cls.extra_args

    def __new__(cls, classname, bases, classdict):
        classdict["all_args"] = property(cls.all_args)
        return super(Metaclass_PriorFunction, cls).__new__(cls, classname, bases, classdict)

    def __init__(cls, name, bases, attrs):
        super(Metaclass_PriorFunction, cls).__init__(name, bases, attrs)
        if cls.__name__ not in ["Core_Prior_Function", ]:
            missing_attrs = ["{}".format(attr) for attr in ["logpdf", ]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Prior_Function(object, metaclass=Metaclass_PriorFunction):
    """Docstring for Prior Prior function class."""

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args"]

    def __init__(self):
        super(Core_Prior_Function, self).__init__()
        # Make Prior_Function an abstract class
        if type(self) is Core_Prior_Function:
            raise NotImplementedError("Core_Prior_Function should not be instanciated!")

    def __call__(self, *args):
        return self.logpdf(*args)

    @classmethod
    def check_args(cls, kwargs_list):
        missing_mandatoryargs = ["{}".format(arg) for arg in cls.mandatory_args
                                 if arg not in kwargs_list]
        if len(missing_mandatoryargs) > 0:
            raise AttributeError("Prior function '{}' requires attribute(s) {}"
                                 "".format(cls.__name__, missing_mandatoryargs))
        unknown_args = ["{}".format(arg) for arg in kwargs_list
                        if arg not in cls.all_args]
        if len(unknown_args) > 0:
            raise AttributeError("Prior function '{}' doesn't recognise attribute(s) {}"
                                 "".format(cls.__name__, unknown_args))


class UniformPrior(Core_Prior_Function):

    __category__ = "uniform"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        self.vmin = vmin
        self.vmax = vmax
        self.C = 1. / (vmax - vmin)
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]

    def create_logpdf(self):
        lnC = mt.log(1. / (self.vmax - self.vmin))
        vmin = self.vmin
        vmax = self.vmax

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return lnC
            else:
                return -inf
        return logpdf

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.lnC,
                            -inf)
        else:
            if x >= self.vmin and x <= self.vmax:
                return self.lnC
            else:
                return -inf

    def ravs(self):
        return np.random.uniform(self.vmin, self.vmax)


class NormalPrior(Core_Prior_Function):

    __category__ = "normal"
    __mandatory_args__ = ["mu", "sigma"]
    __extra_args__ = ["lims"]

    def __init__(self, mu, sigma, lims=None):
        self.lims = np.array(lims) if lims is not None else np.array([-inf, inf])
        self.vmin, self.vmax = self.lims
        if self.vmin >= self.vmax:
            raise ValueError("lims should be a 2 element iterable where the first element is "
                             "strictly inferior to the second")
        self.mu = float(mu)
        self.sigma = float(sigma)
        self._f1 = 1. / mt.sqrt(2. * pi * sigma * sigma)
        self._lf1 = mt.log(self._f1)
        self._f2 = 1. / (2. * sigma * sigma)

    def create_logpdf(self):
        lf1 = mt.log(1. / mt.sqrt(2. * pi * self.sigma * self.sigma))
        f2 = 1. / (2. * self.sigma * self.sigma)
        vmin = self.vmin
        vmax = self.vmax
        mu = self.mu

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return lf1 - (x - mu) * (x - mu) * f2
            else:
                return -inf
        return logpdf

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self._lf1 - (x - self.mu)**2 * self._f2,
                            -inf)
        else:
            return self._lf1 - (x - self.mu)**2 * self._f2 if self.vmin < x < self.vmax else -inf

    def ravs(self):
        val = self.vmin
        while not((self.vmin < val) and (self.vmax > val)):
            val = np.random.normal(self.mu, self.sigma)
        return val


class LogNormPrior(Core_Prior_Function):

    __category__ = "lognormal"
    __mandatory_args__ = ["mu", "sigma"]
    __extra_args__ = ["lims"]

    def __init__(self, mu, sigma, lims=None):
        self.lims = np.array(lims) if lims is not None else np.array([0, inf])
        self.vmin, self.vmax = self.lims
        if self.vmin >= self.vmax:
            raise ValueError("lims should be a 2 element iterable where the first element is "
                             "strictly inferior to the second")
        self.mu = mu
        self.sigma = sigma
        self.C = -mt.log(sigma * mt.sqrt(2 * pi))
        self._B = 2 * sigma**2

    def create_logpdf(self):
        C = -mt.log(self.sigma * mt.sqrt(2 * pi))
        mu = self.mu
        B = 2 * self.sigma**2
        vmin = self.vmin
        vmax = self.vmax

        def logpdf(x):
            if x >= vmin and x <= vmax:
                lnx = mt.log(x)
                return -lnx + C - ((lnx * lnx - mu * lnx + mu * mu) / B)
            else:
                return -inf
        return logpdf

    def __logpdf_wcustargs(self, x, mu, C, B):
        lnx = mt.log(x)
        return -lnx + C - ((lnx * lnx - mu * lnx + mu * mu) / B)

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(self, x, self.mu, self.C, self.B),
                            -inf)
        else:
            if (x <= self.vmin) or (x > self.vmax):
                return -inf
            return self.__logpdf_wcustargs(self, x, self.mu, self.C, self.B)

    def ravs(self):
        val = self.vmin
        while not((self.vmin < val) and (self.vmax > val)):
            val = np.random.lognormal(self.mu, self.sigma)
        return val


class JeffreysPrior(Core_Prior_Function):

    __category__ = "jeffreys"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        self.vmin = vmin
        self.vmax = vmax
        self.C = vmax / vmin
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]

    def create_logpdf(self):
        vmin = self.vmin
        vmax = self.vmax
        lnC = self.lnC

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return -mt.log(x * lnC)
            else:
                return -inf
        return logpdf

    def __logpdf_wcustargs(self, x, lnC):
        -mt.log(x * lnC)

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(x, self.lnC),
                            -inf)
        if x >= self.vmin and x <= self.vmax:
            return self.__logpdf_wcustargs(x, self.lnC)
        else:
            return -inf

    def ravs(self):
        x1 = reciprocal(self.vmin, self.vmax)
        return x1.rvs()


class SinePrior(Core_Prior_Function):

    __category__ = "sine"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        if vmin < 0. or vmin > 180.:
            raise ValueError("vmin should between 0. and 180")
        if vmax < 0. or vmax > 180.:
            raise ValueError("vmin should between 0. and 180")
        self.vmin = vmin
        self.vmax = vmax
        self.C = 1. / (180 / pi * (np.cos(vmin * pi / 180.0) - np.cos(vmax * pi / 180.0)))
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]
        self.degtorad = pi / 180.0

    def create_logpdf(self):
        vmin = self.vmin
        vmax = self.vmax
        lnC = self.lnC
        degtorad = self.degtorad

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return mt.log(np.sin(x * degtorad)) + lnC
            else:
                return -inf
        return logpdf

    def __logpdf_wcustargs(self, x, lnC, degtorad):
        return mt.log(np.sin(x * degtorad)) + lnC

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(x, self.lnC, self.degtorad),
                            -inf)
        if x >= self.vmin and x <= self.vmax:
            return self.__logpdf_wcustargs(x, self.lnC, self.degtorad)
        else:
            return -inf

    # a random angle x has a probability density function = sin(x)
    def ravs(self):
        return np.random.uniform(self.vmin, self.vmax)
