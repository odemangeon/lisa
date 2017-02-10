#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
posterior module.

The objective of this package is to provides the core Posterior class.

@ DONE:
    - Posterior.__init__: Doc and UT
    - Posterior.data_folder: Doc and UT
    - Posterior.isset_datafolder: Doc and UT
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

from ...tools.miscellaneous import define_folder_withdefault  # , look4file_withdeffolder
from ...tools.name import Name
from ...software_parameters import input_run_folder
from .dataset_and_instrument.dataset_database import DatasetDatabase, DatasetDbAttr
from .model.manager_model import Manager_Model

logger = getLogger()

manager_model = Manager_Model()
manager_model.load_setup()


class Posterior(DatasetDbAttr, Name):
    """docstring for Posterior."""
    def __init__(self, object_name):
        """Init method for the Posterior class.

        This function does:
            1. Define the name of the object studied
            2. Initialize the dataset database
            3. Initialize the data_folder
            4. Initialize the run_folder
            5. Initialise the model
            6. Initialise the lnprior
            7. Initialise the lnlike
            8. Initialise the lnpost
        ----
        Arguments:
            name : string,
                Name of the object studied.
        """
        # 1.
        Name.__init__(self, name=object_name)
        # 2.
        DatasetDbAttr.__init__(self, dataset_db=DatasetDatabase(self.name))
        ## Folder where the program should look for config files by default: Initialise it
        self.__run_folder = None
        # 4.
        ## model: Initialise it
        self.__model = None
        # 5.
        ## lnprior: Initialise it
        self.__lnprior = None
        # 6.
        ## lnlike: Initialise it
        self.__lnlike = None
        # 7.
        ## lnpost: Initialise it
        self.__lnpost = None

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
        return self.__run_folder

    @run_folder.setter
    def run_folder(self, run_folder="default"):
        """Set the run_folder attribute."""
        self.__run_folder = define_folder_withdefault(main_default_folder=input_run_folder,
                                                      object_name=self.name,
                                                      folder=run_folder)
        self.dataset_db.run_folder = self.run_folder

    def isset_runfolder(self):
        """Tells if the run_folder attribute is defined."""
        return self.run_folder is not None

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
        self.dataset_db.freeze = True
        self.__model = model_subclass(dataset_db=self.dataset_db, **kwargs)
        logger.info("Model defined with name {} !".format(self.model.name))

    def rm_model(self):
        """Remove a model."""
        self.__model = None
        self.dataset_db.freeze = False

    def isdefined_model(self):
        """Return true if a model is defined."""
        return self.model is not None

    def get_lnprior():
        """Get lnprior from a model and store it into lnprior."""
        raise NotImplementedError

    def get_lnlike():
        """Get lnlike from a model and store it into lnlike."""
        raise NotImplementedError

    def get_lnpost():
        """Get lnpost from a model and store it into lnpost."""
        raise NotImplementedError

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
