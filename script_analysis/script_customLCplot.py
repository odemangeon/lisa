#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce custom plots of WASP-151 RV + LC data

@TODO:
"""
from __future__ import print_function
from logging import DEBUG, INFO

import numpy as np
from matplotlib.gridspec import GridSpec
from scipy.stats import binned_statistic
from matplotlib.offsetbox import AnchoredText
from pandas import read_table
from copy import copy  # , deepcopy
from collections import OrderedDict
from PyAstronomy.pyasl import foldAt

from fig_styler import styler

import source.posterior.core.posterior as cpost
import source.tools.emcee_tools as et
import source.tools.mylogger as ml

from source.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel


mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


# from ipdb import set_trace


@styler
def create_LC_plots(fig, ndataset, nplanet, periods, tcs, datasim_dbf, dataset_db, model_instance,
                    fitted_values, l_param_name, fig_param=None, *args, **kwargs):

    ###########
    # Load Data
    ###########

    # Define dataset names
    dico_datasetname = OrderedDict()
    # 1. WASP
    dico_datasetname["WASP"] = OrderedDict()
    dico_datasetname["WASP"]["0"] = "LC_WASP-151_WASP_0"
    # 2. TRAPPIST
    dico_datasetname["TRAPPIST"] = OrderedDict()
    dico_datasetname["TRAPPIST"]["0"] = "LC_WASP-151_TRAPPIST_0"
    # 3. IAC80
    dico_datasetname["IAC80"] = OrderedDict()
    dico_datasetname["IAC80"]["0"] = "LC_WASP-151_IAC80_0"
    dico_datasetname["IAC80"]["2"] = "LC_WASP-151_IAC80_2"
    dico_datasetname["IAC80"]["3"] = "LC_WASP-151_IAC80_3"
    # 4. EulerCam
    dico_datasetname["EulerCam"] = OrderedDict()
    dico_datasetname["EulerCam"]["0"] = "LC_WASP-151_EulerCam_0"
    dico_datasetname["EulerCam"]["1"] = "LC_WASP-151_EulerCam_1"
    # 5. K2
    dico_datasetname["K2"] = OrderedDict()
    dico_datasetname["K2"]["0"] = "LC_WASP-151_K2_0"

    # Load the defined datasets
    dico_kwargs = OrderedDict()
    for inst in dico_datasetname:
        dico_kwargs[inst] = OrderedDict()
        for key in dico_datasetname[inst]:
            dataset_inst_key = dataset_db[dico_datasetname[inst][key]]
            dico_kwargs[inst][key] = dataset_inst_key.get_kwargs()

    # Load WASP full dataset
    pathfile_fullWASP = ("~/Data/target_data/WASP-151/lightcurve/"
                         "1SWASPJ231615.22+001824.5_J231615_300_ORFG_TAMUZ.lc")
    df_WASP = read_table(pathfile_fullWASP, sep="\s+", comment="#",
                         names=["time", "mag", "mag_err"])
    # For an unknown reason the time is not in ascending order so I sort it first
    df_WASP.sort_values("time", inplace=True)
    df_WASP["time"] = df_WASP["time"] + 50000
    df_WASP["flux"] = 10**(-df_WASP["mag"] / 2.5)
    df_WASP["flux_err"] = np.log(10) / 2.5 * df_WASP["mag_err"] * df_WASP["flux"]

    ##################################################
    # Compute the phases associated to the time values
    ##################################################
    phases = OrderedDict()
    P = periods[0]
    tc = tcs[0]

    # 1. WASP full data
    phases["full_WASP"] = foldAt(df_WASP["time"], P, T0=(tc + P / 2)) - 0.5

    # 1. The rest
    for inst in dico_datasetname:
        phases[inst] = OrderedDict()
        for key in dico_datasetname[inst]:
            phases[inst][key] = foldAt(dico_kwargs[inst][key]["t"], P, T0=(tc + P / 2)) - 0.5

    ########################
    # Load datasim functions
    ########################
    datasim_docfunc = OrderedDict()
    for inst in dico_datasetname:
        datasim_docfunc[inst] = OrderedDict()
        for key in dico_datasetname[inst]:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
            datasim_docfunc[inst][key] = datasim_dbf.instrument_db[instmod_fullname_key]["whole"]

    # ###################
    # # Load noise models
    # ###################
    # noise_model = OrderedDict()
    # for inst in dico_datasetname:
    #     noise_model[inst] = OrderedDict()
    #     for key in dico_datasetname[inst]:
    #         instmod_fullname_key = noisemodel_dbf.get_instmod_fullname(dico_datasetname[inst]
    #                                                                    [key])
    #         noise_model[inst][key] = noisemodel_dbf.instrument_db[instmod_fullname_key]["whole"]

    ######################
    # Load the jitter info
    ######################
    # jitter = OrderedDict()
    # for inst in noise_model:
    #     jitter[inst] = OrderedDict()
    #     for key in noise_model[inst]:
    #         if noise_model[inst][key].has_jitter:
    #             jitter_param_fullname = noise_model[inst][key].get_jitterparam().full_name
    #             idx_jitter = l_param_name.index(jitter_param_fullname)
    #             jitter[inst][key] = {"value": fitted_values[idx_jitter],
    #                                  "type": noise_model[inst][key].jitter_type}
    #         else:
    #             jitter[inst][key] = {"value": None, "type": None}

    ##############################################
    # Apply the jitter to the data error if needed
    ##############################################
    data_err = OrderedDict()
    dico_jitter = {}
    for inst in dico_datasetname:
        data_err[inst] = OrderedDict()
        dico_jitter[inst] = {}
        for key in dico_datasetname[inst]:
            dico_jitter[inst][key] = {}
            data_err[inst][key] = copy(dico_kwargs[inst][key]["data_err"])
            inst_mod_fullname = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
            inst_mod = model_instance.instruments[inst_mod_fullname]
            noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
            if noise_model.has_jitter:
                dico_jitter[inst][key]["type"] = noise_model.jitter_type
                if inst_mod.jitter.free:
                    idx_jitter = l_param_name.index(inst_mod.jitter.full_name)
                    dico_jitter[inst][key]["value"] = fitted_values[idx_jitter]
                else:
                    dico_jitter[inst][key]["value"] = inst_mod.jitter.value
                if dico_jitter[inst][key]["type"] == "multi":
                    data_err[inst][key] *= np.exp(dico_jitter[inst][key]["value"])
                elif dico_jitter[inst][key]["type"] == "add":
                    data_err[inst][key] = np.sqrt(data_err[inst][key]**2 *
                                                  (1 +
                                                   np.exp(2 * dico_jitter[inst][key]["value"])))
                else:
                    raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            else:
                dico_jitter[inst][key]["type"] = None
                dico_jitter[inst][key]["value"] = None

    ###################
    # Load OOT_var info
    ###################
    OOT_var = OrderedDict()
    for inst in dico_datasetname:
        OOT_var[inst] = OrderedDict()
        for key in dico_datasetname[inst]:
            OOT_var[inst][key] = None
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
            instmodobj_key = model_instance.instruments[instmod_fullname_key]
            if instmodobj_key.get_with_OOT_var():
                OOT_var[inst][key] = np.zeros_like(dico_kwargs[inst][key]["t"])
                for order in range(instmodobj_key.get_OOT_var_order() + 1):
                    OOT_var_name = instmodobj_key.get_OOT_param_name(order)
                    OOT_var_param = instmodobj_key.parameters[OOT_var_name]
                    OOT_var_paramname = OOT_var_param.full_name
                    if OOT_var_param.free:
                        idx = l_param_name.index(OOT_var_paramname)
                        OOT_var_paramvalue = fitted_values[idx]
                    else:
                        OOT_var_paramvalue = OOT_var_param.value
                    OOT_var[inst][key] += (OOT_var_paramvalue *
                                           (dico_kwargs[inst][key]["t"] -
                                            dico_kwargs[inst][key]["tref"])**order
                                           )

    ##############
    # Bin the data
    ##############

    # Define the phase bins for the binned data/resi plot
    phase_min = -0.05
    phase_max = 0.05
    exptime_bin = 0.02043402778  # Kepler exposure time: 29.424 min
    bin_size = exptime_bin / P
    # bins = np.arange(phase_min, phase_max + bin_size, bin_size)
    # midbins = bins[:-1] + bin_size / 2
    # nbin = len(bins) - 1

    bins = {}
    binval = {}
    binstd = {}
    midbins = {}
    for inst in dico_datasetname:
        binval[inst] = {}
        binstd[inst] = {}
        bins[inst] = {}
        midbins[inst] = {}
        for ii, key in enumerate(dico_datasetname[inst]):
            binval[inst][key] = {}
            nb_key = len(dico_kwargs[inst])
            bins[inst][key] = np.arange(phase_min - (ii * bin_size / nb_key),
                                        phase_max + bin_size, bin_size)
            midbins[inst][key] = bins[inst][key][:-1] + bin_size / 2
            # Bin the data
            if OOT_var[inst][key] is None:
                data_inst_key = dico_kwargs[inst][key]["data"]
            else:
                data_inst_key = dico_kwargs[inst][key]["data"] - OOT_var[inst][key]
            if inst == "WASP":  # For the WASP data the transit is not visible in mean but is in
                                # median
                binning_stat = "median"
            else:
                binning_stat = "mean"
            (binval[inst][key]["corr"],
             binedges_inst,
             binnb_inst) = binned_statistic(phases[inst][key], data_inst_key,
                                            statistic=binning_stat, bins=bins[inst][key],
                                            range=(phase_min, phase_max))
            (binval[inst][key]["uncorr"],
             binedges_inst,
             binnb_inst) = binned_statistic(phases[inst][key], dico_kwargs[inst][key]["data"],
                                            statistic=binning_stat, bins=bins[inst][key],
                                            range=(phase_min, phase_max))

            # Compute the error bars on the binned data
            nbin_inst_key = len(bins[inst][key]) - 1
            binstd[inst][key] = np.zeros(nbin_inst_key)
            bincount_inst = np.zeros(nbin_inst_key)
            for ii in range(nbin_inst_key):
                bincount_inst[ii] = len(np.where(binnb_inst == (ii + 1))[0])
                if bincount_inst[ii] > 0.0:
                    binstd[inst][key][ii] = np.sqrt(np.sum(np.power((data_err[inst][key]
                                                                     [binnb_inst == (ii + 1)]),
                                                                    2.)) /
                                                    bincount_inst[ii]**2)
                else:
                    binstd[inst][key][ii] = np.nan

    ###################
    # Plots preparation
    ###################

    # Create the global gridspec
    if fig_param is None:
        fig_param = {}
    left = fig_param.get("left", 0.16)
    right = fig_param.get("right", 0.98)
    top = fig_param.get("top", 0.98)
    bottom = fig_param.get("bottom", 0.05)
    hspace = fig_param.get("hspace", 0.05)
    # hspaceothers_fact = fig_param.get("hspaceothers", 0.12)
    h_dataset = (1 - (1 - top) - bottom - 3 / 4 * hspace * (1 + ndataset)) / (1 + 4 / 3 * ndataset)
    print(h_dataset)

    gs_fullWASP = GridSpec(nrows=1, ncols=1, top=top, bottom=top - h_dataset, left=left,
                           right=right)
    gs = GridSpec(nrows=ndataset, ncols=1,
                  left=left, bottom=bottom, right=right, top=top - h_dataset - hspace,
                  wspace=None, hspace=(hspace / 2 / (4 / 3 * h_dataset + (ndataset - 1) *
                                       hspace / 2)))

    # Set parameters for the instrument gridspec
    gs_from_sps_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot

    # Set the plots keywords arguments
    pl_kwarg_rawfulldata = {"color": "grey", "fmt": ".", "alpha": 0.01}
    pl_kwarg_rawdata = {"color": "k", "fmt": ".", "alpha": 0.2, "markersize": 4}
    pl_kwarg_binneddata = {"color": "r", "fmt": ".", "alpha": 1.0, "markersize": 4}

    pl_kwarg_modelraw = {"color": "k", "fmt": '', "alpha": 1., "linestyle": "--"}
    pl_kwarg_modelbinned = {"color": "k", "fmt": '', "alpha": 1.}  # , "linestyle": "-"

    pl_kwarg = {}
    for inst in dico_datasetname:
        pl_kwarg[inst] = {"model": {"raw": pl_kwarg_modelraw.copy(),
                                    "binned": pl_kwarg_modelbinned.copy()},
                          "data": {}}
        for key in dico_datasetname[inst]:
            pl_kwarg[inst]["data"][key] = {"raw": pl_kwarg_rawdata.copy(),
                                           "binned": pl_kwarg_binneddata.copy()}

    pl_kwarg["IAC80"]["data"]["2"]["raw"]["fmt"] = "p"
    pl_kwarg["IAC80"]["data"]["2"]["raw"]["markersize"] = 2.5
    pl_kwarg["IAC80"]["data"]["3"]["raw"]["fmt"] = "^"
    pl_kwarg["IAC80"]["data"]["3"]["raw"]["markersize"] = 2.5
    pl_kwarg["EulerCam"]["data"]["1"]["raw"]["fmt"] = "p"
    pl_kwarg["EulerCam"]["data"]["1"]["raw"]["markersize"] = 2.5
    pl_kwarg["IAC80"]["data"]["2"]["binned"]["fmt"] = pl_kwarg["IAC80"]["data"]["2"]["raw"]["fmt"]
    pl_kwarg["IAC80"]["data"]["2"]["binned"]["markersize"] = (pl_kwarg["IAC80"]["data"]["2"]["raw"]
                                                              ["markersize"])
    pl_kwarg["IAC80"]["data"]["2"]["binned"]["color"] = "green"
    pl_kwarg["IAC80"]["data"]["3"]["binned"]["fmt"] = pl_kwarg["IAC80"]["data"]["3"]["raw"]["fmt"]
    pl_kwarg["IAC80"]["data"]["3"]["binned"]["markersize"] = (pl_kwarg["IAC80"]["data"]["3"]["raw"]
                                                              ["markersize"])
    pl_kwarg["IAC80"]["data"]["3"]["binned"]["color"] = "blue"
    pl_kwarg["EulerCam"]["data"]["1"]["binned"]["fmt"] = (pl_kwarg["EulerCam"]["data"]["1"]["raw"]
                                                          ["fmt"])
    pl_kwarg["EulerCam"]["data"]["1"]["binned"]["markersize"] = (pl_kwarg["EulerCam"]["data"]["1"]
                                                                 ["raw"]["markersize"])
    pl_kwarg["EulerCam"]["data"]["1"]["binned"]["color"] = "green"

    # Create the axes
    ax = {}
    for ii, inst in enumerate(dico_datasetname.keys()):
        ax[inst] = {}
        axes_inst = et.add_twoaxeswithsharex_perplanet(gs[ii], nplanet=nplanet, fig=fig,
                                                       gs_from_sps_kw=gs_from_sps_kw)
        ax[inst] = {"data": axes_inst[0][0], "resi": axes_inst[1][0]}
        if inst != list(dico_datasetname.keys())[-1]:
            ax[inst]["resi"].tick_params(labelbottom="off")

    ax_fullWASP = fig.add_subplot(gs_fullWASP[0])

    # Set the axis labels
    for inst in dico_datasetname:
        ax[inst]["data"].set_ylabel(r"$\Delta \mathrm{F} / \mathrm{F}$")
        ax[inst]["resi"].set_ylabel(r"O - C")

    last_inst = list(dico_datasetname.keys())[-1]
    ax[last_inst]["resi"].set_xlabel("Orbital phase")

    ax_fullWASP.set_ylabel(r"$\Delta \mathrm{F} / \mathrm{F}$")

    # Align y labels
    x_ylabel_coord = -0.135  # for y label alignment
    offset_resi = 0.01
    for inst in dico_datasetname:
        ax[inst]["data"].yaxis.set_label_coords(x_ylabel_coord, 0.5)
        ax[inst]["resi"].yaxis.set_label_coords(x_ylabel_coord - offset_resi, 0.5)

    ax_fullWASP.yaxis.set_label_coords(x_ylabel_coord, 0.5)

    # Set the min and max phase for the plots
    for inst in dico_datasetname:
        ax[inst]["data"].set_xlim(phase_min, phase_max)  # as resi share x axis, no need to repeat

    ax_fullWASP.set_xlim(-0.5, 0.5)

    # Set the min and max relative flux and residuals for the plots
    ylim_min_data = 0.975
    ylim_max_data = 1.015
    ylim_min_resi = -0.003
    ylim_max_resi = 0.003

    for inst in dico_datasetname:
        ax[inst]["data"].set_ylim(ylim_min_data, ylim_max_data)
        ax[inst]["resi"].set_ylim(ylim_min_resi, ylim_max_resi)

    ax_fullWASP.set_ylim(0.94, 1.06)

    # Number of point for plotting the model
    npt_model = 1000

    # Define t min and max for plotting the model
    tmin_model = tc + P * phase_min
    tmax_model = tc + P * phase_max

    # Set the supersampling factor for the binned model
    supersamp_mod = 10

    # Define which datsimulator to use when there is several instrument model/dataset
    key4inst = {}
    for inst in dico_datasetname:
        key4inst[inst] = list(datasim_docfunc[inst])[0]

    # Put an box with the name of the instrument
    for inst in dico_datasetname:
        anchored_text_inst = AnchoredText(inst, loc=3)  # loc=3 is 'lower left'
        anchored_text_inst.set_alpha(0.5)
        ax[inst]["data"].add_artist(anchored_text_inst)

    anchored_textWASP = AnchoredText("WASP", loc=3)  # loc=3 is 'lower left'
    anchored_textWASP.set_alpha(0.5)
    ax_fullWASP.add_artist(anchored_textWASP)

    ###################
    # Plot the raw data
    ###################

    # 1. WASP full data
    et.plot_phase_folded_timeserie(t=df_WASP["time"], data=df_WASP["flux"], P=P, tc=tc,
                                   # data_err=data_errWASP,
                                   ax=ax_fullWASP, pl_kwargs=pl_kwarg_rawfulldata)

    # 2. The rest
    for inst in dico_datasetname:
        phases[inst] = {}
        for key in dico_datasetname[inst]:
            if OOT_var[inst][key] is None:
                data_inst_key = dico_kwargs[inst][key]["data"]
            else:
                data_inst_key = dico_kwargs[inst][key]["data"] - OOT_var[inst][key]
            et.plot_phase_folded_timeserie(t=dico_kwargs[inst][key]["t"], data=data_inst_key,
                                           P=P, tc=tc, ax=ax[inst]["data"],
                                           pl_kwargs=pl_kwarg[inst]["data"][key]["raw"])

    ###############################
    # Plot the model at raw cadence
    ###############################

    # 1. WASP full model
    tmin_modelfull = tc - P * 0.5
    tmax_modelfull = tc + P * 0.5

    pl_kwarg_modelfull = pl_kwarg_modelraw.copy()
    pl_kwarg_modelfull["linewidth"] = 1
    et.plot_model(tmin_modelfull, tmax_modelfull, 1000, datasim_docfunc["WASP"]["0"],
                  fitted_values, l_param_name,
                  plot_phase=True, P=P, tc=tc,
                  pl_kwargs_model=pl_kwarg_modelfull,
                  ax=ax_fullWASP)

    # 2. The rest
    for inst in dico_datasetname:
        if inst in ["TRAPPIST", "IAC80"]:
            # Because TRAPPIST and IAC80 includes OOT_var. I use the WASP datasim
            datasim_docfunc_inst_key = datasim_docfunc["WASP"][key4inst["WASP"]]
        else:
            datasim_docfunc_inst_key = datasim_docfunc[inst][key4inst[inst]]
        et.plot_model(tmin_model, tmax_model, npt_model,
                      datasim_docfunc_inst_key,
                      fitted_values, l_param_name,
                      plot_phase=True, P=P, tc=tc,
                      pl_kwargs_model=pl_kwarg[inst]["model"]["raw"],
                      ax=ax[inst]["data"])

    ######################
    # Plot the binned data
    ######################
    for inst in dico_datasetname:
        for key in dico_datasetname[inst]:
            ax[inst]["data"].errorbar(midbins[inst][key], binval[inst][key]["corr"],
                                      yerr=binstd[inst][key],
                                      **pl_kwarg[inst]["data"][key]["binned"])

    ##################################
    # Plot the model at binned cadence
    ##################################
    for inst in dico_datasetname:
        if inst in ["TRAPPIST", "IAC80"]:
            # Because TRAPPIST and IAC80 includes OOT_var. I use the WASP datasim
            datasim_docfunc_inst_key = datasim_docfunc["WASP"][key4inst["WASP"]]
        else:
            datasim_docfunc_inst_key = datasim_docfunc[inst][key4inst[inst]]
        et.plot_model(tmin_model, tmax_model, npt_model, datasim_docfunc_inst_key,
                      fitted_values, l_param_name,
                      supersamp=supersamp_mod, exptime=exptime_bin,
                      plot_phase=True, P=P, tc=tc,
                      pl_kwargs_model=pl_kwarg[inst]["model"]["binned"],
                      ax=ax[inst]["data"])

    ###################################
    # Plot the residuals at raw cadence
    ###################################
    for inst in dico_datasetname:
        for key in dico_datasetname[inst]:
            et.plot_residuals(t=dico_kwargs[inst][key]["t"],
                              data=dico_kwargs[inst][key]["data"],
                              datasim_db_docfunc=datasim_docfunc[inst][key],
                              datasim_kwargs={"tref": dico_kwargs[inst][key]["tref"]},
                              param=fitted_values, l_param_name=l_param_name,
                              plot_phase=True, P=P, tc=tc,
                              pl_kwargs_model=pl_kwarg[inst]["data"][key]["raw"],
                              ax=ax[inst]["resi"])

    ######################################
    # Plot the residuals at binned cadence
    ######################################
    for inst in dico_datasetname:
        for key in dico_datasetname[inst]:
            phase_tref = foldAt(dico_kwargs[inst][key]["tref"], P, T0=(tc + P / 2)) - 0.5
            et.plot_residuals(t=dico_kwargs[inst][key]["tref"] + P * (midbins[inst][key] -
                                                                      phase_tref),
                              data=binval[inst][key]["uncorr"],
                              data_err=binstd[inst][key],
                              datasim_db_docfunc=datasim_docfunc[inst][key],
                              datasim_kwargs={"tref": dico_kwargs[inst][key]["tref"]},
                              param=fitted_values, l_param_name=l_param_name,
                              supersamp=supersamp_mod, exptime=exptime_bin,
                              plot_phase=True, P=P, tc=tc,
                              pl_kwargs_model=pl_kwarg[inst]["data"][key]["binned"],
                              ax=ax[inst]["resi"])


if __name__ == "__main__":
    # Define the object name
    obj_name = "WASP-151"

    ## logger
    logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                            fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

    load_from_pickle = True

    logger.info("1. Load from pickle if necessary")
    if load_from_pickle:
        # recreate post_instance object
        post_instance = cpost.Posterior(object_name=obj_name)
        post_instance.init_from_pickle()
        l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
        # chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
        #                                                                                folder=".")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                        folder=".")
        fitted_values = fitted_values_dic["array"]
        l_param_name = fitted_values_dic["l_param"]
        planet_name = []
        periods = []
        tcs = []
        for planet in post_instance.model.planets.values():
            planet_name.append(planet.name)
            periods.append(df_fittedval.loc[planet.P.full_name, 'value'])
            tcs.append(df_fittedval.loc[planet.tc.full_name, 'value'])

    dataset_db = post_instance.dataset_db
    datasim_dbf = post_instance.datasimulators
    model_instance = post_instance.model

    ndataset = 5

    create_LC_plots(nplanet=1, ndataset=ndataset, periods=periods, tcs=tcs,
                    datasim_dbf=datasim_dbf, dataset_db=dataset_db, model_instance=model_instance,
                    fitted_values=fitted_values, l_param_name=l_param_name,
                    figsize=(None, 0.29 * (4 / 3. * ndataset + 1)), tight=False, dpi=200,
                    fig_param={"top": 0.99, "bottom": 0.04, "hspace": 0.04},
                    save="./images/custom_data_comp_LC.png"
                    # verbose=True,
                    )
