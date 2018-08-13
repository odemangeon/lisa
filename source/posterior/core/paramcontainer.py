#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Core_ParamContainer module.

The objective of this module is to define the Core_ParamContainer class wich is an object defined by
a set of parameters. It could be a Planet or a Star for exoplanet models
"""
from logging import getLogger
from collections import OrderedDict

from ...tools.metaclasses import MandatoryReadOnlyAttr
from ...tools.name import Named, check_getname_kwargs
from ...tools.miscellaneous import spacestring_like
from .parameter import Parameter

## Logger Object
logger = getLogger()


key_params_fileinfo = "Param names"

class Core_ParamContainer(Named, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_ParamContainer."""

    __mandatoryattrs__ = ["category"]

    def __init__(self, name, name_prefix=None, **kwargs):
        """docstring Core_ParamContainer init method.

        :param str name: Name of the parameter container instance.
        :param str/Name/None name_prefix: Prefix for the parameter container instance.

        Keyword arguments are passed to Named.__init__ (see docstring for more info)
        """
        ## Parameters WARNING, BECAUSE OF THE __GETATTR__ METHOD THIS HAS TO BE THE FIRST LINE !
        self.__parameters = OrderedDict()
        ## Do the Name class init
        super(Core_ParamContainer, self).__init__(name=name, prefix=name_prefix, **kwargs)
        ## Initialise path to parametrisation file
        self.__param_file = None
        ## Initialise the info regarding the content of the parametrisation file
        self.__paramfile_info = dict()
        ## This class is not meant to be instanciated but subclassed and then instanciated.
        if type(self) is Core_ParamContainer:
            raise NotImplementedError("Core_ParamContainer should not be instanciated !")

    def __getattr__(self, attr=""):
        """Intercept attribute call to look in the parameter list."""
        if attr in Core_ParamContainer.__get_list_all_paramnames(self):
            return self.parameters[attr]
        else:
            # Default behaviour
            raise AttributeError("{}".format(attr))

    @property
    def parameters(self):
        """Parameters contained in the Core_ParamContainer."""
        return self.__parameters

    def add_parameter(self, parameter):
        """Add a parameter to the Core_ParamContainer."""
        if isinstance(parameter, Parameter):
            self.parameters[parameter.get_name()] = parameter
        else:
            raise ValueError("parameter should be an instance of the Parameter class")

    def __get_list_all_params(self):
        """Return the list of all parameters."""
        return list(self.parameters.values())

    def __get_list_all_paramnames(self):
        """Return the list of all parameters."""
        return list(self.parameters.keys())

    def get_list_params(self, main=False, free=False):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :return list_of_param result: list of Parameter instances
        """
        if main:
            result = []
            for param in Core_ParamContainer.__get_list_all_params(self):
                if free and (param.main) and (param.free):
                    result.append(param)
                elif not(free) and param.main:
                    result.append(param)
            return result
        else:
            return Core_ParamContainer.__get_list_all_params(self)

    def get_list_paramnames(self, main=False, free=False, **kwargs):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameter names
        :param bool free: If true (default false) returns only the free parameter names

        Keyword arguments are passed directly to the Named.get_name method (see docstring of
        for exhaustive information).

        :return list_of_param result: list of Parameter instances
        """
        result = []
        for param in Core_ParamContainer.get_list_params(self, main=main, free=free):
            result.append(param.get_name(**kwargs))
        return result

    def has_parameter(self, name,  main=False, free=False, **kwargs):
        """Return True in the parameter designated by the name provided exists.

        :param str name: Name of the parameter you are looking for
        :param bool main: If true (default false) returns True only if the parameter exists and is a
            main parameter
        :param bool free: If true (default false) returns True only if the parameter exists and is a
            free parameter

        Keyword arguments are passed directly to the Named.get_name method (see docstring of
        for exhaustive information).

        :return bool has: True if the parameter as specified exists, False otherwise.
        """
        return name in self.get_list_paramnames(main=main, free=free, **kwargs)

    def get_param(self, name, kwargs_get_name=None, **kwargs):
        """Return parameter instance designated by it's name.

        :param str name: Name of the Parameter looked for.
        :param dict kwargs_get_name: Keyword arguments dictionary for the Paremeter.get_name method.

        Keyword arguments are passed directly to the self.get_list_params method (see docstring of
        for exhaustive information).

        :return Parameter/None result: Parameter instance if uniquely found, None otherwise.
        """
        l_param = self.get_list_params(**kwargs)
        if kwargs_get_name is None:
            kwargs_get_name = {}
        l_param_names = [param.get_name(**kwargs_get_name) for param in l_param]
        if l_param_names.count(name) == 0:
            logger.warning("Parameter {} not found".foramt(name))
        elif l_param_names.count(name) == 1:
            return l_param[l_param_names.index(name)]
        else:
            logger.warning("Parameter {} found multiple times. The name is not unique".foramt(name))

    @property
    def paramfile_info(self):
        """Information about the content of the param file"""
        return self.__paramfile_info

    def update_paramfile_info(self, recursive=False):
        """Update the paramfile info attribute."""
        self.paramfile_info.update({key_params_fileinfo: [param.get_name() for param in
                                                          self.get_list_params(main=True)]})
        logger.debug("Updated paramfile info for {}.\nKeys of paramfile_info: {}"
                     "".format(self.get_name(), self.paramfile_info))

    def get_paramfile_section(self, text_tab="", texttab_1tline=True,
                              entete_symb=" = ", quote_name=False, **kwargs):
        """Return the text to include in the parameter_file for this CelestialBody.

        :param str text_tab: text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        :param bool texttab_1tline: Wether to use the tab for the first line or not.
        :param str entete_symb: Symbol to use after the paramcontainers name
        :param bool quote_name: Wether to put quote around the paramcontainer name or not.

        Keywords arguments are given to self.get_list_params (see docstring for details).

        :return str text: Text for the parameter file.
        """
        if quote_name:
            entete = "'{}'{}{{"
        else:
            entete = "{}{}{{"
        entete = entete.format(self.code_name, entete_symb)
        space_entete_param = spacestring_like(entete)
        text = ""
        if texttab_1tline:
            text += text_tab
        text += entete
        texttab_1tline_param = False
        for param in self.get_list_params(main=True, **kwargs):
            text += param.get_paramfile_section(text_tab=text_tab + space_entete_param,
                                                texttab_1tline=texttab_1tline_param,
                                                entete_symb=": ",
                                                quote_name=True)
            texttab_1tline_param = True
        text += text_tab + space_entete_param + "}"
        self.update_paramfile_info()
        return text

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary

        :param dict dico_config: Dictionnary containing the new configuration for the main Parameters
            read from the parameter file.
        """
        logger.debug("List of Param names: {}".format(self.paramfile_info["Param names"]))
        for param_name in self.paramfile_info[key_params_fileinfo]:
            param = getattr(self, param_name)
            if param.get_name(code_version=True) in dico_config:
                param.main = True
                param.load_config(dico_config[param.get_name(code_version=True)])
            else:
                param.main = False
