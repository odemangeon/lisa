#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
ParamContainer module.

The objective of this module is to define the ParamContainer class wich is an object defined by a
set of parameters. It could be a Planet or a Star for exoplanet models
"""
import logging
import os

from source.tools.miscellaneous import spacestring_like, check_name, check_name_code
from source.tools.human_machine_interface.QCM import QCM_utilisateur

## Logger Object
logger = logging.getLogger()


class ParamContainer(object):
    """docstring for ParamContainer."""

    def __init__(self, name=""):
        """docstring ParamContainer init method."""
        super(ParamContainer, self).__init__()
        ## String: name of the instrument
        self.__name = check_name(name)
        logger.debug("Name set to {}".format(check_name(name)))
        ## List of Parameter object
        self.parameter_list = []
        ## Initialise path to parametrisation file
        self.__param_file = None
        ## Initialise the info regarding the content of the parametrisation file
        self.__paramfile_info = dict()
        if type(self) is ParamContainer:
            raise NotImplementedError("ParamContainer should not be instanciated !")

    @property
    def name(self):
        """Return the name of the ParamContainer."""
        return self.__name

    @property
    def name_code(self):
        """Return the name of the ParamContainer that can be used in code."""
        return check_name_code(self.name)

    def get_list_params(self):
        """Return the list of all parameters."""
        return self.parameter_list

    def extend_list_params(self, l_new_params):
        """Extend the list of parameter with new paremeters given by l_new_params."""
        self.parameter_list.extend(l_new_params)

    def get_parametrisation(self):
        """Return the list of main parameters (non redondant parameter)."""
        result = []
        for param in self.get_list_params():
            if param.main:
                result.append(param)
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
            self.__param_file = path
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

    def update_paramfile_info(self):
        """Update the paramfile info attribute."""
        self.paramfile_info.update({"Param names": self.get_parametrisation()})

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
        for param in self.get_parametrisation():
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
        if reply == "y":
            with open(filepath, 'w') as f:
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                f.write("# Parametrisation file of {}\n\n".format(self.name))
                f.write("# Parameters\n")
                f.write(self.get_paramfile_section())
            logger.info("Parameter file created at path: {}".format(filepath))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(filepath))
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
        for param in self.paramfile_info["Param names"]:
            param.load_config(dico_config[param.name_code])

    def load_parameter_file(self, dico_config):
        """load the parameter file."""
        dico_config = self.read_parameter_file()
        self.load_config(dico_config)
