"""
posterior module.

The objective of this package is to provides the core Posterior class.

@ DONE:
    - Posterior.__init__: Doc and UT
    - Posterior.data_folder: Doc and UT
    - Posterior.hasdata_folder: Doc and UT
    - Posterior.dataset_db: Doc and UT
    - Posterior._add_a_dataset: Doc and UT
    - Posterior.rm_dataset: Doc and UT
    - Posterior.add_a_dataset_from_path: Doc and UT
    - Posterior.add_datasets_from_datasetsfile: Doc and UT
@TODO:
    - functions to visualize the content of the dataset database
    - function to add datasets from a folder.
    - add_model, rm_model
    - get_lnprior, get_lnlike, get_lnpost
"""
from loguru import logger
from numpy import inf, isfinite, ones_like
from dill import dump, load
from os.path import join
from os import getcwd, chdir
from textwrap import dedent
from copy import copy, deepcopy
from pprint import pformat
from collections import OrderedDict

from .config_file import ConfigFileAttr
from .dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from .instmodel4dataset import Instmodel4DatasetAttr, Instmodel4Dataset
from .database_instlevelsanddataset import DstDbLockAttr
from .dataset_and_instrument.dataset_database import DatasetDatabase, DatasetDbAttr
from .model import par_vec_name
from .model.manager_model import Manager_Model
from .model.datasimulator_timeseries_toolbox import time_vec
from .database_func import DatabaseFunc, DatabaseInstLvlDataset
from .datasetsfile_db import DatasetsFileDbAttr
from .likelihood_posterior_docfunc import LikelihoodPosteriorDocFunc
from ..exoplanet.model.gravgroup.model import GravGroup
from ...tools.name import Named
from ...tools.default_folders_data_run import RunFolderAttr
from ...tools.function_w_doc import DocFunction
from ...tools.human_machine_interface.standard_questions import ask4CreationDefaultFile
from ...tools.time_series_toolbox import get_time_supersampled, average_supersampled_values
from ...tools.miscellaneous import spacestring_like, get_filename_from_file_path


manager_model = Manager_Model()
manager_model.load_setup()
manager_inst_dst = Manager_Inst_Dataset()
manager_inst_dst.load_setup()

alldtst_key = DatabaseFunc._alldtst_key


class Posterior(Named, RunFolderAttr, DstDbLockAttr, DatasetsFileDbAttr, ConfigFileAttr):
    """Posterior is the main class of lisa.

    It allows to define the datasets that you want to analyse, the model that you want to use to analyse
    these datasets, the noise models that you want to use. Finally, it produces function to simulate
    the datasets (datasimulators), logn priors (lnpriors), logn likelihoods (lnlikelihoods) and logn
    posteriors (lnposteriors).

    An instance of posterior has the following set of attributes:
    - dataset_db: Database for the datasets (empty at init - see definition lisa.posterior.dataset_and_instrument)
    - name: Instance of Name (fully defined at init - see definition lisa.tools.name)
    - run_folder: Define the "run" folder (can be defined at init or later - see definition lisa.tools.default_folders_data_run).
        Folder where the parameter files should be.
    - model: Instance of a Subclass of Core_Model (None at init - see CoreModel definition lisa.posterior.core.model.core_model)
        This should be defined after initialisation using the define_model method.
    - datasetsfile_db: Database containing the content of the dataset file (empty at init - see definition
        lisa.posterior.core.datasetsfile_dbs).
    - datasimulators: Database containing the datasimulator functions.
    - lnpriors: Database containing the lnprior functions.
    - lnlikelihoods: Database containing the lnlikelihood functions.
    - lnposteriors: Database containing the lnposterior functions.

    The traditional sequence of use is:
    >>> post_instance = Posterior(object_name="HD209458")
    >>> post_instance.dataset_db.data_folder = "data_folder"  # Defines the folder where the dataset files are.
    >>> post_instance.run_folder = "run_folder"  # Defines the folder where the parameter files are/will be.
    >>> post_instance.load_datasetsfile("datasets.txt")  # Create the file defining the datasets to be used
    # and the associated instrument and noise models
    >>> post_instance.define_model(category="GravitionalGroups", name="HD209458", stars=1, planets=1)
    # Define the model that you want to use to interpret the data. The arguments depends on the model
    # that you want to use.
    >>> post_instance.model.create_instcat_paramfile()  # Create parameter files specific to the instrument
    # categories used by the datasets to analyse.
    >>> post_instance.model.load_instcat_paramfile()  # Load the parameter files specific to the instrument
    # categories used by the datasets to analyse.
    >>> post_instance.model.set_parametrisation(parametrisation="EXOFAST")  # Define the parametrisation
    # to be used
    >>> post_instance.model.create_parameter_file("param_file.py")  # Create the file defining the priors
    # to be used for each main parameter of the model.
    >>> post_instance.model.load_parameter_file()  # Load the parameter file defining the priors to be used
    # for each main parameter.
    >>> post_instance.get_datasimulators()  # Create the datasimulator functions
    >>> post_instance.get_lnlikelihoods()  # Create the lnlikelihood functions
    >>> post_instance.get_individal_lnpriors()  # Create the individual lnprior functions
    >>> post_instance.get_lnpriors()  # Create the lnprior functions
    >>> post_instance.get_lnposteriors()  # Create the lnposterior functions.
    """

    __model_classes = [GravGroup, ]

    msg_err_datasetdb_notlocked = "You can't use this function if the dataset_db is not frozen."

    #############################
    ## Methods for user interface
    #############################

    def __init__(self, object_name, data_folder=None, run_folder=None):
        """Init method for the Posterior class.

        Arguments
        ---------
        object_name     : str
            Name of the object studied.
        model_category  : str
            Category of the model that you want to use
        model_kwargs    : dict
            Dictionary providing the arguments required for the initialization of the model.
            The required content of this dictionary depends on the model category chosen.
        data_folder     : str
            Specify the folder where the data can be found
        run_folder      : str
            Specify the folder where the run files are/will be located
        """
        # Initialise the model attribute
        # self.__model = None
        # Define the name of the object studied
        Named.__init__(self, name=object_name)
        # Init the run_folder (needs to be after Named.__init__ as it uses the object_name)
        RunFolderAttr.__init__(self, run_folder=run_folder)
        # Define two locks: dataset_lock and database_lock
        DstDbLockAttr.__init__(self, lock_dataset=None, lock_database=None, use_samelock=False)
        # Initialize the dataset database attribute and assign it dataset_lock
        DatasetDbAttr.__init__(self, dataset_db=DatasetDatabase(self.get_name(), data_folder=data_folder,
                                                                lock=self.get_dataset_Lock_instance()))
        # Initialize the configuration file attribute
        ConfigFileAttr.__init__(self)
        # # Initialise the database function attribute: lnprior_db, lnlike_db, lnpost_db,
        # # datasim_db. Asssign them the database_lock and dataset_lock and the instmodel4dataset
        # self.__lnprior_db = DatabaseFunc(object_stored="prior", database_name=self.object_name,
        #                                  instmodel4dataset=self.model.instmodel4dataset,
        #                                  instordered=False, use_samelock=self.samelock,
        #                                  lock_dataset=self.get_dataset_Lock_instance(),
        #                                  lock_database=self.get_database_Lock_instance())
        # self.__lnlike_db = DatabaseFunc(object_stored="likelihood", database_name=self.object_name,
        #                                 instmodel4dataset=self.model.instmodel4dataset,
        #                                 instordered=False, use_samelock=self.samelock,
        #                                 lock_dataset=self.get_dataset_Lock_instance(),
        #                                 lock_database=self.get_database_Lock_instance())
        # self.__lnpost_db = DatabaseFunc(object_stored="posterior", database_name=self.object_name,
        #                                 instmodel4dataset=self.model.instmodel4dataset,
        #                                 instordered=False, use_samelock=self.samelock,
        #                                 lock_dataset=self.get_dataset_Lock_instance(),
        #                                 lock_database=self.get_database_Lock_instance())
        # self.__datasim_db = DatabaseFunc(object_stored="datasimulator",
        #                                  instmodel4dataset=self.model.instmodel4dataset,
        #                                  database_name=self.object_name, instordered=False,
        #                                  use_samelock=self.samelock,
        #                                  lock_dataset=self.get_dataset_Lock_instance(),
        #                                  lock_database=self.get_database_Lock_instance())
        
    def configure_posterior(self, path_config_file=None, cluster=False):
        """Configure the whole posterior using the configuration file.

        The configuration file contains all the configuration for the analysis
        - The list of dataset to analyze
        - All the model configuration
        - All the likelihood configuration
        - The priors of the parameter

        Argument
        --------
        path_config_file   : str
            Path to the configuration file
        cluster         : bool
            Whether or not you are running the code on a cluster where interactions with the
            user is not possible. In this case, you need to have all the configurations files
            already defined.
        """
        logger.info(f"Look for configuration file.")
        self.config_file.path = self.look4runfile(file_path=path_config_file)
        # If doesn't exists offer the possibility to create a default one
        if self.config_file is None:
            logger.info(f"Config file doesn't exist (path provided was {path_config_file})")
            default_file_content = f"# Configuration file for the analysis of {self.get_name()}.\n"
            self.config_file = ask4CreationDefaultFile(path_file=path_config_file, default_file_content=default_file_content, default_folder=self.get_run_folder())

        logger.info(f"Load datasets.")
        self._load_config(config2load='datasets')

        logger.info(f"Load instrument models definition.")
        instmodel4dataset = self._load_config(config2load='instmoddef')

        logger.info("Load model category definition.")
        self._load_config(config2load='modelcatdef', instmodel4dataset=instmodel4dataset)

        self.model._configure_model()

        self.model._configure_noisemodel()

        logger.info("11. Set parametrisation of the model")
        self.model.set_parametrisation()

        logger.info("12. Create and modify the paramerisation file")
        if cluster:
            self.model.create_parameter_file("param_file.py", answer_overwrite="n", answer_create=None)
        else:
            self.model.create_parameter_file("param_file.py")

            input("Modifiy the paramerisation file")

        logger.info("13. Load the paramerisation file")
        self.model.load_parameter_file()

    ############################################################
    ## Methods and properties used by the user interface methods
    ############################################################

    # Methods for the datasets part of the config file
    ##################################################

    def __add_default_config_var_datasets(self, file):
        file.write("\n###########\n## Datasets\n###########\n\n# List of the paths to the dataset files that you want to use\n")
        file.write(f"l_dataset = []\n")    

    def __config_var_exist_datasets(self, dico_config_file):
        return 'l_dataset' in dico_config_file    

    def __load_config_var_content_datasets(self, dico_config_file, **kwargs):
        datasets_var = dico_config_file['l_dataset']
        # Check that the content is valid
        assert isinstance(datasets_var, list)
        assert all([isinstance(dst, str) for dst in datasets_var])
        # Load it
        self.dataset_db._add_datasets_from_listdatasetpath(dico_config_file['l_dataset'])

    # Methods for the instrument model definition part of the config file
    #####################################################################
    def __add_default_config_var_instmoddef(self, file):
        file.write("\n##############################\n## Instrument model definition\n##############################\n"
                   "# Define which instrument model you want to use for each dataset\n"
                   "# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument\n"
                   "# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.\n"
                   "# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0').\n"
                   )
        dico = self.dataset_db.get_datasetnbs(inst_name=None, inst_fullcat=None, sortby_instname=True, sortby_instfullcat=True)
        instmoddef = {}
        for inst_fullcat in dico:
            for inst_name in dico[inst_fullcat]:
                l_dst_nb = dico[inst_fullcat][inst_name]
                dico[inst_fullcat][inst_name] = {dst_nb: "inst" for dst_nb in l_dst_nb}
            instmoddef[inst_fullcat] = dict(dico[inst_fullcat])
        tab_instmoddef = spacestring_like('d_inst_model_def' + " = ")
        file.write("{instmoddef} = {content}\n".format(instmoddef='d_inst_model_def',
                                                       content=pformat(instmoddef, compact=True).replace('\n', f'\n{tab_instmoddef}')
                                                       )
                   )
        
    def __config_var_exist_instmoddef(self, dico_config_file):
        return 'd_inst_model_def' in dico_config_file

    def __load_config_var_content_instmoddef(self, dico_config_file, **kwargs):
        instmoddef_var = dico_config_file['d_inst_model_def']
        # Check that the content is valid
        assert isinstance(instmoddef_var, dict)
        assert set(instmoddef_var.keys()) == set(self.dataset_db.inst_fullcategories)
        for inst_fullcat in instmoddef_var:
            assert isinstance(instmoddef_var[inst_fullcat], dict)
            assert set(instmoddef_var[inst_fullcat].keys()) == set(self.dataset_db.get_instnames(inst_fullcat=inst_fullcat))
            for inst_name in instmoddef_var[inst_fullcat]:
                assert isinstance(instmoddef_var[inst_fullcat][inst_name], dict)
                assert set(instmoddef_var[inst_fullcat][inst_name].keys()) == set(self.dataset_db.get_datasetnbs(inst_fullcat=inst_fullcat, inst_name=inst_name))
                for dst_nb in instmoddef_var[inst_fullcat][inst_name]:
                    assert isinstance(instmoddef_var[inst_fullcat][inst_name][dst_nb], str)
        # Load it
        l_inst_model_shortname = []
        l_dataset_fullname = []
        for dataset in self.dataset_db.get_datasets(inst_name=None, inst_fullcat=None, sortby_instcat=False,
                                                    sortby_instname=False, sortby_nb=False):
            dataset_name = manager_inst_dst.dataset_name_from_file_name(dataset.filename)
            l_dataset_fullname.append(dataset_name)
            # Extract, instrument category, instrument name, ... from the dataset filename
            dataset_info = manager_inst_dst.interpret_data_filename(dataset.filename)
            inst_fullcat = dataset_info["inst_fullcat"]
            inst_name = dataset_info["inst_name"]
            dst_nb = dataset_info["number"]
            l_inst_model_shortname.append(instmoddef_var[inst_fullcat][inst_name][str(dst_nb)])
        return Instmodel4Dataset(list_datasetnames=l_dataset_fullname, list_instmodels=l_inst_model_shortname, lock=self.get_dataset_Lock_instance())
    
    # Methods for the model category definition part of the config file
    ###################################################################
    def __add_default_config_modelcategory(self, file):
        """Add the default config for the parametrisation specific to the model category in the configuration file.

        This function is stored in Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables
        """
        file.write("\n####################################\n## Model category definition\n####################################\n"
                   f"# Define the model category and the parameters of the model that are specfic to the model category.\n"
                   f"\n# Available model categories are {manager_model.get_available_models()}\n"
                   )
        file.write("model_category = 'GravitionalGroups'\n")          
        # This function needs to be overloaded in the Model subclasses that requierts parameterisation specific to the model category

    def __config_var_exist_modelcategory(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables
        """
        return 'model_category' in dico_config_file
    
    def __load_config_var_content_modelcategory(self, dico_config_file, **kwargs):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables
        """
        Model_Class = self._get_ModelClass(model_category=dico_config_file['model_category'])
        self.__model = Model_Class(name=self.get_name(), lock=self.get_dataset_Lock_instance(), instmodel4dataset=kwargs["instmodel4dataset"],
                                   run_folder=self.run_folder, config_file=self.config_file)

    # Other methods and properties
    ##############################
    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'datasets':
                return self.__add_default_config_var_datasets
            elif config2load == 'instmoddef':
                return self.__add_default_config_var_instmoddef
            elif config2load == 'modelcatdef':
                return self.__add_default_config_modelcategory
        elif function_type == 'check_config_exists':
            if config2load == 'datasets':
                return self.__config_var_exist_datasets
            elif config2load == 'instmoddef':
                return self.__config_var_exist_instmoddef
            elif config2load == 'modelcatdef':
                return self.__config_var_exist_modelcategory
        elif function_type == 'load_config_content':
            if config2load == 'datasets':
                return self.__load_config_var_content_datasets
            elif config2load == 'instmoddef':
                return self.__load_config_var_content_instmoddef
            elif config2load == 'modelcatdef':
                return self.__load_config_var_content_modelcategory
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")
    
    def _get_ModelClass(self, model_category):
        """Set of model categories available.
        """
        for Model_Class in self.__model_classes:
            if Model_Class.category == model_category:
                return Model_Class
        raise ValueError(f"There is no Core_Model Subclass corresponding to the model category"
                         f" {model_category} provided.")
            

    ####################################
    ## Convenience function for the user
    ####################################

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.get_name()

    @property
    def possible_model_categories(self):
        """Set of model categories available.
        """
        return set([Model_Class.category for Model_Class in self.__model_classes])
    
    @property
    def model(self):
        """Return the model."""
        return self.__model

    def _load_noisemodelsfile(self, path_noise_models_file=None):
        """Load the noise models file

        The noise models file define which noise model will be used by which instrument model

        Argument
        --------
        path_noise_models_file: None or str
            If None the function will offer the possibility to create a default instrument models file
            It str, should be the path to an existing noise model file.

        Return
        ------
        noisemod4instmodfullname: dict of NoiseModel instance

        """
        # Look for the noise models file to check if it exists
        file_path = self.look4runfile(file_path=path_noise_models_file)
        # If doesn't exists offer the possibility to create a default one
        if file_path is None:
            logger.info("{} doesn't exist.".format(path_noise_models_file))
            # Create the text for the file
            default_file_content = "# Define which noise model you want to use for each instrument model\n# By default the gaussian noise model is used for all the instrument models"
            default_file_content += "# This is imposed by the fact that below all instrument models have 'gaussian' as entry.\n"
            default_file_content += "# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].\n"
            default_file_content += "# If you want to change the noise model used for a given instrument model, just change the value of its key.\n"
            dico = self.instmodel4dataset.name_instmodels_used(sortby_instname=True, sortby_instfullcat=True, return_fullname=False)
            for inst_fullcat in dico:
                for inst_name in dico[inst_fullcat]:
                    l_instmod_shortname = dico[inst_fullcat][inst_name]
                    dico[inst_fullcat][inst_name] = {instmod_shortname: "gaussian" for instmod_shortname in l_instmod_shortname}
                header_instfullcat = f"{inst_fullcat} = "
                tab_instfullcat = spacestring_like(header_instfullcat)
                default_file_content += "{inst_fullcat} = {dico}\n".format(inst_fullcat=inst_fullcat, 
                                                                           dico=pformat(dict(deepcopy(dico[inst_fullcat])), compact=True).replace('\n', f'\n{tab_instfullcat}')
                                                                           )
            file_path = ask4CreationDefaultFile(path_file=path_noise_models_file, default_file_content=default_file_content,
                                                default_folder=self.get_run_folder())
            input("Modifiy the noise model file")
        # Read the instrument models file
        cwd = getcwd()
        chdir(self.get_run_folder())
        with open(file_path) as ff:
            exec(ff.read())
        chdir(cwd)
        dico = locals().copy()
        for var_name in ["self", "cwd", "ff", "file_path", "path_noise_models_file"]:
            dico.pop(var_name)
        logger.debug(f"Noise model file ({file_path}) parameter file read.\nContent of the parameter file: {dico.keys()}")
        # Create noisemodcat4instmodfullname. Dict with the keys being instrument model full names and values being noise model subclasses 
        l_inst_model_fullname = []
        l_noisemodel_subclass = [] 
        for inst_fullcat in self.datasetsfile_db.inst_fullcategories:
            for inst_name in dico[inst_fullcat]:
                for instmod_shortname in dico[inst_fullcat][inst_name]:
                    l_noisemodel_subclass.append(manager_noisemodel.get_noisemodel_subclass(dico[inst_fullcat][inst_name][instmod_shortname]))
                    l_inst_model_fullname.append(f"{inst_fullcat}_{inst_name}_{instmod_shortname}")
        return {instmod_fullname: noisemod_subclass for instmod_fullname, noisemod_subclass in zip(l_inst_model_fullname, l_noisemodel_subclass)}

    def _define_model(self, category, load_setup=False, **kwargs):
        """Set/Initialize the model.

        :param str category: String which refers to an available Core_Model Subclass that has been
            defined in the model_setup_file.
        :param bool load_setup: If True load the list of available Models from the model_setup_file.

        Keywords arguments are passed to the Core Model subclass for its initialisation.
        """
        # Load the model_setup_file.py to get all the available  models
        if load_setup:
            manager_model.load_setup()
        # If the name of the object studied by the model is not provided put default
        if "name" not in kwargs:
            kwargs.update({"name": "Target"})
        # Get the CoreModel subclass associated to the provided category
        logger.info("Defining new model of category {}...".format(category))
        model_subclass = manager_model.get_model_subclass(category)
        # Get the dictionary giving the noise model category associated to each instrument model
        # (designated by their full name)
        noisemod4instmodfullname = self.datasetsfile_db.get_noisemod4instmodfullname()
        # Create the model instance
        self.__model = model_subclass(dataset_db=self.dataset_db, run_folder=self.get_run_folder(),
                                      instmodel4dataset=self.instmodel4dataset,
                                      l_instmod_fullnames=list(noisemod4instmodfullname.keys()),
                                      **kwargs)
        self.model.set_noisemodels(noisemod4instmodfullname=noisemod4instmodfullname)
        self.lock()
        logger.info("Model defined with name {} !".format(self.model.get_name()))

    def _lock(self):
        """Lock the dataset_db and update instmodel4dataset attributes.
        """
        list_datasetnames = self.dataset_db.get_datasetnames()
        # update datasets in instmodel4dataset attribute in model.
        self.instmodel4dataset.update(list_datasetnames)
        # update datasets in datasim_db.
        self.datasimulators.update_datasets()
        # update datasets in lnprior_db.
        self.lnpriors.update_datasets()
        # update datasets in lnlike_db.
        self.lnlikelihoods.update_datasets()
        # update datasets in lnpost_db.
        self.lnposteriors.update_datasets()
        # Lock everything
        super(Posterior, self).dataset_lock()  # 7.

    def _unlock(self):
        """Unlock the dataset_db."""
        super(Posterior, self).unlock()

    @property
    def islocked_dataset_db(self):
        """True if dataset_db is frozen."""
        return self.dataset_db.locked

    def rm_model(self):
        """Remove a model."""
        self.__model = None
        self.dataset_db.unlock()

    @property
    def isdefined_model(self):
        """True if a model is defined."""
        return self.model is not None

    @property
    def lnpriors(self):
        """Lnprior database."""
        return self.__lnprior_db

    def get_individal_lnpriors(self):
        """Get individual lnpriors from the model and store them into lnpriors."""
        if self.islocked_dataset_db:
            self.lnpriors.individual = self.model.create_individual_lnpriors()
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    def get_lnpriors(self):
        """Get joint lnpriors from the model and store them into lnpriors."""
        if self.islocked_dataset_db:
            if not(hasattr(self.lnpriors, "individual")):
                logger.info("Creating individual lnpriors")
                self.get_individal_lnpriors()
            logger.info("Creating lnpriors for all entry in self.lnpriors.instrument_db")
            (self.lnpriors.instrument_db.
             update(self.model.create_lnpriors(lnlike_db=self.lnlikelihoods.instrument_db,
                                               individual_priors=self.lnpriors.individual)))
            logger.info("Creating lnpriors for all entry in self.lnpriors.dataset_db")
            (self.lnpriors.dataset_db.
             update(self.model.
                    create_lnpriors_perdataset(individual_priors=self.lnpriors.individual,
                                               lnlike_db_dtst=self.lnlikelihoods.dataset_db)))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def datasimulators(self):
        """Datasimulator database."""
        return self.__datasim_db

    def get_datasimulators(self):
        """Get datasimulators from the model and store them into datasimulators."""
        if self.islocked_dataset_db:
            self.datasimulators.instrument_db.update(self.model.create_datasimulators())  # self.model.create_datasimulators is defined in Datasimulator
            (self.datasimulators.dataset_db.
             update(self.model.create_datasimulators_perdataset(dataset_db=self.dataset_db)))
            (self.datasimulators.dataset_db
             [alldtst_key]) = (self.model.
                               create_datasimulator_alldatasets(dataset_db=self.dataset_db))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def lnlikelihoods(self):
        """Return the current content lnprior database."""
        return self.__lnlike_db

    def get_lnlikelihoods(self):
        """Get lnlikes from the model and store them into lnlikelihoods."""
        if self.islocked_dataset_db:
            # Since for now I cannot produce lnlike for datasim that doesn't include the dataset
            # kwargs, I cannot fill the instrument_db in self.likelihoods
            # datasim_db = self.datasimulators.instrument_db
            # db_lnlike = self.model.create_lnlikelihoods(datasim_inst_db=datasim_db)
            # self.lnlikelihoods.instrument_db.update(db_lnlike)

            # Create the lnlikelihood function for each dataset. This in uses all the datasets in
            # datasimulators.dataset_db, it includes the "all" dataset which includes all the datasets.
            db_lnlike, db_decorr_like = self.model.create_lnlikelihoods_perdataset(datasim_db_dtset=(self.datasimulators.dataset_db))
            self.lnlikelihoods.dataset_db.update(db_lnlike)  # create_lnlikelihoods_perdataset is defined in LikelihoodCreator
            self.datasimulators.dataset_db.unlock()
            for dataset_name, decorr_funcs in db_decorr_like.items():
                for func_shortname in decorr_funcs.keys():
                    self.datasimulators.dataset_db[f"{dataset_name}_{func_shortname}_like"] = decorr_funcs[func_shortname]
            self.datasimulators.dataset_db.lock()
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    def compute_model(self, tsim, dataset_name, param, l_param_name, key_obj=None, datasim_kwargs=None,
                      supersamp=1, exptime=30 / (24 * 60), include_gp=False):
        """Function to compute the models of one dataset for display purposes.

        Arguments
        ---------
        tsim           : np.array
        dataset_name   : String
        param          : np.array
        l_param_name   : List of String
        datasim_kwargs : Dictionary
        supersamp      : Integer
        exptime        : Float
        include_gp     : Bool
            If True and if the noise model includes a gp, the function will output model_wGP, gp_pred
            and gp_pred_var on top of model

        Returns
        -------
        model : np.array
        model_wGP : np.array
        gp_pred : np.array
        gp_pred_var : np.array
        """
        # Supersample the time if needed
        if supersamp > 1:
            t_model = get_time_supersampled(tsim, supersamp, exptime)
        else:
            t_model = tsim

        # If datasim_kwargs is None affect an empty dict and no additional arguments will be passed to
        # the datasim function
        if datasim_kwargs is None:
            datasim_kwargs = {}

        # Get the datasimulator corresponding to the dataset
        if key_obj is None:
            key_obj = self.model.key_whole
        instmod_fullname = self.model.get_instmod_fullname(dataset_name=dataset_name)
        if key_obj in self.datasimulators.instrument_db[instmod_fullname]:
            datasim_docfunc = self.datasimulators.instrument_db[instmod_fullname][key_obj]

            # Compute the model values for each time
            idx_param_datasim = []
            datasim_function = datasim_docfunc.function
            datasim_paramnames = datasim_docfunc.param_model_names_list
            for par in datasim_paramnames:
                idx_param_datasim.append(l_param_name.index(par))
            if f"{time_vec}" in datasim_docfunc.mand_kwargs_list:
                mand_kwargs = {"t": t_model}
            else:
                mand_kwargs = {}
            model = datasim_function(param[idx_param_datasim], **mand_kwargs, **datasim_kwargs)
            if f"{time_vec}" not in datasim_docfunc.mand_kwargs_list:
                model = model * ones_like(t_model)

            # De-supersamp the model if needed.
            if supersamp > 1:
                model = average_supersampled_values(model, supersamp)

            # Get the noise model subclass associated with the dataset
            inst_mod_fullname = self.model.get_instmod_fullname(dataset_name)
            inst_mod_obj = self.model.instruments[inst_mod_fullname]
            noise_model_subclass = manager_noisemodel.get_noisemodel_subclass(inst_mod_obj.noise_model)

            # Compute GP contribution if needed.
            if noise_model_subclass.has_GP and include_gp:
                # Get the list of datasets using the same GP kernel
                l_dataset_sameGP = self.model.get_same_GP_kernel_datasets(dataset_name=dataset_name)  # Defined in Core_model
                # Create the datasimulator for these datasets which we will need to create the GP simulatiop.
                # For that you need the list of dataset_object
                # At the same time we will get the corresponding list of instrument objects required by for the gp simulator creation
                l_dataset_obj = []
                l_instmod_obj = []
                for dataset_name_ii in l_dataset_sameGP:
                    l_dataset_obj.append(self.dataset_db[dataset_name_ii])
                    l_instmod_obj.append(self.model.get_instmod(dataset_name_ii))  # Define in Instmodel4DatasetAttr
                model_allsameGPkernel = self.model.create_datasimulator_4_ldataset(l_dataset_obj=l_dataset_obj)[self.model.key_whole]

                # Create the gp_simulator function
                # For that I need the list of the parameter full names for the datasimulator
                l_datasim_param_fullname = model_allsameGPkernel.param_model_names_list
                gp_simulator, f_format_param, datasets_kwargs, l_params_new = noise_model_subclass.create_gpsimulator_and_formatinputs(model_instance=self.model, l_instmod_obj=l_instmod_obj, l_dataset_obj=l_dataset_obj, l_datasim_param_fullname=l_datasim_param_fullname, l_provided_param_fullname=l_param_name)

                # Compute the simulated data
                # For that I need the list of the indexes of the datasimulator parameter in the provided list pf parameters
                l_idx_param_datasim = []
                for param_fullname_ii in l_datasim_param_fullname:
                    l_idx_param_datasim.append(l_param_name.index(param_fullname_ii))
                sim_data = model_allsameGPkernel(param[l_idx_param_datasim])
                gp_pred, gp_pred_var = gp_simulator(sim_data=sim_data,
                                                    param_noisemod=f_format_param(param),
                                                    l_datakwargs=datasets_kwargs,
                                                    tsim=t_model)
                if supersamp > 1:
                    gp_pred = average_supersampled_values(gp_pred, supersamp)
                    gp_pred_var = average_supersampled_values(gp_pred_var, supersamp)

                model_wGP = model + gp_pred

            else:
                model_wGP = None
                gp_pred = None
                gp_pred_var = None

            if include_gp:
                return model, model_wGP, gp_pred, gp_pred_var
            else:
                return model
        else:
            logger.warning(f"{key_obj} doesn't exists in datasimulators.instrument_db.")
            if include_gp:
                return None, None, None, None
            else:
                return None

    @property
    def lnposteriors(self):
        """Return the current content lnprior database."""
        return self.__lnpost_db

    def get_lnposteriors(self):
        """Get lnposts from the model and store them into lnposteriors."""
        if self.islocked_dataset_db:
            (self.lnposteriors.instrument_db.
             update(self.create_lnposteriors(lnlike_db=self.lnlikelihoods.instrument_db,
                                             lnprior_db=self.lnpriors.instrument_db)))
            (self.lnposteriors.dataset_db.
             update(self.
                    create_lnposteriors_perdataset(lnprior_db_dtset=self.lnpriors.dataset_db,
                                                   lnlike_db_dtset=self.lnlikelihoods.dataset_db)))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    def _create_lnposterior(self, lnlike_func, lnprior_func):
        """Return the log posterior function."""
        arg_list = lnlike_func.arg_list.copy()

        def lnpost(p, data, data_err, **kwarg_data):
            lnprior_val = lnprior_func.function(p)
            if not isfinite(lnprior_val):
                return -inf
            return lnlike_func.function(p, data, data_err, **kwarg_data) + lnprior_val

        return DocFunction(function=lnpost, arg_list=arg_list)

    def create_lnposteriors(self, lnlike_db, lnprior_db, affectinstmodel4dataset=False,
                            lock_db=False):
        """Return the posterior for each instrument model used."""
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="posterior", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        # if lnlike_db is None:
        #     lnlike_db = self.model.create_lnlikelihoods(datasim_db=datasim_db,
        #                                                 category="wo jitter")
        for inst_cat in lnlike_db:
            for inst_name in lnlike_db[inst_cat]:
                for inst_model in lnlike_db[inst_cat][inst_name]:
                    db[inst_cat][inst_name][inst_model] = {}
                    for obj in lnlike_db[inst_cat][inst_name][inst_model]:
                        lnlike = lnlike_db[inst_cat][inst_name][inst_model][obj]
                        lnprior = lnprior_db[inst_cat][inst_name][inst_model][obj]
                        lnpost = self._create_lnposterior(lnlike_func=lnlike, lnprior_func=lnprior)
                        db[inst_cat][inst_name][inst_model][obj] = lnpost
        if lock_db:
            db.lock()
        return db

    def create_lnposteriors_perdataset(self, lnprior_db_dtset, lnlike_db_dtset):
        """Create the log likelihood function with the data hardcoded."""
        db = {}
        for dataset_name in lnprior_db_dtset:
            if lnprior_db_dtset[dataset_name] is None:
                logger.warning(f"Posterior for dataset {dataset_name} could not be created because lnprior is not available.")
                continue
            lnprior_func = lnprior_db_dtset[dataset_name].function
            if lnlike_db_dtset[dataset_name] is None:
                logger.warning(f"Posterior for dataset {dataset_name} could not be created because lnplikelihood is not available.")
                continue
            lnlike_docfunc = lnlike_db_dtset[dataset_name]

            def lnpost_withdataset_creator(prior_func, like_func):
                def lnpost_withdataset(p_vect, *args, **kwargs):
                    lnprior_val = prior_func(p_vect)
                    # logger.debug("lnprior: {}".format(lnprior_val))
                    if not isfinite(lnprior_val):
                        return -inf
                    else:
                        lnlike_val = like_func(p_vect, *args, **kwargs)
                        if not isfinite(lnlike_val):
                            logger.error("lnlike: {}".format(lnlike_val))
                            logger.error(f"params lnpost ({len(p_vect)}): {p_vect}")
                        return lnlike_val + lnprior_val
                        # return like_func(p_vect, *args, **kwargs) + lnprior_val
                return lnpost_withdataset

            mand_kwargs_list = copy(lnlike_docfunc.mand_kwargs_list)
            if par_vec_name in mand_kwargs_list:
                mand_kwargs_list.remove(par_vec_name)
            db[dataset_name] = LikelihoodPosteriorDocFunc(function=lnpost_withdataset_creator(prior_func=lnprior_func, like_func=lnlike_docfunc.function),
                                                          param_model_names_list=lnlike_docfunc.param_model_names_list,
                                                          params_model_vect_name=par_vec_name,
                                                          inst_cats_list=lnlike_docfunc.inst_cats_list,
                                                          inst_model_fullnames_list=lnlike_docfunc.inst_model_fullnames_list,
                                                          dataset_names_list=lnlike_docfunc.dataset_names_list,
                                                          noisemodel_names_list=lnlike_docfunc.noisemodel_names_list,
                                                          include_dataset_kwarg=lnlike_docfunc.include_dataset_kwarg,
                                                          mand_kwargs_list=mand_kwargs_list,
                                                          opt_kwargs_dict=lnlike_docfunc.opt_kwargs_dict
                                                          )

        return db

    _extension_postinstance = "_posterior_instance.pk"

    def save_post_instance(self, pickle_folder=".", pickle_filename=None):
        """Save the instance (the constituent of the instance) into a pickle file.

        :param str pickle_folder: path to the folder containing the pickle file.
        :param str pickle_filename: Name of the posterior instance pickle file
        """
        # strcture to store the informations about the Posterior instance
        dico = {}
        dico["object_name"] = self.object_name
        dico["data_folder"] = self.dataset_db.data_folder
        dico["run_folder"] = self.get_run_folder()
        dico["dataset_file"] = self.datasetsfile_db.datasetsfile_path
        dico["model_category"] = self.model.category
        dico["model_kwargs"] = self.model.init_kwargs
        dico["model_auto_init_kwargs"] = self.model.automatic_init_kwargs

        # Save it to a pickle
        if pickle_filename is None:
            pickle_filename = "{}{}".format(self.object_name, self._extension_postinstance)
        with open(join(pickle_folder, pickle_filename), "wb") as fpostinst:
            dump(dico, fpostinst)

    def init_from_pickle(self, pickle_folder=".", pickle_filename=None, data_folder=None, run_folder=None):
        """Initialize the instance from the post_instance pickle file produced with save_post_instance.

        :param str pickle_folder: path to the folder containing the pickle file.
        :param str pickle_filename: Name of the posterior instance pickle file
        """
        # load the dictionary
        if pickle_filename is None:
            pickle_filename = "{}{}".format(self.object_name, self._extension_postinstance)
        with open(join(pickle_folder, pickle_filename), "rb") as fdico:
            dico = load(fdico)
        # define data and run folder
        if data_folder is None:
            data_folder = dico["data_folder"]
        if run_folder is None:
            run_folder = dico["run_folder"]
        self.dataset_db.data_folder = data_folder
        self.set_run_folder(run_folder=run_folder)
        # load datasetfile
        self.load_datasetsfile(dico["dataset_file"])
        # define model
        # Temporary fix for define_model not taking transit_model and rv_model as argument anymore.
        # transit_model = dico["model_kwargs"].pop("transit_model", None)  # For compatibility with previsous version
        # rv_model = dico["model_kwargs"].pop("rv_model", None)  # For compatibility with previsous version
        self.define_model(category=dico["model_category"], name=dico["object_name"],
                          **dico["model_kwargs"])
        # Automatic model_init: Set parameterisation, set param_file and inst_cat_param_file and load them
        self.model.automatic_model_initialisation(**dico["model_auto_init_kwargs"])
        self.get_datasimulators()
        self.get_lnlikelihoods()
        self.get_individal_lnpriors()
        self.get_lnpriors()
        self.get_lnposteriors()

    # Code to add all datasets in a folder
    # # Examine data folder to look for available datasets
    # folder_content = os.listdir(folder)
    # logger.info("List the content of {}:\n{}".format(folder, folder_content))
    # for content in folder_content:
    # if not(os.path.isfile(os.path.join(folder, content))):
    #     logger.info("Content is not a file and is ignored: {}".format(content))
    # else:
    #     try:
    #         # Check if filename is in the list of datasets specified by the datasets_files
    #         if l_input_files_provided:
    #             if content not in l_files:
    #                 logger.info("Content ignored because not in the datasets files: {}"
    #                             "".format(content))
    #                 continue
    #         filename_info = interpret_data_filename(content)
    #         # Check if filename is compatible with file name convention
    #         if filename_info is None:
    #             continue
    #         # Check if the target associated with the file is the good one
    #         if filename_info["target"] != self.target_name:
    #             logger.warning("Content target is not the provided target "
    #                            "and is ignored: {}".format(content))
    #             continue
    #         # Build a dataset (RV, LightCurve, ...) instance and store in datasets
    #         # dictionnaries
    #         key = build_dataset_key(filename_info["instrument"],
    #                                 number=filename_info["number"])
    #         inst_type = filename_info["type"]
    #         if inst_type == "LC":
    #             self.lc_datasets[key] = LightCurve(content, data_folder=folder)
    #             logger.info("Content accepted as LC datasets files and as been loaded: {}\n"
    #                         "".format(content))
    #         elif inst_type == "RV":
    #             self.rv_datasets[key] = RV(content, data_folder=folder)
    #             logger.info("Content accepted as RV datasets files and as been loaded: {}\n"
    #                         "".format(content))
    #         elif inst_type == "SED":
    #             logger.warning("Data file type SED not implemented yet.")
    #             continue
    #         # Build an instrument instance (if needed) and store in isntruments
    #         # dictionnaries
    #         inst_name = filename_info["instrument"]
    #         inst_exist, _ = self.isin_instruments(inst_name)
    #         logger.info("Instrument {} exists already: {}".format(inst_name, inst_exist))
    #         if not inst_exist:
    #             if inst_type == "LC":
    #                 self.lc_instruments[inst_name] = Instrument(inst_name, inst_type)
    #             elif inst_type == "RV":
    #                 self.rv_instruments[inst_name] = Instrument(inst_name, inst_type)
    #     except:
    #         raise}

    # Possible function to interact with datasets.
    # def get_LC_dataset_keys(self):
    #     """Return the list of light-curve dataset_key available."""
    #     return list(self.lc_datasets.keys())
    #
    # def get_RV_dataset_keys(self):
    #     """Return the list of radial velocity dataset_key available."""
    #     return list(self.rv_datasets.keys())
    #
    # def get_dataset_keys(self):
    #     """Return a dictionnary with the lists of LC, RV (and SED) dataset_key available."""
    #     return {"LC": self.get_LC_dataset_keys(),
    #             "RV": self.get_RV_dataset_keys()}
    #
    # def get_LC_instrument_keys(self):
    #     """Return the list of light-curve instruments available."""
    #     return list(self.lc_instruments.keys())
    #
    # def get_RV_instrument_keys(self):
    #     """Return the list of radial velocity instruments available."""
    #     return list(self.rv_instruments.keys())
    #
    # def get_instrument_keys(self):
    #     """Return a dictionnary with the lists of LC, RV (and SED) isntrument_key available."""
    #     return {"LC": self.get_LC_instrument_keys(),
    #             "RV": self.get_RV_instrument_keys()}
    #
    # def get_LC_dataset_keys_perinstrument(self):
    #     """Return a dictionnary with the lists of LC dataset_key per isntrument."""
    #     lc_keys = self.get_LC_dataset_keys()
    #     result = {}
    #     for key in lc_keys:
    #         key_info = interpret_dataset_key(key)
    #         if key_info["instrument"] in result.keys():
    #             result[key_info["instrument"]].append(key)
    #         else:
    #             result[key_info["instrument"]] = [key]
    #
    # def get_RV_dataset_keys_perinstrument(self):
    #     """Return a dictionnary with the lists of LC dataset_key per isntrument."""
    #     rv_keys = self.get_RV_dataset_keys()
    #     result = {}
    #     for key in rv_keys:
    #         key_info = interpret_dataset_key(key)
    #         if key_info["instrument"] in result.keys():
    #             result[key_info["instrument"]].append(key)
    #         else:
    #             result[key_info["instrument"]] = [key]
    #
    # def isin_LC_datasets(self, key):
    #     """Indicate if the LC dataset designed by key is exisiting and loaded."""
    #     return key in self.lc_datasets
    #
    # def isin_RV_datasets(self, key):
    #     """Indicate if the RV dataset designed by key is exisiting and loaded."""
    #     return key in self.rv_datasets
    #
    # def isin_datasets(self, key):
    #     """Indicate if the dataset designed by key is exisiting and loaded and if yes
    #     which type."""
    #     if self.isin_LC_datasets(key):
    #         return True, "LC"
    #     elif self.isin_RV_datasets(key):
    #         return True, "RV"
    #     else:
    #         return False, None
    #
    # def isin_LC_instruments(self, key):
    #     """Indicate if the LC instrument designed by key is exisiting."""
    #     return key in self.lc_instruments
    #
    # def isin_RV_instruments(self, key):
    #     """Indicate if the RV instrument designed by key is exisiting."""
    #     return key in self.rv_instruments
    #
    # def isin_instruments(self, key):
    #     """Indicate if the instrument designed by key is exisiting and if yes which type."""
    #     if self.isin_LC_instruments(key):
    #         return True, "LC"
    #     elif self.isin_RV_instruments(key):
    #         return True, "RV"
    #     else:
    #         return False, None
