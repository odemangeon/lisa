#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator LC module.
"""
from logging import getLogger
from textwrap import dedent
from copy import deepcopy
from math import acos, degrees, sqrt

from batman import TransitModel, TransitParams
# from pytransit import MandelAgol

from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.model.datasimulator_toolbox import check_datasets_and_instmodels, get_has_datasets
from ...core.model.datasimulator_timeseries_toolbox import (add_time_argument, time_vec,
                                                            l_time_vec, add_timeref_arguments,
                                                            time_ref, l_time_ref)
from ....tools.function_from_text_toolbox import (init_arglist_paramnb_arguments_ldict, add_param_argument,
                                                  par_vec_name, add_argskwargs_argument, argskwargs)
from ....posterior.exoplanet.model.convert import getaoverr, getomega_fast, getomega_deg_fast


## Logger object
logger = getLogger()


def create_datasimulator_LC(star, planets, key_whole, key_param, key_mand_kwargs, key_opt_kwargs, ext_plonly,
                            parametrisation, ldmodel4instmodfname, LDs, transit_model, SSE4instmodfname,
                            inst_models=None, datasets=None,
                            param_vector_name=par_vec_name):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    :param Star star: Star object
    :param dict_of_Planet planets: dictionary: key: planet name, value: Planet object
    :param string key_whole: key to use to identify the whole system in the output dictionary
        (dico_docf).
    :param string key_param: Key used for the parameters entry of arg_list
    :param str key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param str key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param str ext_plonly: extension to the planet name used for planet only model (without star, nor instrument)
    :param string parametrisation: String refering to the parametrisation to use
    :param dict_of_ ldmodel4instmodfname: Dictionary giving Limd darkening model to use for each
        instrument model
    :param LDs: LD object?
    :param string transit_model: String refering to the transit model to be used.
    :param dict_of_ SSE4instmodfname: Dictionary giving the supersampling factor and the exposure
        time to use for each instrument model
    :param Instrument_Model inst_model: instance of Instrument_Model
    :param Dataset/list_of_Dataset/None datasets:
        If Dataset, the datasimulator include the kwargs of the dataset, so provided parameters
            of for the model, it simulates the data in the dataset.
        If None, the datasimulator function requires the time (and eventually the t_ref) on top
            of the parameters of the model.
        If list of Dataset, it has to provide exactly one dataset (no None) for each Instrument
            model in inst_models and the produced datasimulator will include the kwargs of the
            datasets.
    :param str param_vector_name: str giving the name of the vector of parameters argument of the
        datasimulator function.

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

    # Check if datasets are provided
    has_dataset = get_has_datasets(l_dataset)

    # text_def_func is a dictionary which will received the text of the datasimulator functions
    # It has several keys for several datasimulator functions:
    #   - "whole" for the whole system with all the planets
    #   - "b", "c", ... ("planet name") for only the contribution of one planet.
    text_def_func = {}

    ## Initialise param_nb and arg_list
    # param_nb is a dictionary that will keep track of the number of parameter for each
    # function in text_def_func (so the keys are the same).
    # arg_list is a dictionary which will receive the argument list of the datasimulator
    # function in text_def_func (so the keys are the same).
    # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
    # keys:
    #   - "param": list of the free parameters name in order
    #   - "kwargs": list of the additional argument taht you need to provide to simulate the
    #               data. For example the time]
    # Create the "arguments" text variable and intial with the parameter vector
    # Create and intialise the "ldict" dictionary variable which will be used as local dictionary
    # for the creation of the datasim functions with exec
    (param_nb,
     arg_list,
     arguments,
     ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, keys=[key_whole], key_mand_kwargs=key_mand_kwargs,
                                                   key_opt_kwargs=key_opt_kwargs, param_vector_name=par_vec_name)

    # Add rhostar to arg_list if required by the parametrisation
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    if parametrisation == "Multis":
        rhostar = add_param_argument(param=star.rho, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                     key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]
    else:
        rhostar = None

    # Get the ld_parcont and ld_param_list
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    (l_LD_parcont_name,
     l_LD_parcont,
     l_ld_param_list) = get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, LDs, param_nb,
                                                 arg_list, key_whole, key_param)

    # Initialise arg_list and param_nb for the current planet only contribution
    for i, planet in enumerate(planets.values()):
        arg_list[planet.get_name() + ext_plonly] = deepcopy(arg_list[key_whole])
        param_nb[planet.get_name() + ext_plonly] = param_nb[key_whole]

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

    # Initialise the template for planetary contibution only (No instrument nor star) for phase fold plots per planet
    template_returns_pl_only = "{planets_lc}"

    # Add the time as additional argument: TODO: time_arg_name is a new return and is not used in
    # the rest of the function. Check if it can be used.
    (arguments, time_arg_name, time_arg
     ) = add_time_argument(arguments=arguments, multi=multi, has_dataset=has_dataset, arg_list=arg_list,
                           key_arglist=key_whole, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                           ldict=ldict, l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                           add_to_ldict=True, backup_add_to_args=True)

    # Get the out of transit variation contribution for each couple instrument - dataset
    l_oot_var, arguments = get_ootvar(l_inst_model, l_dataset, multi,
                                      ldict, arguments, param_nb, arg_list, key_whole,
                                      key_param, key_mand_kwargs, key_opt_kwargs,
                                      time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                      timeref_name=time_ref, l_timeref_name=l_time_ref)

    # Create the preambule
    template_preambule_pl = """
        {tab}ecc_{planet} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})"""
    if parametrisation == "Multis":
        template_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar})"""

    if transit_model == "batman":
        template_preambule_pl += """
        {tab}omega_{planet} = getomega_deg_fast({esinw}, {ecosw})
        {tab}inc_{planet} = degrees(acos({cosinc}))"""

        for instmdl, dst, LD_parcont, ld_param_list in zip(l_inst_model, l_dataset, l_LD_parcont,
                                                           l_ld_param_list):
            # If the same model is used for several dataset a model will be several times in
            # l_inst_model. So to avoid the repetition we check if this instrument has already been
            # done.
            if multi:
                template_batman_pl = """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.t0 = {{tic}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.per = {{P}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.rp = {{Rrat}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.inc = inc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.ecc = ecc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.w = omega_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.u = {ld_param_list}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.limb_dark = '{ld_mod_name}'"""
                template_batman_pl = (template_batman_pl.
                                      format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                             dst_key=dst.number,
                                             ld_mod_name=LD_parcont.ld_type,
                                             ld_param_list=ld_param_list))
            else:
                template_batman_pl = """
        {{tab}}params_{{planet}}.t0 = {{tic}}
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

            if parametrisation == "Multis":
                if multi:
                    template_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = aR_{{planet}}
        """.format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True), dst_key=dst.number)
                else:
                    template_preambule_pl += """
        {tab}params_{planet}.a = aR_{planet}
        """
            else:
                if multi:
                    template_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = {{aR}}
        """.format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True), dst_key=dst.number)
                else:
                    template_preambule_pl += """
        {tab}params_{planet}.a = {aR}
        """
    else:
        template_preambule_pl += """
        {tab}omega_{planet} = getomega_fast({esinw}, {ecosw})
        {tab}inc_{planet} = acos({cosinc})
        """
    template_preambule_pl = dedent(template_preambule_pl)

    # Add the initialisation of the TransitModel (to the template_preambule)
    l_par_bat = []
    for ii, instmdl, dst, LD_parcont in zip(range(len(l_inst_model)), l_inst_model, l_dataset,
                                            l_LD_parcont):
        supersamp = SSE4instmodfname.get_supersamp(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
        if supersamp > 1:
            exptime = SSE4instmodfname.get_exptime(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
            if transit_model == "batman":
                if dst is None:
                    if multi:
                        template_batman_pl_4 = ("{{tab}}m_{{planet}}_{instmod_fullname}_"
                                                "dataset{dst_key} = TransitModel("
                                                "params_{{planet}}_{instmod_fullname}, "
                                                "{{ltime_vec}}[{ii}], "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime,
                                                            ii=ii,
                                                            instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                            dst_key=dst.number))
                    else:
                        template_batman_pl_4 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}, {{time_vec}}, "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime))
                    template_preambule_pl += template_batman_pl_4
                    l_par_bat.append({})
                    for planet in planets.values():
                        for add_plonlyext in [True, False]:
                            if add_plonlyext:
                                pl_key = planet.get_name() + ext_plonly
                            else:
                                pl_key = planet.get_name()
                            l_par_bat[ii][pl_key] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        for add_plonlyext in [True, False]:
                            if add_plonlyext:
                                pl_key = planet.get_name() + ext_plonly
                            else:
                                pl_key = planet.get_name()
                            l_par_bat[ii][pl_key] = TransitParams()
                            if multi:  # time of inf. conjunction
                                l_par_bat[ii][pl_key].t0 = ldict[l_time_vec][ii].mean()
                            else:
                                l_par_bat[ii][pl_key].t0 = ldict[time_vec][ii].mean()
                            l_par_bat[ii][pl_key].per = 1.   # orbital period
                            l_par_bat[ii][pl_key].rp = 0.1   # planet radius(in stel radii)
                            l_par_bat[ii][pl_key].a = 15.    # semi-major axis(in stel radii)
                            l_par_bat[ii][pl_key].inc = 90.  # orbital inclination (in degrees)
                            l_par_bat[ii][pl_key].ecc = 0.   # eccentricity
                            l_par_bat[ii][pl_key].w = 90.    # long. of periastron (in deg.)
                            l_par_bat[ii][pl_key].limb_dark = LD_parcont.ld_type  # LD model
                            l_par_bat[ii][pl_key].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if transit_model == "batman":
                if dst is None:
                    if multi:
                        template_batman_pl_5 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}, {{ltime_vec}}[{ii}])"
                                                "\n".format(ii=ii))
                        template_preambule_pl += template_batman_pl_5
                    else:
                        template_preambule_pl += ("{tab}m_{planet} = TransitModel("
                                                  "params_{planet}, {time_vec})\n")
                    l_par_bat.append({})
                    for planet in planets.values():
                        for add_plonlyext in [True, False]:
                            if add_plonlyext:
                                pl_key = planet.get_name() + ext_plonly
                            else:
                                pl_key = planet.get_name()
                            l_par_bat[ii][pl_key] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        for add_plonlyext in [True, False]:
                            if add_plonlyext:
                                pl_key = planet.get_name() + ext_plonly
                            else:
                                pl_key = planet.get_name()
                        l_par_bat[ii][pl_key] = TransitParams()
                        if multi:  # time of inf. conjunction
                            l_par_bat[ii][pl_key].t0 = ldict[l_time_vec][ii].mean()
                        else:
                            l_par_bat[ii][pl_key].t0 = ldict[time_vec][ii].mean()
                        l_par_bat[ii][pl_key].per = 1.   # orbital period
                        l_par_bat[ii][pl_key].rp = 0.1   # planet radius(in stel radii)
                        l_par_bat[ii][pl_key].a = 15.    # semi-major axis(in stel radii)
                        l_par_bat[ii][pl_key].inc = 90.  # orbital inclination (in degrees)
                        l_par_bat[ii][pl_key].ecc = 0.   # eccentricity
                        l_par_bat[ii][pl_key].w = 90.    # long. of periastron (in deg.)
                        l_par_bat[ii][pl_key].limb_dark = LD_parcont.ld_type  # LD model
                        l_par_bat[ii][pl_key].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

    # Create the text for template_planet_lc
    if transit_model == "batman":
        if multi:
            template_planet_lc = ("m_{planet}_{instmod_fullname}_dataset{dst_key}.light_curve("
                                  "params_{planet}_{instmod_fullname}_dataset{dst_key}) - 1 ")
        else:
            template_planet_lc = ("m_{planet}.light_curve(params_{planet}) - 1 ")
    else:
        if parametrisation == "Multis":
            if multi:
                template_planet_lc = ("m.evaluate({ltime_vec}[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tic}, {P}, aR_{planet}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_planet_lc = ("m.evaluate({time_vec}, {Rrat}, {ld_param_list}, {tic}, {P},"
                                      " aR_{planet}, inc_{planet}, ecc_{planet}, "
                                      "omega_{planet}) - 1 ")
        else:
            if multi:
                template_planet_lc = ("m.evaluate({ltime_vec}[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tic}, {P}, {aR}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_planet_lc = ("m.evaluate({time_vec}, {Rrat}, {ld_param_list}, {tic}, "
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
        arg_list[planet.get_name()] = deepcopy(arg_list_before)
        param_nb[planet.get_name()] = param_nb_before

        # Create the params_planet object
        if transit_model == "batman":
            for ii, instmdl, dst, par_bat in zip(range(len(l_inst_model)), l_inst_model,
                                                 l_dataset, l_par_bat):
                if dst is not None:
                    if multi:
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.get_name(),
                                                    instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                    dst_key=dst.number))
                        tt = ldict[l_time_vec][ii]
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.get_name())
                        tt = ldict[time_vec]
                    ldict[params_pl_inst] = par_bat[planet.get_name()]
                    supersamp = SSE4instmodfname.get_supersamp(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
                    if supersamp > 1:
                        exptime = SSE4instmodfname.get_exptime(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
                        m_batman = TransitModel(ldict[params_pl_inst],
                                                tt, supersample_factor=supersamp,
                                                exp_time=exptime)
                    else:
                        m_batman = TransitModel(ldict[params_pl_inst], tt)
                    if multi:
                        m_pl_inst = ("m_{planet}_{instmod_fullname}_dataset{dst_key}"
                                     "".format(planet=planet.get_name(),
                                               instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                               dst_key=dst.number))

                    else:
                        m_pl_inst = "m_{planet}".format(planet=planet.get_name())
                    ldict[m_pl_inst] = m_batman
                else:
                    if multi:
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.get_name(),
                                                    instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                    dst_key=dst.number))
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.get_name())
                    ldict[params_pl_inst] = par_bat[planet.get_name()]

        # Create two dictionaries which will contain the text for each planet parameter for the
        # current planet and for the whole system.
        params_planet = {}
        params_planet_only = {}
        params_whole = {}
        # Create the text for each planet parameter for the current planet and for the whole
        # system.
        l_param = [planet.ecosw, planet.esinw, planet.cosinc, planet.tic, planet.P,
                   planet.Rrat]
        if parametrisation != "Multis":
            l_param.append(planet.aR)
        else:
            params_planet["aR"] = ""
            params_planet_only["aR"] = ""
        for param in l_param:
            param_text = add_param_argument(param=param, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                            key_arglist=[key_whole, planet.get_name(), planet.get_name() + ext_plonly],
                                            param_vector_name=par_vec_name)
            params_whole[param.get_name()] = param_text[key_whole]
            params_planet[param.get_name()] = param_text[planet.get_name()]
            params_planet_only[param.get_name()] = param_text[planet.get_name() + ext_plonly]

        # Create the preambule text that compute intermediate variables
        # No need to make different cases for if batman or not or is dataset is None or not
        # because if one argument is not in the template, it is not used and this is it.
        preambule_planet = (template_preambule_pl.
                            format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                   ecosw=params_planet["ecosw"],
                                   esinw=params_planet["esinw"],
                                   tic=params_planet["tic"], rhostar=rhostar,
                                   cosinc=params_planet["cosinc"], P=params_planet["P"],
                                   Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                   # ld_mod_name=LD_parcont.ld_type,
                                   # ld_param_list=ld_param_list,
                                   tab=tab))
        preambule_planet_only = (template_preambule_pl.
                                 format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                        ecosw=params_planet_only["ecosw"],
                                        esinw=params_planet_only["esinw"],
                                        tic=params_planet_only["tic"], rhostar=rhostar,
                                        cosinc=params_planet_only["cosinc"], P=params_planet_only["P"],
                                        Rrat=params_planet_only["Rrat"], aR=params_planet_only["aR"],
                                        # ld_mod_name=LD_parcont.ld_type,
                                        # ld_param_list=ld_param_list,
                                        tab=tab))
        preambule_whole += (template_preambule_pl.
                            format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                   ecosw=params_whole["ecosw"],
                                   esinw=params_whole["esinw"], tic=params_whole["tic"],
                                   cosinc=params_whole["cosinc"], P=params_whole["P"],
                                   Rrat=params_whole["Rrat"], aR=params_planet["aR"],
                                   # ld_mod_name=LD_parcont.ld_type,
                                   rhostar=rhostar,
                                   # ld_param_list=ld_param_list,
                                   tab=tab))

        # planets LC contribution (planet_lc and whole_planets_lc)
        # No need for case if batman or if dataset is None. Same reason than above
        l_planet_lc = []
        l_planet_only_lc = []
        for ii, instmdl, dst, ld_param_list in zip(range(len(l_inst_model)), l_inst_model,
                                                   l_dataset, l_ld_param_list):
            if instmdl is None:
                instmdl_fname = None
            else:
                instmdl_fname = instmdl.get_name(include_prefix=True, code_version=True, recursive=True)
            if dst is None:
                dst_nb = None
            else:
                dst_nb = dst.number
            l_planet_lc.append(template_planet_lc.format(planet=planet.get_name(),
                                                         ltime_vec=l_time_vec,
                                                         time_vec=time_vec,
                                                         instmod_fullname=instmdl_fname,
                                                         dst_key=dst_nb,
                                                         aR=params_planet["aR"],
                                                         Rrat=params_planet["Rrat"],
                                                         tic=params_planet["tic"],
                                                         P=params_planet["P"],
                                                         ld_param_list=ld_param_list,
                                                         ii=ii
                                                         ))
            l_planet_only_lc.append(template_planet_lc.format(planet=planet.get_name(),
                                                              ltime_vec=l_time_vec,
                                                              time_vec=time_vec,
                                                              instmod_fullname=instmdl_fname,
                                                              dst_key=dst_nb,
                                                              aR=params_planet_only["aR"],
                                                              Rrat=params_planet_only["Rrat"],
                                                              tic=params_planet_only["tic"],
                                                              P=params_planet_only["P"],
                                                              ld_param_list=ld_param_list,
                                                              ii=ii
                                                              ))
            l_whole_planets_lc[ii] += "+ " + template_planet_lc.format(planet=planet.get_name(),
                                                                       ltime_vec=l_time_vec,
                                                                       time_vec=time_vec,
                                                                       instmod_fullname=instmdl_fname,
                                                                       dst_key=dst_nb,
                                                                       aR=params_planet["aR"],
                                                                       Rrat=params_whole["Rrat"],
                                                                       tic=params_whole["tic"],
                                                                       P=params_whole["P"],
                                                                       ld_param_list=ld_param_list,
                                                                       ii=ii
                                                                       )

        # Fill returns text for each planet
        returns_pl = ""
        returns_pl_only = ""
        for oot_var, planet_lc, planet_only_lc in zip(l_oot_var, l_planet_lc, l_planet_only_lc):
            returns_pl += template_returns_instmod.format(oot_var=oot_var,
                                                          planets_lc="+ " + planet_lc)
            returns_pl_only += template_returns_pl_only.format(planets_lc=planet_only_lc)
            returns_pl += ", "
            returns_pl_only += ", "
        if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
            returns_pl = returns_pl[:-2]
            returns_pl_only = returns_pl_only[:-2]

        # Finalise the  text of planet LC simulator function
        if argskwargs not in arguments:
            arguments = add_argskwargs_argument(arguments)
        text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(), preambule=preambule_planet,
                                                                     arguments=arguments, returns=returns_pl,
                                                                     tab=tab))
        text_def_func[planet.get_name() + ext_plonly] = (template_function.format(object=planet.get_name() + ext_plonly,
                                                                                  preambule=preambule_planet_only,
                                                                                  arguments=arguments,
                                                                                  returns=returns_pl_only,
                                                                                  tab=tab))
        # logger.debug("text of {object} LC simulator function :\n{text_func}"
        #              "".format(object=planet.get_name(), text_func=text_def_func[planet.get_name()]))

    # Fill returns text for the whole system
    returns_whole = ""
    for oot_var, whole_planet_lc in zip(l_oot_var, l_whole_planets_lc):
        returns_whole += template_returns_instmod.format(oot_var=oot_var,
                                                         planets_lc=whole_planet_lc)
        returns_whole += ", "
    if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
        returns_whole = returns_whole[:-2]

    # Finalise the text of whole system LC simulator function
    text_def_func[key_whole] = (template_function.
                                format(object=key_whole, preambule=preambule_whole,
                                       arguments=arguments, returns=returns_whole,
                                       tab=tab))

    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict["sqrt"] = sqrt
        ldict["acos"] = acos
        if parametrisation == "Multis":
            ldict["getaoverr"] = getaoverr
        if transit_model == "batman":
            if not(has_dataset):
                ldict["TransitModel"] = TransitModel
            ldict["getomega_deg_fast"] = getomega_deg_fast
            ldict["degrees"] = degrees
        else:
            ldict["getomega_fast"] = getomega_fast
            ldict["m"] = m_pytransit
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=obj_key, text_func=text_def_func[obj_key]))
        exec(text_def_func[obj_key], ldict)
        params_model = arg_list[obj_key][key_param]
        if len(arg_list[obj_key][key_mand_kwargs]) > 0:
            mand_kwargs = str(arg_list[obj_key][key_mand_kwargs])
        else:
            mand_kwargs = None
        if len(arg_list[obj_key][key_opt_kwargs]) > 0:
            opt_kwargs = str(arg_list[obj_key][key_opt_kwargs])
        else:
            opt_kwargs = None
        logger.debug("Parameters for {object} LC simulator function :\n{dico_param}"
                     "".format(object=obj_key, dico_param={nb: param for nb, param in enumerate(params_model)}))
        dico_docf[obj_key] = DatasimDocFunc(function=ldict[function_name.format(object=obj_key)],
                                            params_model=params_model,
                                            inst_cat=instcat_docf,
                                            include_dataset_kwarg=has_dataset,
                                            mand_kwargs=mand_kwargs,
                                            opt_kwargs=opt_kwargs,
                                            inst_model_fullname=instmod_docf,
                                            dataset=dtsts_docf)
    return dico_docf


def get_ootvar(l_inst_model, l_dataset, multi, ldict, arguments, param_nb, arg_list,
               key_whole, key_param, key_mand_kwargs, key_opt_kwargs,
               time_vec_name=time_vec, l_time_vec_name=l_time_vec, l_time_vec_format=None,
               timeref_name=time_ref, l_timeref_name=l_time_ref,
               l_timeref_format=None):
    """Get the out of transit variation contribution to the light-curve

    :param list_of_Dataset l_inst_model: Checked list of Instrument_Model instance(s).
    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s).
    :param bool multi: True if the datasim function needs multiple outputs.
    :param dict ldict: dictionary to be used as local dictionary argument of the exec function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param str arguments: string giving the current text of arguments
    :param dict_of_int param_nb: dictionary with key = key_whole, value = current number of free
        parameters in the model
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param string key_whole: Key used for the whole system
    :param string key_param: Key used for the parameters entry of arg_list
    :param str key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param str key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param str time_vec_name: Str used to designate the time vector
    :param str l_time_vec_name: Str used to designate the list of time vectors
    :param str l_time_vec_format: Str used to access an element of l_time_vec_name
    :param str timeref_name: Str used to designate the time vector
    :param str l_timeref_name: Str used to designate the list of time references
    :param str l_timeref_format: Str used to access an element of l_timeref_name
    :return list_of_string l_oot_var: list give the string representation of the contributions
        of the out of transit variation for each couple instrument model - dataset in
        l_inst_model and l_dataset.
    :return str arguments: Updated string giving the new text of arguments
    """
    # Check if datasets are provided
    has_dataset = get_has_datasets(l_dataset)
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
                # ..., If this parameter is a main parameter (it should be), ...
                if instmdl.parameters[OOT_param_name].main:
                    value_not0 = True
                    text_OOT_param = add_param_argument(param=instmdl.parameters[OOT_param_name],
                                                        arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                                        key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]
                    # ..., if the parameter is free or the fixed value is not zero, ...
                    if text_OOT_param != str(0.0):
                        l_oot_var[ii] += "+ {}".format(text_OOT_param)
                    # ..., else, since the fixed value is zero, this order doesn't have any
                    # contribution
                    else:
                        value_not0 = False
                    # ..., if the order has a contribution to the out of transit variation and
                    # the considered order is more than 0 meaning the time plays a role, ...
                    if value_not0 and order > 0:
                        # ..., if neither "tref" nor "l_tref" are in the list of kwargs and
                        # no dataset is provided, ...
                        if ((timeref_name not in arg_list[key_whole][key_mand_kwargs] +
                             arg_list[key_whole][key_opt_kwargs]) and
                            (l_timeref_name not in arg_list[key_whole][key_mand_kwargs] +
                             arg_list[key_whole][key_opt_kwargs])):
                            def get_time_ref(time):
                                return time[0]
                            (arguments, timeref_arg_name, timeref_arg
                             ) = add_timeref_arguments(arguments, multi, arg_list, key_whole,
                                                       key_mand_kwargs, key_opt_kwargs, ldict,
                                                       get_time_ref, has_dataset, True, l_dataset,
                                                       timeref_name, l_timeref_name)
                        # ..., add the end of this order's contribution to the text of the out of
                        # transit variation, ...
                        if order == 1:
                            if multi:
                                if l_time_vec_format is None:
                                    l_time_ii = ("{ltimevec}[{ii}]"
                                                 "".format(ltimevec=l_time_vec_name, ii=ii))
                                else:
                                    l_time_ii = l_time_vec_format.format(ii=ii)
                                if l_timeref_format is None:
                                    l_timeref_ii = ("{ltimeref}[{ii}]"
                                                    "".format(ltimeref=l_timeref_name, ii=ii))
                                else:
                                    l_timeref_ii = l_timeref_format.format(ii=ii)
                                l_oot_var[ii] += (" * ({l_time_ii} - {l_timeref_ii}) "
                                                  "".format(ii=ii, l_time_ii=l_time_ii,
                                                            l_timeref_ii=l_timeref_ii))
                            else:
                                l_oot_var[ii] += (" * ({time} - {timeref}) "
                                                  "".format(time=time_vec_name,
                                                            timeref=timeref_name))
                        elif order > 1:
                            if multi:
                                l_time_ii = l_time_vec_format.format(ii=ii)
                                l_timeref_ii = l_timeref_format.format(ii=ii)
                                l_oot_var[ii] += (" * ({l_time_ii} - {l_timeref_ii})"
                                                  "**{order}".format(order=order, ii=ii,
                                                                     l_time_ii=l_time_ii,
                                                                     l_timeref_ii=l_timeref_ii))
                            else:
                                l_oot_var[ii] += (" * ({time} - {timeref})**{order}"
                                                  "".format(order=order, time=time_vec_name,
                                                            timeref=timeref_name))
                    # If the is no contribution to the oot of transit variation from this order
                    # add only a space.
                    elif value_not0 and order == 0:
                        l_oot_var[ii] += " "
    return l_oot_var, arguments


def get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, LDs, param_nb, arg_list, key_whole,
                             key_param):
    """Return the list of LD param container name, instance and parameter string list for a given star.

    :param list_of_Dataset l_inst_model: Checked list of Instrument_Model instance(s).
    :param dict_of_ ldmodel4instmodfname: Dictionary giving Limd darkening model to use for each
        instrument model
    :param Star star: Star object
    :param LDs: LD object?
    :param dict_of_int param_nb: dictionary with key = key_whole, value = current number of free
        parameters in the model
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param string key_whole: key to use to identify the whole system in the output dictionary
        (dico_docf).
    :param string key_param: Key used for the parameters entry of arg_list
    :return list_of_string l_LD_parcont_name: List of limb darkening parameter container name
        associated with the Instrument_Model instances in l_inst_model.
    :return list_of_LD l_LD_parcont: list of LD parameter container object associated with the
        Instrument_Model instances in l_inst_model.
    :return l_LD_param_list: list of string giving the list of limb darkening parameters values
        associated with the Instrument_Model instances in l_inst_model.
    """
    # Get the ld_parcont and ld_param_list
    l_LD_parcont_name = []
    l_LD_parcont = []
    l_LD_param_list = []
    for ii, instmdl in enumerate(l_inst_model):
        l_LD_parcont_name.append(ldmodel4instmodfname[instmdl.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name])
        l_LD_parcont.append(LDs[star.code_name + "_" + l_LD_parcont_name[ii]])
        l_LD_param_list.append("[")
        for param in l_LD_parcont[ii].get_list_params(main=True):
            l_LD_param_list[ii] += (add_param_argument(param=param, arg_list=arg_list, key_param=key_param,
                                                       param_nb=param_nb, key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole] +
                                    ", ")
        l_LD_param_list[ii] += "]"
    return l_LD_parcont_name, l_LD_parcont, l_LD_param_list
