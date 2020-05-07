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
from ....tools.name import Named
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.miscellaneous import spacestring_like, interpret_data_filename
from ..likelihood.manager_noise_model import Manager_NoiseModel


## Logger object
logger = getLogger()

## Instrument manager
manager_inst = Manager_Inst_Dataset()
manager_noisemodel = Manager_NoiseModel()

instrument_model_category = "instruments"

string4datasetdico = "Dataset"

key_inst = "inst_dic"
key_misc = "misc"


def interpret_instmod_fullname(instmod_fullname):
    """Return the instrument name associated to the instrument model full_name."""
    res = {}
    res["inst_name"], res["inst_model"] = instmod_fullname.split("_")
    return res


def build_instmod_fullname(inst_model, inst_name):
    """Return the instrument name associated to the instrument model full_name."""
    return "{}_{}".format(inst_name, inst_model)


# class MethodIntercept(type):
#
#     def __getattr__(cls, name):
#         try:
#             return lambda *args, **kwargs: getattr(cls, name)(*args, **kwargs)
#         except:
#             raise AttributeError


class Instrument_Model(Core_ParamContainer):
    """Docstring of Instrument_Model class."""

    __category__ = instrument_model_category

    def __init__(self, instrument, name, noise_model=None, **kwargs):
        """Docstring of the Instrument_Model init method.

        :param Core_Instrument instrument: Instrument that is modelled.
        :param string name: Name of the instrument model
        :param string/None noise_model: Name of noise model to use for this instruments data
            likelihood.

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        # Make the initialisation of Core_ParamContainer
        # name_prefix is set to None because it will be set when the gravgroup is set.
        if "name_prefix" in kwargs:
            raise TypeError("'name_prefix' is an invalid keyword argument for this function. "
                            "name_prefix is automatically set as gravgroup.name if gravgroup is"
                            "provided")
        super(Instrument_Model, self).__init__(name=name, name_prefix=instrument.name, **kwargs)
        # Set the instrument attribute
        self.__instrument = instrument
        # Set the noise_model attribute
        if noise_model is None:
            self.__noise_model = noise_model
        else:
            self.noise_model = noise_model
        # Set the parameters necessary to model the instrument behavior.
        for name, dico in instrument.params_model.items():
            self.add_parameter(Parameter(name=name, name_prefix=self.name,
                                         **dico))

    def __getattr__(self, name):
        if hasattr(self.instrument, name):
            if hasattr(getattr(self.instrument, name), "__call__"):
                return lambda *args, **kwargs: getattr(self.instrument, name)(inst_model=self,
                                                                              *args, **kwargs)
        # Default behaviour
        return super(Instrument_Model, self).__getattr__(name)

    @property
    def noise_model(self):
        """Return the noise model used for this instrument model."""
        return self.__noise_model

    @noise_model.setter
    def noise_model(self, nm):
        """Set the noise model to use for this instrument model."""
        available_noisemodels = manager_noisemodel.get_available_noisemodels()
        if nm not in available_noisemodels:
            raise ValueError("{} is not an available noise model: {}"
                             "".format(nm, available_noisemodels))
        self.__noise_model = nm

    @property
    def instrument(self):
        return self.__instrument


class Core_Instrument(Named, metaclass=MandatoryReadOnlyAttr):
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
        # Do the Named initialization
        super(Core_Instrument, self).__init__(name=name)

        self.Instrument_Model = Instrument_Model
        # IMPORTANT: THE INSTRUMENT CATEGORY IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL
        # Make Dataset an abstract class
        if type(self) is Core_Instrument:
            raise NotImplementedError("Dataset should not be instanciated!")

    def create_model_instance(self, name, **kwargs):
        """Return the instrument type.

        :param string name: Name of the instrument model

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        return self.Instrument_Model(instrument=self, name=name, **kwargs)


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
                text_instmod4dataset += "{}: '{}', ".format(number, model_name)
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
            text += "\n{}}}\n\n".format(text_tab + extra_tab)
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
            if hasattr(inst_subclass, "_update_inst_paramfile_info"):
                func = getattr(inst_subclass, "_update_inst_paramfile_info")
                func(inst_db_info[inst_cat][key_inst][inst_name])
        if hasattr(inst_subclass, "_update_instcat_paramfile_info"):
            func = getattr(inst_subclass, "_update_instcat_paramfile_info")
            func(inst_db_info[inst_cat][key_misc])


def load_instrument_config(dico_config, inst_db_info, inst_db, model_instance, available_joint_priors={}):
    """Update the paramfile_info for an instrument category.

    It updates things introduced by get_allinst_paramfilesection in paramfile_info.
    """
    logger.debug("Categories of instruments in the param_file_info: {}"
                 "".format(list(inst_db_info.keys())))
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
            logger.debug("Set of inst model before the loading: {}\n"
                         "Set of inst model in the paramfile: {}".format(set_paramfile_info,
                                                                         set_dico_config))
            # Load config of already existing instrument model
            for inst_model in (set_paramfile_info & set_dico_config):
                logger.debug("Instmodel to be updated: {}".format(inst_model))
                paramcont_dico = dico_config[inst_name][inst_model]
                inst_db[inst_cat][inst_name][inst_model].load_config(dico_config=paramcont_dico,
                                                                     model_instance=model_instance,
                                                                     available_joint_priors=available_joint_priors)
            # Remove instrument model that are not in the param_file anymore
            for inst_model in (set_paramfile_info.difference(set_dico_config)):
                logger.debug("Instmodel to be suppressed: {}".format(inst_model))
                model_instance.rm_an_instrument_model(inst_model=inst_model, inst_name=inst_name,
                                                      inst_cat=inst_cat)
                model_instance.update_paramfile_info()
            # Add instrument model are in the param_file but not yet in the model
            for inst_model in (set_dico_config.difference(set_paramfile_info)):
                logger.debug("Instmodel to be added: {}".format(inst_model))
                paramcont_dico = dico_config[inst_name][inst_model]
                instrument = manager_inst.get_instrument(inst_name)
                model_instance.add_an_instrument_model(instrument=instrument, name=inst_model)
                model_instance.update_paramfile_info()
                inst_db[inst_cat][inst_name][inst_model].load_config(dico_config=paramcont_dico,
                                                                     model_instance=model_instance,
                                                                     available_joint_priors=available_joint_priors)
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
