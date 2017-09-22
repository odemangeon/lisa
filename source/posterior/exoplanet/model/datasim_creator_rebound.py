#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator rebound module.
"""
import numpy as np

import rebound

from logging import getLogger
from textwrap import dedent
from collections import OrderedDict
from copy import deepcopy
from numpy import concatenate, argsort, cumsum
from astropy.constants import R_sun, au

from batman._quadratic_ld import _quadratic_ld

from .datasim_creator_rv import get_starmeanrv_and_deltarv
from ...core.model.datasimulator import check_datasets_and_instmodels
from ...core.dataset_and_instrument.lc import LC_inst_cat
from ...core.dataset_and_instrument.rv import RV_inst_cat
from ....tools.emcee_tools import get_time_supersampled, average_supersampled_values


## Logger object
logger = getLogger()

## Exposure time of Kepler long cadence
exptime_Kp_lc = 0.02043402778

## 1 day in seconds
day_sec = 86400.0

## Sun radius in meter
Rsun_meter = R_sun.value

## Astronomical unit in meter
au_meter = au.value


def create_datasimulator_rebound(star, planets, key_whole, key_param, key_kwargs,
                                 parametrisation,
                                 LC_multis_parametrisations, ldmodel4instmodfname, LDs,
                                 transit_model, SSE4instmodfname,
                                 RV_globalref_instname, RV_instref_modnames, RV_inst_db,
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
    :param string RV_globalref_instname: Name of the instrument used as global RV reference. All the
        Delta RV for the other instruments are relative to this instrument.
    :param dict_of_string RV_instref_modnames: Dictionary giving the name of the instrument model
        (not the full name) that is used has reference for this instrument. The other instrument
        models for this instrument will have an extra Delta RV relative to this instrument model.
    :param RV_inst_db:
    :param Instrument_Model inst_models: instance of Instrument_Model
    :param Dataset datasets: instance of Dataset

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
    #   - "param": list of the free parameters name in order
    #   - "kwargs": list of the additional argument taht you need to provide to simulate the
    #               data. For example the time
    arg_list = {}

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

    # Initialise the template for each instmodel
    template_returns_instmodlc = "1 {oot_var}{planets_lc}"

    # Initialise the template for each instmodel
    template_returns_instmod = "{delta_inst_rv} {star_mean_rv} {planets_rv}"

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
    arg_list[key_whole]["param"] = []
    arg_list[key_whole]["kwargs"] = []
    param_nb[key_whole] = 0

    # Add time in the kwargs entry of the whole system arg_list
    if datasets is None:
        if multi:
            arg_list[key_whole]["kwargs"].append("l_t")
        else:
            arg_list[key_whole]["kwargs"].append("t")

    # Get star mean rv and instrument delta rv contribution for each couple instrument - dataset
    (l_star_mean_rv,
     l_delta_inst_rv) = get_starmeanrv_and_deltarv(l_inst_model, l_dataset, star, multi,
                                                   RV_globalref_instname, RV_instref_modnames,
                                                   RV_inst_db, param_nb, key_whole, arg_list,
                                                   key_param, key_kwargs)

    # Save the param_nb and arg_list for the whole function before iterating over the planets
    # text_def_func_before = text_def_func[self.key_whole]
    param_nb_before = param_nb[key_whole]
    arg_list_before = deepcopy(arg_list[key_whole])

    # Get the ld_parcont and ld_param_list
    l_LD_parcont_name = []
    l_LD_parcont = []
    l_ld_param_list = []
    for ii, instmdl in enumerate(l_inst_model):
        l_LD_parcont_name.append(ldmodel4instmodfname[instmdl.full_name])
        l_LD_parcont.append(LDs[l_LD_parcont_name[ii]])
        if l_LD_parcont.ld_type == "quadratic":
            raise ValueError("For now rebound only accept the quadratic limb-darkening model.")
        l_ld_param_list.append("[")
        for param in l_LD_parcont[ii].get_list_params(main=True):
            if param.free:
                l_ld_param_list[ii] += "p[{}], ".format(param_nb[key_whole])
                param_nb[key_whole] += 1
                arg_list[key_whole][key_param].append(param.full_name)
            else:
                l_ld_param_list[ii] += "{}, ".format(param.value)
        l_ld_param_list[ii] += "]"

    # Check if datasets are provided
    has_dataset = datasets is not None

    # Initialise the local dictionary for the creation of the datasim functions by exec
    # ldict = locals().copy()  # TODO: think if there is a way to put that in a function common to
    # all datasimulator because it's more or less repeated in my 3 datasimulators for now
    ldict = {}
    # if datasets are provided add the time array and tref to the local dictionary
    if has_dataset:
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

    # Check if their is LC instrument and or RV instrument
    has_LC = LC_inst_cat in instcat_docf
    has_RV = RV_inst_cat in instcat_docf

    ## Prepare the list of light-curve times and radial velocity times to provide to the rebound
    ## function along with the indexes in those two vectors corresponding to each dataset
    if has_LC:
        l_LC_instmodel = []
        if has_dataset:
            lc_times = []
            l_LC_nb_times = []
            l_idx_LCmodel = []
        else:
            lc_times = None
    if has_RV:
        l_RV_instmodel = []
        if has_dataset:
            rv_times = []
            l_RV_nb_times = []
            l_idx_RVmodel = []
        else:
            rv_times = None

    # Create l_dict_instmod_dataset which will tell you where to find the model for each couple
    # instrument model - dataset in order to build the list of outputs
    l_dict_retrieve_instmod_dataset = {}

    # For each couple instrument model - dataset, ...
    for inst_cat, instmdl, dst in zip(instcat_docf, l_inst_model, l_dataset):
        dico_retrieve = {}
        if has_dataset:
            time = dst.get_time()
            nb_time = len(time)
        if inst_cat == LC_inst_cat:
            dico_retrieve["LC or RV"] = "LC"
            dico_retrieve["idx"] = len(l_LC_instmodel)
            l_LC_instmodel.append(instmdl)
            if has_dataset:
                l_LC_nb_times.append(nb_time)
                lc_times.append(time)
        else:  # inst_cat == RV_inst_cat:
            dico_retrieve["LC or RV"] = "RV"
            dico_retrieve["idx"] = len(l_RV_instmodel)
            l_RV_instmodel.append(instmdl)
            if has_dataset:
                l_RV_nb_times.append(nb_time)
                rv_times.append(time)
        l_dict_retrieve_instmod_dataset.append(dico_retrieve)

    if has_dataset:
        for has, times, l_nb_time, l_idx_model in [(has_LC, lc_times, l_LC_nb_times, l_idx_LCmodel),
                                                   (has_RV, rv_times, l_RV_nb_times, l_idx_RVmodel)
                                                   ]:
            if has:
                idx_tosorttime = argsort(times)
                idx_todesorttime = argsort(idx_tosorttime)
                times = times[idx_tosorttime]
                for low, up in zip(cumsum([0, ] + l_nb_time[-1]), cumsum(l_nb_time)):
                    l_idx_model.append(idx_todesorttime[low, up])

    # TODO: Preambule which construct the lc_times and rv_times inside the function


    return None


def funrebound(param_planet, stellar_mass, stellar_radius, limb_dark, treference,
               dt=0.01, supersamp=1, exptime=exptime_Kp_lc, lc_times=None, rv_times=None,
               nthreads=1):
    """
    Get the photodynamical model for photometry and/or radial velocity points.

    Multiplanets transis are ok unless the planets pass in front of each other.
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
