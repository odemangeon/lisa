#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
paramcontainer_database module.

The objective of this module is to manage the Paramcontainers database.

@DONE:
    -
@TODO:
    - update nb_of_paramcontainers to properly take into account the instruments
"""
from logging import getLogger
from collections import OrderedDict

from ..paramcontainer import Core_ParamContainer

## Logger
logger = getLogger()


class ParamContainerDatabase(object):
    """docstring for ParamContainerDatabase."""
    def __init__(self):
        # super(ParamContainerDatabase, self).__init__()
        self._paramcontainers = OrderedDict()

    @property
    def name(self):
        """Return "ParamContainerDatabase" should be overloaded by subclass."""
        return "ParamContainerDatabase"

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

    @property
    def paramcontainers_categories(self):
        """Return the list of the paramcontainer categories in this ParamContainerDatabase."""
        return list(self.paramcontainers.keys())

    def get_list_params(self,  main=False, free=False, **kwargs):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters

        Keyword arguments are arguments specific to a certain type of parameter containers (like the
         instruments). See get_list_params of these parameter container for more information.

        :return list_of_param result: list of Parameter instances
        """
        result = []
        for paramcont_cat in self.paramcontainers_categories:
            if isinstance(self.paramcontainers[paramcont_cat], SpecificParamContainerCategory):
                selectedkwargs = (self.paramcontainers[paramcont_cat].
                                  get_subkwargs_4_get_list_params(**kwargs))
                result.extend(self.paramcontainers[paramcont_cat].
                              get_list_params(**selectedkwargs))
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result.extend(param_cont.get_list_params(main=main, free=free))
        return result

    def get_list_paramnames(self, full_name=False, *args, **kwargs):
        """Return the list of all parameters.

        :param bool full_name:
        :param *args, **kwargs: Those parameters are given directly to get_list_params. So see this
            function for more details.
        :return list_of_string l_paramnames: List of names or full names of the parameters specified
            by args and kwargs.
        """
        result = []
        for param in self.get_list_params(*args, **kwargs):
            if full_name:
                result.append(param.full_name)
            else:
                result.append(param.name)
        return result


class SpecificParamContainerCategory(object):
    """docstring for SpecificParamContainerCategory."""

    def get_subkwargs_4_get_list_params(self, model_instance, **kwargs):
        """Select the keyword arguments for the get_list_params method of this param container.

        :param Core_Model model_instance: Model instance which can be used for the default value
            of some arguments of the SpecificParamContainerCategory.
        Keyword arguments that are used only by the get_list_params method of a SpecificParamContainerCategory

        :return dict selected_kwargs: Dictionary with key = argument name, value = argument value
        """
        raise NotImplementedError("You have to overwrite the get_subkwargs_4_get_list_params method"
                                  "when you create a subclass of SpecificParamContainerCategory")
