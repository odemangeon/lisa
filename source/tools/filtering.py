#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
:py:mod:`filtering.py` - Filtering utils
------------------------------

Miscellaneous filtering utilities.
"""
import numpy as np
from scipy.signal import medfilt
from scipy.signal import savgol_filter
from logging import getLogger


logger = getLogger()


def MedianFilter(x, kernel_size=5):
    '''
    A silly wrapper around :py:func:`scipy.signal.medfilt`.

    Taken from https://github.com/rodluger/everest/blob/master/everest/math.py
    '''
    if kernel_size % 2 == 0:
        kernel_size += 1
    return medfilt(x, kernel_size=kernel_size)


def Smooth(x, window_len=100, window='hanning'):
    '''
    Smooth data by convolving on a given timescale.

    :param ndarray x: The data array
    :param int window_len: The size of the smoothing window. Default `100`
    :param str window: The window type. Default `hanning`

    Taken from https://github.com/rodluger/everest/blob/master/everest/math.py
    '''

    if window_len == 0:
        return np.zeros_like(x)
    s = np.r_[2 * x[0] - x[window_len - 1::-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    if window == 'flat':
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len:-window_len + 1]


def Chunks(l, n, all=False):
    '''
    Returns a generator of consecutive `n`-sized chunks of list `l`.
    If `all` is `True`, returns **all** `n`-sized chunks in `l`
    by iterating over the starting point.

    '''

    if all:
        jarr = range(0, n - 1)
    else:
        jarr = [0]

    for j in jarr:
        for i in range(j, len(l), n):
            if i + 2 * n <= len(l):
                yield l[i:i + n]
            else:
                if not all:
                    yield l[i:]
                break


def Scatter(y, win=13, remove_outliers=False):
    '''
    Return the scatter in ppm based on the median running standard deviation for
    a window size of :py:obj:`win` = 13 cadences (for K2, this is ~6.5 hours, as in VJ14).

    :param ndarray y: The array whose CDPP is to be computed
    :param int win: The window size in cadences. Default `13`
    :param bool remove_outliers: Clip outliers at 5 sigma before computing the CDPP? Default `False`

    '''
    if remove_outliers:
        # Remove 5-sigma outliers from data
        # smoothed on a 1 day timescale
        if len(y) >= 50:
            ys = y - Smooth(y, 50)
        else:
            ys = y
        M = np.nanmedian(ys)
        MAD = 1.4826 * np.nanmedian(np.abs(ys - M))
        out = []
        for i, _ in enumerate(y):
            if (ys[i] > M + 5 * MAD) or (ys[i] < M - 5 * MAD):
                out.append(i)
        out = np.array(out, dtype=int)
        y = np.delete(y, out)
    if len(y):
        return 1.e6 * np.nanmedian([np.std(yi) / np.sqrt(win) for yi in Chunks(y, win, all=True)])
    else:
        return np.nan


def SavGol(y, win=49):
    '''
    Subtracts a second order Savitsky-Golay filter with window size `win`
    and returns the result. This acts as a high pass filter.

    '''

    if len(y) >= win:
        return y - savgol_filter(y, win, 2) + np.nanmedian(y)
    else:
        return y


def get_outliers(x, max_iter=10, sigma_out=5, badmask=None):
    '''
    Performs iterative sigma clipping to get outliers.

    :param np.ndarray x:
    :param int max_iter: strictly positive int
    :param np.ndarray badmask:

    '''
    outmask = np.array([], dtype=int)
    nanmask = np.argwhere(np.isnan(x))
    if badmask is None:
        badmask = np.array([], dtype=int)
    logger.info("Clipping outliers...")
    logger.info('Iter %d/%d: %d outliers' % (0, max_iter, len(outmask)))

    def M(x):
        return np.delete(x, np.concatenate([nanmask, badmask]), axis=0)

    t = M(range(len(x)))
    l_outmask = [np.array([-1]), outmask]

    # Loop as long as the last two outlier arrays aren't equal
    while not np.array_equal(outmask[-2], outmask[-1]):

        # Check if we've done this too many times
        if len(outmask) - 1 > max_iter:
            logger.error('Maximum number of iterations in ``get_outliers()`` exceeded. Skipping...')
            break

        # Check if we're going in circles
        if np.any([np.array_equal(outmask[-1], i) for i in outmask[:-1]]):
            logger.error('Function ``get_outliers()`` is going in circles. Skipping...')
            break

        # Get the outliers
        f = SavGol(M(x))
        med = np.nanmedian(f)
        MAD = 1.4826 * np.nanmedian(np.abs(f - med))
        inds = np.where((f > med + sigma_out * MAD) | (f < med - sigma_out * MAD))[0]

        # Project onto unmasked time array
        inds = np.array([np.argmax(self.time == t[i]) for i in inds])
        outmask = np.array(inds, dtype=int)

        # Add them to the running list
        l_outmask.append(np.array(inds))

        # Log
        logger.info('Iter %d/%d: %d outliers' % (len(outmask) - 2, max_iter, len(self.outmask)))
