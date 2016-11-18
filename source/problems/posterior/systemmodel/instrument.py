#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Instrument module.

The objective of this module is to define the Instrument classes.

"""
from .parameter import Parameter
from source.tools.miscellaneous import spacestring_like


class Instrument(object):
    """docstring for Instrument."""

    spectral_transmission = None

    def __init__(self, name, inst_type):
        """docstring for Instrument init method."""
        super(Instrument, self).__init__()
        ## Name of the instrument
        self.name = name
        ## Jitter of the instrument
        self.jitter = Parameter(name="jitter")
        ## List of parameters
        self.parameter_list = [self.jitter,
                               ]

    def get_short_name(self):
        """Return the short name of the instrument."""
        return self.name

    def get_full_name(self):
        """Return the full name of the instrument."""
        return self.name

    def get_parametrisation(self):
        """Return the list of main parameters (non redondant parameter)."""
        result = []
        for param in self.get_list_params():
            if param.ismain():
                result.append(param)
        return result

    def get_list_params(self):
        """Return the list of all parameters."""
        return self.parameter_list

    def get_paramfile_section(self, text_tab=""):
        """Return the text to include in the parameter_file for this parameter.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        name = self.get_full_name()
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
