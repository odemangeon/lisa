"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from numpy import min, max, concatenate, argsort, mean, floor, log10, ceil, format_float_positional
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec, SubplotSpec
from matplotlib.figure import Figure
from loguru import logger
from copy import copy
from pandas import DataFrame
from typing import Callable

from .misc import AandA_fontsize, fmt_sci_not, set_legend
from .core_plot import PlotsDefinition_GLSP, ComputedModels_Database
from .binning import compute_binning
from .core_compute_load import compute_model, get_key_compute_model, compute_data_err_jittered
from ..posterior.core.posterior import Posterior
from ..emcee_tools import emcee_tools as et

from gls_mod import Gls


# day2sec = 24 * 60 * 60


def create_GLSP_plots(post_instance:Posterior, df_fittedval:DataFrame,
                      compute_raw_models_func: Callable,
                      plotdef:PlotsDefinition_GLSP,
                      period_range:tuple[float, float],
                      computedmodels_db:ComputedModels_Database|None=None,
                      split_GP_computation:int|None=None,
                      datasim_kwargs:dict|None=None,
                      period_no_ticklabels:list[int]|None=None,
                      scientific_notation_P_axis:bool|None=None,
                      periods:dict[float, dict]|None=None,
                      create_axes_main_gridspec:dict|None=None,
                      create_axes_glspwf_gridspec:dict|None=None,
                      legend_kwargs:dict|None=None,
                      npt_model_default:int|None=None,
                      extra_dt_model:float|None=None,
                      fontsize=AandA_fontsize,
                      get_key_compute_model_func=get_key_compute_model,
                      kwargs_get_key_compute_model=None,
                      fig:Figure|None=None,
                      subplotspec:SubplotSpec|None=None,
                      ):
    logger.debug("Doing GLSP plot")
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

    # Set default values for parameters
    if period_no_ticklabels is None:
        period_no_ticklabels = []
    if scientific_notation_P_axis is None:
        scientific_notation_P_axis = True
    if periods is None:
        periods = {}

    ############################
    # Make the glsp and WF plots
    ############################
    for i_row in range(plotdef.nb_rows):
        for i_col in range(plotdef.nb_cols):
            logger.debug(f"Doing GLSP plot for row {i_row}/{plotdef.nb_rows}, column {i_col}/{plotdef.nb_cols}")
            subplotspec_i = gs[i_row, i_col]
            Pbeg, Pend = period_range
            gls_inputs = {}

            # Create the data and residuals axes and set properties ans style
            axes_properties_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col)
            if axes_properties_i.WF:
                (axe_glsp, axe_wf) = et.add_twoaxeswithsharex(subplotspec_i, fig, gs_from_sps_kw=create_axes_glspwf_gridspec)  # gs_from_sps_kw={"wspace": 0.1}
                l_axe = [axe_glsp, axe_wf]
            else:
                axe_glsp = fig.add_subplot(subplotspec_i)
                l_axe = [axe_glsp, ]

            # create and set the twiny axis
            l_axe_twin = [axe.twiny() for axe in l_axe]

            l_axe[-1].set_xlabel(axes_properties_i.x.label, fontsize=fontsize)
            
            l_axe_twin[0].set_xlabel("Period (1/Frequency)", fontsize=fontsize)

            l_yaxis_properties = [getattr(axes_properties_i, axe_name) for axe, axe_name in zip(l_axe, ["yglsp", "ywf"])]
            l_ylabel = [yaxis_properties_i.label for yaxis_properties_i in l_yaxis_properties]
            l_yshowlabel = [yaxis_properties_i.show_label for yaxis_properties_i in l_yaxis_properties]
            for axe, ylabel, yshowlabel in zip(l_axe, l_ylabel, l_yshowlabel):
                if yshowlabel and (len(ylabel) > 0):
                    axe.set_ylabel(ylabel, fontsize=fontsize)
            for axe, yaxis_properties_i in zip(l_axe, l_yaxis_properties): 
                axe.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False, labelsize=fontsize)
                axe.xaxis.set_minor_locator(AutoMinorLocator())
                axe.yaxis.set_minor_locator(AutoMinorLocator())
                axe.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
                axe.grid(axis="y", color="black", alpha=.5, linewidth=.5)
                if yaxis_properties_i.logscale:
                    axe.set_xscale("log")

            #########################
            # Set the title if needed
            #########################
            if plotdef.get_axes_properties(i_row=i_row, i_col=i_col).show_title and (len(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).title) > 0):
                axe_glsp.set_title(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).title, fontsize=fontsize)
            
            #######################
            # load the data plotdef
            #######################
            for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_data2plot_i] = {}
                times_dataset_i = data2plot_i.get_times_dataset(post_instance=post_instance)
                time_fact_i = data2plot_i.pl_factors.time_factor
                amplitude_fact_i = data2plot_i.pl_factors.value_factor
                data_i, data_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                    compute_raw_models_func=compute_raw_models_func, 
                                                    expression=data2plot_i.expression, times=times_dataset_i, datasetname=data2plot_i.datasetname,
                                                    exptime=None, supersampling=None,
                                                    computedmodels_db=computedmodels_db, 
                                                    get_key_compute_model_func=get_key_compute_model,
                                                    kwargs_get_key_compute_model=None,
                                                    split_GP_computation=split_GP_computation
                                                    )
                # Compute jittered_errors
                data_err_jitter_i = compute_data_err_jittered(data_err=data_err_i, post_instance=post_instance, datasetname=data2plot_i.datasetname, df_fittedval=df_fittedval)  
                # Bin the residuals if needed
                if data2plot_i.exptime > 0:
                    (bins_i, _, bindata_i, bindata_std_i, bindata_std_jitter_i
                        ) = compute_binning(times_dataset=times_dataset_i, values=data_i, errors=data_err_i, errors_jitter=data_err_jitter_i, exptime=data2plot_i.exptime, method=data2plot_i.method)
                    midbins_i = bins_i[:-1] + data2plot_i.exptime / 2
                    gls_inputs[name_data2plot_i]["times"] = midbins_i
                    gls_inputs[name_data2plot_i]["values"] = bindata_i
                    gls_inputs[name_data2plot_i]["errors"] = bindata_std_i
                else:
                    gls_inputs[name_data2plot_i]["times"] = times_dataset_i
                    gls_inputs[name_data2plot_i]["values"] = data_i
                    gls_inputs[name_data2plot_i]["errors"] = data_err_i
                idx_sort = argsort(gls_inputs[name_data2plot_i]["times"])
                gls_inputs[name_data2plot_i]["times"] = gls_inputs[name_data2plot_i]["times"][idx_sort] * time_fact_i
                gls_inputs[name_data2plot_i]["values"] = gls_inputs[name_data2plot_i]["values"][idx_sort] * amplitude_fact_i
                gls_inputs[name_data2plot_i]["errors"] = gls_inputs[name_data2plot_i]["errors"][idx_sort] * amplitude_fact_i
            
            for name_multidata2plot_i, multidata2plot_i in plotdef.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_multidata2plot_i] = {}
                times = []
                values = []
                errors = []
                for data2plot_i in multidata2plot_i.l_data2plot:
                    # Compute values and errors
                    times_dataset_i = data2plot_i.get_times_dataset(post_instance=post_instance)
                    time_fact_i = data2plot_i.pl_factors.time_factor
                    amplitude_fact_i = data2plot_i.pl_factors.value_factor
                    data_i, data_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                        compute_raw_models_func=compute_raw_models_func, 
                                                        expression=data2plot_i.expression, times=times_dataset_i, datasetname=data2plot_i.datasetname,
                                                        exptime=None, supersampling=None,
                                                        computedmodels_db=computedmodels_db, 
                                                        get_key_compute_model_func=get_key_compute_model,
                                                        kwargs_get_key_compute_model=None,
                                                        split_GP_computation=split_GP_computation
                                                        )
                    # Compute jittered_errors
                    data_err_jitter_i = compute_data_err_jittered(data_err=data_err_i, post_instance=post_instance, datasetname=data2plot_i.datasetname, df_fittedval=df_fittedval)  
                    # Bin the residuals if needed
                    if data2plot_i.exptime > 0:
                        (bins_i, _, bindata_i, bindata_std_i, bindata_std_jitter_i
                            ) = compute_binning(times_dataset=times_dataset_i, values=data_i, errors=data_err_i, errors_jitter=data_err_jitter_i, exptime=data2plot_i.exptime, method=data2plot_i.method)
                        midbins_i = bins_i[:-1] + data2plot_i.exptime / 2
                        times.append(midbins_i)
                        values.append(bindata_i)
                        errors.append(bindata_std_i)
                    else:
                        times.append(times_dataset_i)
                        values.append(data_i)
                        errors.append(data_err_i)
                gls_inputs[name_multidata2plot_i]["times"] = concatenate(times)
                idx_sort = argsort(gls_inputs[name_multidata2plot_i]["times"])
                gls_inputs[name_multidata2plot_i]["times"] = gls_inputs[name_multidata2plot_i]["times"][idx_sort] * time_fact_i
                gls_inputs[name_multidata2plot_i]["values"] = concatenate(values)[idx_sort] * amplitude_fact_i
                gls_inputs[name_multidata2plot_i]["errors"] = concatenate(errors)[idx_sort] * amplitude_fact_i

            for name_model2plot_i, model2plot_i in plotdef.get_models2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_model2plot_i] = {}
                # Compute values and errors
                times_dataset_i = model2plot_i.get_times_dataset(post_instance=post_instance)
                time_fact_i = model2plot_i.pl_factors.time_factor
                amplitude_fact_i = model2plot_i.pl_factors.value_factor
                # Compute the model
                model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                        compute_raw_models_func=compute_raw_models_func, 
                                                        expression=model2plot_i.expression, times=times_dataset_i, datasetname=model2plot_i.datasetname,
                                                        exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                        computedmodels_db=computedmodels_db, 
                                                        get_key_compute_model_func=get_key_compute_model,
                                                        kwargs_get_key_compute_model=None,
                                                        split_GP_computation=split_GP_computation)
                gls_inputs[name_model2plot_i]["times"] = times_dataset_i
                gls_inputs[name_model2plot_i]["values"] = model_i
                if model_err_i is None:
                    gls_inputs[name_model2plot_i]["errors"] = model2plot_i.get_errors_datasets(post_instance=post_instance)
                else:
                    gls_inputs[name_model2plot_i]["errors"] = model_err_i
                idx_sort = argsort(gls_inputs[name_model2plot_i]["times"])
                gls_inputs[name_model2plot_i]["times"] = gls_inputs[name_model2plot_i]["times"][idx_sort] * time_fact_i
                gls_inputs[name_model2plot_i]["values"] = gls_inputs[name_model2plot_i]["values"][idx_sort] * amplitude_fact_i
                gls_inputs[name_model2plot_i]["errors"] = gls_inputs[name_model2plot_i]["errors"][idx_sort] * amplitude_fact_i

            for name_multimodel2plot_i, multimodel2plot_i in plotdef.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_multimodel2plot_i] = {}
                times = []
                values = []
                errors = []
                for model2plot_i in multimodel2plot_i.l_model2plot:
                    # Compute values and errors
                    times_dataset_i = model2plot_i.get_times_dataset(post_instance=post_instance)
                    time_fact_i = model2plot_i.pl_factors.time_factor
                    amplitude_fact_i = model2plot_i.pl_factors.value_factor
                    # Compute the model
                    model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                            compute_raw_models_func=compute_raw_models_func, 
                                                            expression=model2plot_i.expression, times=times_dataset_i, datasetname=model2plot_i.datasetname,
                                                            exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                            computedmodels_db=computedmodels_db, 
                                                            get_key_compute_model_func=get_key_compute_model,
                                                            kwargs_get_key_compute_model=None,
                                                            split_GP_computation=split_GP_computation)
                    times.append(times_dataset_i)
                    values.append(model_i)
                    if model_err_i is None:
                        errors.append(model2plot_i.get_errors_datasets(post_instance=post_instance))
                    else:
                        errors.append(model_err_i)
                gls_inputs[name_multimodel2plot_i]["times"] = concatenate(times)
                idx_sort = argsort(gls_inputs[name_multimodel2plot_i]["times"])
                gls_inputs[name_multimodel2plot_i]["times"] = gls_inputs[name_multimodel2plot_i]["times"][idx_sort] * time_fact_i
                gls_inputs[name_multimodel2plot_i]["values"] = concatenate(values)[idx_sort] * amplitude_fact_i
                gls_inputs[name_multimodel2plot_i]["errors"] = concatenate(errors)[idx_sort] * amplitude_fact_i

            glsps = {}
            for key in gls_inputs:
                glsps[key] = Gls((gls_inputs[key]["times"], gls_inputs[key]["values"], gls_inputs[key]["errors"]), Pbeg=Pbeg, Pend=Pend, verbose=False)
                            
                # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
                pl_kwargs = copy(plotdef.things2plot[key].pl_kwargs)
                axe_glsp.plot(glsps[key].freq, glsps[key].power, **pl_kwargs)

            if len(glsps) > 0:
                freq_lims = plotdef.get_axes_properties(i_row=i_row, i_col=i_col).x.lims
                for axe, axe_twin in zip(l_axe, l_axe_twin):
                    axe.set_zorder(axe_twin.get_zorder() + 1)  # To make sure that the orginal axis is above the new one
                    axe.patch.set_visible(False)
                    axe_twin.tick_params(axis="x", labeltop=True, labelsize=fontsize, which="both", direction="in")
                    axe_twin.tick_params(axis="x", which="major", length=4, width=1)
                    axe_twin.tick_params(axis="x", which="minor", length=2, width=0.5)
                    axe.tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
                    axe.tick_params(axis="both", which="major", length=4, width=1)
                    axe.tick_params(axis="both", which="minor", length=2, width=0.5)
                    axe.tick_params(axis="x", labelleft=True, labelbottom=True, labelsize=fontsize, which="both", direction="in")
                    axe.tick_params(axis="y", labelleft=True, labelsize=fontsize, which="both", direction="in")
                    axe.yaxis.set_minor_locator(AutoMinorLocator())
                    axe.xaxis.set_minor_locator(AutoMinorLocator())

                # Set ticks and tick labels
                axe_glsp.set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # {gls_inputs[key]['label']}
                ylims = axe_glsp.get_ylim()
                xlims = axe_glsp.get_xlim()
                # Print the period axis
                per_min = min(1 / glsps[key].freq)
                freq_min = min(glsps[key].freq)
                per_max = max(1 / glsps[key].freq)
                freq_max = max(glsps[key].freq)
                per_xlims = [1 / freq_lim_i for freq_lim_i in xlims]
                if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
                    per_xlims[0] = per_max
                per_xlims = per_xlims[::-1]
                if not(axes_properties_i.x.logscale):
                    axe_twin.plot([freq_min, freq_max],
                                  [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                else:
                    axe_twin.plot([per_min, per_max], [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                    xlims_per = axe_twin.get_xlim()
                    axe_twin.set_xlim(xlims_per[::-1])
                if not(axes_properties_i.x.logscale):
                    per_decades = [10**(exp) for exp in list(range(int(floor(log10(per_min))), int(ceil(log10(per_max))) + 1))]
                    per_ticks_major = []
                    per_ticklabels_major = []
                    per_ticks_minor = []
                    for dec in per_decades:
                        for fact in range(1, 10):
                            tick = dec * fact
                            if (tick > per_xlims[0]) and (tick < per_xlims[1]):
                                if fact == 1:
                                    per_ticks_major.append(tick)
                                    if tick in period_no_ticklabels:
                                        per_ticklabels_major.append("")
                                    else:
                                        per_ticklabels_major.append(tick)
                                else:
                                    per_ticks_minor.append(tick)
                    # axe_glsp_period.set_xticks(per_ticks_minor, minor=True)
                    axe_twin.set_xticks([1 / tick for tick in per_ticks_major])
                    if scientific_notation_P_axis:
                        axe_twin.set_xticklabels([fmt_sci_not(tick) if tick != "" else "" for tick in per_ticklabels_major])
                    else:
                        axe_twin.set_xticklabels(per_ticklabels_major)
                    # axe_glsp_period.set_xticks(per_ticks_minor, minor=True)
                    axe_twin.set_xticks([1 / tick for tick in per_ticks_minor], minor=True)

                if freq_lims is None:
                    axe_glsp.set_xlim(xlims)
                    if axes_properties_i.x.logscale:
                        axe_twin.set_xlim(xlims_per[::-1])
                    else:
                        axe_twin.set_xlim(xlims)
                else:
                    axe_glsp.set_xlim(freq_lims)
                    if axes_properties_i.x.logscale:
                        axe_twin.set_xlim([1 / (freq) for freq in freq_lims])
                    else:
                        axe_twin.set_xlim(freq_lims)

                ylims = axe_glsp.get_ylim()
                xlims = axe_glsp.get_xlim()

                #####################################
                # Vertical lines at specified periods
                #####################################
                for per, dico_per in periods.items():
                    vlines_kwargs = dico_per.get("vlines_kwargs", {})
                    if 'label' not in vlines_kwargs:
                        vlines_kwargs['label'] = str(format_float_positional(per, precision=3, unique=False, fractional=False, trim='k'))
                    freq_4_per = 1 / per
                    lines_per = axe_glsp.vlines(freq_4_per, *ylims, **vlines_kwargs)
                axe_glsp.set_ylim(ylims)

                ##########################################
                # Horizontal lines at specified FAP levels
                ##########################################
                ylims = axe_glsp.get_ylim()
                xlims = axe_glsp.get_xlim()

                default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
                                    1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
                                    10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
                for fap_lvl, dico_fap in default_fap_dict.items():
                    pow_ii = glsps[key].powerLevel(fap_lvl / 100)
                    hlines_kwargs = dico_fap.get("hlines_kwargs", {})
                    if pow_ii < ylims[1]:
                        lines_fap = axe_glsp.hlines(pow_ii, *xlims, **hlines_kwargs)
                        text_kwargs = dico_fap.get("text_kwargs", {}).copy()
                        x_pos = text_kwargs.pop("x_pos", 1.05)
                        y_shift = text_kwargs.pop("y_shift", 0)
                        label = str(text_kwargs.pop("label", fr"{fap_lvl}\%"))
                        color = text_kwargs.pop("color", None)
                        if color is None:
                            color = lines_fap.get_color()[0]
                        axe_glsp.text(xlims[0] + x_pos * (xlims[1] - xlims[0]), pow_ii + y_shift * (ylims[1] - ylims[0]),
                                        label, color=color, fontsize=fontsize, **text_kwargs)

                axe_glsp.set_xlim(xlims)

            ############################
            # Set the x lims if provided
            ############################
            logger.debug(f"Setting xlims for row {i_row}, column {i_col}")
            for axe in l_axe:
                axe.set_xlim(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).x.lims)
            logger.debug(f"Done: Set xlims for row {i_row}, column {i_col}")

            ##########################
            # Set the legend if needed
            ##########################
            if plotdef.get_axes_properties(i_row=i_row, i_col=i_col).do_legend:
                set_legend(ax=axe_glsp, legend_kwargs=plotdef.get_axes_properties(i_row=i_row, i_col=i_col).legend_kwargs, fontsize_def=fontsize)
        

                # if GLSP_kwargs.get("show_WF", True):
                #     for i_WF, l_WF_key_model in enumerate(l_l_WF_key_model):
                #         ax_gls[-i_WF - 1].plot(glsps[l_WF_key_model[0]].freq / day2sec * freq_fact, glsps[l_WF_key_model[0]].wf, '-', color="k", label=f"WF {l_WF_key_model}", linewidth=GLSP_kwargs.get("lw ", 1.))
                #         if jj == 0:
                #             ax_gls[-i_WF - 1].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get("WF", {}))
                #             ax_gls[-i_WF - 1].set_ylabel("Relative Amplitude")
                #         labelleft = True if jj == 0 else False
                #         ax_gls[-i_WF - 1].tick_params(axis="both", labelleft=labelleft, labelsize=fontsize, right=True, which="both", direction="in")
        logger.debug("Done: GLSP plot")
    return computedmodels_db