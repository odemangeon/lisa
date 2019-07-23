#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Location and scale estimators module.

@package dr_tools.stats.robust_moment
@ingroup robust_moment

@brief librairie of function to compute robust moments.
@details Module which defines robust estimates of classical statistics location and scale.

@file
@author Olivier Demangeon
@date July 06, 2016
@version 5.2 06/07/2016 ODE # First released version
@todo: Unit tests of mad and estimator_loc_scale
"""

from numpy import sort, median, where, sqrt, pi, arange, transpose, prod
from numpy import sum as npsum
import statsmodels.api as sm

## Estimator of location and scale with LeastSquares norm
estimator_LeastSquares = sm.robust.Huber(norm=sm.robust.norms.LeastSquares())

## Estimator of location and scale with HuberT norm
estimator_HuberT = sm.robust.Huber(norm=sm.robust.norms.HuberT())

## Estimator of location and scale with RamsayE norm
estimator_RamsayE = sm.robust.Huber(norm=sm.robust.norms.RamsayE())

## Estimator of location and scale with Andrew Wave norm
estimator_AndrewWave = sm.robust.Huber(norm=sm.robust.norms.AndrewWave())

## Estimator of location and scale with TrimmedMean norm
estimator_TrimmedMean = sm.robust.Huber(norm=sm.robust.norms.TrimmedMean())

## Estimator of location and scale with Hampel norm
estimator_Hampel = sm.robust.Huber(norm=sm.robust.norms.Hampel())

## Estimator of location and scale with TukeyBiweight norm
estimator_TukeyBiweight = sm.robust.Huber(norm=sm.robust.norms.TukeyBiweight())

## Dictionaries which associate the string of estimator and the estimator
_estimators_dico = {"LeastSquares": estimator_LeastSquares,
                    "HuberT": estimator_HuberT,
                    "RamsayE": estimator_RamsayE,
                    "AndrewWave": estimator_AndrewWave,
                    "TrimmedMean": estimator_TrimmedMean,
                    "Hampel": estimator_Hampel,
                    "TukeyBiweight": estimator_TukeyBiweight}


def estimator_loc_scale(data, norm=None, **kwargs):
    """
    Estimate location and scale.

    Estimate location and scale and allows to select the norm to be used.

    ----

    @author Olivier Demangeon LAM

    Arguments:
        data : iterable,
            data on which to compute the location and scale
        norm : string, optional (default: TukeyBiweight),
            Norm to use to compute the location and scale

    Keyword arguments:
        kwargs : keyword argument to be passed to the estimator

    Returns:
        results : tuple of 2 arrays, the first one give the location the second one the scale

    Raises:
        ValueError: Norm argument should be in ["LeastSquares", "HuberT", "RamsayE", "AndrewWave",
                    "TrimmedMean", "Hampel", "TukeyBiweight"]
    """
    if norm in _estimators_dico.keys():
        return _estimators_dico[norm](data)
    else:
        raise ValueError("Norm argument should be in {}".format(_estimators_dico.keys()))


def mad(data, axis=None, **kwargs):
    """
    Median absolute deviation.

    ----

    @author Olivier Demangeon LAM

    Arguments:
        data : numpy.ndarray
            data on which to compute the mad
        axis : None or int
            if None flatten the array before computing the mad otherwise apply on specified axis

    Keyword arguments:
        center : float, optional
            center value to use
        norm : norm to use to compute the center, optional
            should be in statsmodels.api.robust.norms

    Returns:
        result : value of the mad
    """
    if axis is None:
        return sm.robust.mad(data.flatten(), **kwargs)
    else:
        return sm.robust.mad(data, **kwargs)


def rob_mom(data, center=None, moment=None):
    """
    Calculate robust estimates of the central location and spread of a distribution.

    It's based on Tuckey's biweight. For an uncontaminated distribution, these are identical to
    the mean and the standard deviation.

    The choices of the estimators are based on extensive simulations by Beers et al. (1990).
    Use the biweight centre location to estimate the mean in as many cases as possible. Where it
    fails, use the median instead.
    For N < 10, use the gapper algorithm to estimate the spread.
    For N > 10 use the median absolute deviation (MAD) as the initial estimate of the centre
    location, then weight points using Tukey's Biweight to obtain an estimate of the spread.

    References:
    -----------
    "Understanding Robust and Exploratory Data Analysis," by Hoaglin, Mosteller and Tukey,
    John Wiley & Sons, 1983.
    Beers, Flynn & Gebhardt, Astronomical Journal, vol. 100, 32, 1990.

    Syntax:
    -------
    centre, spread = rob_mom(data, center=None)

    Parameters:
    -----------
    data : ndarray
        Vector with dataset for which the dispersion (and center) is to be calculated.
    center : float, optional
        If set, the spread is calculated w.r.t. zero rather than the central value of the vector.
        If data is a vector of residuals, this should be set to zero.
    moment : int, optional
        if None return the two moment. If 1 or 2 return the 1st (average) or 2nd (std) moment
        respectively.

    Returns:
    --------
    centre : float
        the central value of data. In case of failure, returns zero value.
    spread : float
        the spread of data. In case of failure, returns zero value.

    Revision history"
    -----------------
    Based on the IDL routines ROBUST_SIGMA and MED by H. Freudenreich and the
    Fortran 77 routine ROBUST.FOR by R.H. den Hartog, Leiden Observatory, 3/92.

    Examples:
    ---------
        >>> data = np.random.rand(3,4)
        >>> centre, spread = rob_mom(data)
    """
    # Set some useful values
    eps = 1.0E-20
    n = data.size

    # xi = np.where(zero != 0) # Non
    # zi = np.array(xi) #
    # test = np.any(zi)

    # If center is provided, take it as cen, otherwise use the median value of the data.
    if center is None:
        cen = median(data)
    else:
        cen = center

    # Obtain the median absolute deviation about the median, or what it specified as the center
    # of the distribution.
    res = data - cen
    mad = median(abs(res)) / 0.6745

    # COMPUTE Centre
    # Initialize centre (return) as cen
    centre = cen

    # If the MAD=0, try the mean absolute deviation, and if that failes, the median itself.
    if mad <= eps:
        mad = npsum(abs(res)) / n / 0.80

    if mad > eps:
        # Now the biweighted location estimator:
        u = res / 6.0 / mad
        indices = where(abs(u) < 1.0)
        cnt = indices[0].size
        if cnt > 3:
            u2 = (1.0 - u[indices]**2)**2
            centre = cen + npsum(res[indices] * u2) / npsum(u2)

    # COMPUTE Spread
    if n > 10:
        # In the case of enough datapoints, apply Tukey's biweight estimator
        spread = 0.
        if mad > eps:
            # The biweight scale estimator:
            u = res / 9.0 / mad
            indices = where(abs(u) < 1.0)
            cnt = indices[0].size
            if cnt >= 3:
                u2 = u[indices]**2
                u1 = 1.0 - u2
                spread = (sqrt(n * npsum((u1**4) * res[indices]**2)) /
                          abs(npsum(u1 * (1.0 - 5.0 * u2))))
    else:
        # In the limit of small numbers, use the gapper algorithm to estimate the spread.
        # In the case of N=1, 2 provide a very rough estimate.
        if n == 1:
            spread = cen  # "Poissonian assumption"
        if n == 2:
            spread = 0.5 * abs(data.flatten()[1] - data.flatten()[0])
        if n >= 3:
            x = sort(data)
            g = abs(x[1:n] - x[0:n - 1])
            w = arange(n - 1, dtype=float) + 1.0
            w = w * (n - w)
            spread = sqrt(pi) / (n * (n - 1)) * npsum(w * g)

    if moment is None:
        return centre, spread
    elif moment == 1:
        return centre
    elif moment == 2:
        return spread
    else:
        raise ValueError("moment argument can be None, 1 or 2. Got {}".format(moment))
