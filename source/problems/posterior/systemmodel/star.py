#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Star module.

The objective of this module is to define the Star classe.

"""
from .parameter import Parameter
from source.tools.miscellaneous import spacestring_like


class Star(object):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    def __init__(self, name):
        """docstring Planet init method."""
        super(Star, self).__init__()

        grav_companion = None   # List of gravitational companions
        spectral_type = None
        ## Name of the star
        self.name = name
        ## Radius of the star
        self.R = Parameter(name="R")
        ## Mass of the star
        self.M = Parameter(name="M")
        ## Mean density of the star
        self.rho = Parameter(name="rho")
        ## Age of the star
        self.age = Parameter(name="age")
        ## logg
        self.logg = Parameter(name="logg")
        ## Effective temperature of the star
        self.Teff = Parameter(name="Teff")
        ## Distance to observer
        self.dist = Parameter(name="dist")
        ## Extinction E(B-V)
        self.ebmv = Parameter(name="ebmv")
        ## Proper motion radial velocity contribution
        self.v0 = Parameter(name="v0")
        ## drift in the radial velocity signal
        self.drift = Parameter(name="drift")
        ## Mean Luminosity
        self.L = Parameter(name="L")
        ## Mean Magnitude
        self.mag = Parameter(name="mag")
        ## Mean Flux
        self.F = Parameter(name="F")
        ## Metallicity
        self.feh = Parameter(name="feh")
        ## dict of the list of limb darkening coefficients for an instrument
        limb_dark_coeff = {}  # Dict or vector
        ## dict of limb darkening law for an instrument
        limb_dark_law = {}
        ## List of parameters
        self.parameter_list = [self.R, self.M, self.rho, self.age, self.logg, self.Teff, self.dist,
                               self.ebmv, self.v0, self.drift, self.L, self.mag, self.F, self.feh
                               ]

    def get_short_name(self):
        """Return the short name of the star."""
        return self.name

    def get_full_name(self):
        """Return the full name of the star."""
        return self.name

    def get_short_name_code(self):
        """Return the full name of the planet."""
        name = self.get_short_name()
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
        name = self.get_short_name_code()
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
