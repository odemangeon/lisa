#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
gp_lnlike module.

The objective of this module is to define the log likelihood in case you want to use a GP to
model the residuals.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger

from ..dataset_and_instrument.rv import RV_inst_cat
from ..dataset_and_instrument.lc import LC_inst_cat
from ...core.parameter import Parameter


## logger object
logger = getLogger()

amp = "lnAmpSA"
evol_timescal = "tauESA"
periodic_timescal = "tauPSA"
period = "PSA"


def apply_parametrisation_stellar_activity(model_instance, instmod_fullname):
    """Check that there is a jitter main parameter in the instrument model."""
    star = model_instance.stars[list(model_instance.stars.keys())[0]]
    star.add_parameter(Parameter(name=evol_timescal, name_prefix=star.get_name(include_prefix=True, recursive=True), main=True))
    star.add_parameter(Parameter(name=periodic_timescal, name_prefix=star.get_name(include_prefix=True, recursive=True),
                                 main=True))
    star.add_parameter(Parameter(name=period, name_prefix=star.get_name(include_prefix=True, recursive=True), main=True))
    inst_model_obj = model_instance.instruments[instmod_fullname]
    inst = inst_model_obj.instrument
    inst_cat = inst.category
    if inst_cat == RV_inst_cat:
        star.add_parameter(Parameter(name=amp, name_prefix=star.get_name(include_prefix=True, recursive=True), main=True))
    elif inst_cat == LC_inst_cat:
        star.add_parameter(Parameter(name=amp, name_prefix=star.get_name(include_prefix=True, recursive=True), main=True))
    else:
        raise ValueError("Stellar activity noise model cannot be used for instrument category {}"
                         "".format(inst_cat))
