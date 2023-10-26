"""
configuration file module.

The objective of this package is to provides basic function to handle the configuration file
which can be used by both the Posterior instance and the Model instance.
"""
from os import getcwd, chdir

from loguru import logger

from ...tools.human_machine_interface.QCM import QCM_utilisateur

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
            logger.warning("The path of the config_file has NOT been defined because the provided folder is None")
        else:
            if not(isinstance(path, str)):
                raise ValueError("path shoud be a str")
            self.__path = path
            logger.info(f"Config file path set to {self.path}.")


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

    def _read_configfile(self):
        """Function that reads the config file

        Arguments
        ---------
        path_config_file: None or str
            If None the function will offer the possibility to create a default datasets file
            It str, should be the path to an existing datasets file.
        """
        # Read the content of the config file
        cwd = getcwd()
        chdir(self.run_folder.path)  # Self run folder comes from the RunFolderAttr (and is a RunFolder instance) that is also a parent class of Posterior and Core_Model.
        with open(self.config_file.path) as ff:
            exec(ff.read())
        chdir(cwd)
        dico = locals().copy()
        for var_name in ["self", "cwd", "ff", "path_config_file", "file_path", 'default_file_content']:
            if var_name in dico:
                dico.pop(var_name)
        logger.debug(f"Content (just the name of the variables) of the config file (located at {self.config_file}):\n{list(dico.keys())}")
        return dico
    
    def _askadd2configfile(self, config2load):
        """ Ask the use if he wants to add a missing configuration variable to the config file.

        Arguments
        ---------
        config2load : 
            Specify the config to load. Possible values are provided by self._config_categories
        """
        intitule_question = f"The variable(s) for the {config2load} configuration is/are missing from the config file. Do you want to add it/them ?\n"
        return QCM_utilisateur(intitule_question=intitule_question, l_reponses_possibles=['y', 'n'])
    
    def _load_config(self, config2load, **kwargs):
        """Function that reads the config file

        Arguments
        ---------
        config2load         : str
            Specify the config to load. Possible values are provided by self._config_categories
        path_config_file    : None or str
            If None the function will offer the possibility to create a default datasets file
            It str, should be the path to an existing datasets file.
        """
        dico_config_file = self._read_configfile()
        if not(self._get_function_config(function_type='check_config_exists', config2load=config2load)(dico_config_file=dico_config_file)):  # _get_function_config is a method of both Posterior and Core_Model
            # If the variable where the configuration of the category is supposed to be done is not defined in the config file
            # Propose to add it with the default configuration
            # I AM HERE
            reply = self._askadd2configfile(config2load=config2load)
            # If the reply is no raise an error
            if reply == 'n':
                raise ValueError(f"The configuration file doesn't define the variable {self._d_varname_configfile[config2load]}.")
            # If the reply is yes add it to the config_file and ask the user to check the content.
            else:
                # Look for the config file to check if it exists
                file_path = self.look4runfile(file_path=self.config_file.path)  # look4runfile is provided by RunFolderAttr which is also a parent classe of Posterior and Core_Model
                with open(file_path, "+a") as ff:
                    self._get_function_config(function_type='add_default_config', config2load=config2load)(file=ff) # _get_function_config is a method of both Posterior and Core_Model
                input(f"{config2load}: Default configuration variable(s) was/were added to the configuration file ({self.config_file.path}).\n"
                      "Modify it/them to your needs and then press ENTER.\n")
                dico_config_file = self._read_configfile()
        # Check the content of the configuration variable and load it
        return self._get_function_config(function_type='load_config_content', config2load=config2load)(dico_config_file=dico_config_file, **kwargs) # _get_function_config is a method of both Posterior and Core_Model           