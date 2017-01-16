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
        self.object = object_name

        ## Dataset dictionnary: Initialise it
        self.dataset_dict = dict()

        ## Folder where the program should look for dataset files by default: Initialise it
        self.data_folder = None

        ## Model: Initialise it
        self.model = None

        ## lnprior: Initialise it
        self.lnprior = None

        ## lnlike: Initialise it
        self.lnlike = None

        ## lnpost: Initialise it
        self.lnpost = None

    def isdefined_datafolder(self):
        """Tells if the data_folder attribute is defined."""
        return self.data_folder is not None

    def define_datafolder(self, data_folder=None):
        """Define the data_folder attribute.

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
            folder = os.path.join(main_data_folder, self.object)
        folder_exist = os.path.isdir(folder)
        if folder_exist:
            self.data_folder = folder
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
                    self.data_folder = folder
                    logger.info("Data_folder not provided but standard folder has been created and "
                                "is used: {}".format(folder))
                else:
                    logger.info("Data_folder not provided and standard folder doesn't exist so no "
                                "data_folder defined.")

    def add_dataset():
        """Add a dataset to the dataset_dict."""
        raise NotImplementedError

    def rm_dataset():
        """Remove a dataset from the the dataset_dict."""
        raise NotImplementedError

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
