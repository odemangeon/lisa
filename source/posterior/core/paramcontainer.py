#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
ParamContainer module.

The objective of this module is to define the ParamContainer class wich is an object defined by a
set of parameters. It could be a Planet or a Star for exoplanet models
"""
import os
from logging import getLogger
from collections import OrderedDict

from source.tools.name import Name
from source.tools.miscellaneous import spacestring_like
from source.tools.human_machine_interface.QCM import QCM_utilisateur
from .parameter import Parameter

## Logger Object
logger = getLogger()


class ParamContainer(Name):
    """docstring for ParamContainer."""

    def __init__(self, name, name_prefix=None):
        """docstring ParamContainer init method."""
        ## Parameters WARNING, BECAUSE OF THE __GETATTR__ METHOD THIS HAS TO BE THE FIRST LINE !
        self.__parameters = OrderedDict()
        #
        super(ParamContainer, self).__init__(name=name, name_prefix=name_prefix)
        ## Initialise path to parametrisation file
        self.__param_file = None
        ## Initialise the info regarding the content of the parametrisation file
        self.__paramfile_info = dict()
        if type(self) is ParamContainer:
            raise NotImplementedError("ParamContainer should not be instanciated !")

    def __getattr__(self, attr=""):
        """Intercept attribute call to look first in the parameter list."""
        if attr in self.get_list_all_paramnames():
            return self.parameters[attr]
        else:
            # Default behaviour
            raise AttributeError("{}".format(attr))

    @property
    def parameters(self):
        """Parameters contained in the ParamContainer."""
        return self.__parameters

    def get_list_all_params(self):
        """Return the list of all parameters."""
        return list(self.parameters.values())

    def get_list_all_paramnames(self):
        """Return the list of all parameters."""
        return list(self.parameters.keys())

    def add_parameter(self, parameter):
        """Add a parameter to the ParamContainer."""
        if isinstance(parameter, Parameter):
            self.parameters[parameter.name] = parameter
        else:
            raise ValueError("parameter should be an instance of the Parameter class")

    def get_list_main_params(self):
        """Return the list of main parameters (non redondant parameter)."""
        result = []
        for param in self.get_list_all_params():
            if param.main:
                result.append(param)
        return result

    def get_list_main_paramname(self):
        """Return the list of main parameters names (non redondant parameter)."""
        result = []
        for param in self.get_list_main_params():
            result.append(param.name)
        return result

    @property
    def param_file(self):
        """Path to the parametrisation file"""
        return self.__param_file

    @param_file.setter
    def param_file(self, path):
        """Path to the parametrisation file"""
        file_exists = os.path.isfile(path)
        if file_exists:
            self.param_file = path
        else:
            raise AssertionError("File {} doesn't exists".format(path))

    @property
    def isdefined_paramfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.param_file is not None

    @property
    def paramfile_info(self):
        """Information about the content of the param file"""
        return self.__paramfile_info

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute."""
        self.paramfile_info.update({"Param names": [param.name for param in
                                                    self.get_list_main_params()]})
        logger.debug("Updated paramfile info for {}.\nKeys of paramfile_info: {}"
                     "".format(self.name, self.paramfile_info))

    def get_paramfile_section(self, text_tab="", entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this CelestialBody.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        if quote_name:
            entete = "'{}'{}{{".format(self.name_code, entete_symb)
        else:
            entete = "{}{}{{".format(self.name_code, entete_symb)
        text = text_tab + entete
        text_tab_param = spacestring_like(text_tab + entete)
        texttab_1tline = False
        for param in self.get_list_main_params():
            text += param.get_paramfile_section(text_tab=text_tab_param,
                                                texttab_1tline=texttab_1tline,
                                                entete_symb=": ",
                                                quote_name=True)
            texttab_1tline = True
        text += text_tab_param + "}"
        self.update_paramfile_info()
        return text

    def create_parameter_file(self, filepath):
        """Create the parameter file."""
        if os.path.isfile(filepath):
            answers_list = ['y', 'n']
            question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                        "".format(filepath, answers_list))
            reply = QCM_utilisateur(question, answers_list)
        else:
            reply = "y"
        if reply == "y":
            with open(filepath, 'w') as f:
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                f.write("# Parametrisation file of {}\n\n".format(self.name))
                f.write("# Parameters\n")
                f.write(self.get_paramfile_section())
            logger.info("Parameter file created at path: {}".format(filepath))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(filepath))
            self.update_paramfile_info(recursive=True)
        self.param_file = filepath

    def read_parameter_file(self):
        """Read the content of the parameter file."""
        if self.isdefined_paramfile:
            exec(open(self.param_file).read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("Parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read parameter file: {}".format(self.param_file))

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        logger.debug("List of Param names: {}".format(self.paramfile_info["Param names"]))
        for param_name in self.paramfile_info["Param names"]:
            param = getattr(self, param_name)
            param.load_config(dico_config[param.name_code])

    def load_parameter_file(self):
        """load the parameter file."""
        dico_config = self.read_parameter_file()
        self.load_config(dico_config)
