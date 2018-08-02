#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator rebound module.
"""
import numpy as np

import rebound

from logging import getLogger
from textwrap import dedent
from collections import defaultdict

# from copy import deepcopy
from numpy import concatenate, argsort, cumsum, array, append, sign
from astropy.constants import R_sun, au
import astropy.units as unt

from batman._quadratic_ld import _quadratic_ld

from .datasim_creator_rv import get_starmeanrv_and_deltarv
from .datasim_creator_lc import get_LD_parcont_and_param, get_ootvar
from .limb_darkening import (LinearLD, QuadraticLD, SquareRootLD, LogarithmicLD, ExponentialLD,
                             NonLinearLD)
from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.model.datasimulator_toolbox import (check_datasets_and_instmodels, add_param_argument,
                                                 get_has_datasets, par_vec_name,
                                                 init_arglist_paramnb_arguments_ldict,
                                                 get_lists_bijection_instcat, add_nonparam_argument,
                                                 add_argskwargs_argument, argskwargs)
from ...core.model.datasimulator_timeseries_toolbox import (add_time_argument, time_vec, l_time_vec,
                                                            time_ref, l_time_ref)
from ...exoplanet.dataset_and_instrument.lc import LC_inst_cat
from ...exoplanet.dataset_and_instrument.rv import RV_inst_cat
from ....tools.time_series_toolbox import get_time_supersampled, average_supersampled_values
from ....tools.convert import getecc_fast, getomega_fast, getMref_4_tic_fast, getecc_plc_4_handk_fast, getomega_plc_4_handk_fast

## Logger object
logger = getLogger()


# TODO: Implement Np parametrisation.


## Exposure time of Kepler long cadence
exptime_Kp_lc = 0.02043402778

## 1 day in seconds
day_sec = 86400.0

## Sun radius in meter
Rsun_meter = R_sun.value

## Astronomical unit in meter
au_meter = au.value

## Convert m.s-1 to km.s-1
ms2kms = 1e-3

## String used for the rv time vector
time_vec_rv = "{}_rv".format(time_vec)

## String used for the list of rv time vectors
l_time_vec_rv = "{}_rv".format(l_time_vec)

## String used for the rv time vector
time_vec_lc = "{}_lc".format(time_vec)

## String used for the list of lc time vectors
l_time_vec_lc = "{}_lc".format(l_time_vec)

## String used for the rv reference time
time_ref_rv = "{}_rv".format(time_ref)

## String used for the list of rv reference times
l_time_ref_rv = "{}_rv".format(l_time_ref)

## String used for the lc reference time
time_ref_lc = "{}_lc".format(time_ref)

## String used for the list of lc reference times
l_time_ref_lc = "{}_lc".format(l_time_ref)

## String used for the reference time of the dynamical model
time_ref_dyn = "{}_dyn".format(time_ref)

## String used for the time of step of the dynamical model
deltat_dyn = "dt_dyn"

## String used for the numbre of threads for the flux computation
nthreads = "nthreads"


## Dictionary giving the fonction to use to compute the flux for each LD models
def defaultdict_constructor():
    return {"name": None, "fct": None}


dico_compute_flux = defaultdict(None)
dico_compute_flux[QuadraticLD.__ld_type__] = {"name": "_quadratic_ld", "fct": _quadratic_ld}


# TODO: For now the LC_multis_parametrisations argument is not used
def create_datasimulator_rebound(gravgroup, key_whole, key_param, key_mand_kwargs,
                                 key_opt_kwargs, parametrisation,
                                 LC_multis_parametrisations, ldmodel4instmodfname, LDs,
                                 transit_model, SSE4instmodfname,
                                 RV_globalref_instname, RV_instref_modnames, RV_inst_db,
                                 inst_models=None, datasets=None,
                                 param_vector_name=par_vec_name):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    :param GravgroupDyn gravgroup: GravgroupDyn object
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
    :param string RV_globalref_instname: Name of the instrument used as global RV reference. All the
        Delta RV for the other instruments are relative to this instrument.
    :param dict_of_string RV_instref_modnames: Dictionary giving the name of the instrument model
        (not the full name) that is used has reference for this instrument. The other instrument
        models for this instrument will have an extra Delta RV relative to this instrument model.
    :param RV_inst_db:
    :param Instrument_Model inst_models: instance of Instrument_Model
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
    # Get the star and the planets out of the gravgroup object
    star = list(gravgroup.stars.values())[0]
    planets = gravgroup.planets

    # Check the content of inst_models argument. Give the list of instrument models (l_inst_model)
    # even just for one element and set instmod_docf for the Datasim_DocFunc.
    # Check the content of datasets argument: Give the list of datasets (l_dataset)
    # even just for one element and set dtsts_docf for the Datasim_DocFunc.
    # Set the list of instrument categories for the Datasim_DocFunc (instcat_docf)
    # Set multi indicating if multiple outputs are required for the datasimulator
    # Set the inst_model_full_name for the name of the function
    (l_dataset, l_inst_model, multi, inst_model_full_name, instcat_docf, instmod_docf,
     dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

    logger.debug("Datasim creator Rebound for : {}".format(inst_model_full_name))
    logger.debug("list of instrument categories: {}".format(instcat_docf))
    logger.debug("list of instrument models: {}".format(instmod_docf))
    logger.debug("list of datasets: {}".format(dtsts_docf))

    # Check if datasets are provided
    has_dataset = get_has_datasets(l_dataset)

    # Create the lists of RV and LC Datasets and Instrument_Models and detect if the datasim should
    # output RV or LC
    dico_inst_cat, l_output_retrieve = get_lists_bijection_instcat(l_dataset, l_inst_model,
                                                                   inst_cat=[LC_inst_cat,
                                                                             RV_inst_cat])
    logger.debug("dico_inst_cat: {}".format(dico_inst_cat))
    logger.debug("l_output_retrieve: {}".format(l_output_retrieve))

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
    # Create the "arguments" text variable and Initialize it with the parameter vector
    # Create and intialise the "ldict" dictionary variable which will be used as local dictionary
    # for the creation of the datasim functions with exec
    param_nb, arg_list, arguments, ldict = init_arglist_paramnb_arguments_ldict([key_whole],
                                                                                key_param,
                                                                                key_mand_kwargs,
                                                                                key_opt_kwargs,
                                                                                par_vec_name)

    # Initialise the template function text
    function_name = ("Reboundsim_{{object}}_{instmod_fullname}"
                     "".format(instmod_fullname=inst_model_full_name))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule}}
    {{tab}}return {{returns}}
    """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Dictionary which will store the name of the time argument if there is one
    time_arg_name = {}

    # Dictionary saying if an instrument category have multiple couple inst_model/dataset
    multi_cat = {}

    # Make specific preparation for LC modelling
    if dico_inst_cat[LC_inst_cat]["has"]:
        # See if there is multiple couple inst_model/dataset
        multi_cat[LC_inst_cat] = len(dico_inst_cat[LC_inst_cat]["l_inst_model"]) > 1
        # Add lc time as additional argument
        (arguments, time_arg_name[LC_inst_cat], time_arg_LC
         ) = add_time_argument(arguments, multi_cat[LC_inst_cat], has_dataset, arg_list, key_whole,
                               key_mand_kwargs,
                               key_opt_kwargs, ldict, dico_inst_cat[LC_inst_cat]["l_dataset"],
                               time_vec_name=time_vec_lc, l_time_vec_name=l_time_vec_lc,
                               add_to_ldict=False, backup_add_to_args=False)

        # Get the out of transit variation contribution for each couple instrument - dataset
        (dico_inst_cat[LC_inst_cat]["l_oot_var"],
         arguments
         ) = get_ootvar(dico_inst_cat[LC_inst_cat]["l_inst_model"],
                        dico_inst_cat[LC_inst_cat]["l_dataset"], multi_cat[LC_inst_cat],
                        ldict, arguments, param_nb, arg_list, key_whole,
                        key_param, key_mand_kwargs, key_opt_kwargs, time_vec_name=time_vec_lc,
                        l_time_vec_name=l_time_vec_lc,
                        timeref_name=time_ref_lc,
                        l_timeref_name=l_time_ref_lc)

        # Get the ld_parcont and ld_param_list
        (l_LD_parcont_name,
         dico_inst_cat[LC_inst_cat]["l_LD_parcont"],
         dico_inst_cat[LC_inst_cat]["l_ld_param_list"]
         ) = get_LD_parcont_and_param(dico_inst_cat[LC_inst_cat]["l_inst_model"],
                                      ldmodel4instmodfname, LDs,
                                      param_nb, arg_list, key_whole, key_param)

        # Get the supersampling factor and exposure time
        dico_inst_cat[LC_inst_cat]["supersamp"] = []
        dico_inst_cat[LC_inst_cat]["exptime"] = []

        for instmdl in dico_inst_cat[LC_inst_cat]["l_inst_model"]:
            dico_inst_cat[LC_inst_cat]["supersamp"].append(SSE4instmodfname.
                                                           get_supersamp(instmdl.full_name))
            dico_inst_cat[LC_inst_cat]["exptime"].append(SSE4instmodfname.
                                                         get_exptime(instmdl.full_name))

    # Make specific preparation for RV modelling
    if dico_inst_cat[RV_inst_cat]["has"]:
        # See if there is multiple couple inst_model/dataset
        multi_cat[RV_inst_cat] = len(dico_inst_cat[RV_inst_cat]["l_inst_model"]) > 1
        # Add rv time as additional argument
        (arguments, time_arg_name[RV_inst_cat], time_arg_RV
         ) = add_time_argument(arguments, multi_cat[RV_inst_cat], has_dataset, arg_list, key_whole,
                               key_mand_kwargs, key_opt_kwargs, ldict,
                               dico_inst_cat[RV_inst_cat]["l_dataset"],
                               time_vec_name=time_vec_rv, l_time_vec_name=l_time_vec_rv,
                               add_to_ldict=False, backup_add_to_args=False)

        # Get star mean rv and instrument delta rv contribution for each couple instrument - dataset
        (dico_inst_cat[RV_inst_cat]["l_star_mean_rv"],
         dico_inst_cat[RV_inst_cat]["l_delta_inst_rv"],
         arguments) = get_starmeanrv_and_deltarv(dico_inst_cat[RV_inst_cat]["l_inst_model"],
                                                 dico_inst_cat[RV_inst_cat]["l_dataset"], star,
                                                 multi_cat[RV_inst_cat], RV_globalref_instname,
                                                 RV_instref_modnames, RV_inst_db, ldict, arguments,
                                                 param_nb, arg_list, key_whole, key_param,
                                                 key_mand_kwargs, key_opt_kwargs,
                                                 time_vec_name=time_vec_rv,
                                                 l_time_vec_name=l_time_vec_rv,
                                                 timeref_name=time_ref_rv,
                                                 l_timeref_name=l_time_ref_rv)

    # Build the LC and RV times vector for the rebound wrapper
    # For RV and LC, add a key "times" to contain the full vector of sorted times
    # also add a key "l_times_retrieve" to contain the index of the time sample corresponding to
    # the each dataset times in the "l_dataset" key
    if has_dataset:
        format_supersamp_time_vec = ""
        l_times_retrieve = {}
        dico_times = {}
        tt = {}
        for cat, l_times_cat, times_cat in zip([LC_inst_cat, RV_inst_cat],
                                               [l_time_vec_lc, l_time_vec_rv],
                                               [time_vec_lc, time_vec_rv]):
            if dico_inst_cat[cat]["has"]:
                dico_inst_cat[cat]["times"] = array([])
                if multi_cat[cat]:
                    tt[cat] = []
                l_nb_times = []  # Nb of times samples in each dataset for l_times_retrieve
                for ii, dtst in enumerate(dico_inst_cat[cat]["l_dataset"]):
                    times = dtst.get_time()
                    if cat == LC_inst_cat:
                        supersamp = dico_inst_cat[cat]["supersamp"][ii]
                        exptime = dico_inst_cat[cat]["exptime"][ii]
                        if supersamp > 1:
                            times = get_time_supersampled(times, supersamp, exptime)
                    if multi_cat[cat]:
                        tt[cat].append(times)
                    else:
                        tt[cat] = times
                    l_nb_times.append(len(times))  # TODO: Below, maybe concatenate will be faster ?
                    dico_inst_cat[cat]["times"] = append(dico_inst_cat[cat]["times"], times)
                idx_tosorttime = argsort(dico_inst_cat[cat]["times"])
                idx_todesorttime = argsort(idx_tosorttime)
                dico_inst_cat[cat]["times"] = dico_inst_cat[cat]["times"][idx_tosorttime]
                dico_inst_cat[cat]["l_times_retrieve"] = []
                for low, up in zip(cumsum([0, ] + l_nb_times[:-1]), cumsum(l_nb_times)):
                    dico_inst_cat[cat]["l_times_retrieve"].append(idx_todesorttime[low:up])
                l_times_retrieve[cat] = dico_inst_cat[cat]["l_times_retrieve"]
                dico_times[cat] = dico_inst_cat[cat]["times"]
                if multi_cat[cat]:
                    ldict[l_times_cat] = tt[cat]
                else:
                    ldict[times_cat] = tt[cat]
        ldict["l_times_retrieve"] = l_times_retrieve
        ldict["dico_times"] = dico_times
    else:
        format_supersamp_time_vec = "{tab}dico_times = {{}}".format(tab=tab)
        if multi_cat.get(LC_inst_cat, False) or multi_cat.get(RV_inst_cat, False):
            format_supersamp_time_vec += "\n{tab}l_nb_times = {{}}".format(tab=tab)
            format_supersamp_time_vec += "\n{tab}l_times_retrieve = {{}}".format(tab=tab)
            ldict["array"] = array  # For the creation of dico_times[{cat}] array
            ldict["append"] = append  # For the append of dico_times[{cat}] times vectors
            ldict["cumsum"] = cumsum  # For the creation of l_times_retrieve
        do_supersamp = False  # True if at least one LC dataset requires supersampling
        for cat in [LC_inst_cat, RV_inst_cat]:
            if dico_inst_cat[cat]["has"]:
                if multi_cat[cat]:
                    format_supersamp_time_vec += ("\n{tab}dico_times['{cat}'] = array([])"
                                                  "".format(tab=tab, cat=cat))
                    format_supersamp_time_vec += ("\n{tab}l_nb_times['{cat}'] = []"
                                                  "".format(tab=tab, cat=cat))
                for ii, instmod in enumerate(dico_inst_cat[cat]["l_inst_model"]):
                    if multi_cat[cat]:
                        times_instmod = "{time_arg}[{ii}]".format(time_arg=time_arg_name[cat],
                                                                  ii=ii)
                    else:
                        times_instmod = "{time_arg}".format(time_arg=time_arg_name[cat])
                    if cat == LC_inst_cat:
                        supersamp = dico_inst_cat[cat]["supersamp"][ii]
                        exptime = dico_inst_cat[cat]["exptime"][ii]
                        if supersamp > 1:
                            do_supersamp = True
                            supersamp_time = """
{{tab}}time_supersamp_{ii} = get_time_supersampled({times_instmod}, {supersamp}, {exptime})
""".format(ii=ii, times_instmod=times_instmod, supersamp=supersamp, exptime=exptime)
                            format_supersamp_time_vec += dedent(supersamp_time).format(tab=tab)
                            final_time_instmod = "time_supersamp_{ii}".format(ii=ii)
                        else:
                            final_time_instmod = times_instmod
                    else:
                        final_time_instmod = times_instmod
                    if multi_cat[cat]:
                        text_nb_times = ("\n{tab}l_nb_times['{cat}'].append({final_time_instmod})"
                                         "").format(cat=cat, final_time_instmod=final_time_instmod,
                                                    tab=tab)
                        format_supersamp_time_vec += text_nb_times
                        text_append_times = ("\n{tab}dico_times['{cat}'] = append(dico_times"
                                             "['{cat}'], {final_time_instmod})"
                                             "").format(cat=cat, tab=tab,
                                                        final_time_instmod=final_time_instmod)
                        format_supersamp_time_vec += text_append_times
                    else:
                        format_supersamp_time_vec += ("\n{tab}dico_times['{cat}'] = {time_vec}"
                                                      "".format(tab=tab, cat=cat,
                                                                time_vec=final_time_instmod))
                if multi_cat[cat]:
                    format_supersamp_time_vec += ("\n{tab}idx_tosorttime_{cat} = "
                                                  "argsort(dico_times['{cat}'])".format(cat=cat,
                                                                                        tab=tab))
                    format_supersamp_time_vec += ("\n{tab}idx_todesorttime_{cat} = argsort"
                                                  "(idx_tosorttime_{cat})".format(cat=cat,
                                                                                  tab=tab))
                    format_supersamp_time_vec += ("\n{tab}dico_times['{cat}'] = dico_times['{cat}']"
                                                  "[idx_tosorttime_{cat}]".format(cat=cat,
                                                                                  tab=tab))
                    text_build_l_times_retrieve = """
{{tab}}for low, up in zip(cumsum([0, ] + l_nb_times['{cat}'][:-1]), cumsum(l_nb_times['{cat}'])):
{{tab}}   l_times_retrieve['{cat}'].append(idx_todesorttime_{cat}[low, up])
""".format(cat=cat)
                    format_supersamp_time_vec += dedent(text_build_l_times_retrieve).format(tab=tab)
            else:
                format_supersamp_time_vec += "\n{tab}dico_times['{cat}'] = None".format(tab=tab,
                                                                                        cat=cat)
        if do_supersamp:
            ldict["get_time_supersampled"] = get_time_supersampled  # for supersampling

    ## Prepare the text for the stellar mass and radius parameter
    star.M.unit = unt.M_sun
    M_star = add_param_argument(star.M, arg_list, key_whole, key_param, param_nb,
                                par_vec_name)[key_whole]
    if dico_inst_cat[LC_inst_cat]["has"]:
        R_star_name = "R_star"
        R_star_def = "{} = {} * Rsun_meter / au_meter"
        ldict["Rsun_meter"] = Rsun_meter
        ldict["au_meter"] = au_meter
        star.R.unit = unt.R_sun
        R_star_def = R_star_def.format(R_star_name,
                                       add_param_argument(star.R, arg_list, key_whole, key_param,
                                                          param_nb, par_vec_name)[key_whole])
    else:
        R_star_def = ""

    ## Prepare the vector of parameters param_planets for the rebound function
    ## And if LC simulation the planetary radius vector.
    ## TODO: Part of this could be a function of datasimulator toolbox which create a text,
    ##       for example "p[0], p[3]", from a list of parameter instances.

    # If LC, create the text vector of planetary radius ratios
    if dico_inst_cat[LC_inst_cat]["has"]:
        R_planet_list_name = "rp"
        text_param_rp = "{} = [".format(R_planet_list_name)
        for planet in planets.values():
            text_param_rp += add_param_argument(planet.parameters["Rrat"], arg_list, key_whole,
                                                key_param, param_nb, par_vec_name)[key_whole] + ", "
        text_param_rp = text_param_rp[:-2] + "]"

    # Create the text to convert the jumping parameters into arguments for the rebound wrapper.
    # Create the text of the list of rebound wrapper arguments.

    param_conv = ""
    param_planets_reb = "["
    if parametrisation == "Standard":
        template_param_conv = """
        {{tab}}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {{tab}}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {{tab}}MeanAnomaly_{planet} = getMref_4_tic_fast({tic}, {P}, ecc_{planet}, omega_{planet}, {t_ref})
        """
        template_param_conv = dedent(template_param_conv)
        ldict["getecc_fast"] = getecc_fast
        ldict["getomega_fast"] = getomega_fast
        ldict["getMref_4_tic_fast"] = getMref_4_tic_fast
        params_whole = {}
        for planet in planets.values():
            l_param = [planet.M, planet.P, planet.secosw, planet.sesinw, planet.inc, planet.OMEGA,
                       planet.tic]
            for param in l_param:
                params_whole[param.name] = add_param_argument(param, arg_list, key_whole, key_param,
                                                              param_nb, par_vec_name)[key_whole]
            param_conv += template_param_conv.format(planet=planet.name, secosw=params_whole["secosw"],
                                                     sesinw=params_whole["secosw"], tic=params_whole["tic"],
                                                     t_ref=time_ref_dyn)
            param_planets_reb += ", ".join([params_whole["M"], params_whole["P"], "ecc_{}".format(planet.name),
                                            params_whole["inc"], params_whole["OMEGA"], "omega_{}".format(planet.name),
                                            "MeanAnomaly_{}".format(planet.name)])
            param_planets_reb += ", "
        param_planets_reb = param_planets_reb[:-2] + "]"
    elif parametrisation == "Np":
        template_param_conv_gravgroup = """
        {{tab}}M_{planets[0]} = ({qplus} * {M_star}) / (1 + {qp})
        {{tab}}M_{planets[1]} = {qp} * M_{planets[0]}
        {{tab}}ecc_{planets[0]} = getecc_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus}, {P_1}/{P_0})
        {{tab}}ecc_{planets[1]} = getecc_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
        {{tab}}omega_{planets[0]} = getomega_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
        {{tab}}omega_{planets[1]} = getomega_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
        """
        template_param_conv_gravgroup = dedent(template_param_conv_gravgroup)
        ldict["getecc_plb_4_handk_fast"] = getecc_plb_4_handk_fast
        ldict["getecc_plc_4_handk_fast"] = getecc_plc_4_handk_fast
        ldict["getomega_plb_4_handk_fast"] = getomega_plb_4_handk_fast
        ldict["getomega_plc_4_handk_fast"] = getomega_plc_4_handk_fast
        template_param_conv_pl = """
        {{tab}}MeanAnomaly_{planet} = getMref_4_tic_fast({tic}, {P}, ecc_{planet}, omega_{planet}, {t_ref})
        """
        template_param_conv_pl = dedent(template_param_conv_pl)
        ldict["getMref_4_tic_fast"] = getMref_4_tic_fast
        param_gravgroup = {}
        l_param_gravgroup = [gravgroup.qplus, gravgroup.qp, gravgroup.hplus, gravgroup.hminus, gravgroup.kplus, gravgroup.kminus])
        for param in l_param_gravgroup:
            param_gravgroup[param.name] = add_param_argument(param, arg_list, key_whole, key_param,
                                                             param_nb, par_vec_name)[key_whole]
        param_pl = {}
        for planet in planets.values:
            param_pl[planet.name] = {}
            l_param_pl = [planet.P, planet.tic, planet.inc, planet.OMEGA]
            for param in l_param_pl:
                param_pl[planet.name][param.name] = add_param_argument(param, arg_list, key_whole, key_param,
                                                                       param_nb, par_vec_name)[key_whole]
            param_conv += template_param_conv_pl.format(planet=planet.name, tic=param_pl[planet.name]["tic"], P=param_pl[planet.name]["P"],
                                                        t_ref=time_ref_dyn)
            param_planets_reb += ", ".join(["M_{}".format(planet.name, param_pl[planet.name]["P"], "ecc_{}".format(planet.name),
                                            param_pl[planet.name]["inc"], param_pl[planet.name]["OMEGA"], "omega_{}".format(planet.name),
                                            "MeanAnomaly_{}".format(planet.name)])
        planet_names = [planet.name for planet in planets.values()]
        param_conv += template_param_conv_gravgroup.format(planets=planet_names, qplus=param_gravgroup["qplus"], qplus=param_gravgroup["qp"],
                                                           M_star=M_star, hplus=param_gravgroup["hplus"], hminus=param_gravgroup["hminus"],
                                                           kplus=param_gravgroup["kplus"], kminus=param_gravgroup["kminus"],
                                                           P_0=param_pl[planet_names[0]]["P"], P_1=param_pl[planet_names[1]]["P"])

    # Add the reference time for the dynamical simulation as argument
    (arguments, timeref_arg
     ) = add_nonparam_argument(arguments, time_ref_dyn, arg_list, key_whole, key_mand_kwargs,
                               key_opt_kwargs, ldict, add_to_ldict=False, new_arg_value=None,
                               def_arg_value=None)

    # Add the time step for the dynamical simulation as argument
    (arguments, deltadyn_arg
     ) = add_nonparam_argument(arguments, deltat_dyn, arg_list, key_whole, key_mand_kwargs,
                               key_opt_kwargs, ldict, add_to_ldict=False, new_arg_value=None,
                               def_arg_value=0.01)

    ## Create the template for the text of the rebound wrapper and add the rebound wrapper function
    ## to ldict
    returns_rebound_wrap = ""
    if dico_inst_cat[LC_inst_cat]["has"] and dico_inst_cat[RV_inst_cat]["has"]:
        returns_rebound_wrap += "rr, zz, rvs"
    elif dico_inst_cat[LC_inst_cat]["has"]:
        returns_rebound_wrap += "rr, zz"
    else:
        returns_rebound_wrap += "rvs"
    text_rebound_wrap = """
        {{tab}}{returns} = rebound_wrap_r_z_vz({param_planets}, {M_star}, {timeref_dyn},
        {{tab}}                                dt={dt_dyn}, lc_times={time_vec_lc},
        {{tab}}                                rv_times={time_vec_rv})
        """.format(returns=returns_rebound_wrap, param_planets=param_planets_reb, M_star=M_star,
                   timeref_dyn=time_ref_dyn, dt_dyn=deltat_dyn,
                   time_vec_lc="dico_times['{}']".format(LC_inst_cat),
                   time_vec_rv="dico_times['{}']".format(RV_inst_cat))
    text_rebound_wrap = dedent(text_rebound_wrap).format(tab=tab)
    ldict["rebound_wrap_r_z_vz"] = rebound_wrap_r_z_vz
    if has_dataset:  # Add to ldict the times formatted for the rebound wrapper if has_dataset.
        for cat in [LC_inst_cat, RV_inst_cat]:
            if dico_inst_cat[cat]["has"]:
                ldict["dico_times[{}]".format(cat)] = dico_inst_cat[cat]["times"]

    template_prembule = """
    {format_and_supersamp_time}
    {param_conv}
    {rebound_wrap}
    {init_res}
    {compute_flux}
    {desupersamp_time}
    {retrieve_rv}
    """
    template_prembule = dedent(template_prembule)

    ## text to initialise the result
    res_name = "res"
    if multi:
        text_init_res = ("{tab}{res_name} = [nan] * {nb_res}\n"
                         "".format(tab=tab, res_name=res_name, nb_res=len(l_inst_model)))
        ldict["nan"] = np.nan
    else:
        text_init_res = ""

    ## Compute flux values
    text_compute_flux = ""
    if dico_inst_cat[LC_inst_cat]["has"]:
        # Retrieve the rr and zz values corresponding to each LC instrument model (and dataset)
        # Using the correct limb darkening law compute the flux from rr and zz and the LDC values
        text_compute_flux += "{{tab}}{Rstar_def}".format(Rstar_def=R_star_def)
        text_compute_flux += "\n{tab}" + text_param_rp
        for (idx_LC, ld_param_list, LD_parcont, supersamp, oot_var, index_res
             ) in zip(range(len(dico_inst_cat[LC_inst_cat]["l_inst_model"])),
                      dico_inst_cat[LC_inst_cat]["l_ld_param_list"],
                      dico_inst_cat[LC_inst_cat]["l_LD_parcont"],
                      dico_inst_cat[LC_inst_cat]["supersamp"],
                      dico_inst_cat[LC_inst_cat]["l_oot_var"],
                      dico_inst_cat[LC_inst_cat]["l_index"]):
            compute_flux_fct_name = dico_compute_flux[LD_parcont.ld_type]["name"]
            compute_flux_fct = dico_compute_flux[LD_parcont.ld_type]["fct"]
            if multi:
                res = "{res_name}[{index_res}]".format(res_name=res_name, index_res=index_res)
            else:
                res = res_name
            if compute_flux_fct_name is None:
                raise ValueError("For now {} LD model is not included !".format(LD_parcont.ld_type))
            else:
                ldict[compute_flux_fct_name] = compute_flux_fct
            if multi_cat.get(LC_inst_cat, False):
                projected_dist = ("rr[l_times_retrieve['{cat}'][{idx_LC}], jj] / {R_star_name}"
                                  "".format(cat=LC_inst_cat, idx_LC=idx_LC,
                                            R_star_name=R_star_name))
                zz = ("zz[l_times_retrieve['{cat}'][{idx_LC}], jj]"
                      "".format(cat=LC_inst_cat, idx_LC=idx_LC))
            else:
                projected_dist = ("rr[:, jj] / {R_star_name}"
                                  "".format(R_star_name=R_star_name))
                zz = "zz[:, jj]"
            # If zz is negative (the planet is behind the star) we articiacial augment a lot the
            # projected distance to avoid having a transit during the secondary
            compute_flux = """
{{tab}}{res} = 1 {oot_var}
{{tab}}for jj in range(0, {nb_planet}):
{{tab}}    dist_{idx_LC} = {projected_dist} + 1e28 * (1-sign({zz}))
{{tab}}    {res} += {flux_fct_name}(dist_{idx_LC}, {R_planet_vec_name}[jj],
{{tab}}                             {ld_param_list}, nthreads) - 1
""".format(res=res, nb_planet=len(planets), flux_fct_name=compute_flux_fct_name,
           projected_dist=projected_dist, R_planet_vec_name=R_planet_list_name,
           ld_param_list=ld_param_list.strip()[1:-1].strip(" ,"),
           oot_var=oot_var, idx_LC=idx_LC, zz=zz)
            text_compute_flux += compute_flux
            ldict["sign"] = sign
            if supersamp > 1:
                supersamp_text = """
{{tab}}{res} = average_supersampled_values({res}, {supersamp})
""".format(res=res, supersamp=supersamp)
                text_compute_flux += supersamp_text
                ldict["average_supersampled_values"] = average_supersampled_values

        text_compute_flux = dedent(text_compute_flux).format(tab=tab)

        # Add nthreads as argument with def value = 1
        (arguments, nthreads_arg
         ) = add_nonparam_argument(arguments, nthreads, arg_list, key_whole, key_mand_kwargs,
                                   key_opt_kwargs, ldict, add_to_ldict=False, new_arg_value=None,
                                   def_arg_value=1)

    ## Retrieve the RV values for each RV instrument model (and dataset)
    text_retrieve_rv = ""
    if dico_inst_cat[RV_inst_cat]["has"]:
        for (idx_RV,
             star_mean_rv,
             delta_inst_rv,
             index_res) in zip(range(len(dico_inst_cat[RV_inst_cat]["l_inst_model"])),
                               dico_inst_cat[RV_inst_cat]["l_star_mean_rv"],
                               dico_inst_cat[RV_inst_cat]["l_delta_inst_rv"],
                               dico_inst_cat[RV_inst_cat]["l_index"]):
            if multi:
                res = "{res_name}[{index_res}]".format(res_name=res_name, index_res=index_res)
            else:
                res = res_name
            if multi_cat[RV_inst_cat]:
                text_retrieve_rv += """
            {{tab}}{res} = {delta_inst_rv} {star_mean_rv} + rvs[l_times_retrieve['{cat}'][{idx_RV}]]
            """.format(res=res, star_mean_rv=star_mean_rv, delta_inst_rv=delta_inst_rv,
                       cat=RV_inst_cat, idx_RV=idx_RV)
            else:
                text_retrieve_rv += """
            {{tab}}{res} = {delta_inst_rv} {star_mean_rv} + rvs
            """.format(res=res, star_mean_rv=star_mean_rv, delta_inst_rv=delta_inst_rv)
        text_retrieve_rv = dedent(text_retrieve_rv).format(tab=tab)

    ## Create the datasim function
    text_preambule = template_prembule.format(format_and_supersamp_time=format_supersamp_time_vec,
                                              param_conv=param_conv,
                                              rebound_wrap=text_rebound_wrap,
                                              init_res=text_init_res,
                                              compute_flux=text_compute_flux, desupersamp_time="",
                                              retrieve_rv=text_retrieve_rv,
                                              # returns="",
                                              tab=tab
                                              )
    arguments = add_argskwargs_argument(arguments)
    text_def_func = template_function.format(object=key_whole,
                                             tab=tab,
                                             arguments=arguments,
                                             preambule=text_preambule,
                                             returns="res")
    logger.debug("text of Rebound simulator function for {instmod_fullname}:\n{text_func}"
                 "".format(object=key_whole, instmod_fullname=inst_model_full_name,
                           text_func=text_def_func))

    exec(text_def_func, ldict)
    params_model = arg_list[key_whole][key_param]
    if len(arg_list[key_whole][key_mand_kwargs]) > 0:
        mand_kwargs = str(arg_list[key_whole][key_mand_kwargs])
    else:
        mand_kwargs = None
    if len(arg_list[key_whole][key_opt_kwargs]) > 0:
        opt_kwargs = str(arg_list[key_whole][key_opt_kwargs])
    else:
        opt_kwargs = None
    dico_docf = {}
    dico_docf[key_whole] = DatasimDocFunc(function=ldict[function_name.format(object=key_whole)],
                                          params_model=params_model,
                                          inst_cat=instcat_docf,
                                          mand_kwargs=mand_kwargs,
                                          include_dataset_kwarg=has_dataset,
                                          opt_kwargs=opt_kwargs,
                                          inst_model_fullname=instmod_docf,
                                          dataset=dtsts_docf)
    return dico_docf


def funrebound(param_planet, stellar_mass, stellar_radius, limb_dark, treference,
               dt=0.01, supersamp=1, exptime=exptime_Kp_lc, lc_times=None, rv_times=None,
               nthreads=1):
    """
    Get the photodynamical model for photometry and/or radial velocity points.

    FUNCTION USED AS EXAMPLE FOR THE DEVELOPMENT BUT NOT USED ANYMORE.

    Multiplanets transits are ok unless the planets pass in front of each other.
    All masses are in units of M_sun, all times are in days, all angles are in radians, all lenghts
    are in AU.

    :param Iterable param_planet: Planets parameters at the reference time (treference) in this
        order: mass [M_sun], period [days], eccentricity, inclination [radians],
        Long of the ascending node (Omega) [radians], Argument of periastron (omega) [radians],
        Mean Anomaly (M) [radian] and radius in stellar units (rp/rs)
        repeated for each planet. The length of param_planets is thus nplanets * 8. Any number of
        planets is allowed.
    :param float stellar_mass: Stellar mass [M_sun]
    :param float stellar_radius: Stellar radius in solar radius
    :param Iterable limb_dark: Iterable with two element, the two coefficients of the quadratic LD
        limd darkening law.
    :param float treference: Time at which the parameters are given
    :param float dt: Time step for the integration [days]. Should be < 1/20 of shortest planetary
        orbit
    :param int supersamp: Super sampling factor to apply (>= 1)
    :param float exptime: Exposure time of the time vector, in the same unit than the other time
        values like dt [days].
    :param Iterable_of_float lc_times: Times at which you want the function to output simulated
        values of the light-curve. If None, no values are outputed. Same unit than dt [days].
    :param Iterable_of_float rv_times: Times at which you want the function to output simulated
        values of the radial velocity curve. Same unit than dt [days].
    :param int nthreads: Number of threads for parrallel computing of the batman _quadratic_ld
        function.
    :return : when both are given the output is [lcmodel, rvmodel]. model of photometry normalised
        or/ and  model of the radial velocity (m/s) for the times requested

    TODO:
    transitpy not working
    """
    # Convert stellar radius from solar radius to astronomical unit
    rstar = stellar_radius * Rsun_meter / au_meter

    u = limb_dark

    ## Get the time at which rebound will have to provide the outputs
    # If simulated times for the light-curve are required, ...
    if lc_times is not None:
        # ..., store those times in ltimes and supersample them if necessary
        if supersamp > 1:
            ltimes = get_time_supersampled(lc_times, supersamp, exptime)
        else:
            ltimes = lc_times
        np_lc = len(ltimes)

    # If simulated times for the radial velocity curve are required, ...
    if rv_times is not None:
        # ..., store those times in ltimes too
        # but if simulated times for the light-curve have also been requested, ...
        if lc_times is not None:
            # concatenate the two times vector with the light-curve one first
            ttimes = concatenate((ltimes, rv_times))
            # Get the index that would allow you to sorte this time vector (for rebound as sorted
            # time vector is better)
            sorte = argsort(ttimes)
            # get where were each times sample in the sorted time vector in the intial time vector
            ffsorte = argsort(sorte)
            # get the index corresponding to the lc and rv in the sorted time vectors
            sorte_lc = ffsorte[:np_lc]
            sorte_rv = ffsorte[np_lc:]
            # Actually sort the time vector
            ltimes = ttimes[sorte]
        else:
            ltimes = rv_times

    # calculate the number of planets
    # Mplanet Period E I Omega omega Meananomaly, radius ratio
    nplanets = np.int(len(param_planet) / 8.0)
    npoints = len(ltimes)

    rp = np.zeros(nplanets)

    sim = rebound.Simulation()
    sim.integrator = 'whfast'  # 'ias15'
    sim.t = treference
    sim.units = ('d', 'AU', 'Msun')
    # sim.dt = stepdt # Sets the timestep (will change for adaptive integrators such as IAS15).
    sim.dt = dt
    m0 = stellar_mass

    # Add a star
    sim.add(m=m0)

    # Add planets
    for jj in range(0, nplanets):
        sim.add(m=param_planet[0 + jj * 8], P=param_planet[1 + jj * 8], e=param_planet[2 + jj * 8],
                inc=param_planet[3 + jj * 8], Omega=param_planet[4 + jj * 8],
                omega=param_planet[5 + jj * 8], M=param_planet[6 + jj * 8],
                primary=sim.particles[0])
        # get radius ratio
        rp[jj] = param_planet[7 + jj * 8]

    # sim.status()

    # moves to centre of momentum
    sim.move_to_com()
    particles = sim.particles

    # add rvs and fluxes
    distance = np.zeros((npoints, nplanets), dtype=float)
    rvs = np.zeros_like(ltimes)
    for ii, time in enumerate(ltimes):
        sim.integrate(time, exact_finish_time=1)
        for jj in range(0, nplanets):  # TODO: Only compute for lc_times
            distance[ii, jj] = np.sqrt((particles[jj + 1].x - particles[0].x)**2 +
                                       (particles[jj + 1].y - particles[0].y)**2)

        rvs[ii] = particles[0].vz * au_meter / day_sec  # TODO: Only compute for rv_times

    # separate rvs and flux
    if lc_times is not None:
        mflux = _quadratic_ld(distance[:, 0] / rstar, rp[0], u[0], u[1], nthreads)
        for jj in range(1, nplanets):
            mflux = mflux + _quadratic_ld(distance[:, jj] / rstar, rp[jj], u[0], u[1], nthreads) - 1
    else:
        return rvs

    if rv_times is not None:
        sortflux = mflux[sorte_lc]  # TODO: If we only compute flux and rvs for the required time
        sortrvs = rvs[sorte_rv]     # This is not needed anymore.
        if supersamp > 1:
            totalflux = average_supersampled_values(sortflux, supersamp)
        else:
            totalflux = sortflux
        return [totalflux, sortrvs]
    else:
        if supersamp > 1:
            totalflux = average_supersampled_values(mflux, supersamp)
        else:
            totalflux = mflux
        return totalflux


def rebound_wrap_r_z_vz(param_planet, stellar_mass, treference, dt=0.01, supersamp=1,
                        exptime=exptime_Kp_lc, lc_times=None, rv_times=None):
    """Return the projected distance, z coordinate and/or radial velocities.

    :param Iterable param_planet: Planets parameters at the reference time (treference) in this
        order: mass [M_sun], period [days], eccentricity, inclination [radians],
        Long of the ascending node (Omega) [radians], Argument of periastron (omega) [radians],
        and Mean Anomaly (M) [radian].
        repeated for each planet. The length of param_planets is thus nplanets * 8. Any number of
        planets is allowed.
    :param float stellar_mass: Stellar mass [M_sun]
    :param float treference: Time at which the parameters are given
    :param float dt: Time step for the integration [days]. Should be < 1/20 of shortest planetary
        orbit
    :param int supersamp: Super sampling factor to apply (>= 1)
    :param float exptime: Exposure time of the time vector, in the same unit than the other time
        values like dt [days].
    :param Iterable_of_float lc_times: Times at which you want the function to output simulated
        values of the light-curve. If None, no values are outputed. Same unit than dt [days].
    :param Iterable_of_float rv_times: Times at which you want the function to output simulated
        values of the radial velocity curve. Same unit than dt [days].
    :return np.darray rr: 2 dimension (N, P) ndarray giving the sky-projected distance between the
        star and each planet in the system. N is the number of time sample requested in lc_times.
        P is the number of planets. Only ouputed if lc_times is provided.
    :return np.array zz: 2 dimension (N, P) ndarray giving the position of each planet in the system
        relative to the star. N is the number of time sample requested in lc_times.
        P is the number of planets. Only ouputed if lc_times is provided.
    :return np.array rvs: 1 dimension (N) ndarray giving the radial velocity of the star
        (in km.s-1). N is the the number of time sample requested in rv_times.
        Only ouputed if rv_times is provided.
    """
    ## Get the time at which rebound will have to provide the outputs (ltimes)
    # If simulated times for the light-curve are required, ...
    if lc_times is not None:
        # ..., store those times in ltimes and supersample them if necessary
        if supersamp > 1:
            ltimes = get_time_supersampled(lc_times, supersamp, exptime)
        else:
            ltimes = lc_times
        np_lc = len(lc_times)
        lc_or_rv = [True for ii in range(np_lc)]

    # If simulated times for the radial velocity curve are required, ...
    if rv_times is not None:
        # ..., store those times in ltimes too
        # but if simulated times for the light-curve have also been requested, ...
        np_rv = len(rv_times)
        if lc_times is not None:
            # concatenate the two times vector with the light-curve one first
            ttimes = concatenate((ltimes, rv_times))
            lc_or_rv = concatenate((lc_or_rv, [False for ii in range(len(rv_times))]))
            # Get the index that would allow you to sorte this time vector (for rebound as sorted
            # time vector is better)
            sorte = argsort(ttimes)
            # get where were each times sample in the sorted time vector in the intial time vector
            # ffsorte = argsort(sorte)
            # get the index corresponding to the lc and rv in the sorted time vectors
            # sorte_lc = ffsorte[:np_lc]
            # sorte_rv = ffsorte[np_lc:]
            # Actually sort the time vector
            ltimes = ttimes[sorte]
            lc_or_rv = lc_or_rv[sorte]
        else:
            ltimes = rv_times
            lc_or_rv = [False for ii in range(len(ltimes))]

    # calculate the number of planets
    # Mplanet Period E I Omega omega Meananomaly, radius ratio
    nplanets = np.int(len(param_planet) / 7.0)
    # npoints = len(ltimes)

    sim = rebound.Simulation()
    sim.integrator = 'whfast'  # 'ias15'
    sim.t = treference
    sim.units = ('d', 'AU', 'Msun')
    # sim.dt = stepdt # Sets the timestep (will change for adaptive integrators such as IAS15).
    sim.dt = dt

    # Add a star
    sim.add(m=stellar_mass)

    # Add planets
    for jj in range(0, nplanets):
        sim.add(m=param_planet[0 + jj * 7], P=param_planet[1 + jj * 7], e=param_planet[2 + jj * 7],
                inc=param_planet[3 + jj * 7], Omega=param_planet[4 + jj * 7],
                omega=param_planet[5 + jj * 7], M=param_planet[6 + jj * 7],
                primary=sim.particles[0])

    # sim.status()

    # moves to centre of momentum
    sim.move_to_com()
    particles = sim.particles

    # add rvs and fluxes
    if lc_times is not None:
        rr = np.zeros((np_lc, nplanets), dtype=float)
        zz = np.zeros((np_lc, nplanets), dtype=float)
        ii_lc = 0
    if rv_times is not None:
        rvs = np.zeros((np_rv))
        ii_rv = 0
    for ii, time in enumerate(ltimes):
        sim.integrate(time, exact_finish_time=1)
        if lc_or_rv[ii]:
            for jj in range(0, nplanets):
                rr[ii_lc, jj] = np.sqrt((particles[jj + 1].x - particles[0].x)**2 +
                                        (particles[jj + 1].y - particles[0].y)**2)
                zz[ii_lc, jj] = (particles[jj + 1].z - particles[0].z)
            ii_lc += 1
        else:
            rvs[ii_rv] = particles[0].vz * au_meter / day_sec
            ii_rv += 1

    # separate rvs and flux
    # if lc_times is not None:
    #     mflux = _quadratic_ld(distance[:, 0] / rstar, rp[0], u[0], u[1], nthreads)
    #     for jj in range(1, nplanets):
    #         mflux = (mflux +
    #                  _quadratic_ld(distance[:, jj] / rstar, rp[jj], u[0], u[1], nthreads) -
    #                  1)
    # else:
    #     return rvs
    #
    # if rv_times is not None:
    #     sortflux = mflux[sorte_lc]  # TODO: If we only compute flux and rvs for the required time
    #     sortrvs = rvs[sorte_rv]     # This is not needed anymore.
    #     if supersamp > 1:
    #         totalflux = average_supersampled_values(sortflux, supersamp)
    #     else:
    #         totalflux = sortflux
    #     return [totalflux, sortrvs]
    # else:
    #     if supersamp > 1:
    #         totalflux = average_supersampled_values(mflux, supersamp)
    #     else:
    #         totalflux = mflux
    #     return totalflux

    if (lc_times is not None) and (rv_times is not None):
        return rr, zz, rvs * ms2kms
    elif (lc_times is not None):
        return rr, zz
    elif (rv_times is not None):
        return rvs * ms2kms
    else:
        raise ValueError("You have to provide at least one parameter amongst lc_times and rv_times")


def photodynam(param_planet, stellar_mass, stellar_radius, limb_dark, treference,
               dt=0.01, supersamp=1, exptime=exptime_Kp_lc, lc_times=None, rv_times=None,
               nthreads=1):
    """
    Get the photodynamical model for photometry and/or radial velocity points.

    Multiplanets transits are ok unless the planets pass in front of each other.
    All masses are in units of M_sun, all times are in days, all angles are in radians, all lenghts
    are in AU.

    :param Iterable param_planet: Planets parameters at the reference time (treference) in this
        order: mass [M_sun], period [days], eccentricity, inclination [radians],
        Long of the ascending node (Omega) [radians], Argument of periastron (omega) [radians],
        and radius in stellar units (rp/rs)
        repeated for each planet. The length of param_planets is thus nplanets * 8. Any number of
        planets is allowed.
    :param float stellar_mass: Stellar mass [M_sun]
    :param float stellar_radius: Stellar radius in solar radius
    :param Iterable limb_dark: Iterable with two element, the two coefficients of the quadratic LD
        limd darkening law.
    :param float treference: Time at which the parameters are given
    :param float dt: Time step for the integration [days]. Should be < 1/20 of shortest planetary
        orbit
    :param int supersamp: Super sampling factor to apply (>= 1)
    :param float exptime: Exposure time of the time vector, in the same unit than the other time
        values like dt [days].
    :param Iterable_of_float lc_times: Times at which you want the function to output simulated
        values of the light-curve. If None, no values are outputed. Same unit than dt [days].
    :param Iterable_of_float rv_times: Times at which you want the function to output simulated
        values of the radial velocity curve. Same unit than dt [days].
    :param int nthreads: Number of threads for parrallel computing of the batman _quadratic_ld
        function.
    :return : when both are given the output is [lcmodel, rvmodel]. model of photometry normalised
        or/ and  model of the radial velocity (m/s) for the times requested

    TODO:
    transitpy not working
    """
    if (lc_times is not None) and (rv_times is not None):
        rr, zz, rvs = rebound_wrap_r_z_vz(param_planet, stellar_mass, treference, dt, supersamp,
                                          exptime, lc_times, rv_times)
    elif lc_times is not None:
        rr, zz = rebound_wrap_r_z_vz(param_planet, stellar_mass, treference, dt, supersamp,
                                     exptime, lc_times, rv_times)
    elif rv_times is not None:
        rvs = rebound_wrap_r_z_vz(param_planet, stellar_mass, treference, dt, supersamp,
                                  exptime, lc_times, rv_times)
    else:
        raise ValueError("You have to provide at least one parameter amongst lc_times and rv_times")

    if lc_times is not None:
        # Convert stellar radius from solar radius to astronomical unit
        rstar = stellar_radius * Rsun_meter / au_meter

        # calculate the number of planets
        # Mplanet Period E I Omega omega Meananomaly, radius ratio
        nplanets = np.int(len(param_planet) / 8.0)

        flux = 1.
        for jj in range(0, nplanets):
            flux += _quadratic_ld(rr[:, jj] / rstar, param_planet[7 + jj * 8],
                                  limb_dark[0], limb_dark[1], nthreads) - 1

    if (lc_times is not None) and (rv_times is not None):
        return flux, rvs
    elif lc_times is not None:
        return flux
    elif rv_times is not None:
        return rvs


def update_arguments_photodynam(arguments, multi, has_dataset, has_LC, has_RV, arg_list, key_whole,
                                key_kwargs,
                                time_vec=time_vec, l_time_vec=l_time_vec,
                                time_ref=time_ref, l_time_ref=l_time_ref):
    """
    """
    # Create the arguments text and add the time in the kwargs entry of the whole system arg_list
    if multi:
        if not has_dataset:
            if has_LC:
                arguments += ", l_t_lc, l_tref_lc"
                arg_list[key_whole][key_kwargs].append("l_t_lc")
            if has_RV:
                arguments += ", l_t_rv, l_tref_rv"
                arg_list[key_whole][key_kwargs].append("l_t_rv")
    else:
        if not has_dataset:
            if has_LC:
                arguments += ", t_lc, tref_lc=None"
                arg_list[key_whole][key_kwargs].append("t_lc")
            if has_RV:
                arguments += ", t_rv, tref_rv=None"
                arg_list[key_whole][key_kwargs].append("t_rv")
    return arguments


def update_ldict_photodynam(ldict, multi, has_dataset, l_dataset,
                            time_vec=time_vec, l_time_vec=l_time_vec,
                            time_ref=time_ref, l_time_ref=l_time_ref):
    """Update the local dictionary for datasim of time series.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    It should also be called after init_ldict since it uses its output.

    :param dict ldict: dictionary to be used as local dictionary argument of the exec
        function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param bool multi: True if the datasimulator simulate multiple outputs
    :param bool has_dataset: True if the datasimulator should includes datasets values
    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s) or None.
    """
    # if datasets are provided add the time array and tref to the local dictionary
    if has_dataset:
        if multi:
            l_t = []
            l_tref = []
            for dst in zip(l_dataset):
                l_t.append(dst.get_time())
                l_tref.append(dst.get_tref())
            ldict[l_time_vec] = l_t
            ldict[l_time_ref] = l_tref
        else:
            ldict[time_vec] = l_dataset[0].get_time()
            ldict[time_ref] = l_dataset[0].get_tref()
