#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce custom plots of CORALIE-153 RV data

@TODO:
"""
from os import getcwd, makedirs
from os.path import join

import numpy as np

from logging import DEBUG, INFO
from matplotlib.gridspec import GridSpec
from copy import deepcopy
from collections import OrderedDict
from PyAstronomy.pyasl import foldAt

from fig_styler import styler

import source.tools.emcee_tools as et
import source.posterior.core.posterior as cpost
import source.tools.mylogger as ml

from source.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel

# from ipdb import set_trace

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

@styler
def create_RV_plots(fig, dico_datasetname, planets, periods, tcs, datasim_dbf, dataset_db, model_instance, fitted_values,
                    l_param_name, star, fig_param=None, show_legend=True, legend_param=None, show_xlabel=True,
                    show_ylabel=True, *args, **kwargs):
    """Produce a clean RV plot.

    :param fig: Figure instance (provided by the styler)
    :param dico_datasetname: Dictionary providing the datasets to load and use
    :param list_of_str planets: List of planet names (used to infer the number of planets and create the good number of subplots)
    :param periods: Orbital periods for each planets (used to phase fold)
    :param tcs: Time of inferior conjunction for each planet (used to phase fold)
    :param model_instance: Core_Model subclass instance
    :param fitted_values: Fitted values
    :param list_of_str l_param_name: List of parameter names
    :param star: Star instance
    :param fig_param: Dictionary providing keyword arguments for the figure definition. For example,
        right, left, bottom, top keywords can be defined and they will be passed to the GridSpec init function
    :param bool show_legend: If True, show the legend
    :param legend_param: Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True)
    :param bool show_xlabel: If True, show the x label
    :param bool show_ylabel: If True, show the y labels
    """

    ###########
    # Load Data
    ###########

    # Load the defined datasets
    dico_dataset = {}
    dico_kwargs = {}
    for inst in dico_datasetname:
        dico_dataset[inst] = {}
        dico_kwargs[inst] = {}
        for key in dico_datasetname[inst]:
            dico_dataset[inst][key] = dataset_db[dico_datasetname[inst][key]]
            dico_kwargs[inst][key] = dico_dataset[inst][key].get_kwargs()

    ##################################################
    # Compute the phases associated to the time values
    ##################################################
    phases = OrderedDict()
    P = periods[0]
    tc = tcs[0]

    for inst in datasetname:
        phases[inst] = OrderedDict()
        for key in datasetname[inst]:
            phases[inst][key] = foldAt(kwargs[inst][key]["t"], P, T0=(tc + P / 2)) - 0.5

    ########################
    # Load datasim functions
    ########################
    datasim_docfunc = {}
    for inst in datasetname:
        datasim_docfunc[inst] = {}
        for key in dataset[inst]:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname[inst][key])
            datasim_docfunc[inst][key] = datasim_dbf.instrument_db[instmod_fullname_key]["whole"]

    ###################
    # Load noise models
    ###################
    noise_model = OrderedDict()
    for inst in datasetname:
        noise_model[inst] = OrderedDict()
        for key in datasetname[inst]:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname[inst][key])
            noise_model[inst][key] = noisemodel_dbf.instrument_db[instmod_fullname_key]["whole"]

    ######################
    # Load the jitter info
    ######################
    jitter = OrderedDict()
    for inst in noise_model:
        jitter[inst] = OrderedDict()
        for key in noise_model[inst]:
            if noise_model[inst][key].has_jitter:
                jitter_param_fullname = noise_model[inst][key].get_jitterparam().full_name
                idx_jitter = l_param_name.index(jitter_param_fullname)
                jitter[inst][key] = {"value": fitted_values[idx_jitter],
                                     "type": noise_model[inst][key].jitter_type}
            else:
                jitter[inst][key] = {"value": None, "type": None}

    ##############################################
    # Apply the jitter to the data error if needed
    ##############################################
    # data_err = OrderedDict()
    # for inst in jitter:
    #     data_err[inst] = OrderedDict()
    #     for key in jitter[inst]:
    #         data_err[inst][key] = kwargs[inst][key]["data_err"]
    #         if jitter[inst][key]["value"] is not None:
    #             if jitter[inst][key]["type"] == "multi":
    #                 data_err[inst][key] *= np.exp(jitter[inst][key]["value"])
    #             elif jitter[inst][key]["type"] == "add":
    #                 data_err[inst][key] = np.sqrt(data_err[inst][key]**2 *
    #                                               (1 + np.exp(2 * jitter[inst][key]["value"])))

    ####################################################
    # Compute the deltaRV to apply to the data and model
    ####################################################
    deltaRV = OrderedDict()
    RVrefglobal_instname = RV_references["global"]
    for inst in datasetname:
        RVref4inst_modname = RV_references[inst]
        deltaRV[inst] = OrderedDict()
        for key in datasetname[inst]:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname[inst][key])
            instmodobj_key = instrument_db[instmod_fullname_key]
            deltaRV[inst][key] = 0.0
            if inst != RVrefglobal_instname:
                instmod_RVref4inst = instrument_db["RV"][inst][RVref4inst_modname]
                if instmod_RVref4inst.DeltaRV.main:
                    if instmod_RVref4inst.DeltaRV.free:
                        idx_deltaRV = l_param_name.index(instmod_RVref4inst.DeltaRV.full_name)
                        deltaRV[inst][key] += fitted_values[idx_deltaRV]
                    else:
                        deltaRV[inst][key] += instmod_RVref4inst.DeltaRV.value
            if instmodobj_key.name != RVref4inst_modname:
                if instmodobj_key.deltaRV.main:
                    if instmodobj_key.deltaRV.free:
                        idx_deltaRV = l_param_name.index(instmodobj_key.deltaRV.full_name)
                        deltaRV[inst][key] += fitted_values[idx_deltaRV]
                    else:
                        deltaRV[inst][key] += instmodobj_key.deltaRV.value

    ###################
    # Plots preparation
    ###################
    fontsize = 5
    nplanet = len(planets)

    # Create the gridspec
    if fig_param is None:
        fig_param = {}
    left = fig_param.get("left", 0.17)
    right = fig_param.get("right", 0.98)
    top = fig_param.get("top", 0.98)
    bottom = fig_param.get("bottom", 0.1)

    gs = GridSpec(nrows=nplanet, ncols=1,
                  left=left, bottom=bottom, right=right, top=top,
                  wspace=None, hspace=None)

    # Set parameters for the instrument gridspec
    gs_from_sps_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot

    # Set the plots keywords arguments
    pl_kwarg_data = {"color": "r", "fmt": ".", "alpha": 1.}
    pl_kwarg_model = {"color": "k", "fmt": "", "alpha": 1., "linestyle": "-"}

    pl_kwarg = {}
    for inst in datasetname:
        pl_kwarg[inst] = {"model": pl_kwarg_model, "data": {}}
        for key in datasetname[inst]:
            pl_kwarg_data_key = deepcopy(pl_kwarg_data)
            pl_kwarg_data_key["label"] = inst
            pl_kwarg[inst]["data"][key] = pl_kwarg_data_key

    # Create the axes
    (ax_data, ax_resi) = et.add_twoaxeswithsharex_perplanet(gs[0], nplanet=nplanet, fig=fig,
                                                            gs_from_sps_kw=gs_from_sps_kw)
    ax_data = ax_data[0]
    ax_resi = ax_resi[0]

    # Set the axis labels
    if show_ylabel:
        ax_data.set_ylabel(r"RV [$\kms$]")
        ax_resi.set_ylabel(r"O - C [$\kms$]")
    if show_xlabel:
        ax_resi.set_xlabel("Orbital phase")

    # Align y labels
    x_ylabel_coord = -0.15  # for y label alignment
    ax_data.yaxis.set_label_coords(x_ylabel_coord, 0.5)
    ax_resi.yaxis.set_label_coords(x_ylabel_coord, 0.5)

    # Number of point for plotting the model
    npt_model = 1000

    # Define t  and phase min and max for plotting the model
    phase_min_mod = -0.5
    phase_max_mod = 0.5
    tmin_model = tc + P * phase_min_mod
    tmax_model = tc + P * phase_max_mod

    # Define which datsimulator to use when there is several instrument model/dataset
    key4inst = {}
    RVrefglobal_modname = RV_references[RVrefglobal_instname]
    datasim_RVrefglobal = (datasim_dbf.instrument_db["RV"][RVrefglobal_instname]
                           [RVrefglobal_modname]["whole"])
    key4inst = {}
    for inst in datasetname:
        key4inst[inst] = list(datasim_docfunc[inst])[0]
    ###############
    # Plot the data
    ###############
    for inst in datasetname:
        for key in kwargs[inst]:
            et.plot_phase_folded_timeserie(t=kwargs[inst][key]["t"],
                                           data=kwargs[inst][key]["data"] - deltaRV[inst][key],
                                           data_err=kwargs[inst][key]["data_err"],
                                           jitter=jitter[inst][key]["value"],
                                           jitter_type=jitter[inst][key]["type"], P=P, tc=tc,
                                           ax=ax_data, pl_kwargs=pl_kwarg[inst]["data"][key])

    ################
    # Plot the model
    ################
    et.plot_model(tmin_model, tmax_model, npt_model, datasim_RVrefglobal, fitted_values,
                  l_param_name, plot_phase=True, P=P, tc=tc,
                  # noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                  pl_kwargs_model=pl_kwarg[RVrefglobal_instname]["model"],
                  ax=ax_data)
    # for inst in datasetname:
    #     et.plot_model(tmin_model, tmax_model, npt_model,
    #                   datasim_docfunc[inst][key4inst[inst]],
    #                   fitted_values, l_param_name,
    #                   plot_phase=True, P=P, tc=tc,
    #                   # noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
    #                   pl_kwargs_model=pl_kwarg[inst]["model"],
    #                   ax=ax_data)

    ####################
    # Plot the residuals
    ####################

    for inst in datasetname:
        for key in kwargs[inst]:
            et.plot_residuals(t=kwargs[inst][key]["t"], data=kwargs[inst][key]["data"],
                              data_err=kwargs[inst][key]["data_err"],
                              jitter=jitter[inst][key]["value"],
                              jitter_type=jitter[inst][key]["type"],
                              datasim_db_docfunc=datasim_docfunc[inst][key],
                              param=fitted_values, l_param_name=l_param_name,
                              plot_phase=True, P=P, tc=tc,
                              # noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                              pl_kwargs_model=pl_kwarg[inst]["data"][key],
                              ax=ax_resi)

    ###################
    # Finalise the plot
    ###################
    if show_legend:
        ax_data.legend(**legend_param)


if __name__ == "__main__":
    # Define the object name
    obj_name = "WASP-153"

    # Define dataset names to be loaded
    datasetname = OrderedDict()
    # 1. SOPHIE
    datasetname["SOPHIE"] = {}
    datasetname["SOPHIE"]["0"] = "RV_WASP-153_SOPHIE_0"

    chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
    plot_folder = join(chain_analysis_output_folder, "plots")
    makedirs(plot_folder, exist_ok=True)

    load_from_pickle = True
    exploration_output_folder = join(getcwd(), "outputs/exploration")
    exploration_pickle_folder = join(exploration_output_folder, "pickles")
    chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
    chain_analysis_pickle_folder = join(chain_analysis_output_folder, "pickles")

    ## logger
    logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                            fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

    logger.info("1. Load from pickle if necessary")
    if load_from_pickle:
        # recreate post_instance object
        post_instance = cpost.Posterior(object_name=obj_name)
        post_instance.init_from_pickle(pickle_folder=exploration_pickle_folder)
        l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
        # chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
        #                                                                                folder=".")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                        folder=chain_analysis_pickle_folder)
        fitted_values = fitted_values_dic["array"]
        l_param_name = fitted_values_dic["l_param"]
        planet_name = []
        periods = []
        tcs = []
        for planet in post_instance.model.planets.values():
            planet_name.append(planet.get_name())
            periods.append(df_fittedval.loc[planet.P.get_name(include_prefix=True, recursive=True), 'value'])
            tcs.append(df_fittedval.loc[planet.tic.get_name(include_prefix=True, recursive=True), 'value'])

    dataset_db = post_instance.dataset_db
    datasim_dbf = post_instance.datasimulators
    noisemodel_dbf = post_instance.noisemodels
    instrument_db = post_instance.model.instruments
    RV_references = post_instance.model.RV_references

    create_RV_plots(datasetname=datasetname, nplanet=1, periods=periods, tcs=tcs,
                    datasim_dbf=datasim_dbf, dataset_db=dataset_db, noisemodel_dbf=noisemodel_dbf,
                    instrument_db=instrument_db, RV_references=RV_references,
                    fitted_values=fitted_values, l_param_name=l_param_name,
                    fig_param={"top": 0.98, "bottom": 0.18}, show_legend=False, show_x_label=False,
                    # Styler arguments
                    figsize=(None, 0.5), tight=False, dpi=300,
                    save=join(plot_folder, "custom_data_comp_RV.pdf")
                    )
