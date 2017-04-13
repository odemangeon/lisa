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
from logging import getLogger
from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase
from copy import deepcopy
from textwrap import dedent
from ajplanet import pl_rv_array

from ...core.model.core_model import Core_Model
from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation
from ....tools.function_w_doc import DocFunction
from ....tools.convert import getecc_fast, getomega_fast, gettp_fast

# from pdb import set_trace


## Logger object
logger = getLogger()


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

    def __init__(self, name, dataset_db, instmodel4dataset=None, l_instmod_fullnames=[],
                 transit_model=None, ld_model=None, rv_model=None,
                 stars=None, planets=None, run_folder=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, dataset_db, run_folder,
                                        instmodel4dataset=instmodel4dataset,
                                        l_instmod_fullnames=l_instmod_fullnames)
        if "LC" in self.dataset_db.inst_categories:
            # light-curve model
            self.transit_model = transit_model
            # Limb darkening model
            self.ld_model = ld_model
        if "RV" in self.dataset_db.inst_categories:
            # radial velocities model
            self.rv_model = rv_model
            # Initialise the dictionary giving the RV zero point RV_references
            self.__RV_references = dict.fromkeys(self.get_inst_names("RV"), None)
            logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
            self.__RV_references["global"] = list(self.__RV_references.keys())[0]
            for key in self.__RV_references:
                if key != "global":
                    self.__RV_references[key] = self.get_instmodel_names(inst_name=key,
                                                                         inst_cat="RV")[0]
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

    @property
    def RV_references(self):
        return self.__RV_references

    @property
    def RV_globalref_instname(self):
        return self.__RV_references["global"]

    def set_RV_globalref_instname(self, inst_name):
        self.__RV_references["global"] = inst_name

    def get_RVref4inst_modname(self, inst_name):
        return self.__RV_references[inst_name]

    def set_RVref4inst_modname(self, inst_name, inst_model_name):
        self.__RV_references[inst_name] = inst_model_name

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
        # Get the star object.
        star = self.stars[list(self.stars.keys())[0]]

        # text_def_func is a dictionary which will received the text of the datasimulator functions
        # It has several keys for several datasimulator functions:
        #   - "whole" for the whole system with all the planets
        #   - "b", "c", ... ("planet name") for only the contribution of one planet.
        text_def_func = {}

        # param_nb is a dictionary that will keep track of the number of parameter for each
        # function in text_def_func (so the keys are the same).
        param_nb = {}

        # arg_list is a dictionary which will receive the argument list of the datasimulator
        # function in text_def_func (so the keys are the same).
        # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
        # keys:
        #   - "param": list of the free parameters name in order
        #   - "kwargs": list of the additional argument taht you need to provide to simulate the
        #               data. For example the time
        arg_list = {}

        # Initialise the template function text
        function_name = ("RVsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model.full_name))
        template_function = """
        def {function_name}(p, t):
        {{tab}}{{preambule}}
        {{tab}}return {{delta_inst_rv}} {{drift_rv}} {{star_mean_rv}} {{planets_rv}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Create for the instrument Delta RV (delta_inst_rv)
        inst_name = inst_model.instrument.name
        ## RVrefglobal_inst: name of the instrument chosen as global RV reference (eg: HARPS)
        RVrefglobal_instname = self.RV_globalref_instname
        ## RVref4inst_modname: name of the instrument model chosen as reference for the current
        ## instrument (eg: default)
        RVref4inst_modname = self.get_RVref4inst_modname(inst_name)
        ## RVrefglobal_modname: name of the instrument model chosen as reference for the global RV
        ## reference instrument (eg: default model of the HARPS instrument)
        RVrefglobal_modname = self.get_RVref4inst_modname(RVrefglobal_instname)
        # Add the Delta_RV of the global RV reference instrument model if needed
        delta_inst_rv = ""  # If no delta RV is main, I still need an empty string
        if inst_name != RVrefglobal_instname:
            instmod_RVref4inst = self.instruments["RV"][inst_name][RVref4inst_modname]
            if instmod_RVref4inst.DeltaRV.main:
                if instmod_RVref4inst.DeltaRV.free:
                    delta_inst_rv += "p[{}] + ".format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(instmod_RVref4inst.DeltaRV.full_name)
                else:
                    delta_inst_rv += "{} + ".format(instmod_RVref4inst.DeltaRV.value)
        # Add the Delta_RV of the model used as RV reference for the current instrument
        if inst_model.name != RVref4inst_modname:
            if inst_model.DeltaRV.main:
                if inst_model.DeltaRV.free:
                    delta_inst_rv += "p[{}] + ".format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(inst_model.DeltaRV.full_name)
                else:
                    delta_inst_rv += "{} + ".format(inst_model.DeltaRV.value)

        # Create the text for the istrument RV drift (drift_rv)
        if inst_model.drift.main:
            if inst_model.drift.free:
                drift_rv = "p[{}] * t + ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(inst_model.drift.full_name)
            else:
                drift_rv = "{} * t + ".format(inst_model.drift.value)
        else:
            drift_rv = ""

        # Create the text for the star mean RV (star_mean_rv)
        if star.v0.free:
            star_mean_rv = "p[{}]".format(param_nb[self.key_whole])
            param_nb[self.key_whole] += 1
            arg_list[self.key_whole]["param"].append(star.v0.full_name)
        else:
            star_mean_rv = "{}".format(star.v0.value)

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
        # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
        # planets functions.
        preambule_whole = ""
        template_preambule = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
        """
        template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet},"
                              " {P})")
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            for param_name, param in zip(["K", "secosw", "sesinw", "tc", "P"],
                                         [planet.K, planet.secosw, planet.sesinw, planet.t0,
                                          planet.P]):
                if param.free:
                    param_text = "p[{}]"
                    params_whole[param_name] = param_text.format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(param.full_name)
                    params_planet[param_name] = param_text.format(param_nb[planet.name])
                    param_nb[planet.name] += 1
                    arg_list[planet.name]["param"].append(param.full_name)
                else:
                    params_whole[param_name] = "{}".format(param.value)
                    params_planet[param_name] = params_whole[param_name]

            # Create the preambule text that compute intermediate variables
            preambule_planet = (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_planet["secosw"],
                                       sesinw=params_planet["secosw"], P=params_planet["P"],
                                       tc=params_planet["tc"], tab=tab))
            preambule_whole += (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["secosw"], P=params_whole["P"],
                                       tc=params_whole["tc"], tab=tab))

            # planets RV contribution (planet_rv and whole_planets_rv)
            planet_rv = template_planet_rv.format(planet=planet.name, K=params_planet["K"],
                                                  P=params_planet["K"])
            whole_planets_rv = template_planet_rv.format(planet=planet.name, K=params_whole["K"],
                                                         P=params_whole["K"])

            # Finalise the  text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 delta_inst_rv=delta_inst_rv, drift_rv=drift_rv,
                                                 star_mean_rv=star_mean_rv, planets_rv=planet_rv,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

            # Add time in the kwargs entry of the planet arg_list
            arg_list[planet.name]["kwargs"].append("t")

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                delta_inst_rv=delta_inst_rv, drift_rv=drift_rv,
                                                star_mean_rv=star_mean_rv, tab=tab,
                                                planets_rv=whole_planets_rv))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create the text for the planet contribution to the RV signal with ajplanet
        # text_pl_rv_array = " + pl_rv_array(t, 0."
        # text_def_func[planet.name] += text_pl_rv_array
        # text_def_func[self.key_whole] += text_pl_rv_array
        # for param in [planet.K, [planet.secosw, planet.sesinw], planet.t0, planet.P]:
        #     if param == [planet.secosw, planet.sesinw]:
        #         test_param = (", omega_{}, ecc_{}")
        #         text_sys = []
        #         text_planet = []
        #         for par in param:
        #             if par.free:
        #                 text = "p[{}]"
        #                 text_sys.append(text.format(param_nb[self.key_whole]))
        #                 param_nb[self.key_whole] += 1
        #                 arg_list[self.key_whole]["param"].append(par.full_name)
        #                 text_planet.append(text.format(param_nb[planet.name]))
        #                 param_nb[planet.name] += 1
        #                 arg_list[planet.name]["param"].append(par.full_name)
        #             else:
        #                 text = "{}"
        #                 text_sys.append(text.format(par.value))
        #                 text_planet.append(text.format(par.value))
        #     elif param == planet.t0:
        #         pass
        #     else:
        #         test_param = ", {}"
        #         if param.free:
        #             text = "p[{}]"
        #             text_sys = text.format(param_nb[self.key_whole])
        #             param_nb[self.key_whole] += 1
        #             arg_list[self.key_whole]["param"].append(param.full_name)
        #             text_planet = text.format(param_nb[planet.name])
        #             param_nb[planet.name] += 1
        #             arg_list[planet.name]["param"].append(param.full_name)
        #         else:
        #             text_sys = "{}".format(param.value)
        #             text_planet = text_sys
        #     # Add the parameter to the text of the function for the whole system and the current
        #     # planet
        #     text_def_func[self.key_whole] += test_param.format(text_sys)
        #     text_def_func[planet.name] += test_param.format(text_planet)
        # # Create the text for the planet contribution to the RV signal with ajplanet
        # text_def_func[self.key_whole] += ")"
        # text_def_func[planet.name] += ")"
        #
        #

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict = locals().copy()
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["gettp_fast"] = gettp_fast
            ldict["pl_rv_array"] = pl_rv_array
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
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
