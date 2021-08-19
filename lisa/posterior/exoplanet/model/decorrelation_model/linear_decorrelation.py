#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger

from .core_decorrelation_model import Core_DecorrelationModel
## Logger object
logger = getLogger()


class LinearDecorrelation(Core_DecorrelationModel):
    """docstring for LinearDecorrelation."""

    # def __init__(self, arg):
    #     super(LinearDecorrelation, self).__init__()
    #     self.arg = arg
