#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create plots specifically for radial velocity data

@TODO:
"""
import numpy as np
from logging import getLogger

from copy import deepcopy, copy
from collections import OrderedDict, defaultdict
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter, FuncFormatter
from PyAstronomy.pyasl import foldAt
from scipy.stats import binned_statistic


from .lc_plots import check_row4datasetname, get_pl_kwargs, update_binned_label
from ..emcee_tools import emcee_tools as et
from ..posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add
from ..posterior.core.model.core_model import Core_Model
# from ..posterior.exoplanet.model.gravgroup.datasim_creator_rv import RVdrift_tref_name

import sys
path_pyGLS = "/Users/olivier/Softwares/PyGLS"
if path_pyGLS not in sys.path:
    sys.path.append(path_pyGLS)
from gls_mod import Gls

key_whole = Core_Model.key_whole

AandA_fontsize = 8

day2sec = 24 * 60 * 60

# managers
mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()

# logger
logger = getLogger()

# Formatter for the Ticks major of the period axis
sf = ScalarFormatter(useOffset=False, useMathText=True)
sf.set_scientific(True)


def sci_not_str(x, pos):
    return f"${sf.format_data(x)}$"  # f"${sf._formatSciNotation('%1.10e' % x)}$"


fmt_sci_not = FuncFormatter(sci_not_str)


def create_RV_phasefolded_plots(fig, post_instance, df_fittedval, datasim_kwargs=None, planets=None, star_name="A",
                                datasetnames=None, row4datasetname=None,
                                plot_model_for_all_datasets=False, datasetnameformodel4row=None, npt_model=1000,
                                remove_inst_var=True, remove_stellar_var=True, remove_decorrelation=True,
                                remove_decorrelation_likelihood=True, remove_GP_dataNmodel=True, remove_GP_residual=True,
                                RV_fact=1.,
                                show_time_from_tic=False, time_fact=24, time_unit="h",
                                exptime_bin=0., binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                                one_binning_per_row=True,
                                sharey=False,
                                fig_param=None, pl_kwargs=None, show_legend=True, legend_param=None,
                                show_datasetnames=True,
                                show_system_name_in_suptitle=True,
                                show_rms_residuals_in_suptitle=True,
                                RV_unit="$km/s$"
                                ):
    """Produce clean RV phase folded plots of a system.

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
    row4datasetname    : dict of int
        Dictionary saying which dataset to plot on which row. The format is:
        {"<dataset_name>": <int giving the row index starting at 0>, ...}
    plot_model_for_all_datasets : bool
    datasetnameformodel4row : list of str
        List saying which datasetmodel to use to compute the oversampled model of each row
    npt_model     : int
        Number of points used to simulated the model
    remove_GP     : Boolean
        If True the GP model is remove from the data for the plot.
    RV_fact       : float
        Factor to apply to the RV
    exptime_bin : float
        Width of the bins used for the binning the unit of this depends on the value of show_time_from_tic.
        If show_time_from_tic is True, it's a time unit otherwise the unit is orbital phase.
        If it's a time unit then the unit depend on the unit of the data after time_fact is applied.
        For example if the time unit of the data is days and time_fact=24, the unit of exptime_bin is hours.
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
            - 'pad_data': Iterable of 2 floats (Def: (0.1, 0.1))
                Define the bottom and top pad to apply for data axes.
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
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    fontsize = fig_param.get("fontsize", AandA_fontsize)

    # Do the suptitle
    if show_system_name_in_suptitle:
        system_name = fig_param.get('system_name_4_suptitle', post_instance.full_name)
        fig.suptitle(f"{system_name} system", fontsize=fontsize)

    # Make sure that fig_param is a dictionaries
    if fig_param is None:
        fig_param = {}

    # If no dataset name is provided get all the available RV datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="RV", sortby_instcat=False, sortby_instname=False)

    # Define on which rows the datasets are plots using the row4datasetname input
    row4datasetname, datasetnames4rowidx = check_row4datasetname(row4datasetname=row4datasetname, datasetnames=datasetnames)
    nb_rows = len(datasetnames4rowidx)
    # Define which datasetname to use to compute the oversampled model to plot for each row
    if datasetnameformodel4row is None:
        datasetnameformodel4row = [None for i_row in range(nb_rows)]
    for i_row, datasetname in enumerate(datasetnameformodel4row):
        if datasetname is None:
            datasetnameformodel4row[i_row] = datasetnames4rowidx[i_row][0]
    for i_row, datasetname in enumerate(datasetnameformodel4row):
        if datasetname not in datasetnames4rowidx[i_row]:
            raise ValueError(f"Dataset {datasetname} chosen to compute the oversampled model of row {i_row} is not amongst the datasets for this row.")

    # Create the GridSpec
    gs = GridSpec(figure=fig, nrows=nb_rows, ncols=1, **fig_param.get('main_gridspec', {}))

    # If no planet name is provided get all the available RV datasets and get all the planets in the model
    all_planets = list(post_instance.model.planets.keys())
    all_planets.sort()
    if planets is None:
        planets = copy(all_planets)
    nplanet = len(planets)

    # star = post_instance.model.stars[star_name]

    # Load the defined datasets and check how many dataset there is by instrument.
    (dico_datasets, dico_kwargs, dico_nb_dstperinsts, datas, data_errs, data_err_jitters, data_err_worwojitters,
     has_jitters, dico_jitters, models, gp_preds, gp_pred_vars, inst_vars, stellar_vars, decorrs,
     decorr_likelihoods, residuals
     ) = load_datasets_and_models_RV(datasetnames=datasetnames, post_instance=post_instance, datasim_kwargs=datasim_kwargs,
                                     df_fittedval=df_fittedval, RV_fact=RV_fact, remove_inst_var=remove_inst_var,
                                     remove_stellar_var=remove_stellar_var, remove_decorrelation=remove_decorrelation,
                                     remove_decorrelation_likelihood=remove_decorrelation_likelihood,
                                     remove_GP_dataNmodel=remove_GP_dataNmodel, remove_GP_residual=remove_GP_residual)

    # Get the central phase for the plot
    phasefold_central_phase = fig_param.get("phasefold_central_phase", 0.)

    # Get the limits for the x axis for all planets and all row and set the default values
    # xlims_def = (-0.5, 0.5) if not(show_time_from_tic) else (- 10 / 24 * time_fact, 10 / 24 * time_fact)
    xlims_def = (None, None)
    xlims = fig_param.get("xlims", {})
    if isinstance(xlims, dict):
        xlims_def = xlims.pop("all", xlims_def)
        xlims_dico = xlims
    else:
        xlims_def = xlims
        xlims_dico = {}

    # Set parameters for the planets gridspec
    add_axeswithsharex_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot
    add_axeswithsharex_kw.update(fig_param.get("add_axeswithsharex_kw", {}))
    gs_from_sps_kw = {}
    gs_from_sps_kw.update(fig_param.get("gs_from_sps_kw", {}))

    # Set the plots keywords arguments for each dataset
    # Define the default values
    (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
     ) = get_pl_kwargs(pl_kwargs=pl_kwargs, dico_nb_dstperinsts=dico_nb_dstperinsts, datasetnames=datasetnames,
                       bin_size=exptime_bin, one_binning_per_row=one_binning_per_row,
                       nb_rows=nb_rows, alpha_def_data=1., color_def_data=None, show_error_data_def=True)

    #################################
    # Main row loop: For each row ...
    #################################
    axes_data, axes_resi = {}, {}
    for i_row in range(nb_rows):

        ######################################################
        # Create one pair (data, residuals) of axes per planet
        ######################################################
        (axes_data[i_row], axes_resi[i_row]
         ) = et.add_twoaxeswithsharex_perplanet(gs[i_row], nplanet=nplanet, fig=fig, sharey=sharey,
                                                gs_from_sps_kw=gs_from_sps_kw,
                                                add_axeswithsharex_kw=add_axeswithsharex_kw)

        #######################################
        # Main planet loop: For each planet ...
        #######################################
        for i_pl, planet_name in enumerate(planets):

            #####################################
            # Format ticks, set labels and titles
            #####################################
            # Set ticks
            axes_data[i_row][i_pl].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_data[i_row][i_pl].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False)
            axes_data[i_row][i_pl].xaxis.set_minor_locator(AutoMinorLocator())
            axes_data[i_row][i_pl].yaxis.set_minor_locator(AutoMinorLocator())
            axes_data[i_row][i_pl].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_data[i_row][i_pl].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            axes_resi[i_row][i_pl].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_resi[i_row][i_pl].yaxis.set_minor_locator(AutoMinorLocator())
            axes_resi[i_row][i_pl].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True)
            axes_resi[i_row][i_pl].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_resi[i_row][i_pl].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            if i_pl != 0:
                axes_data[i_row][i_pl].tick_params(axis="both", labelleft=False)
                axes_resi[i_row][i_pl].tick_params(axis="both", labelleft=False)
            # Set title with planet name on the first row
            if i_row == 0:
                axes_data[i_row][i_pl].set_title("{} {}".format("Planet", planet_name), fontsize=fontsize)
            # Set x label for the last row
            if i_row == nb_rows - 1:
                if show_time_from_tic:
                    axes_resi[i_row][i_pl].set_xlabel(f"Time from mid-transit [{time_unit}]", fontsize=fontsize)
                else:
                    axes_resi[i_row][i_pl].set_xlabel("Orbital phase", fontsize=fontsize)
            # Set y labels on the first column and align them, also set the Anchor boxes
            if i_pl == 0:
                y_str = "RV"
                ylabel_data = f"{y_str} [{RV_unit}]"
                ylabel_resi = f"O - C [{RV_unit}]"
                axes_data[i_row][i_pl].set_ylabel(ylabel_data, fontsize=fontsize)
                axes_resi[i_row][i_pl].set_ylabel(ylabel_resi, fontsize=fontsize)

            ####################################################################################################
            # Compute the x_values (time or phase depending on show_time_from_tic) associated to the time values
            ####################################################################################################
            # Get the period and time of inferior conjunction
            Per = df_fittedval.loc[post_instance.model.planets[planet_name].P.full_name]["value"]
            tc = df_fittedval.loc[post_instance.model.planets[planet_name].tic.full_name]["value"]

            # Get the limits for the x axis for all planets and all row and set the default values
            if i_row in xlims_dico:
                xlims = xlims_dico[i_row]
                if planet_name in xlims:
                    xlims = xlims[planet_name]
                else:
                    xlims = xlims_def
            elif planet_name in xlims_dico:
                xlims = xlims_dico[planet_name]
            else:
                xlims = xlims_def
            x_min, x_max = xlims

            # Compute the phase or time (x_values) corresponding to each point in each dataset and the minimum and maximum of all dataset for the row
            x_values = OrderedDict()
            x_min_data = np.inf
            x_max_data = -np.inf
            for datasetname in datasetnames4rowidx[i_row]:
                phases_dst = (foldAt(dico_kwargs[datasetname]['time'], Per, T0=(tc + Per * (phasefold_central_phase - 0.5))) + (phasefold_central_phase - 0.5))
                x_values[datasetname] = phases_dst * Per * time_fact if show_time_from_tic else phases_dst
                if np.min(x_values[datasetname]) < x_min_data:
                    x_min_data = np.min(x_values[datasetname])
                if np.max(x_values[datasetname]) > x_max_data:
                    x_max_data = np.max(x_values[datasetname])

            if x_min is not None:
                if x_min_data < x_min:
                    x_min_data = x_min
            if x_max is not None:
                if x_max_data > x_max:
                    x_max_data = x_max

            # Define the bins
            if exptime_bin > 0.:
                bin_size_unit = f" {time_unit}" if show_time_from_tic else "orb. phase"
                update_binned_label(pl_kwarg_final=pl_kwarg_final, datasetnames=datasetnames, bin_size=exptime_bin,
                                    bin_size_unit=bin_size_unit, one_binning_per_row=one_binning_per_row,
                                    nb_rows=nb_rows)
                bins = np.arange(x_min_data, x_max_data + exptime_bin, exptime_bin)
                midbins = bins[:-1] + exptime_bin / 2
                nbins = len(bins) - 1

            # Define time for evaluating the plotting the model
            tmin_model = tc + x_min_data / time_fact if show_time_from_tic else tc + Per * x_min_data
            tmax_model = tc + x_max_data / time_fact if show_time_from_tic else tc + Per * x_max_data

            #####################################################
            # Main dataset loop for the row: For each dataset ...
            #####################################################
            data_pl = OrderedDict()
            text_rms = OrderedDict()
            text_rms_binned = OrderedDict()
            rms_format = fig_param.get("rms_format", ".1e")
            for datasetname in datasetnames4rowidx[i_row]:

                ################################################################################
                # Compute the data for the planet (removing the contribution from other planets)
                ################################################################################
                data_pl[datasetname] = datas[datasetname].copy()
                # Compute and remove the other planet contribution
                for plnt in all_planets:
                    if plnt == planet_name:
                        continue
                    else:
                        (model_pl_only, _, _, _
                         ) = post_instance.compute_model(tsim=dico_kwargs[datasetname]['time'], dataset_name=datasetname,
                                                         param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                                         key_obj=f"{plnt}", datasim_kwargs=datasim_kwargs
                                                         )
                        model_pl_only *= RV_fact
                        data_pl[datasetname] = data_pl[datasetname] - model_pl_only

                ###############
                # Plot the data
                ###############
                if pl_show_error[datasetname]["data"]:
                    ebcont = axes_data[i_row][i_pl].errorbar(x_values[datasetname], y=data_pl[datasetname], yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]['data'], zorder=10)
                    if not("ecolor" in pl_kwarg_jitter[datasetname]["data"]):
                        pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
                    if not("color" in pl_kwarg_final[datasetname]["data"]):
                        pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
                    if has_jitters[datasetname]:
                        axes_data[i_row][i_pl].errorbar(x_values[datasetname], y=data_pl[datasetname], yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"], zorder=1)
                else:
                    axes_data[i_row][i_pl].errorbar(x_values[datasetname], y=data_pl[datasetname], **pl_kwarg_final[datasetname]['data'], zorder=10)

                ####################
                # Plot the residuals
                ####################
                if pl_show_error[datasetname]["data"]:
                    ebcont = axes_resi[i_row][i_pl].errorbar(x_values[datasetname], y=residuals[datasetname], yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]['data'], zorder=10)
                    if has_jitters[datasetname]:
                        axes_resi[i_row][i_pl].errorbar(x_values[datasetname], y=residuals[datasetname], yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"], zorder=1)
                else:
                    axes_resi[i_row][i_pl].errorbar(x_values[datasetname], y=residuals[datasetname], **pl_kwarg_final[datasetname]['data'], zorder=10)
                # Compute rms of the residuals and print it on the top of the residuals graphs
                text_rms_template = f"{{:{rms_format}}}"
                text_rms[datasetname] = text_rms_template.format(np.std(residuals[datasetname][np.logical_and(x_values[datasetname] > x_min_data, x_values[datasetname] < x_max_data)]))
                print(f"RMS {datasetname} (plot planet {planet_name}) = {text_rms[datasetname]} {RV_unit} (raw cadence)")

                #########################################
                # Compute and plot the oversampled  model
                #########################################
                if plot_model_for_all_datasets or (datasetnameformodel4row[i_row] == datasetname):
                    tsim = np.linspace(tmin_model, tmax_model, npt_model)
                    xsim = np.linspace(x_min_data, x_max_data, npt_model)
                    # Compute the oversampled model to plot for the raw cadence
                    model2plot, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                      dataset_name=datasetname,
                                                                      param=df_fittedval["value"].values,
                                                                      l_param_name=list(df_fittedval.index),
                                                                      key_obj=f"{planet_name}",
                                                                      datasim_kwargs=datasim_kwargs)

                    # Add inst_var if needed
                    if not(remove_inst_var) and (datasetname in inst_vars):
                        model_instvar, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                             dataset_name=datasetname,
                                                                             param=df_fittedval["value"].values,
                                                                             l_param_name=list(df_fittedval.index),
                                                                             key_obj="inst_var",
                                                                             datasim_kwargs=datasim_kwargs)
                        model2plot += model_instvar

                    # Add inst_var if needed
                    if not(remove_stellar_var) and (datasetname in stellar_vars):
                        model_stellarvar, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                                dataset_name=datasetname,
                                                                                param=df_fittedval["value"].values,
                                                                                l_param_name=list(df_fittedval.index),
                                                                                key_obj="stellar_var",
                                                                                datasim_kwargs=datasim_kwargs)
                        model2plot += model_stellarvar
                    # Add decorrelation if needed
                    if not(remove_decorrelation) and (datasetname in decorrs):
                        model_decorr, _, _, _ = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                            param=df_fittedval["value"].values,
                                                                            l_param_name=list(df_fittedval.index),
                                                                            key_obj="decorr",
                                                                            datasim_kwargs=datasim_kwargs)
                        for model_part in model_decorr:
                            if model_part == "add_2_totalrv":
                                model2plot += model_decorr['add_2_totalrv']
                            else:
                                logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
                    # Multiply by RV fact
                    model2plot *= RV_fact
                    # Plot the oversampled model to plot for the raw cadence
                    ebconts_lines_labels_model = axes_data[i_row][i_pl].errorbar(xsim, model2plot, **pl_kwarg_final[datasetname]["model"])
                    if not("color" in pl_kwarg_final[datasetname]["model"]):
                        pl_kwarg_final[datasetnames]["model"]["color"] = ebconts_lines_labels_model["model"]["ebcont or line"][0].get_color()
                    # Compute the oversampled model to plot for the binned cadence
                    if show_binned_model:
                        # Compute the exposure time for the binned model in the same unit than the data
                        # Since exptime_bin unit depends on show_time_from_tic and time_fact
                        exptime = exptime_bin / time_fact if show_time_from_tic else exptime_bin * Per
                        model2plot, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                          dataset_name=datasetname,
                                                                          param=df_fittedval["value"].values,
                                                                          l_param_name=list(df_fittedval.index),
                                                                          key_obj=f"{planet_name}",
                                                                          supersamp=supersamp_bin_model, exptime=exptime,
                                                                          datasim_kwargs=datasim_kwargs)
                        # Add inst_var if needed
                        if not(remove_inst_var) and (datasetname in inst_vars):
                            model_instvar, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                                 dataset_name=datasetname,
                                                                                 param=df_fittedval["value"].values,
                                                                                 l_param_name=list(df_fittedval.index),
                                                                                 key_obj="inst_var",
                                                                                 supersamp=supersamp_bin_model, exptime=exptime,
                                                                                 datasim_kwargs=datasim_kwargs)
                            model2plot += model_instvar
                        # Add inst_var if needed
                        if not(remove_stellar_var) and (datasetname in stellar_vars):
                            model_stellarvar, _, _, _ = post_instance.compute_model(tsim=tsim,
                                                                                    dataset_name=datasetname,
                                                                                    param=df_fittedval["value"].values,
                                                                                    l_param_name=list(df_fittedval.index),
                                                                                    key_obj="stellar_var",
                                                                                    supersamp=supersamp_bin_model, exptime=exptime,
                                                                                    datasim_kwargs=datasim_kwargs)
                            model2plot += model_stellarvar
                        # Add decorrelation if needed
                        if not(remove_decorrelation) and (datasetname in decorrs):
                            model_decorr, _, _, _ = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                                param=df_fittedval["value"].values,
                                                                                l_param_name=list(df_fittedval.index),
                                                                                key_obj="decorr",
                                                                                supersamp=supersamp_bin_model, exptime=exptime,
                                                                                datasim_kwargs=datasim_kwargs)
                            for model_part in model_decorr:
                                if model_part == "add_2_totalflux":
                                    model2plot += model_decorr['add_2_totalflux']
                                else:
                                    logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
                        # Multiply by RV fact
                        model2plot *= RV_fact
                        # Plot the oversampled model to plot for the raw cadence
                        ebconts_lines_labels_model = axes_data[i_row][i_pl].errorbar(xsim, model2plot, **pl_kwarg_final[datasetname]["modelbinned"])
                        if not("color" in pl_kwarg_final[datasetname]["modelbinned"]):
                            pl_kwarg_final[datasetnames]["modelbinned"]["color"] = ebconts_lines_labels_model["model"]["ebcont or line"][0].get_color()

                ################################################################################
                # Compute and Plot the binned data and residuals if one_binning_per_row is False
                ################################################################################
                if not(one_binning_per_row) and (exptime_bin > 0.):
                    # Compute the binned values
                    (bindata, binedges, binnb
                     ) = binned_statistic(x_values[datasetname], data_pl[datasetname],
                                          statistic=binning_stat, bins=bins,
                                          range=(x_min_data, x_max_data))
                    (binresi, binedges, binnb
                     ) = binned_statistic(x_values[datasetname], residuals[datasetname],
                                          statistic=binning_stat, bins=bins,
                                          range=(x_min_data, x_max_data))
                    # Compute the err on the binned values
                    binstd = np.zeros(nbins)
                    if has_jitters[datasetname]:
                        binstd_jitter = np.zeros(nbins)
                    bincount = np.zeros(nbins)
                    for i_bin in range(nbins):
                        bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                        if bincount[i_bin] > 0.0:
                            binstd[i_bin] = np.sqrt(np.sum(np.power((data_errs[datasetname]
                                                                     [binnb == (i_bin + 1)]),
                                                                    2.)) /
                                                    bincount[i_bin]**2)
                            if has_jitters[datasetname]:
                                binstd_jitter[i_bin] = np.sqrt(np.sum(np.power((data_err_jitters[datasetname]
                                                                                [binnb == (i_bin + 1)]),
                                                                               2.)) /
                                                               bincount[i_bin]**2)
                        else:
                            binstd[i_bin] = np.nan
                            if has_jitters[datasetname]:
                                binstd_jitter[i_bin] = np.nan
                    # Plot the binned data
                    bin_err = binstd if pl_show_error[datasetname]["databinned"] else None
                    ebcont_binned = axes_data[i_row][i_pl].errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
                    if not("color" in pl_kwarg_final[datasetname]["databinned"]):
                        pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
                    if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
                        pl_kwarg_jitter[datasetname]["databinned"]["ecolor"] = pl_kwarg_final[datasetname]["databinned"]["color"]
                    _ = axes_resi[i_row][i_pl].errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
                    if has_jitters[datasetname] and pl_show_error[datasetname]["databinned"]:
                        _ = axes_data[i_row][i_pl].errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)
                        _ = axes_resi[i_row][i_pl].errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)
                    # Compute rms of the binned residuals
                    text_rms_binned_template = f"{{:{rms_format}}} (bin)"
                    text_rms_binned[datasetname] = text_rms_binned_template.format(np.nanstd(binresi[np.logical_and(midbins > x_min_data, midbins < x_max_data)]))
                    print(f"RMS {datasetname}: {text_rms_binned[datasetname]} {RV_unit}")

            ################################################################################
            # Compute and Plot the binned data and residuals if one_binning_per_row is True
            ################################################################################
            if one_binning_per_row and (exptime_bin > 0.):
                x_values_row = np.concatenate([x_values[dst] for dst in datasetnames4rowidx[i_row]])
                # Compute the binned values
                (bindata, binedges, binnb
                 ) = binned_statistic(x_values_row, np.concatenate([data_pl[dst] for dst in datasetnames4rowidx[i_row]]),
                                      statistic=binning_stat, bins=bins,
                                      range=(x_min_data, x_max_data))
                (binresi, binedges, binnb
                 ) = binned_statistic(x_values_row, np.concatenate([residuals[dst] for dst in datasetnames4rowidx[i_row]]),
                                      statistic=binning_stat, bins=bins,
                                      range=(x_min_data, x_max_data))
                # Compute the err on the binned values
                binstd = np.zeros(nbins)
                if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]):
                    binstd_jitter = np.zeros(nbins)
                bincount = np.zeros(nbins)
                data_err_row = np.concatenate([data_errs[dst] for dst in datasetnames4rowidx[i_row]])
                data_err_jitter_row = np.concatenate([data_err_jitters[dst] if has_jitters[dst] else np.ones_like(data_errs[dst]) * np.nan for dst in datasetnames4rowidx[i_row]])
                for i_bin in range(nbins):
                    bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                    if bincount[i_bin] > 0.0:
                        binstd[i_bin] = np.sqrt(np.sum(np.power((data_err_row
                                                                 [binnb == (i_bin + 1)]),
                                                                2.)) /
                                                bincount[i_bin]**2)
                        if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]):
                            binstd_jitter[i_bin] = np.sqrt(np.nansum(np.power((data_err_jitter_row
                                                                               [binnb == (i_bin + 1)]),
                                                                              2.)) /
                                                           bincount[i_bin]**2)
                    else:
                        binstd[i_bin] = np.nan
                        if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]):
                            binstd_jitter[i_bin] = np.nan
                # Plot the binned data
                bin_err = binstd if pl_show_error[f"row{i_row}"] else None
                ebcont_binned = axes_data[i_row][i_pl].errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
                if not("color" in pl_kwarg_final[f"row{i_row}"]):
                    pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
                if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
                    pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
                _ = axes_resi[i_row][i_pl].errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
                if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]) and pl_show_error[f"row{i_row}"]:
                    _ = axes_data[i_row][i_pl].errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)
                    _ = axes_resi[i_row][i_pl].errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)
                # Compute rms of the binned residuals
                text_rms_binned_template = f"{{:{rms_format}}} (bin)"
                text_rms_binned[f"row{i_row}"] = text_rms_binned_template.format(np.nanstd(binresi[np.logical_and(midbins > x_min_data, midbins < x_max_data)]))
                print(f"RMS row {i_row}: {text_rms_binned[f'row{i_row}']} {RV_unit}")

            ###########
            # Write rms
            ###########
            # WARNING, TO BE IMPROVED for more than one dataset
            show_rms = True
            if show_rms:
                text_rms_to_plot = ""
                for i_dst, datasetname in enumerate(datasetnames4rowidx[i_row]):
                    # text_rms_to_plot_dst = f"{pl_kwarg_final[datasetname]['data']['label']}: {text_rms[datasetname]}"
                    text_rms_to_plot_dst = f"{pl_kwarg_final[datasetname]['data']['label']}: {text_rms[datasetname]}"
                    if datasetname in text_rms_binned:
                        text_rms_to_plot_dst += f", {text_rms_binned[datasetname]} (bin)"
                    if (i_pl == 0) and (i_dst == 0):
                        text_rms_to_plot_dst = "rms = " + text_rms_to_plot_dst
                    if RV_unit is not None:
                        text_rms_to_plot_dst += f" {RV_unit}"
                    text_rms_to_plot += text_rms_to_plot_dst + "; "
                if f"row{i_row}" in text_rms_binned:
                    text_rms_to_plot += "\n"
                    if i_pl == 0:
                        text_rms_to_plot += f"rms bin = {text_rms_binned[f'row{i_row}']} {RV_unit}"
                axes_resi[i_row][i_pl].text(0.0, 1.05, text_rms_to_plot, fontsize=fontsize, transform=axes_resi[i_row][i_pl].transAxes)

            # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
            default_ylims = None
            default_pad = (0.1, 0.1)
            for axe, data_or_resi, points, in zip((axes_data[i_row][i_pl], axes_resi[i_row][i_pl]),
                                                  ("data", "resi"),
                                                  (data_pl, residuals),
                                                  ):
                # Set teh y axis limits
                ylims = fig_param.get(f"ylims_{data_or_resi}", {})
                if isinstance(ylims, dict):
                    if i_row in ylims:
                        ylims = ylims[i_row]
                        if planet_name in ylims:
                            ylims = ylims[planet_name]
                        else:
                            ylims = default_ylims
                    elif planet_name in ylims:
                        ylims = ylims[planet_name]
                    else:
                        ylims = default_ylims
                if ylims is None:
                    pad_data = fig_param.get(f"pad_{data_or_resi}", {})
                    if isinstance(pad_data, dict):
                        if i_row in pad_data:
                            pad_data = pad_data[i_row]
                            if planet_name in pad_data:
                                pad_data = pad_data[planet_name]
                            else:
                                pad_data = default_pad
                        elif planet_name in pad_data:
                            pad_data = pad_data[planet_name]
                        else:
                            pad_data = default_pad
                    points_pl_i_row = np.concatenate([points[datasetname] for datasetname in datasetnames4rowidx[i_row]])
                    et.auto_y_lims(points_pl_i_row, axe, pad=pad_data)
                else:
                    axe.set_ylim(ylims)
                # Indicate outlier values that are off y-axis with an arrows for raw cadence
                if fig_param.get(f"indicate_y_outliers_{data_or_resi}", True):
                    for datasetname in datasetnames4rowidx[i_row]:
                        et.indicate_y_outliers(x=x_values[datasetname], y=points[datasetname], ax=axe,
                                               color=pl_kwarg_final[datasetname]["data"]["color"],
                                               alpha=pl_kwarg_final[datasetname]["data"]["alpha"])

            # Set the x axis limits
            axes_data[i_row][i_pl].set_xlim((x_min_data, x_max_data))

    ###################
    # Finalise the plot
    ###################

    # Show legend
    if show_legend:
        legend_kwargs = {"fontsize": fontsize, "idx_planet": 0}
        idx_planet = legend_kwargs.pop("idx_planet")
        for i_row in range(nb_rows):
            axes_data[i_row][idx_planet].legend(**legend_kwargs)


def create_RV_TSNGLSP_plots(fig, post_instance, df_fittedval, datasim_kwargs=None, planets=None, star_name="A",
                            datasetnames=None,
                            remove_inst_var=False, remove_stellar_var=False, remove_decorrelation=True,
                            remove_decorrelation_likelihood=True,
                            remove_GP_dataNmodel=True, remove_GP_residual=True,
                            fig_param=None, TS_kwargs=None, GLSP_kwargs=None,
                            show_system_name_in_suptitle=True,
                            RV_fact=1., RV_unit="$km/s$",
                            ):
    """Produce clean RV time series and generalized Lomb-Scargle plots of a system.

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
    fig_param     : dict
        Dictionary providing keyword arguments for the figure definition and settings. The possible keys are
            - 'system_name_4_suptitle': Name that you want to use for the suptitle if different from the post_instance name
            - 'gridspec_kwargs': The content of this entry should be a dictionary which will be passed to
                GridSpec (GridSpec(..., **fig_param['gridspec_kwargs'])) instance creation with create the gridspec
                separating the TS and GLSP
            - 'add_axeswithsharex_kw': The content of this entry should be a dictionary which will be
                passed to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., add_axeswithsharex_kw=fig_param['add_axeswithsharex_kw'])
                function creating two axes data and residuals per planet.
            - 'fontsize' : Int specifiying the fontsize
            - 'suptitle_kwargs': to pass kwargs to the suptitle command
    remove_inst_var  : bool
        If True remove the instrumental variations
    remove_stellar_var  : bool
        If True remove the systemic velocity and the stellar variations
    remove_decorrelation  : bool
        If True remove the model decorrelation
    remove_decorrelation_likelihood  : bool
        If True remove the likelihood decorrelation
    remove_GP_data  : bool
        If True remove the GP model from the data
    remove_GP_residual  : bool
        If True remove the GP model from the residuals
    TS_kwargs     : None or dict
            - 'do': boolean (Def: True)
            - 'npt_model': int (Def: 1000) giving the number of points to use for the model
            - 'extra_dt_model': float (Def: 0)
                Specify the extra time that for which you want to compute the model before and after the
                data.
            - 't_lims': None or Iterable of 2 float (Def: None)
                Specificy the time limits for the plot
            - 't_lims_zoom': None or Iterable of 2 float (Def: None)
                If provided a zoom on the right of the main plot will be drawn.
                This gives the beginning and end time for the zoom
            - 't_unit': str (Def: days)
                String that is going to be used to give the unit (and reference system) of the time.
            - 'pl_kwargs': dict
                Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "GP"
                and values a dictionary that will be passed as keyword arguments associated the plotting functions.
                You can also add a 'jitter' key with value a dictionary that will contain the changes that you
                want to make for the update error bars due to potential jitter.
                Finally you can use the 'show_error' keyword with value True or False to specify if you want
                the error bars of the dataset to be plotted.
            - 'pad_data': Iterable of 2 floats (Def: (0.1, 0.1))
                Define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
            - 'pad_resi': Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
            - 'indicate_y_outliers_data': boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
            - 'indicate_y_outliers_resi': boolean. If True, residuals outliers (outside of the plot) are indicated
                by arrows.
            - 'title_kwargs': to pass kwargs to the title command
            - 'show_legend'  : bool
                If True, show the legend
            - 'show_title'  : bool
                If True, show the titles (of the main and the zoom)
            - 'legend_param' : dict
                Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True).
            - 'show_rms_residuals_in_title': bool
               If True the rms of the residuals will be provided in the title.
            - 'rms_format': Format that will be used to format the rms values (for example '.0f')
            - 'gridspec_kwargs': dict
                The content of this entry should be a dictionary which will be passed to
                GridSpecFromSubplotSpec (GridSpecFromSubplotSpec(..., **TS_kwargs['gridspec_kwargs'])) which
                create the gridspec separating the full and zoom GLSP columns
            - 'axeswithsharex_kwargs': dict
                The content of this entry should be a dictionary which will be passed to
                et.add_twoaxeswithsharex(... gs_from_sps_kw=TS_kwargs['axeswithsharex_kwargs']) which
                creates the data and residuals axes.
    GLSP_kwargs   : None or dict
            - 'do': boolean (Def: True)
            - 'use_jitter': boolen (Def: True)
                If True it uses the error bars with jitter to compute the GLSP and the FAP levels
            - 'period_range': Iterable of 2 float providing the beginning and end period for the computation
                of the GLSP
            - 'freq_fact': float (Def: 1e6)
                Factor to apply to the frequency for example to plot them in micro Hertz
            - 'freq_unit': str  (Def: "$\\mu$Hz"),
                Unit to display on the frequency axis. Must be coherent with freq_fact !
            - 'freq_lims': None or Iterable of 2 float (Def: None)
                Specificy the frequency limits for the plot in freq_unit
            - 'logscale': boolean (Def: False),
            - 'show_WF': boolean (Def: True),
            - 'periods': dict
                Specify the periods for which you want to draw a vertical line.
                The keys are the period values and the values are dict that can be empty or specify the
                values of the following keywords:
                - 'color': str giving the color of the line
                - 'linestyle': str giving the style of the line
                - 'label': str giving the label to plot
                - 'align': str ('left', 'right', 'center') the horizontal alignment of the label compared to the vertical line
                - 'xshift': float x shift of the label
                - 'yshift': float y shift of the label
            - 'fap': dict
                Specify the fap levels for which you want to draw a horizontal line.
                The keys are the fap level values and the values are dict that can be empty or specify the
                values of the following keywords:
                - 'color': str giving the color of the line
                - 'linestyle': str giving the style of the line
                - 'label': int (0: don't show, 1: only the fap value, 2: fap value followed by %)
                - 'align': str ('top', 'center', 'bottom') the horizontal alignment of the label compared to the vertical line
                - 'xshift': float x shift of the label
                - 'yshift': float y shift of the label
            - 'freq_lims_zoom': None or Iterable of 2 float (Def: None)
                If provided a zoom on the right of the main plot will be drawn.
                This gives the beginning and end time for the zoom
            - 'scientific_notation_P_axis': boolean (default: True)
                If True the tick label on the period axis are in scientific notations
            - 'period_no_ticklabels': list of int
                list of decades to for which you don't want to show the tick label
            - 'period_no_ticklabels_zoom': list of int
                list of decades to for which you don't want to show the tick label for the zoom
            - 'gridspec_kwargs': dict
                The content of this entry should be a dictionary which will be passed to
                GridSpecFromSubplotSpec (GridSpecFromSubplotSpec(..., **GLSP_kwargs['gridspec_kwargs'])) which
                create the gridspec separating the full and zoom GLSP columns
            - 'axeswithsharex_kwargs': dict
                The content of this entry should be a dictionary which will be passed to
                et.add_axeswithsharex(... gs_from_sps_kw=TS_kwargs['axeswithsharex_kwargs']) which
                creates the different GLSP axes for the data, model ...
            - 'legend_param': dict of dict
                Dictionary with key in ('data', 'model', 'resi', 'GP', 'WF') and values dictionaries that
                will be passed on to legend ( legend(.., **GLSP_kwargs['legend_param'][key]))
    show_system_name_in_suptitle : bool
        If True show the system name in the suptitle
    RV_fact       : float
        Factor to apply to the RV
    RV_unit        : str
        String giving the unit of the RVs
    """
    star = post_instance.model.stars[star_name]

    ###
    # Setup figure structure and common parameters
    ###
    if fig_param is None:
        fig_param = {}
    fontsize = fig_param.get("fontsize", AandA_fontsize)

    # Make sure that the TS_kwargs and GLSP_kwargs are dictionaries
    TS_kwargs = {} if TS_kwargs is None else TS_kwargs
    GLSP_kwargs = {} if GLSP_kwargs is None else GLSP_kwargs

    # Create The GridSpec
    gs = GridSpec(nrows=1, ncols=int(TS_kwargs.get("do", True)) + int(GLSP_kwargs.get("do", True)),
                  figure=fig, **fig_param.get('gridspec_kwargs', {}))
    if TS_kwargs.get("do", True):
        gs_ts = gs[0]
        if GLSP_kwargs.get("do", True):
            gs_gls = gs[1]
    else:
        gs_gls = gs[0]

    # If no dataset name is provided get all the available RV datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="RV", sortby_instcat=False, sortby_instname=False)

    # Load the defined datasets and check how many dataset there is by instrument.
    (dico_datasets, dico_kwargs, dico_nb_dstperinsts, datas, data_errs, data_err_jitters, data_err_worwojitters,
     has_jitters, dico_jitters, models, gp_preds, gp_pred_vars, inst_vars, stellar_vars, decorrs,
     decorr_likelihoods, residuals
     ) = load_datasets_and_models_RV(datasetnames=datasetnames, post_instance=post_instance, datasim_kwargs=datasim_kwargs,
                                     df_fittedval=df_fittedval, RV_fact=RV_fact, remove_inst_var=remove_inst_var,
                                     remove_stellar_var=remove_stellar_var, remove_decorrelation=remove_decorrelation,
                                     remove_decorrelation_likelihood=remove_decorrelation_likelihood,
                                     remove_GP_dataNmodel=remove_GP_dataNmodel, remove_GP_residual=remove_GP_residual)

    # Do the suptitle
    suptitle_text = ""
    if show_system_name_in_suptitle:
        system_name = fig_param.get('system_name_4_suptitle', post_instance.full_name)
        suptitle_text = f"{system_name} system"
    removed_from_model_text = ""
    for compo, asked2removed, compo_models in zip(["Stellar var", "Inst var", "Decorrelation", "GP"],
                                                  [remove_stellar_var, remove_inst_var, remove_decorrelation, remove_GP_dataNmodel],
                                                  [stellar_vars, inst_vars, decorrs, gp_preds],
                                                  ):
        if asked2removed and len(compo_models) > 0:
            if removed_from_model_text != "":
                removed_from_model_text += ", "
            removed_from_model_text += compo
    if removed_from_model_text != "":
        removed_from_model_text += " removed from model"
    if removed_from_model_text != "":
        if suptitle_text != "":
            suptitle_text += f"\n{removed_from_model_text}"
        else:
            suptitle_text = removed_from_model_text
    removed_from_data_text = ""
    for compo, asked2removed, compo_models in zip(["Stellar var", "Inst var", "Decorrelation", "Decorrelation Likelihood", "GP"],
                                                  [remove_stellar_var, remove_inst_var, remove_decorrelation, remove_decorrelation_likelihood, remove_GP_dataNmodel],
                                                  [stellar_vars, inst_vars, decorrs, decorr_likelihoods, gp_preds],
                                                  ):
        if asked2removed and len(compo_models) > 0:
            if removed_from_data_text != "":
                removed_from_data_text += ", "
            removed_from_data_text += compo
    if removed_from_data_text != "":
        removed_from_data_text += " removed from data"
    if removed_from_data_text != "":
        if suptitle_text != "":
            suptitle_text += f"\n{removed_from_data_text}"
        else:
            suptitle_text = removed_from_data_text
    if suptitle_text != "":
        fig.suptitle(suptitle_text, fontsize=fontsize)

    ################
    # RV TIME SERIES
    ################
    if TS_kwargs.get("do", True):

        ################################################
        # Create additional axe if zoom and several rows
        ################################################
        # Define on which rows the datasets are plots using the row4datasetname input
        row4datasetname, datasetnames4rowidx = check_row4datasetname(row4datasetname=TS_kwargs.get("row4datasetname", None), datasetnames=datasetnames)
        nb_rows = len(datasetnames4rowidx)
        # Create the updated grid space according to the number of rows
        gs_ts = GridSpecFromSubplotSpec(nb_rows, 1, subplot_spec=gs_ts, **TS_kwargs.get('gridspec_kwargs', {}))
        # Determine which rows require a zoom.
        if TS_kwargs.get("t_lims", None) is None:
            t_lims = [None for row in range(nb_rows)]
        else:
            if isinstance(TS_kwargs["t_lims"], dict):
                t_lims = [TS_kwargs["t_lims"][row] for row in range(nb_rows)]
            else:
                if nb_rows == 1:
                    t_lims = [TS_kwargs["t_lims"], ]
                else:
                    raise ValueError("Since theer is more than one row, TS_kwargs['t_lims'] should be a dictionary.")
        if TS_kwargs.get("t_lims_zoom", None) is None:
            t_lims_zoom = [None for row in range(nb_rows)]
        else:
            if isinstance(TS_kwargs["t_lims_zoom"], dict):
                t_lims_zoom = [TS_kwargs["t_lims_zoom"][row] for row in range(nb_rows)]
            else:
                if nb_rows == 1:
                    t_lims_zoom = [TS_kwargs["t_lims_zoom"], ]
                else:
                    raise ValueError("Since theer is more than one row, TS_kwargs['t_lims_zoom'] should be a dictionary.")
        # Infer from t_lims_zoom how many columns are required
        if any([zoom is not None for zoom in t_lims_zoom]):
            nb_cols = 2
        else:
            nb_cols = 1

        # Set the binning variables
        one_binning_per_row = TS_kwargs.get("one_binning_per_row", False)
        exptime_bin = TS_kwargs.get("exptime_bin", 0.)
        binning_stat = TS_kwargs.get("binning_stat", "mean")
        time_unit = TS_kwargs.get('t_unit', 'days')

        ##############################################
        # Set the arguments for the plotting functions
        ##############################################
        pl_kwargs = TS_kwargs.get('pl_kwargs', {})
        (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
         ) = get_pl_kwargs(pl_kwargs=pl_kwargs, dico_nb_dstperinsts=dico_nb_dstperinsts,
                           datasetnames=datasetnames, bin_size=exptime_bin, one_binning_per_row=one_binning_per_row,
                           nb_rows=nb_rows, alpha_def_data=1, color_def_data=None, show_error_data_def=True)
        update_binned_label(pl_kwarg_final=pl_kwarg_final, datasetnames=datasetnames, bin_size=exptime_bin,
                            bin_size_unit=f" {time_unit}", one_binning_per_row=one_binning_per_row,
                            nb_rows=nb_rows)

        #############################################################
        # Make the RV and residuals plots (full and zoomed if needed)
        #############################################################
        show_title = TS_kwargs.get("show_title", True)
        for i_row in range(nb_rows):
            gs_ts_row = GridSpecFromSubplotSpec(1, nb_cols, subplot_spec=gs_ts[i_row], **TS_kwargs.get('gridspec_kwargs', {}))
            for i_col in range(nb_cols):
                gs_ts_i = gs_ts_row[i_col]
                if i_col == 0:
                    t_lims_i = t_lims[i_row]
                else:  # i_col == 1
                    t_lims_i = t_lims_zoom[i_row]
                # Create the data and residuals axes and set properties ans style
                (axe_data, axe_resi) = et.add_twoaxeswithsharex(gs_ts_i, fig, gs_from_sps_kw=TS_kwargs.get('axeswithsharex_kwargs', {}))  # gs_from_sps_kw={"wspace": 0.1}

                if show_title and (i_row == 0):
                    axe_data.set_title("RV time series", fontsize=fontsize)
                axe_resi.set_xlabel(f"time [{time_unit}]", fontsize=fontsize)
                if i_col == 0:
                    y_str = "RV"
                    ylabel_data = f"{y_str} [{RV_unit}]" if RV_unit is not None else f"{y_str}"
                    ylabel_resi = f"O - C [{RV_unit}]" if RV_unit is not None else "O - C"
                    axe_data.set_ylabel(ylabel_data, fontsize=fontsize)
                    axe_resi.set_ylabel(ylabel_resi, fontsize=fontsize)

                axe_data.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False, labelsize=fontsize)
                axe_data.xaxis.set_minor_locator(AutoMinorLocator())
                axe_data.yaxis.set_minor_locator(AutoMinorLocator())
                axe_data.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
                axe_data.grid(axis="y", color="black", alpha=.5, linewidth=.5)
                axe_resi.yaxis.set_minor_locator(AutoMinorLocator())
                axe_resi.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelsize=fontsize)
                axe_resi.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
                axe_resi.grid(axis="y", color="black", alpha=.5, linewidth=.5)

                for datasetname in datasetnames4rowidx[i_row]:
                    ###################
                    # Compute the models
                    ###################
                    npt_model = TS_kwargs.get("npt_model", 1000)
                    tsim = np.linspace(np.min(dico_kwargs[datasetname]['time']) - TS_kwargs.get("extra_dt_model", 0.),
                                       np.max(dico_kwargs[datasetname]['time']) + TS_kwargs.get("extra_dt_model", 0.),
                                       npt_model)

                    model, model_wGP, gp_pred, gp_pred_var = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                                         param=df_fittedval["value"].values,
                                                                                         l_param_name=list(df_fittedval.index),
                                                                                         key_obj=key_whole,
                                                                                         datasim_kwargs=datasim_kwargs)

                    # stellar_var
                    if (datasetname in stellar_vars):
                        model_stellarvar, _, _, _ = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                                param=df_fittedval["value"].values,
                                                                                l_param_name=list(df_fittedval.index),
                                                                                key_obj="stellar_var",
                                                                                datasim_kwargs=datasim_kwargs)

                    # inst_var
                    if (datasetname in inst_vars):
                        model_instvar, _, _, _ = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                             param=df_fittedval["value"].values,
                                                                             l_param_name=list(df_fittedval.index),
                                                                             key_obj="inst_var",
                                                                             datasim_kwargs=datasim_kwargs)

                    # decorr
                    if (datasetname in decorrs):
                        model_decorr, _, _, _ = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                                            param=df_fittedval["value"].values,
                                                                            l_param_name=list(df_fittedval.index),
                                                                            key_obj="decorr",
                                                                            datasim_kwargs=datasim_kwargs)

                    # Remove the decorrelation:
                    if (datasetname in decorrs) and remove_decorrelation:
                        for model_part in model_decorr:
                            if model_part == "add_2_totalrv":
                                model -= model_decorr['add_2_totalrv']
                                if model_wGP is not None:
                                    model_wGP -= model_decorr['add_2_totalrv']
                            else:
                                logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")

                    # Remove the stellar_var if required
                    if datasetname in stellar_vars:
                        if remove_stellar_var:
                            model -= model_stellarvar
                            if model_wGP is not None:
                                model_wGP -= model_stellarvar
                        else:
                            if model_wGP is not None:
                                gp_pred += model_stellarvar
                                pl_kwarg_final[datasetname]["GP"]['label'] += " + stellar"

                    # Remove the inst_var if required
                    if datasetname in inst_vars:
                        if remove_inst_var:
                            model -= model_instvar
                            if model_wGP is not None:
                                model_wGP -= model_instvar
                        else:
                            if model_wGP is not None:
                                gp_pred += model_instvar
                                pl_kwarg_final[datasetname]["GP"]['label'] += " + inst."

                    # Multiply by LC fact
                    model *= RV_fact
                    if (datasetname in inst_vars):
                        model_instvar *= RV_fact
                    if (datasetname in stellar_vars):
                        model_stellarvar *= RV_fact
                    if (datasetname in decorrs):
                        for model_part in model_decorr:
                            if model_part == "add_2_totalrv":
                                model_decorr["add_2_totalrv"] *= RV_fact
                        # Else is already addressed above
                    if model_wGP is not None:
                        model_wGP *= RV_fact
                        gp_pred *= RV_fact
                        gp_pred_var *= RV_fact**2

                    #####################################
                    # Plot the model and the GP if needed
                    #####################################
                    line_model = axe_data.errorbar(tsim, model, **pl_kwarg_final[datasetname]["model"], zorder=20)
                    if not("color" in pl_kwarg_final[datasetname]["model"]):
                        pl_kwarg_final[datasetname]["model"]["color"] = line_model[0].get_color()
                    if not("alpha" in pl_kwarg_final[datasetname]["model"]):
                        pl_kwarg_final[datasetname]["model"]["alpha"] = line_model[0].get_alpha()
                    if model_wGP is not None:
                        if not("color" in pl_kwarg_final[datasetname]["GP"]):
                            pl_kwarg_final[datasetname]["GP"]["color"] = pl_kwarg_final[datasetname]["model"]["color"]
                        if not("alpha" in pl_kwarg_final[datasetname]["GP"]):
                            pl_kwarg_final[datasetname]["GP"]["alpha"] = pl_kwarg_final[datasetname]["model"]["alpha"] / 2
                        if not(remove_GP_dataNmodel):
                            pl_kwarg_final[datasetname]["GP"].pop("label")
                            _ = axe_data.errorbar(tsim, model_wGP, **pl_kwarg_final[datasetname]["modelwGP"], zorder=20)
                            _ = axe_data.fill_between(tsim, model_wGP - np.sqrt(gp_pred_var), model_wGP + np.sqrt(gp_pred_var),
                                                      **pl_kwarg_final[datasetname]["GP"],
                                                      # color=pl_kwarg_final[datasetname]["GP"]["color"], alpha=pl_kwarg_final[datasetname]["GP"]["alpha"],
                                                      # label=pl_kwarg_final[datasetname]["GP"]["label"],  # **kwarg_GP_pred_var
                                                      zorder=0
                                                      )
                        else:
                            _ = axe_data.errorbar(tsim, gp_pred, **pl_kwarg_final[datasetname]["GP"], zorder=20)
                            pl_kwarg_final[datasetname]["GP"].pop("label")
                            _ = axe_data.fill_between(tsim, gp_pred - np.sqrt(gp_pred_var), gp_pred + np.sqrt(gp_pred_var),
                                                      **pl_kwarg_final[datasetname]["GP"], zorder=0
                                                      )

                    #############################
                    # Plot the inst_var if needed
                    #############################
                    if (datasetname in stellar_vars) and not(remove_stellar_var):
                        _ = axe_data.plot(tsim, model_stellarvar, **pl_kwarg_final[datasetname]["stellar_var"])

                    #############################
                    # Plot the inst_var if needed
                    #############################
                    if (datasetname in inst_vars) and not(remove_inst_var):
                        _ = axe_data.plot(tsim, model_instvar, **pl_kwarg_final[datasetname]["inst_var"])

                    ########################################
                    # Plot the decorrelation model if needed
                    ########################################
                    if (datasetname in decorrs) and not(remove_decorrelation):
                        for model_part in decorrs[datasetname]:
                            if model_part == "add_2_totalflux":
                                pl_kwarg_final_decorr_model_part = deepcopy(pl_kwarg_final[datasetname]["decorr"])
                                pl_kwarg_final_decorr_model_part.update(pl_kwargs.get(f"decorr_{model_part}", {}))
                                _ = axe_data.plot(tsim, model_decorr["add_2_totalflux"], **pl_kwarg_final_decorr_model_part)
                            # Else is already addressed above

                    ###############
                    # Plot the data
                    ###############
                    if pl_show_error[datasetname]['data']:
                        ebcont = axe_data.errorbar(dico_kwargs[datasetname]['time'], y=datas[datasetname],
                                                   yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)  # Plot the data point and error bars without jitter
                        if not("ecolor" in pl_kwarg_jitter[datasetname]):
                            pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
                        if not("color" in pl_kwarg_final[datasetname]):
                            pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
                        if has_jitters[datasetname]:
                            axe_data.errorbar(dico_kwargs[datasetname]['time'], y=datas[datasetname],
                                              yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"], zorder=1)  # Plot the error bars with jitter

                    else:
                        axe_data.errorbar(dico_kwargs[datasetname]['time'], y=datas[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)  # Plot the data point and error bars without jitter

                    ####################
                    # Plot the residuals
                    ####################
                    if pl_show_error[datasetname]['data']:
                        if has_jitters[datasetname]:
                            axe_resi.errorbar(dico_kwargs[datasetname]['time'], y=residuals[datasetname], yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"])  # Plot the error bars with jitter
                        axe_resi.errorbar(dico_kwargs[datasetname]['time'], y=residuals[datasetname], yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]["data"])
                    else:
                        axe_resi.errorbar(dico_kwargs[datasetname]['time'], y=residuals[datasetname], **pl_kwarg_final[datasetname]["data"])

                    ################################################################################
                    # Compute and Plot the binned data and residuals if one_binning_per_row is False
                    ################################################################################
                    if not(one_binning_per_row) and (exptime_bin > 0.):
                        t_min_data, t_max_data = (min(dico_kwargs[datasetname]['time']), max(dico_kwargs[datasetname]['time']))
                        bins = np.arange(t_min_data, t_max_data + exptime_bin, exptime_bin)
                        midbins = bins[:-1] + exptime_bin / 2
                        nbins = len(bins) - 1
                        # Compute the binned values
                        (bindata, binedges, binnb
                         ) = binned_statistic(dico_kwargs[datasetname]['time'], datas[datasetname],
                                              statistic=binning_stat, bins=bins,
                                              range=(t_min_data, t_max_data))
                        (binresi, binedges, binnb
                         ) = binned_statistic(dico_kwargs[datasetname]['time'], residuals[datasetname],
                                              statistic=binning_stat, bins=bins,
                                              range=(t_min_data, t_max_data))
                        # Compute the err on the binned values
                        binstd = np.zeros(nbins)
                        if has_jitters[datasetname]:
                            binstd_jitter = np.zeros(nbins)
                        bincount = np.zeros(nbins)
                        for i_bin in range(nbins):
                            bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                            if bincount[i_bin] > 0.0:
                                binstd[i_bin] = np.sqrt(np.sum(np.power((data_errs[datasetname]
                                                                         [binnb == (i_bin + 1)]),
                                                                        2.)) /
                                                        bincount[i_bin]**2)
                                if has_jitters[datasetname]:
                                    binstd_jitter[i_bin] = np.sqrt(np.sum(np.power((data_err_jitters[datasetname]
                                                                                    [binnb == (i_bin + 1)]),
                                                                                   2.)) /
                                                                   bincount[i_bin]**2)
                            else:
                                binstd[i_bin] = np.nan
                                if has_jitters[datasetname]:
                                    binstd_jitter[i_bin] = np.nan
                        # Plot the binned data
                        bin_err = binstd if pl_show_error[datasetname]["databinned"] else None
                        ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
                        if not("color" in pl_kwarg_final[datasetname]["databinned"]):
                            pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
                        if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
                            pl_kwarg_jitter[datasetname]["databinned"] = pl_kwarg_final[datasetname]["databinned"]["color"]
                        _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
                        if has_jitters[datasetname] and pl_show_error[datasetname]["databinned"]:
                            _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)
                            _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)

                ################################################################################
                # Compute and Plot the binned data and residuals if one_binning_per_row is True
                ################################################################################
                if one_binning_per_row and (exptime_bin > 0.):
                    t_row = np.concatenate([dico_kwargs[dst]['time'] for dst in datasetnames4rowidx[i_row]])
                    t_min_data, t_max_data = (min(t_row), max(t_row))
                    bins = np.arange(t_min_data, t_max_data + exptime_bin, exptime_bin)
                    midbins = bins[:-1] + exptime_bin / 2
                    nbins = len(bins) - 1
                    # Compute the binned values
                    (bindata, binedges, binnb
                     ) = binned_statistic(t_row, np.concatenate([datas[dst] for dst in datasetnames4rowidx[i_row]]),
                                          statistic=binning_stat, bins=bins,
                                          range=(t_min_data, t_max_data))
                    (binresi, binedges, binnb
                     ) = binned_statistic(t_row, np.concatenate([residuals[dst] for dst in datasetnames4rowidx[i_row]]),
                                          statistic=binning_stat, bins=bins,
                                          range=(t_min_data, t_max_data))
                    # Compute the err on the binned values
                    binstd = np.zeros(nbins)
                    if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                        binstd_jitter = np.zeros(nbins)
                    bincount = np.zeros(nbins)
                    data_err_row = np.concatenate([dico_kwargs[dst]['flux_err'] for dst in datasetnames4rowidx[i_row]])
                    data_err_jitter_row = np.concatenate([data_err_jitters[dst] if has_jitters[dst] else np.ones_like(dico_kwargs[dst]['flux_err']) * np.nan for dst in datasetnames4rowidx[i_row]])
                    for i_bin in range(nbins):
                        bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                        if bincount[i_bin] > 0.0:
                            binstd[i_bin] = np.sqrt(np.sum(np.power((data_err_row
                                                                     [binnb == (i_bin + 1)]),
                                                                    2.)) /
                                                    bincount[i_bin]**2)
                            if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                                binstd_jitter[i_bin] = np.sqrt(np.sum(np.power((data_err_jitter_row
                                                                                [binnb == (i_bin + 1)]),
                                                                               2.)) /
                                                               bincount[i_bin]**2)
                        else:
                            binstd[i_bin] = np.nan
                            if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                                binstd_jitter[i_bin] = np.nan
                    # Plot the binned data
                    bin_err = binstd if pl_show_error[f"row{i_row}"] else None
                    ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
                    if not("color" in pl_kwarg_final[f"row{i_row}"]):
                        pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
                    if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
                        pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
                    _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
                    if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]) and pl_show_error[f"row{i_row}"]:
                        _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)
                        _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)

                # Draw a horizontal line at the level of reference stellar flux level
                xlims = axe_data.get_xlim()
                reference_stellar_flux = 0 if TS_kwargs.get("remove1", True) else 1
                axe_data.hlines(reference_stellar_flux, *xlims, colors="k", linestyles="dashed")

                # Adjust the y lims for the data plot
                ylims_data = TS_kwargs.get("ylims_data", None)
                if ylims_data is None:
                    pad_data = TS_kwargs.get("pad_data", (0.1, 0.1))
                    et.auto_y_lims(np.concatenate([datas[dst] for dst in datasetnames4rowidx[i_row]]), axe_data,
                                   pad=pad_data)
                else:
                    axe_data.set_ylim(ylims_data)

                # Indicate values that are off y-axis with an arrows in the data plot
                # This should be here an not in the previous for datasetname in datasetnames4rowidx[i_row] loop because the
                # y_lims can change after each dataset
                if TS_kwargs.get("indicate_y_outliers_data", True):
                    for datasetname in datasetnames4rowidx[i_row]:
                        et.indicate_y_outliers(x=dico_kwargs[datasetname]['time'], y=datas[datasetname],
                                               ax=axe_data, color=pl_kwarg_final[datasetname]["data"].get("color", None),
                                               alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))

                # Draw a horizontal line at 0 in the residual plot
                axe_resi.hlines(0, *xlims, colors="k", linestyles="dashed")

                # Adjust the y lims for the residuals plot
                ylims_resi = TS_kwargs.get("ylims_resi", None)
                if ylims_resi is None:
                    pad_resi = TS_kwargs.get("pad_resi", (0.1, 0.1))
                    et.auto_y_lims(np.concatenate([residuals[dst] for dst in datasetnames]), axe_resi,
                                   pad=pad_resi)
                else:
                    axe_resi.set_ylim(ylims_resi)

                # Indicate values that are off y-axis with an arrows in the residuals plot
                # This should be here an not in the previous for datasetname in datasetnames4rowidx[i_row] loop because the
                # y_lims can change after each dataset
                if TS_kwargs.get("indicate_y_outliers_resi", True):
                    for datasetname in datasetnames:
                        et.indicate_y_outliers(x=dico_kwargs[datasetname]['time'], y=residuals[datasetname],
                                               ax=axe_resi, color=pl_kwarg_final[datasetname]["data"].get("color", None),
                                               alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))

                ############################
                # Set the t_lims if provided
                ############################
                if t_lims_i is None:
                    axe_resi.set_xlim(xlims)
                else:
                    axe_resi.set_xlim(t_lims_i)

                ##########################
                # Set the legend if needed
                ##########################
                if (i_col == 0) and TS_kwargs.get('show_legend', True):
                    axe_data.legend(fontsize=fontsize, **TS_kwargs.get('legend_param', {}))

    #########
    # RV GLSP
    #########
    if GLSP_kwargs.get("do", True):
        all_rv_data = np.concatenate([dico_kwargs[dst]["data"] for dst in datasetnames])[idx_sort]
        if GLSP_kwargs.get("use_jitter", True):
            all_rv_data_err = np.concatenate([data_err_jitter[dst] for dst in datasetnames])[idx_sort]
        else:
            all_rv_data_err = np.concatenate([dico_kwargs[dst]["data_err"] for dst in datasetnames])[idx_sort]
        # Create the model for the GLS
        model_GLS, _, gp_pred_GLS, gp_pred_var_GLS = post_instance.compute_model(tsim=all_time, dataset_name=l_datasetname_RVrefglobal[0],
                                                                                 param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
                                                                                 key_obj=key_whole, datasim_kwargs=datasim_kwargs)
        model_GLS *= RV_fact
        if gp_pred_GLS is not None:
            gp_pred_GLS *= RV_fact
            gp_pred_var_GLS *= RV_fact**2

        if model_wGP is not None:  # WARNING: This assumes that all datasets have (or don't have) GP
            gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
                          "model": {"data": model_GLS, "err": np.sqrt(gp_pred_var_GLS), 'label': "model"},  # np.sqrt(gp_pred_var_GLS)
                          "GP": {"data": gp_pred_GLS, "err": np.sqrt(gp_pred_var_GLS), 'label': "GP"},
                          "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
                          }
            l_gls_key = ["data", "model", "GP", "resi"]
        else:
            gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
                          "model": {"data": model_GLS, "err": all_rv_data_err, 'label': "model"},  # np.sqrt(gp_pred_var_GLS)
                          "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
                          }
            l_gls_key = ["data", "model", "resi"]

        ###############################
        # Compute the GLSPs
        ###############################
        Pbeg, Pend = GLSP_kwargs.get("period_range", (0.1, 1000))

        glsps = {}
        for ii, key in enumerate(l_gls_key):
            glsps[key] = Gls((all_time, gls_inputs[key]["data"], gls_inputs[key]["err"]), Pbeg=Pbeg, Pend=Pend, verbose=False)

        ###############################
        # Create additional axe if zoom
        ###############################
        if GLSP_kwargs.get("freq_lims_zoom", None) is not None:
            gs_gls = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_gls, **TS_kwargs.get('gridspec_kwargs', {}))  # , wspace=0.2, width_ratios=(2, 1)
            freq_lims = [GLSP_kwargs.get("freq_lims", None), GLSP_kwargs["freq_lims_zoom"]]
            period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), GLSP_kwargs.get("period_no_ticklabels_zoom", [])]
            nb_columns = 2
        else:
            gs_gls = [gs_gls, ]
            freq_lims = [GLSP_kwargs.get("freq_lims", None), ]
            period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), ]
            nb_columns = 1

        ################################################
        # Create additional axes for data, model, etc...
        ################################################
        show_WF = GLSP_kwargs.get("show_WF", True)
        nb_axes = len(l_gls_key) + int(show_WF)
        freq_fact = GLSP_kwargs.get("freq_fact", 1e6)
        freq_unit = GLSP_kwargs.get("freq_unit", '$\mu$Hz')
        logscale = GLSP_kwargs.get("logscale", False)
        legend_param = GLSP_kwargs.get('legend_param', {})

        for jj, (gs_gls_j, freq_lims_j, period_no_ticklabels_j) in enumerate(zip(gs_gls, freq_lims, period_no_ticklabels)):
            ax_gls = et.add_axeswithsharex(gs_gls_j, fig, nb_axes=nb_axes, gs_from_sps_kw=GLSP_kwargs.get("axeswithsharex_kwargs", {}))  # {"wspace": 0.2})
            if jj == 0:
                ax_gls[0].set_title("GLS Periodograms", fontsize=fontsize)
            if logscale:
                ax_gls[-1].set_xscale("log")
            # ax_gls[-1].set_xlabel("Period [days]", fontsize=fontsize)
            ax_gls[-1].set_xlabel(f"Frequency [{freq_unit}]", fontsize=fontsize)
            # create and set the twiny axis
            ax_gls_twin = []
            for ii, key in enumerate(l_gls_key):
                ax_gls_twin.append(ax_gls[ii].twiny())
                if logscale:
                    ax_gls_twin[ii].set_xscale("log")
                ax_gls[ii].set_zorder(ax_gls_twin[ii].get_zorder() + 1)  # To make sure that the orginal axis is above the new one
                ax_gls[ii].patch.set_visible(False)
                labeltop = True if ii == 0 else False
                ax_gls_twin[ii].tick_params(axis="x", labeltop=labeltop, labelsize=fontsize, which="both", direction="in")
                ax_gls_twin[ii].tick_params(axis="x", which="major", length=4, width=1)
                ax_gls_twin[ii].tick_params(axis="x", which="minor", length=2, width=0.5)
                ax_gls[ii].tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
                ax_gls[ii].tick_params(axis="both", which="major", length=4, width=1)
                ax_gls[ii].tick_params(axis="both", which="minor", length=2, width=0.5)
                # ax_gls[ii].yaxis.set_label_position("right")
                # ax_gls[ii].yaxis.tick_right()
                labelleft = True if jj == 0 else False
                labelbottom = True if ii == (nb_axes - 1) else False
                ax_gls[ii].tick_params(axis="x", labelleft=labelleft, labelbottom=labelbottom, labelsize=fontsize, which="both", direction="in")
                ax_gls[ii].tick_params(axis="y", labelleft=labelleft, labelsize=fontsize, which="both", direction="in")
                ax_gls[ii].yaxis.set_minor_locator(AutoMinorLocator())
                ax_gls[ii].xaxis.set_minor_locator(AutoMinorLocator())

                # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
                ax_gls[ii].plot(glsps[key].freq / day2sec * freq_fact, glsps[key].power, '-', color="k", label=gls_inputs[key]["label"], linewidth=GLSP_kwargs.get("lw ", 1.))
                # Set ticks and tick labels
                if jj == 0:
                    ax_gls[ii].set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # {gls_inputs[key]['label']}

                ylims = ax_gls[ii].get_ylim()
                xlims = ax_gls[ii].get_xlim()

                # Print the period axis
                per_min = np.min(1 / glsps[key].freq)
                freq_min = np.min(glsps[key].freq)
                per_max = np.max(1 / glsps[key].freq)
                freq_max = np.max(glsps[key].freq)
                per_xlims = [1 / (freq_lim / freq_fact * day2sec) for freq_lim in xlims]
                if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
                    per_xlims[0] = per_max
                per_xlims = per_xlims[::-1]
                if not(logscale):
                    ax_gls_twin[ii].plot([freq_min / day2sec * freq_fact, freq_max / day2sec * freq_fact],
                                         [np.mean(glsps[key].power), np.mean(glsps[key].power)], "k", alpha=0)
                else:
                    ax_gls_twin[ii].plot([per_min, per_max], [np.mean(glsps[key].power), np.mean(glsps[key].power)], "k", alpha=0)
                    xlims_per = ax_gls_twin[ii].get_xlim()
                    ax_gls_twin[ii].set_xlim(xlims_per[::-1])
                if not(logscale):
                    per_decades = [10**(exp) for exp in list(range(int(np.floor(np.log10(per_min))), int(np.ceil(np.log10(per_max))) + 1))]
                    per_ticks_major = []
                    per_ticklabels_major = []
                    per_ticks_minor = []
                    for dec in per_decades:
                        for fact in range(1, 10):
                            tick = dec * fact
                            if (tick > per_xlims[0]) and (tick < per_xlims[1]):
                                if fact == 1:
                                    per_ticks_major.append(tick)
                                    if tick in period_no_ticklabels_j:
                                        per_ticklabels_major.append("")
                                    else:
                                        per_ticklabels_major.append(tick)
                                else:
                                    per_ticks_minor.append(tick)
                    # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
                    ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_major])
                    if GLSP_kwargs.get('scientific_notation_P_axis', True):
                        ax_gls_twin[ii].set_xticklabels([fmt_sci_not(tick) for tick in per_ticklabels_major])
                    else:
                        ax_gls_twin[ii].set_xticklabels(per_ticklabels_major)
                    # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
                    ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_minor], minor=True)

                if freq_lims_j is None:
                    ax_gls[ii].set_xlim(xlims)
                    if logscale:
                        ax_gls_twin[ii].set_xlim(xlims_per[::-1])
                    else:
                        ax_gls_twin[ii].set_xlim(xlims)
                else:
                    ax_gls[ii].set_xlim(freq_lims_j)
                    if logscale:
                        ax_gls_twin[ii].set_xlim([1 / (freq / freq_fact * day2sec) for freq in freq_lims_j])
                    else:
                        ax_gls_twin[ii].set_xlim(freq_lims_j)

                ylims = ax_gls[ii].get_ylim()
                xlims = ax_gls[ii].get_xlim()

                #####################################
                # Vertical lines at specified periods
                #####################################
                for per, dico_per in GLSP_kwargs.get('periods', {}).items():
                    vlines_kwargs = dico_per.get("vlines_kwargs", {})
                    lines_per = ax_gls[ii].vlines(1 / per / day2sec * freq_fact, *ylims, **vlines_kwargs)
                    if key == "data":
                        text_kwargs = dico_per.get("text_kwargs", {}).copy()
                        x_shift = text_kwargs.pop("x_shift", 0)
                        y_pos = text_kwargs.pop("y_pos", 0.9)
                        label = str(text_kwargs.pop("label", np.format_float_positional(per, precision=3, unique=False, fractional=False, trim='k')))
                        color = text_kwargs.pop("color", None)
                        if color is None:
                            color = lines_per.get_color()[0]
                        ax_gls_twin[ii].text(1 / (per) / day2sec * freq_fact + x_shift * (xlims[1] - xlims[0]),
                                             ylims[0] + y_pos * (ylims[1] - ylims[0]), label, color=color,
                                             fontsize=fontsize, **text_kwargs)
                ax_gls[ii].set_ylim(ylims)

                ##########################################
                # Horizontal lines at specified FAP levels
                ##########################################
                ylims = ax_gls[ii].get_ylim()
                xlims = ax_gls[ii].get_xlim()

                default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
                                    1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
                                    10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
                for fap_lvl, dico_fap in GLSP_kwargs.get('fap', default_fap_dict).items():
                    pow_ii = glsps[key].powerLevel(fap_lvl / 100)
                    hlines_kwargs = dico_fap.get("hlines_kwargs", {})
                    if pow_ii < ylims[1]:
                        lines_fap = ax_gls[ii].hlines(pow_ii, *xlims, **hlines_kwargs)
                        text_kwargs = dico_fap.get("text_kwargs", {}).copy()
                        x_pos = text_kwargs.pop("x_pos", 1.05)
                        y_shift = text_kwargs.pop("y_shift", 0)
                        label = str(text_kwargs.pop("label", f"{fap_lvl}\%"))
                        color = text_kwargs.pop("color", None)
                        if color is None:
                            color = lines_fap.get_color()[0]
                        if jj == (nb_columns - 1):
                            ax_gls[ii].text(xlims[0] + x_pos * (xlims[1] - xlims[0]), pow_ii + y_shift * (ylims[1] - ylims[0]),
                                            label, color=color, fontsize=fontsize, **text_kwargs)

                ax_gls[ii].set_xlim(xlims)
                #
                if jj == 0:
                    ax_gls[ii].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get(key, {}))

            ax_gls_twin[0].set_xlabel("Period [days]", fontsize=fontsize)

            if GLSP_kwargs.get("show_WF", True):
                ax_gls[-1].plot(glsps[key].freq / day2sec * freq_fact, glsps[key].wf, '-', color="k", label="WF", linewidth=GLSP_kwargs.get("lw ", 1.))
                if jj == 0:
                    ax_gls[-1].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get("WF", {}))
                    ax_gls[-1].set_ylabel("Relative Amplitude")
                labelleft = True if jj == 0 else False
                ax_gls[-1].tick_params(axis="both", labelleft=labelleft, labelsize=fontsize, right=True, which="both", direction="in")

                # ax_gls_twin[-1].tick_params(axis="x", which="both", top=False, direction="in")


def load_datasets_and_models_RV(datasetnames, post_instance, datasim_kwargs, df_fittedval, RV_fact,
                                remove_inst_var, remove_stellar_var, remove_decorrelation, remove_decorrelation_likelihood,
                                remove_GP_dataNmodel, remove_GP_residual):
    """Load the dataset and models for later use by the other two function

    remove_inst_var  : bool
        If True remove the instrumental variations
    remove_stellar_var  : bool
        If True remove the systemic velocity and the stellar variations
    remove_decorrelation  : bool
        If True remove the model decorrelation
    remove_decorrelation_likelihood  : bool
        If True remove the likelihood decorrelation
    remove_GP_data  : bool
        If True remove the GP model from the data
    remove_GP_residual  : bool
        If True remove the GP model from the residuals
    """
    dico_datasets = {}
    dico_kwargs = {}
    dico_nb_dstperinsts = defaultdict(lambda: 0)
    times = {}
    datas = {}
    data_errs = {}
    data_err_jitters = {}
    data_err_worwojitters = {}
    has_jitters = {}
    dico_jitters = {}
    models = {}
    gp_preds = {}
    gp_pred_vars = {}
    inst_vars = {}
    stellar_vars = {}
    decorrs = {}
    decorr_likelihoods = {}
    residuals = {}
    for datasetname in datasetnames:
        ##########################################
        # Load Data and instrument and noise model
        ##########################################
        dico_datasets[datasetname] = post_instance.dataset_db[datasetname]
        dico_kwargs[datasetname] = dico_datasets[datasetname].get_all_datasetkwargs()
        times[datasetname] = dico_datasets[datasetname].get_datasetkwarg("time")
        datas[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data")
        data_errs[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data_err")
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
        dico_nb_dstperinsts[filename_info["inst_name"]] += 1

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        dico_jitters[datasetname] = {}
        data_err_jitters[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data_err")
        has_jitters[datasetname] = noise_model.has_jitter
        if has_jitters[datasetname]:
            dico_jitters[datasetname]["type"] = noise_model.jitter_type
            if inst_mod.jitter.free:
                dico_jitters[datasetname]["value"] = df_fittedval.loc[inst_mod.jitter.full_name]["value"]
            else:
                dico_jitters[datasetname]["value"] = inst_mod.jitter.value
            if dico_jitters[datasetname]["type"] == "multi":
                data_err_jitters[datasetname] = np.sqrt(apply_jitter_multi(data_err_jitters[datasetname], dico_jitters[datasetname]["value"]))
            elif dico_jitters[datasetname]["type"] == "add":
                data_err_jitters[datasetname] = np.sqrt(apply_jitter_add(data_err_jitters[datasetname], dico_jitters[datasetname]["value"]))
            else:
                raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            data_err_worwojitters[datasetname] = data_err_jitters[datasetname].copy()
        else:
            data_err_worwojitters[datasetname] = data_errs[datasetname].copy()

        ###############################################################################
        # Compute the stellar variations (stellar_vars) to later remove from the data
        ###############################################################################
        # For each dataset
        # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
        # and remove RV_drift
        (model_stellar_vars, _, _, _
         ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname, param=df_fittedval["value"],
                                         l_param_name=list(df_fittedval.index), key_obj="stellar_var", datasim_kwargs=datasim_kwargs
                                         )
        if model_stellar_vars is not None:
            stellar_vars[datasetname] = model_stellar_vars

        ###############################################################################
        # Compute the instrumental variations (inst_vars) to later remove from the data
        ###############################################################################
        # For each dataset
        # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
        # and remove RV_drift
        (model_inst_var, _, _, _
         ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname, param=df_fittedval["value"],
                                         l_param_name=list(df_fittedval.index), key_obj="inst_var", datasim_kwargs=datasim_kwargs
                                         )
        if model_inst_var is not None:
            inst_vars[datasetname] = model_inst_var

        #########################################################################
        # Compute the decorrelation models (decorr) to later remove from the data
        #########################################################################
        if post_instance.model.instcat_models["RV"].decorrelation_model_config[inst_mod_fullname]["do"]:
            (model_decorr, _, _, _
             ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname, param=df_fittedval["value"],
                                             l_param_name=list(df_fittedval.index), key_obj="decorr", datasim_kwargs=datasim_kwargs
                                             )
            decorrs[datasetname] = {}
            for model_part in post_instance.model.instcat_models["RV"].decorrelation_model_config[inst_mod_fullname]['what to decorrelate']:
                if model_part == "add_2_totalflux":
                    (model_decorr, _, _, _
                     ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname, param=df_fittedval["value"],
                                                     l_param_name=list(df_fittedval.index), key_obj="decorr", datasim_kwargs=datasim_kwargs
                                                     )
                    decorrs[datasetname][model_part] = model_decorr['add_2_totalflux']
                else:
                    logger.error("Decorrelation of model part {model_part} is not currently taken into account by this function.")

        #######################################
        # Compute the models and GP predictions
        #######################################
        (model, model_wGP, gp_pred, gp_pred_var
         ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
                                         param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
                                         key_obj=key_whole, datasim_kwargs=datasim_kwargs)
        if model_wGP is not None:
            gp_preds[datasetname] = gp_pred
            gp_pred_vars[datasetname] = gp_pred_var

        if (model_wGP is not None) and not(remove_GP_dataNmodel):
            models[datasetname] = model_wGP
        else:
            models[datasetname] = model

        ###################################################
        # Compute the likelihood decorrelation contribution
        ###################################################
        if remove_decorrelation_likelihood and (f"{datasetname}_decorr_like" in post_instance.datasimulators.dataset_db):
            datasim_docfunc_decorr_like = post_instance.datasimulators.dataset_db[f"{datasetname}_decorr_like"]
            p_vect = df_fittedval["value"][datasim_docfunc_decorr_like.param_model_names_list]
            decorr_likelihoods[datasetname] = datasim_docfunc_decorr_like.function(p_vect)

        #######################
        # Compute the residuals
        #######################
        if (model_wGP is not None) and remove_GP_residual:
            residuals[datasetname] = datas[datasetname] - model_wGP
        else:
            residuals[datasetname] = datas[datasetname] - model

        ################################################################################
        # Remove GP (if needed)
        ################################################################################
        if (model_wGP is not None) and remove_GP_dataNmodel:
            datas[datasetname] -= gp_pred

        ################################################################################
        # Remove stellar_vars (if needed)
        ################################################################################
        if (datasetname in stellar_vars) and remove_stellar_var:
            datas[datasetname] -= stellar_vars[datasetname]
            models[datasetname] -= stellar_vars[datasetname]

        ################################################################################
        # Remove inst_vars (if needed)
        ################################################################################
        if (datasetname in inst_vars) and remove_inst_var:
            datas[datasetname] -= inst_vars[datasetname]
            models[datasetname] -= inst_vars[datasetname]

        ################################################################################
        # Remove decorrelation (if needed)
        ################################################################################
        if (datasetname in decorrs) and remove_decorrelation:
            for model_part in decorrs[datasetname]:
                if model_part == "add_2_totalrv":
                    datas[datasetname] -= decorrs[datasetname]['add_2_totalrv']
                    models[datasetname] -= decorrs[datasetname]['add_2_totalrv']
                else:
                    logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")

        ################################################################################
        # Remove decorrelation likelihood (if needed)
        ################################################################################
        if (datasetname in decorrs) and remove_decorrelation_likelihood:
            datas[datasetname] -= decorr_likelihoods[datasetname]

        ################################################################################
        # Apply RV_fact
        ################################################################################
        datas[datasetname] *= RV_fact
        data_errs[datasetname] *= RV_fact
        data_err_worwojitters[datasetname] *= RV_fact
        residuals[datasetname] *= RV_fact
        models[datasetname] *= RV_fact
        if model_wGP is not None:
            gp_preds[datasetname] *= RV_fact
            gp_pred_vars[datasetname] *= RV_fact**2
        if has_jitters[datasetname]:
            dico_jitters[datasetname]["value"] *= RV_fact
            data_err_jitters[datasetname] *= RV_fact

    return (dico_datasets, dico_kwargs, dico_nb_dstperinsts, datas, data_errs, data_err_jitters, data_err_worwojitters,
            has_jitters, dico_jitters, models, gp_preds, gp_pred_vars, inst_vars, stellar_vars, decorrs,
            decorr_likelihoods, residuals
            )
