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
from loguru import logger
from george.kernels import ExpSquaredKernel, ExpSine2Kernel
from george import GP
from numpy import concatenate, sqrt
import numpy as np
from collections import defaultdict, Counter, OrderedDict
import os
from os.path import basename
# from collections import OrderedDict

# from ..model.celestial_bodies import Star
from ...exoplanet.dataset_and_instrument.rv import RV_inst_cat
from ...exoplanet.dataset_and_instrument.lc import LC_inst_cat
from ..parameter import Parameter
from .core_noise_model import Core_Noise_Model
from ..dataset_and_instrument.indicator import IND_inst_cat
from ....tools.miscellaneous import spacestring_like
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.function_from_text_toolbox import FunctionBuilder
# from ....tools.function_w_doc import DocFunction


amp = "amp"
tau = "tau"
gamma = "gamma"
logperiod = "lnperiod"

param_noisemod_name = "param_noisemod"

GP1D_noisemodel_cat = "GP1D"


class GP1D_Noise_Models(Core_Noise_Model):
    """docstring for GP1D_Noise_Models."""

    __category__ = "GP1D"
    __has_GP__ = True
    __has_jitter__ = True

    ################
    # Main functions
    ################
    def __init__(self, model_instance, run_folder, config_file):
        super(GP1D_Noise_Models, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self._models_config = self._init_model_config()
        self._define_default_model()

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        dict2print['model_definitions'] = dict2print['model_definitions'].copy()
        for model_name in dict2print['model_definitions']:
            dict2print['model_definitions'][model_name] = dict2print['model_definitions'][model_name].dict2print
        return dict2print
    
    def get_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a gaussian noise model")
        model_name = self._models_config['model4instrument'][inst_model_fullname]
        return self._models_config['model_definitions'][model_name]
    
    ##############################
    # Required by the main methods
    ##############################

    # Required by the __init__ method
    #################################

    def _init_model_config(self):
        return  {'model4instrument': {instmodfullname: '' for instmodfullname in self.l_inst_model_fullname},
                 'model_definitions': {},
                 }
    

    
