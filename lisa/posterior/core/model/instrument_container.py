#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument container module.

The objective of this module is to provide the interface InstrumentContainerInterface. It upgrades
a ParamContainerDatabase with the possibility to handle an instruments database.
"""
from ..dataset_and_instrument.instrument import instrument_model_category, Core_Instrument
from ....tools.database_with_instrument_level import DatabaseInstLevel, check_args
from .paramcontainers_database import SpecificParamContainerCategory


class InstrumentContainerInterface(object):
    """docstring for InstrumentContainerInterface and interface of core_model.Core_Model.

    It has to be in the list of parent classes of Model before ParamContainerDatabase.
    It's an Interface of core_model.Core_Model which allows the model to properly handle instrument
    models.
    """
    def __init__(self):
        # super(ParamContainerDatabase, self).__init__()
        # Init the instruments
        self.paramcontainers.update({instrument_model_category: InstrumentContainer()})

    @property
    def instruments(self):
        """Return an Orderedict with the instrument models currently in the instance."""
        return self.paramcontainers[instrument_model_category]

    def add_an_instrument_model(self, instrument, name, force=False):
        """Add an instrument model to the paramcontainers of this model."""
        if not(isinstance(instrument, Core_Instrument)):
            raise ValueError("instrument should be an instance of a subclass of "
                             "Core_Instrument.")
        inst_cat = instrument.category
        inst_name = instrument.get_name()
        inst_model_obj = instrument.create_model_instance(name=name, kwargs_getname_4_storename={"include_prefix": True, "recursive": True},
                                                          kwargs_getname_4_codename={"include_prefix": False, "code_version": True})
        self.instruments[inst_cat][inst_name][name] = inst_model_obj

    def rm_an_instrument_model(self, inst_model, inst_name, inst_cat, **kwargs):
        """Remove an instrument model to the paramcontainers of this model."""
        inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
                                                     inst_cat=inst_cat, **kwargs)
        self.instruments[inst_cat][inst_name].pop(inst_model)

    @property
    def instruments_categories(self):
        """Return the list of instruments categories in this ParamContainerDatabase."""
        return self.instruments.inst_categories

    def get_instmodel_objs(self, inst_model=None, inst_name=None, inst_cat=None,
                           sortby_instcat=False, sortby_instname=False, sortby_instmodel=False,
                           **kwargs):
        """Return instrument model objects."""
        return self.instruments.get_objects(inst_model=inst_model, inst_name=inst_name,
                                            inst_cat=inst_cat, sortby_instcat=sortby_instcat,
                                            sortby_instname=sortby_instname,
                                            sortby_instmodel=sortby_instmodel, **kwargs)

    def get_instmodel_names(self, inst_name=None, inst_cat=None,
                            sortby_instname=False, sortby_instcat=False):
        """Return instrument model names."""
        return self.instruments.get_instmodels(inst_name=inst_name, inst_cat=inst_cat,
                                               sortby_instname=sortby_instname,
                                               sortby_instcat=sortby_instcat)

    def get_inst_names(self, inst_cat=None, sortby_instcat=False):
        """Return the list of instrument names."""
        return self.instruments.get_instnames(inst_cat=inst_cat, sortby_instcat=sortby_instcat)

    def instrumenthasatleast1model(self, inst_name, inst_cat=None):
        """Return True if there is at least one instrument model for the instrument."""
        return self.instruments.hasatleast1instmod(inst_name=inst_name, inst_cat=inst_cat)


class InstrumentContainer(DatabaseInstLevel, SpecificParamContainerCategory):
    """docstring for InstrumentContainer."""

    def __init__(self):
        super(InstrumentContainer, self).__init__(object_stored="instmodobj",
                                                  database_name="instrument container",
                                                  ordered=True)

    def get_list_params(self, main=False, free=False, no_duplicate=True, inst_models={}):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param dict inst_models : Dictionnary which for each instrument name give the list of the
                names of instrument models for which you want the params.
                key = isntrument name, value = list of instrument model name
        :return list_of_param result: list of Parameter instances
        """
        result = []
        for inst_name, list_mod_name in inst_models.items():
            for inst_mod_name in list_mod_name:
                mod = self[inst_name][inst_mod_name]
                result_mod = mod.get_list_params(main=main, free=free, no_duplicate=no_duplicate)
                if no_duplicate:
                    result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True) for param_in_res in result]
                    for param in result_mod:
                        if param.get_name(include_prefix=True, recursive=True) in result_param_name:
                            result_mod.remove(param)
                result.extend(result_mod)
        return result

    def get_subkwargs_4_get_list_params(self, model_instance=None, **kwargs):
        """Select the keyword arguments for the get_list_params method.

        :param Core_Model model_instance: Model instance which is used for the default value of
            inst_models, see below (optional).

        Keyword argument that are used by the get_list_params method of InstrumentContainer
        only:
        :param dict inst_models : Dictionnary which for each instrument name give the list of the
                names of instrument models for which you want the params.
                key = isntrument name, value = list of instrument model name
                If not provided, we return all the instrument models used by the model.

        :return dict selected_kwargs: Dictionary with key = argument name, value = argument value
        """
        selected_kwargs = {}
        # Get the specific arguments for InstrumentContainer get_param function
        for kwarg_name in ["inst_models"]:
            selected_kwargs[kwarg_name] = kwargs.get(kwarg_name, None)
        # Set the default value for inst_models, if not provided
        if selected_kwargs["inst_models"] is None:
            selected_kwargs["inst_models"] = model_instance.name_instmodels_used(sortby_instname=True)
        return selected_kwargs
