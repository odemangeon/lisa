#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
jitter module.

The objective of this module is to provide the functions to add the jitter to the model.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger

from ...core.parameter import Parameter


## Logger Object
logger = getLogger()


jitter_name = "jitter"


class Jitter(object):
    """docstring for Jitter."""

    def model_extranoise_w_jitter(self, inst_model_obj):
        """Add a jitter parameter to the instrument model and make it a main parameter."""
        inst_model_obj.add_parameter(Parameter(name=jitter_name,
                                               name_prefix=inst_model_obj.full_name, main=True))
