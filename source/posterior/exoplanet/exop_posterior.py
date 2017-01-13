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
