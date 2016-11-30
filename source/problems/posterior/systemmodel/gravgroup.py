#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (GravGroup) module.

The objective of this module is to define the GravGroup, Star and Planet class.
A GravGroup intance is a group of gravitationnaly bond objects (stars or planets).
It could be:
- a stellar planetary system (one star, and one or several planets),
- a binary system (two star, no planets),
- a herarchical triple system (two stars, one planet orbiting around one of the stars)
- a circum binary system (a planet orbiting, a binary star)
- any combinaison of stars and planets (for now I think it should contain at least two objects
  including at least a star so that it produces a variable signal in RV and or LC)

@TODO:
    - Introduce spectral type in Star Class
    - Implement subgravgroups in GravGroup
"""
import logging

from collections import OrderedDict

from .core.parameter import Parameter
from .core.paramcontainer import ParamContainer
from source.tools.miscellaneous import check_name_code


## Logger object
logger = logging.getLogger()


class GravGroup(ParamContainer):
    """docstring for GravGroup."""

    def __init__(self, name):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name)
        ## OrderedDict: dictionary of the stars in the grav group
        self.stars = OrderedDict()
        ## OrderedDict: dictionary of the planets in the grav group
        self.planets = OrderedDict()
        ## List of Dict: [{"stars": [key in self.stars,], "planets":[key in self.planets]}]
        ## Define sub-gravitational group for example for planets orbiting one componant of a wide
        ## separation binary star.
        self.subgravgroups = []

    def get_paramfile_section(self, text_tab=""):
        """Return the text to include in the parameter_file for this GravGroup.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.


        TODO: Decide if this is needed
        """
        pass


class CelestialBody(ParamContainer):
    """docstring for CelestialBody."""

    def __init__(self, gravgroup, name):
        """docstring GravGroup init method."""
        super(CelestialBody, self).__init__(name)
        if not isinstance(gravgroup, GravGroup):
            raise ValueError("gravgroup should be a GravGroup instance."
                             " Got {}.".format(type(gravgroup)))
        ## GravGroup: Gravtional group to which the celestial body belongs
        self.gravgroup = gravgroup

    def get_short_name(self):
        """Return the short name of the CelestialBody."""
        return super().get_name()

    def get_name(self):
        """Return the full name of the CelestialBody."""
        return self.gravgroup.get_name() + '_' + self.get_short_name()

    def get_name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.get_name())


class Planet(CelestialBody):
    """docstring for Planet."""

    def __init__(self, gravgroup, name):
        """docstring Planet init method."""
        super(Planet, self).__init__(gravgroup, name)
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
        # Update List of parameters
        super().extend_list_params([self.R, self.M, self.rho, self.age, self.period, self.a,
                                    self.ecc, self.inc, self.b, self.w, self.Omega, self.t0,
                                    self.K, self.R_rat, self.M_rat, self.ar, self.ecosw, self.esinw
                                    ])


class Star(CelestialBody):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    def __init__(self, gravgroup, name):
        """docstring Planet init method."""
        super(Star, self).__init__(gravgroup, name)
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
        # Update List of parameters
        super().extend_list_params([self.R, self.M, self.rho, self.age, self.logg, self.Teff,
                                    self.dist, self.ebmv, self.v0, self.drift, self.L, self.mag,
                                    self.F, self.feh
                                    ])
