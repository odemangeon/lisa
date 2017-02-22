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
from copy import deepcopy
from ajplanet import pl_rv_array

from ...core.model.core_model import Core_Model
from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation
from ....tools.function_w_doc import DocFunction
from ....tools.convert import getecc_fast, getomega_fast

from pdb import set_trace


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
                 stars=None, planets=None, run_folder=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, dataset_db, run_folder)
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

    @property
    def stars(self):
        return self.paramcontainers["stars"]

    @property
    def nb_star(self):
        return self.nb_of_paramcontainers["stars"]

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

    @property
    def planets(self):
        return self.paramcontainers["planets"]

    @property
    def nb_planets(self):
        return self.nb_of_paramcontainers["planets"]

    def _create_datasimulator_RV(self, inst_model):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each instrument
        model individually.

        This function does:
            1. Check if the dataset_db contain RV data
            2. If Yes:
                2.1. for each planet
        ----
        Returns:
            - 1 data simulator function for the whole dataset.
            - 3 levels dictionary with instrument category, instrument name, instrument model
            containing function that take parameters values and return simulated data.
        """
        # Need to know which parametrisation is used
        star = self.stars[list(self.stars.keys())[0]]
        text_def_func = {}
        param_nb = {}
        arg_list = {}
        function_name = "RV_simulator"
        text_def_func[self.name] = "def {}(p, t):\n    return ".format(function_name)
        arg_list[self.name] = OrderedDict()
        arg_list[self.name]["param"] = []
        arg_list[self.name]["kwargs"] = []
        param_nb[self.name] = 0
        if inst_model.drift.main:
            if inst_model.drift.free:
                text_param_drift = "p[{}] * t + ".format(param_nb[self.name])
                param_nb[self.name] += 1
                arg_list[self.name]["param"].append(inst_model.drift.full_name)
            else:
                text_param_drift = "{} * t + ".format(inst_model.drift.value)
            text_def_func[self.name] += text_param_drift
        if star.v0.free:
            text_param_v0 = "p[{}]".format(param_nb[self.name])
            param_nb[self.name] += 1
            arg_list[self.name]["param"].append(star.v0.full_name)
        else:
            text_param_v0 = "{}".format(star.v0.value)
        text_def_func[self.name] += text_param_v0
        param_nb_before = param_nb[self.name]
        arg_list_before = deepcopy(arg_list[self.name])
        for i, planet in enumerate(self.planets.values()):
            text_def_func[planet.full_name] = text_def_func[self.name]
            arg_list[planet.full_name] = arg_list_before
            param_nb[planet.full_name] = param_nb_before
            text_pl_rv_array = " + pl_rv_array(t, 0."
            text_def_func[planet.full_name] += text_pl_rv_array
            text_def_func[self.name] += text_pl_rv_array
            for param in [planet.K, [planet.ecosw, planet.esinw], planet.t0, planet.P]:
                if param == [planet.ecosw, planet.esinw]:
                    test_param = (", getomega_fast({0[0]}, {0[1]}), "
                                  "getecc_fast({0[0]}, {0[1]})")
                    text_sys = []
                    text_planet = []
                    for par in param:
                        if par.free:
                            text = "p[{}]"
                            text_sys.append(text.format(param_nb[self.name]))
                            param_nb[self.name] += 1
                            arg_list[self.name]["param"].append(par.full_name)
                            text_planet.append(text.format(param_nb[planet.full_name]))
                            param_nb[planet.full_name] += 1
                            arg_list[planet.full_name]["param"].append(par.full_name)
                        else:
                            text = "{}"
                            text_sys.append(text.format(par.value))
                            text_planet.append(text.format(par.value))
                else:
                    test_param = ", {}"
                    if param.free:
                        text = "p[{}]"
                        text_sys = text.format(param_nb[self.name])
                        param_nb[self.name] += 1
                        arg_list[self.name]["param"].append(param.full_name)
                        text_planet = text.format(param_nb[planet.full_name])
                        param_nb[planet.full_name] += 1
                        arg_list[planet.full_name]["param"].append(param.full_name)
                    else:
                        text_sys = "{}".format(param.value)
                        text_planet = text_sys
                text_def_func[self.name] += test_param.format(text_sys)
                text_def_func[planet.full_name] += test_param.format(text_planet)
            text_def_func[self.name] += ")"
            text_def_func[planet.full_name] += ")"
            arg_list[planet.full_name]["kwargs"].append("time")
        arg_list[self.name]["kwargs"].append("time")
        logger.debug("Dictionnary containing the texts of the futur datasimulator functions :\n"
                     "{}".format(text_def_func))
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for key in dico_docf:
            exec(text_def_func[key])
            dico_docf[key] = DocFunction(function=locals()[function_name],
                                         arg_list=arg_list[key])
        return dico_docf

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
