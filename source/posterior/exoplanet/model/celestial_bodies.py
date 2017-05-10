#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the CelestialBody, Star and Planet class.

@TODO:
    - Make the adding of the name_prefix when a parameter is created in a Core_ParamContainer
"""
from logging import getLogger

from ...core.parameter import Parameter
from ...core.paramcontainer import Core_ParamContainer

## Logger object
logger = getLogger()


class CelestialBody(Core_ParamContainer):
    """docstring for CelestialBody."""

    __category__ = "celestialbodies"

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
        # name_prefix is set to None because it will be set when the gravgroup is set.
        super(CelestialBody, self).__init__(name=name)
        self.gravgroup = gravgroup
        # Make CelestialBody not instanciable (abstract class)
        if type(self) is CelestialBody:
            raise NotImplementedError("CelestialBody should not be instanciated !")

    @property
    def gravgroup(self):
        """Return the GravGroup instance to which the Celestial Body belongs."""
        return self.__gravgroup

    @gravgroup.setter
    def gravgroup(self, gravgroup):
        """Set the gravgroup attribute of a CelestialBody."""
        if self.hasgravgroup:
            logger.warning("The GravGroup to which the Celestial body belongs has already been "
                           "defined. One should not redefined it so set_gravgroup command is "
                           "ignored")
        else:
            if gravgroup is None:
                logger.debug("No Gravgroup provided for CelestialBody {}.".format(self.name))
            else:
                self.__gravgroup = gravgroup
                self.name_prefix = gravgroup.name
                logger.debug("gravgroup of CelestialBody {} set to {}."
                             "".format(self.name, gravgroup.name))

    @property
    def hasgravgroup(self):
        """Indicate if a CelestialBody instance has a attibute gravgroup defined."""
        if hasattr(self, "gravgroup"):
            return self.gravgroup is not None
        else:
            return False


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

    __category__ = "planets"

    def __init__(self, gravgroup=None, name=""):
        """docstring Planet init method."""
        super(Planet, self).__init__(gravgroup, name)
        ## Radius of the planet
        self.add_parameter(Parameter(name="R", name_prefix=self.full_name, main=False))
        ## Mass of the planet
        self.add_parameter(Parameter(name="M", name_prefix=self.full_name, main=False))
        ## Mean density of the planet
        self.add_parameter(Parameter(name="rho", name_prefix=self.full_name, main=False))
        ## Density of the star from the transit
        self.add_parameter(Parameter(name="rhostar", name_prefix=self.full_name, main=False))
        ## logg of the star from the transit
        self.add_parameter(Parameter(name="loggstar", name_prefix=self.full_name, main=False))
        ## Age of the planet
        self.add_parameter(Parameter(name="age", name_prefix=self.full_name, main=False))
        ## Orbital period
        self.add_parameter(Parameter(name="P", name_prefix=self.full_name, main=False))
        ## log Orbital period
        self.add_parameter(Parameter(name="logP", name_prefix=self.full_name, main=False))
        ## Semi-major axis
        self.add_parameter(Parameter(name="a", name_prefix=self.full_name, main=False))
        ## Excentricity
        self.add_parameter(Parameter(name="ecc", name_prefix=self.full_name, main=False))
        ## Inclination
        self.add_parameter(Parameter(name="inc", name_prefix=self.full_name, main=False))
        ## Cos Inclination
        self.add_parameter(Parameter(name="cosinc", name_prefix=self.full_name, main=False))
        ## Impact parameter
        self.add_parameter(Parameter(name="b", name_prefix=self.full_name, main=False))
        ## Argument of periastron of star (= argument of periastron of planet + pi)
        self.add_parameter(Parameter(name="omega", name_prefix=self.full_name, main=False))
        ## Longitude of the acending node
        self.add_parameter(Parameter(name="OMEGA", name_prefix=self.full_name, main=False))
        ## First Transit time
        self.add_parameter(Parameter(name="tc", name_prefix=self.full_name, main=False))
        ## Radial velocity semi-amplitude
        self.add_parameter(Parameter(name="K", name_prefix=self.full_name, main=False))
        ## log Radial velocity semi-amplitude
        self.add_parameter(Parameter(name="logK", name_prefix=self.full_name, main=False))
        ## Radius ratio planet over star
        self.add_parameter(Parameter(name="Rrat", name_prefix=self.full_name, main=False))
        ## Transit depth
        self.add_parameter(Parameter(name="Trdepth", name_prefix=self.full_name, main=False))
        ## Mass ratio planet over star
        self.add_parameter(Parameter(name="Mrat", name_prefix=self.full_name, main=False))
        ## a over R, ratio of semi-major axis over Radius of the host star
        self.add_parameter(Parameter(name="aR", name_prefix=self.full_name, main=False))
        ## log a over R, ratio of semi-major axis over Radius of the host star
        # self.add_parameter(Parameter(name="logaR", name_prefix=self.full_name, main=False))
        ## sqrt(ecc) . cos(w)
        self.add_parameter(Parameter(name="secosw", name_prefix=self.full_name, main=False))
        ## sqrt(ecc) . sin(w)
        self.add_parameter(Parameter(name="sesinw", name_prefix=self.full_name, main=False))
        ## Transit duration D14
        self.add_parameter(Parameter(name="D14", name_prefix=self.full_name, main=False))
        ## Transit duration D23
        self.add_parameter(Parameter(name="D23", name_prefix=self.full_name, main=False))
        ## Transit duration D12
        self.add_parameter(Parameter(name="D12", name_prefix=self.full_name, main=False))
        ## Circularisation time
        self.add_parameter(Parameter(name="circtime", name_prefix=self.full_name, main=False))
        ## Teq: Equilibrium Temperature
        self.add_parameter(Parameter(name="Teq", name_prefix=self.full_name, main=False))
        ## transit times
        self.transit_times = {}


class Star(CelestialBody):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    __category__ = "stars"

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
        self.add_parameter(Parameter(name="R", name_prefix=self.full_name, main=False))
        ## Mass of the star
        self.add_parameter(Parameter(name="M", name_prefix=self.full_name, main=False))
        ## Mean density of the star
        self.add_parameter(Parameter(name="rho", name_prefix=self.full_name, main=False))
        ## Age of the star
        self.add_parameter(Parameter(name="age", name_prefix=self.full_name, main=False))
        ## logg
        self.add_parameter(Parameter(name="logg", name_prefix=self.full_name, main=False))
        ## Effective temperature of the star
        self.add_parameter(Parameter(name="Teff", name_prefix=self.full_name, main=False))
        ## Distance to observer
        self.add_parameter(Parameter(name="dist", name_prefix=self.full_name, main=False))
        ## Extinction E(B-V)
        self.add_parameter(Parameter(name="ebmv", name_prefix=self.full_name, main=False))
        ## Proper motion radial velocity contribution
        self.add_parameter(Parameter(name="v0", name_prefix=self.full_name, main=False))
        ## drift in the radial velocity signal
        self.add_parameter(Parameter(name="drift", name_prefix=self.full_name, main=False))
        ## Mean Luminosity
        self.add_parameter(Parameter(name="L", name_prefix=self.full_name, main=False))
        ## Mean Magnitude
        self.add_parameter(Parameter(name="mag", name_prefix=self.full_name, main=False))
        ## Mean Flux
        self.add_parameter(Parameter(name="F", name_prefix=self.full_name, main=False))
        ## Metallicity
        self.add_parameter(Parameter(name="feh", name_prefix=self.full_name, main=False))
        ## dict of the list of limb darkening coefficients for an instrument
        self.ld_coeff = {}  # Dict or vector
        ## dict of limb darkening law for an instrument
        self.ld_models = {}
