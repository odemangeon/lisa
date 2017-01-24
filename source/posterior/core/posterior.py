#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
posterior module.

The objective of this package is to provides the core Posterior class.

@ DONE:
    - Posterior.__init__: Doc and UT
    - Posterior.object_name: Doc and UT
    - Posterior.data_folder: Doc and UT
    - Posterior.isset_datafolder: Doc and UT
    - Posterior.dataset_database: Doc and UT
    - Posterior._add_a_dataset: Doc and UT
    - Posterior.rm_dataset: Doc and UT
    - Posterior.add_a_dataset_from_path: Doc and UT
    - Posterior.add_datasets_from_datasetsfile: Doc and UT
@TODO:
    - Function to add datasets from a folder.
    - add_model, rm_model
    - get_lnprior, get_lnlike, get_lnpost
"""
import logging
import os

from ...software_parameters import input_data_folder
from ...tools.human_machine_interface.QCM import QCM_utilisateur
from .dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset


logger = logging.getLogger()
manager = Manager_Inst_Dataset()
manager.load_setup()


def interpret_dataset_key(dataset_key):
    """
    Interpret dataset key.

    ----

    Arguments:
        dataset_key : string,
            dataset_key
    Returns:
        dictionnary with the interpration of the dataset key which contains the following keys:
            - instrument : instrument name
            - number : give the number of the data file if there is several data files from the same
            instrument
    """
    cuts = dataset_key.split("_")
    if len(cuts) > 2:
        logging.warning("dataset_key not recognized. Should be in the format "
                        "instrument_number. Got: {}".format(dataset_key))
        return None
    result = {"instrument": cuts[0]}
    if len(cuts) == 2:
        result["number"] = cuts[1]
    elif len(cuts) == 1:
        result["number"] = None
    return result


def build_dataset_key(instrument, number=None):
    """
    build dataset key.

    ----

    Arguments:
        instrument : string,
            instrument name
        number : string, optional,
            number of the dataset for this instrument
    Returns:
        dataset_key
    """
    separator = "_"
    dataset_key = instrument
    if number is not None:
        dataset_key += separator + number
    return dataset_key


class Posterior(object):
    """docstring for Posterior."""
    def __init__(self, object_name):
        """Init method for the Posterior class.

        This function does:
            1. Define the name of the object studied
            2. Initialize the dataset database
            3. Initialize the data_folder
            4. Initialise the model
            5. Initialise the lnprior
            6. Initialise the lnlike
            7. Initialise the lnpost
        ----
        Arguments:
            object_name : string,
                Name of the object studied.
        """
        super(Posterior, self).__init__()

        # 1.
        ## Name of the object you are trying to modelize
        self.__object_name = object_name
        # 2.
        ## Dataset dictionnary: Initialise it
        self.dataset_database = dict()
        # 3.
        ## Folder where the program should look for dataset files by default: Initialise it
        self.__data_folder = None
        # 4.
        ## Model: Initialise it
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
        return self.__object_name

    @property
    def data_folder(self):
        """Get the data_folder attributes."""
        return self.__data_folder

    @data_folder.setter
    def data_folder(self, data_folder="default"):
        """Set the data_folder attribute.

        The data_folder is the folder where the program will look for the dataset files.
        It can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the data_folder is
              automatically define as "input_data_folder/object_name". To use this you should assign
              "default"
            - Via the data_folder argument: You can provide any folder here via the data_folder
              argument.
        This function does:
            1. Check if the data_folder argument has been provided. If yes use this otherwise try
                use a folder with the object name in the fodler designated by the input_data_folder
                provided by the software_parameter module
            2. Test is the folder selected in 1 exists
            3. If yes, Set the data_folder attribute to be this folder
            4. If no, Ask if the user want to create the folder selected.
                4.1. If yes, create it and set the data_folder attribute
                4.2. If no, don't create, don't set and put log warning message
            5. log the definition of the data folder
        ----
        Arguments:
            data_folder : string, (default: None),
                path to the folder which contain the data. If provided the main_data_folder argument
                is ignored.
        """
        # 1.
        data_folder_provided = (data_folder != "default")
        if data_folder_provided:
            folder = data_folder
        else:
            folder = os.path.join(input_data_folder, self.object_name)
        # 2.
        folder_exist = os.path.isdir(folder)
        # 3.
        if folder_exist:
            self.__data_folder = folder
            data_folder_defined = True
        # 4.
        else:
            if data_folder_provided:
                error_msg = "Folder doesn't exist: {}".format(folder)
                reply = QCM_utilisateur(error_msg + "\n Do you want to create it ? ['y', 'n']",
                                        ['y', 'n'])
            else:
                msg = ("You didn't provided any data_folder and the standard one doesn't exist."
                       "Do you want to create the folder (reply by 'y' or 'n'):\n{}".format(folder))
                reply = QCM_utilisateur(msg, ["y", "n"])
            # 4.1.
            if reply == "y":
                os.makedirs(folder)
                self.__data_folder = folder
                data_folder_defined = True
                logger.info("Folder created: {}".format(folder))
            # 4.2.
            else:
                data_folder_defined = False
                logger.warning("Data_folder has not been defined because provided folder doesn't "
                               "exist and has not been created.")
        # 5.
        if data_folder_defined:
            if data_folder_provided:
                logger.info("Data_folder is defined as a specific folder: {}".format(folder))
            else:
                logger.info("Data_folder not provided but standard fodler exist and is used:"
                            " {}".format(folder))

    def isset_datafolder(self):
        """Tells if the data_folder attribute is defined."""
        return self.data_folder is not None

    @property
    def dataset_database(self):
        """Return the dataset database."""
        return self.__dataset_database

    @dataset_database.setter
    def dataset_database(self, database):
        """Set/Initialize the dataset database.

        For now only assignement to dict() is possible
        ----
        Arguments:
            database : dict,
                Dictionnary that contains a dataset database.
        """
        if database == dict():
            self.__dataset_database = database
        else:
            raise ValueError("For now only now an empty dict is accepted to reset the database.")

    def _add_a_dataset(self, dataset):
        """Add a dataset to the dataset database.
        ----
        Arguments:
            dataset : Subclass of Dataset object,
                Instance of a subclass of Dataset.
        """
        inst_type = dataset.instrument.inst_type
        inst_name = dataset.instrument.name
        number = dataset.number
        if inst_type not in self.dataset_database:
            self.dataset_database.update({inst_type: {}})
        if inst_name not in self.dataset_database[inst_type]:
            self.dataset_database[inst_type].update({inst_name: {}})
        if str(number) in self.dataset_database[inst_type][inst_name]:
            raise ValueError("The number of the dataset is {}. This number correspond to an alredy"
                             "added dataset".format(number))
        self.dataset_database[inst_type][inst_name][str(number)] = dataset

    def rm_dataset(self, inst_type, inst_name, number=0):
        """Remove a dataset from the the dataset database.
        ----
        Arguments:
            inst_type   : string,
                Type of instrument associated to the dataset you want to remove
            inst_name   : string,
                Name of the instrument associated to the dataset you want to remove
            number      : int, (default: 0)
                Number associated to the dataset you want to remove.
        """
        self.dataset_database[inst_type][inst_name].pop(str(number))
        if len(self.dataset_database[inst_type][inst_name]) == 0:
            self.dataset_database[inst_type].pop(inst_name)
            if len(self.dataset_database[inst_type]) == 0:
                self.dataset_database.pop(inst_type)

    def add_a_dataset_from_path(self, datafile_path, load_setup=False):
        """Add a dataset designated by its path to the dataset database.
        ----
        Arguments:
            datafile_path   : string,
                path to the data file.
            load_setup      : bool, (default: False)
                tell if you want to manager to laod the inst_and_dataset_setup file.
        """
        if os.path.isfile(datafile_path):
            path = datafile_path
            found = True
        else:
            if self.isset_datafolder:
                if os.path.isfile(os.path.join(self.data_folder, datafile_path)):
                    path = os.path.join(self.data_folder, datafile_path)
                    found = True
                else:
                    found = False
            else:
                found = False
        if not found:
            return ValueError("File {} not found".format(datafile_path))
        if load_setup:
            manager.load_setup()
        self._add_a_dataset(manager.create_dataset(path))
        logger.info("dataset added to the database: {}".format(datafile_path))

    def add_datasets_from_datasetsfile(self, path_datasets_file, load_setup=False):
        """Add the datasets specified in the datasets_file to the dataset database.
        ----
        Arguments:
            path_datasets_file  : string,
                path to the datasets file.
            load_setup          : bool, (default: False)
                tell if you want to manager to laod the inst_and_dataset_setup file.
        """
        if os.path.exists(path_datasets_file):
            logger.debug("file exists: {}".format(path_datasets_file))
            list_files = []
            with open(path_datasets_file, 'r') as f:
                for line in f.readlines():
                    line_striped = line.strip(" \n")
                    logger.debug("raw line: {}striped line: {}".format(line, line_striped))
                    if not(line_striped.startswith("#")) and (len(line_striped) > 0):
                        logger.debug("line accepted as filename: {}".format(True))
                        list_files.append(line_striped)
                    else:
                        logger.debug("line accepted as filename: {}".format(False))
        else:
            error_msg = "file doesn't exist: {}".format(path_datasets_file)
            raise ValueError(error_msg)
        logger.debug("List of files to use: {}".format(list_files))
        if load_setup:
            manager.load_setup()
        for filepath in list_files:
            self.add_a_dataset_from_path(filepath)

    def add_model():
        """Add a model."""
        raise NotImplementedError

    def rm_model():
        """Remove a model."""
        raise NotImplementedError

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
    #     """Indicate if the dataset designed by key is exisiting and loaded and if yes which type."""
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
