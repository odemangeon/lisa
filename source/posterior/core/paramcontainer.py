#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
ParamContainer module.

The objective of this module is to define the ParamContainer class wich is an object defined by a
set of parameters. It could be a Planet or a Star for exoplanet models
"""
import logging

from source.tools.miscellaneous import spacestring_like, check_name, check_name_code

## Logger Object
logger = logging.getLogger()


class ParamContainer(object):
    """docstring for ParamContainer."""

    def __init__(self, name=""):
        """docstring ParamContainer init method."""
        super(ParamContainer, self).__init__()
        ## String: name of the instrument
        self.name = check_name(name)
        ## List of Parameter object
        self.parameter_list = []
        if type(self) is ParamContainer:
            raise NotImplementedError("ParamContainer should not be instanciated !")

    def set_name(self, name):
        """set the name of the ParamContainer."""
        self.name = check_name(name)
        logger.debug("Name of ParamContainer set to {}".format(check_name(name)))

    def get_name(self):
        """Return the name of the ParamContainer."""
        return self.name

    def get_name_code(self):
        """Return the name of the ParamContainer."""
        return check_name_code(self.get_name())

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
            if param.ismain():
                result.append(param)
        return result

    def get_paramfile_section(self, text_tab=""):
        """Return the text to include in the parameter_file for this CelestialBody.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        name = self.get_name_code()
        entete = "{0} = {{".format(name)
        text = text_tab + entete
        text_tab_param = spacestring_like(text_tab + entete)
        texttab_1tline = False
        for param in self.get_parametrisation():
            text += param.get_paramfile_section(text_tab=text_tab_param,
                                                texttab_1tline=texttab_1tline)
            texttab_1tline = True
        text += text_tab_param + "}\n"
        return text
