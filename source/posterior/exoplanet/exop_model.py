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
from string import ascii_lowercase
from string import ascii_uppercase

from .core.parameter import Parameter
from .core.paramcontainer import ParamContainer
from .core.model.core_model import Model
from source.tools.miscellaneous import check_name_code


## Logger object
logger = logging.getLogger()


class GravGroup(Model):
    """docstring for GravGroup."""

    ## model_type
    _model_type = "ExoP_Standard"

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["ajplanet"]

    ## List of available lc models, the 1st element is used as default
    _lc_models = ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit-MandelAgol": ["quadratic", "linear", "uniform"],
                  "pytransit-Gimenez": ["quadratic", "linear", "uniform"]
                  }

    def __init__(self, name, instruments, transit_model=None, ld_model=None, rv_model=None,
                 stars=None, planets=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, instruments)
        if "LC" in instruments:
            # light-curve model
            if transit_model in self._lc_models:
                self.transit_model = transit_model
            elif transit_model is None:
                self.transit_model = self._lc_models[0]
            else:
                raise ValueError("transit_model should be in {}".format(self._lc_models))
            # Limb darkening model
            if ld_model in self._ld_models[self.transit_model]:
                self.ld_model = ld_model  # if  batman limb darkening model
            elif ld_model is None:
                self.ld_model = self._ld_models[self.transit_model][0]
            else:
                raise ValueError("For transit model {}, ld_model should be in {}"
                                 "".format(self.transit_model, self._ld_models[self.transit_model]))
        if "RV" in instruments:
            # radial velocities model
            if rv_model in self._rv_models:
                self.rv_model = rv_model
            elif rv_model is None:
                self.rv_model = self._rv_models[0]
            else:
                raise ValueError("rv_model should be in {}".format(self._rv_models))
        # Initialise the stars in the system
        ## stars: ordered dictionary of the stars in the grav group
        self.__stars = OrderedDict()
        if isinstance(stars, int):
            if stars >= 1:
                self.add_stars(number=stars)
            else:
                raise ValueError("If you specify the number of stars, it should be "
                                 "strictly positive ! Got {}".format(stars))
        elif isinstance(stars, list) and isinstance(stars[0], str):
            self.add_stars(number=len(stars), names=stars)
        elif stars is None:
            pass
        else:
            raise ValueError("stars should be either a strictly positive int or a list of sting "
                             "or None. {}".format(stars))
        # Initialise the planets in the system
        ## planets: ordered dictionary of the planets in the grav group
        self.__planets = OrderedDict()
        # Initialise the planets in the system
        self.planets = OrderedDict()
        if isinstance(planets, int):
            if planets >= 1:
                self.add_planets(number=planets)
            else:
                raise ValueError("If you specify the number of planets, it should be "
                                 "strictly positive ! Got {}".format(planets))
        elif isinstance(planets, list) and isinstance(planets[0], str):
            self.add_planets(number=len(planets), names=planets)
        elif planets is None:
            pass
        else:
            raise ValueError("planets should be either a strictly positive int or a list of sting "
                             "or None. Got {}".format(planets))
        ## List of Dict: [{"stars": [key in self.stars,], "planets":[key in self.planets]}]
        ## Define sub-gravitational group for example for planets orbiting one componant of a wide
        ## separation binary star. This is kept for later.
        # self.subgravgroups = []

    @property
    def stars(self):
        """Returns an OrderedDict containing the stars in the GravGroup."""
        return self.__stars

    @property
    def planets(self):
        """Returns an OrderedDict containing the planets in the GravGroup."""
        return self.__planets

    def is_star(self, name):
        """Returns True if a star of this name exists in the gravgroup."""
        return name in self.stars

    def add_a_star(self, name=None):
        """Add a Star in the GravGroup."""
        if self.is_star(name):
            logger.warning("A star with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_uppercase:
                if self.is_star(possible_name):
                    continue
                else:
                    name = possible_name
                    break
        self.stars[name] = Star(name=name, gravgroup=self)

    def add_stars(self, number, names=None):
        """Add Stars in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_star()
        else:
            for i in range(number):
                self.add_a_star(names[i])

    def is_planet(self, name):
        """Returns True if a planet of this name exists in the gravgroup."""
        return name in self.planets

    def add_a_planet(self, name):
        """Add a Planet in the GravGroup."""
        if self.is_planet(name):
            logger.warning("A planet with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_lowercase[1:]:
                if self.is_planet(possible_name):
                    continue
                else:
                    name = possible_name
                    break
        self.planets[name] = Planet(name=name, gravgroup=self)

    def add_planets(self, number, names=None):
        """Add Planets in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_planet()
        else:
            for i in range(number):
                self.add_a_planet(names[i])

    def del_a_star(self, name):
        """Delete a Star in the GravGroup."""
        res = self.stars.pop(name, None)
        if res is None:
            logger.warning("The deletion of the star {} from the GravGroup has failed because this"
                           "star was not found.".format(name))

    def del_a_planet(self, name):
        """Delete a Planet in the GravGroup."""
        res = self.planets.pop(name, None)
        if res is None:
            logger.warning("The deletion of the planet {} from the GravGroup has failed because "
                           "this star was not found.".format(name))

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
        if self.hasgravgroup:
            logger.warning("The GravGroup to which the Celestial body belongs has already been "
                           "defined. One should not redefined it so set_gravgroup command is "
                           "ignored")
        else:
            if not isinstance(gravgroup, GravGroup):
                logger.warning("gravgroup should be a GravGroup instance."
                               " Got {}.".format(type(gravgroup)))
            else:
                ## GravGroup: Gravtional group to which the celestial body belongs
                self.gravgroup = gravgroup
                logger.debug("gravgroup of CelestialBody set. "
                             "GravGroup name: {}".format(gravgroup.get_name()))

    def hasgravgroup(self):
        """Indicate if a CelestialBody instance has a attibute gravgroup defined."""
        return hasattr(self, "gravgroup")

    def get_short_name(self):
        """Return the short name of the CelestialBody."""
        return super().get_name()

    def get_name(self):
        """Return the full name of the CelestialBody."""
        if self.hasgravgroup():
            return self.gravgroup.get_name() + '_' + self.get_short_name()
        else:
            return self.get_short_name()

    def get_name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.get_name())


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
