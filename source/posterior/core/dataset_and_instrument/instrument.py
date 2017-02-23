#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument module.

The objective of this package is to provides the core Isntrument and Default_Instrument classes
to store information about the isntrument used to measurement the data stored in the Dataset class.

@DONE:
    - Core_Instrument.__init__: Doc and UT
    - Default_Instrument: Doc and UT

@TODO:
"""
from logging import getLogger

from .manager_dataset_instrument import Manager_Inst_Dataset
from ..paramcontainer import Core_ParamContainer
from ..parameter import Parameter
from ....tools.name import Name
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.miscellaneous import spacestring_like, interpret_data_filename


## Logger object
logger = getLogger()

## Instrument manager
manager_inst = Manager_Inst_Dataset()

instrument_model_category = "instruments"

string4datasetdico = "Dataset"

key_inst = "inst_dic"
key_misc = "misc"


class Core_Instrument(Name, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_Instrument abstract class."""

    __mandatoryattrs__ = ["category", "params_model"]

    def __init__(self, name):
        """Core_Instrument init method FOR INHERITANCE PURPOSES (as Core_Instrument is an abstract class).

        This __init__ does:
            1. Set name of the instrument
        ----
        Arguments:
            name : string,
                Name of the Instrument
        """
        super(Core_Instrument, self).__init__(name=name)

        class Instrument_Model(Core_ParamContainer):
            """Docstring of Instrument_Model class."""

            __category__ = instrument_model_category

            def __init__(self, instrument, name):
                """Docstring of the Instrument_Model init method."""
                # name_prefix is set to None because it will be set when the gravgroup is set.
                super(Instrument_Model, self).__init__(name=name, name_prefix=instrument.name)
                self.__instrument = instrument
                for name, dico in instrument.params_model.items():
                    self.add_parameter(Parameter(name=name, name_prefix=self.full_name,
                                                 **dico))

            @property
            def instrument(self):
                return self.__instrument

        self.Instrument_Model = Instrument_Model
        # IMPORTANT: THE INSTRUMENT TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL
        # Make Dataset an abstract class
        if type(self) is Core_Instrument:
            raise NotImplementedError("Dataset should not be instanciated!")

    def create_model_instance(self, name):
        """Return the instrument type."""
        return self.Instrument_Model(instrument=self, name=name)


class Default_Instrument(Core_Instrument):
    """docstring for Default_Instrument class (not abstract contrary to Core_Instrument)."""
    def __init__(self, category, name, params_model={}):
        """Default_Instrument init method.

        This __init__ does:
            1. Set type of the instrument
            2. Set name of the instrument
        ----
        Arguments:
            category : string,
                Category of the Instrument
            name : string,
                Name of the Instrument
        """
        super(Default_Instrument, self).__init__(name)
        self.__category__ = category
        self.__params_model__ = params_model


def get_instrument_paramfilesection(model_instance, inst_db, text_tab="", entete_symb=" = ",
                                    quote_name=False):
    """Return the paramfile section for every instrument category."""
    text = ""
    for inst_cat in inst_db.keys():
        text += "{}# {} {}\n".format(text_tab, instrument_model_category, inst_cat)
        inst_subclass = manager_inst.get_inst_subclass(inst_cat)
        for inst_name in inst_db[inst_cat]:
            if quote_name:
                entete_inst_name = "'{}'{}{{".format(inst_name, entete_symb)
            else:
                entete_inst_name = "{}{}{{".format(inst_name, entete_symb)
            extra_tab = spacestring_like(entete_inst_name)
            text += text_tab + entete_inst_name
            texttab_1tline = False
            for inst_model in inst_db[inst_cat][inst_name].values():
                text += inst_model.get_paramfile_section(text_tab=text_tab + extra_tab,
                                                         texttab_1tline=texttab_1tline,
                                                         entete_symb=": ",
                                                         quote_name=True)
                texttab_1tline = True
                text += ",\n"
            model_name_def = list(inst_db[inst_cat][inst_name].keys())[0]
            text_instmod4dataset = ""
            for datasetname in model_instance.dataset_db.get_datasetnames(inst_name=inst_name):
                number = interpret_data_filename(datasetname)["number"]
                model_name = model_instance.instmodel4dataset[datasetname]
                text_instmod4dataset += "'{}': '{}', ".format(number, model_name)
            text += ("{0}# By default all the datasets of an instrument are associated "
                     "to {1}.\n{0}# If you want to model some datasets with another "
                     "instrument model copy paste it,\n{0}# give it a new name and "
                     "file the {2} dict.\n{0}'{2}': {{{3}}},"
                     "".format(text_tab + extra_tab, model_name_def, string4datasetdico,
                               text_instmod4dataset))
            if hasattr(inst_subclass, "_get_inst_paramfilesection"):
                text += "\n\n"
                func = getattr(inst_subclass, "_get_inst_paramfilesection")
                text += func(text_tab=text_tab + extra_tab, model_instance=model_instance,
                             inst_name=inst_name)
            text += "{}}}\n\n".format(text_tab + extra_tab)
        if hasattr(inst_subclass, "_get_instcat_paramfilesection"):
            func = getattr(inst_subclass, "_get_instcat_paramfilesection")
            text += func(text_tab=text_tab, model_instance=model_instance)
        text += "\n"
    return text


def update_instrument_paramfile_info(inst_db_info, inst_db):
    """Update the paramfile_info for an instrument category.

    It updates things introduced by get_instcat_paramfilesection in paramfile_info.
    """
    for inst_cat in inst_db.keys():
        inst_subclass = manager_inst.get_inst_subclass(inst_cat)
        inst_db_info[inst_cat] = {}
        inst_db_info[inst_cat][key_inst] = {}
        inst_db_info[inst_cat][key_misc] = []
        for inst_name in inst_db[inst_cat]:
            inst_db_info[inst_cat][key_inst][inst_name] = []
            for inst_model in inst_db[inst_cat][inst_name].keys():
                inst_db_info[inst_cat][key_inst][inst_name].append(inst_model)
                inst_db[inst_cat][inst_name][inst_model].update_paramfile_info()
            inst_db_info[inst_cat][key_inst][inst_name].append(string4datasetdico)
            # TODO: DELEGATE TO INSTRUMENT CLASS METHOD
            if hasattr(inst_subclass, "_update_inst_paramfile_info"):
                func = getattr(inst_subclass, "_update_inst_paramfile_info")
                func(inst_db_info[inst_cat][key_inst][inst_name])
        if hasattr(inst_subclass, "_update_instcat_paramfile_info"):
            func = getattr(inst_subclass, "_update_instcat_paramfile_info")
            func(inst_db_info[inst_cat][key_misc])


def load_instrument_config(dico_config, inst_db_info, inst_db, model_instance):
    """Update the paramfile_info for an instrument category.

    It updates things introduced by get_allinst_paramfilesection in paramfile_info.
    """
    for inst_cat in inst_db_info.keys():
        inst_subclass = manager_inst.get_inst_subclass(inst_cat)
        logger.debug("Content of param_file_info for {} {}: {}"
                     "".format(instrument_model_category, inst_cat,
                               inst_db_info[inst_cat]))
        for inst_name in inst_db_info[inst_cat][key_inst].keys():
            logger.debug("Content of param_file_info for {} {}: {}"
                         "".format(instrument_model_category, inst_name,
                                   inst_db_info[inst_cat][key_inst][inst_name]))
            logger.debug("Content of dico_config for {} {}: {}"
                         "".format(instrument_model_category, inst_name,
                                   dico_config[inst_name]))
            # Load config of instrument models
            set_paramfile_info = set(inst_db_info[inst_cat][key_inst][inst_name])
            set_dico_config = set(dico_config[inst_name].keys())
            instcat_hasspecifickeys = False
            if hasattr(inst_subclass, "_load_config_listspecifickeys_inst"):
                fun = getattr(inst_subclass, "_load_config_listspecifickeys_inst")
                listspecifickeys = fun()
                instcat_hasspecifickeys = True
            for set_obj in [set_paramfile_info, set_dico_config]:
                set_obj.remove(string4datasetdico)
                if instcat_hasspecifickeys:
                    for key in listspecifickeys:
                        set_obj.remove(key)
            # Load config of already existing instrument model
            for inst_model in (set_paramfile_info & set_dico_config):
                paramcont_dico = dico_config[inst_name][inst_model]
                inst_db[inst_cat][inst_name][inst_model].load_config(paramcont_dico)
            # Remove instrument model that are not in the param_file anymore
            for inst_model in (set_paramfile_info.difference(set_dico_config)):
                model_instance.rm_an_instrument_model(inst_cat, inst_name, inst_model)
                model_instance.update_paramfile_info()
            # Add instrument model are in the param_file but not yet in the model
            for inst_model in (set_dico_config.difference(set_paramfile_info)):
                paramcont_dico = dico_config[inst_name][inst_model]
                instrument = manager_inst.get_instrument(inst_name)
                model_instance.add_an_instrument_model(instrument, inst_model)
                model_instance.update_paramfile_info()
                inst_db[inst_name][inst_model].load_config(paramcont_dico)
            # Load which instrument model to use for which dataset
            for dataset in model_instance.dataset_db.get_datasetnames(inst_name=inst_name):
                number = interpret_data_filename(dataset)["number"]
                inst_model = dico_config[inst_name][string4datasetdico][number]
                if model_instance.instmodel4dataset[dataset] != inst_model:
                    logger.debug("Instrument model to use for dataset {} changed from "
                                 "{} to {}.".format(dataset,
                                                    model_instance.instmodel4dataset[dataset],
                                                    inst_model))
                    model_instance.instmodel4dataset[dataset] = inst_model
            # Load specific keys of the instrument category
            if instcat_hasspecifickeys:
                inst_subclass._load_config_specifickeys_inst(dico_config[inst_name],
                                                             inst_name=inst_name,
                                                             model_instance=model_instance)
        for key in inst_db_info[inst_cat][key_misc]:
            inst_subclass._load_config_instcat(dico_config=dico_config,
                                               model_instance=model_instance)
