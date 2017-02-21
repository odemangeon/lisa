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
from os.path import isfile, join

from ....tools.metaclasses import MandatoryReadOnlyAttr
from ..paramcontainer import Core_ParamContainer
from ..dataset_and_instrument.instrument import instrument_model_category
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..dataset_and_instrument.manager_dataset_instrument import interpret_data_filename
from ..prior.core_prior import Prior
from ....tools.default_folders_data_run import RunFolder
from ..likelihood import create_lnlikelihood as _create_lnlikelihood
from .paramcontainers_database import ParamContainerDatabase

## Logger
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()

string4datasetdico = "Dataset"


class Core_Model(Core_ParamContainer, DatasetDbAttr, Prior, RunFolder, ParamContainerDatabase,
                 metaclass=MandatoryReadOnlyAttr):

    __mandatoryattrs__ = ["category"]

    """docstring for Core_Model abstract class."""
    def __init__(self, name, dataset_db, run_folder=None):
        """Core_Model init method FOR INHERITANCE PURPOSES (as Core_Model is an abstract class).

        This __init__ does:
            1. Set name of the model and add a list of parameter attribute
        ----
        Arguments:
            name  : string,
                Name of the Core_Model
            dataset_db : DatasetDatabase instance,
                DatasetDatabase giving the dataset to be modeled.
        """
        # 1.
        Core_ParamContainer.__init__(self, name)
        # 2.
        DatasetDbAttr.__init__(self, dataset_db)
        if not(self.hasdataset_db):
            raise ValueError("You need to provide a DatasetDatabase to create a model !")
        # 3.
        RunFolder.__init__(self, run_folder=run_folder)
        # 4.
        ParamContainerDatabase.__init__(self)
        # 5.
        self.__init_instruments_models()
        # 6.
        self.__instmodel4dataset = dict.fromkeys(self.dataset_db.get_datasetnames(), "default")
        # IMPORTANT NOTE THE MODEL TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    @property
    def instmodel4dataset(self):
        """Dictionnary giving which instrument model to use for which dataset."""
        return self.__instmodel4dataset

    @property
    def name_instmodel_used(self):
        """Return a dict which for each instrument name give the instrument models to use."""
        result = {}
        result = dict.fromkeys(self.dataset_db.get_instruments().keys(), [])
        for dataset_name, mod_name in self.instmodel4dataset.items():
            file_info = interpret_data_filename(dataset_name)
            result[file_info["inst_name"]].append(mod_name)
        return result

    def __init_instruments_models(self):
        """Add an instrument model for each instrument used in the dataset database."""
        for inst in self.dataset_db.get_instruments().values():
            self.add_an_instrument_model(inst, name="default")

    def get_list_params(self, main=False, free=False):
        """Return the list of all parameters."""
        result = []
        result.extend(Core_ParamContainer.get_list_params(self, main=main, free=free))
        for paramcont_cat in self.paramcontainers_categories:
            if paramcont_cat == instrument_model_category:
                result.extend(ParamContainerDatabase.
                              get_list_params(self, main=main, free=free,
                                              inst_models=self.name_instmodel_used))
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result.extend(param_cont.get_list_params(main=main, free=free))
        return result

    def get_list_paramnames(self, main=False, free=False, full_name=False):
        """Return the list of all parameters."""
        result = []
        for param in self.get_list_params(main=main, free=free):
            if full_name:
                result.append(param.full_name)
            else:
                result.append(param.name)
        return result

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
                    for datasetname in self.dataset_db.get_datasetnames(inst_name=inst_name):
                        number = interpret_data_filename(datasetname)["number"]
                        model_name = self.instmodel4dataset[datasetname]
                        text += "'{}': '{}', ".format(number, model_name)
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
                    logger.debug("Content of dico_config for {} {}: {}"
                                 "".format(paramcont_type, inst_name,
                                           dico_config[inst_name]))
                    # Load config of instrument models
                    set_paramfile_info = set(self.paramfile_info[paramcont_type][inst_name])
                    set_dico_config = set(dico_config[inst_name].keys())
                    for set_obj in [set_paramfile_info, set_dico_config]:
                        set_obj.remove(string4datasetdico)
                    # Load config of already existing instrument model
                    for inst_model in (set_paramfile_info & set_dico_config):
                        paramcont_dico = dico_config[inst_name][inst_model]
                        self.paramcontainers[paramcont_type][inst_name][inst_model].load_config(paramcont_dico)
                    # Remove instrument model that are not in the param_file anymore
                    for inst_model in (set_paramfile_info.difference(set_dico_config)):
                        self.rm_an_instrument_model(paramcont_type, inst_name, inst_model)
                        self.update_paramfile_info()
                    # Add instrument model are in the param_file but not yet in the model
                    for inst_model in (set_dico_config.difference(set_paramfile_info)):
                        paramcont_dico = dico_config[inst_name][inst_model]
                        instrument = manager_inst.get_instrument(inst_name)
                        self.add_an_instrument_model(instrument, inst_model)
                        self.update_paramfile_info()
                        self.paramcontainers[paramcont_type][inst_name][inst_model].load_config(paramcont_dico)
                    # Load which insstrument model to use for which dataset
                    for dataset in self.dataset_db.get_datasetnames(inst_name=inst_name):
                        number = interpret_data_filename(dataset)["number"]
                        inst_model = dico_config[inst_name][string4datasetdico][number]
                        if self.instmodel4dataset[dataset] != inst_model:
                            logger.debug("Instrument model to use for dataset {} changed from {} "
                                         "to {}.".format(dataset, self.instmodel4dataset[dataset],
                                                         inst_model))
                            self.instmodel4dataset[dataset] = inst_model

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

    def create_parameter_file(self, paramfile_path):
        """Create the parameter file."""
        file_path = self.look4runfile(file_path=paramfile_path)
        if file_path is not None:
            answers_list_yn = ['y', 'n']
            question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                        "".format(file_path, answers_list_yn))
            reply = QCM_utilisateur(question, answers_list_yn)
        else:
            answers_list_create = ["absolute", "error"]
            question = ("File {} doesn't exists. Do you want to\nCreate it at the 'absolute' path: "
                        "{}".format(paramfile_path, paramfile_path))
            if self.hasrun_folder:
                answers_list_create.append("run_folder")
                run_folder_path = join(self.run_folder, paramfile_path)
                question += "\nCreate it at the 'run_folder' path: {}".format(run_folder_path)
            question += "\nNot create it and raise an 'error' ? {}".format(answers_list_create)
            reply = QCM_utilisateur(question, answers_list_create)
            if reply == "absolute":
                file_path = paramfile_path
            elif reply == "run_folder":
                file_path = run_folder_path
            else:
                raise ValueError("File {} doesn't exist and the user doesn't want to create it."
                                 "".format(paramfile_path))
            reply = "y"
        if reply == "y":
            with open(file_path, 'w') as f:
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                f.write("# Parametrisation file of {}\n\n".format(self.name))
                f.write("# Parameters\n")
                f.write(self.get_paramfile_section())
            logger.info("Parameter file created at path: {}".format(file_path))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(file_path))
            self.update_paramfile_info(recursive=True)
        self.param_file = file_path

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

    def create_lnlikelihood(self):
        """create the loglikelihood function"""
        # _create_lnlikelihood()create_lnlikelihood(datasimulator
        #                         category="wo jitter", jitter_param=None)
        pass
