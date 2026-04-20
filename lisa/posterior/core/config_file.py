"""
configuration file module.

The objective of this package is to provides basic function to handle the configuration file
which can be used by both the Posterior instance and the Model instance.
"""
import runpy

from os import getcwd, chdir

import logging

from ...tools.human_machine_interface.QCM import QCM_utilisateur
from ...tools.miscellaneous import look4file_withdeffolder


logger = logging.getLogger("lisa.config_file")


class ConfigFile(object):
    """
    """

    def __init__(self):
        """Initialise the run_folder property.

        Argument
        --------
        object_name : str
            Name of the object studied. This is used by the path.setter function.
        """
        self.__path = None

    @property
    def path(self):
        """Path to the config_file"""
        return self.__path    

    @path.setter
    def path(self, path):
        """Set the path attribute"""
        if path is None:
            logger.warning("The path of the config_file has NOT been defined because the provided path is None")
        else:
            if not(isinstance(path, str)):
                raise ValueError("path shoud be a str")
            self.__path = path
            logger.info(f"Config file path set to {self.path}.")

    def _read_configfile(self, config_logger=None, log_full_config=False):
        """Function that reads the config file

        Arguments
        ---------
        path_config_file: None or str
            If None the function will offer the possibility to create a default datasets file
            It str, should be the path to an existing datasets file.
        """
        # Make sure that the config_logger is defined
        config_logger = define_config_logger(config_logger=None)
        # Read the content of the config file
        dico = runpy.run_path(self.path, init_globals={'logger': config_logger})
        for var_name in ["self", "cwd", "ff", "path_config_file", "file_path", 'default_file_content']:
            if var_name in dico:
                dico.pop(var_name)
        if log_full_config:
            config_logger.debug(f"Content (just the name of the variables) of the config file (located at {self.config_file.path}):\n{list(dico.keys())}")
        return dico

class ConfigFileAttr(object):
    """docstring for ConfigFileAttr.

    This class is an interface class which is aimed at being used as a Parent class of Posterior and Core_Model
    """

    def __init__(self, config_file=None):
        """Initialise the config_file property.

        Argument
        --------
        run_folder  : str
            Path to the folder to use as run folder.
        """
        if config_file is None:
            self.__config_file = ConfigFile()
        elif isinstance(config_file, ConfigFile):
            self.__config_file = config_file
        elif isinstance(config_file, str):
            self.__config_file = ConfigFile()
            self.__config_file.path = config_file
        else:
            raise ValueError("config_file should be a None, a string or a ConfigFile instance")
    
    @property
    def config_file(self):
        """ConfigFile instance"""
        return self.__config_file
    
    def _askadd2configfile(self, config2load):
        """ Ask the use if he wants to add a missing configuration variable to the config file.

        Arguments
        ---------
        config2load : 
            Specify the config to load. Possible values are provided by self._config_categories
        """
        intitule_question = f"The variable(s) for the {config2load} configuration is/are missing from the config file. Do you want to add it/them ? ['y', 'n']\n"
        return QCM_utilisateur(intitule_question=intitule_question, l_reponses_possibles=['y', 'n'])
    
    def _load_config(self, config2load, ask_before_adding=False, config_logger=None, **kwargs):
        """Function that reads the config file

        Arguments
        ---------
        config2load         : str
            Specify the config to load. Possible values are provided by self._config_categories
        path_config_file    : None or str
            If None the function will offer the possibility to create a default datasets file
            It str, should be the path to an existing datasets file.
        """
        # Make sure that the config_logger is defined
        config_logger = define_config_logger(config_logger=None)
        # Read the content of the config file
        dico_config_file = self.config_file._read_configfile(config_logger=config_logger, log_full_config=False)
        if not(self._get_function_config(function_type='check_config_exists', config2load=config2load)(dico_config_file=dico_config_file)):  # _get_function_config is a method of both Posterior and Core_Model
            # If the variable where the configuration of the category is supposed to be done is not defined in the config file
            # Propose to add it with the default configuration
            if ask_before_adding:
                reply = self._askadd2configfile(config2load=config2load)
            else:
                reply = 'y'
            # If the reply is no raise an error
            if reply == 'n':
                raise ValueError(f"The configuration file doesn't define the variables for {config2load}.")
            # If the reply is yes add it to the config_file and ask the user to check the content.
            else:
                # Look for the config file to check if it exists
                file_path = look4file_withdeffolder(file_path=self.config_file.path, default_folder=None)  # look4runfile is provided by RunFolderAttr which is also a parent classe of Posterior and Core_Model
                with open(file_path, "+a") as ff:
                    self._get_function_config(function_type='add_default_config', config2load=config2load)(file=ff) # _get_function_config is a method of both Posterior and Core_Model
                input(f"{config2load}: Default configuration variable(s) was/were added to the configuration file ({self.config_file.path}).\n"
                      "Modify it/them to your needs and then press ENTER.\n")
                dico_config_file = self.config_file._read_configfile(config_logger=config_logger, log_full_config=False)
        # Check the content of the configuration variable and load it
        return self._get_function_config(function_type='load_config_content', config2load=config2load)(dico_config_file=dico_config_file, **kwargs) # _get_function_config is a method of both Posterior and Core_Model    


def define_config_logger(config_logger=None):
    """Define the config_logger to be used when reading the config file.

    Arguments
    ---------
    config_logger : None or logging.Logger instance or loguru.logger
        If None, the loguru logger will be used if loguru is installed, else a standard logging.Logger instance will be created.
        If a logging.Logger instance is provided, it will be used as is.
    """
    if config_logger is None:
        try:
            import loguru
            from loguru import logger as config_logger
        except ImportError:
            config_logger = logging.getLogger("read_config_file")
    else:
        try:
            from loguru._logger import Logger as LoguruLogger
            if not(isinstance(config_logger, logging.Logger)) and not(isinstance(config_logger, LoguruLogger)):
                raise ValueError("config_logger should be a None or a logging.Logger instance or loguru.logger")
        except ImportError:
            if not(isinstance(config_logger, logging.Logger)):
                raise ValueError("config_logger should be a None or a logging.Logger instance")
    return config_logger       