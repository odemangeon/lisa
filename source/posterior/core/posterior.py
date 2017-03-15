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

from .instmodel4dataset import Instmodel4DatasetAttr
from .dataset_database_locks import DstDbLockAttr
from .dataset_and_instrument.dataset_database import DatasetDatabase, DatasetDbAttr
from .model.manager_model import Manager_Model
from .database_func import DatabaseFunc, DatabaseInstLvlDataset
from ...tools.name import Name
from ...tools.default_folders_data_run import RunFolder
from ...tools.function_w_doc import DocFunction
# from ...tools.lockable_dict import LockableDict


logger = getLogger()

manager_model = Manager_Model()
manager_model.load_setup()


class Posterior(DatasetDbAttr, Name, RunFolder, Instmodel4DatasetAttr, DstDbLockAttr):
    """docstring for Posterior."""

    msg_err_datasetdb_notlocked = "You can't use this function if the dataset_db is not frozen."

    def __init__(self, object_name, run_folder=None):
        """Init method for the Posterior class.

        This function does:
            1. Define the name of the object studied
            2. Define two locks: dataset_lock and database_lock
            3. Initialize the dataset database attribute and assign it dataset_lock
            4. Initialize the run_folder attribute
            5. Initialie instmodel4dataset attribute and assign it dataset_lock
            6. Initialise the model attribute
            7. Initialise the database function attribute: lnprior_db, lnlike_db, lnpost_db,
               datasim_db. Asssign them the database_lock and dataset_lock and the instmodel4dataset
        ----
        Arguments:
            name : string,
                Name of the object studied.
        """
        Name.__init__(self, name=object_name)  # 1
        DstDbLockAttr.__init__(self, lock_dataset=None, lock_database=None, use_samelock=False)  # 2
        DatasetDbAttr.__init__(self,  # 3
                               dataset_db=DatasetDatabase(self.name,
                                                          lock=self.get_dataset_Lock_instance()))
        RunFolder.__init__(self, run_folder=run_folder)  # 4
        Instmodel4DatasetAttr.__init__(self, lock=self.get_dataset_Lock_instance())  # 5
        self.__model = None  # 6
        self.__lnprior_db = DatabaseFunc(object_stored="prior", database_name=self.object_name,
                                         instmodel4dataset=self.instmodel4dataset,
                                         instordered=False, use_samelock=self.samelock,
                                         lock_dataset=self.get_dataset_Lock_instance(),
                                         lock_database=self.get_database_Lock_instance())  # 7
        self.__lnlike_db = DatabaseFunc(object_stored="likelihood", database_name=self.object_name,
                                        instmodel4dataset=self.instmodel4dataset,
                                        instordered=False, use_samelock=self.samelock,
                                        lock_dataset=self.get_dataset_Lock_instance(),
                                        lock_database=self.get_database_Lock_instance())  # 7
        self.__lnpost_db = DatabaseFunc(object_stored="posterior", database_name=self.object_name,
                                        instmodel4dataset=self.instmodel4dataset,
                                        instordered=False, use_samelock=self.samelock,
                                        lock_dataset=self.get_dataset_Lock_instance(),
                                        lock_database=self.get_database_Lock_instance())  # 7
        self.__datasim_db = DatabaseFunc(object_stored="datasimulator",
                                         instmodel4dataset=self.instmodel4dataset,
                                         database_name=self.object_name, instordered=False,
                                         use_samelock=self.samelock,
                                         lock_dataset=self.get_dataset_Lock_instance(),
                                         lock_database=self.get_database_Lock_instance())  # 7

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

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

    def define_model(self, category, load_setup=False, **kwargs):
        """Set/Initialize the model.

        For now only assignement to None is possible.
        This function should check that the category is an available Core_Model Subclass

        ----
        Arguments:
            category : string,
                String which refers to an available Core_Model Subclass that has been defined in the
                model_setup_file.
        """
        if load_setup:
            manager_model.load_setup()
        if "name" not in kwargs:
            kwargs.update({"name": "default"})
        model_subclass = manager_model.get_model_subclass(category)
        self.__model = model_subclass(dataset_db=self.dataset_db, run_folder=self.run_folder,
                                      instmodel4dataset=self.instmodel4dataset,
                                      **kwargs)
        self.lock()
        logger.info("Model defined with name {} !".format(self.model.name))

    def lock(self):
        """Lock the dataset_db and update instmodel4dataset attributes.

        1. update datasets in instmodel4dataset attribute in model.
        2. update datasets in model.
        3. update datasets in datasim_db.
        4. update datasets in lnprior_db.
        5. update datasets in lnlike_db.
        6. update datasets in lnpost_db.
        7. Lock everything
        """
        list_datasetnames = self.dataset_db.get_datasetnames()
        self.instmodel4dataset.update_datasets(list_datasetnames)  # 1.
        self.model.init_missinginstmodels()  # 2. TODO: It should be more, see init of model
        self.datasimulators.update_datasets()  # 3.
        self.lnpriors.update_datasets()  # 4.
        self.lnlikelihoods.update_datasets()  # 5.
        self.lnposteriors.update_datasets()  # 6.
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
                    create_lnpriors_perdataset(lnprior_db=self.lnpriors.instrument_db,
                                               instmodel4dataset=self.instmodel4dataset)))
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def datasimulators(self):
        """Return the current content lnprior database."""
        return self.__datasim_db

    def get_datasimulators(self):
        """Get datasimulators from the model and store them into datasimulators."""
        if self.islocked_dataset_db:
            self.__datasim_db.instrument_db.update(self.model.create_datasimulators())
        else:
            raise AssertionError(self.msg_err_datasetdb_notlocked)

    @property
    def lnlikelihoods(self):
        """Return the current content lnprior database."""
        return self.__lnlike_db

    def get_lnlikelihoods(self, category="wo jitter"):
        """Get lnlikes from the model and store them into lnlikelihoods."""
        if self.islocked_dataset_db:
            (self.lnlikelihoods.instrument_db.
             update(self.model.create_lnlikelihoods(datasim_db=self.datasimulators.instrument_db,
                                                    category=category)))
            (self.lnlikelihoods.dataset_db.
             update(self.model.
                    create_lnlikelihoods_perdataset(lnlike_db=self.lnlikelihoods.instrument_db,
                                                    dataset_db=self.dataset_db,
                                                    instmodel4dataset=self.instmodel4dataset)))
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
                            # **kwarg_data):
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
            lnlike_func = lnprior_db_dtset[dataset_name].function
            lnprior_func = lnlike_db_dtset[dataset_name].function
            arg_list_new = lnprior_db_dtset[dataset_name].arg_list.copy()

            def lnpost_withdataset(p):
                return lnlike_func(p) + lnprior_func(p)

            db[dataset_name] = DocFunction(function=lnpost_withdataset, arg_list=arg_list_new)

        return db

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
