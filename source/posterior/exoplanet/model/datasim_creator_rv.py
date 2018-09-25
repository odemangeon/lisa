#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator RV module.
"""
from logging import getLogger
from textwrap import dedent
from copy import deepcopy

import math as mt

from ajplanet import pl_rv_array

# from ..dataset_and_instrument.rv import RV_inst_cat
from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.model.datasimulator_toolbox import check_datasets_and_instmodels, get_has_datasets
from ...core.model.datasimulator_timeseries_toolbox import (add_time_argument, time_vec, l_time_vec,
                                                            add_timeref_arguments, time_ref,
                                                            l_time_ref)
# from ...core.dataset_and_instrument.instrument import Instrument_Model
# from ...core.dataset_and_instrument.dataset import Dataset
from ....tools.function_from_text_toolbox import (init_arglist_paramnb_arguments_ldict, add_param_argument,
                                                  par_vec_name, add_argskwargs_argument, argskwargs)
from ....tools.convert import gettp_fast  # getecc_fast, getomega_fast


## Logger object
logger = getLogger()


def create_datasimulator_RV(star, planets, key_whole, key_param, key_mand_kwargs, key_opt_kwargs,
                            RV_globalref_instname=None,
                            RV_instref_modnames=None,
                            RV_inst_db=None,
                            inst_models=None, datasets=None,
                            param_vector_name=par_vec_name):
    """Return a radial velocity datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each instrument
    model individually.

    :param Star star: Star instance corresponding to the star in the planetary system
    :param dict planets: key=planet name, value=Planet instance
    :param string key_whole: Key used for the whole system
    :param string key_param: Key used for the parameters entry of arg_list
    :param str key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param str key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param string RV_globalref_instname: Instrument name of the instrument used as RV reference
    :param dict RV_instref_modnames: key=instrument name, value=instrument model name (not
        full name) used as reference for the instrument
    :param dict RV_inst_db: key=instrument name, value=dict: key= instrument model name,
        value=instrument model object.
    :param Instrument_Model/list_of_Instrument_Model/None inst_models:
        If None the datasimulator does not include any contribution from the instrument.
        If Instrument_Model, return a datasimulator docfunc for this instrument model
        If list of Instrument_Model, a datasimulator is produced for each instrument model in the
            list
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

    :return dict dico_docf: key=object (planet name or whole_key), value=DatasimDocFunc
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
    #               data. For example the time
    # Create the "arguments" text variable and intial with the parameter vector
    # Create and intialise the "ldict" dictionary variable which will be used as local dictionary
    # for the creation of the datasim functions with exec
    (param_nb,
     arg_list,
     arguments,
     ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, keys=[key_whole], key_mand_kwargs=key_mand_kwargs,
                                                   key_opt_kwargs=key_opt_kwargs, param_vector_name=par_vec_name)

    # Initialise the template function text
    function_name = ("RVsim_{{object}}_{instmod_fullname}"
                     "".format(instmod_fullname=inst_model_full_name))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule}}
    {{tab}}return {{returns}}
    """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Initialise the template for each instmodel
    template_returns_instmod = "{delta_inst_rv} {star_mean_rv} {planets_rv}"

    # Add the time as additional argument
    (arguments, time_arg_name, time_arg
     ) = add_time_argument(arguments=arguments, multi=multi, has_dataset=has_dataset, arg_list=arg_list,
                           key_arglist=key_whole, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                           ldict=ldict, l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                           add_to_ldict=True, backup_add_to_args=True)

    # Get star mean rv and instrument delta rv contribution for each couple instrument - dataset
    (l_star_mean_rv, l_delta_inst_rv, arguments
     ) = get_starmeanrv_and_deltarv(l_inst_model, l_dataset, star, multi, RV_globalref_instname,
                                    RV_instref_modnames, RV_inst_db, ldict, arguments, param_nb,
                                    arg_list, key_whole, key_param, key_mand_kwargs, key_opt_kwargs,
                                    time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                    timeref_name=time_ref, l_timeref_name=l_time_ref)

    # Save the param_nb and arg_list for the whole function before iterating over the planets
    # text_def_func_before = text_def_func[self.key_whole]
    param_nb_before = param_nb[key_whole]
    arg_list_before = deepcopy(arg_list[key_whole])

    # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
    # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
    # planets functions.
    template_preambule = """
    {tab}ecc_{planet} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})
    {tab}omega_{planet} = atan2({esinw}, {ecosw})
    {tab}tp_{planet} = gettp_fast({P}, {tic}, ecc_{planet}, omega_{planet})
    """
    template_planet_rv = "+ pl_rv_array({time}, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet}, {P})"

    # Initialise the text for the whole system preambule
    preambule_whole = ""
    l_whole_planets_rv = []
    for instmdl in l_inst_model:
        l_whole_planets_rv.append("")
    for i, planet in enumerate(planets.values()):
        # Initialise arg_list and param_nb for the current planet
        arg_list[planet.get_name()] = deepcopy(arg_list_before)
        param_nb[planet.get_name()] = param_nb_before

        # Create two dictionaries which will contain the text for each planet parameter for the
        # current planet and for the whole system.
        params_planet = {}
        params_whole = {}
        # Create the text for each planet parameter for the current planet and for the whole
        # system.
        l_param = [planet.K, planet.ecosw, planet.esinw, planet.tic, planet.P]
        for param in l_param:
            param_text = add_param_argument(param=param, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                            key_arglist=[key_whole, planet.get_name()], param_vector_name=par_vec_name)
            params_whole[param.get_name()] = param_text[key_whole]
            params_planet[param.get_name()] = param_text[planet.get_name()]

        # Create the preambule text that compute intermediate variables
        preambule_planet = (dedent(template_preambule).
                            format(planet=planet.get_name(), ecosw=params_planet["ecosw"],
                                   esinw=params_planet["esinw"], P=params_planet["P"],
                                   tic=params_planet["tic"], tab=tab))
        preambule_whole += (dedent(template_preambule).
                            format(planet=planet.get_name(), ecosw=params_whole["ecosw"],
                                   esinw=params_whole["esinw"], P=params_whole["P"],
                                   tic=params_whole["tic"], tab=tab))

        # planets RV contribution (planet_rv and whole_planets_rv)
        l_planet_rv = []
        for ii, instmdl in enumerate(l_inst_model):
            if multi:
                time = "{ltime_vec}[{ii}]".format(ltime_vec=l_time_vec, ii=ii)
            else:
                time = time_vec
            l_planet_rv.append(template_planet_rv.format(planet=planet.get_name(),
                                                         time=time,
                                                         K=params_planet["K"],
                                                         P=params_planet["P"]))
            l_whole_planets_rv[ii] += template_planet_rv.format(planet=planet.get_name(),
                                                                time=time,
                                                                K=params_whole["K"],
                                                                P=params_whole["P"])

        # Fill returns text for each planet
        returns_pl = ""
        for delta_inst_rv, planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                          l_planet_rv,
                                                          l_star_mean_rv):
            returns_pl += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                          star_mean_rv=star_mean_rv,
                                                          planets_rv=planet_rv)
            returns_pl += ", "
        returns_pl = returns_pl[:-2]

        # Finalise the text of planet RV simulator function
        if argskwargs not in arguments:
            arguments = add_argskwargs_argument(arguments)
        text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(), preambule=preambule_planet,
                                                                     arguments=arguments, returns=returns_pl,
                                                                     tab=tab))
        # logger.debug("text of {object} RV simulator function :\n{text_func}"
        #              "".format(object=planet.get_name(), text_func=text_def_func[planet.get_name()]))

    # Fill returns text for the whole system
    returns_whole = ""
    for delta_inst_rv, whole_planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                            l_whole_planets_rv,
                                                            l_star_mean_rv):
        returns_whole += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                         star_mean_rv=star_mean_rv,
                                                         planets_rv=whole_planet_rv)
        returns_whole += ", "
    returns_whole = returns_whole[:-2]

    # Finalise the  text of whole system RV simulator function
    text_def_func[key_whole] = (template_function.format(object=key_whole,
                                                         preambule=preambule_whole,
                                                         arguments=arguments, returns=returns_whole,
                                                         tab=tab))

    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict["sqrt"] = mt.sqrt
        ldict["atan2"] = mt.atan2
        ldict["gettp_fast"] = gettp_fast
        ldict["pl_rv_array"] = pl_rv_array
        logger.debug("text of {object} RV simulator function :\n{text_func}"
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
        logger.debug("Parameters for {object} RV simulator function :\n{dico_param}"
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


def get_starmeanrv_and_deltarv(l_inst_model, l_dataset, star, multi,
                               RV_globalref_instname, RV_instref_modnames, RV_inst_db, ldict,
                               arguments, param_nb, arg_list, key_whole, key_param,
                               key_mand_kwargs, key_opt_kwargs,
                               time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                               timeref_name=time_ref, l_timeref_name=l_time_ref):
    """Get the contribution of the systemic/star rv contribution and the instrumental delta RV.

    :param list_of_Dataset l_inst_model: Checked list of Instrument_Model instance(s).
    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s).
    :param Star star: Star instance corresponding to the star in the planetary system
    :param bool multi: True if the datasim function needs multiple outputs.
    :param string RV_globalref_instname: Instrument name of the instrument used as RV reference
    :param dict RV_instref_modnames: key=instrument name, value=instrument model name (not
        full name) used as reference for the instrument
    :param dict RV_inst_db: key=instrument name, value=dict: key= instrument model name,
        value=instrument model object.
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
    :param str time_vec_name: Str used to design the time vector
    :param str l_time_vec_name: Str used to design the list of time vector
    :param str timeref_name: Str used to design the time vector
    :param str l_timeref_name: Str used to design the list of time vector
    :return list_of_string l_delta_inst_rv: list give the string representation of the contributions
        of the instrumental delta_rv for each couple instrument model - dataset in l_inst_model and
        l_dataset.
    :return list_of_string l_star_mean_rv: list give the string representation of the contribution
        of the systemic/star rv  for each couple instrument model - dataset in
        l_inst_model and l_dataset.
    :return str arguments: Updated string giving the new text of arguments
    """
    # Check if datasets are provided
    has_dataset = get_has_datasets(l_dataset)
    # Create list for the text of each instrument Delta RV (delta_inst_rv)
    l_delta_inst_rv = []
    # Create list for the text of each instrument star_mean_rv (delta_inst_rv)
    l_star_mean_rv = []
    for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
        l_delta_inst_rv.append("")
        if instmdl is not None:
            inst_name = instmdl.instrument.get_name()
            ## RVrefglobal_inst: name of the instrument chosen as global RV reference
            ## (eg: HARPS)
            RVrefglobal_instname = RV_globalref_instname
            ## RVref4inst_modname: name of the instrument model chosen as reference for the
            ## current instrument (eg: default)
            RVref4inst_modname = RV_instref_modnames[inst_name]
            # Add the Delta_RV of the global RV reference instrument model if needed
            if inst_name != RVrefglobal_instname:
                instmod_RVref4inst = RV_inst_db[inst_name][RVref4inst_modname]
                if instmod_RVref4inst.DeltaRV.main:
                    l_delta_inst_rv[ii] += (add_param_argument(param=instmod_RVref4inst.DeltaRV, arg_list=arg_list,
                                                               key_param=key_param, param_nb=param_nb,
                                                               key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole] +
                                            " + ")
            # Add the Delta_RV of the model used as RV reference for the current instrument
            if instmdl.get_name() != RVref4inst_modname:
                if instmdl.DeltaRV.main:
                    l_delta_inst_rv[ii] += (add_param_argument(param=instmdl.DeltaRV, arg_list=arg_list,
                                                               key_param=key_param, param_nb=param_nb,
                                                               key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole] +
                                            " + ")
        # Create the text for the star mean RV (star_mean_rv)
        l_star_mean_rv.append("")
        l_star_mean_rv[ii] += add_param_argument(param=star.v0, arg_list=arg_list, key_param=key_param,
                                                 param_nb=param_nb, key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]

        # If stellar RV drift has been asked, create the text for stellar RV drift, ...
        if star.with_RVdrift:
            # ..., For each order in the required polynomial model (zero is the system mean
            # velocity, so the orders starts at 1), ...
            for order in range(1, star.RVdrift_order + 1):
                # ..., get the name and full name of the parameter for this order
                RVdrift_param_name = star.get_RVdrift_param_name(order)
                # ..., If this parameter is a main parameter (it should be), ...
                if star.parameters[RVdrift_param_name].main:
                    value_not0 = True
                    text_RV_drift_param = add_param_argument(param=star.parameters[RVdrift_param_name],
                                                             arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, key_arglist=key_whole,
                                                             param_vector_name=par_vec_name)[key_whole]
                    # ..., if the parameter is free or the fixed value is not zero, ...
                    if text_RV_drift_param != str(0.0):
                        l_star_mean_rv[ii] += "+ {}".format(text_RV_drift_param)
                    # ..., else, since the fixed value is zero, this order doesn't have any
                    # contribution
                    else:
                        value_not0 = False
                    # ..., if the order has a contribution to the RV drift, ...
                    if value_not0:
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
                        # ..., add the end of this order's contribution to the text of the RV drift.
                        if order == 1:
                            if multi:
                                l_star_mean_rv[ii] += (" * ({ltime}[{ii}] - {ltimeref}[{ii}]) "
                                                       "".format(ii=ii, ltime=l_time_vec_name,
                                                                 ltimeref=l_timeref_name))
                            else:
                                l_star_mean_rv[ii] += (" * ({time} - {timeref}) "
                                                       "".format(time=time_vec_name,
                                                                 timeref=timeref_name))
                        elif order > 1:
                            if multi:
                                l_star_mean_rv[ii] += (" * ({ltime}[{ii}] - {ltimeref}[{ii}])"
                                                       "**{order}".format(order=order, ii=ii,
                                                                          ltime=l_time_vec_name,
                                                                          ltimeref=l_timeref_name))
                            else:
                                l_star_mean_rv[ii] += (" * ({time} - {timeref})**{order}"
                                                       "".format(order=order, time=time_vec_name,
                                                                 timeref=timeref_name))
    return l_star_mean_rv, l_delta_inst_rv, arguments
