#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument container module.

The objective of this module is to provide the interface InstrumentContainerInterface. It upgrades
a ParamContainerDatabase with the possibility to handle an instruments database.
"""
from ..dataset_and_instrument.instrument import instrument_model_category, Core_Instrument
from ....tools.database_with_instrument_level import DatabaseInstLevel, check_args


class InstrumentContainerInterface(object):
    """docstring for ParamContainerDatabase.

    It has to be in the list of parent before ParamContainerDatabase.
    """
    def __init__(self):
        # super(ParamContainerDatabase, self).__init__()
        # Init the instruments
        self.paramcontainers.update({instrument_model_category:
                                     DatabaseInstLevel(object_stored="instmodobj",
                                                       database_name=self.name,
                                                       ordered=True)})

    def add_an_instrument_model(self, instrument, name, force=False):
        """Add an instrument model to the paramcontainers of this model."""
        if not(isinstance(instrument, Core_Instrument)):
            raise ValueError("instrument should be an instance of a subclass of "
                             "Core_Instrument.")
        inst_cat = instrument.category
        inst_name = instrument.name
        inst_model_obj = instrument.create_model_instance(name=name)
        self.instruments[inst_cat][inst_name][name] = inst_model_obj

    def rm_an_instrument_model(self, inst_model, inst_name, inst_cat, **kwargs):
        """Remove an instrument model to the paramcontainers of this model."""
        inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
                                                     inst_cat=inst_cat, **kwargs)
        self.instruments[inst_cat][inst_name].pop(inst_model)

    @property
    def instruments(self):
        """Return the instruments an Orderedict with the instrument models of the model."""
        return self.paramcontainers[instrument_model_category]

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
                        mod = self.instruments[inst_name][inst_mod_name]
                        result.extend(mod.get_list_params(main=main, free=free))
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result.extend(param_cont.get_list_params(main=main, free=free))
        return result

    def instrumenthasatleast1model(self, inst_name, inst_cat=None):
        """Return True if there is at least one instrument model for the instrument."""
        return self.instruments.hasatleast1instmod(inst_name=inst_name, inst_cat=inst_cat)
