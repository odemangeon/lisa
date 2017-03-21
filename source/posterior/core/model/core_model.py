#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_model module.

The objective of this package is to provides the core Core_Model class.

@DONE:
    -

@TODO:
    - See if it's possible to put or at leat partially put get_paramfile_section,
    update_paramfile_info, load_config in paramcontainers_database
"""
from logging import getLogger
from os.path import isfile, join
from collections import OrderedDict
from numpy import array

from .datasimulator import DatasimulatorCreator
from .paramcontainers_database import ParamContainerDatabase
from ..instmodel4dataset import Instmodel4DatasetAttr, Instmodel4Dataset
from ..paramcontainer import Core_ParamContainer
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ..dataset_and_instrument.instrument import instrument_model_category as instmod_cat
from ..dataset_and_instrument.instrument import load_instrument_config
from ..dataset_and_instrument.instrument import get_instrument_paramfilesection
from ..dataset_and_instrument.instrument import update_instrument_paramfile_info
from ..likelihood import LikelihoodCreator
from ..prior.core_prior import Prior
from ..prior.manager_prior import Manager_Prior
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.default_folders_data_run import RunFolder


## Logger
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()
manager_prior = Manager_Prior()


class Core_Model(Core_ParamContainer, DatasetDbAttr, Prior, RunFolder, ParamContainerDatabase,
                 Instmodel4DatasetAttr, LikelihoodCreator, DatasimulatorCreator,
                 metaclass=MandatoryReadOnlyAttr):

    __mandatoryattrs__ = ["category"]

    ## Key to use in DatabaseFunc for the function that will concern the whole object to model
    key_whole = "whole"

    """docstring for Core_Model abstract class."""
    def __init__(self, name, dataset_db, run_folder=None, instmodel4dataset=None):
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
        if not(self.isdefined_datasetdb):
            raise ValueError("You need to provide a DatasetDatabase to create a model !")
        # 3.
        RunFolder.__init__(self, run_folder=run_folder)
        # 4.
        ParamContainerDatabase.__init__(self)
        # 5.
        self.init_missinginstmodels()
        # 6.
        if instmodel4dataset is None:
            instmodel4dataset = Instmodel4Dataset(list_datasetnames=(self.dataset_db.
                                                                     get_datasetnames()))
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       lock="instmodel4dataset")
        # IMPORTANT NOTE THE MODEL TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    def init_missinginstmodels(self):
        """If necessary, add a default instrument model for each instrument used.

        1. For each instrument used in the dataset database
            2. Check if there is at least one instrument model associated
                2a. If no, add one called default
                2b. If yes, do nothing
        """
        for inst in self.dataset_db.get_instruments():  # 1.
            if not(self.instrumenthasatleast1model(inst_name=inst.name,
                                                   inst_cat=inst.category)):  # 2.
                self.add_an_instrument_model(inst, name="default")

    def get_param(self, full_name):
        """Return the instance of the Parameter designated by full_name."""
        logger.debug("Parameter full name: {}".format(full_name))
        for paramcont_cat in self.paramcont_categories:
            if paramcont_cat is not instmod_cat:
                obj_name, subobj_name, param_name = full_name.split("_")
                if subobj_name in self.paramcontainers[paramcont_cat]:
                    if (self.paramcontainers[paramcont_cat][subobj_name].
                       has_parameter(name=param_name)):
                            return (self.paramcontainers[paramcont_cat][subobj_name].
                                    parameters[param_name])

            else:
                inst_name, inst_model, param_name = full_name.split("_")
                inst_db = self.instruments
                inst_model = inst_db["{}_{}".format(inst_name, inst_model)]
                if inst_model is not None:
                    return inst_model.parameters[param_name]

    def get_list_params(self, main=False, free=False):
        """Return the list of all parameters."""
        result = []
        result.extend(Core_ParamContainer.get_list_params(self, main=main, free=free))
        result.extend(ParamContainerDatabase.
                      get_list_params(self, main=main, free=free,
                                      inst_models=self.name_instmodels_used(sortby_instname=True)))
        # for paramcont_cat in self.paramcontainers_categories:
        #     if paramcont_cat == instmod_cat:
        #         result.extend(ParamContainerDatabase.
        #                       get_list_params(self, main=main, free=free,
        #                                       inst_models=self.name_instmodels_used))
        #     else:
        #         for param_cont in self.paramcontainers[paramcont_cat].values():
        #             result.extend(param_cont.get_list_params(main=main, free=free))
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

    def get_initial_values(self, list_paramnames=None, sortby_paramfullname=False):
        """Return intial values for the parameter.

        If value is provided for the parameter this value is returned otherwise a value is stochas-
        tically drawn from the prior.
        """
        if list_paramnames is None:
            l_param_main_free = self.get_list_params(main=True, free=True)
        else:
            l_param_main_free = []
            for param_name in list_paramnames:
                l_param_main_free.append(self.get_param(param_name))
        if sortby_paramfullname:
            res = OrderedDict()
        else:
            res = []
        for param in l_param_main_free:
            if param.value is None:
                prior_func_cls = manager_prior.get_priorfunc_subclass(param.prior_category)
                value = prior_func_cls(**param.prior_args).ravs()
            else:
                value = param.value
            if sortby_paramfullname:
                res[param.full_name] = value
            else:
                res.append(value)
        if sortby_paramfullname:
            return res
        else:
            return array(res)

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
            if parcont_type != instmod_cat:
                for parcont in self.paramcontainers[parcont_type].values():
                    text += parcont.get_paramfile_section(text_tab=text_tab,
                                                          entete_symb=entete_symb,
                                                          quote_name=quote_name)
                    text += "\n\n"
            else:
                text += get_instrument_paramfilesection(model_instance=self,
                                                        inst_db=self.paramcontainers[parcont_type],
                                                        text_tab=text_tab, entete_symb=entete_symb,
                                                        quote_name=quote_name)
        self.update_paramfile_info()
        return text

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute."""
        self.paramfile_info.clear()
        for parcont_type in self.paramcont_categories:
            if parcont_type != instmod_cat:
                self.paramfile_info[parcont_type] = []
                for parcont_name, parcont in self.paramcontainers[parcont_type].items():
                    self.paramfile_info[parcont_type].append(parcont_name)
                    parcont.update_paramfile_info()
            else:
                self.paramfile_info[instmod_cat] = {}
                update_instrument_paramfile_info(inst_db_info=self.paramfile_info[instmod_cat],
                                                 inst_db=self.paramcontainers[parcont_type])

        logger.debug("Updated paramfile info for {}.\nParamfile_info: {}"
                     "".format(self.name, self.paramfile_info))

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        logger.debug("List of Core_ParamContainer types in param_file_info: {}"
                     "".format(self.paramfile_info.keys()))
        for paramcont_type in self.paramfile_info.keys():
            logger.debug("Content of param_file_info for {}: {}"
                         "".format(paramcont_type, self.paramfile_info[paramcont_type]))
            if paramcont_type != instmod_cat:
                for paramcont_name in self.paramfile_info[paramcont_type]:
                    paramcont_dico = dico_config[paramcont_name]
                    logger.debug("Content of param dictionary for {} {}: {}"
                                 "".format(paramcont_type, paramcont_name, paramcont_dico))
                    self.paramcontainers[paramcont_type][paramcont_name].load_config(paramcont_dico)
            else:
                load_instrument_config(dico_config=dico_config,
                                       inst_db_info=self.paramfile_info[paramcont_type],
                                       inst_db=self.paramcontainers[paramcont_type],
                                       model_instance=self)

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
