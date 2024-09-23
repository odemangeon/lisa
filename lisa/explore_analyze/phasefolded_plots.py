"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from matplotlib.pyplot import figure
from numpy import std, argsort, concatenate, isfinite
from copy import copy
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec, SubplotSpec
from matplotlib.figure import Figure
from PyAstronomy.pyasl import foldAt
from loguru import logger
from scipy.stats import binned_statistic
from pandas import DataFrame
from typing import Callable, Dict

from .misc import (AandA_fontsize, check_spec_data_or_resi, check_row4datasetname, check_datasetnameformodel4row,
                   check_spec_by_column_or_row, check_spec_for_data_or_resi_by_column_or_row, do_suptitle,
                   get_pl_kwargs, check_kwargs_by_column_and_row, define_x_or_y_lims, update_data_binned_label,
                   print_rms, set_legend, AandA_full_width, default_figheight_factor
                   )
from .core_plot import PlotsDefinitionPF, ComputedModels_Database, Expression
from .binning import compute_binning
from .core_compute_load import compute_model, get_key_compute_model, compute_data_err_jittered
from ..emcee_tools import emcee_tools as et
from ..posterior.core.posterior import Posterior



def create_phasefolded_plots(post_instance:Posterior, df_fittedval:DataFrame,
                             compute_raw_models_func: Callable,
                             plotdef:PlotsDefinitionPF,
                             computedmodels_db:ComputedModels_Database|None=None,
                             split_GP_computation:int|None=None,
                             datasim_kwargs=None,
                             create_axes_main_gridspec:dict|None=None,
                             create_axes_dataresi_gridspec:dict|None=None,
                             indicate_y_outliers:dict|None=None,
                             pad:dict|None=None,
                             legend_kwargs:dict|None=None,
                             npt_model_default:int|None=None,
                             extra_dt_model:float|None=None,
                             fontsize:int=AandA_fontsize,
                             get_key_compute_model_func:Callable=get_key_compute_model,
                             kwargs_get_key_compute_model:Dict|None=None,
                             fig:Figure|None=None,
                             subplotspec:SubplotSpec|None=None,
                             ):
    logger.debug("Start: create_PF_plots")

    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")

    # If no ComputedModels_Database is provided create a new one
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    # Make sure that indicate_y_outliers is well defined
    indicate_y_outliers = check_spec_data_or_resi(spec_user=indicate_y_outliers, l_type_spec=[bool], spec_def=True)

    # Make sure that pad is well defined
    pad = check_spec_data_or_resi(spec_user=pad, l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

    # Create the updated grid space for TS according to the number of rows and cols specified in plotdef
    if create_axes_main_gridspec is None:
        create_axes_main_gridspec = {}
    if subplotspec is None:
        if fig is None:
            fig = Figure()
    if subplotspec is not None:
        gs = GridSpecFromSubplotSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, subplot_spec=subplotspec, **create_axes_main_gridspec)
    else:
        gs = GridSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, figure=fig, **create_axes_main_gridspec)

    # Make sure that legend_kwargs is well defined
    legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=legend_kwargs, l_row_name=list(range(plotdef.nb_rows)), l_col_name=list(range(plotdef.nb_cols)),
                                                   kwargs_def={'do': False}, kwargs_init={0: {i_row: {'do': True} for i_row in range(plotdef.nb_rows)}}
                                                   )
    
    # Set default values for parameters
    if npt_model_default is None:
        npt_model_default = 1000
    if extra_dt_model is None:
        extra_dt_model = 0.
    
    ###########################################
    # Make the data, models and residuals plots
    ###########################################
    rms_values = OrderedDict()
    for i_row in range(plotdef.nb_rows):
        for i_col in range(plotdef.nb_cols):
            logger.debug(f"Doing PF plot for row {i_row}/{plotdef.nb_rows - 1}, column {i_col}/{plotdef.nb_cols - 1}")
            subplotspec_i = gs[i_row, i_col]

            # Create the data and residuals axes and set properties ans style
            (axe_data, axe_resi) = et.add_twoaxeswithsharex(subplotspec_i, fig, gs_from_sps_kw=create_axes_dataresi_gridspec)  # gs_from_sps_kw={"wspace": 0.1}
        
            axe_resi.set_xlabel(plotdef.axes_properties[i_row][i_col]["x"].label, fontsize=fontsize)
            ylabel_data = plotdef.axes_properties[i_row][i_col]["y_data"].label
            ylabel_resi = plotdef.axes_properties[i_row][i_col]["y_resi"].label
            if ylabel_data is not None:
                axe_data.set_ylabel(ylabel_data, fontsize=fontsize)
            if ylabel_resi is not None:
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

            ##################################
            # Get the phase folding properties
            ##################################
            phasefold_i = plotdef.get_phasefold_properties(i_row=i_row, i_col=i_col)
            T0_i = phasefold_i.T0
            period_i = phasefold_i.period
            phasefold_centralphase_i = phasefold_i.phasefold_centralphase
            show_time_from_T0_i = phasefold_i.show_time_from_T0

            ######################################
            # Plot the models specified in plotdef
            ######################################
            for name_model2plot_i, model2plot_i in plotdef.get_models2plot(i_row=i_row, i_col=i_col).items():
                logger.info(f"Start Plotting model {name_model2plot_i}")
                times_model2plot_i = model2plot_i.get_times(post_instance=post_instance, time_limits=(T0_i, T0_i + period_i), npt=npt_model_default, extra_dt=extra_dt_model)
                time_fact = model2plot_i.pl_factors.time_factor
                amplitude_fact = model2plot_i.pl_factors.value_factor
                # Compute the model
                model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                        compute_raw_models_func=compute_raw_models_func, 
                                                        expression=model2plot_i.expression, times=times_model2plot_i, datasetname=model2plot_i.datasetname,
                                                        exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                        computedmodels_db=computedmodels_db, 
                                                        get_key_compute_model_func=get_key_compute_model,
                                                        kwargs_get_key_compute_model=None,
                                                        split_GP_computation=split_GP_computation)
                # Compute the phasefolded times
                phasefolded_times_i = foldAt(times_model2plot_i, period_i, T0=(T0_i + period_i * (phasefold_centralphase_i - 0.5))) + (phasefold_centralphase_i - 0.5)
                # Convert phasefolded_times in times unit if needed
                if show_time_from_T0_i:
                    phasefolded_times_i = phasefolded_times_i * period_i
                # Sort according to phase folded times to avoid lines all over the plot
                idx_sort = argsort(phasefolded_times_i)
                phasefolded_times_i = phasefolded_times_i[idx_sort]
                model_i = model_i[idx_sort]
                if model_err_i is not None:
                    model_err_i = model_err_i[idx_sort]
                # Plot
                # Plot the model values
                pl_kwarg_to_use = copy(model2plot_i.pl_kwargs)
                # You are plot data or a modified version of the data
                ebcont = axe_data.errorbar(phasefolded_times_i * time_fact, y=model_i * amplitude_fact,
                                            **pl_kwarg_to_use)
                color = ebcont[0].get_color()
                alpha = ebcont[0].get_alpha()
                # Plot the model uncertainty region for models that do not involve data 
                if (model_err_i is not None) and model2plot_i.show_error:
                    pl_kwarg_to_use = copy(model2plot_i.pl_kwargs_error)
                    if not("color" in pl_kwarg_to_use):
                        pl_kwarg_to_use["color"] = color
                    if not("alpha" in pl_kwarg_to_use):
                        if alpha is None:
                            alpha = 1.
                        pl_kwarg_to_use["alpha"] = alpha / 3
                        _ = axe_data.fill_between(phasefolded_times_i * time_fact, (model_i - model_err_i) * amplitude_fact, (model_i + model_err_i) * amplitude_fact,
                                                  **pl_kwarg_to_use)
            
            for name_multimodel2plot_i, multimodel2plot_i in plotdef.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                raise NotImplementedError("Plotting of MultiModel2Plot is not implemented yet")

            ####################################
            # Plot the data specified in plotdef
            ####################################
            dico_data = {}  # Will be used for ylims and y outliers indication 
            dico_resi = {}  # Will be used for ylims and y outliers indication
            dico_phasefoldedtimes = {}  # Will be used for y outliers indication
            pl_kwarg_to_use = {}  # Will be used for y outliers indication

            for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                logger.info(f"Start Plotting data {name_data2plot_i}")
                times_dataset = data2plot_i.get_times_dataset(post_instance=post_instance)
                time_fact = data2plot_i.pl_factors.time_factor
                amplitude_fact = data2plot_i.pl_factors.value_factor
                # Compute the data_model
                data_i, data_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                      compute_raw_models_func=compute_raw_models_func, 
                                                      expression=data2plot_i.expression, times=times_dataset, datasetname=data2plot_i.datasetname,
                                                      exptime=None, supersampling=None,
                                                      computedmodels_db=computedmodels_db, 
                                                      get_key_compute_model_func=get_key_compute_model,
                                                      kwargs_get_key_compute_model=None,
                                                      split_GP_computation=split_GP_computation
                                                      )
                # Compute jittered_errors
                data_err_jitter_i = compute_data_err_jittered(data_err=data_err_i, post_instance=post_instance, datasetname=data2plot_i.datasetname, df_fittedval=df_fittedval)                    
                # Compute residuals 
                logger.info(f"Compute residuals for {name_data2plot_i}")
                expression_resi = Expression(expression="data - model - GP - decorrelation_likelihood")
                residuals_i, _, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                  compute_raw_models_func=compute_raw_models_func, 
                                                  expression=expression_resi, times=times_dataset,
                                                  datasetname=data2plot_i.datasetname,
                                                  exptime=None, supersampling=None,
                                                  computedmodels_db=computedmodels_db, 
                                                  get_key_compute_model_func=get_key_compute_model,
                                                  kwargs_get_key_compute_model=None,
                                                  split_GP_computation=split_GP_computation
                                                  )
                # Compute the phasefolded times
                phasefolded_times = foldAt(times_dataset, period_i, T0=(T0_i + period_i * (phasefold_centralphase_i - 0.5))) + (phasefold_centralphase_i - 0.5)
                # Bin the data and residuals if needed
                if data2plot_i.exptime > 0:
                    (bins_i, _, bindata_i, bindata_std_i, bindata_std_jitter_i
                        ) = compute_binning(times_dataset=phasefolded_times, values=data_i, errors=data_err_i, errors_jitter=data_err_jitter_i, 
                                            exptime=data2plot_i.exptime / period_i, method=data2plot_i.method)
                    (_, _, binresi_i, _, _
                        ) = compute_binning(times_dataset=phasefolded_times, values=residuals_i, errors=data_err_i, errors_jitter=data_err_jitter_i, 
                                            exptime=data2plot_i.exptime / period_i, method=data2plot_i.method)
                    midbins_i = bins_i[:-1] + data2plot_i.exptime  / period_i / 2
                # Compute the rms of the residuals
                if data2plot_i.exptime > 0:
                    rms_values[name_data2plot_i] = std(binresi_i)
                else:
                    rms_values[name_data2plot_i] = std(residuals_i)
                logger.info(f"RMS {name_data2plot_i} = {rms_values[name_data2plot_i] * amplitude_fact} {plotdef.axes_properties[i_row][i_col]['y_resi'].unit} (raw cadence)")
                # Plot the data or binned data
                if data2plot_i.exptime == 0.:
                    data_plot_i = data_i
                    resi_plot_i = residuals_i
                    data_err_plot_i = data_err_i
                    data_err_jitter_plot_i = data_err_jitter_i
                    time_plot_i = phasefolded_times
                else:
                    data_plot_i = bindata_i
                    resi_plot_i = binresi_i
                    data_err_plot_i = bindata_std_i
                    data_err_jitter_plot_i = bindata_std_jitter_i
                    time_plot_i = midbins_i
                # Convert phasefolded_times in times unit if needed
                if show_time_from_T0_i:
                    time_plot_i = time_plot_i * period_i
                pl_kwarg_to_use[name_data2plot_i] = copy(data2plot_i.pl_kwargs)
                show_error = pl_kwarg_to_use[name_data2plot_i].get('show_error', True)
                if 'show_error' in pl_kwarg_to_use[name_data2plot_i]:
                    pl_kwarg_to_use[name_data2plot_i].pop('show_error')
                dico_data[name_data2plot_i] = data_plot_i * amplitude_fact
                dico_resi[name_data2plot_i] = resi_plot_i * amplitude_fact
                dico_phasefoldedtimes[name_data2plot_i] = time_plot_i * time_fact
                if not(show_error) or (data_err_i is None):
                    ebcont = axe_data.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_data[name_data2plot_i], **pl_kwarg_to_use[name_data2plot_i])
                    if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["color"] = ebcont[0].get_color()
                    ebcont = axe_resi.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_resi[name_data2plot_i], **pl_kwarg_to_use[name_data2plot_i])
                else:
                    ebcont = axe_data.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["color"] = ebcont[0].get_color()
                    ebcont = axe_resi.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                color = ebcont[0].get_color()
                alpha = ebcont[0].get_alpha()
                if "alpha" not in pl_kwarg_to_use[name_data2plot_i]:
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] = alpha
                if pl_kwarg_to_use[name_data2plot_i]["alpha"] is None:
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] = 1
                if not(not(show_error) or (data_err_jitter_plot_i is None)):
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] /= 3
                    if 'label' in pl_kwarg_to_use[name_data2plot_i]:
                        label = pl_kwarg_to_use[name_data2plot_i].pop('label')
                    _ = axe_data.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    _ = axe_resi.errorbar(dico_phasefoldedtimes[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] *= 3

                for name_multidata2plot_i, multidata2plot_i in plotdef.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                    raise NotImplementedError("Plotting of MultiData2Plot is not implemented yet")
            
            ###################################
            # Set ylims and indicate_y_outliers
            ###################################
            logger.debug(f"Setting ylims and indicating outliers for row {i_row}, column {i_col}")
            # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
            for axe, data_or_resi, points, in zip((axe_data, axe_resi), ("data", "resi"), (dico_data, dico_resi)):
                # Set the y axis limits
                if data_or_resi == "data":
                    y_lims_i = plotdef.get_axis_lims(which="y_data", i_row=i_row, i_col=i_col)
                else:
                    y_lims_i = plotdef.get_axis_lims(which="y_resi", i_row=i_row, i_col=i_col)
                if all([y_lims_i[jj] is None for jj in range(2)]) and (pad[data_or_resi] is not None):
                    if len(plotdef.get_datas2plot(i_row=i_row, i_col=i_col)):
                        points_pl_i = concatenate([points[name_data2plot_i] for name_data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col)])
                        et.auto_y_lims(points_pl_i[isfinite(points_pl_i)], axe, pad=pad[data_or_resi])
                else:
                    axe.set_ylim(y_lims_i)

                # Indicate outlier values that are off y-axis with an arrows for raw cadence
                if indicate_y_outliers[data_or_resi]:
                    for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                        et.indicate_y_outliers(x=dico_phasefoldedtimes[name_data2plot_i], y=points[name_data2plot_i], ax=axe,
                                               color=pl_kwarg_to_use[name_data2plot_i]["color"],
                                               alpha=pl_kwarg_to_use[name_data2plot_i]["alpha"])

            # # Draw a horizontal line at 0 in the residual plot
            # axe_resi.hlines(0, *current_xlims, colors="k", linestyles="dashed")
            logger.debug(f"Done: Set ylims and indicate outliers for row {i_row}, column {i_col}")

            ############################
            # Set the tlims if provided
            ############################
            logger.debug(f"Setting xlims for row {i_row}, column {i_col}")
            # Set the x axis limits
            # if TS_kwargs.get('force_tlims', False):
            axe_data.set_xlim(plotdef.get_axis_lims(which="x", i_row=i_row, i_col=i_col))
            # else:
            #     x_row = concatenate([dico_times[name_data2plot_i] for name_data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).keys()])
            #     axe_data.set_xlim((min(x_row), max(x_row)))
            logger.debug(f"Done: Set xlims for row {i_row}, column {i_col}")
            ##########################
            # Set the legend if needed
            ##########################
            set_legend(ax=axe_data, legend_kwargs=legend_kwargs[i_col][i_row], fontsize_def=fontsize)
    
    logger.debug("Done: create_PF_plots")
    return computedmodels_db, rms_values
