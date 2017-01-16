#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
posterior module.

The objective of this package is to provides the core Posterior class.

@TODO:
"""
import logging
import os

from ...software_parameters import input_data_folder
from ...tools.human_machine_interface.QCM import QCM_utilisateur


logger = logging.getLogger()


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
        dataset
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
