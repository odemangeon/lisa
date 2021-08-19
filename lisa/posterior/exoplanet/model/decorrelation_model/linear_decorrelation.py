#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger

from .core_decorrelation_model import Core_DecorrelationModel
## Logger object
logger = getLogger()


class LinearDecorrelation_LC(Core_DecorrelationModel):
    """docstring for LinearDecorrelation_LC."""

    # def __init__(self, arg):
    #     super(LinearDecorrelation_LC, self).__init__()
    #     self.arg = arg
