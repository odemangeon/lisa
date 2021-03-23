#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create oplot specifically for radial velocity data

@TODO:
"""
import numpy as np

from copy import deepcopy, copy
from collections import OrderedDict, defaultdict
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator
from PyAstronomy.pyasl import foldAt
from scipy.stats import binned_statistic

from ..emcee_tools import emcee_tools as et

from ..posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add
from ..posterior.exoplanet.model.datasim_creator_rv import RVdrift_tref_name

AandA_fontsize = 8

# managers
mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


def create_RV_phasefolded_plots(fig, post_instance, df_fittedval, datasim_kwargs=None, planets=None, star_name="A",
                                datasetnames=None,
                                remove_GP=False, RV_fact=1.,
                                phase_binsize=0., binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                                sharey=False,
                                fig_param=None, pl_kwargs=None, show_legend=True, legend_param=None,
                                show_system_name_in_suptitle=True, show_rms_residuals_in_suptitle=True,
                                RV_unit="$km/s$", *args, **kwargs):
    """Produce a clean RV plot.

    WARNING/TODO: Because the plots are done independantly for each planet when sharey is True,
    I am not sure that the indicate_y_outliers function behaves correctly.

    Arguments
    ---------
    fig           :
        Figure instance (provided by the styler)
    post_instance : Posterior instance
    df_fittedval  : DataFrame
        Dataframe containing the parameter estimates (index=Parameter_fullname, columns=[value, sigma-, sigma+] )
    datasim_kwargs : dict
        Dictionary of keyword arguments for the datasimulator.
    planets : list_of_str or None
        List of the names of the planets for which you want a phase pholded curve. If None all planets are used
    star_name     : String
    datasetnames  : list of String
        List providing the datasets to load and use
    remove_GP     : Boolean
        If True the GP model is remove from the data for the plot.
    RV_fact       : float
        Factor to apply to the RV
    phase_binsize : float
        If phase_binsize is superior to 0. The the data will be binned (all dataset included) and display.
        phase_binsize then gives the size of the bin used
    binning_stat  : str
        Statitical method used to compute the binned value. Can be "mean" or "median". This is passed to the
        statistic argument of scipy.stats.binned_statistic
    supersamp_bin_model : int
        Supersampling factor for the binned model.
    show_binned_model   : bool
        If True the binned model is shown.
    sharey        : bool
    fig_param     : dict
        Dictionary providing keyword arguments for the figure definition and settings. The possible keys are
            - 'system_name_4_suptitle': Name that you want to use for the suptitle if different from the post_instance name
            - 'main_gridspec': The content of this entry should be a dictionary which will be passed to
                GridSpec (GridSpec(..., **fig_param['main_gridspec'])) instance creation with create the main gridspec
            - 'add_axeswithsharex_kw': The content of this entry should be a dictionary which will be
                passed to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., add_axeswithsharex_kw=fig_param['add_axeswithsharex_kw'])
                function creating two axes data and residuals per planet.
            - 'gs_from_sps_kw': The content of this entry should be a dictionary which will be passed
                to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., gs_from_sps_kw=fig_param['gs_from_sps_kw'])
                function creating two axes data and residuals per planet.
            - 'pad_data': Iterable of 2 floats which define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
            - 'pad_resi': Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
            - 'indicate_y_outliers_data': boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
            - 'indicate_y_outliers_resi': boolean. If True, residuals outliers (outside of the plot) are indicated
                by arrows.
            - fontsize : Int specifiying the fontsize
            - 'rms_format': Format that will be used to format the rms values (for example '.0f')
            - 'suptitle_kwargs': to pass kwargs to the suptitle command
    pl_kwargs    : dict
        Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "modelbinned" or "databinned" and values
        a dictionary that will be passed as keyword arguments associated the plotting functions.
        You can also add a 'jitter' key with value a dictionary that will contain the changes that you
        want to make for the update error bars due to potential jitter.
    show_legend  : bool
        If True, show the legend
    legend_param : dict
        Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True).
        Can also contains another entry that will not be passed to pyplot.legend:
        'idx_planet': This contains the idx of the planet plot on which you want to show the legend()
    show_system_name_in_suptitle : bool
        If True show the system name in the suptitle
    show_rms_residuals_in_suptitle: bool
        If True the rms of the residuals will be provided in the suptitle.
    RV_unit        : str
        String giving the unit of the RVs
    """
    all_planets = list(post_instance.model.planets.keys())
    all_planets.sort()
    if planets is None:
        planets = copy(all_planets)
    nplanet = len(planets)

    star = post_instance.model.stars[star_name]

    ###########
    # Load Data
    ###########
    # If no dataset name is provided get all the available RV datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="RV", sortby_instcat=False, sortby_instname=False)
    # Load the defined datasets and check how many dataset there is by instrument.
    dico_dataset = {}
    dico_kwargs = {}
    dico_nb_dstperinst = defaultdict(lambda: 0)
    for datasetname in datasetnames:
        dico_dataset[datasetname] = post_instance.dataset_db[datasetname]
        dico_kwargs[datasetname] = dico_dataset[datasetname].get_kwargs()
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        dico_nb_dstperinst[filename_info["inst_name"]] += 1
        # apply the RV fact to RV and RV_err
        dico_kwargs[datasetname]["data"] *= RV_fact
        dico_kwargs[datasetname]["data_err"] *= RV_fact

    ###################
    # Plots preparation
    ###################

    # Create the gridspec
    if fig_param is None:
        fig_param = {}

    fontsize = fig_param.get("fontsize", AandA_fontsize)

    gs = GridSpec(figure=fig, nrows=1, ncols=1, **fig_param.get('main_gridspec', {}))

    # Set parameters for the instrument gridspec
    add_axeswithsharex_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot
    add_axeswithsharex_kw.update(fig_param.get("add_axeswithsharex_kw", {}))
    gs_from_sps_kw = {}
    gs_from_sps_kw.update(fig_param.get("gs_from_sps_kw", {}))

    # Set the plots keywords arguments
    pl_kwarg_data = {"fmt": "."}
    pl_kwarg_databinned = {"fmt": "o", 'alpha': 1., 'label': f"bin({phase_binsize:.2f})"}
    pl_kwarg_model = {"fmt": "", "linestyle": "-"}
    pl_kwarg_modelbinned = {"fmt": "", "linestyle": "-", 'label': f"model: bin({phase_binsize:.2f})"}
    show_error_data = True
    show_error_databinned = True

    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    pl_kwarg_jitter = {}
    pl_show_error = {}

    for datasetname in datasetnames:
        # Set the labels
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        if dico_nb_dstperinst[filename_info["inst_name"]] == 1:
            label_dst = filename_info["inst_name"]
        else:
            label_dst = filename_info["inst_name"] + "({})".format(filename_info["number"])
        pl_kwarg_final[datasetname] = {"label": label_dst, }
        pl_kwarg_final[datasetname].update(deepcopy(pl_kwarg_data))
        # Update with the user's inputs
        pl_kwarg_final[datasetname].update(pl_kwargs.get(datasetname, {}))
        if "jitter" in pl_kwarg_final[datasetname]:
            dico_jitter = pl_kwarg_final[datasetname].pop("jitter")
        else:
            dico_jitter = {}
        dico_jitter["fmt"] = "none"  # To ensure that only the error bars are drawn
        pl_kwarg_jitter[datasetname] = deepcopy(pl_kwarg_final[datasetname])
        pl_kwarg_jitter[datasetname].update(dico_jitter)
        pl_kwarg_jitter[datasetname].pop("label")  # To ensure that a second label doesn't appear on the legend
        # default value for alpha jitter
        if "alpha" not in dico_jitter:
            if "alpha" in pl_kwarg_jitter[datasetname]:
                pl_kwarg_jitter[datasetname]["alpha"] = pl_kwarg_jitter[datasetname]["alpha"] / 2
            else:
                pl_kwarg_jitter[datasetname]["alpha"] = 0.5
        # default value for ecolor
        if ("ecolor" not in pl_kwarg_jitter[datasetname]) and ("color" in pl_kwarg_jitter[datasetname]):
            pl_kwarg_jitter[datasetname]["ecolor"] = pl_kwarg_jitter[datasetname]["color"]
        pl_show_error[datasetname] = pl_kwarg_final[datasetname].pop("show_error") if "show_error" in pl_kwarg_final[datasetname] else show_error_data
    pl_kwarg_final["model"] = deepcopy(pl_kwarg_model)
    pl_kwarg_final["model"].update(pl_kwargs.get("model", {}))
    pl_kwarg_final["modelbinned"] = deepcopy(pl_kwarg_modelbinned)
    pl_kwarg_final["modelbinned"].update(pl_kwargs.get("modelbinned", {}))
    pl_kwarg_final["databinned"] = deepcopy(pl_kwarg_databinned)
    pl_kwarg_final["databinned"].update(pl_kwargs.get("databinned", {}))
    if "jitter" in pl_kwarg_final["databinned"]:
        dico_jitter = pl_kwarg_final["databinned"].pop("jitter")
    else:
        dico_jitter = {}
    dico_jitter["fmt"] = "none"  # To ensure that only the error bars are drawn
    pl_kwarg_final["binned_jitter"] = deepcopy(pl_kwarg_final["databinned"])
    pl_kwarg_final["binned_jitter"].update(dico_jitter)
    pl_kwarg_final["binned_jitter"].pop("label")
    # default value for alpha jitter
    if "alpha" not in dico_jitter:
        if "alpha" in pl_kwarg_final["binned_jitter"]:
            pl_kwarg_final["binned_jitter"]["alpha"] = pl_kwarg_final["binned_jitter"]["alpha"] / 2
        else:
            pl_kwarg_final["binned_jitter"]["alpha"] = 0.5
    # default value for ecolor
    if ("ecolor" not in pl_kwarg_final["binned_jitter"]) and ("color" in pl_kwarg_final["binned_jitter"]):
        pl_kwarg_final["binned_jitter"]["ecolor"] = pl_kwarg_final["binned_jitter"]["color"]
    pl_show_error["databinned"] = pl_kwarg_final["databinned"].pop("show_error") if "show_error" in pl_kwarg_final["databinned"] else show_error_databinned

    # Create the axes
    (ax_data, ax_resi) = et.add_twoaxeswithsharex_perplanet(gs[0], nplanet=nplanet, fig=fig, sharey=sharey,
                                                            gs_from_sps_kw=gs_from_sps_kw,
                                                            add_axeswithsharex_kw=add_axeswithsharex_kw)
    ax_data0 = ax_data[0]
    ax_resi0 = ax_resi[0]

    # Set the axis labels
    ax_data0.set_ylabel(r"RV [{}]".format(RV_unit), fontsize=fontsize)
    # ax_data0.set_ylabel("RV [m.s-1]", fontsize=fontsize)
    ax_resi0.set_ylabel(r"O - C [{}]".format(RV_unit), fontsize=fontsize)
    # ax_resi0.set_ylabel("O - C [m.s-1]", fontsize=fontsize)
    for res_ax in ax_resi:
        res_ax.set_xlabel("Orbital phase", fontsize=fontsize)

    # Align y labels
    # ax_data0.yaxis.set_label_coords(x_ylabel_coord, 0.5)
    # ax_resi0.yaxis.set_label_coords(x_ylabel_coord, 0.5)

    # Number of point for plotting the model
    npt_model = 1000

    for ii, planet_name in enumerate(planets):
        ax_data_pl = ax_data[ii]
        ax_resi_pl = ax_resi[ii]

        ax_data_pl.set_title("{} {}".format("Planet", planet_name), fontsize=fontsize)
        ax_data_pl.tick_params(axis='both', which='major', labelsize=fontsize)
        ax_resi_pl.tick_params(axis='both', which='major', labelsize=fontsize)

        ax_data_pl.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False)
        ax_data_pl.xaxis.set_minor_locator(AutoMinorLocator())
        ax_data_pl.yaxis.set_minor_locator(AutoMinorLocator())
        ax_data_pl.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
        ax_data_pl.grid(axis="y", color="black", alpha=.5, linewidth=.5)
        ax_resi_pl.yaxis.set_minor_locator(AutoMinorLocator())
        ax_resi_pl.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True)
        ax_resi_pl.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
        ax_resi_pl.grid(axis="y", color="black", alpha=.5, linewidth=.5)
        if ii != 0:
            ax_data_pl.tick_params(axis="both", labelleft=False)
            ax_resi_pl.tick_params(axis="both", labelleft=False)

        ##################################################
        # Compute the phases associated to the time values
        ##################################################

        phases = OrderedDict()
        Per = df_fittedval.loc[post_instance.model.planets[planet_name].P.full_name]["value"]
        tc = df_fittedval.loc[post_instance.model.planets[planet_name].tic.full_name]["value"]
        # print(Per, tc)

        # Define t and phase min and max for plotting the model
        phase_min_mod = -0.5
        phase_max_mod = 0.5
        tmin_model = tc + Per * phase_min_mod
        tmax_model = tc + Per * phase_max_mod

        for datasetname in datasetnames:
            phases[datasetname] = (foldAt(dico_kwargs[datasetname]["t"], Per, T0=(tc + Per / 2)) - 0.5)

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        data_err_jitter = OrderedDict()
        dico_jitter = {}
        for datasetname in datasetnames:
            dico_jitter[datasetname] = {}
            data_err_jitter[datasetname] = dico_kwargs[datasetname]["data_err"].copy()
            inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
            inst_mod = post_instance.model.instruments[inst_mod_fullname]
            noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
            if noise_model.has_jitter:
                dico_jitter[datasetname]["type"] = noise_model.jitter_type
                if inst_mod.jitter.free:
                    dico_jitter[datasetname]["value"] = df_fittedval.loc[inst_mod.jitter.full_name]["value"] * RV_fact
                else:
                    dico_jitter[datasetname]["value"] = inst_mod.jitter.value
                if dico_jitter[datasetname]["type"] == "multi":
                    data_err_jitter[datasetname] = np.sqrt(apply_jitter_multi(data_err_jitter[datasetname], dico_jitter[datasetname]["value"]))
                elif dico_jitter[datasetname]["type"] == "add":
                    data_err_jitter[datasetname] = np.sqrt(apply_jitter_add(data_err_jitter[datasetname], dico_jitter[datasetname]["value"]))
                else:
                    raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            else:
                dico_jitter[datasetname]["type"] = None
                dico_jitter[datasetname]["value"] = None
                data_err_jitter[datasetname] = None

        ####################################################
        # Compute the deltaRV to apply to the data and model
        ####################################################
        deltaRV = OrderedDict()
        RVrefglobal_instname = post_instance.model.RV_references["global"]
        # For each dataset
        for datasetname in datasetnames:
            filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
            RVref4inst_modname = post_instance.model.RV_references[filename_info["inst_name"]]
            instmod_fullname_key = post_instance.datasimulators.get_instmod_fullname(datasetname)
            instmodobj_key = post_instance.model.instruments[instmod_fullname_key]
            deltaRV[datasetname] = 0.0
            # If the current instrument is not the instrument of the global reference:
            # Add to Delta_RV the values of delta RV of the current instrument model reference to the global reference.
            if filename_info['inst_name'] != RVrefglobal_instname:
                instmod_RVref4inst = post_instance.model.instruments["RV"][filename_info['inst_name']][RVref4inst_modname]
                if instmod_RVref4inst.DeltaRV.main:
                    if instmod_RVref4inst.DeltaRV.free:
                        deltaRV[datasetname] += df_fittedval.loc[instmod_RVref4inst.DeltaRV.full_name]["value"]
                    else:
                        deltaRV[datasetname] += instmod_RVref4inst.DeltaRV.value
            # If the current instrument model is not the reference instrument model for the instrument:
            # Add to Delta_RV the values of delta RV of the current instrument model to the current instrument model reference.
            if instmodobj_key.get_name() != RVref4inst_modname:
                if instmodobj_key.DeltaRV.main:
                    if instmodobj_key.DeltaRV.free:
                        deltaRV[datasetname] += df_fittedval.loc[instmodobj_key.DeltaRV.full_name]["value"]
                    else:
                        deltaRV[datasetname] += instmodobj_key.DeltaRV.value
            # Apply RV_fact to deltaRV
            deltaRV[datasetname] *= RV_fact

        RVrefglobal_modname = post_instance.model.RV_references[RVrefglobal_instname]
        inst_RVclass = mgr_inst_dst.get_inst_subclass("RV")
        RVrefglobal_instmod_fullname = inst_RVclass.build_instmod_fullname(inst_model=RVrefglobal_modname, inst_name=RVrefglobal_instname, inst_fullcat="RV")
        l_datasetname_RVrefglobal = post_instance.model.get_ldatasetname4instmodfullname(instmod_fullname=RVrefglobal_instmod_fullname)

        ###############
        # Plot the data
        ###############
        data_pl = OrderedDict()
        for datasetname in datasetnames:
            # The data to plot for a planet and an instrument are the raw data to which you substract
            # the delta RV to the global reference (deltaRV[datasetname]) and then to which you substract the
            # other planets contribution

            # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
            # and remove RV_drift
            kwargs_dataset = dico_kwargs[datasetname].copy()
            t_dst = kwargs_dataset.pop("t")
            kwargs_dataset.pop("data")
            kwargs_dataset.pop("data_err")
            kwargs_dataset.update(datasim_kwargs.copy())

            # Remove the DeltaRV to the global RV reference
            data_pl[datasetname] = dico_kwargs[datasetname]["data"] - deltaRV[datasetname]

            # Remove the systemic velocity (with drift when needed)
            data_pl[datasetname] -= df_fittedval.loc[star.v0.full_name]["value"] * RV_fact
            if star.with_RVdrift:
                for orderm1 in range(star.RVdrift_order):
                    data_pl[datasetname] -= df_fittedval.loc[star.parameters[star.get_RVdrift_param_name(orderm1 + 1)].full_name]["value"] * RV_fact * (t_dst - datasim_kwargs[RVdrift_tref_name])**(orderm1 + 1)

            print(f"RMS of the data of {datasetname} before GP model removal: {np.std(data_pl[datasetname])} {RV_unit}")
            # Remove GP model
            if remove_GP:
                (model_dst, model_wGP_dst, GP_pred, GP_pred_var
                 ) = post_instance.compute_model(tsim=t_dst, dataset_name=datasetname, param=df_fittedval["value"],
                                                 l_param_name=list(df_fittedval.index), key_obj="whole", datasim_kwargs=kwargs_dataset
                                                 )
                # Apply RV_fact to models and GP
                model_dst *= RV_fact
                if model_wGP_dst is not None:
                    model_wGP_dst *= RV_fact
                    GP_pred *= RV_fact
                    GP_pred_var *= RV_fact**2
                    # Correct data from GP pred
                    data_pl[datasetname] -= GP_pred

            print(f"RMS of the data of {datasetname} after GP model removal: {np.std(data_pl[datasetname])} {RV_unit}")

            # Compute and remove the other planet contribution
            for plnt in all_planets:
                if plnt == planet_name:
                    continue
                else:
                    (model_pl_only, _, _, _
                     ) = post_instance.compute_model(tsim=t_dst, dataset_name=datasetname, param=df_fittedval["value"],
                                                     l_param_name=list(df_fittedval.index), key_obj=f"{plnt}_only", datasim_kwargs=kwargs_dataset
                                                     )
                    # Apply RV_fact to models
                    model_pl_only *= RV_fact
                    data_pl[datasetname] = data_pl[datasetname] - model_pl_only

            # Plot the data
            if pl_show_error[datasetname]:
                data_err = dico_kwargs[datasetname]["data_err"]
            else:
                data_err = None
            ebcont, _, _ = et.plot_phase_folded_timeserie(t_data=dico_kwargs[datasetname]["t"],
                                                          data=data_pl[datasetname],
                                                          data_err=data_err,
                                                          Per=Per, tref=tc,
                                                          ax=ax_data_pl, pl_kwargs=pl_kwarg_final[datasetname],
                                                          )
            if not("ecolor" in pl_kwarg_jitter[datasetname]):
                pl_kwarg_jitter[datasetname]["ecolor"] = ebcont[0].get_color()
            if not("color" in pl_kwarg_final[datasetname]):
                pl_kwarg_final[datasetname]["color"] = ebcont[0].get_color()
            if pl_show_error[datasetname]:
                ebcont, _, _ = et.plot_phase_folded_timeserie(t_data=dico_kwargs[datasetname]["t"],
                                                              data=data_pl[datasetname],
                                                              data_err=data_err_jitter[datasetname],
                                                              only_errorbar=True,
                                                              Per=Per, tref=tc,
                                                              ax=ax_data_pl,
                                                              # pl_kwargs={'fmt': 'none', 'alpha': 0.25}
                                                              pl_kwargs=pl_kwarg_jitter[datasetname],
                                                              )

        # Set the y axis limits
        pad_data_default = (0.1, 0.1)
        if planet_name in fig_param.get("pad_data", {}):
            pad_data = fig_param["pad_data"][planet_name]
        else:
            pad_data_content = fig_param.get("pad_data", pad_data_default)
            if isinstance(pad_data_content, dict):
                pad_data = pad_data_default
            else:
                pad_data = pad_data_content
        et.auto_y_lims(np.concatenate([y for y in data_pl.values()]), ax_data_pl, pad=pad_data)
        # Indicate values that are off y-axis with anarrows
        if fig_param.get("indicate_y_outliers_data", True):
            for datasetname in datasetnames:
                et.indicate_y_outliers(x=phases[datasetname], y=data_pl[datasetname], ax=ax_data_pl, color=pl_kwarg_final[datasetname]["color"],
                                       alpha=pl_kwarg_final[datasetname].get("alpha", 1))

        ################
        # Plot the model
        ################
        ebconts_lines_labels = et.plot_model(tmin=tmin_model, tmax=tmax_model, nt=npt_model, dataset_name=l_datasetname_RVrefglobal[0],
                                             param=df_fittedval["value"], l_param_name=list(df_fittedval.index), post_instance=post_instance,
                                             key_obj=f"{planet_name}_only", datasim_kwargs=kwargs_dataset,
                                             multiplication_factor=RV_fact,
                                             plot_phase=True, Per=Per, tref=tc,
                                             pl_kwargs_model=pl_kwarg_final["model"], pl_kwargs_modelandGP=pl_kwarg_final["model"],
                                             show_modelandGP=not(remove_GP), force_plot_phase_GP=False,
                                             ax=ax_data_pl)
        if not("color" in pl_kwarg_final["model"]):
            pl_kwarg_final["model"]["color"] = ebconts_lines_labels["model"]["ebcont or line"][0].get_color()

        ####################
        # Plot the residuals
        ####################
        residual_pl = OrderedDict()
        residual_wGP_pl = OrderedDict()
        y_residuals_all = []
        for datasetname in datasetnames:
            (_, _, _, _, _, residual_pl[datasetname], residual_wGP_pl[datasetname], ebconts_lines_labels
             ) = et.plot_residuals(dataset_name=datasetname, param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                   post_instance=post_instance, key_obj="whole", datasim_kwargs=kwargs_dataset,
                                   multiplication_factor=RV_fact,
                                   plot_phase=True, Per=Per, tref=tc,
                                   pl_kwargs_model=pl_kwarg_final[datasetname], show_model=not(remove_GP),
                                   show_error_model=pl_show_error[datasetname],
                                   pl_kwargs_modelandGP=pl_kwarg_final[datasetname], show_modelandGP=remove_GP,
                                   show_error_modelandGP=pl_show_error[datasetname],
                                   ax=ax_resi_pl)
            if (residual_wGP_pl[datasetname] is None) or not(remove_GP):
                y_residuals_all.append(residual_pl[datasetname])
            else:
                y_residuals_all.append(residual_wGP_pl[datasetname])
        # Set the y axis limits
        y_residuals_all = np.concatenate(y_residuals_all)
        pad_resi_default = (0.1, 0.1)
        if planet_name in fig_param.get("pad_resi", {}):
            pad_resi = fig_param["pad_resi"][planet_name]
        else:
            pad_resi_content = fig_param.get("pad_resi", pad_data_default)
            if isinstance(pad_resi_content, dict):
                pad_resi = pad_resi_default
            else:
                pad_resi = pad_resi_content
        et.auto_y_lims(y_residuals_all, ax_resi_pl, pad=pad_resi)
        # Indicate values that are off y-axis with arrows
        # Also print the rms of the residuals
        if ii == 0:
            rms_resi = []
            rms_resi_label = []
            rms_format = fig_param.get("rms_format", ".1e")
            text_rms = f"{{:{rms_format}}}"
        for datasetname in datasetnames:
            if fig_param.get("indicate_y_outliers_resi", True):
                if (residual_wGP_pl[datasetname] is None) or not(remove_GP):
                    et.indicate_y_outliers(x=phases[datasetname], y=residual_pl[datasetname], ax=ax_resi_pl, color=pl_kwarg_final[datasetname]["color"],
                                           alpha=pl_kwarg_final[datasetname].get("alpha", 1))
                else:
                    et.indicate_y_outliers(x=phases[datasetname], y=residual_wGP_pl[datasetname], ax=ax_resi_pl, color=pl_kwarg_final[datasetname]["color"],
                                           alpha=pl_kwarg_final[datasetname].get("alpha", 1))
            if ii == 0:
                filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
                if residual_pl[datasetname] is not None:
                    rms_resi.append(text_rms.format(np.std(residual_pl[datasetname])))
                    if dico_nb_dstperinst[filename_info["inst_name"]] == 1:
                        label_rms_resi_ii = pl_kwargs.get(datasetname, {}).get("label", filename_info["inst_name"])
                    else:
                        label_rms_resi_ii = pl_kwargs.get(datasetname, {}).get("label", filename_info["inst_name"]) + "({})".format(filename_info["number"])
                    rms_resi_label.append(label_rms_resi_ii)
                    print(f"RMS of the residuals of {datasetname} before GP model removal: {rms_resi[-1]} {RV_unit}")
                if residual_wGP_pl[datasetname] is not None:
                    rms_resi.append(text_rms.format(np.std(residual_wGP_pl[datasetname])))
                    if dico_nb_dstperinst[filename_info["inst_name"]] == 1:
                        label_rms_resi_ii = f"{pl_kwargs.get(datasetname, {}).get('label', filename_info['inst_name'])}(GP)"
                    else:
                        label_rms_resi_ii = f"{pl_kwargs.get(datasetname, {}).get('label', filename_info['inst_name'])}({filename_info['number']},GP)"
                    rms_resi_label.append(label_rms_resi_ii)
                    print(f"RMS of the residuals of {datasetname} after GP model removal: {rms_resi[-1]} {RV_unit}")

        if ii == 0:
            if show_system_name_in_suptitle:
                system_name = fig_param.get('system_name_4_suptitle', post_instance.full_name)
                text_system_name = f"{system_name} system\n"
            else:
                text_system_name = ""
            if show_rms_residuals_in_suptitle:
                text_rms_resi = f"rms of the residuals = {', '.join(rms_resi)} {RV_unit} ({rms_resi_label})"
            else:
                text_rms_resi = ""
            fig.suptitle(f"{text_system_name}{text_rms_resi}", fontsize=fontsize, **fig_param.get('suptitle_kwargs', {}))

        ##########################################
        # Bin the data and residuals and plot them
        ##########################################
        # Make array gathering all datasets
        # TODO: plot the binned model
        if phase_binsize > 0.:
            all_phase = np.concatenate([phases[datasetname] for datasetname in datasetnames])
            idx_sort_alldatasetphase = np.argsort(all_phase)
            all_phase = all_phase[idx_sort_alldatasetphase]
            all_data_pl = np.concatenate([data_pl[datasetname] for datasetname in datasetnames])[idx_sort_alldatasetphase]
            all_data_err = np.concatenate([dico_kwargs[datasetname]["data_err"] for datasetname in datasetnames])[idx_sort_alldatasetphase]
            all_data_err_jitter = np.concatenate([data_err_jitter[datasetname] if data_err_jitter[datasetname] is not None else dico_kwargs[datasetname]["data_err"] for datasetname in datasetnames])[idx_sort_alldatasetphase]
            l_residuals_wGP_pl = [residual_wGP_pl[datasetname] if (remove_GP and (residual_wGP_pl[datasetname] is not None)) else residual_pl[datasetname] for datasetname in datasetnames]
            all_residuals_pl = np.concatenate(l_residuals_wGP_pl)[idx_sort_alldatasetphase]
            # Define the phase bins for the binned data/resi plot
            bins = np.arange(-0.5, 0.5 + phase_binsize, phase_binsize)
            midbins = bins[:-1] + phase_binsize / 2
            # Bin the data and residuals
            (binval, binedges, binnb
             ) = binned_statistic(all_phase, all_data_pl, statistic=binning_stat, bins=bins, range=(0, 1))
            (binval_resi, _, _
             ) = binned_statistic(all_phase, all_residuals_pl, statistic=binning_stat, bins=bins, range=(0, 1))
            # Compute the error bars on the binned data (and residuals)
            nbins = len(bins) - 1
            binstd = np.zeros(nbins)
            binstd_jitter = np.zeros(nbins) if (data_err_jitter[datasetname] is not None) else None
            bincount = np.zeros(nbins)
            for i_bin in range(nbins):
                bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                if bincount[i_bin] > 0.0:
                    binstd[i_bin] = np.sqrt(np.sum(np.power(all_data_err[binnb == (i_bin + 1)], 2.)) /
                                            bincount[i_bin]**2)
                    if data_err_jitter[datasetname] is not None:
                        binstd_jitter[i_bin] = np.sqrt(np.sum(np.power(all_data_err_jitter[binnb == (i_bin + 1)], 2.)) /
                                                       bincount[i_bin]**2)
                else:
                    binstd[i_bin] = np.nan
                    if data_err_jitter[datasetname] is not None:
                        binstd_jitter[i_bin] = np.nan
            # Plot the binned data
            if pl_show_error["databinned"]:
                bin_err = binstd
            else:
                bin_err = None
            ebcont_binned = ax_data_pl.errorbar(midbins, binval, yerr=bin_err, **pl_kwarg_final["databinned"])
            # I always print the data_jitter error bar even if they are identical to the normal error bars.
            if not("color" in pl_kwarg_final["databinned"]):
                pl_kwarg_final["databinned"]["color"] = ebcont_binned[0].get_color()
            if not("ecolor" in pl_kwarg_final["binned_jitter"]):
                pl_kwarg_final["binned_jitter"]["ecolor"] = pl_kwarg_final["databinned"]["color"]
            if (binstd_jitter is not None) and pl_show_error["databinned"]:
                ax_data_pl.errorbar(midbins, binval, yerr=binstd_jitter, **pl_kwarg_final["binned_jitter"])
            # Indicate values that are off y-axis with arrows
            et.indicate_y_outliers(x=midbins, y=binval, ax=ax_data_pl,
                                   color=pl_kwarg_final["databinned"]["color"],
                                   alpha=pl_kwarg_final["databinned"]["alpha"])
            # Plot the binned residuals
            ax_resi_pl.errorbar(midbins, binval_resi, yerr=bin_err, **pl_kwarg_final["databinned"])
            if (binstd_jitter is not None) and pl_show_error["databinned"]:
                ax_resi_pl.errorbar(midbins, binval_resi, yerr=binstd_jitter, **pl_kwarg_final["binned_jitter"])
            # Indicate values that are off y-axis with arrows
            et.indicate_y_outliers(x=midbins, y=binval_resi, ax=ax_resi_pl,
                                   color=pl_kwarg_final["databinned"]["color"],
                                   alpha=pl_kwarg_final["databinned"]["alpha"])
            # Plot binned model  f"{planet_name}_only"
            if show_binned_model:
                ebconts_lines_labels_model = et.plot_model(tmin=tmin_model, tmax=tmax_model, nt=npt_model,
                                                           dataset_name=datasetname, param=df_fittedval["value"],
                                                           l_param_name=list(df_fittedval.index), post_instance=post_instance,
                                                           key_obj=f"{planet_name}_only", datasim_kwargs=kwargs_dataset,
                                                           multiplication_factor=RV_fact,
                                                           supersamp=supersamp_bin_model, exptime=phase_binsize * Per,
                                                           plot_phase=True, Per=Per, tref=tc,
                                                           show_time_from_tref=False,
                                                           pl_kwargs_model=pl_kwarg_final["modelbinned"], pl_kwargs_modelandGP=pl_kwarg_final["modelbinned"],
                                                           show_modelandGP=not(remove_GP), force_plot_phase_GP=False,
                                                           ax=ax_data_pl)
                if not("color" in pl_kwarg_final["modelbinned"]):
                    pl_kwarg_final["modelbinned"]["color"] = ebconts_lines_labels_model["model"]["ebcont or line"][0].get_color()

    ###################
    # Finalise the plot
    ###################
    if show_legend:
        legend_kwargs = {"fontsize": fontsize, "idx_planet": 0}
        if legend_param is not None:
            legend_kwargs.update(legend_param)
        idx_planet = legend_kwargs.pop("idx_planet")
        ax_data[idx_planet].legend(**legend_kwargs)
