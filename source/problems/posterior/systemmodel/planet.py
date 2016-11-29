#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Planet module.

The objective of this module is to define the Planet classe.

"""
from .parameter import Parameter
from source.tools.miscellaneous import spacestring_like


class Planet(object):
    """docstring for Planet."""

    def __init__(self, name, host_star):
        """docstring Planet init method."""
        super(Planet, self).__init__()
        ## Gravitational host star
        self.host_star = host_star
        ## Name of the planet
        self.name = name
        ## Radius of the planet
        self.R = Parameter(name="R")
        ## Mass of the planet
        self.M = Parameter(name="M")
        ## Mean density of the planet
        self.rho = Parameter(name="rho")
        ## Age of the planet
        self.age = Parameter(name="age")
        ## Orbital period
        self.period = Parameter(name="P")
        ## Semi-major axis
        self.a = Parameter(name="a")
        ## Excentricity
        self.ecc = Parameter(name="ecc")
        ## Inclination
        self.inc = Parameter(name="inc")
        ## Impact parameter
        self.b = Parameter(name="b")
        ## Argument of periapsis
        self.w = Parameter(name="w")
        ## Longitude of the acending node
        self.Omega = Parameter(name="Omega")
        ## First Transit time
        self.t0 = Parameter(name="t0")
        ## Radial velocity semi-amplitude
        self.K = Parameter(name="K")
        ## Radius ratio planet over star
        self.R_rat = Parameter(name="R_rat")
        ## Mass ratio planet over star
        self.M_rat = Parameter(name="M_rat")
        ## a over R, ratio of semi-major axis over Radius of the host star
        self.ar = Parameter(name="ar")
        ## ecc . cos(w)
        self.ecosw = Parameter(name="ecosw")
        ## ecc . sin(w)
        self.esinw = Parameter(name="esinw")
        ## List of parameters
        self.parameter_list = [self.R, self.M, self.rho, self.age, self.period, self.a, self.ecc,
                               self.inc, self.b, self.w, self.Omega, self.t0, self.K, self.R_rat,
                               self.M_rat, self.ar, self.ecosw, self.esinw
                               ]

    def get_short_name(self):
        """Return the short name of the planet."""
        return self.name

    def get_full_name(self):
        """Return the full name of the planet."""
        return self.host_star.get_short_name() + "_" + self.name

    def get_full_name_code(self):
        """Return the full name of the planet."""
        name = self.get_full_name()
        return name.replace("-", "")

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
        name = self.get_full_name_code()
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
