#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Dynamical Gravitational group (gravgroup) module.

The objective of this module is to define the GravGroupDyn class.
A GravGroupDyn intance is a SubClass of GravGroup for which will use dynamical code to interpret the
data.

@TODO:
"""
from logging import getLogger
from os.path import isfile, join
from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase
# from copy import deepcopy
from textwrap import dedent
# from math import acos, degrees
# from ajplanet import pl_rv_array
# from batman import TransitModel, TransitParams
# from pytransit import MandelAgol

from .gravgroup import GravGroup
from .parametrisation import GravGroup_Parametrisation
from .limb_darkening import Manager_LD, CoreLD
from .datasim_creator_rebound import create_datasimulator_rebound
from .datasim_creator_lc import create_datasimulator_LC
from .supersamp_exptime import SuperSampExpTimeAttr, _supersamp_key, _exptime_key
from ..dataset_and_instrument.lc import LC_inst_cat
from ..dataset_and_instrument.rv import RV_inst_cat
# from ...core.dataset_and_instrument.instrument import Instrument_Model
# from ...core.dataset_and_instrument.dataset import Dataset
from ...core.model.core_model import Core_Model
# from ....tools.function_w_doc import DocFunction
# from ....tools.convert import getecc_fast, getomega_fast, getaoverr  # , gettp_fast
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like


# from pdb import set_trace


## Logger object
logger = getLogger()


mgr_LD = Manager_LD()


class GravGroupDyn(GravGroup):
    """docstring for GravGroup."""

    ## category
    __category__ = "GravitionalGroupsDynamic"

    ## List of available dynamical models, the 1st element is used as default
    _dyn_models = ["rebound"]

    ## List of available transit models, the 1st element is used as default
    _transit_models = ["batman"]

    ## List of available rv models, the 1st element is used as default
    # redefinied here to not mix up with the herited GravGroup one.
    _rv_models = ["rebound"]

    ## The available LD models are defined in GravGroup and I keep it like that

    def __init__(self, name, dataset_db, instmodel4dataset=None, l_instmod_fullnames=[],
                 dynamical_model=None, transit_model=None, parametrisation=None,
                 stars=None, planets=None, run_folder=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, dataset_db, instmodel4dataset=instmodel4dataset,
                                        l_instmod_fullnames=l_instmod_fullnames,
                                        transit_model=transit_model, rv_model=None,
                                        parametrisation=parametrisation,
                                        stars=stars, planets=planets, run_folder=run_folder)
        if LC_inst_cat in self.dataset_db.inst_categories:
            self._produce_LC = True
        else:
            self._produce_LC = False
        if RV_inst_cat in self.dataset_db.inst_categories:
            self._produce_RV = True
        else:
            self._produce_RV = False

        self.dynamical_model = dynamical_model

        # Fill the datasimcreatorname4instcat dictionnary
        if self.dynamical_model == "rebound":
            self.datasimcreatorname4instcat[RV_inst_cat] = "sim_rebound"
            self.datasimcreatorname4instcat[LC_inst_cat] = "sim_rebound"
        else:
            raise NotImplementedError("Only dynamical model rebound is implemented for now")

        # Fill the datasimcreator dictionnary
        self.datasimcreator["sim_rebound"] = None

    @property
    def dynamical_model(self):
        """Returns the name of the transit model used."""
        return self.__dynamical_model

    @dynamical_model.setter
    def dynamical_model(self, model_name):
        """Returns the name of the dynamical model used."""
        if model_name in self._dyn_models:
            self.__dynamical_model = model_name
        elif model_name is None:
            self.__dynamical_model = self._dyn_models[0]
        else:
            raise AssertionError("dynamical_model should be in {}".format(self._dyn_models))

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        dico = GravGroupDyn.init_kwargs.fget(self)
        dico["dynamical_model"] = self.dynamical_model
        if "rv_model" in dico:
            dico.pop("rv_model")
        return dico

    def _create_datasimulator_RV_LC_rebound(self, inst_models=None, datasets=None):
        return create_datasimulator_rebound(star=list(self.stars.values())[0],
                                            planets=self.planets,
                                            key_whole=self.key_whole,
                                            parametrisation=self.parametrisation,
                                            LC_multis_parametrisations=(self.
                                                                        LC_multis_parametrisations),
                                            ldmodel4instmodfname=self.ldmodel4instmodfname,
                                            LDs=self.LDs, transit_model=self.transit_model,
                                            SSE4instmodfname=self.SSE4instmodfname,
                                            RV_globalref_instname=self.RV_globalref_instname,
                                            RV_instref_modnames=self.RV_references,
                                            RV_inst_db=self.instruments[RV_inst_cat],
                                            inst_models=inst_models, datasets=datasets)
