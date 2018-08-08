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
from collections import OrderedDict  # , defaultdict
from numpy import array
# from copy import deepcopy

from .datasimulator import DatasimulatorCreator
from .paramcontainers_database import ParamContainerDatabase
from .instrument_container import InstrumentContainerInterface
from ..instmodel4dataset import Instmodel4DatasetAttr, Instmodel4Dataset
from ..paramcontainer import Core_ParamContainer, key_params_fileinfo
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ..dataset_and_instrument.instrument import instrument_model_category as instmod_cat
from ..dataset_and_instrument.instrument import load_instrument_config
from ..dataset_and_instrument.instrument import get_instrument_paramfilesection
from ..dataset_and_instrument.instrument import update_instrument_paramfile_info
from ..dataset_and_instrument.instrument import interpret_instmod_fullname
from ..likelihood.core_likelihood import LikelihoodCreator
from ..likelihood.manager_noise_model import Manager_NoiseModel
from ..prior.model_prior import Model_Prior, joint_prior_name
from ..prior.manager_prior import Manager_Prior
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.default_folders_data_run import RunFolder
from ....tools.miscellaneous import spacestring_like


## Logger
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()
manager_prior = Manager_Prior()
manager_prior.load_setup()
manager_noisemodel = Manager_NoiseModel()
manager_noisemodel.load_setup()


class Core_Model(Core_ParamContainer, DatasetDbAttr, Model_Prior, RunFolder, InstrumentContainerInterface,
                 ParamContainerDatabase, Instmodel4DatasetAttr, LikelihoodCreator,
                 DatasimulatorCreator, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_Model abstract class."""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "possible_inst_categories"]
    # category: String which designate the model (for example: "GravitionalGroups"). To choose the
    #   model to be used, the user will use this string.
    # possible_inst_categories: Set of the categories of data that the model can simulate
    #   (for example: {"RV", "LC"} for "GravitionalGroups")

    ## Key to use in DatabaseFunc for the function that will concern the whole object to model
    key_whole = "whole"

    def __init__(self, name, dataset_db, run_folder=None, instmodel4dataset=None,
                 l_instmod_fullnames=[]):
        """Core_Model init method FOR INHERITANCE PURPOSES (as Core_Model is an abstract class).

        :param string name: Name of the Core_Model
        :param DatasetDatabase dataset_db: DatasetDatabase giving the dataset to be modeled.
        :param string/None run_folder: Folder to use as run folder. For more info check run_folder
        :param Instmodel4Dataset/None instmodel4dataset:
        :param list_of_string l_instmod_fullnames: list of instrument model full names

        """
        # Core_Model is a Core_ParamContainer, so set the model name and init through
        # Core_ParamContainer init method
        Core_ParamContainer.__init__(self, name)

        # Model needs to access the datasets so give model the dataset_db attribute
        DatasetDbAttr.__init__(self, dataset_db)
        if not(self.isdefined_datasetdb):
            raise ValueError("You need to provide a DatasetDatabase to create a model !")

        # Intialise the run_folder property
        RunFolder.__init__(self, run_folder=run_folder)

        # Core Model is also a ParamContainer Database, so initialise it
        ParamContainerDatabase.__init__(self)

        # Core Model is also an InstrumentContainer, so initialise it
        InstrumentContainerInterface.__init__(self)

        # Initialise the attributes related to the Prior
        Model_Prior.init(self, self.paramfile_info)

        # Initialise the instrument models
        self.init_instmodels(l_instmod_fullnames=l_instmod_fullnames)

        # If no instmodel4dataset provided create it and then initialise the instmodel4dataset of
        # the model
        if instmodel4dataset is None:  # 6.
            instmodel4dataset = Instmodel4Dataset(list_datasetnames=(self.dataset_db.
                                                                     get_datasetnames()))
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       lock="instmodel4dataset")

        # Initialise datasimcreatorname4instcat which as to be overwriten in the Model Subclass
        self.__datasimcreatorname4instcat = {}

        # Initialise datasimcreator which as to be overwriten in the Model Subclass
        # Define the available datasimcreator for the model (key: name, value: datasimcreator docf)
        self.__datasimcreator = {}

        # IMPORTANT NOTE THE MODEL CATEGORY IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        raise NotImplementedError("You need to create this property for your model !")

    @property
    def datasimcreatorname4instcat(self):
        """Dictionary giving the name of the datasimulator for each instrument category.

        key: instrument category, value: datasimcreator name
        """
        return self.__datasimcreatorname4instcat

    @property
    def datasimcreator(self):
        """Dictionary giving the datasimcreator function for each datasimcreator name.

        key: datasimcreator name, value: datasimcreator docfunction
        """
        return self.__datasimcreator

    def get_datasimcreatorname(self, inst_cat):
        """Return the name of the datasimcreator (without_instrument?) function associated with
        the instrument category.

        :param inst_cat string: Instrument category
        :return datasimcreator_name string: Datasimcreator name
        """
        return self.__datasimcreatorname4instcat[inst_cat]

    def get_datasimcreator(self, inst_cat):
        """Return the datasimcreator docfunc (without_instrument?) associated with the instrument
        category.

        :param inst_cat string: Instrument category
        :return datasimcreator_name string: Datasimcreator name
        """
        datasimcreatorname = self.get_datasimcreatorname(inst_cat)
        return self.datasimcreator[datasimcreatorname]

    def init_instmodels(self, l_instmod_fullnames):
        """Create the instrument models."""
        for instmod_fullname in l_instmod_fullnames:
            inst_mod_info = interpret_instmod_fullname(instmod_fullname)
            inst = manager_inst.get_instrument(inst_mod_info["inst_name"])
            self.add_an_instrument_model(inst, name=inst_mod_info["inst_model"])

    def set_noisemodels(self, noisemod4instmodfullname):
        """If necessary, add a default instrument model for each instrument used.
        1. For each instrument used in the dataset database
            2. Check if there is at least one instrument model associated
                2a. If no, add one called default
                2b. If yes, do nothing
        ----
        Arguments:
            noisemod4instmodfullname: dict,
                Give the noise model name associated to the instrument model full name
        """
        logger.debug("noisemod4instmodfullname: {}".format(noisemod4instmodfullname))
        for instmod_fullname, noise_model in noisemod4instmodfullname.items():
            self.instruments[instmod_fullname].noise_model = noise_model
            noise_model_subclass = manager_noisemodel.get_noisemodel_subclass(noise_model)
            noise_model_subclass.apply_parametrisation(model_instance=self,
                                                       instmod_fullname=instmod_fullname)

    def get_noisemodandinstmod4dataset(self):
        """Return the dictionary giving the noise model subclass for each dataset.

        :return dict res: Dictionary, key = dataset name, value = dict:
            key = "noise model", value = noise model subclass
            key = "instrument model", value = instrument model
        """
        res = {}
        for dataset_name in self.instmodel4dataset:
            inst_mod = self.get_instmod(dataset_name)
            res[dataset_name]["instrument model"] = inst_mod
            (res[dataset_name]
             ["noise model"]) = manager_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
        return res

    def get_param(self, full_name):
        """Return the instance of the Parameter designated by full_name.

        :param str full_name:
        """
        logger.debug("Parameter full name: {}".format(full_name))
        full_name_split = full_name.split("_")
        if len(full_name_split) > 2:
            for paramcont_cat in self.paramcont_categories:
                if paramcont_cat is not instmod_cat:
                    obj_name, subobj_name, param_name = full_name_split
                    if subobj_name in self.paramcontainers[paramcont_cat]:
                        if (self.paramcontainers[paramcont_cat][subobj_name].
                           has_parameter(name=param_name)):
                                return (self.paramcontainers[paramcont_cat][subobj_name].
                                        parameters[param_name])

                else:
                    inst_name, inst_model, param_name = full_name_split
                    inst_db = self.instruments
                    inst_model = inst_db["{}_{}".format(inst_name, inst_model)]
                    if inst_model is not None:
                        return inst_model.parameters[param_name]
        else:
            obj_name, param_name = full_name_split
            if self.has_parameter(param_name):
                return self.parameters[param_name]

    def get_list_params(self, main=False, free=False, recursive=False, **kwargs):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param bool recursive: If true (default false) also returns the parameters in the param
            containers of the param container database

        Keyword arguments are given to ParamContainerDatabase.get_list_params (see docstring for
        exhaustive information. Below I describe some of these.
        :param dict inst_models : Dictionnary which for each instrument name give the list of the
                names of instrument models for which you want the params.
                Default = all instrument models used

        :return list_of_param result: list of Parameter instances
        """
        kwargs_CoreParamContainer = kwargs.copy()
        result = []
        # Get parameters that in the model parameters and not in any specific param container
        result.extend(Core_ParamContainer.get_list_params(self, main=main, free=free))
        # Get parameters that in the param containers
        if recursive:
            result.extend(ParamContainerDatabase.get_list_params(self, main=main, free=free, **kwargs))
        return result

    def get_list_paramnames(self, main=False, free=False, recursive=False, **kwargs):
        """Return the list of all parameters names in the model.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param bool recursive: If true (default false) also returns the parameters in the param
            containers of the param container database

        Keyword arguments are passed to the Name.get_name (see docstring for exhaustive information)
        Below is the description of some of these:
        :param bool full_name: If True (default False) return the full name of the parameter
        :param bool code_name: If True (default False) return the code version of the name of the parameter
        :param bool prefix: If True (default False) return the prefix of the full name of the parameter
            This argument and full_name cannot be true at the same time

        :return list_of_paramname result: list of Parameter instances names
        """
        result = []
        for param in get_list_params(self, main=main, free=free, recursive=recursive):
            result.append(param.get_name(**kwargs))
        return result

    def get_initial_values(self, list_paramnames=None, sortby_paramfullname=False):
        """Return intial values for the parameter.

        If value is provided for the parameter this value is returned otherwise a value is stochas-
        tically drawn from the prior.
        """
        if list_paramnames is None:
            l_param_main_free = self.get_list_params(main=True, free=True, recursive=True)
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

        :param str text_tab: text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        :param str entete_symb: Symbol to use after the paramcontainers name
        :param bool quote_name: Wether to put quote around the paramcontainer name or not.
        :return str text: Text for the parameter file.
        """
        text = ""
        # For each paramcontainer in the param container database. Produce the param file section.
        for parcont_type in self.paramcont_categories:
            text += "{}# {}\n".format(text_tab, parcont_type)
            # Instruments Param containers are a special case
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
        # Produce the param file section for the parameter of the model which are not in
        # any specific paramcontainer
        text += "# {}\n\n".format(self.category)
        text += super(Core_Model, self).get_paramfile_section(text_tab=text_tab, texttab_1tline=False,
                                                              entete_symb=" = ", quote_name=False,
                                                              recursive=False)
        # Produce the text to introduce the joint paramaters distribution section
        text += "\n" + self.get_paramfile_section_jointprior()

        self.update_paramfile_info()
        return text

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute.

        TODO: The recursive argument doesn't seems to be used here
        """
        self.paramfile_info.clear()
        # For each paramcontainer in the param container database. Produce the param file section.
        for parcont_type in self.paramcont_categories:
            # Instruments Param containers are a special case
            if parcont_type != instmod_cat:
                self.paramfile_info[parcont_type] = []
                for parcont_name, parcont in self.paramcontainers[parcont_type].items():
                    self.paramfile_info[parcont_type].append(parcont_name)
                    parcont.update_paramfile_info()
            else:
                self.paramfile_info[instmod_cat] = {}
                update_instrument_paramfile_info(inst_db_info=self.paramfile_info[instmod_cat],
                                                 inst_db=self.paramcontainers[parcont_type])
        # Finally update the paramfile_info for the params in the model itself (which are not in any)
        # specific paramcontainer
        super(Core_Model, self).update_paramfile_info()
        logger.debug("Updated paramfile info for {}.\nParamfile_info: {}"
                     "".format(self.name, self.paramfile_info))

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary

        :param dict dico_config: Dictionnary containing the new configuration for the main Parameters
            read from the parameter file.
        """
        # load the joint prior configuration
        Model_Prior.load_jointprior_config(dico_config=dico_config)
        # Load the new configuration from the parameter file for each Paramcontainer and parameter
        logger.debug("List of Core_ParamContainer types in param_file_info: {}"
                     "".format(self.paramfile_info.keys()))
        for paramcont_type in self.paramfile_info.keys():
            logger.debug("Content of param_file_info for {}: {}"
                         "".format(paramcont_type, self.paramfile_info[paramcont_type]))
            if paramcont_type not in [instmod_cat, key_params_fileinfo, joint_prior_name]:
                for paramcont_name in self.paramfile_info[paramcont_type]:
                    paramcont_dico = dico_config[paramcont_name]
                    logger.debug("Content of param dictionary for {} {}: {}"
                                 "".format(paramcont_type, paramcont_name, paramcont_dico))
                    self.paramcontainers[paramcont_type][paramcont_name].load_config(paramcont_dico)
            elif paramcont_type == instmod_cat:
                load_instrument_config(dico_config=dico_config,
                                       inst_db_info=self.paramfile_info[paramcont_type],
                                       inst_db=self.paramcontainers[paramcont_type],
                                       model_instance=self)
            else:  # For the model parameters (those who do no belong in any param container)
                super(Core_Model, self).load_config(dico_config=dico_config[self.name_code])

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

    def create_parameter_file(self, paramfile_path, answer_overwrite=None, answer_create=None):
        """Create the parameter file.

        :param string paramfile_path: Path to the param_file.
        :param string answer_overwrite: If the LC_param_file already exists, do you want to
            overwrite it ? "y" or "n". If this not provide the program will ask you interactively.
        :param string answer_create: If the LC_param_file doesn't exists aleardy, where do you want
            to create it ? "absolute", "run_folder" or "error". If this not provide the program will
            ask you interactively.
        """
        file_path = self.look4runfile(file_path=paramfile_path)
        if file_path is not None:
            answers_list_yn = ['y', 'n']
            if answer_overwrite is None:
                question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                            "".format(file_path, answers_list_yn))
                reply = QCM_utilisateur(question, answers_list_yn)
            else:
                if answer_overwrite in answers_list_yn:
                    reply = answer_overwrite
                else:
                    raise ValueError("answer_overwrite should by in {}".format(answers_list_yn))
        else:
            answers_list_create = ["absolute", "error"]
            if self.hasrun_folder:
                answers_list_create.append("run_folder")
                run_folder_path = join(self.run_folder, paramfile_path)
            if answer_create is None:
                question = ("File {} doesn't exists. Do you want to\nCreate it at the 'absolute' path: "
                            "{}".format(paramfile_path, paramfile_path))
                if self.hasrun_folder:
                    question += "\nCreate it at the 'run_folder' path: {}".format(run_folder_path)
                question += ("\nNot create it and raise an 'error' ?\nReply one of these answers {}\n"
                             "".format(answers_list_create))
                reply = QCM_utilisateur(question, answers_list_create)
            else:
                if answer_create in answers_list_create:
                    reply = answer_create
                else:
                    raise ValueError("answer_create should by in {}".format(answers_list_create))
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

    @property
    def automatic_init_kwargs(self):
        """Return a dictionary giving the keyword arguments for automatic_model_initialisation."""
        dico = {}
        dico["param_file"] = self.param_file
        return dico

    def automatic_model_initialisation(self, param_file):
        """load the parameter file."""
        self.param_file = param_file
        self.update_paramfile_info()
        self.load_parameter_file()

    def _check_dataset_instcat(self):
        """Check that the instrument categories of the datasets are all handled by the model. """
        if not(self.possible_inst_categories >= set(self.dataset_db.inst_categories)):
            raise ValueError("Model of category {} cannot simulate data of the following category: {}."
                             " Remove the datasets of this(ese) category(ies) or change the model."
                             "".format(self.category, set(self.dataset_db.inst_categories) - self.possible_inst_categories))
