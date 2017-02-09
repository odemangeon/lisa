#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Core_ParamContainer module.

The objective of this module is to define the Core_ParamContainer class wich is an object defined by
a set of parameters. It could be a Planet or a Star for exoplanet models
"""
from logging import getLogger
from collections import OrderedDict

from ...tools.metaclasses import  MandatoryReadOnlyAttr
from ...tools.name import Name
from ...tools.miscellaneous import spacestring_like
from .parameter import Parameter

## Logger Object
logger = getLogger()


class Core_ParamContainer(Name, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_ParamContainer."""

    __mandatoryattrs__ = ["category"]

    def __init__(self, name, name_prefix=None):
        """docstring Core_ParamContainer init method."""
        ## Parameters WARNING, BECAUSE OF THE __GETATTR__ METHOD THIS HAS TO BE THE FIRST LINE !
        self.__parameters = OrderedDict()
        #
        super(Core_ParamContainer, self).__init__(name=name, name_prefix=name_prefix)
        ## Initialise path to parametrisation file
        self.__param_file = None
        ## Initialise the info regarding the content of the parametrisation file
        self.__paramfile_info = dict()
        if type(self) is Core_ParamContainer:
            raise NotImplementedError("Core_ParamContainer should not be instanciated !")

    def __getattr__(self, attr=""):
        """Intercept attribute call to look first in the parameter list."""
        if attr in self.get_list_all_paramnames():
            return self.parameters[attr]
        else:
            # Default behaviour
            raise AttributeError("{}".format(attr))

    @property
    def parameters(self):
        """Parameters contained in the Core_ParamContainer."""
        return self.__parameters

    def get_list_all_params(self):
        """Return the list of all parameters."""
        return list(self.parameters.values())

    def get_list_all_paramnames(self):
        """Return the list of all parameters."""
        return list(self.parameters.keys())

    def add_parameter(self, parameter):
        """Add a parameter to the Core_ParamContainer."""
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
    def paramfile_info(self):
        """Information about the content of the param file"""
        return self.__paramfile_info

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute."""
        self.paramfile_info.update({"Param names": [param.name for param in
                                                    self.get_list_main_params()]})
        logger.debug("Updated paramfile info for {}.\nKeys of paramfile_info: {}"
                     "".format(self.name, self.paramfile_info))

    def get_paramfile_section(self, text_tab="", texttab_1tline=True,
                              entete_symb=" = ", quote_name=False, ):
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
        space_entete_param = spacestring_like(entete)
        text = ""
        if texttab_1tline:
            text += text_tab
        text += entete
        texttab_1tline_param = False
        for param in self.get_list_main_params():
            text += param.get_paramfile_section(text_tab=text_tab + space_entete_param,
                                                texttab_1tline=texttab_1tline_param,
                                                entete_symb=": ",
                                                quote_name=True)
            texttab_1tline_param = True
        text += text_tab + space_entete_param + "}"
        self.update_paramfile_info()
        return text

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        logger.debug("List of Param names: {}".format(self.paramfile_info["Param names"]))
        for param_name in self.paramfile_info["Param names"]:
            param = getattr(self, param_name)
            param.load_config(dico_config[param.name_code])
