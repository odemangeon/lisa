#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_model module.

The objective of this package is to provides the core Model class.

@DONE:
    -

@TODO:
    -
"""
import logging

## Logger
logger = logging.getLogger()


class Model(object):
    """docstring for Model."""
    def __init__(self, arg):
        super(Model, self).__init__()
        self.arg = arg
