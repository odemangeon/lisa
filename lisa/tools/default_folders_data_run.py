#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
default_folders_data_run module.

Provide the data_folder and run_folder interfaces Class.

@TODO:
    - Enforce the definition of a object_name property for subclasses of RunFolder and DataFolder
    - The two Classes are exact duplicates of one another. Make one Superclass and twosubclasses
"""
from loguru import logger

from .miscellaneous import define_folder_withdefault, look4file_withdeffolder
from ..software_parameters import input_run_folder
from ..software_parameters import input_data_folder


class RunFolder(object):
    """docstring for the interface RunFolder class for the Posterior Instance.

    Should be used as a parent class of the Posterior class to give the instances of the posterior instances the attribute run_folder and the methods to use it.

    It could be used as a Parent class of another class as long as this class has the object_name attribute.
    """

    def __init__(self, run_folder=None):
        """Initialise the run_folder property.

        :param string/None run_folder: Folder to use as run folder. For more info check run_folder property definition
        """
        # 1.
        ## Folder where the program should look for config files by default: Initialise it
        self.run_folder = run_folder
        # 2.
        if type(self) is RunFolder:
            raise NotImplementedError("RunFolder should not be instanciated !")

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
        try:
            return self.__run_folder
        except AttributeError:
            return None

    @run_folder.setter
    def run_folder(self, run_folder="default"):
        """Set the run_folder attribute, see run_folder property docstring."""
        if run_folder is None:
            logger.warning("The run_folder has NOT been defined because the provided folder is "
                           "None")
        else:
            res = define_folder_withdefault(main_default_folder=input_run_folder,
                                            object_name=self.object_name,
                                            folder=run_folder)
            if res is not None:
                self.__run_folder = res
                logger.info("Run folder of the instance of class {} set to {}."
                            "".format(self.__class__.__name__, self.run_folder))

    @property
    def hasrun_folder(self):
        """Return True is run_folder has been set already, False otherwise."""
        return self.run_folder is not None

    def look4runfile(self, file_path):
        """Look for a file in absolute or in the default folder.

        :param string file_path: path or name to the file you are looking for.
        :return string absolute_path: Path to the file that you are looking for. None if not found.
        """
        return look4file_withdeffolder(file_path=file_path, default_folder=self.run_folder)


class DataFolder(object):
    """docstring for the interface DataFolder class for the Posterior Instance.

    Should be used as a parent class of the Posterior class to give the instances of the posterior instances the attribute data_folder and the methods to use it.

    It could be used as a Parent class of another class as long as this class has the object_name attribute.
    """

    def __init__(self, data_folder=None):
        # 1.
        ## Folder where the program should look for dataset files by default: Initialise it
        self.data_folder = data_folder
        # 2.
        if type(self) is DataFolder:
            raise NotImplementedError("DataFolder should not be instanciated !")

    @property
    def data_folder(self):
        """The data_folder is the folder where the program will look for the dataset files.
        It can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the data_folder is
              automatically define as "input_data_folder/object_name". To use this you should assign
              "default"
            - Via the data_folder argument: You can provide any folder here via the data_folder
              argument.
        If not defined, return None.
        """
        try:
            return self.__data_folder
        except AttributeError:
            return None

    @data_folder.setter
    def data_folder(self, data_folder="default"):
        """Set the data_folder attribute."""
        if data_folder is None:
            logger.warning("The data_folder has NOT been defined because the provided folder is "
                           "None")
        else:
            res = define_folder_withdefault(main_default_folder=input_data_folder,
                                            object_name=self.object_name,
                                            folder=data_folder)
            if res is not None:
                self.__data_folder = res
                logger.info("Data folder of the instance of class {} set to {}."
                            "".format(self.__class__.__name__, self.data_folder))

    @property
    def hasdata_folder(self):
        """Return True is data_folder has been set already, False otherwise."""
        return self.data_folder is not None

    def look4datafile(self, file_path):
        """Look for a file in absolute or in the default folder."""
        return look4file_withdeffolder(file_path=file_path, default_folder=self.data_folder)
