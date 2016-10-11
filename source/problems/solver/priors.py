""" Module defining priors.

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

    add Jeffreys prior Susana Barros 28 Sep 2016

    @TODO: Implement a sine prior for the inclination
"""

from __future__ import division

import math as mt
import numpy as np
from numpy import array, asarray, log, pi, inf

class Prior(object):
    def __init__(self):
        raise NotImplementedError()
    def logpdf(self, x):
        raise NotImplementedError()
    def __call__(self, x):
        return self.logpdf(x)


class UniformPrior(Prior):
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.C = 1./(vmax-vmin)
        self.lnC = mt.log(self.C)
        self.lims = [vmin,vmax]

    def logpdf(self, x):
        if x >= self.vmin and x <= self.vmax:
            return self.lnC
        else:
            return -inf

    def ravs(self):
        return np.random.uniform(self.vmin, self.vmax)


class NormalPrior(Prior):
    def __init__(self, mu, sigma, lims=None):
        self.lims = np.array(lims)
        self.vmin, self.vmax = lims
        self.mu    = float(mu)
        self.sigma = float(sigma)
        self._f1 = 1./ mt.sqrt(2.*pi*sigma*sigma)
        self._lf1 = mt.log(self._f1)
        self._f2 = 1./ (2.*sigma*sigma)

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),  self._lf1 - (x-self.mu)**2 * self._f2, -inf)
        else:
            return self._lf1 -(x-self.mu)**2*self._f2 if self.vmin < x < self.vmax else -inf

    def ravs(self):
        return np.random.normal(self.mu, self.sigma)



class LogNormPrior(Prior):
    def __init__(self, mu, sigma, lims=None):
        self.mu = mu
        self.sigma = sigma
        self.C = -mt.log(sigma*mt.sqrt(2*pi))
        self.lims = lims if lims is not None else [0,inf]
        self._B = 2*sigma**2

    def logpdf(self, x):
        if (x <= self.lims[0]) or (x > self.lims[1]):
            return -inf
        mu = self.mu
        lnx = mt.log(x)
        return -lnx + self.C - ((lnx*lnx - mu*lnx + mu*mu)/self._B)

    def ravs(self):
        return np.random.lognormal(self.mu, self.sigma)




class JeffreysPrior(Prior):
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.C = vmax/vmin
        self.lnC = mt.log(self.C)
        self.lims = [vmin,vmax]

    def logpdf(self, x):
        if x >= self.vmin and x <= self.vmax:
            return np.log(1) - mt.log(x  *  self.lnC)
        else:
            return -inf

    def ravs(self):
        from scipy import stats
        x1  =   stats.reciprocal(self.vmin, self.vmax)
        return x1.rvs()


class SinePrior(Prior):
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.C =  1./( 180/pi*(np.cos(vmin*pi/180.0) - np.cos(vmax*pi/180.0)) )
        self.lnC = mt.log(self.C)
        self.lims = [vmin,vmax]

    def logpdf(self, x):
        if x >= self.vmin and x <= self.vmax:
            return mt.log( np.sin(x * pi/180.0) ) + self.lnC
        else:
            return -inf

    # a random angle x has a probability density function = sin(x)
    def ravs(self):
        return np.random.uniform(self.vmin, self.vmax)
