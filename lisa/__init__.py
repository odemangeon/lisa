#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lisa package.

The objective of this package is to provides a framework for posterior function generation. The main
focus for now is the analysis of exoplanet datasets and in particular transit photometry and radial
velocity data.
"""

__version__ = "0.2.5dev"

# __all__ = []  # Put here the import classes or function from the modules or packages of lisa
# from .data_interface import  # import the main classes or function defined in data_interface
from .posterior.core.posterior import Posterior

__all__ = ["Posterior", ]
# NO CODE here expect what is above.
