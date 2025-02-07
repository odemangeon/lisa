"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from numpy import std, concatenate, isfinite
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec, SubplotSpec
from matplotlib.figure import Figure
from loguru import logger
from copy import copy
from pandas import DataFrame
from typing import Callable, Dict

from .misc import AandA_fontsize, set_legend
# from .models2computenplot import Models2plotTS, check_Models2plot
from .core_plot import PlotsDefinition_TS, ComputedModels_Database, Expression
from .binning import compute_binning
from .core_compute_load import compute_model, get_key_compute_model, compute_data_err_jittered
from ..emcee_tools import emcee_tools as et
from ..posterior.core.model.core_model import Core_Model
from ..posterior.core.posterior import Posterior


def create_TS_plots(post_instance:Posterior, df_fittedval:DataFrame,
                    compute_raw_models_func: Callable,
                    plotdef:PlotsDefinition_TS,
                    computedmodels_db:ComputedModels_Database|None=None,
                    split_GP_computation:int|None=None,
                    datasim_kwargs:dict|None=None,
                    create_axes_main_gridspec:dict|None=None,
                    create_axes_dataresi_gridspec:dict|None=None,
                    npt_model_default:int|None=None,
                    extra_dt_model:float|None=None,
                    fontsize:int=AandA_fontsize,
                    get_key_compute_model_func:Callable=get_key_compute_model,
                    kwargs_get_key_compute_model:Dict|None=None,
                    fig:Figure|None=None,
                    subplotspec:SubplotSpec|None=None,
                    ):
    logger.debug("Start: create_TS_plots")
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")

    # If no ComputedModels_Database is provided create a new one
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    # Create the updated grid space for TS according to the number of rows and cols specified in plotdef
    if create_axes_main_gridspec is None:
        create_axes_main_gridspec = {}
    if fig is None:
        fig = Figure()
    if subplotspec is None:
        gs = GridSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, figure=fig, **create_axes_main_gridspec)
    else:
        gs = GridSpecFromSubplotSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, subplot_spec=subplotspec, **create_axes_main_gridspec)

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
            logger.debug(f"Doing TS plot for row {i_row}/{plotdef.nb_rows - 1}, column {i_col}/{plotdef.nb_cols - 1}")
            subplotspec_i = gs[i_row, i_col]

            # Create the data and residuals axes and set properties ans style
            axes_properties_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col)
            if axes_properties_i.residuals:
                (axe_data, axe_resi) = et.add_twoaxeswithsharex(subplotspec_i, fig, gs_from_sps_kw=create_axes_dataresi_gridspec)  # gs_from_sps_kw={"wspace": 0.1}
                l_axe = [axe_data, axe_resi]
            else:
                axe_data = fig.add_subplot(subplotspec_i)
                l_axe = [axe_data, ]

            l_axe[-1].set_xlabel(axes_properties_i.x.label, fontsize=fontsize)
            l_yaxis_properties = [getattr(axes_properties_i, axe_name) for _, axe_name in zip(l_axe, ["ydata", "yresi"])]
            l_ylabel = [yaxis_properties_i.label for yaxis_properties_i in l_yaxis_properties]
            l_yshowlabel = [yaxis_properties_i.show_label for yaxis_properties_i in l_yaxis_properties]
            for axe, ylabel, yshowlabel in zip(l_axe, l_ylabel, l_yshowlabel):
                if yshowlabel and (len(ylabel) > 0):
                    axe.set_ylabel(ylabel, fontsize=fontsize)
            for axe, yaxis_properties_i in zip(l_axe, l_yaxis_properties):
                # Set the ticks direction and length, also set fontsize for tick labels for both x and y and by default do not show the tick labels on the x axes (this is changed later if needed)
                axe.tick_params(axis="both", which="major", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False, labelsize=fontsize)
                axe.tick_params(axis="both", which="minor", direction="in", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
                # Set minor location ticks for both x and y
                axe.xaxis.set_minor_locator(AutoMinorLocator())
                axe.yaxis.set_minor_locator(AutoMinorLocator())
                # Set grid in "y"
                axe.grid(axis="y", color="black", alpha=.5, linewidth=.5)
                #
                if yaxis_properties_i.logscale:
                    axe.set_xscale("log")
            # remove the tick labels on the bottom x axis if needed
            if axes_properties_i.x.show_ticklabels:
                l_axe[-1].tick_params(axis="x", labelbottom=True)

            #########################
            # Set the title if needed
            #########################
            if plotdef.get_axes_properties(i_row=i_row, i_col=i_col).show_title and (len(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).title) > 0):
                axe_data.set_title(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).title, fontsize=fontsize)

            ######################################
            # Plot the models specified in plotdef
            ######################################
            for name_model2plot_i, model2plot_i in plotdef.get_models2plot(i_row=i_row, i_col=i_col).items():
                logger.info(f"Start Plotting model {name_model2plot_i}")
                npt = model2plot_i.npt
                if npt is None:
                    npt = npt_model_default
                times_model2plot_i = model2plot_i.get_times(post_instance=post_instance, npt=npt, extra_dt=extra_dt_model)
                time_fact = model2plot_i.pl_factors.time_factor
                amplitude_fact = model2plot_i.pl_factors.value_factor
                # Compute the model
                model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                        compute_raw_models_func=compute_raw_models_func, 
                                                        expression=model2plot_i.expression, times=times_model2plot_i, datasetname=model2plot_i.datasetname,
                                                        exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                        computedmodels_db=computedmodels_db, 
                                                        get_key_compute_model_func=get_key_compute_model_func,
                                                        kwargs_get_key_compute_model=None,
                                                        split_GP_computation=split_GP_computation)
                # Plot
                # Plot the model values
                pl_kwarg_to_use = copy(model2plot_i.pl_kwargs)
                # You are plot data or a modified version of the data
                ebcont = axe_data.errorbar(times_model2plot_i * time_fact, y=model_i * amplitude_fact,
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
                        _ = axe_data.fill_between(times_model2plot_i * time_fact, (model_i - model_err_i) * amplitude_fact, (model_i + model_err_i) * amplitude_fact,
                                                    **pl_kwarg_to_use)

            ##################################################
            # Plot the data and residuals specified in plotdef
            ##################################################
            dico_data = {}  # Will be used for ylims and y outliers indication 
            dico_resi = {}  # Will be used for ylims and y outliers indication
            dico_times = {}  # Will be used for y outliers indication
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
                                                      get_key_compute_model_func=get_key_compute_model_func,
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
                                                  get_key_compute_model_func=get_key_compute_model_func,
                                                  kwargs_get_key_compute_model=None,
                                                  split_GP_computation=split_GP_computation
                                                  )
                # Bin the data and residuals if needed
                if data2plot_i.exptime > 0:
                    (bins_i, _, bindata_i, bindata_std_i, bindata_std_jitter_i
                        ) = compute_binning(times_dataset=times_dataset, values=data_i, errors=data_err_i, errors_jitter=data_err_jitter_i, 
                                            exptime=data2plot_i.exptime, method=data2plot_i.method)
                    (_, _, binresi_i, _, _
                        ) = compute_binning(times_dataset=times_dataset, values=residuals_i, errors=data_err_i, errors_jitter=data_err_jitter_i, 
                                            exptime=data2plot_i.exptime, method=data2plot_i.method)
                    midbins_i = bins_i[:-1] + data2plot_i.exptime / 2
                # Compute the rms of the residuals
                if data2plot_i.exptime > 0:
                    rms_values[name_data2plot_i] = std(binresi_i)
                else:
                    rms_values[name_data2plot_i] = std(residuals_i)
                logger.info(f"RMS {name_data2plot_i} = {rms_values[name_data2plot_i] * amplitude_fact} {plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.unit} (raw cadence)")
                # Plot the data or binned data
                if data2plot_i.exptime == 0.:
                    data_plot_i = data_i
                    resi_plot_i = residuals_i
                    data_err_plot_i = data_err_i
                    data_err_jitter_plot_i = data_err_jitter_i
                    time_plot_i = times_dataset
                else:
                    data_plot_i = bindata_i
                    resi_plot_i = binresi_i
                    data_err_plot_i = bindata_std_i
                    data_err_jitter_plot_i = bindata_std_jitter_i
                    time_plot_i = midbins_i
                pl_kwarg_to_use[name_data2plot_i] = copy(data2plot_i.pl_kwargs)
                show_error = pl_kwarg_to_use[name_data2plot_i].get('show_error', True)
                if 'show_error' in pl_kwarg_to_use[name_data2plot_i]:
                    pl_kwarg_to_use[name_data2plot_i].pop('show_error')
                dico_data[name_data2plot_i] = data_plot_i * amplitude_fact
                dico_resi[name_data2plot_i] = resi_plot_i * amplitude_fact
                dico_times[name_data2plot_i] = time_plot_i * time_fact
                if not(show_error) or (data_err_plot_i is None):
                    ebcont = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i], **pl_kwarg_to_use[name_data2plot_i])
                    if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["color"] = ebcont[0].get_color()
                    ebcont = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], **pl_kwarg_to_use[name_data2plot_i])
                else:
                    ebcont = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["color"] = ebcont[0].get_color()
                    ebcont = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                color = ebcont[0].get_color()
                alpha = ebcont[0].get_alpha()
                if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                    pl_kwarg_to_use[name_data2plot_i]["color"] = color
                if "alpha" not in pl_kwarg_to_use[name_data2plot_i]:
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] = alpha
                if pl_kwarg_to_use[name_data2plot_i]["alpha"] is None:
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] = 1
                if not(not(show_error) or (data_err_jitter_plot_i is None)):
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] /= 3
                    if 'label' in pl_kwarg_to_use[name_data2plot_i]:
                        label = pl_kwarg_to_use[name_data2plot_i].pop('label')
                    _ = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    _ = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                    pl_kwarg_to_use[name_data2plot_i]["alpha"] *= 3 
                
            for name_multidata2plot_i, multidata2plot_i in plotdef.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                raise NotImplementedError("Plotting of MultiData2Plot is not implemented yet")
            
            for name_multimodel2plot_i, multimodel2plot_i in plotdef.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                raise NotImplementedError("Plotting of MultiModel2Plot is not implemented yet")

            ###################################
            # Set ylims and indicate_y_outliers
            ###################################
            logger.debug(f"Setting ylims and indicating outliers for row {i_row}, column {i_col}")
            # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
            for axe, data_or_resi, points, pad, indicate_outliers in zip((axe_data, axe_resi), ("data", "resi"), (dico_data, dico_resi), 
                                                                         (plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.pad, plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.pad),
                                                                         (plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.indicate_outliers, plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.indicate_outliers),
                                                                         ):
                # Set the y axis limits
                if data_or_resi == "data":
                    y_lims_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.lims
                else:
                    y_lims_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.lims
                if all([y_lims_i[jj] is None for jj in range(2)]):
                    if len(plotdef.get_datas2plot(i_row=i_row, i_col=i_col)):
                        points_pl_i = concatenate([points[name_data2plot_i] for name_data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col)])
                        et.auto_y_lims(points_pl_i[isfinite(points_pl_i)], axe, pad=pad)
                else:
                    axe.set_ylim(y_lims_i)

                # Indicate outlier values that are off y-axis with an arrows for raw cadence
                if indicate_outliers:
                    for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                        et.indicate_y_outliers(x=dico_times[name_data2plot_i], y=points[name_data2plot_i], ax=axe,
                                                color=pl_kwarg_to_use[name_data2plot_i]["color"],
                                                alpha=pl_kwarg_to_use[name_data2plot_i]["alpha"])

            # # Draw a horizontal line at 0 in the residual plot
            # axe_resi.hlines(0, *current_xlims, colors="k", linestyles="dashed")
            logger.debug(f"Done: Set ylims and indicate outliers for row {i_row}, column {i_col}")

            ############################
            # Set the tlims if provided
            ############################
            logger.debug(f"Setting xlims for row {i_row}, column {i_col}")
            axe_data.set_xlim(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).x.lims)
            logger.debug(f"Done: Set xlims for row {i_row}, column {i_col}")

            ##########################
            # Set the legend if needed
            ##########################
            if plotdef.get_axes_properties(i_row=i_row, i_col=i_col).do_legend:
                set_legend(ax=axe_data, legend_kwargs=plotdef.get_axes_properties(i_row=i_row, i_col=i_col).legend_kwargs, fontsize_def=fontsize)

    logger.debug("Done: TS plot")
    return computedmodels_db, rms_values