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
        self._store_name_rules = OrderedDict()

    @property
    def name(self):
        """Return "ParamContainerDatabase" should be overloaded by subclass."""
        return "ParamContainerDatabase"

    @property
    def paramcontainers(self):
        """ParamContainers contained in the models sorted into categorie."""
        return self._paramcontainers

    @property
    def store_name_rules_db(self):
        """ParamContainers contained in the models sorted into categorie."""
        return self._store_name_rules

    def add_a_paramcontainer(self, paramcontainer, force=False):
        """Add a paramcontainer to the model.

        :param Core_ParamContainer paramcontainer: Paramcontainer to add to the database.
        :param bool force: If True the paramcontainer is added to the database even if a paramcontainer
            with the same store name already exists (it will be overwriten).
        """
        if not(isinstance(paramcontainer, Core_ParamContainer)):
            raise ValueError("paramcontainer should be an instance of a subclass of "
                             "Core_ParamContainer.")
        parcont_name = paramcontainer.store_name
        parcont_cat = paramcontainer.category
        # Check if the category of the param container already exist in the database. If not add it
        if parcont_cat not in self.paramcontainers:
            self.paramcontainers.update({parcont_cat: OrderedDict()})
            self.store_name_rules_db.update({parcont_cat: paramcontainer.store_name_rules})
        # Check if the
        if not(self.store_name_rules_db[parcont_cat] == paramcontainer.store_name_rules):
            raise ValueError("This param container ({}) doesn't not have the same store name rules "
                             "than previous ones of the same category.")
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
                Storage name of the paramcontainer.
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

    def get_list_params(self, model_instance, main=False, free=False, no_duplicate=True, **kwargs):
        """Return the list of all parameters.

        :param Core_Model model_instance: Model instance which is used for the default value of
            some SpecificParamContainerCategory (optional).
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
                                  get_subkwargs_4_get_list_params(model_instance, **kwargs))
                result.extend(self.paramcontainers[paramcont_cat].
                              get_list_params(main=main, free=free, no_duplicate=no_duplicate, **selectedkwargs))
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result_param_cont = param_cont.get_list_params(main=main, free=free, no_duplicate=no_duplicate)
                    if no_duplicate:
                        result_param_cont_name = [param_in_res.get_name(include_prefix=True, recursive=True) for param_in_res in result_param_cont]
                        for param in result_param_cont:
                            if param.get_name(include_prefix=True, recursive=True) in result_param_cont_name:
                                result_param_cont.remove(param)
                    result.extend()
        return result

    def get_list_paramnames(self, model_instance=None, main=False, free=False, no_duplicate=True, **kwargs):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param Core_Model model_instance: Model instance which is used for the default value of
            some SpecificParamContainerCategory (optional).

        Keyword arguments are passed to the Named.get_name methods (see docstring for details).

        :return list_of_string l_paramnames: List of names or full names of the parameters specified
            by args and kwargs.
        """
        result = []
        for param in self.get_list_params(model_instance=model_instance, main=main, free=free, no_duplicate=no_duplicate):
            result.append(param.get_name(**kwargs))
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
