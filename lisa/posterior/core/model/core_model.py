"""
core_model module.

The objective of this package is to provides the core Core_Model class.

@DONE:
    -

@TODO:
    - See if it's possible to put or at least partially put get_paramfile_section,
    update_paramfile_info, load_config in paramcontainers_database
"""
from loguru import logger
from os import getcwd
from os.path import isfile, join, basename
from collections import defaultdict  # OrderedDict
from numpy import array, ones
from pprint import pformat
# from copy import deepcopy

from .datasimulator import DatasimulatorCreator
from .paramcontainers_database import ParamContainerDatabase
from .instrument_container import InstrumentContainerInterface
from ..config_file import ConfigFileAttr, ConfigFile
from ..instmodel4dataset import Instmodel4DatasetAttr, Instmodel4Dataset
from ..paramcontainer import Core_ParamContainer, key_params_fileinfo
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..dataset_and_instrument.dataset_database import DatasetDbAttr
from ..dataset_and_instrument.instrument import instrument_model_category as instmod_cat
# from ..dataset_and_instrument.instrument import load_instrument_config
# from ..dataset_and_instrument.instrument import get_instrument_paramfilesection
# from ..dataset_and_instrument.instrument import update_instrument_paramfile_info
from ..likelihood.core_likelihood import LikelihoodCreator
from ..likelihood.GP1D import GP1DContainerInterface
from ..prior.model_prior import Model_Prior
from ..prior.core_prior import Manager_Prior
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.default_folders_data_run import RunFolderAttr, RunFolder
from ....tools.miscellaneous import spacestring_like

# from ....tools.miscellaneous import spacestring_like


manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()
manager_prior = Manager_Prior()
manager_prior.load_setup()

create_key = "create"
load_key = "load"


class Core_Model(Core_ParamContainer, Model_Prior, InstrumentContainerInterface,
                 ParamContainerDatabase, Instmodel4DatasetAttr, LikelihoodCreator, DatasimulatorCreator,
                 ConfigFileAttr, RunFolderAttr,
                 GP1DContainerInterface,
                 metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_Model abstract class."""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "instcat_model_classes", "noise_model_classes", 'has_model_paramfile']
    # category: String which designate the model (for example: "GravitionalGroups"). To choose the
    #   model to be used, the user will use this string.
    # instcat_model_classes: List of InstCat_Model Classes implemented for the Model

    ## Key to use in DatabaseFunc for the function that will concern the whole object to model
    key_whole = "whole"

    ###########################################
    ## Methods for interface with other modules
    ###########################################

    def __init__(self, name, instmodel4dataset, run_folder, config_file, lock=None):
        """Core_Model init method FOR INHERITANCE PURPOSES (as Core_Model is an abstract class).

        This function should be use in the __init__ function of Subclass of this class
        
        Argument
        --------
        name    : str
            Name of the object studied by the model
        """
        # Core_Model is a Core_ParamContainer, so set the model name and init through
        # Core_ParamContainer init method
        Core_ParamContainer.__init__(self, name)
        # Core Model is also a ParamContainer Database, so initialise it
        ParamContainerDatabase.__init__(self)
        # Core Model is also an InstrumentContainer, so initialise it
        InstrumentContainerInterface.__init__(self)
        # Core Model is also a GP1DContainer, so Initialise it
        GP1DContainerInterface.__init__(self)
        # Init the run_folder
        if not(isinstance(run_folder, RunFolder)):
            raise ValueError("run_folder should be a RunFolder instance, the one defined for the Posterior intance (Posterior.run_folder)")
        RunFolderAttr.__init__(self, run_folder=run_folder)
        # Init the config_folder
        if not(isinstance(config_file, ConfigFile)):
            raise ValueError("config_file should be a ConfigFile instance, the one defined for the Posterior intance (Posterior.config_file)")
        ConfigFileAttr.__init__(self, config_file=config_file)
        # Initialise the attributes related to the Prior
        Model_Prior.__init__(self)  # self.paramfile_info comes from Core_ParamContainer
        # Init the instmodel4dataset
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       lock="instmodel4dataset")
        # Initialise the instrument models
        self.__init_instmodels(l_instmod_fullnames=self.instmodel4dataset.name_instmodels_used(inst_name=None, sortby_instname=False, inst_fullcat=None, sortby_instfullcat=None, return_fullname=True))     
        # Check that all datasets correspond to instrument model categories that valid for the model
        self.__check_dataset_instcat()
        # Initialize the dictionary providing the function to get same GP kernel datasets.
        self._same_GP_kernel_function = {}
        # Initialise datasimcreatorname4instcat which has to be filled in the Model Subclass
        # Define name of the datasimcreator function for each instrument category (key: inst_cat, value: name of datasimcreator method)
        self.__datasimcreatorname4instcat = {}
        # Initialise datasimcreator which has to be filled in the Model Subclass
        # Define the available datasimcreator for the model (key: name, value: datasimcreator docf)
        self.__datasimcreator = {}
        # Initialise instcat_models which has to be filled with the InstCat_Model instances available for the model
        # {<inst category>: InstCat_Model subclass instance}
        self.__instcat_models = {}
        # Initialise noise_models which has to be filled with the NoiseModel instances available for the model
        # {<noise model category>: NoiseModel subclass instance}
        self.__noise_models = {}
        # IMPORTANT NOTE THE MODEL CATEGORY IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL
    
    ######################################
    ## Dealing with the configuration file
    ######################################

    # Methods related to the instrument model categories
    ####################################################
    def _configure_model(self):
        """Configure the model
        """
        self._init_instcat_models_and_datasimcreator()

        logger.info("Load instrument category configuration.")
        for inst_cat in self.inst_categories: 
            instcat_model = self.get_instcat_model(inst_cat)
            instcat_model._configure_instcat_model()

    def _init_instcat_models_and_datasimcreator(self):
        """Finish the initialisation of the instrument category models required by the model and the associated datasimulators.

        This function is used in self._configure_model. 
        """   
        # Now load the available InstCat_Models and do the __init__
        for InstCat_Model in self.instcat_model_classes:
            if InstCat_Model.inst_cat in self.get_instcat_used():  # Maybe you should use a method of InstrumentContainerInterface, but get_instcat_used is a method of Instmodel4DatasetAttr
                self.__instcat_models[InstCat_Model.inst_cat] = InstCat_Model(model_instance=self, run_folder=self.run_folder, config_file=self.config_file)
                self.__datasimcreatorname4instcat[InstCat_Model.inst_cat] = InstCat_Model.datasim_creator_name
                self.__datasimcreator[InstCat_Model.datasim_creator_name] = self.__instcat_models[InstCat_Model.inst_cat].datasim_creator

    # Methods related to the noise model categories
    ###############################################

    def _configure_noisemodel(self):
        """Configure the noise models
        """
        logger.info("Load noise model definition.")
        self._load_config(config2load='noisemoddef')

        logger.info("Load noise model categories configuration.")
        self._init_noisemodels()

        for noise_cat in self.noisemodel_categories: # noisemodel_categories is a property of InstrumentContainerInterface as the noise models are stored in the instrument models
            noisemodcat = self.get_noise_model(noise_cat=noise_cat) 
            noisemodcat._configure_noisemodcat_model()

    def _init_noisemodels(self):
        """Finish the initialisation of the noise models required by the model.

        This function is used in self._configure_noisemodel. 
        """   
        # Now load the available InstCat_Models and do the __init__
        for NoiseModel in self.noise_model_classes:
            if NoiseModel.noise_cat in self.noisemodel_categories:  # noisemodel_categories is a property of InstrumentContainerInterface
                self.__noise_models[NoiseModel.noise_cat] = NoiseModel(model_instance=self, run_folder=self.run_folder, config_file=self.config_file)

    # Function that get the function required by  ConfigFileAttr._load_config
    #########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'noisemoddef':
                return self.__add_default_config_var_noisemoddef
            elif config2load == 'duplicates':
                return self.__add_default_config_var_duplicates
            elif config2load == 'frozens':
                return self.__add_default_config_var_frozens
            elif config2load == 'frozen_values':
                return self.__add_default_config_var_frozenvals
            elif config2load == 'priors':
                return self.__add_default_config_var_priors
        elif function_type == 'check_config_exists':
            if config2load == 'noisemoddef':
                return self.__config_var_exist_noisemoddef
            elif config2load == 'duplicates':
                return self.__config_var_exist_duplicates
            elif config2load == 'frozens':
                return self.__config_var_exist_frozens
            elif config2load == 'frozen_values':
                return self.__config_var_exist_frozenvals
            elif config2load == 'priors':
                return self.__config_var_exist_priors
        elif function_type == 'load_config_content':
            if config2load == 'noisemoddef':
                return self.__load_config_var_content_noisemoddef
            elif config2load == 'duplicates':
                return self.__load_config_var_content_duplicates
            elif config2load == 'frozens':
                return self.__load_config_var_content_frozens
            elif config2load == 'frozen_values':
                return self.__load_config_var_content_frozenvals
            elif config2load == 'priors':
                return self.__load_config_var_content_priors
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")

    # Methods for the noise model definition part of the config file
    ################################################################
    def __add_default_config_var_noisemoddef(self, file):
        file.write("\n#########################\n## Noise model definition\n#########################\n"
                   "\n# Noise model for intrument model"
                   "\n#################################\n"
                   "# Define which noise model you want to use for each instrument model\n"
                   "# By default the gaussian noise model is used for all the instrument models\n"
                   "# This is imposed by the fact that below all instrument models have 'gaussian' as entry.\n"
                   "# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].\n"
                   "# If you want to change the noise model used for a given instrument model, just change the value of its key.\n"
                   "# For indicator (IND) instrument models, you can provide None and the model will not try to model the data associated to this instrument.\n"
                   )
        dico = self.instmodel4dataset.name_instmodels_used(sortby_instname=True, sortby_instfullcat=True, return_fullname=False)
        noisemoddef = {}
        for inst_fullcat in dico:
            for inst_name in dico[inst_fullcat]:
                l_instmod_shortname = dico[inst_fullcat][inst_name]
                dico[inst_fullcat][inst_name] = {instmod_shortname: "gaussian" for instmod_shortname in l_instmod_shortname}
            noisemoddef[inst_fullcat] = dict(dico[inst_fullcat])
        tab_noisemoddef = spacestring_like('d_noise_model_def' + " = ")
        file.write("{var} = {content}\n".format(var='d_noise_model_def',
                                                content=pformat(noisemoddef, compact=True).replace('\n', f'\n{tab_noisemoddef}')
                                                )
                   )
        
    def __config_var_exist_noisemoddef(self, dico_config_file):
        return 'd_noise_model_def' in dico_config_file

    def __load_config_var_content_noisemoddef(self, dico_config_file, **kwargs):
        noisemoddef = dico_config_file['d_noise_model_def']
        # Check that the content is valid
        assert isinstance(noisemoddef, dict)
        assert set(noisemoddef.keys()) == set(self.inst_fullcategories)  # self.inst_fullcategories is a property of InstrumentContainerInterface
        for inst_fullcat in noisemoddef:
            info_inst_fullcat = manager_inst.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
            assert isinstance(noisemoddef[inst_fullcat], dict)
            assert set(noisemoddef[inst_fullcat].keys()) == set(self.get_inst_names(inst_fullcat=inst_fullcat))  # get_inst_names is a method of InstrumentContainerInterface
            for inst_name in noisemoddef[inst_fullcat]:
                assert isinstance(noisemoddef[inst_fullcat][inst_name], dict)
                assert set(noisemoddef[inst_fullcat][inst_name].keys()) == set(self.get_instmodel_names(inst_name=inst_name, inst_fullcat=inst_fullcat))
                for instmod_shortname in noisemoddef[inst_fullcat][inst_name]:
                    if not(info_inst_fullcat[0] == "IND" and noisemoddef[inst_fullcat][inst_name][instmod_shortname] is None):
                        assert noisemoddef[inst_fullcat][inst_name][instmod_shortname] in self.possible_noise_model_categories
        # Load it
        for inst_fullcat in noisemoddef:
            for inst_name in noisemoddef[inst_fullcat]:
                for instmod_shortname in noisemoddef[inst_fullcat][inst_name]:
                    inst_mod_obj = self.instruments[inst_fullcat][inst_name][instmod_shortname]
                    inst_mod_obj.noise_model_category = noisemoddef[inst_fullcat][inst_name][instmod_shortname]

    # Methods related to the configuration of the parameters
    ########################################################

    def _configure_parameters(self):
        """Add the priors configuration to the configuration file."""
        logger.info("Load duplicate parameters definition")
        self._load_config(config2load='duplicates')
        logger.info("Load frozen parameters definition")
        self._load_config(config2load='frozens')
        logger.info("Load frozen parameters values definition")
        self._load_config(config2load='frozen_values')
        logger.info("Load parameters priors definition")
        self._load_config(config2load='priors')

    # Methods related to the configuration of the duplicate parameters
    ##################################################################

    def __add_default_config_var_duplicates(self, file):
        file.write("\n###########################"
                   "\n## Parameters configuration"
                   "\n###########################\n"
                   "\n# The list of main parameter full names in the model is:"
                   f"\n# {self.get_list_paramnames(main=True, recursive=True, no_duplicate=False, include_prefix=True, code_version=False, recursive_naming=True)}\n"
                   "\n# Duplicate parameters"
                   "\n######################"
                   "\n# Indicates in the duplicates dictionary which parameters you want to be seen being duplicates of another parameters"
                   "\n# Format: keys are the full name of main parameters that you want to be duplicated."
                   "\n# Values are the list of main parameters full names that you want to be duplicates of the parameter named by the corresponding key.\n"
                   )
        duplicates = {}
        for param in self.get_list_params(main=True, free=False, no_duplicate=False, only_duplicates=True, recursive=True):
            if param.duplicate not in duplicates:
                duplicates[param.duplicate] = []
            duplicates[param.duplicate].append(param.full_name)
        tabs = spacestring_like('duplicates' + " = ")
        file.write("{var} = {content}\n".format(var='duplicates',
                                                content=pformat(duplicates, compact=True).replace('\n', f'\n{tabs}')
                                                )
                   )
        
    def __config_var_exist_duplicates(self, dico_config_file):
        return 'duplicates' in dico_config_file

    def __load_config_var_content_duplicates(self, dico_config_file, **kwargs):
        duplicates = dico_config_file['duplicates']
        l_all_main_parameters_full_name = self.get_list_paramnames(main=True, recursive=True, no_duplicate=False, include_prefix=True, code_version=False, recursive_naming=True)
        for duplicated_param_full_name in duplicates:
            if duplicated_param_full_name not in l_all_main_parameters_full_name:
                raise ValueError(f"In the duplicates dictionary of the configuration file, {duplicated_param_full_name} is not a known main parameter full name.")
            duplicated_param = self.get_parameter(name=duplicated_param_full_name, kwargs_get_list_params={'main': True, 'free': False, 'recursive': True, 'no_duplicate': True},
                                                  kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
            if not(isinstance(duplicates[duplicated_param_full_name], list)):
                raise ValueError(f"In the configuration file duplicates[{duplicated_param_full_name}] should be a list (got {duplicates[duplicated_param_full_name]})")
            for duplicate_param_full_name in duplicates[duplicated_param_full_name]:
                if duplicate_param_full_name not in l_all_main_parameters_full_name:
                    raise ValueError(f"In the duplicates[{duplicated_param_full_name}] list of the configuration file, {duplicate_param_full_name} is not a known main parameter full name.")
                duplicate_param = self.get_parameter(name=duplicate_param_full_name, kwargs_get_list_params={'main': True, 'free': False, 'recursive': True, 'no_duplicate': False},
                                                     kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
                duplicate_param.duplicate = duplicated_param

    # Methods related to the configuration of the frozen parameters
    ###############################################################

    def __add_default_config_var_frozens(self, file):
        file.write("\n# Frozen parameters"
                   "\n###################"
                   "\n# Indicates the list the main parameters full names that you want to freeze."
                   "\n# A frozen parameter will have its value fixed to a given value that you will define in the next step.\n"
                   )
        frozens = []
        for param in self.get_list_params(main=True, free=False, no_duplicate=True, only_duplicates=False, recursive=True):
            if not(param.free):
                frozens.append(param.full_name)
        tabs = spacestring_like('frozens' + " = ")
        file.write("{var} = {content}\n".format(var='frozens',
                                                content=pformat(frozens, compact=True).replace('\n', f'\n{tabs}')
                                                )
                   )
        
    def __config_var_exist_frozens(self, dico_config_file):
        return 'frozens' in dico_config_file

    def __load_config_var_content_frozens(self, dico_config_file, **kwargs):
        frozens = dico_config_file['frozens']
        # Get the list of parameter full names curretly frozen.
        l_param_fullname_to_defreeze = []
        for param in self.get_list_params(main=True, free=False, no_duplicate=True, only_duplicates=False, recursive=True):
            if not(param.free):
                l_param_fullname_to_defreeze.append(param.full_name)
        # Freeze (if necessary) the parameter specified
        l_all_main_parameters_full_name = self.get_list_paramnames(main=True, recursive=True, no_duplicate=False, include_prefix=True, code_version=False, recursive_naming=True)
        for param_full_name in frozens:
            if param_full_name not in l_all_main_parameters_full_name:
                raise ValueError(f"In the frozens list of the configuration file, {param_full_name} is not a known main parameter full name.")
            if param_full_name in l_param_fullname_to_defreeze:
                l_param_fullname_to_defreeze.remove(param_full_name)
            else:
                param = self.get_parameter(name=param_full_name, kwargs_get_list_params={'main': True, 'free': False, 'recursive': True, 'no_duplicate': True},
                                           kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
                param.free = False
        # Defreeze the parameter that where frozen but should not be.
        for param_full_name in l_param_fullname_to_defreeze:
            param = self.get_parameter(name=param_full_name, kwargs_get_list_params={'main': True, 'free': False, 'recursive': True, 'no_duplicate': True},
                                                  kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
            param.free = True
            param.value = None

    def __add_default_config_var_frozenvals(self, file):
        file.write("\n# Indicates the values for the frozens main parameters"
                   "\n# You should not change the unit value. Every changes that you might make to unit will be ignored."
                   "\n")
        frozen_values = {}
        for param in self.get_list_params(main=True, free=False, no_duplicate=True, only_duplicates=False, recursive=True):
            if not(param.free):
                frozen_values[param.full_name] = {'value': param.value, 'unit': param.unit}
        tabs = spacestring_like('frozen_values' + " = ")
        file.write("{var} = {content}\n".format(var='frozen_values',
                                                content=pformat(frozen_values, compact=True).replace('\n', f'\n{tabs}')
                                                )
                   )
        
    def __config_var_exist_frozenvals(self, dico_config_file):
        return 'frozen_values' in dico_config_file

    def __load_config_var_content_frozenvals(self, dico_config_file, **kwargs):
        frozens_values = dico_config_file['frozen_values']
        # Get the list of parameter full names currently frozen.
        l_frozen_param_fullname = []
        for param in self.get_list_params(main=True, free=False, no_duplicate=True, only_duplicates=False, recursive=True):
            if not(param.free):
                l_frozen_param_fullname.append(param.full_name)
        # Freeze (if necessary) the parameter specified
        for param_full_name, dico_param_frozen_values in frozens_values.items():
            if param_full_name not in l_frozen_param_fullname:
                raise ValueError(f"In the frozen_values of the configuration file, {param_full_name} is provided but is not a frozen main parameter full name.")
            else:
                param = self.get_parameter(name=param_full_name, kwargs_get_list_params={'main': True, 'free': False, 'recursive': True, 'no_duplicate': True},
                                           kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
                param.value = dico_param_frozen_values['value']

    # Methods related to the configuration of the parameters priors
    ###############################################################

    def __add_default_config_var_priors(self, file):
        file.write("\n# Priors"
                   "\n########"
                   "\n# The units are provided as information and you should not change it. Any change will be ignored."
                   "\n")
        priors = {}
        for parcont_type in self.paramcont_categories:
            priors[parcont_type] = {}
            for parcont in self.paramcontainers[parcont_type].values():
                if parcont_type != instmod_cat:
                    priors[parcont_type][parcont.full_name] = parcont.priors_dict
                else:
                    priors[parcont_type] = self.instruments.priors_dict
        priors[f"sys_{self.get_name()}"] = self.priors_dict
        priors[self.joint_prior_name] = self.jointprior_config_dict
        tab_priors = spacestring_like('priors' + " = ")
        file.write("{var} = {content}\n".format(var='priors',
                                                content=pformat(priors, compact=True).replace('\n', f'\n{tab_priors}')
                                                )
                   )
        
    def __config_var_exist_priors(self, dico_config_file):
        return 'priors' in dico_config_file

    def __load_config_var_content_priors(self, dico_config_file, **kwargs):
        priors = dico_config_file['priors']
        # Check that the content is valid
        # Check that there is all the required keys at the top level
        set_keys_parameters = set(self.paramcont_categories + [f"sys_{self.get_name()}", self.joint_prior_name])
        if (set_keys_parameters != set(priors.keys())):
            raise ValueError(f"The priors dictionary of the configuration file doesn't have the correct keys: Expect {set_keys_parameters}, got {set(priors.keys())}")
        # Check that each parametercontainer_type in self.paramcont_categories has the correct parameter containers names
        for parcont_type in self.paramcont_categories:
            if (set(self.paramcontainers[parcont_type].keys()) != set(priors[parcont_type].keys())):
                raise ValueError(f"The priors[{parcont_type}] dictionary of the configuration file doesn't have the correct keys: Expect {set(self.paramcontainers[parcont_type].keys())}, got {set(priors[parcont_type].keys())}")
        # Load it
        # load the joint prior configuration
        Model_Prior.load_jointprior_config(self, dico_jointprior_config=priors[self.joint_prior_name])
        # Load the new configuration from the parameter file for each Paramcontainer and parameter
        for parcont_type in self.paramcont_categories:
            for parcont_name in self.paramcontainers[parcont_type]:
                if parcont_type != instmod_cat:
                    self.paramcontainers[parcont_type][parcont_name].load_priors_config(dico_priors_config=priors[parcont_type][parcont_name],
                                                                                        available_joint_priors=self.joint_prior_container)
                else:
                    self.instruments.load_priors_config(dico_priors_config=priors[parcont_type], available_joint_priors=self.joint_prior_container)
        # Load the new configuration for the parameters stored in the model itself
        self.load_priors_config(dico_priors_config=priors[f"sys_{self.get_name()}"], available_joint_priors=self.joint_prior_container)


    ##########################################
    ## Methods to create the instrument models
    ##########################################

    def __init_instmodels(self, l_instmod_fullnames):
        """Create the instrument models."""
        for instmod_fullname in l_instmod_fullnames:
            inst_mod_info = manager_inst.interpret_instmod_fullname(instmod_fullname=instmod_fullname)
            inst = manager_inst.get_inst(inst_name=inst_mod_info["inst_name"], inst_fullcat=inst_mod_info["inst_fullcategory"])
            self.add_an_instrument_model(inst, name=inst_mod_info["inst_model"])


    ##################
    ## Methods to sort
    ##################

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    #####################################################################
    ## Dealing with instrument categories and instrument model categories
    #####################################################################

    @property
    def possible_inst_categories(self):
        """Set of instrument categories handled by the model.
        """
        return set([InstCat_Model.inst_cat for InstCat_Model in self.instcat_model_classes])

    @property
    def instcat_models(self):
        """Dictionary containing the InstCat_Model instances.

        This dictionary initialised filled in the Core_Model.__init__ 
        and filled in the self._init_instcat_models_and_datasimcreator
        called by self._configure_model

        Structure:
        Key: inst_cat (string giving the instrument category)
        values: InstCat_Model instance
        """
        return self.__instcat_models

    def get_InstCatModelClass(self, inst_cat):
        """Return the Core_InstCat_Model subclass corresponding to the instrument category provided

        Arguments
        ---------
        inst_cat    : str
            String giving the category of instrument for which you want the Model class

        Returns
        -------
        InstCat_Model   : Core_InstCat_Model Subclass
            Class of the Model for the instrument category provided
        """
        for InstCat_Model in self.instcat_model_classes:
            if InstCat_Model.inst_cat == inst_cat:
                return InstCat_Model
        raise ValueError("There is no Core_InstCat_Model Subclass corresponding to the instrument category"
                         f" {inst_cat} in this model.")

    def get_instcat_model(self, inst_cat):
        """Return the InstCat_Model instance corresponding to the instrument category provided

        Arguments
        ---------
        inst_cat    : str
            String giving the category of instrument for which you want the Model class

        Returns
        -------
        instcat_model   : InstCat_Model instance
            Model for the instrument category provided
        """
        return self.__instcat_models[inst_cat]

    def __check_dataset_instcat(self):
        """Check that the instrument categories of the datasets are all handled by the model. """
        if not(self.possible_inst_categories >= set(self.get_instcat_used())):  # self.get_instcat_used is defined in Instmodel4DatasetAttr
            raise ValueError("Model of category {} cannot simulate data of the following category: {}."
                             " Remove the datasets of this(ese) category(ies) or change the model."
                             "".format(self.category, set(self.get_instcat_used()) - self.possible_inst_categories))

    ############################
    ## Dealing with noise models
    ############################

    @property
    def noise_models(self):
        """Dictionary containing the NoiseModel instances.

        This dictionary initialised filled in the Core_Model.__init__ 
        and filled in the self._init_noisemodels
        called by self._configure_noisemodel

        Structure:
        Key: noise model category (string giving the noise model category)
        values: NoiseModel instance
        """
        return self.__noise_models

    @property
    def possible_noise_model_categories(self):
        """Set of instrument categories handled by the model.
        """
        return set([Noise_Model.noise_cat for Noise_Model in self.noise_model_classes])
    
    def get_noise_model(self, noise_cat):
        """Return the NoiseModel instance corresponding to the noise model category provided

        Arguments
        ---------
        noise_cat    : str
            String giving the category of instrument for which you want the Model class

        Returns
        -------
        noise_model   : NoiseModel instance
            Model for the instrument category provided
        """
        return self.__noise_models[noise_cat]

    ##########################
    ## Dealing with Parameters
    ##########################

    # Setting parameters/parametrisation acoording to the configuration 
    ###################################################################

    def set_parametrisation(self, **kwargs):
        """Choose the parametrisation to use and apply it.
        """
        self._set_instcat_parameterisation(**kwargs)
        self._set_noisemodelcat_parameterisation(**kwargs)

    def _set_noisemodelcat_parameterisation(self, **kwargs):
        """Apply the parametrisation of the noise models"""
        for noisemodcat in self.noise_models.values():  # noise_models comes from Core_Model
            noisemodcat.set_parametrisation(**kwargs)

    def _set_instcat_parameterisation(self, **kwargs):
        """Apply the parametrisation of the instrument models"""
        for inst_cat_model in self.instcat_models.values():  # instcat_models comes from Core_Model
            inst_cat_model.set_parametrisation(**kwargs)

    # Interacting with parameters
    #############################

    def get_list_params(self, main=False, free=False, no_duplicate=True, only_duplicates=False, recursive=False, **kwargs):
        """Return the list of all parameters.

        Arguments
        ---------
        main            : bool
            If true (default false) returns only the main parameters. If False all parameters are returned.
        free            : bool
            If true (default false) returns only the free parameters. If False, wether or the parameter
            is not free is not used to return it or not. the free argument only makes sense for main parameters,
            so it's ignored if main is not True.
        no_duplicate    : bool
            If True, the output list will not include the duplicate parameters, only the orignals
            no_duplicate and only_duplicates cannot be True at the same time
        only_duplicates : bool
            If True, the output list will only include duplicate parameters (not the original of these duplicates)
            no_duplicate and only_duplicates cannot be True at the same time
        recursive   : bool
            If True (default false) also returns the parameters in the param containers of the
            param container database

        Keyword arguments are given to ParamContainerDatabase.get_list_params (see docstring for information)

        Return
        ------
        result  : list_of_Parameter
            list of Parameter instances
        """
        result = []
        # Get parameters that in the model parameters and not in any specific param container
        result.extend(Core_ParamContainer.get_list_params(self, main=main, free=free, no_duplicate=no_duplicate, only_duplicates=only_duplicates))
        # Get parameters that in the param containers
        if recursive:
            result_in_paramcont_db = ParamContainerDatabase.get_list_params(self, model_instance=self, main=main, free=free, no_duplicate=no_duplicate, only_duplicates=only_duplicates, **kwargs)
            if no_duplicate:
                result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param_in_res in result]
                for param in result_in_paramcont_db:
                    if param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) not in result_param_name:
                        result.append(param)
            else:
                result.extend(result_in_paramcont_db)
        return result

    def get_list_paramnames(self, main=False, free=False, recursive=False, no_duplicate=True, only_duplicates=False, **kwargs):
        """Return the list of all parameters names in the model.

        Arguments
        ---------
        main            : bool
            If true (default false) returns only the main parameters. If False all parameters are returned.
        free            : bool
            If true (default false) returns only the free parameters. If False, wether or the parameter
            is not free is not used to return it or not. the free argument only makes sense for main parameters,
            so it's ignored if main is not True.
        no_duplicate    : bool
            If True, the output list will not include the duplicate parameters, only the orignals
            no_duplicate and only_duplicates cannot be True at the same time
        only_duplicates : bool
            If True, the output list will only include duplicate parameters (not the original of these duplicates)
            no_duplicate and only_duplicates cannot be True at the same time

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
        for param in self.get_list_params(main=main, free=free, recursive=recursive, no_duplicate=no_duplicate, only_duplicates=only_duplicates):
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
            list_params = self.get_list_params(main=True, free=True, recursive=True, no_duplicate=True)
            list_paramnames = [param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param in list_params]
        else:
            list_params = []
            for param_name in list_paramnames:
                param = self.get_parameter(param_name, kwargs_get_list_params={'main': True, 'free': True, 'recursive': True},
                                           kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
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

    #####################################
    ## Dealing with the priors param file
    #####################################

    # def load_config(self, dico_config):
    #     """load the configuration specified by the dictionnary from the parameter_file

    #     :param dict dico_config: Dictionnary containing the new configuration for the main Parameters
    #         read from the parameter file.
    #     """
    #     # load the joint prior configuration
    #     Model_Prior.load_jointprior_config(self, dico_config=dico_config)
    #     # Load the new configuration from the parameter file for each Paramcontainer and parameter
    #     logger.debug("List of Core_ParamContainer types in param_file_info: {}"
    #                  "".format(self.paramfile_info.keys()))
    #     for paramcont_type in self.paramfile_info.keys():  # self.paramfile_info comes from Core_ParamContainer
    #         logger.debug("Content of param_file_info for {}: {}"
    #                      "".format(paramcont_type, self.paramfile_info[paramcont_type]))
    #         if paramcont_type not in [instmod_cat, key_params_fileinfo, joint_prior_name]:
    #             for paramcont_name in self.paramfile_info[paramcont_type]:
    #                 paramcont_dico = dico_config[paramcont_name]
    #                 logger.debug("Content of param dictionary for {} {}: {}"
    #                              "".format(paramcont_type, paramcont_name, paramcont_dico))
    #                 self.paramcontainers[paramcont_type][paramcont_name].load_config(dico_config=paramcont_dico,
    #                                                                                  model_instance=self,
    #                                                                                  available_joint_priors=self.joint_prior_container)
    #         elif paramcont_type == instmod_cat:
    #             self.instruments.load_config(dico_config=dico_config,
    #                                          inst_db_info=self.paramfile_info[paramcont_type],
    #                                          model_instance=self,
    #                                          available_joint_priors=self.joint_prior_container)
    #         else:  # For the model parameters (those who do no belong in any param container)
    #             super(Core_Model, self).load_config(dico_config=dico_config[f"sys_{self.code_name}"], model_instance=self,
    #                                                 available_joint_priors=self.joint_prior_container)

    ##############################
    ## Dealing with datasimulators
    ##############################

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
        """Return the datasimcreator method associated with the instrument category.

        This datasimcreator method is the one that creates the datasimulator functions for the given
        instrument category

        Arguments
        ---------
        inst_cat    : str
            Instrument category for which you want the datasimulator

        Returns
        -------
        datasimcreator  : Method/function
            Function that create the datasimulator function for given instrument category
        """
        datasimcreatorname = self.get_datasimcreatorname(inst_cat)
        return self.datasimcreator[datasimcreatorname]

    ############################
    ## Dealing with noise models
    ############################

    def get_same_GP_kernel_datasets(self, dataset_name):
        """Return the list of datasets that are modeled using the same GP kernel than the dataset provided.

        Arguments
        ---------
        dataset_name :  String
            Name of the dataset of interest.

        Returns
        -------
        l_dataset_name : List of String
            List of dataset names using the same GP kernel than the dataset provided.
        """
        # Get the noise_model category associated with the dataset
        inst_mod_obj = self.get_instmod(dataset_name=dataset_name)  # Comes from Instmodel4DatasetAttr
        noisemod_cat = inst_mod_obj.noise_model
        # Use the function pointed by self__same_GP_kernel_function to get the list of instrument model full name using the same GP kernel
        l_instmod_fullname = self._same_GP_kernel_function[noisemod_cat](instmod_fullname=inst_mod_obj.full_name)
        # Get the list of datasets using these instrument models
        res = []
        for instmod_fullname_ii in l_instmod_fullname:
            res.extend(self.get_ldatasetname4instmodfullname(instmod_fullname=instmod_fullname_ii))  # Defined in Instmodel4DatasetAttr
        return res

    ################
    ## Multi-purpose
    ################

    def _choose_parameter_file_path(self, default_paramfile_name, paramfile_name=None, answer_overwrite=None, answer_create=None):
        """Choose the path for any parameter file.

        Arguments
        ---------
        default_paramfile_name : str
            Default name for the parameter file
        paramfile_name      : str or None
            Name for the parameter file. If None default_paramfile_name is used
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
        if paramfile_name is None:
            paramfile_name = default_paramfile_name
        param_file_path = self.look4runfile(file_path=paramfile_name)
        if param_file_path is not None:
            answers_list_yn = ['y', 'n']
            if answer_overwrite is None:
                question = f"File {paramfile_name} already exists ({param_file_path}). Do you want to overwrite it ? {answers_list_yn}\n"
                reply = QCM_utilisateur(question, answers_list_yn)
            else:
                if answer_overwrite in answers_list_yn:
                    reply = answer_overwrite
                else:
                    raise ValueError("answer_overwrite should by in {}".format(answers_list_yn))
        else:
            answers_list_create = ["create", "error"]
            if not(self.hasrun_folder):
                self.run_folder = getcwd()
            param_file_path = join(self.run_folder, paramfile_name)
            if answer_create is None:
                question = f"File {paramfile_name} doesn't exists. Do you want to\nCreate it in the run_folder ({self.run_folder}) "
                question += (f"\nNot create it and raise an 'error' ?\nReply one of these answers {answers_list_create}\n")
                reply = QCM_utilisateur(question, answers_list_create)
            else:
                if answer_create in answers_list_create:
                    reply = answer_create
                else:
                    raise ValueError(f"answer_create should by in {answers_list_create}")
            if reply == "error":
                raise ValueError(f"File {paramfile_name} doesn't exist and the user doesn't want to create it.")
            reply = "y"
        return param_file_path, reply
