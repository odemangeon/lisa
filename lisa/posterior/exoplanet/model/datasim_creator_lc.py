#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator LC module.

TODO:
- In the docstring of create_datasimulator_LC for the arguments inst_models, I wrote that it could be
None, now I am not sure that it's actually possible for it to be None. To Check.
- time_arg_name is a new return of add_time_argument and is not used in the rest of the create_datasimulator_LC function.
Check if it can be used.
- I am not sure that some of the comments are still valid. So I need to check if this comment are still valid or not.
Search for TODO_CHECK_THIS_COMMENT which I put in front each one of these comments.
"""
from logging import getLogger
from textwrap import dedent
from copy import deepcopy
from math import acos, degrees, sqrt
from numpy import ones_like, inf

from batman import TransitModel, TransitParams
# from pytransit import MandelAgol  # Temporarily? remove pytransit from the available rv_models

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

    Arguments
    ---------
    star                    : Star object
        Star instance of the parent star
    planets                 : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    key_whole               : str
        key to use to identify the whole system in the output dictionary (dico_docf).
    key_param               : str
        Key used for the parameters entry of arg_list
    key_mand_kwargs         : str
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs          : str
        Key used for the optional keyword argument entry of arg_list
    ext_plonly              : str
        extension to the planet name used for planet only model (without star, nor instrument)
    parametrisation         : str
        string refering to the parametrisation to use
    ldmodel4instmodfname    : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                     : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    transit_model           : str
        String refering to the transit model to use (can be 'pytransit' or 'batman')
    SSE4instmodfname        : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    inst_models             : Instrument_Model or List of Instrument_Model or None
        List of Instrument_Model instance which, if datasets is provided, should be the instrument models
        to use for each dataset provided in the datasets arguments.
    datasets                : Dataset or list_of_Dataset or None
        List of datasets to be simulated.
        If no dataset is provided (datasets=None), the datasimulator function produced by this function will
        have as arguments the times on top of the parameter vector of the model.
        If at least one dataset is provided (datasets!=None), then the datasimulator function produced
        by this function will include the times, so it will not be an argument.
        If provided the number of datasets needs to match the number of instrument models provided by
        the inst_models arguments
    param_vector_name       : str
        string giving the name of the vector of parameters argument of the datasimulator function.

    Returns
    -------
    dico_docf : dict_of_DatasimDocFunc
        A dictionary with DocFunctions containing the data
        simulator function for the whole system ("whole") and for the each planet individually
        ("planet_name")
    """
    ## Check the content of the datasets and inst_models arguments
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

    ## Check if datasets are provided and store the answer in the has_dataset variable
    has_dataset = get_has_datasets(l_dataset)

    ## Initialise text_def_func
    # text_def_func is a dictionary which will received the text of the datasimulator functions
    # It has several keys for several datasimulator functions:
    #   - "whole" for the whole system with all the planets
    #   - "b", "c", ... ("planet name") for only the contribution of one planet.
    # Format: {"System part name": str_text_of_the_datasimulator_for_the_system_part}
    text_def_func = {}

    ## Initialise param_nb, arg_list, arguments and ldict
    # - param_nb is a dictionary that will keep track of the number of parameter for each
    # function in text_def_func (so the keys are the same).
    # Format: {"System part name": int_current_nb_of_model_parameters_of_the_datasimulator}
    # - arg_list is a dictionary which will receive the argument list of the datasimulator
    # function in text_def_func (so the keys are the same).
    # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
    # keys:
    #   - "param": list of the free parameters name in order
    #   - "kwargs": list of the additional argument that you need to provide to simulate the
    #               data. For example the time]
    # Format: {"System part name": {"params": [str_name_of_model_parameter_in_the_parameter_vector, ],
    #                               "kwargs": [str_name_of_additional_argument_for the datasimulator, ]}
    # - arguments is ...
    # Create the "arguments" text variable and intial with the parameter vector
    # - ldict is the dictionary which will be used as local dictionary for the creation/co;plilation
    # of the datasimulator functions with exec
    # Format: {"variable name": variable, }
    (param_nb,
     arg_list,
     arguments,
     ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, keys=[key_whole], key_mand_kwargs=key_mand_kwargs,
                                                   key_opt_kwargs=key_opt_kwargs, param_vector_name=par_vec_name)

    # Add the stellar density the model parameter vectors (in arg_list) if required by the parametrisation
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    # rhostar is the reference to the value of rho star (if rho star is a free parameter it's "p[ii]"
    # the reference to rho star within the parameter vector of the function simulating the whole system.
    # Otherwise it's the fixed value of rho star)
    if parametrisation == "Multis":
        rhostar = add_param_argument(param=star.rho, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                     key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]
    else:
        rhostar = None

    ## Get the ld_parcont_name, ld_parcont and ld_param_list variable
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    # - l_LD_parcont_name is the List of limb darkening models name (parameter container name) associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: ["<limb darkening model name>", ]
    # - l_LD_parcont is the list of limb darkening models (parameter container object) associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: [<limb darkening model>, ]
    # - l_LD_param_list is the list of string which themself write the list of limb darkening parameters values associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: ["[p[1], p[2]]", ]
    (l_LD_parcont_name,
     l_LD_parcont,
     l_ld_param_list) = get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, LDs, param_nb,
                                                 arg_list, key_whole, key_param)

    # Initialise arg_list and param_nb keys and values for the planet only datasimulators
    for planet in planets.values():
        arg_list[planet.get_name() + ext_plonly] = deepcopy(arg_list[key_whole])
        param_nb[planet.get_name() + ext_plonly] = param_nb[key_whole]

    # Initialise function_name and template_function the template function name and the template function text
    function_name = ("LCsim_{{object}}_{instmod_fullname}"
                     "".format(instmod_fullname=inst_model_full_name))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule}}
    {{tab}}{{condition}}
    {{tab}}try:
    {{tab}}    return {{returns}}
    {{tab}}except RuntimeError:
    {{tab}}    return {{returns_except}}
    """.format(function_name=function_name)
    # Below this was used for debugging purposes
    # template_function = """
    # def {function_name}({{arguments}}):
    # {{tab}}{{preambule}}
    # {{tab}}{{condition}}
    # {{tab}}with open("chain.dat", "a") as file
    # {{tab}}    print(" ".join([str(p_i) for p_i in p]), file=file)
    # {{tab}}return {{returns}}
    # """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Initialise template_returns_instmod, the template for each instmodel
    template_returns_instmod = "1 {oot_var}{planets_lc}"

    # Initialise template_returns_pl_only, the template for planetary contibution only (No instrument nor star) for phase fold plots per planet
    template_returns_pl_only = "{planets_lc}"

    # Add the time as additional argument for the functions or include it in ldict
    (arguments, time_arg_name, time_arg, time_arg_in_arguments
     ) = add_time_argument(arguments=arguments, multi=multi, has_dataset=has_dataset, arg_list=arg_list,
                           key_arglist=key_whole, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                           ldict=ldict, l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                           add_to_ldict=True, backup_add_to_args=True)

    ## Get the l_oot_var and add the t_ref(s) to the list of arguments for the functions
    # l_oot_var is the list of strings giving the string representation of the out of transit variation model
    # for each couple instrument model - dataset in l_inst_model and l_dataset.
    # Format: ["oot model", ]
    l_oot_var, arguments = get_ootvar(l_inst_model, l_dataset, multi,
                                      ldict, arguments, param_nb, arg_list, key_whole,
                                      key_param, key_mand_kwargs, key_opt_kwargs,
                                      time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                      timeref_name=time_ref, l_timeref_name=l_time_ref)
    # Initialise template_condition, the template for the condition (no planet should pass into the star)
    template_condition = """
    {tab}{preambule}
    {tab}if {condition}:
    {tab}    return {returns}
    """
    template_condition = dedent(template_condition)

    # Initialise template_preambule_pl, the template of the preambule of the function for each planet
    template_preambule_pl = """
        {tab}ecc_{planet} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})"""

    if transit_model == "batman":
        template_preambule_pl += """
        {tab}omega_{planet} = getomega_deg_fast({ecosw}, {esinw})
        {tab}inc_{planet} = degrees(acos({cosinc}))"""
        if parametrisation == "Multis":
            template_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar}, ecc_{planet}, omega_{planet})"""

        for instmdl, dst, LD_parcont, ld_param_list in zip(l_inst_model, l_dataset, l_LD_parcont,
                                                           l_ld_param_list):
            # TODO_CHECK_THIS_COMMENT: If the same model is used for several dataset a model will be several times in
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
    else:  # pytransit
        template_preambule_pl += """
        {tab}omega_{planet} = getomega_fast({esinw}, {ecosw})
        {tab}inc_{planet} = acos({cosinc})
        """
        if parametrisation == "Multis":
            template_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar}, ecc_{planet}, degrees(omega_{planet}))"""
    template_preambule_pl = dedent(template_preambule_pl)

    ## Add or not the initialisation of the TransitModel instance or MandelAgol instance (to the template_preambule)
    l_par_bat = []
    for ii, instmdl, dst, LD_parcont in zip(range(len(l_inst_model)), l_inst_model, l_dataset,
                                            l_LD_parcont):
        supersamp = SSE4instmodfname.get_supersamp(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
        # If you need to supersample the model
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
        # If you DON'T need to supersample the model
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

    # Create the templates to conpute the condition to know if the planet passes in the star
    # and of what tho return if condition is True
    # Fill return if condition planet goes in the star is True
    # The condition is taken from https://iopscience.iop.org/article/10.1086/592381/fulltext/75178.text.html (section 3.1)
    if parametrisation == "Multis":  # aR is not a main parameter
        template_preambule_cond_pl = "condition_{planet} = (aR_{planet} < ((1.5 / (1 - ecc_{planet})) + {Rrat}))\n"
    else:  # aR is a main parameter
        template_preambule_cond_pl = "condition_{planet} = ({aR} < ((1 .5 / (1 - ecc_{planet})) + {Rrat}))\n"
    if multi:
        template_returns_condition = "ones_like({ltime_vec}) * (- inf)"  # "ones_like({ltime_vec}[{ii}]) * (- inf)"
    else:
        template_returns_condition = "ones_like({time_vec}) * (- inf)"

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
    param_nb_before = param_nb[key_whole]
    arg_list_before = deepcopy(arg_list[key_whole])

    # Initialise the text for the whole system preambule
    preambule_whole = ""
    preambule_cond_whole = "condition = False\n"
    l_whole_planets_lc = []
    l_whole_return_condition = []
    for instmdl in l_inst_model:
        l_whole_planets_lc.append("")
        l_whole_return_condition.append(template_returns_condition.format(ltime_vec=l_time_vec, time_vec=time_vec))
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
            params_whole["aR"] = ""
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
                                   Rrat=params_whole["Rrat"], aR=params_whole["aR"],
                                   # ld_mod_name=LD_parcont.ld_type,
                                   rhostar=rhostar,
                                   # ld_param_list=ld_param_list,
                                   tab=tab))
        preambule_cond_planet = template_preambule_cond_pl.format(planet=planet.get_name(), aR=params_planet["aR"],
                                                                  Rrat=params_planet["Rrat"])
        preambule_cond_planet_only = template_preambule_cond_pl.format(planet=planet.get_name(), aR=params_planet_only["aR"],
                                                                       Rrat=params_planet["Rrat"])
        condition_planet_only = condition_planet = "condition_{planet}".format(planet=planet.get_name())
        preambule_cond_whole += tab + template_preambule_cond_pl.format(planet=planet.get_name(), aR=params_whole["aR"],
                                                                        Rrat=params_whole["Rrat"])
        preambule_cond_whole += "{tab}condition = condition or condition_{planet}\n".format(planet=planet.get_name(), tab=tab)

        # planets LC contribution (planet_lc and whole_planets_lc)
        # No need for case if batman or if dataset is None. Same reason than above
        l_planet_lc = []
        l_planet_only_lc = []
        l_planet_return_condition = []
        l_planet_only_return_condition = []
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
            l_planet_return_condition.append(template_returns_condition.format(ltime_vec=l_time_vec, time_vec=time_vec))
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
            l_planet_only_return_condition.append(template_returns_condition.format(ltime_vec=l_time_vec, time_vec=time_vec))
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

        # Fill condition text for each planet
        # template_condition = """"
        # {tab}{preambule}
        # {tab}if {condition}:
        # {tab}    return {returns}
        # """
        condition_return_planet = ""
        condition_return_planet_only = ""
        for ret_cond_pl, ret_cond_pl_only in zip(l_planet_return_condition, l_planet_only_return_condition):
            condition_return_planet += ret_cond_pl
            condition_return_planet += ", "
            condition_return_planet_only += ret_cond_pl_only
            condition_return_planet_only += ", "
        if not(multi):
            condition_return_planet = condition_return_planet[:-2]
            condition_return_planet_only = condition_return_planet_only[:-2]
        condition_planet = template_condition.format(preambule=preambule_cond_planet, condition=condition_planet, returns=condition_return_planet, tab=tab)
        condition_planet_only = template_condition.format(preambule=preambule_cond_planet_only, condition=condition_planet_only, returns=condition_return_planet_only, tab=tab)

        # Finalise the  text of planet LC simulator function
        if argskwargs not in arguments:
            arguments = add_argskwargs_argument(arguments)
        text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(), preambule=preambule_planet,
                                                                     condition=condition_planet,
                                                                     arguments=arguments, returns=returns_pl,
                                                                     returns_except=condition_return_planet,
                                                                     tab=tab))
        text_def_func[planet.get_name() + ext_plonly] = (template_function.format(object=planet.get_name() + ext_plonly,
                                                                                  preambule=preambule_planet_only,
                                                                                  condition=condition_planet_only,
                                                                                  arguments=arguments,
                                                                                  returns=returns_pl_only,
                                                                                  returns_except=condition_return_planet_only,
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
    condition_return_whole = ""
    for ret_cond_whole in l_whole_return_condition:
        condition_return_whole += ret_cond_pl
        condition_return_whole += ", "
    if not(multi):
        condition_return_whole = condition_return_whole[:-2]
    condition_whole = template_condition.format(preambule=preambule_cond_whole, condition="condition", returns=condition_return_whole, tab=tab)

    text_def_func[key_whole] = (template_function.
                                format(object=key_whole, preambule=preambule_whole, condition=condition_whole,
                                       arguments=arguments, returns=returns_whole, returns_except=condition_return_whole,
                                       tab=tab))

    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict["ones_like"] = ones_like
        ldict["inf"] = inf
        ldict["sqrt"] = sqrt
        ldict["acos"] = acos
        ldict["degrees"] = degrees
        if parametrisation == "Multis":
            ldict["getaoverr"] = getaoverr
        if transit_model == "batman":
            if not(has_dataset):
                ldict["TransitModel"] = TransitModel
            ldict["getomega_deg_fast"] = getomega_deg_fast
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
               timeref_name=time_ref, l_timeref_name=l_time_ref, l_timeref_format=None, use_dataset_4_tref=False,
               time_ref_val=None):
    """Get the out of transit variation contribution to the light-curve

    Arguments
    ---------
    l_inst_model        : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset           : list_of_Dataset
        Checked list of Dataset instance(s).
    multi               : bool
        True if the datasim function needs to give multiple outputs.
    ldict               : dict
        dictionary to be used as local dictionary argument of the exec function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arguments           : str
        string giving the current text of arguments for the functions
    param_nb            : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list            : dict_of_dict_of_list_of_str
        Dictionary giving the arguments of the functions currently being produced. The keys of this
        dictionary are string giving the name/ref of the simulated functions and the values are dictionary
        with at least one key which is the content of the argument key_param and the value associated to
        this key is the list of parameter full names in the parameter vector of the functions being produced.
        If the parameter provided by param is free. It's name will be added to one or several of these list.
        Format: {"name_of_function": {key_param: [str_name_of_model_parameter_in_the_parameter_vector], }, }
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_whole           : str
        Key used for the whole system in arg_list and param_nb
    key_param           : str
        Key used for the parameters entry of arg_list values
    key_mand_kwargs     : str
        Key used for the mandatory keyword argument entry of arg_list values
    key_opt_kwargs      : str
        Key used for the optional keyword argument entry of arg_list values
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors
    l_time_vec_format   : str
        Str used to access an element of l_time_vec_name
    timeref_name        : str
        Str used to designate the time reference
    l_timeref_name      : str
        Str used to designate the list of time references
    l_timeref_format    : str
        Str used to access an element of l_timeref_name
    use_dataset_4_tref  : bool
        If True, then the dataset will be used to compute the reference time
    time_ref_val        :
        Value of the time reference(s) if not computed from the datasets

    Returns
    -------
    l_oot_var   : list_of_string
        list giving the string representation of the out of transit variation model for each couple
        instrument model - dataset in l_inst_model and l_dataset.
        Format: ["oot model", ]
    arguments   : str
        Updated string giving the new text of arguments
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
                             ) = add_timeref_arguments(arguments=arguments, multi=multi, vect_for_multi=True,
                                                       use_dataset=use_dataset_4_tref,
                                                       arg_list=arg_list, key_arglist=key_whole,
                                                       key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                                       ldict=ldict, has_dataset=has_dataset, get_time_ref=get_time_ref,
                                                       time_ref_val=time_ref_val, l_dataset=l_dataset,
                                                       timeref_name=timeref_name, l_timeref_name=l_timeref_name,
                                                       time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name)
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
                    # If the is no contribution to the oot of transit variation from this order or order == 0
                    # add only a space.
                    elif value_not0 and order == 0:
                        l_oot_var[ii] += " "
    return l_oot_var, arguments


def get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, LDs, param_nb, arg_list, key_whole,
                             key_param):
    """Return the list of LD param container name, instance and parameter string list for a given star.

    Arguments
    ---------
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    ldmodel4instmodfname    : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    star                    : Star
        Star object
    LDs                     : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    param_nb                : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list                : dict_of_dict_of_list_of_str
        Dictionary giving the arguments of the functions currently being produced. The keys of this
        dictionary are string giving the name/ref of the simulated functions and the values are dictionary
        with at least one key which is the content of the argument key_param and the value associated to
        this key is the list of parameter full names in the parameter vector of the functions being produced.
        If the parameter provided by param is free. It's name will be added to one or several of these list.
        Format: {"name_of_function": {key_param: [str_name_of_model_parameter_in_the_parameter_vector], }, }
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_whole               : str
        key to use to identify the whole system in param_nb, arg_list.
    key_param               : str
        Key used for the parameters entry of arg_list values

    Returns
    -------
    l_LD_parcont_name   : list_of_string
        List of limb darkening models name (parameter container name) associated with the Instrument_Model instances
        in l_inst_model.
    l_LD_parcont        : list_of_LD
        list of limb darkening models (parameter container object) associated with the Instrument_Model instances
        in l_inst_model.
    l_LD_param_list     : list_of_str
        list of string which themself write the list of limb darkening parameters values associated with the Instrument_Model instances
        in l_inst_model.
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
