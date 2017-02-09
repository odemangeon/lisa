#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_model module.

The objective of this package is to provides the core Core_Model class.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import OrderedDict
from os.path import isfile

from ....tools.metaclasses import  MandatoryReadOnlyAttr
from ..paramcontainer import Core_ParamContainer
from ..dataset_and_instrument.instrument import Core_Instrument, instrument_model_category
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like


## Logger
logger = getLogger()

string4datasetdico = "Dataset"


class Core_Model(Core_ParamContainer, DatasetDbAttr, metaclass=MandatoryReadOnlyAttr):

    __mandatoryattrs__ = ["category"]

    """docstring for Core_Model abstract class."""
    def __init__(self, name, dataset_db=None):
        """Core_Model init method FOR INHERITANCE PURPOSES (as Core_Model is an abstract class).

        This __init__ does:
            1. Set name of the model and add a list of parameter attribute
        ----
        Arguments:
            name  : string,
                Name of the Core_Model
            instruments : dict, (default: None)
                Dictionnary with keys being the instrument types of the dataset to be modeled and
                each key contain the list of instrument instances associated to the instrument used
                for this type of instrument.
        """
        # 1.
        Core_ParamContainer.__init__(self, name)
        # 2.
        DatasetDbAttr.__init__(self, dataset_db)
        # 3.
        self._paramcontainers = OrderedDict()
        # 4.
        if self.hasdataset_db:
            self.__init_instruments_models()
        # IMPORTANT NOTE THE MODEL TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

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
        inst_category = instrument.Instrument_Model.__category__
        if inst_category not in self.paramcontainers:
            self.paramcontainers.update({inst_category: dict()})
        inst_name = instrument.name
        if inst_name not in self.paramcontainers[inst_category]:
            self.paramcontainers[inst_category].update({inst_name: OrderedDict()})
        if name in self.paramcontainers[inst_category][inst_name]:
            if not(force):
                error_msg = ("Intrument model {} already exist in the model, it will not be "
                             "added.".format(inst_category + '_' + inst_name + '_' + name))
                raise ValueError(error_msg)
            else:
                warning_msg = ("Intrument model {} already exist in the model, it will be replaced."
                               "".format(inst_category + '_' + inst_name + '_' + name))
                logger.warning(warning_msg)
        inst_model = instrument.create_model_instance(name=name)
        self.paramcontainers[inst_category][inst_name].update({name: inst_model})
        logger.debug("Added instrument model {} in model {}"
                     "".format(inst_category + '_' + inst_name + '_' + name, self.name))

    def __init_instruments_models(self):
        """Add an instrument model for each instrument used in the dataset database."""
        for inst in self.dataset_db.get_instruments().values():
            self.add_an_instrument_model(inst, name="default")

    def get_paramfile_section(self, text_tab="", entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this Model.
        ----
        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        text = ""
        for parcont_type in self.paramcont_categories:
            text += "{}# {}\n".format(text_tab, parcont_type)
            if parcont_type != instrument_model_category:
                for parcont in self.paramcontainers[parcont_type].values():
                    text += parcont.get_paramfile_section(text_tab=text_tab,
                                                          entete_symb=entete_symb,
                                                          quote_name=quote_name)
                    text += "\n\n"
            else:
                for inst_name in self.paramcontainers[parcont_type].keys():
                    if quote_name:
                        entete_inst_name = "'{}'{}{{".format(inst_name, entete_symb)
                    else:
                        entete_inst_name = "{}{}{{".format(inst_name, entete_symb)
                    extra_tab = spacestring_like(entete_inst_name)
                    text += text_tab + entete_inst_name
                    texttab_1tline = False
                    for parcont in self.paramcontainers[parcont_type][inst_name].values():
                        text += parcont.get_paramfile_section(text_tab=text_tab + extra_tab,
                                                              texttab_1tline=texttab_1tline,
                                                              entete_symb=": ",
                                                              quote_name=True)
                        texttab_1tline = True
                        text += ",\n"
                    model_name = list(self.paramcontainers[parcont_type][inst_name].keys())[0]
                    text += ("{}# By default all the datasets of an instrument are associated to "
                             "{}.\n{}# If you want to model some datasets with another instrument "
                             "model copy paste it,\n{}# give it a new name and file the {} dict."
                             "".format(text_tab + extra_tab, model_name, text_tab + extra_tab,
                                       text_tab + extra_tab, string4datasetdico))
                    text += "\n{}'{}': {{".format(text_tab + extra_tab, string4datasetdico)
                    for datasetnbget in self.dataset_db.get_datasetnbs(inst_name=inst_name):

                        text += "'{}': '{}', ".format(datasetnbget, model_name)
                    text += "}}\n\n{}}}\n\n".format(text_tab + extra_tab)
            text += "\n"
        self.update_paramfile_info()
        return text

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute."""
        self.paramfile_info.clear()
        for parcont_type in self.paramcont_categories:
            if parcont_type != instrument_model_category:
                self.paramfile_info[parcont_type] = []
                for parcont_name, parcont in self.paramcontainers[parcont_type].items():
                    self.paramfile_info[parcont_type].append(parcont_name)
                    parcont.update_paramfile_info()
            else:
                self.paramfile_info[parcont_type] = {}
                for inst_name in self.paramcontainers[parcont_type].keys():
                    self.paramfile_info[parcont_type][inst_name] = []
                    for inst_model in self.paramcontainers[parcont_type][inst_name].keys():
                        self.paramfile_info[parcont_type][inst_name].append(inst_model)
                        self.paramcontainers[parcont_type][inst_name][inst_model].update_paramfile_info()
                    self.paramfile_info[parcont_type][inst_name].append(string4datasetdico)
        logger.debug("Updated paramfile info for {}.\nKeys of paramfile_info: {}"
                     "".format(self.name, self.paramfile_info))

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        logger.debug("List of Core_ParamContainer types in param_file_info: {}"
                     "".format(self.paramfile_info.keys()))
        for paramcont_type in self.paramfile_info.keys():
            logger.debug("Content of param_file_info for {}: {}"
                         "".format(paramcont_type, self.paramfile_info[paramcont_type]))
            if paramcont_type != instrument_model_category:
                for paramcont_name in self.paramfile_info[paramcont_type]:
                    paramcont_dico = dico_config[paramcont_name]
                    logger.debug("Content of param dictionary for {} {}: {}"
                                 "".format(paramcont_type, paramcont_name, paramcont_dico))
                    self.paramcontainers[paramcont_type][paramcont_name].load_config(paramcont_dico)
            else:
                for inst_name in self.paramfile_info[paramcont_type].keys():
                    logger.debug("Content of param_file_info for {} {}: {}"
                                 "".format(paramcont_type, inst_name,
                                           self.paramfile_info[paramcont_type][inst_name]))
                    for inst_model in self.paramfile_info[paramcont_type][inst_name]:
                        if inst_model != string4datasetdico:
                            paramcont_dico = dico_config[inst_name][inst_model]
                            self.paramcontainers[paramcont_type][inst_name][inst_model].load_config(paramcont_dico)

    @property
    def param_file(self):
        """Path to the parametrisation file"""
        return self.__param_file

    @param_file.setter
    def param_file(self, path):
        """Path to the parametrisation file"""
        file_exists = isfile(path)
        if file_exists:
            self.__param_file = path
        else:
            raise AssertionError("File {} doesn't exists".format(path))

    @property
    def isdefined_paramfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.param_file is not None

    def create_parameter_file(self, filepath):
        """Create the parameter file."""
        if isfile(filepath):
            answers_list = ['y', 'n']
            question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                        "".format(filepath, answers_list))
            reply = QCM_utilisateur(question, answers_list)
        else:
            reply = "y"
        if reply == "y":
            with open(filepath, 'w') as f:
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                f.write("# Parametrisation file of {}\n\n".format(self.name))
                f.write("# Parameters\n")
                f.write(self.get_paramfile_section())
            logger.info("Parameter file created at path: {}".format(filepath))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(filepath))
            self.update_paramfile_info(recursive=True)
        self.param_file = filepath

    def read_parameter_file(self):
        """Read the content of the parameter file."""
        if self.isdefined_paramfile:
            exec(open(self.param_file).read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("Parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read parameter file: {}".format(self.param_file))

    def load_parameter_file(self):
        """load the parameter file."""
        dico_config = self.read_parameter_file()
        self.load_config(dico_config)
