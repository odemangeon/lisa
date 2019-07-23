#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Time series toolbox module.

The objective of this package is to provides a toolbox to manipulate time series

@ DONE:
    -
@TODO:
    -
"""
from numpy import arange, asarray, newaxis, mean


def get_time_supersampled(time, supersamp, exptime):
    """Return a time vector supersampled.

    Inspired from https://github.com/hpparvi/PyTransit/blob/master/src/supersampler.py

    :param array_like time: time vector
    :param int supersamp: Super sampling factor to apply (>= 1)
    :param float exptime: Exposure time of the time vector, in the same unit than time
    :return array_like supersamp_time: Super sampled time vector.
    """
    relative_supersample_positions = exptime * ((arange(1, supersamp + 1, dtype='d') - 0.5) /
                                                supersamp - 0.5)
    return (asarray(time)[:, newaxis] + relative_supersample_positions).reshape(-1)


def average_supersampled_values(values, supersamp):
    """Return an averaged values vector.

    Inspired from https://github.com/hpparvi/PyTransit/blob/master/src/supersampler.py
    and https://github.com/lkreidberg/batman/blob/master/batman/transitmodel.py

    :param np.ndarray values: supersampled values vector has to be 1D
    :param int supersamp: Super sampling factor of the values vector
    """
    return mean(values.reshape(-1, supersamp), axis=1)
