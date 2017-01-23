#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
posterior module.

The objective of this package is to provides the core Posterior class.

@TODO:
    - Function to add datasets from a folder.
"""
import logging
import os

from ...software_parameters import input_data_folder
from ...tools.human_machine_interface.QCM import QCM_utilisateur


logger = logging.getLogger()

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
        super(Posterior, self).__init__()

        ## Name of the object you are trying to modelize
        self.__object = object_name

        ## Dataset dictionnary: Initialise it
        self.__dataset_dict = dict()

        ## Folder where the program should look for dataset files by default: Initialise it
        self.__data_folder = None

        ## Model: Initialise it
        self.__model = None

        ## lnprior: Initialise it
        self.__lnprior = None

        ## lnlike: Initialise it
        self.__lnlike = None

        ## lnpost: Initialise it
        self.__lnpost = None

    def __set_objectname(self, object_name):
        """Define the name of the object studied."""
        self.__object = object_name

    def get_objectname(self, object_name):
        """Get the name of the object studied."""
        return self.__object

    def set_datafolder(self, data_folder=None):
        """Set the data_folder attribute.

        The data_folder is the folder where the program will look for the dataset files. This folder
        can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the data_folder is
              automatically define as "input_data_folder/target". To use this you should not provide
              the data_folder argument.
            - Via the data_folder argument: You can provide any folder here via the data_folder
              argument.
        ----
        Arguments:
            data_folder : string,
                path to the folder which contain the data. If provided the main_data_folder argument
                is ignored.
        """
        # Initialise data_folder attribute
        data_folder_provided = data_folder is not None
        if data_folder_provided:
            folder = data_folder
        else:
            folder = os.path.join(input_data_folder, self.object)
        folder_exist = os.path.isdir(folder)
        if folder_exist:
            self.__data_folder = folder
            if data_folder_provided:
                logger.info("Data_folder is defined as a specific folder: {}".format(folder))
            else:
                logger.info("Data_folder not provided but standard fodler exist and is used:"
                            " {}".format(folder))
        else:
            if data_folder_provided:
                error_msg = "Folder doesn't exist: {}".format(folder)
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                msg = ("You didn't provided any data_folder and the standard one doesn't exist."
                       "Do you want to create the folder (reply by 'y' or 'n'):\n{}".format(folder))
                reply = QCM_utilisateur(msg, ["y", "n"])
                if reply == "y":
                    os.makedirs(folder)
                    self.__data_folder = folder
                    logger.info("Data_folder not provided but standard folder has been created and "
                                "is used: {}".format(folder))
                else:
                    logger.info("Data_folder not provided and standard folder doesn't exist so no "
                                "data_folder defined.")

    def get_datafolder(self):
        """Get the data_folder attributes."""
        return self.__data_folder

    def isset_datafolder(self):
        """Tells if the data_folder attribute is defined."""
        return self.get_datafolder() is not None

    def add_dataset(self, dataset):
        """Add a dataset to the dataset_dict."""
        dataset_instance = Data
        self.__dataset_dict[dataset.]

    def rm_dataset():
        """Remove a dataset from the the dataset_dict."""
        raise NotImplementedError

    def add_datasets_from_file(path_datasets_file):
        """Add a dataset specified in a datafile.
        ----
        Arguments:
            path_datasets_file: string,
                path to the datasets file.
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
        for filepath in list_files:
            self.add_dataset(filepath)

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
