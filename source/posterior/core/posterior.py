#!/usr/bin/python
# -*- coding:  utf-8 -*-
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
from logging import getLogger
from numpy import inf
from dill import dump, load
from os.path import join
from textwrap import dedent

from .instmodel4dataset import Instmodel4DatasetAttr
from .database_instlevelsanddataset import DstDbLockAttr
from .dataset_and_instrument.dataset_database import DatasetDatabase, DatasetDbAttr
from .model.manager_model import Manager_Model
from .database_func import DatabaseFunc, DatabaseInstLvlDataset
from .datasetsfile_db import DatasetsFileDbAttr
from ...tools.name import Named
from ...tools.default_folders_data_run import RunFolder
from ...tools.function_w_doc import DocFunction
from ...tools.human_machine_interface.QCM import QCM_utilisateur


logger = getLogger()

manager_model = Manager_Model()
manager_model.load_setup()

alldtst_key = DatabaseFunc._alldtst_key


class Posterior(DatasetDbAttr, Named, RunFolder, Instmodel4DatasetAttr, DstDbLockAttr,
                DatasetsFileDbAttr):
    """docstring for Posterior."""

    msg_err_datasetdb_notlocked = "You can't use this function if the dataset_db is not frozen."

    def __init__(self, object_name, run_folder=None):
        """Init method for the Posterior class.

        :param str object_name : Name of the object studied.
        :param str/None run_folder: Path to the run folder
        """
        # Define the name of the object studied
        Named.__init__(self, name=object_name)
        # Define two locks: dataset_lock and database_lock
        DstDbLockAttr.__init__(self, lock_dataset=None, lock_database=None, use_samelock=False)
        # Initialize the dataset database attribute and assign it dataset_lock
        DatasetDbAttr.__init__(self,
                               dataset_db=DatasetDatabase(self.get_name(),
                                                          lock=self.get_dataset_Lock_instance()))
        # Initialize the run_folder attribute
        RunFolder.__init__(self, run_folder=run_folder)
        # Initialize instmodel4dataset attribute and assign it dataset_lock
        Instmodel4DatasetAttr.__init__(self, lock=self.get_dataset_Lock_instance())
        DatasetsFileDbAttr.__init__(self, object_name=self.object_name,
                                    instmodel4dataset=self.instmodel4dataset)
        # Initialise the model attribute
        self.__model = None
        # Initialise the database function attribute: lnprior_db, lnlike_db, lnpost_db,
        # datasim_db. Asssign them the database_lock and dataset_lock and the instmodel4dataset
        self.__lnprior_db = DatabaseFunc(object_stored="prior", database_name=self.object_name,
                                         instmodel4dataset=self.instmodel4dataset,
                                         instordered=False, use_samelock=self.samelock,
                                         lock_dataset=self.get_dataset_Lock_instance(),
                                         lock_database=self.get_database_Lock_instance())
        self.__lnlike_db = DatabaseFunc(object_stored="likelihood", database_name=self.object_name,
                                        instmodel4dataset=self.instmodel4dataset,
                                        instordered=False, use_samelock=self.samelock,
                                        lock_dataset=self.get_dataset_Lock_instance(),
                                        lock_database=self.get_database_Lock_instance())
        self.__lnpost_db = DatabaseFunc(object_stored="posterior", database_name=self.object_name,
                                        instmodel4dataset=self.instmodel4dataset,
                                        instordered=False, use_samelock=self.samelock,
                                        lock_dataset=self.get_dataset_Lock_instance(),
                                        lock_database=self.get_database_Lock_instance())
        self.__datasim_db = DatabaseFunc(object_stored="datasimulator",
                                         instmodel4dataset=self.instmodel4dataset,
                                         database_name=self.object_name, instordered=False,
                                         use_samelock=self.samelock,
                                         lock_dataset=self.get_dataset_Lock_instance(),
                                         lock_database=self.get_database_Lock_instance())
        # TODO: This looks like it's not used ! IF not also suppress noisemodels property below
        self.__noisemodel_db = DatabaseFunc(object_stored="noise model",
                                            instmodel4dataset=self.instmodel4dataset,
                                            database_name=self.object_name, instordered=False,
                                            use_samelock=self.samelock,
                                            lock_dataset=self.get_dataset_Lock_instance(),
                                            lock_database=self.get_database_Lock_instance())

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.get_name()

    @property
    def run_folder(self):
        """The run_folder is the folder where the program will look for config files and put
        outputs. It can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the run_folder is
              automatically define as "input_run_folder/object_name". To use this you should assign
              "default"
            - Via the run_folder argument: You can provide any folder here via the run_folder
              argument.
        If not defined, return None.
        """
        return super(Posterior, self).run_folder

    @run_folder.setter
    def run_folder(self, run_folder="default"):
        """Set the run_folder attribute."""
        super(Posterior, self.__class__).run_folder.fset(self, run_folder)
        if self.hasrun_folder:
            self.dataset_db.run_folder = self.run_folder
            if self.isdefined_model:
                self.model.run_folder = self.run_folder

    @property
    def model(self):
        """Return the model."""
        return self.__model

    def load_datasetsfile(self, path_datasets_file):
        file_path = self.look4runfile(file_path=path_datasets_file)
        if file_path is None:
            logger.info("{} doesn't exist.".format(path_datasets_file))
            answers_list_yn = ['y', 'n']
            question = ("File {} doesn't exist. Do you want to create it ? {}\n"
                        "".format(path_datasets_file, answers_list_yn))
            reply = QCM_utilisateur(question, answers_list_yn)
            if reply == "y":

                answers_list_create = ["absolute", "error"]
                question = ("File {} doesn't exists. Do you want to\nCreate it at the 'absolute' "
                            "path: {}".format(path_datasets_file, path_datasets_file))
                if self.hasrun_folder:
                    answers_list_create.append("run_folder")
                    run_folder_path = join(self.run_folder, path_datasets_file)
                    question += "\nCreate it at the 'run_folder' path: {}".format(run_folder_path)
                question += ("\nNot create it and raise an 'error' ? {}\n"
                             "".format(answers_list_create))
                reply2 = QCM_utilisateur(question, answers_list_create)
                if reply2 == 'absolute':
                    file_path = path_datasets_file
                elif reply2 == "run_folder":
                    file_path = join(self.run_folder, path_datasets_file)
                else:
                    raise ValueError("File {} doesn't exist and the user doesn't want to create it."
                                     "".format(path_datasets_file))
                with open(file_path, 'x') as fdatasets:
                    header = """
                    # Datasets file: List below all the files you want to use for this run
                    # The first columns is the path to a dataset file
                    # The second columns is the name of the instrument model used for this dataset
                    # The third column is the noise model.
                    """
                    header = dedent(header[1:-1])
                    fdatasets.write(header)
                input("Modifiy the dataset file")
        self.datasetsfile_db.load(file_path)
        self.dataset_db._add_datasets_from_listdatasetpath(self.datasetsfile_db.dataset_filepaths)

    def define_model(self, category, load_setup=False, **kwargs):
        """Set/Initialize the model.

        For now only assignement to None is possible.
        This function should check that the category is an available Core_Model Subclass

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
            kwargs.update({"name": "default"})
        # Get the CoreModel subclass associated to the provided category
        logger.info("Defining new model of category {}...".format(category))
        model_subclass = manager_model.get_model_subclass(category)
        # Get the dictionary giving the noise model category associated to each instrument model
        # (designated by their full name)
        noisemod4instmodfullname = self.datasetsfile_db.get_noisemod4instmodfullname()
        # Create the model instance
        self.__model = model_subclass(dataset_db=self.dataset_db, run_folder=self.run_folder,
                                      instmodel4dataset=self.instmodel4dataset,
                                      l_instmod_fullnames=list(noisemod4instmodfullname.keys()),
                                      **kwargs)
        self.model.set_noisemodels(noisemod4instmodfullname=noisemod4instmodfullname)
        self.lock()
        logger.info("Model defined with name {} !".format(self.model.get_name()))

    def lock(self):
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

    def unlock(self):
        """Unlock the dataset_db."""
        super(Posterior, self).unlock()

    @property
    def islocked_dataset_db(self):
        """Return True if dataset_db is frozen."""
        return self.dataset_db.locked

    def rm_model(self):
        """Remove a model."""
        self.__model = None
        self.dataset_db.unlock()

    @property
    def isdefined_model(self):
        """Return true if a model is defined."""
        return self.model is not None

    @property
    def lnpriors(self):
        """Return the current content lnprior database."""
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
            (self.lnpriors.instrument_db.
             update(self.model.create_lnpriors(lnlike_db=self.lnlikelihoods.instrument_db,
                                               individual_priors=self.lnpriors.individual)))
            (self.lnpriors.dataset_db.
             update(self.model.
                    create_lnpriors_perdataset(individual_priors=self.lnpriors.individual,
                                               lnlike_db_dtst=self.lnlikelihoods.dataset_db)))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def datasimulators(self):
        """Return the current content lnprior database."""
        return self.__datasim_db

    def get_datasimulators(self):
        """Get datasimulators from the model and store them into datasimulators."""
        if self.islocked_dataset_db:
            self.datasimulators.instrument_db.update(self.model.create_datasimulators())
            (self.datasimulators.dataset_db.
             update(self.model.create_datasimulators_perdataset(dataset_db=self.dataset_db)))
            (self.datasimulators.dataset_db
             [alldtst_key]) = (self.model.
                               create_datasimulator_alldatasets(dataset_db=self.dataset_db))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def noisemodels(self):
        """Return the current content lnprior database."""
        return self.__noisemodel_db

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

            # Create the lnlikelihood function for each dataset
            (self.lnlikelihoods.dataset_db.
             update(self.model.
                    create_lnlikelihoods_perdataset(datasim_db_dtset=(self.datasimulators.
                                                                      dataset_db)
                                                    )
                    )
             )
            # (self.lnlikelihoods.dataset_db.
            #  update(self.model.
            #         create_lnlikelihoods_perdataset(lnlike_db=self.lnlikelihoods.instrument_db,
            #                                         dataset_db=self.dataset_db,
            #                                         instmodel4dataset=self.instmodel4dataset)))
            # (self.lnlikelihoods.dataset_db['all'], dico_noisemodel_instance
            #  ) = (self.model.
            #       create_lnlikelihood_alldataset(datasim_db_dtset=self.datasimulators.dataset_db,
            #                                      dataset_db=self.dataset_db,
            #                                      instmodel4dataset=self.instmodel4dataset
            #                                      )
            #       )
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

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
            return (lnlike_func.function(p, data, data_err, **kwarg_data) +
                    lnprior_func.function(p))

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
            lnprior_func = lnprior_db_dtset[dataset_name].function
            lnlike_func = lnlike_db_dtset[dataset_name].function
            arg_list_new = lnprior_db_dtset[dataset_name].arg_list.copy()

            def lnpost_withdataset_creator(prior_func, like_func, arg_list):
                def lnpost_withdataset(p, *args, **kwargs):
                    # logger.debug("paramnames lnpost ({}): {}\nparams lnpost ({}): {}"
                    #              "".format(len(arg_list["param"]), arg_list["param"], len(p), p))
                    lnprior_val = prior_func(p)
                    # logger.debug("lnprior: {}".format(lnprior_val))
                    if lnprior_val == -inf:
                        return -inf
                    else:
                        # lnlike_val = like_func(p)
                        # logger.debug("lnlike: {}".format(lnlike_val))
                        return like_func(p, *args, **kwargs) + lnprior_val
                return DocFunction(function=lnpost_withdataset, arg_list=arg_list_new)

            db[dataset_name] = lnpost_withdataset_creator(prior_func=lnprior_func,
                                                          like_func=lnlike_func,
                                                          arg_list=arg_list_new)

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
        dico["run_folder"] = self.run_folder
        dico["dataset_file"] = self.datasetsfile_db.datasetsfile_path
        dico["model_category"] = self.model.category
        dico["model_kwargs"] = self.model.init_kwargs
        dico["model_auto_init_kwargs"] = self.model.automatic_init_kwargs

        # Save it to a pickle
        if pickle_filename is None:
            pickle_filename = "{}{}".format(self.object_name, self._extension_postinstance)
        with open(join(pickle_folder, pickle_filename), "wb") as fpostinst:
            dump(dico, fpostinst)

    def init_from_pickle(self, pickle_folder=".", pickle_filename=None):
        """Initialize the instance from the post_instance pickle file produced with save_post_instance.

        :param str pickle_folder: path to the folder containing the pickle file.
        :param str pickle_filename: Name of the posterior instance pickle file
        """
        # load the dictionary
        if pickle_filename is None:
            pickle_filename = "{}{}".format(self.object_name, self._extension_postinstance)
        with open(join(pickle_folder, pickle_filename), "rb") as fdico:
            dico = load(fdico)

        # post_instance = Posterior(object_name=dico["object_name"])
        self.dataset_db.data_folder = dico["data_folder"]
        self.run_folder = dico["run_folder"]
        self.load_datasetsfile(dico["dataset_file"])
        self.define_model(category=dico["model_category"], name=dico["object_name"],
                          **dico["model_kwargs"])
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
