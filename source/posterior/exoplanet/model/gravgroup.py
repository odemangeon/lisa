#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

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
    - Move the part of load_parameter_file that update one parameter value to parameter.py
    - Log info the creation of stars and planets in a model
    - Deal with fitting transit times individually
    - Deal with limb darkening coefficients parametrisation
    - Redefine the get_list_main_params routine in gravgroup so that it give the parametrisation of
      the planets and stars inside it.
    - Implement subgravgroups in GravGroup
    - Transform the attributes transit_model, rv_model and ld_model into set and get properties
"""
import logging

from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase

from ...core.model.core_model import Core_Model
from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation


## Logger object
logger = logging.getLogger()


class GravGroup(Core_Model, GravGroup_Parametrisation):
    """docstring for GravGroup."""

    ## category
    __category__ = "GravitionalGroups"

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["ajplanet"]

    ## List of available lc models, the 1st element is used as default
    _transit_models = ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit-MandelAgol": ["quadratic", "linear", "uniform"],
                  "pytransit-Gimenez": ["quadratic", "linear", "uniform"]
                  }

    def __init__(self, name, dataset_db, transit_model=None, ld_model=None, rv_model=None,
                 stars=None, planets=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, dataset_db)
        if "LC" in self.dataset_db.inst_categories:
            # light-curve model
            self.transit_model = transit_model
            # Limb darkening model
            self.ld_model = ld_model
        if "RV" in self.dataset_db.inst_categories:
            # radial velocities model
            self.rv_model = rv_model
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
    def transit_model(self):
        """Returns the name of the transit model used."""
        return self.__transit_model

    @transit_model.setter
    def transit_model(self, model_name):
        """Returns the name of the transit model used."""
        if model_name in self._transit_models:
            self.__transit_model = model_name
        elif model_name is None:
            self.__transit_model = self._transit_models[0]
        else:
            raise AssertionError("transit_model should be in {}".format(self._transit_models))

    @property
    def ld_model(self):
        """Returns the name of the limb darkening model used."""
        return self.__ld_model

    @ld_model.setter
    def ld_model(self, model_name):
        """Returns the name of the limb darkening model used."""
        if model_name in self._ld_models[self.transit_model]:
            self.__ld_model = model_name  # if  batman limb darkening model
        elif model_name is None:
            self.__ld_model = self._ld_models[self.transit_model][0]
        else:
            raise AssertionError("For transit model {}, ld_model should be in {}"
                                 "".format(self.transit_model, self._ld_models[self.transit_model]))

    @property
    def rv_model(self):
        """Returns the name of the transit model used."""
        return self.__rv_model

    @rv_model.setter
    def rv_model(self, model_name):
        """Returns the name of the transit model used."""
        if model_name in self._rv_models:
            self.__rv_model = model_name
        elif model_name is None:
            self.__rv_model = self._rv_models[0]
        else:
            raise AssertionError("rv_model should be in {}".format(self._rv_models))

    def add_a_star(self, name=None):
        """Add a Star in the GravGroup."""
        if self.isavailable_paramcontainer(name, category="stars"):
            logger.warning("A star with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_uppercase:
                if self.isavailable_paramcontainer(possible_name, category="stars"):
                    continue
                else:
                    name = possible_name
                    break
        self.add_a_paramcontainer(Star(name=name, gravgroup=self))

    def add_stars(self, number, names=None):
        """Add Stars in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_star()
        else:
            for i in range(number):
                self.add_a_star(names[i])

    def add_a_planet(self, name=None):
        """Add a Planet in the GravGroup."""
        if self.isavailable_paramcontainer(name, category="planets"):
            logger.warning("A planet with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_lowercase[1:]:
                if self.isavailable_paramcontainer(possible_name, category="planets"):
                    continue
                else:
                    name = possible_name
                    break
        self.add_a_paramcontainer(Planet(name=name, gravgroup=self))

    def add_planets(self, number, names=None):
        """Add Planets in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_planet()
        else:
            for i in range(number):
                self.add_a_planet(names[i])

    # @property
    # def stars(self):
    #     """Returns an OrderedDict containing the stars in the GravGroup."""
    #     if "stars" in self.paramcontainers:
    #         return self.paramcontainers["stars"]
    #     else:
    #         logger.warning("There is no stars in the gravgroup ! Returned None")
    #         return None
    #
    # @property
    # def nb_of_stars(self):
    #     """Returns the number of stars in the GravGroup."""
    #     return len(self.__stars)
    #
    # @property
    # def planets(self):
    #     """Returns an OrderedDict containing the planets in the GravGroup."""
    #     return self.__planets
    #
    # @property
    # def nb_of_planets(self):
    #     """Returns the number of planets in the GravGroup."""
    #     return len(self.__planets)
    #
    # def is_star(self, name):
    #     """Returns True if a star of this name exists in the gravgroup."""
    #     return name in self.stars
    #
    # def is_planet(self, name):
    #     """Returns True if a planet of this name exists in the gravgroup."""
    #     return name in self.planets
    #
    # def rm_star(self, name):
    #     """Delete a Star in the GravGroup."""
    #     res = self.stars.pop(name, None)
    #     if res is None:
    #         logger.warning("The deletion of the star {} from the GravGroup has failed because "
    #                        "this star was not found.".format(name))
    #     else:
    #         logger.info("The star {} has been removed from the GravGroup."
    #                     "".format(name))
    #
    # def rm_planet(self, name):
    #     """Delete a Planet in the GravGroup."""
    #     res = self.planets.pop(name, None)
    #     if res is None:
    #         logger.warning("The deletion of the planet {} from the GravGroup has failed because "
    #                        "this star was not found.".format(name))
    #     else:
    #         logger.info("The planet {} has been removed from the GravGroup."
    #                     "".format(name))
