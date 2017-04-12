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


def apply_parametrisation_jitter(model_instance, instmod_fullname):
    """Check that there is a jitter main parameter in the instrument model."""
    inst_model_obj = model_instance.instruments[instmod_fullname]
    if jitter_name in inst_model_obj.parameters:
        jitter_param = inst_model_obj.parameters[jitter_name]
        jitter_param.main = True
    else:
        inst_model_obj.add_parameter(Parameter(name=jitter_name,
                                               name_prefix=inst_model_obj.full_name, main=True))
        logger.debug("{} main parameter added in instruments model {}."
                     "".format(jitter_name, instmod_fullname))
