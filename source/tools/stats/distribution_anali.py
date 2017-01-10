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

from source.tools.stats.loc_scale_estimator import  rob_mom
import numpy as np



def getconfi(distri, level , centre = None):
    """
    inputs distribution , sigma level we want can be 1,2,3
    optinal input is centre. if given it will be used to calculate the limits otherwise the rob_mon will be used.
    """
    if level == 1:
        s1  =   np.percentile(distri, [16,84], axis=0)

    if level == 2:
        s1  =   np.percentile(distri, [5,95], axis=0)

    if level == 3:
        s1  =   np.percentile(distri, [0.3,99.7], axis=0)

    # If center is provided, take it as cen, otherwise use the median value of the data.
    if centre is None:
        loc = np.asarray(rob_mom(distri))[0]
    else:
        loc = centre

    dis_right, dis_left =  s1[1]-loc,  loc-s1[0]

    return dis_right, loc, dis_left
