#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_model module.

The objective of this package is to provides the core Core_Model class.

@DONE:
    -

@TODO:
    - See if it's possible to put or at least partially put get_paramfile_section,
    update_paramfile_info, load_config in paramcontainers_database
"""
from logging import getLogger
from os.path import isfile, join
# from collections import OrderedDict  # , defaultdict
from numpy import array, ones
# from copy import deepcopy

from .datasimulator import DatasimulatorCreator
from .paramcontainers_database import ParamContainerDatabase
from .core_parametrisation import Core_Parametrisation
from .instrument_container import InstrumentContainerInterface
from ..instmodel4dataset import Instmodel4DatasetAttr, Instmodel4Dataset
from ..paramcontainer import Core_ParamContainer, key_params_fileinfo
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ..dataset_and_instrument.instrument import instrument_model_category as instmod_cat
# from ..dataset_and_instrument.instrument import load_instrument_config
# from ..dataset_and_instrument.instrument import get_instrument_paramfilesection
# from ..dataset_and_instrument.instrument import update_instrument_paramfile_info
from ..likelihood.core_likelihood import LikelihoodCreator
from ..likelihood.manager_noise_model import Manager_NoiseModel
from ..prior.model_prior import Model_Prior, joint_prior_name
from ..prior.core_prior import Manager_Prior
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.default_folders_data_run import RunFolder
# from ....tools.miscellaneous import spacestring_like


## Logger
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()
manager_prior = Manager_Prior()
manager_prior.load_setup()
manager_noisemodel = Manager_NoiseModel()
manager_noisemodel.load_setup()

create_key = "create"
load_key = "load"


class Core_Model(Core_ParamContainer, DatasetDbAttr, Model_Prior, RunFolder, InstrumentContainerInterface,
                 ParamContainerDatabase, Instmodel4DatasetAttr, LikelihoodCreator, DatasimulatorCreator,
                 Core_Parametrisation, metaclass=MandatoryReadOnlyAttr):
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
        Model_Prior.__init__(self, self.paramfile_info)  # self.paramfile_info comes from Core_ParamContainer
        # Initialise the instrument models
        self.init_instmodels(l_instmod_fullnames=l_instmod_fullnames)
        # If no instmodel4dataset provided create it and then initialise the instmodel4dataset of
        # the model
        if instmodel4dataset is None:  # 6.
            instmodel4dataset = Instmodel4Dataset(list_datasetnames=(self.dataset_db.
                                                                     get_datasetnames()))
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       lock="instmodel4dataset")
        # Core_Model is a Core_ParamContainer, so set the model name and init through
        # Core_ParamContainer init method
        Core_ParamContainer.__init__(self, name)
        # Initialise datasimcreatorname4instcat which has to be filled in the Model Subclass
        # Define name of the datasimcreator function for each instrument category (key: inst_cat, value: name of datasimcreator method)
        self.__datasimcreatorname4instcat = {}
        # Initialise datasimcreator which has to be filled in the Model Subclass
        # Define the available datasimcreator for the model (key: name, value: datasimcreator docf)
        self.__datasimcreator = {}
        # Intialise handlers4instcatparamfile which has to be filled in the Model Subclass
        # Define the specific param_file handler for each instrument category (key: inst_cat, value: dict(keys: "create" and "load", value: create and load methods))
        self.__handlers4instcatparamfile = {}
        # Initialise paramfile4instcat which has to be file by the create_paramfile function specified in handlers4instcatparamfile
        # Define the path to the parameter file specific to each instrument category if exists (key: inst_cat, value: path of param file)
        self.__paramfile4instcat = {}
        # Initialise parametrisation related attributes
        self.init_parametrisation_attributes()
        # Initialise parameterisation
        self.parametrisation
        # IMPORTANT NOTE THE MODEL CATEGORY IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior.

        TODO: Maybe There is some common initialisation that could be done. TBC
        """
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

    @property
    def handlers4instcatparamfile(self):
        """Dictionary giving the create/load function of the instrument category specific param files.

        key: instrument category, value: dict(key: "create" and "load", value: create and load methods (None if no method))
        """
        return self.__handlers4instcatparamfile

    @property
    def paramfile4instcat(self):
        """Dictionary giving the path of the param file specific to each instrument category.

        key: instrument category, value: path to param file
        """
        return self.__paramfile4instcat

    def isdefined_paramfile_instcat(self, inst_cat):
        """Return True if a param_file for the specified instrument category has been defined.

        :param str inst_cat: Instrument category for which you want to know if the specific param file is defined.
        """
        return self.paramfile4instcat.get(inst_cat, None) is not None

    def init_instmodels(self, l_instmod_fullnames):
        """Create the instrument models."""
        for instmod_fullname in l_instmod_fullnames:
            inst_mod_info = manager_inst.interpret_instmod_fullname(instmod_fullname=instmod_fullname)
            inst = manager_inst.get_inst(inst_name=inst_mod_info["inst_name"], inst_fullcat=inst_mod_info["inst_fullcategory"])
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

    def get_list_params(self, main=False, free=False, no_duplicate=True, recursive=False, **kwargs):
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
        result = []
        # Get parameters that in the model parameters and not in any specific param container
        result.extend(Core_ParamContainer.get_list_params(self, main=main, free=free, no_duplicate=no_duplicate))
        # Get parameters that in the param containers
        if recursive:
            result_in_paramcont_db = ParamContainerDatabase.get_list_params(self, model_instance=self, main=main, free=free, no_duplicate=no_duplicate, **kwargs)
            if no_duplicate:
                result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True) for param_in_res in result]
                for param in result_in_paramcont_db:
                    if param.get_name(include_prefix=True, recursive=True) in result_param_name:
                        result_in_paramcont_db.remove(param)
            result.extend(result_in_paramcont_db)
        return result

    def get_list_paramnames(self, main=False, free=False, recursive=False, no_duplicate=True, **kwargs):
        """Return the list of all parameters names in the model.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param bool recursive: If true (default false) also returns the parameters in the param
            containers of the param container database

        Keyword arguments are passed to the Named.get_name (see docstring for exhaustive information)
        As recursive is a parameter of both get_list_paramnames and Named.get_name, for the recursive
        parameter of Named.get_name use recursive_naming.

        :return list_of_paramname result: list of Parameter instances names
        """
        result = []
        # Change the parameter recursive_naming into recursive is present in kwargs before giving to
        # get_name.
        if "recursive_naming" in kwargs:
            kwargs["recursive"] = kwargs.pop("recursive_naming")
        for param in self.get_list_params(main=main, free=free, recursive=recursive, no_duplicate=no_duplicate):
            result.append(param.get_name(**kwargs))
        return result

    def get_initial_values(self, list_paramnames=None, nb_values=1, output_dico=False):
        """Return initial values for the parameter.

        If value is provided for the parameter this value is returned otherwise a value is stochas-
        tically drawn from the prior.

        :param list_of_str list_paramnames: List of parameter names for which you want initial values.
            The parameter requested should be free, otherwise they will be ignored.
        :param int nb_values: Number of initial values per parameter in the output.
        :param bool output_dico: If True the output is a dictionary which for keys the parameter names
            and for values the initial values.
        :return np.array/dict init_vals: Initial values for the requested free parameters. The dimension
            would be nb_free_param * nb_values
        """
        # Get the list of parameter instances (and parameter name if needed)
        if list_paramnames is None:
            list_params = self.get_list_params(main=True, free=True, recursive=True)
            list_paramnames = [param.get_name(include_prefix=True, recursive=True) for param in list_params]
        else:
            list_params = []
            for param_name in list_paramnames:
                param = self.get_parameter(param_name, main=True, free=True, recursive=True)
                if param is None:
                    raise ValueError("Parameter {} not found in model.".format(param_name))
                else:
                    list_params.append(param)
        # Pass through all the parameter instance. For the ones that don't have a joint prior, compute
        # the initial value(s) and store them in dico_initvals, a dict with for key the parameter name
        # and for value the initial value(s) computed.
        # For the parameters that are joint, store in a dictionary (joint), the joint prior info and
        # a list of parameter names ordered in the same way than the output on the joint prior ravs
        # (method which draw values from the prior)
        dico_initvals = {}
        joint = {}
        for param_name, param in zip(list_paramnames, list_params):
            logger.info("Generate initial positions for param {}".format(param_name))
            if param.joint:
                if param.joint_prior_ref not in joint:
                    joint[param.joint_prior_ref] = {"prior_info": self.joint_prior_container[param.joint_prior_ref],
                                                    "param_name": []}
                    joint_prior_class = manager_prior.get_priorfunc_subclass(joint[param.joint_prior_ref]["prior_info"]["category"])
                    for param_key, multiple in zip(joint_prior_class.param_refs, joint_prior_class.multiple_params):
                        if multiple:
                            joint[param.joint_prior_ref]["param_name"].append(["" for param_ref in joint[param.joint_prior_ref]["prior_info"]["params"][param_key]])
                        else:
                            joint[param.joint_prior_ref]["param_name"].append("")
                else:
                    joint_prior_class = manager_prior.get_priorfunc_subclass(joint[param.joint_prior_ref]["prior_info"]["category"])
                found = False

                for ii, param_key, multiple in zip(range(len(joint_prior_class.param_refs)), joint_prior_class.param_refs, joint_prior_class.multiple_params):
                    if multiple:
                        l_param_refs = joint[param.joint_prior_ref]["prior_info"]["params"][param_key]
                    else:
                        l_param_refs = [joint[param.joint_prior_ref]["prior_info"]["params"][param_key], ]
                    for jj, param_ref in enumerate(l_param_refs):
                        if param.name.is_name(param_ref):
                            found = True
                            break
                    if found:
                        break
                if found:
                    if multiple:
                        joint[param.joint_prior_ref]["param_name"][ii][jj] = param_name
                    else:
                        joint[param.joint_prior_ref]["param_name"][ii] = param_name
                else:
                    raise ValueError("Parameter {} not found in the joint prior {} parameters dictionary {}"
                                     "".format(param.get_name(include_prefix=True, recursive=True),
                                               param.joint_prior_ref, joint[param.joint_prior_ref]["prior_info"]["params"]))
            else:
                if param.value is None:
                    prior_func_cls = manager_prior.get_priorfunc_subclass(param.prior_category)
                    dico_initvals[param_name] = prior_func_cls(**param.prior_args).ravs(nb_values=nb_values)
                else:
                    dico_initvals[param_name] = ones(nb_values) * param.value
                    if dico_initvals[param_name].size == 1:
                        dico_initvals[param_name] = dico_initvals[param_name][0]
        # Produce the initial values for each parameter with the joint priors and store the result in a dictionary
        # with for key the parameter name and for value the initial value(s).
        for joint_prior_ref, dico in joint.items():
            joint_prior_instance = manager_prior.get_priorfunc_subclass(dico["prior_info"]["category"])(dico["prior_info"]["params"], **dico["prior_info"]["args"])
            vals = joint_prior_instance.ravs(nb_values=nb_values)
            for ii, param_name_or_l_param_name in enumerate(joint[joint_prior_ref]["param_name"]):
                if isinstance(param_name_or_l_param_name, list):
                    for jj, param_name in enumerate(param_name_or_l_param_name):
                        dico_initvals[param_name] = vals[ii][jj]
                else:
                    dico_initvals[param_name_or_l_param_name] = vals[ii]
        # Produce the output
        if output_dico:
            return dico_initvals
        else:
            return array([dico_initvals[param_name] for param_name in list_paramnames])

    def get_paramfile_section(self, text_tab="", entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this Model.

        Arguments
        ---------
        text_tab    : str
            text giving the tabulation that needs to be added to this the text to obtain the good alignment
            in the input file.
        entete_symb : str
            Symbol to use after the paramcontainers name
        quote_name  : bool
            Wether to put quote around the paramcontainer name or not.

        Returns
        -------
        text : str
            Text for the parameter file.
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
                text += self.instruments.get_paramfile_section(model_instance=self, text_tab=text_tab,
                                                               entete_symb=entete_symb, quote_name=quote_name)
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

    def update_paramfile_info(self):
        """Update the paramfile info attribute.

        self.paramfile_info is defined in Core_ParamContainer. It's a dictionary which describes the
        expected content of the parameter file.

        TODO: It doesn't seems to be including the joint_prior_dictionary. Check and include if needed.
        """
        self.paramfile_info.clear()  # self.paramfile_info comes from Core_ParamContainer
        # For each paramcontainer in the param container database. Produce the param file section.
        for parcont_type in self.paramcont_categories:
            # Instruments Param containers are a special case
            if parcont_type != instmod_cat:
                self.paramfile_info[parcont_type] = []
                for parcont in self.paramcontainers[parcont_type].values():
                    self.paramfile_info[parcont_type].append(parcont.code_name)
                    parcont.update_paramfile_info()
            else:
                self.paramfile_info[instmod_cat] = {}
                self.instruments.update_paramfile_info(inst_db_info=self.paramfile_info[instmod_cat])
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
        Model_Prior.load_jointprior_config(self, dico_config=dico_config)
        # Load the new configuration from the parameter file for each Paramcontainer and parameter
        logger.debug("List of Core_ParamContainer types in param_file_info: {}"
                     "".format(self.paramfile_info.keys()))
        for paramcont_type in self.paramfile_info.keys():  # self.paramfile_info comes from Core_ParamContainer
            logger.debug("Content of param_file_info for {}: {}"
                         "".format(paramcont_type, self.paramfile_info[paramcont_type]))
            if paramcont_type not in [instmod_cat, key_params_fileinfo, joint_prior_name]:
                for paramcont_name in self.paramfile_info[paramcont_type]:
                    paramcont_dico = dico_config[paramcont_name]
                    logger.debug("Content of param dictionary for {} {}: {}"
                                 "".format(paramcont_type, paramcont_name, paramcont_dico))
                    self.paramcontainers[paramcont_type][paramcont_name].load_config(dico_config=paramcont_dico,
                                                                                     model_instance=self,
                                                                                     available_joint_priors=self.joint_prior_container)
            elif paramcont_type == instmod_cat:
                self.instruments.load_config(dico_config=dico_config,
                                             inst_db_info=self.paramfile_info[paramcont_type],
                                             model_instance=self,
                                             available_joint_priors=self.joint_prior_container)
            else:  # For the model parameters (those who do no belong in any param container)
                super(Core_Model, self).load_config(dico_config=dico_config[self.code_name], model_instance=self,
                                                    available_joint_priors=self.joint_prior_container)

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

        Arguments
        ---------
        paramfile_path   : string
            Path to the param_file.
        answer_overwrite : string
            If the LC_param_file already exists, do you want to overwrite it ? "y" or "n". If this not
            provide the program will ask you interactively.
        answer_create    : string
            If the LC_param_file doesn't exists aleardy, where do you want to create it ? "absolute",
            "run_folder" or "error". If this not provide the program will ask you interactively.
        """
        # Check is the file path provided correspond to an exiting file
        file_path = self.look4runfile(file_path=paramfile_path)
        # If path provided is an existing file, ask if you want to overwrite
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
        # If path provided is not an existing file, ask if you want to created it
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
        # If the file needs to be created
        if reply == "y":
            with open(file_path, 'w') as f:
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                f.write("# Parametrisation file of {}\n".format(self.get_name()))
                f.write("import numpy as np\n\n")
                f.write("# Parameters\n")
                f.write(self.get_paramfile_section())
            logger.info("Parameter file created at path: {}".format(file_path))
        # If the file doesn't need to be created
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(file_path))
            self.update_paramfile_info()
        self.param_file = file_path

    def read_parameter_file(self):
        """Read the content of the parameter file."""
        if self.isdefined_paramfile:
            with open(self.param_file) as f:
                exec(f.read())
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
        dico["paramfile4instcat"] = self.paramfile4instcat
        dico["kwargs_parametrisation"] = self.parametrisation_kwargs
        return dico

    def automatic_model_initialisation(self, param_file, paramfile4instcat, kwargs_parametrisation):
        """load the parameter file."""
        self.param_file = param_file
        for key in paramfile4instcat:
            if isfile(paramfile4instcat[key]):
                self.paramfile4instcat[key] = paramfile4instcat[key]
            else:
                raise AssertionError("File {} doesn't exists".format(paramfile4instcat[key]))
        self.load_instcat_paramfile()
        self.set_parametrisation(**kwargs_parametrisation)
        self.update_paramfile_info()
        self.load_parameter_file()

    def _check_dataset_instcat(self):
        """Check that the instrument categories of the datasets are all handled by the model. """
        if not(self.possible_inst_categories >= set(self.dataset_db.inst_categories)):  # self.possible_inst_categories is defined in the Subclasses of Core_Model
            raise ValueError("Model of category {} cannot simulate data of the following category: {}."
                             " Remove the datasets of this(ese) category(ies) or change the model."
                             "".format(self.category, set(self.dataset_db.inst_categories) - self.possible_inst_categories))

    def create_instcat_paramfile(self, paramfile_path=None, answer_overwrite=None, answer_create=None):
        """Create the param files specific to each instrument category (if needed).

        :param dict_of_str paramfile_path: Dictionary giving the path of the specific parameter file
            you want for an instrument category. (key: inst_cat, value: path to the paramter file)
        :param None/str/dict_of_None/str answer_overwrite: str should be 'y' or 'n. When it's a dictionary
            keys are instrument categories and values are 'y' or 'n'.
        :param None/str/dict_of_None/str answer_create: str should be 'y' or 'n. When it's a dictionary
            keys are instrument categories and values are 'y' or 'n'.
        """
        if paramfile_path is None:
            paramfile_path = {}
        if (answer_overwrite is None) or isinstance(answer_overwrite, str):
            def_answer_overwrite = answer_overwrite
            dict_answer_overwrite = {}
        elif isinstance(answer_overwrite, dict):
            dict_answer_overwrite = answer_overwrite
            def_answer_overwrite = dict_answer_overwrite.get("def", None)
        else:
            ValueError("answer_overwrite should be None, y, n or a dictionary of the previous ones.")
        if (answer_create is None) or isinstance(answer_create, str):
            def_answer_create = answer_create
            dict_answer_create = {}
        elif isinstance(answer_create, dict):
            dict_answer_create = answer_create
            def_answer_create = dict_answer_create.get("def", None)
        else:
            ValueError("answer_overwrite should be None, y, n or a dictionary of the previous ones.")
        for inst_fullcat in self.inst_fullcategories:
            inst_cat, inst_subcat = manager_inst.interpret_inst_fullcat(inst_fullcat=inst_fullcat)
            if self.handlers4instcatparamfile[inst_cat][create_key] is not None:
                self.handlers4instcatparamfile[inst_cat][create_key](paramfile_path.get(inst_cat, None),
                                                                     answer_overwrite=dict_answer_overwrite.get(inst_cat, def_answer_overwrite),
                                                                     answer_create=dict_answer_create.get(inst_cat, def_answer_create))

    def load_instcat_paramfile(self):
        """Load the param files specific to each instrument category (if needed).
        """
        for inst_fullcat in self.inst_fullcategories:
            inst_cat, inst_subcat = manager_inst.interpret_inst_fullcat(inst_fullcat=inst_fullcat)
            if self.handlers4instcatparamfile[inst_cat][load_key] is not None:
                self.handlers4instcatparamfile[inst_cat][load_key]()

    def _choose_parameter_file_path(self, default_paramfile_path, paramfile_path=None, answer_overwrite=None, answer_create=None):
        """Choose the path for any parameter file.

        Arguments
        ---------
        default_paramfile_path : str
            Default name for the parameter file
        paramfile_path      : str
            Path to the indicator parameter file (IND_param_file).
        answer_overwrite    : str
            If the IND_param_file already exists, do you want to
            overwrite it ? "y" or "n". If this is not provided the program will ask you interactively.
        answer_create       : str
            If the IND_param_file doesn't exists already, where do you want
            to create it ? "absolute", "run_folder" or "error". If this not provide the program will ask you interactively.

        Returns
        -------
        file_path : str
            Chosen path for the parameter file
        reply     : str ("y" or "n")
            If "y" this file should be created or overwriten, if "n" not.
        """
        if paramfile_path is None:
            paramfile_path = default_paramfile_path
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
                question += "\nNot create it and raise an 'error' ? {}\n".format(answers_list_create)
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
        return file_path, reply
