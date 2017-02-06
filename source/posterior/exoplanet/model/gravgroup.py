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
    - Redefine the get_parametrisation routine in gravgroup so that it give the parametrisation of
      the planets and stars inside it.
    - Implement subgravgroups in GravGroup
    - Transform the attributes transit_model, rv_model and ld_model into set and get properties
"""
import logging

from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase

from ...core.model.core_model import Model
from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation


## Logger object
logger = logging.getLogger()


class GravGroup(Model, GravGroup_Parametrisation):
    """docstring for GravGroup."""

    ## model_type
    _model_type = "ExoP_Standard"

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

    def __init__(self, name, instruments, transit_model=None, ld_model=None, rv_model=None,
                 stars=None, planets=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, instruments)
        if "LC" in self.datatypes_tosim:
            # light-curve model
            self.transit_model = transit_model
            # Limb darkening model
            self.ld_model = ld_model
        if "RV" in self.datatypes_tosim:
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

    @property
    def stars(self):
        """Returns an OrderedDict containing the stars in the GravGroup."""
        return self.__stars

    @property
    def nb_of_stars(self):
        """Returns the number of stars in the GravGroup."""
        return len(self.__stars)

    @property
    def planets(self):
        """Returns an OrderedDict containing the planets in the GravGroup."""
        return self.__planets

    @property
    def nb_of_planets(self):
        """Returns the number of planets in the GravGroup."""
        return len(self.__planets)

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

    def add_a_planet(self, name=None):
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

    def rm_star(self, name):
        """Delete a Star in the GravGroup."""
        res = self.stars.pop(name, None)
        if res is None:
            logger.warning("The deletion of the star {} from the GravGroup has failed because this"
                           "star was not found.".format(name))
        else:
            logger.info("The star {} has been removed from the GravGroup."
                        "".format(name))

    def rm_planet(self, name):
        """Delete a Planet in the GravGroup."""
        res = self.planets.pop(name, None)
        if res is None:
            logger.warning("The deletion of the planet {} from the GravGroup has failed because "
                           "this star was not found.".format(name))
        else:
            logger.info("The planet {} has been removed from the GravGroup."
                        "".format(name))

    def get_paramfile_section(self, text_tab="", entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this GravGroup.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        # entete = "{0} = {{".format(self.name_code)
        # text = text_tab + entete + "\n"
        # text_tab_param = spacestring_like(text_tab + "    ")
        text = "{}# Stars".format(text_tab)
        for star in self.stars.values():
            text += "\n"
            text += star.get_paramfile_section(text_tab=text_tab, entete_symb=entete_symb,
                                               quote_name=quote_name)
        text += "\n# Planets"
        for planet in self.planets.values():
            text += "\n"
            text += planet.get_paramfile_section(text_tab=text_tab, entete_symb=entete_symb,
                                                 quote_name=quote_name)
        self.update_paramfile_info()
        return text

    def update_paramfile_info(self):
        """Update the paramfile info attribute."""
        self.paramfile_info.update({"stars": list(self.stars.keys())})
        self.paramfile_info.update({"planets": list(self.planets.keys())})

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        for paramcont_type in self.paramfile_info.keys():
            for paramcont_name in self.paramfile_info[paramcont_type]:
                paramcont_dico = dico_config[paramcont_name]
                logger.debug("Content of param dictionary for star {}: {}".format(paramcont_name,
                                                                                  paramcont_dico))
                getattr(self, paramcont_type)[paramcont_name].load_config(paramcont_dico)
