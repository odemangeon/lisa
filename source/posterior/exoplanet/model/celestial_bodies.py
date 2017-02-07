#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the CelestialBody, Star and Planet class.

@TODO:
    - Make the adding of the name_prefix when a parameter is created in a ParamContainer
"""
import logging

from ...core.parameter import Parameter
from ...core.paramcontainer import ParamContainer
from source.tools.miscellaneous import check_name_code


## Logger object
logger = logging.getLogger()


class CelestialBody(ParamContainer):
    """docstring for CelestialBody."""

    def __init__(self, gravgroup=None, name=""):
        """docstring GravGroup init method.

        ----

        Arguments:
            gravgroup   : GravGroup, (default: None),
                Gravgroup instance to which the star belongs.
            name        : String, (default: ""),
                Name of the star (if the star is K2-19_A, its name will be 'A' and 'K2-19' would be
                the name of the GravGroup)
        """
        super(CelestialBody, self).__init__(name)
        if gravgroup is None:
            logger.debug("CelestialBody instance created without providing a GravGroup.")
        else:
            self.set_gravgroup(gravgroup)
        # Make CelestialBody not instanciable (abstract class)
        if type(self) is CelestialBody:
            raise NotImplementedError("CelestialBody should not be instanciated !")

    def set_gravgroup(self, gravgroup):
        """Set the gravgroup attribute of a CelestialBody."""
        if self.hasgravgroup():
            logger.warning("The GravGroup to which the Celestial body belongs has already been "
                           "defined. One should not redefined it so set_gravgroup command is "
                           "ignored")
        else:
            self.gravgroup = gravgroup
            logger.debug("gravgroup of CelestialBody set. "
                         "GravGroup name: {}".format(gravgroup.name))

    def hasgravgroup(self):
        """Indicate if a CelestialBody instance has a attibute gravgroup defined."""
        return hasattr(self, "gravgroup")

    @property
    def full_name(self):
        """Return the full name of the CelestialBody."""
        if self.hasgravgroup():
            return self.gravgroup.name + '_' + self.name
        else:
            return self.name

    @property
    def name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.name)

    @property
    def full_name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.full_name)


class Planet(CelestialBody):
    """docstring for Planet.

    ----

    Arguments:
        gravgroup   : GravGroup, (default: None),
            Gravgroup instance to which the planet belongs.
        name        : String, (default: ""),
            Name of the planet (if the planet is K2-19_b, its name will be 'b' and 'K2-19' would be
            the name of the GravGroup)
    """

    def __init__(self, gravgroup=None, name=""):
        """docstring Planet init method."""
        super(Planet, self).__init__(gravgroup, name)
        ## Radius of the planet
        self.R = Parameter(name="R", name_prefix=self.full_name, main=False)
        ## Mass of the planet
        self.M = Parameter(name="M", name_prefix=self.full_name, main=False)
        ## Mean density of the planet
        self.rho = Parameter(name="rho", name_prefix=self.full_name, main=False)
        ## Age of the planet
        self.age = Parameter(name="age", name_prefix=self.full_name, main=False)
        ## Orbital period
        self.P = Parameter(name="P", name_prefix=self.full_name, main=False)
        ## log Orbital period
        self.logP = Parameter(name="logP", name_prefix=self.full_name, main=False)
        ## Semi-major axis
        self.a = Parameter(name="a", name_prefix=self.full_name, main=False)
        ## Excentricity
        self.ecc = Parameter(name="ecc", name_prefix=self.full_name, main=False)
        ## Inclination
        self.inc = Parameter(name="inc", name_prefix=self.full_name, main=False)
        ## Cos Inclination
        self.cosinc = Parameter(name="inc", name_prefix=self.full_name, main=False)
        ## Impact parameter
        self.b = Parameter(name="b", name_prefix=self.full_name, main=False)
        ## Argument of periapsis
        self.w = Parameter(name="w", name_prefix=self.full_name, main=False)
        ## Longitude of the acending node
        self.Omega = Parameter(name="Omega", name_prefix=self.full_name, main=False)
        ## First Transit time
        self.t0 = Parameter(name="t0", name_prefix=self.full_name, main=False)
        ## Radial velocity semi-amplitude
        self.K = Parameter(name="K", name_prefix=self.full_name, main=False)
        ## log Radial velocity semi-amplitude
        self.logK = Parameter(name="K", name_prefix=self.full_name, main=False)
        ## Radius ratio planet over star
        self.R_rat = Parameter(name="R_rat", name_prefix=self.full_name, main=False)
        ## Mass ratio planet over star
        self.M_rat = Parameter(name="M_rat", name_prefix=self.full_name, main=False)
        ## a over R, ratio of semi-major axis over Radius of the host star
        self.ar = Parameter(name="ar", name_prefix=self.full_name, main=False)
        ## log a over R, ratio of semi-major axis over Radius of the host star
        self.logar = Parameter(name="ar", name_prefix=self.full_name, main=False)
        ## ecc . cos(w)
        self.ecosw = Parameter(name="ecosw", name_prefix=self.full_name, main=False)
        ## ecc . sin(w)
        self.esinw = Parameter(name="esinw", name_prefix=self.full_name, main=False)
        ## transit times
        self.transit_times = {}
        # Update List of parameters
        super().extend_list_params([self.R, self.M, self.rho, self.age, self.P, self.a,
                                    self.ecc, self.inc, self.b, self.w, self.Omega, self.t0,
                                    self.K, self.R_rat, self.M_rat, self.ar, self.ecosw, self.esinw
                                    ])


class Star(CelestialBody):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    def __init__(self, gravgroup=None, name=""):
        """docstring Planet init method.

        ----

        Arguments:
            gravgroup   : GravGroup, (default: None),
                Gravgroup instance to which the star belongs.
            name        : String, (default: ""),
                Name of the star (if the star is K2-19_A, its name will be 'A' and 'K2-19' would be
                the name of the GravGroup)
        """
        super(Star, self).__init__(gravgroup, name)
        ## Radius of the star
        self.R = Parameter(name="R", name_prefix=self.full_name, main=False)
        ## Mass of the star
        self.M = Parameter(name="M", name_prefix=self.full_name, main=False)
        ## Mean density of the star
        self.rho = Parameter(name="rho", name_prefix=self.full_name, main=False)
        ## Age of the star
        self.age = Parameter(name="age", name_prefix=self.full_name, main=False)
        ## logg
        self.logg = Parameter(name="logg", name_prefix=self.full_name, main=False)
        ## Effective temperature of the star
        self.Teff = Parameter(name="Teff", name_prefix=self.full_name, main=False)
        ## Distance to observer
        self.dist = Parameter(name="dist", name_prefix=self.full_name, main=False)
        ## Extinction E(B-V)
        self.ebmv = Parameter(name="ebmv", name_prefix=self.full_name, main=False)
        ## Proper motion radial velocity contribution
        self.v0 = Parameter(name="v0", name_prefix=self.full_name, main=False)
        ## drift in the radial velocity signal
        self.drift = Parameter(name="drift", name_prefix=self.full_name, main=False)
        ## Mean Luminosity
        self.L = Parameter(name="L", name_prefix=self.full_name, main=False)
        ## Mean Magnitude
        self.mag = Parameter(name="mag", name_prefix=self.full_name, main=False)
        ## Mean Flux
        self.F = Parameter(name="F", name_prefix=self.full_name, main=False)
        ## Metallicity
        self.feh = Parameter(name="feh", name_prefix=self.full_name, main=False)
        ## dict of the list of limb darkening coefficients for an instrument
        self.ld_coeff = {}  # Dict or vector
        ## dict of limb darkening law for an instrument
        self.ld_models = {}
        # Update List of parameters
        super().extend_list_params([self.R, self.M, self.rho, self.age, self.logg, self.Teff,
                                    self.dist, self.ebmv, self.v0, self.drift, self.L, self.mag,
                                    self.F, self.feh
                                    ])
