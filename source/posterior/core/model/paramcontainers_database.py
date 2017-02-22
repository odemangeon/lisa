#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
paramcontainer_database module.

The objective of this module is to manage the Paramcontainers database.

@DONE:
    -
@TODO:
    - TBD
"""
from logging import getLogger
from collections import OrderedDict

from ..paramcontainer import Core_ParamContainer
from ..dataset_and_instrument.instrument import Core_Instrument, instrument_model_category

## Logger
logger = getLogger()


class ParamContainerDatabase(object):
    """docstring for ParamContainerDatabase."""
    def __init__(self):
        # super(ParamContainerDatabase, self).__init__()
        self._paramcontainers = OrderedDict()

    @property
    def paramcontainers(self):
        """ParamContainers contained in the models sorted into categorie."""
        return self._paramcontainers

    def add_a_paramcontainer(self, paramcontainer, use_full_name=False, force=False):
        """Add a paramcontainer to the model"""
        if not(isinstance(paramcontainer, Core_ParamContainer)):
            raise ValueError("paramcontainer should be an instance of a subclass of "
                             "Core_ParamContainer.")
        if use_full_name:
            parcont_name = paramcontainer.full_name
        else:
            parcont_name = paramcontainer.name
        parcont_cat = paramcontainer.category
        if parcont_cat not in self.paramcontainers:
            self.paramcontainers.update({parcont_cat: OrderedDict()})
        if parcont_name in self.paramcontainers[parcont_cat]:
            if not(force):
                logger.error("paramcontainer {} already exist in the model, it will not be "
                             "added.".format(parcont_cat + '_' + parcont_name))
                raise ValueError("The paramcontainer named {} alredy exist in the model"
                                 "".format(parcont_name))
            else:
                logger.error("paramcontainer {} already exist in the model, it will be replaced."
                             "".format(parcont_cat + '_' + parcont_name))
        self.paramcontainers[parcont_cat].update({parcont_name: paramcontainer})

    def isavailable_paramcontainer(self, name, category):
        """Return True if filename correspond to a dataset that is in the database.
        ----
        Arguments:
            name : string,
                name of the paramcontainer.
            category : string,
                category of the paramcontainer
        """
        if category not in self.paramcontainers:
            return False
        else:
            return name in self.paramcontainers[category]

    def rm_paramcontainer(self, name, category):
        """Remove a dataset from the the dataset database.
        ----
        Arguments:
            name : string,
                name of the paramcontainer.
            category : string,
                category of the paramcontainer
        """
        res = self.paramcontainers[category].pop(name)
        if res is None:
            logger.warning("The deletion of the paramcontainer {} from the model has failed "
                           "because it was not found was not found.".format(category + '_' + name))
        else:
            logger.info("The paramcontainer {} has been removed from the model."
                        "".format(category + '_' + name))
        if len(self.paramcontainers[category]) == 0:
            self.paramcontainers.pop(category)

    @property
    def nb_of_paramcontainers(self):
        """Returns the dict giving the number of paramcontainers in each category."""
        result = dict()
        for key, dico_cat in self.paramcontainers.items():
            result[key] = len(dico_cat)
        return result

    @property
    def paramcont_categories(self):
        """ParamContainers contained in the models sorted into categorie."""
        return list(self.paramcontainers.keys())

    def add_an_instrument_model(self, instrument, name, force=False):
        """Add an instrument model to the paramcontainers of this model."""
        if not(isinstance(instrument, Core_Instrument)):
            raise ValueError("instrument should be an instance of a subclass of "
                             "Core_Instrument.")
        if instrument_model_category not in self.paramcontainers:
            self.paramcontainers.update({instrument_model_category: dict()})
        inst_name = instrument.name
        if inst_name not in self.paramcontainers[instrument_model_category]:
            self.paramcontainers[instrument_model_category].update({inst_name: OrderedDict()})
        if name in self.paramcontainers[instrument_model_category][inst_name]:
            if not(force):
                error_msg = ("Intrument model {} already exist in the model, it will not be "
                             "added.".format(instrument_model_category + '_' + inst_name + '_' +
                                             name))
                raise ValueError(error_msg)
            else:
                warning_msg = ("Intrument model {} already exist in the model, it will be replaced."
                               "".format(instrument_model_category + '_' + inst_name + '_' + name))
                logger.warning(warning_msg)
        inst_model = instrument.create_model_instance(name=name)
        self.paramcontainers[instrument_model_category][inst_name].update({name: inst_model})
        logger.debug("Added instrument model {} in model {}"
                     "".format(instrument_model_category + '_' + inst_name + '_' + name, self.name))

    def rm_an_instrument_model(self, inst_cat, inst_name, inst_model):
        """Remove an instrument model to the paramcontainers of this model."""
        res = self.paramcontainers[inst_cat][inst_name].pop(inst_model)
        if res is None:
            logger.warning("The deletion of the instrument model {} from the model has failed "
                           "because it was not found was not found."
                           "".format(inst_cat + '_' + inst_name + "_" + inst_model))
        else:
            logger.info("The instrument model {} has been removed from the model."
                        "".format(inst_cat + '_' + inst_name + "_" + inst_model))

    @property
    def instruments(self):
        """Return the instruments an Orderedict with the instrument models of the model."""
        return self.paramcontainers[instrument_model_category]

    @property
    def paramcontainers_categories(self):
        """Return the list of the paramcontainer categories used in this model."""
        return list(self.paramcontainers.keys())

    def get_list_params(self, main=False, free=False, inst_models={}):
        """Return the list of all parameters.
        ----
        Arguments:
            inst_models : dict, (default:{}),
                dictionnary which for each instrument name give the list of the names of
                instrument models for which you want the params.
        """
        result = []
        for paramcont_cat in self.paramcontainers_categories:
            if paramcont_cat == instrument_model_category:
                for inst_name, list_mod_name in inst_models.items():
                    for inst_mod_name in list_mod_name:
                        mod = self.paramcontainers[paramcont_cat][inst_name][inst_mod_name]
                        result.extend(mod.get_list_params(main=main, free=free))
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result.extend(param_cont.get_list_params(main=main, free=free))
        return result

    def get_list_paramnames(self, main=False, free=False, full_name=False, inst_models={}):
        """Return the list of all parameters."""
        result = []
        for param in self.get_list_params(main=main, free=free, inst_models=inst_models):
            if full_name:
                result.append(param.full_name)
            else:
                result.append(param.name)
        return result

    def get_list_instmodel(self, inst_category=None):
        """Return the list of all parameters."""
        result = []
        for inst_name in list(self.instruments.keys()):
            for inst_model_name in self.instruments[inst_name]:
                inst_model = self.instruments[inst_name][inst_model_name]
                if inst_category is None:
                    result.append(inst_model)
                else:
                    if inst_model.instrument.category == inst_category:
                        result.append(inst_model)
        return result
