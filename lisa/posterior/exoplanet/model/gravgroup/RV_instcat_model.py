#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
RV_instcat_model module.

The objective of this package is to provides the RV_InstCat_Model class to handle the RV instrument class
for the GravGroup class.

@DONE:
    -

@TODO:
    - self.stars is used here but it's only define in GravGroup that makes the code a bit difficult to
    understand and follow. Is there a solution ? same thing for self.paramfile4instcat
"""
from logging import getLogger

from .datasim_creator_rv import create_datasimulator_RV
from ...dataset_and_instrument.rv import RV_inst_cat
from ....core.model.core_instcat_model import Core_InstCat_Model


## Logger object
logger = getLogger()


class RV_InstCat_Model(Core_InstCat_Model):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = RV_inst_cat
    __has_instcat_paramfile__ = False
    __default_paramfile_path__ = None
    __datasim_creator_name__ = "sim_RV"
    __decorrelation_models__ = []

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["radvel", ]  # ["radvel", "ajplanet"] Temporarily? remove ajplanet from the available rv_models

    def __init__(self, model_instance):
        self.param_file_instcat = None
        self.rv_model = None
        # Initialise the dictionary giving the RV zero point RV_references
        self.__RV_references = dict.fromkeys(model_instance.get_inst_names(inst_fullcat=RV_inst_cat), None)
        logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
        self.__RV_references["global"] = list(self.__RV_references.keys())[0]
        for key in self.__RV_references:
            if key != "global":
                self.__RV_references[key] = model_instance.get_instmodel_names(inst_name=key,
                                                                               inst_fullcat=RV_inst_cat)[0]

    @property
    def isdefined_paramfile_instcat(self):
        """Return True is the attribute param_file has been defined."""
        return self.param_file_instcat is not None

    @property
    def RV_references(self):
        return self.__RV_references

    @property
    def RV_globalref_instname(self):
        return self.__RV_references["global"]

    def datasim_creator(self, inst_models=None, datasets=None):
        return create_datasimulator_RV(star=list(self.stars.values())[0],
                                       planets=self.planets,
                                       key_whole=self.key_whole,  # self.key_whole comes from Core_Model
                                       key_param=self.key_param,  # self.key_param comes from DatasimulatorCreator
                                       key_mand_kwargs=self.key_mand_kwargs,  # self.key_mand_kwargs comes from DatasimulatorCreator
                                       key_opt_kwargs=self.key_opt_kwargs,  # self.key_opt_kwargs comes from DatasimulatorCreator
                                       ext_plonly=self._ext_plonly,
                                       RV_globalref_instname=self.RV_globalref_instname,
                                       RV_instref_modnames=self.RV_references,
                                       RV_inst_db=self.instruments[RV_inst_cat],
                                       rv_model=self.rv_model,
                                       inst_models=inst_models, datasets=datasets)

    def create_instcat_paramfile(self, file_path, model_instance):
        """Create a parameter file for the light-curve parametrisation.

        Arguments
        ---------
        file_path           : string
            Path to the param_file.
        model_instance      : Model instance
        """
        raise NotImplementedError()

    def load_instcat_paramfile(self):
        """Load LC_param_file."""
        raise NotImplementedError()
        dico_config = self.read_RV_param_file()
        self.load_RV_config(dico_config)

    def read_RV_param_file(self):
        """Read the content of the LC parameter file."""
        if self.isdefined_RVparamfile:
            with open(self.paramfile4instcat[self.__inst_cat__]) as f:
                exec(f.read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("RV parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read RV parameter file: {}".format(self.paramfile4instcat[self.__inst_cat__]))

    def load_RV_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        raise NotImplementedError()

    def set_RV_globalref_instname(self, inst_name):
        self.__RV_references["global"] = inst_name

    def get_RVref4inst_modname(self, inst_name):
        return self.__RV_references[inst_name]

    def set_RVref4inst_modname(self, inst_name, inst_model_name):
        self.__RV_references[inst_name] = inst_model_name
