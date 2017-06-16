#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculate statistics on the distributions

@package tools
@ingroup getconfi

@brief calculate confidence limits for distributions
@details calculates 1 sigma , 2 sigma , 3 sigma percentiles for distributions
if centre is given it is used for the limits otherwise the rob_mon is used and returned


@file
@author Susana Barros
@date  Decembre 14, 2016
@version 1.0
@todo:
"""
from logging import getLogger
from source.tools.stats.loc_scale_estimator import rob_mom
import numpy as np


logger = getLogger()


def getconfi(distri, level, centre=None, l_param_name=None):
    """
    inputs distribution , sigma level we want can be 1,2,3
    optinal input is centre. if given it will be used to calculate the limits otherwise the rob_mom
    will be used.
    """
    ndim = len(distri.shape)
    if level == 1:
        s1 = np.nanpercentile(distri, [16, 84], axis=0)

    if level == 2:
        s1 = np.nanpercentile(distri, [5, 95], axis=0)

    if level == 3:
        s1 = np.nanpercentile(distri, [0.3, 99.7], axis=0)

    # If center is provided, take it as cen, otherwise use the median value of the data.
    if centre is None:
        if ndim == 1:
            loc = rob_mom(distri, moment=1)
        else:
            loc = np.apply_along_axis(rob_mom, 0, distri, moment=1)
    else:
        loc = centre

    dis_right, dis_left = s1[1] - loc, loc - s1[0]

    text = "\n"
    if ndim == 1:
        if l_param_name is not None:
            param_name = l_param_name
        else:
            param_name = ""
        text += "{}{} +{} -{}\n".format(param_name, loc, dis_right, dis_left)
    else:
        for i in range(distri.shape[1]):
            if l_param_name is not None:
                param_name = l_param_name[i] + ": "
            else:
                param_name = ""
            text += "{}{} +{} -{}\n".format(param_name, loc[i], dis_right[i], dis_left[i])
    logger.info(text)

    return dis_right, loc, dis_left
