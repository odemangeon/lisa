#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator LC module.
"""
from logging import getLogger
from textwrap import dedent
from collections import OrderedDict
from copy import deepcopy
from math import acos, degrees

from batman import TransitModel, TransitParams
from pytransit import MandelAgol

# from ..dataset_and_instrument.lc import LC_inst_cat
from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.model.datasimulator import check_datasets_and_instmodels
# from ...core.dataset_and_instrument.instrument import Instrument_Model
# from ...core.dataset_and_instrument.dataset import Dataset
from ....tools.convert import getecc_fast, getomega_fast, getaoverr


## Logger object
logger = getLogger()


def create_datasimulator_LC(star, planets, key_whole, key_param, key_kwargs,
                            parametrisation,
                            LC_multis_parametrisations, ldmodel4instmodfname, LDs,
                            transit_model, SSE4instmodfname,
                            inst_models=None, datasets=None):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    :param Star star: Star object
    :param dict_of_Planet planets: dictionary: key: planet name, value: Planet object
    :param string key_whole: key to use to identify the whole system in the output dictionary
        (dico_docf).
    :param string key_param: Key used for the parameters entry of arg_list
    :param string key_kwargs: Key used for the keyword argument entry of arg_list
    :param string parametrisation: String refering to the parametrisation to use
    :param list_of_string LC_multis_parametrisations: List of string giving the parametrisation that
        specially made for multi-planetary systems.
    :param dict_of_ ldmodel4instmodfname: Dictionary giving Limd darkening model to use for each
        instrument model
    :param LDs: LD object?
    :param string transit_model: String refering to the transit model to be used.
    :param dict_of_ SSE4instmodfname: Dictionary giving the supersampling factor and the exposure
        time to use for each instrument model
    :param Instrument_Model inst_model: instance of Instrument_Model
    :param Dataset dataset: instance of Dataset

    :return dict_of_DatasimDocFunc dico_docf: A dictionary with DocFunctions containing the data
        simulator function for the whole system ("whole") and for the each planet individually
        ("planet_name")
    """
    # Check the content of inst_models argument. Set multi_inst_model to True if several inst models
    # are provided, to False otherwise. Finally set the inst_model_fullnames argument for the
    # Datasim_DocFunc (instmod_docf)
    # Check the content of datasets argument: Set multi_dataset to True if several datasets
    # are provided, to False otherwise. Finally set the datasets argument for the
    # Datasim_DocFunc (dtsts_docf)
    # Set the list of instrument categories for the Datasim_DocFunc (instcat_docf)
    # Produce the list of datasets and list of models (even of 1 element)
    # Set multi indicating if multiple outputs are required for the datasimulator
    # Set the inst_model_full_name for the name of the function and the inst_cat input
    # (instcat_docf) for the datasim_docfunc
    (l_dataset, l_inst_model, multi, inst_model_full_name, instcat_docf, instmod_docf,
     dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

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
    #   - key_param: list of the free parameters name in order
    #   - key_kwargs: list of the additional argument taht you need to provide to simulate the
    #               data. For example the time
    arg_list = {}

    # Initialise the template function text
    function_name = ("LCsim_{{object}}_{instmod_fullname}"
                     "".format(instmod_fullname=inst_model_full_name))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule}}
    {{tab}}return {{returns}}
    """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Initialise the template for each instmodel
    template_returns_instmod = "1 {oot_var}{planets_lc}"

    # Create the arguments text
    if multi:
        if datasets[0] is None:
            arguments = "p, l_t, l_tref=None"
        else:
            arguments = "p"
    else:
        if datasets is None:
            arguments = "p, t, tref=None"
        else:
            arguments = "p"

    # Initialise arg_list and param_nb for key "whole"
    arg_list[key_whole] = OrderedDict()
    arg_list[key_whole][key_param] = []
    arg_list[key_whole][key_kwargs] = []
    param_nb[key_whole] = 0

    # Add time in the kwargs entry of the whole system arg_list
    if datasets is None:
        if multi:
            arg_list[key_whole][key_kwargs].append("l_t")
        else:
            arg_list[key_whole][key_kwargs].append("t")

    l_oot_var = get_ootvar(l_inst_model, l_dataset, multi,
                           param_nb, key_whole, arg_list, key_param, key_kwargs)

    if parametrisation in LC_multis_parametrisations:
        # Get the star object.
        if star.rho.free:
            rhostar = "p[{}]".format(param_nb[key_whole])
            param_nb[key_whole] += 1
            arg_list[key_whole][key_param].append(star.rho.full_name)
        else:
            rhostar = "{}".format(star.rho.value)
    else:
        rhostar = None

    # Get the ld_parcont and ld_param_list
    l_LD_parcont_name = []
    l_LD_parcont = []
    l_ld_param_list = []
    for ii, instmdl in enumerate(l_inst_model):
        l_LD_parcont_name.append(ldmodel4instmodfname[instmdl.full_name])
        l_LD_parcont.append(LDs[l_LD_parcont_name[ii]])
        l_ld_param_list.append("[")
        for param in l_LD_parcont[ii].get_list_params(main=True):
            if param.free:
                l_ld_param_list[ii] += "p[{}], ".format(param_nb[key_whole])
                param_nb[key_whole] += 1
                arg_list[key_whole][key_param].append(param.full_name)
            else:
                l_ld_param_list[ii] += "{}, ".format(param.value)
        l_ld_param_list[ii] += "]"

    # Create the preambule
    template_preambule_pl = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})"""
    if parametrisation in LC_multis_parametrisations:
        template_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar})"""

    if transit_model == "batman":
        template_preambule_pl += """
        {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
        {tab}inc_{planet} = degrees(acos({cosinc}))"""

        for instmdl, dst, LD_parcont, ld_param_list in zip(l_inst_model, l_dataset, l_LD_parcont,
                                                           l_ld_param_list):
            # If the same model is used for several dataset a model will be several times in
            # l_inst_model. So to avoid the repetition we check if this instrument has already been
            # done.
            if multi:
                template_batman_pl = """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.t0 = {{tc}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.per = {{P}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.rp = {{Rrat}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.inc = inc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.ecc = ecc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.w = omega_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.u = {ld_param_list}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.limb_dark = '{ld_mod_name}'"""
                template_batman_pl = (template_batman_pl.
                                      format(instmod_fullname=instmdl.full_name,
                                             dst_key=dst.number,
                                             ld_mod_name=LD_parcont.ld_type,
                                             ld_param_list=ld_param_list))
            else:
                template_batman_pl = """
        {{tab}}params_{{planet}}.t0 = {{tc}}
        {{tab}}params_{{planet}}.per = {{P}}
        {{tab}}params_{{planet}}.rp = {{Rrat}}
        {{tab}}params_{{planet}}.inc = inc_{{planet}}
        {{tab}}params_{{planet}}.ecc = ecc_{{planet}}
        {{tab}}params_{{planet}}.w = omega_{{planet}}
        {{tab}}params_{{planet}}.u = {ld_param_list}
        {{tab}}params_{{planet}}.limb_dark = '{ld_mod_name}'"""
                template_batman_pl = template_batman_pl.format(ld_mod_name=LD_parcont.ld_type,
                                                               ld_param_list=ld_param_list)
            template_preambule_pl += template_batman_pl

            if parametrisation in LC_multis_parametrisations:
                if multi:
                    template_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = aR_{{planet}}
        """.format(instmod_fullname=instmdl.full_name, dst_key=dst.number)
                else:
                    template_preambule_pl += """
        {tab}params_{planet}.a = aR_{planet}
        """
            else:
                if multi:
                    template_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = {{aR}}
        """.format(instmod_fullname=instmdl.full_name, dst_key=dst.number)
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

    # Initialise the local dictionary for the creation of the datasim functions by exec
    # ldict = locals().copy()  # TODO: think if there is a way to put that in a function common to
    # all datasimulator because it's more or less repeated in my 3 datasimulators for now
    ldict = {}
    # if datasets are provided add the time array and tref to the local dictionary
    if datasets is not None:
        if multi:
            l_t = []
            l_tref = []
            for dst in zip(l_dataset):
                l_t.append(dst.get_time())
                l_tref.append(dst.get_tref())
            ldict["l_t"] = l_t
            ldict["l_tref"] = l_tref
        else:
            ldict["t"] = datasets.get_time()
            ldict["tref"] = datasets.get_tref()

    # Add the initialisation of the TransitModel (to the template_preambule)
    l_par_bat = []
    for ii, instmdl, dst, LD_parcont in zip(range(len(l_inst_model)), l_inst_model, l_dataset,
                                            l_LD_parcont):
        supersamp = SSE4instmodfname.get_supersamp(instmdl.full_name)
        if supersamp > 1:
            exptime = SSE4instmodfname.get_exptime(instmdl.full_name)
            if transit_model == "batman":
                if dst is None:
                    if multi:
                        template_batman_pl_4 = ("{{tab}}m_{{planet}}_{instmod_fullname}_"
                                                "dataset{dst_key} = TransitModel("
                                                "params_{{planet}}_{instmod_fullname}, "
                                                "l_t[{ii}], "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime,
                                                            ii=ii,
                                                            instmod_fullname=instmdl.full_name,
                                                            dst_key=dst.number))
                    else:
                        template_batman_pl_4 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}, t, "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime))
                    template_preambule_pl += template_batman_pl_4
                    l_par_bat.append({})
                    for planet in planets.values():
                        l_par_bat[ii][planet.name] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        l_par_bat[ii][planet.name] = TransitParams()
                        if multi:  # time of inf. conjunction
                            l_par_bat[ii][planet.name].t0 = ldict["l_t"][ii].mean()
                        else:
                            l_par_bat[ii][planet.name].t0 = ldict["t"][ii].mean()
                        l_par_bat[ii][planet.name].per = 1.   # orbital period
                        l_par_bat[ii][planet.name].rp = 0.1   # planet radius(in stel radii)
                        l_par_bat[ii][planet.name].a = 15.    # semi-major axis(in stel radii)
                        l_par_bat[ii][planet.name].inc = 87.  # orbital inclination (in degrees)
                        l_par_bat[ii][planet.name].ecc = 0.   # eccentricity
                        l_par_bat[ii][planet.name].w = 90.    # long. of periastron (in deg.)
                        l_par_bat[ii][planet.name].limb_dark = LD_parcont.ld_type  # LD model
                        l_par_bat[ii][planet.name].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if transit_model == "batman":
                if dst is None:
                    if multi:
                        template_batman_pl_5 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}, l_tp[{ii}])"
                                                "\n".format(ii=ii))
                        template_preambule_pl += template_batman_pl_5
                    else:
                        template_preambule_pl += ("{tab}m_{planet} = TransitModel("
                                                  "params_{planet}, t)\n")
                    l_par_bat.append({})
                    for planet in planets.values():
                        l_par_bat[ii][planet.name] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        l_par_bat[ii][planet.name] = TransitParams()
                        if multi:  # time of inf. conjunction
                            l_par_bat[ii][planet.name].t0 = ldict["l_t"][ii].mean()
                        else:
                            l_par_bat[ii][planet.name].t0 = ldict["t"][ii].mean()
                        l_par_bat[ii][planet.name].per = 1.   # orbital period
                        l_par_bat[ii][planet.name].rp = 0.1   # planet radius(in stel radii)
                        l_par_bat[ii][planet.name].a = 15.    # semi-major axis(in stel radii)
                        l_par_bat[ii][planet.name].inc = 87.  # orbital inclination (in degrees)
                        l_par_bat[ii][planet.name].ecc = 0.   # eccentricity
                        l_par_bat[ii][planet.name].w = 90.    # long. of periastron (in deg.)
                        l_par_bat[ii][planet.name].limb_dark = LD_parcont.ld_type  # LD model
                        l_par_bat[ii][planet.name].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

    # Create the text for template_planet_lc
    if transit_model == "batman":
        if multi:
            template_planet_lc = ("+ m_{planet}_{instmod_fullname}_dataset{dst_key}.light_curve("
                                  "params_{planet}_{instmod_fullname}_dataset{dst_key}) - 1 ")
        else:
            template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
    else:
        if parametrisation in LC_multis_parametrisations:
            if multi:
                template_planet_lc = ("+ m.evaluate(l_t[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tc}, {P}, aR_{planet}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, "
                                      "aR_{planet}, inc_{planet}, ecc_{planet}, "
                                      "omega_{planet}) - 1 ")
        else:
            if multi:
                template_planet_lc = ("+ m.evaluate(l_t[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tc}, {P}, {aR}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, "
                                      "{P}, {aR}, inc_{planet}, ecc_{planet}, "
                                      "omega_{planet}) - 1 ")

    # Save the param_nb and arg_list for the whole function before iterating over the planets
    # text_def_func_before = text_def_func[key_whole]
    param_nb_before = param_nb[key_whole]
    arg_list_before = deepcopy(arg_list[key_whole])

    # Initialise the text for the whole system preambule
    preambule_whole = ""
    l_whole_planets_lc = []
    for instmdl in l_inst_model:
        l_whole_planets_lc.append("")
    for jj, planet in enumerate(planets.values()):
        # Initialise arg_list and param_nb for the current planet
        arg_list[planet.name] = deepcopy(arg_list_before)
        param_nb[planet.name] = param_nb_before

        # Create the params_planet object
        if transit_model == "batman":
            for ii, instmdl, dst, par_bat in zip(range(len(l_inst_model)), l_inst_model,
                                                 l_dataset, l_par_bat):
                if dst is not None:
                    if multi:
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.name,
                                                    instmod_fullname=instmdl.full_name,
                                                    dst_key=dst.number))
                        tt = ldict["l_t"][ii]
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.name)
                        tt = ldict["t"]
                    ldict[params_pl_inst] = par_bat[planet.name]
                    supersamp = SSE4instmodfname.get_supersamp(instmdl.full_name)
                    if supersamp > 1:
                        exptime = SSE4instmodfname.get_exptime(instmdl.full_name)
                        m_batman = TransitModel(ldict[params_pl_inst],
                                                tt, supersample_factor=supersamp,
                                                exp_time=exptime)
                    else:
                        m_batman = TransitModel(ldict[params_pl_inst], tt)
                    if multi:
                        m_pl_inst = ("m_{planet}_{instmod_fullname}_dataset{dst_key}"
                                     "".format(planet=planet.name,
                                               instmod_fullname=instmdl.full_name,
                                               dst_key=dst.number))

                    else:
                        m_pl_inst = "m_{planet}".format(planet=planet.name)
                    ldict[m_pl_inst] = m_batman
                else:
                    if multi:
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.name,
                                                    instmod_fullname=instmdl.full_name,
                                                    dst_key=dst.number))
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.name)
                    ldict[params_pl_inst] = par_bat[planet.name]

        # Create two dictionaries which will contain the text for each planet parameter for the
        # current planet and for the whole system.
        params_planet = {}
        params_whole = {}
        # Create the text for each planet parameter for the current planet and for the whole
        # system.
        l_param_name = ["secosw", "sesinw", "cosinc", "tc", "P", "Rrat"]
        l_param = [planet.secosw, planet.sesinw, planet.cosinc, planet.tc, planet.P,
                   planet.Rrat]
        if parametrisation not in LC_multis_parametrisations:
            l_param_name.append("aR")
            l_param.append(planet.aR)
        else:
            params_planet["aR"] = ""
        for param_name, param in zip(l_param_name, l_param):
            if param.free:
                param_text = "p[{}]"
                params_whole[param_name] = param_text.format(param_nb[key_whole])
                param_nb[key_whole] += 1
                arg_list[key_whole][key_param].append(param.full_name)
                params_planet[param_name] = param_text.format(param_nb[planet.name])
                param_nb[planet.name] += 1
                arg_list[planet.name][key_param].append(param.full_name)
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
                                   # ld_mod_name=LD_parcont.ld_type,
                                   # ld_param_list=ld_param_list,
                                   tab=tab))
        preambule_whole += (template_preambule_pl.
                            format(planet=planet.name, secosw=params_whole["secosw"],
                                   sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                   cosinc=params_whole["cosinc"], P=params_whole["P"],
                                   Rrat=params_whole["Rrat"], aR=params_planet["aR"],
                                   # ld_mod_name=LD_parcont.ld_type,
                                   rhostar=rhostar,
                                   # ld_param_list=ld_param_list,
                                   tab=tab))

        # planets LC contribution (planet_lc and whole_planets_lc)
        # No need for case if batman or if dataset is None. Same reason than above
        l_planet_lc = []
        for ii, instmdl, dst, ld_param_list in zip(range(len(l_inst_model)), l_inst_model,
                                                   l_dataset, l_ld_param_list):
            if instmdl is None:
                instmdl_fname = None
            else:
                instmdl_fname = instmdl.full_name
            if dst is None:
                dst_nb = None
            else:
                dst_nb = dst.number
            l_planet_lc.append(template_planet_lc.format(planet=planet.name,
                                                         instmod_fullname=instmdl_fname,
                                                         dst_key=dst_nb,
                                                         aR=params_planet["aR"],
                                                         Rrat=params_planet["Rrat"],
                                                         tc=params_planet["tc"],
                                                         P=params_planet["P"],
                                                         ld_param_list=ld_param_list,
                                                         ii=ii
                                                         ))
            l_whole_planets_lc[ii] += template_planet_lc.format(planet=planet.name,
                                                                instmod_fullname=instmdl_fname,
                                                                dst_key=dst_nb,
                                                                aR=params_planet["aR"],
                                                                Rrat=params_whole["Rrat"],
                                                                tc=params_whole["tc"],
                                                                P=params_whole["P"],
                                                                ld_param_list=ld_param_list,
                                                                ii=ii
                                                                )

        # Fill returns text for each planet
        returns_pl = ""
        for oot_var, planet_lc in zip(l_oot_var, l_planet_lc):
            returns_pl += template_returns_instmod.format(oot_var=oot_var,
                                                          planets_lc=planet_lc)
            returns_pl += ", "
        returns_pl = returns_pl[:-2]

        # Finalise the  text of planet LC simulator function
        text_def_func[planet.name] = (template_function.
                                      format(object=planet.name, preambule=preambule_planet,
                                             arguments=arguments, returns=returns_pl, tab=tab))
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=planet.name, text_func=text_def_func[planet.name]))

    # Fill returns text for the whole system
    returns_whole = ""
    for oot_var, whole_planet_lc in zip(l_oot_var, l_whole_planets_lc):
        returns_whole += template_returns_instmod.format(oot_var=oot_var,
                                                         planets_lc=whole_planet_lc)
        returns_whole += ", "
    returns_whole = returns_whole[:-2]

    # Finalise the text of whole system LC simulator function
    text_def_func[key_whole] = (template_function.
                                format(object=key_whole, preambule=preambule_whole,
                                       arguments=arguments, returns=returns_whole,
                                       tab=tab))
    logger.debug("text of {object} LC simulator function :\n{text_func}"
                 "".format(object=key_whole, text_func=text_def_func[key_whole]))

    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict["getecc_fast"] = getecc_fast
        ldict["getomega_fast"] = getomega_fast
        ldict["acos"] = acos
        if parametrisation in LC_multis_parametrisations:
            ldict["getaoverr"] = getaoverr
        if transit_model == "batman":
            if datasets is None:
                ldict["TransitModel"] = TransitModel
            ldict["degrees"] = degrees
        else:
            ldict["m"] = m_pytransit
        exec(text_def_func[obj_key], ldict)
        params_model = arg_list[obj_key][key_param]
        if len(arg_list[obj_key][key_kwargs]) > 0:
            dataset_kwargs = str(arg_list[obj_key][key_kwargs])
        else:
            dataset_kwargs = None
        dico_docf[obj_key] = DatasimDocFunc(function=ldict[function_name.format(object=obj_key)],
                                            params_model=params_model,
                                            inst_cat=instcat_docf,
                                            dataset_kwargs=dataset_kwargs,
                                            inst_model_fullname=instmod_docf,
                                            dataset=dtsts_docf)
    return dico_docf


def get_ootvar(l_inst_model, l_dataset, multi,
               param_nb, key_whole, arg_list, key_param, key_kwargs):
    """Get the out of transit variation contribution to the light-curve

    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s).
    :param list_of_Dataset l_inst_model: Checked list of Instrument_Model instance(s).
    :param bool multi: True if the datasim function needs multiple outputs.
    :param dict_of_int param_nb: dictionary with key = key_whole, value = current number of free
        parameters in the model
    :param string key_whole: Key used for the whole system
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
    :param string key_param: Key used for the parameters entry of arg_list
    :param string key_kwargs: Key used for the keyword argument entry of arg_list
    :return list_of_string l_oot_var: list give the string representation of the contributions
        of the out of transit variation for each couple instrument model - dataset in
        l_inst_model and l_dataset.
    """
    # Create the text for oot_var
    l_oot_var = []
    # For each instrument model and dataset, ...
    for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
        l_oot_var.append("")
        # ..., if out of transit variation has been asked, ...
        if instmdl.get_with_OOT_var():
            # ..., For each order in the required polynomial model, ...
            for order in range(instmdl.get_OOT_var_order() + 1):
                # ..., get the name and full name of the parameter for this order
                OOT_param_name = instmdl.get_OOT_param_name(order)
                OOT_param_fullname = instmdl.parameters[OOT_param_name].full_name
                # ..., If this parameter is a main parameter (it should be), ...
                if instmdl.parameters[OOT_param_name].main:
                    value_not0 = True
                    # ..., If this parameter is free, ...
                    if instmdl.parameters[OOT_param_name].free:
                        # ..., add the beginning of this order's contribution to the text of the
                        # out of transit variation, add the parameter name to the list of
                        # parameter, and increment the parameter counter
                        l_oot_var[ii] += "+ p[{}]".format(param_nb[key_whole])
                        param_nb[key_whole] += 1
                        arg_list[key_whole][key_param].append(OOT_param_fullname)
                    # ..., else, ...
                    else:
                        # ..., if the fixed value of this parameter is not zero, ...
                        if instmdl.parameters[OOT_param_name].value != 0.0:
                            # ..., add the beginning of this order's contribution to the text of the
                            # out of transit variation
                            l_oot_var[ii] += "+ {}".format(instmdl.parameters[OOT_param_name].
                                                           value)
                        # ..., else, since the fixed value is zero, this order doesn't have any
                        # contribution
                        else:
                            value_not0 = False
                    # ..., if the order has a contribution to the out of transit variation and
                    # the considered order is more than 0 meaning the time plays a role, ...
                    if value_not0 and order > 0:
                        # ..., if neither "tref" nor "l_tref" are in the list of kwargs and
                        # no dataset is provided, ...
                        if ((("tref" not in arg_list[key_whole][key_kwargs]) and
                             ("l_tref" not in arg_list[key_whole][key_kwargs])) and
                           (dst is None)):
                            # ..., add "tref" or "l_tref" to the list of kwargs.
                            if multi:
                                arg_list[key_whole][key_kwargs].append("l_tref")
                            else:
                                arg_list[key_whole][key_kwargs].append("tref")
                        # ..., add the end of this order's contribution to the text of the out of
                        # transit variation, ...
                        if order == 1:
                            if multi:
                                l_oot_var[ii] += (" * (l_t[{ii}] - l_tref[{ii}]) "
                                                  "".format(ii=ii))
                            else:
                                l_oot_var[ii] += " * (t - tref) "
                        elif order > 1:
                            if multi:
                                l_oot_var[ii] += (" * (l_t[{ii}] - l_tref[{ii}])**{order} "
                                                  "".format(order=order, ii=ii))
                            else:
                                l_oot_var[ii] += " * (t - tref)**{} ".format(order)
                    # If the is no contribution to the oot of transit variation from this order
                    # add only a space.
                    elif value_not0 and order == 0:
                        l_oot_var[ii] += " "
    return l_oot_var
