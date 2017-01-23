#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
exop_posterior module.

The objective of this package is to provides the ExoP_Posterior class.
It should provide a sub class of the Posterior class defines in posterior.core.posterior module

@TODO:
"""
import logging

from .core.posterior import Posterior


logger = logging.getLogger()


class ExoP_Posterior(Posterior):
    """docstring for ExoP_Posterior."""

    __datatypes = ["RV", "LC"]

    def __init__(self, arg):
        super(ExoP_Posterior, self).__init__()
        self.arg = arg

# Functions to plot
# def plot_LC(dataset_key=None):
#     """
#     Plot a specific light-curve data set or all of them.
#
#     To plot a specific LC dataset one should provide the dataset_key which is name of the
#     instrument (followed by _number is several datasets from the same instrument). For example
#     "K2".
#
#     ----
#
#     Arguments:
#         dataset_key : string, optional,
#             Key indicating which dataset you want to plot. If not provided the function plot all
#             the LC dataset in different sub-windows.
#     """
#     raise NotImplementedError
#
# def plot_RV():
#     """
#     Plot a specific radial velocity data set or all of them.
#
#     To plot a specific RV dataset one should provide the dataset_key which is name of the
#     instrument (followed by _number is several datasets from the same instrument). For example
#     "SOPHIE".
#
#     ----
#
#     Arguments:
#         dataset_key : string, optional,
#             Key indicating which dataset you want to plot. If not provided the function plot all
#             the RV dataset in different sub-windows.
#     """
#     raise NotImplementedError
