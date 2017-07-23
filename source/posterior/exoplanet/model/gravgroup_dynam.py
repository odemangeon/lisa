#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Dynamical Gravitational group (gravgroup) module.

The objective of this module is to define the GravGroupDyn class.
A GravGroupDyn intance is a SubClass of GravGroup for which will use dynamical code to interpret the
data.

@TODO:
"""
from logging import getLogger
from os.path import isfile, join
from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase
from copy import deepcopy
from textwrap import dedent
from math import acos, degrees
from ajplanet import pl_rv_array
from batman import TransitModel, TransitParams
from pytransit import MandelAgol


from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation
from .gravgroup import GravGroup
from .limb_darkening import Manager_LD, CoreLD
from ....tools.function_w_doc import DocFunction
from ....tools.convert import getecc_fast, getomega_fast, gettp_fast, getaoverr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like

# from pdb import set_trace


## Logger object
logger = getLogger()


mgr_LD = Manager_LD()


class GravGroupDyn(GravGroup):
    """docstring for GravGroup."""

    ## category
    __category__ = "GravitionalGroupsWDynamic"

    ## List of available ttv models, the 1st element is used as default
    _ttv_models = ["ttvfast"]

    def __init__(self, name, dataset_db, instmodel4dataset=None, l_instmod_fullnames=[],
                 transit_model=None, rv_model=None, ttv_model=None, parametrisation=None,
                 stars=None, planets=None, run_folder=None):
        """docstring Planet init method."""
        super(GravGroupDyn, self).__init__(name, dataset_db, run_folder,
                                           instmodel4dataset=instmodel4dataset,
                                           l_instmod_fullnames=l_instmod_fullnames,
                                           transit_model=transit_model, rv_model=rv_model,
                                           parametrisation=parametrisation,
                                           stars=stars, planets=planets)
        if "TTV" in self.dataset_db.inst_categories:
            # light-curve model
            self.ttv_model = ttv_model

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        dico = GravGroupDyn.init_kwargs.fget(self)
        if "TTV" in self.dataset_db.inst_categories:
            dico["ttv_model"] = self.ttv_model
        return dico

    @property
    def ttv_model(self):
        """Returns the name of the ttv model used."""
        return self.__ttv_model

    @ttv_model.setter
    def ttv_model(self, model_name):
        """Set the name of the transit model used."""
        if model_name in self._ttv_models:
            self.__ttv_model = model_name
        elif model_name is None:
            self.__ttv_model = self._ttv_models[0]
        else:
            raise AssertionError("ttv_model should be in {}".format(self._ttv_models))

    def _create_datasimulator_TTV_RV(self, inst_model, dataset=None):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each instrument
        model individually.

        ----
        Returns:
            - 1 data simulator function for the whole dataset.
            - 3 levels dictionary with instrument category, instrument name, instrument model
            containing function that take parameters values and return simulated data.
        """
        # Get the star object.
        star = self.stars[list(self.stars.keys())[0]]

        # text_def_func is a dictionary which will received the text of the datasimulator functions
        # This one has just one key for one datasimulator functions:
        #   - "whole" for the whole system with all the planets
        #   - Making single planet function doesn't make sense when we look at the dynamical effect
        #     in multis
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
        function_name = ("TTVRVsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model.full_name))
        template_function = """
        def {function_name}({{arguments}}):
        {{tab}}{{preambule}}
        {{tab}}return {{delta_inst_rv}} {{star_mean_rv}} {{planets_rv}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Create the arguments text
        if dataset is None:
            arguments = "p, t, tref=None"
        else:
            arguments = "p"

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        if dataset is None:
            arg_list[self.key_whole]["kwargs"].append("t")

        # Create for the instrument Delta RV (delta_inst_rv)
        inst_name = inst_model.instrument.name
        ## RVrefglobal_inst: name of the instrument chosen as global RV reference (eg: HARPS)
        RVrefglobal_instname = self.RV_globalref_instname
        ## RVref4inst_modname: name of the instrument model chosen as reference for the current
        ## instrument (eg: default)
        RVref4inst_modname = self.get_RVref4inst_modname(inst_name)
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

        # Create the text for the star mean RV (star_mean_rv)
        if star.v0.free:
            star_mean_rv = "p[{}]".format(param_nb[self.key_whole])
            param_nb[self.key_whole] += 1
            arg_list[self.key_whole]["param"].append(star.v0.full_name)
        else:
            star_mean_rv = "{}".format(star.v0.value)
        if star.with_RVdrift:
            for order in range(1, star.RVdrift_order + 1):
                RVdrift_param_name = star.get_RVdrift_param_name(order)
                RVdrift_param_fullname = star.parameters[RVdrift_param_name].full_name
                if star.parameters[RVdrift_param_name].main:
                    value_not0 = True
                    if star.parameters[RVdrift_param_name].free:
                        star_mean_rv += "+ p[{}]".format(param_nb[self.key_whole])
                        param_nb[self.key_whole] += 1
                        arg_list[self.key_whole]["param"].append(RVdrift_param_fullname)
                    else:
                        if inst_model.parameters[RVdrift_param_name].value != 0.0:
                            star_mean_rv += "+ {}".format(inst_model.parameters[RVdrift_param_name].
                                                          value)
                        else:
                            value_not0 = False
                    if value_not0:
                        if "tref" not in arg_list[self.key_whole]["kwargs"]:
                            arg_list[self.key_whole]["kwargs"].append("tref")
                        if order == 1:
                            star_mean_rv += " * (t - tref) "
                        elif order > 1:
                            star_mean_rv += " * (t - tref)**{} ".format(order)

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
        # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
        # planets functions.
        template_preambule = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
        """
        template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet},"
                              " {P})")

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()
        if dataset is not None:
            ldict["t"] = dataset.get_time()
            ldict["tref"] = dataset.get_tref()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        whole_planets_rv = ""
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
                                         [planet.K, planet.secosw, planet.sesinw, planet.tc,
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
                                       sesinw=params_planet["sesinw"], P=params_planet["P"],
                                       tc=params_planet["tc"], tab=tab))
            preambule_whole += (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["sesinw"], P=params_whole["P"],
                                       tc=params_whole["tc"], tab=tab))

            # planets RV contribution (planet_rv and whole_planets_rv)
            planet_rv = template_planet_rv.format(planet=planet.name, K=params_planet["K"],
                                                  P=params_planet["P"])
            whole_planets_rv += template_planet_rv.format(planet=planet.name, K=params_whole["K"],
                                                          P=params_whole["P"])

            # Finalise the  text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 delta_inst_rv=delta_inst_rv, arguments=arguments,
                                                 star_mean_rv=star_mean_rv, planets_rv=planet_rv,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                delta_inst_rv=delta_inst_rv, arguments=arguments,
                                                star_mean_rv=star_mean_rv, tab=tab,
                                                planets_rv=whole_planets_rv))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["gettp_fast"] = gettp_fast
            ldict["pl_rv_array"] = pl_rv_array
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
        return dico_docf

    def _create_datasimulator_LC(self, inst_model, dataset=None):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each planet
        individually.

        :param Instrument_Model inst_model: instance of Instrument_Model
        :param Dataset dataset: instance of Dataset

        ----
        Returns:
            - A dictionary with DocFunctions containing the data simulator function for the whole
             system ("whole") and for the each planet individually ("planet_name")
        """
        # Get the star object.
        # star = self.stars[list(self.stars.keys())[0]]

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
        function_name = ("LCsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model.full_name))
        template_function = """
        def {function_name}({{arguments}}):
        {{tab}}{{preambule}}
        {{tab}}return 1 {{oot_var}}{{planets_lc}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Create the arguments text
        if dataset is None:
            arguments = "p, t, tref=None"
        else:
            arguments = "p"

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        if dataset is None:
            arg_list[self.key_whole]["kwargs"].append("t")

        # Create the text for oot_var
        oot_var = ""
        if inst_model.get_with_OOT_var():
            for order in range(inst_model.get_OOT_var_order() + 1):
                OOT_param_name = inst_model.get_OOT_param_name(order)
                OOT_param_fullname = inst_model.parameters[OOT_param_name].full_name
                if inst_model.parameters[OOT_param_name].main:
                    value_not0 = True
                    if inst_model.parameters[OOT_param_name].free:
                        oot_var += "+ p[{}]".format(param_nb[self.key_whole])
                        param_nb[self.key_whole] += 1
                        arg_list[self.key_whole]["param"].append(OOT_param_fullname)
                    else:
                        if inst_model.parameters[OOT_param_name].value != 0.0:
                            oot_var += "+ {}".format(inst_model.parameters[OOT_param_name].value)
                        else:
                            value_not0 = False
                    if value_not0 and order > 0:
                        if "tref" not in arg_list[self.key_whole]["kwargs"] and dataset is None:
                            arg_list[self.key_whole]["kwargs"].append("tref")
                        if order == 1:
                            oot_var += " * (t - tref) "
                        elif order > 1:
                            oot_var += " * (t - tref)**{} ".format(order)
                    elif value_not0 and order == 0:
                        oot_var += " "

        if self.parametrisation in self.LC_multis_parametrisations:
            # Get the star object.
            star = self.stars[list(self.stars.keys())[0]]
            if star.rho.free:
                rhostar = "p[{}]".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(star.rho.full_name)
            else:
                rhostar = "{}".format(star.rho.value)
        else:
            rhostar = None

        # Create the template preambule
        template_preambule_pl = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})"""
        if self.parametrisation in self.LC_multis_parametrisations:
            template_preambule_pl += """
            {tab}aR_{planet} = getaoverr({P}, {rhostar})"""
        if self.transit_model == "batman":
            template_preambule_pl += """
            {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
            {tab}inc_{planet} = degrees(acos({cosinc}))
            {tab}params_{planet}.t0 = {tc}
            {tab}params_{planet}.per = {P}
            {tab}params_{planet}.rp = {Rrat}
            {tab}params_{planet}.inc = inc_{planet}
            {tab}params_{planet}.ecc = ecc_{planet}
            {tab}params_{planet}.w = omega_{planet}
            {tab}params_{planet}.u = {ld_param_list}"""
            if dataset is None:
                template_preambule_pl += """
            {tab}params_{planet}.limb_dark = '{ld_mod_name}'"""
            if self.parametrisation in self.LC_multis_parametrisations:
                template_preambule_pl += """
            {tab}params_{planet}.a = aR_{planet}
            """
            else:
                template_preambule_pl += """
            {tab}params_{planet}.a = {aR}
            """
        else:
            template_preambule_pl += """
            {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
            {tab}inc_{planet} = acos({cosinc})
            """
        template_preambule_pl = dedent(template_preambule_pl)

        # Get the ld_parcont
        LD_parcont_name = self.ldmodel4instmodfname[inst_model.full_name]
        LD_parcont = self.LDs[LD_parcont_name]

        # Add the initialisation of the TransitModel to the template_preambule
        supersamp = self.get_supersamp(inst_model.full_name)
        if supersamp > 1:
            exptime = self.get_exptime(inst_model.full_name)
            if self.transit_model == "batman":
                if dataset is None:
                    template_preambule_pl += ("{{tab}}m_{{planet}} = TransitModel("
                                              "params_{{planet}}, t, "
                                              "supersample_factor={supersamp}, exp_time={exptime})"
                                              "\n".format(supersamp=supersamp, exptime=exptime))
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if self.transit_model == "batman":
                if dataset is None:
                    template_preambule_pl += ("{tab}m_{planet} = TransitModel(params_{planet}, t)"
                                              "\n")
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

        # Create the ld_param_list
        ld_param_list = "["
        for param in LD_parcont.get_list_params(main=True):
            if param.free:
                ld_param_list += "p[{}], ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(param.full_name)
            else:
                ld_param_list += "{}, ".format(param.value)
        ld_param_list += "]"

        # Create the text for template_planet_lc
        if self.transit_model == "batman":
            template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
        else:
            if self.parametrisation in self.LC_multis_parametrisations:
                template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, "
                                      "aR_{planet}, inc_{planet}, ecc_{planet}, omega_{planet}) "
                                      "- 1 ")
            else:
                template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, {aR}, "
                                      "inc_{planet}, ecc_{planet}, omega_{planet}) - 1 ")

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()
        if dataset is not None:
            ldict["t"] = dataset.get_time()
            ldict["tref"] = dataset.get_tref()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        whole_planets_lc = ""
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create the params_planet object
            if self.transit_model == "batman":
                par_bat = TransitParams()
                if dataset is not None:
                    par_bat.t0 = ldict["t"].mean()          # time of inferior conjunction
                    par_bat.per = 1.                        # orbital period
                    par_bat.rp = 0.1                        # planet radius(in stellar radii)
                    par_bat.a = 15.                         # semi-major axis(in stellar radii)
                    par_bat.inc = 87.                       # orbital inclination (in degrees)
                    par_bat.ecc = 0.                        # eccentricity
                    par_bat.w = 90.                         # longitude of periastron (in degrees)
                    par_bat.limb_dark = LD_parcont.ld_type  # limb darkening model
                    par_bat.u = LD_parcont.init_LD_values   # LDC init values
                    ldict["params_{planet}".format(planet=planet.name)] = par_bat
                    if supersamp > 1:
                        exptime = self.get_exptime(inst_model.full_name)
                        m_batman = TransitModel(ldict["params_{planet}".format(planet=planet.name)],
                                                ldict["t"], supersample_factor=supersamp,
                                                exp_time=exptime)
                    else:
                        m_batman = TransitModel(ldict["params_{planet}".format(planet=planet.name)],
                                                ldict["t"])
                    ldict["m_{planet}".format(planet=planet.name)] = m_batman
                else:
                    ldict["params_{planet}".format(planet=planet.name)] = par_bat

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            l_param_name = ["secosw", "sesinw", "cosinc", "tc", "P", "Rrat"]
            l_param = [planet.secosw, planet.sesinw, planet.cosinc, planet.tc, planet.P,
                       planet.Rrat]
            if self.parametrisation not in self.LC_multis_parametrisations:
                l_param_name.append("aR")
                l_param.append(planet.aR)
            else:
                params_planet["aR"] = ""
            for param_name, param in zip(l_param_name, l_param):
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
            # No need to make different cases for if batman or not or is dataset is None or not
            # because if one argument is not in the template, it is not used and this is it.
            preambule_planet = (template_preambule_pl.
                                format(planet=planet.name, secosw=params_planet["secosw"],
                                       sesinw=params_planet["sesinw"],
                                       tc=params_planet["tc"], rhostar=rhostar,
                                       cosinc=params_planet["cosinc"], P=params_planet["P"],
                                       Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                       ld_mod_name=LD_parcont.ld_type,
                                       ld_param_list=ld_param_list, tab=tab))
            preambule_whole += (template_preambule_pl.
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                       cosinc=params_whole["cosinc"], P=params_whole["P"],
                                       Rrat=params_whole["Rrat"], aR=params_planet["aR"],
                                       ld_mod_name=LD_parcont.ld_type, rhostar=rhostar,
                                       ld_param_list=ld_param_list, tab=tab))

            # planets LC contribution (planet_lc and whole_planets_lc)
            # No need for case if batman or if dataset is None. Same reason than above
            planet_lc = template_planet_lc.format(planet=planet.name,
                                                  aR=params_planet["aR"],
                                                  Rrat=params_planet["Rrat"],
                                                  tc=params_planet["tc"],
                                                  P=params_planet["P"],
                                                  ld_param_list=ld_param_list,
                                                  )
            whole_planets_lc += template_planet_lc.format(planet=planet.name,
                                                          aR=params_planet["aR"],
                                                          Rrat=params_whole["Rrat"],
                                                          tc=params_whole["tc"],
                                                          P=params_whole["P"],
                                                          ld_param_list=ld_param_list)

            # Finalise the  text of planet LC simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 oot_var=oot_var, arguments=arguments,
                                                 planets_lc=planet_lc, tab=tab))
            logger.debug("text of {object} LC simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Finalise the text of whole system LC simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                oot_var=oot_var, arguments=arguments,
                                                planets_lc=whole_planets_lc, tab=tab))
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["acos"] = acos
            if self.parametrisation in self.LC_multis_parametrisations:
                ldict["getaoverr"] = getaoverr
            if self.transit_model == "batman":
                if dataset is None:
                    ldict["TransitModel"] = TransitModel
                ldict["degrees"] = degrees
            else:
                ldict["m"] = m_pytransit
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
        # print(list(dico_docf.keys()))
        return dico_docf

    def _create_datasimulator_woinst_RV(self):
        """Return datasimulator functions without instrument impact.

        A datasimualtor function is created for the whole dataset_database and for each planet
         individually.

        ----
        Returns:
            Returns:
                - A dictionary with DocFunctions containing the data simulator function for the
                 whole system ("whole") and for the each planet individually ("planet_name")
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
        function_name = "RVsim_{{object}}_woinst"
        template_function = """
        def {function_name}(p, t):
        {{tab}}{{preambule}}
        {{tab}}return {{star_mean_rv}} {{planets_rv}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

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
        whole_planets_rv = ""
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
                                         [planet.K, planet.secosw, planet.sesinw, planet.tc,
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
                                       sesinw=params_planet["sesinw"], P=params_planet["P"],
                                       tc=params_planet["tc"], tab=tab))
            preambule_whole += (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["sesinw"], P=params_whole["P"],
                                       tc=params_whole["tc"], tab=tab))

            # planets RV contribution (planet_rv and whole_planets_rv)
            planet_rv = template_planet_rv.format(planet=planet.name, K=params_planet["K"],
                                                  P=params_planet["P"])
            whole_planets_rv += template_planet_rv.format(planet=planet.name, K=params_whole["K"],
                                                          P=params_whole["P"])

            # Finalise the  text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 star_mean_rv=star_mean_rv, planets_rv=planet_rv,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

            # Add time in the kwargs entry of the planet arg_list
            arg_list[planet.name]["kwargs"].append("t")

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                star_mean_rv=star_mean_rv, tab=tab,
                                                planets_rv=whole_planets_rv))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

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

    def _create_datasimulator_woinst_LC(self, LD_parcont, supersamp=1, exptime=0.02043402778):
        """Return datasimulator functions that doesn't include any instrument effect.

        A datasimualtor function is created for the whole dataset_database and for each planet
        individually.

        :param TBC LD_parcont: Limb darkening parameter container
        :param int supersamp: Supersampling for the model
        :param float exptime: Exposure time for the model

        ----
        Returns:
            - A dictionary with DocFunctions containing the data simulator function for the whole
             system ("whole") and for the each planet individually ("planet_name")
        """
        # Get the star object.
        # star = self.stars[list(self.stars.keys())[0]]

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
        function_name = "LCsim_{{object}}_woinst"
        template_function = """
        def {function_name}(p, t):
        {{tab}}{{preambule}}
        {{tab}}return 1 {{planets_lc}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Create the template preambule
        if self.transit_model == "batman":
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
            {tab}inc_{planet} = degrees(acos({cosinc}))
            {tab}params_{planet}.t0 = {tc}
            {tab}params_{planet}.per = {P}
            {tab}params_{planet}.rp = {Rrat}
            {tab}params_{planet}.a = {aR}
            {tab}params_{planet}.inc = inc_{planet}
            {tab}params_{planet}.ecc = ecc_{planet}
            {tab}params_{planet}.w = omega_{planet}
            {tab}params_{planet}.limb_dark = '{ld_mod_name}'
            {tab}params_{planet}.u = {ld_param_list}
            """
        else:
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
            {tab}inc_{planet} = acos({cosinc})
            """
        template_preambule = dedent(template_preambule)

        # Add the initialisation of the TransitModel to the template
        if supersamp > 1:
            if self.transit_model == "batman":
                template_preambule += ("{{tab}}m_{{planet}} = TransitModel(params_{{planet}}, t, "
                                       "supersample_factor={supersamp}, exp_time={exptime})\n"
                                       "".format(supersamp=supersamp, exptime=exptime))
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if self.transit_model == "batman":
                template_preambule += ("{tab}m_{planet} = TransitModel(params_{planet}, t)\n")
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

        # Create the ld_param_list
        ld_param_list = "["
        for param in LD_parcont.get_list_params(main=True):
            if param.free:
                ld_param_list += "p[{}], ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(param.full_name)
            else:
                ld_param_list += "{}, ".format(param.value)
        ld_param_list += "]"

        # Create the text for template_planet_lc
        if self.transit_model == "batman":
            template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
        else:
            template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, {aR}, "
                                  "inc_{planet}, ecc_{planet}, omega_{planet}) - 1 ")

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        whole_planets_lc = ""
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create the params_planet object
            ldict["params_{planet}".format(planet=planet.name)] = TransitParams()

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            for param_name, param in zip(["secosw", "sesinw", "cosinc", "tc", "P", "Rrat", "aR"],
                                         [planet.secosw, planet.sesinw, planet.cosinc, planet.tc,
                                          planet.P, planet.Rrat, planet.aR]):
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
            if self.transit_model == "batman":
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"], tc=params_planet["tc"],
                                           cosinc=params_planet["cosinc"], P=params_planet["P"],
                                           Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                           cosinc=params_whole["cosinc"], P=params_whole["P"],
                                           Rrat=params_whole["Rrat"], aR=params_whole["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
            else:
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"],
                                           cosinc=params_planet["cosinc"], tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"],
                                           cosinc=params_whole["cosinc"], tab=tab))

            # planets LC contribution (planet_lc and whole_planets_lc)
            if self.transit_model == "batman":
                planet_lc = template_planet_lc.format(planet=planet.name)
                whole_planets_lc += template_planet_lc.format(planet=planet.name)
            else:
                planet_lc = template_planet_lc.format(planet=planet.name, aR=params_planet["aR"],
                                                      Rrat=params_planet["Rrat"],
                                                      tc=params_planet["tc"], P=params_planet["P"],
                                                      ld_param_list=ld_param_list)
                whole_planets_lc += template_planet_lc.format(planet=planet.name,
                                                              aR=params_whole["aR"],
                                                              Rrat=params_whole["Rrat"],
                                                              tc=params_whole["tc"],
                                                              P=params_whole["P"],
                                                              ld_param_list=ld_param_list)

            # Finalise the  text of planet LC simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 planets_lc=planet_lc, tab=tab))
            logger.debug("text of {object} LC simulator function wo inst:\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

            # Add time in the kwargs entry of the planet arg_list
            arg_list[planet.name]["kwargs"].append("t")

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                planets_lc=whole_planets_lc, tab=tab))
        logger.debug("text of {object} LC simulator function wo inst:\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["acos"] = acos
            ldict["degrees"] = degrees
            if self.transit_model == "batman":
                ldict["TransitModel"] = TransitModel
            else:
                ldict["m"] = m_pytransit
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
