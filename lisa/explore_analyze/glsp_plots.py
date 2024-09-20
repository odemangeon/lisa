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

from .misc import AandA_fontsize,check_kwargs_by_column_and_row, fmt_sci_not
from .core_plot import PlotsDefinition, ComputedModels_Database
from .binning import compute_binning
from .core_compute_load import compute_model, get_key_compute_model, compute_data_err_jittered
from ..posterior.core.posterior import Posterior

from gls_mod import Gls


day2sec = 24 * 60 * 60


def create_GLSP_plots(post_instance:Posterior, df_fittedval:DataFrame,
                      compute_raw_models_func: Callable,
                      plotdef:PlotsDefinition,
                      computedmodels_db:ComputedModels_Database|None=None,
                      split_GP_computation:int|None=None,
                      datasim_kwargs:dict|None=None,
                      amplitude_fact:float|None=None, unit:str|None=None,
                      amplitude_name:str|None=None,
                      logscale:bool|None=None,
                      legend_param:dict|None=None,
                      time_fact:float|None=None, time_unit:str|None=None,
                      frequence_fact:float|None=None, frequence_unit:str|None=None,
                      period_range:tuple[float, float]|None=None,
                      period_no_ticklabels:list[int]|None=None,
                      scientific_notation_P_axis:bool|None=None,
                      periods:dict[float, dict]|None=None,
                      create_axes_main_gridspec:dict|None=None,
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

    # Make sure that legend_kwargs is well defined
    legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=legend_kwargs, l_row_name=list(range(plotdef.nb_rows)), l_col_name=list(range(plotdef.nb_cols)),
                                                   kwargs_def={'do': False}, kwargs_init={0: {i_row: {'do': True} for i_row in range(plotdef.nb_rows)}}
                                                   )

    # Set defautl values for parameters
    if time_fact is None:
        time_fact = 1.
    if time_unit is None:
        time_unit = 'days'
    if frequence_fact is None:
        frequence_fact = 1e6
    if frequence_unit is None:
        frequence_unit = '$\mu$Hz'
    if amplitude_fact is None:
        amplitude_fact = 1.
    if period_range is None:
        period_range = (0.1, 1000)
    if logscale is None:
        logscale = False
    if legend_param is None:
        legend_param = {}
    if period_no_ticklabels is None:
        period_no_ticklabels = []
    if scientific_notation_P_axis is None:
        scientific_notation_P_axis = True
    if periods is None:
        periods = {}

    for i_row in range(plotdef.nb_rows):
        for i_col in range(plotdef.nb_cols):
            logger.debug(f"Doing GLSP plot for row {i_row}/{plotdef.nb_rows}, column {i_col}/{plotdef.nb_cols}")
            subplotspec_i = gs[i_row, i_col]
            Pbeg, Pend = period_range
            gls_inputs = {}
            
            # Load the input for the glsp computation
            for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_data2plot_i] = {}
                times_dataset_i = data2plot_i.get_times_dataset(post_instance=post_instance)
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
                gls_inputs[name_data2plot_i]["times"] = gls_inputs[name_data2plot_i]["times"][idx_sort] * time_fact
                gls_inputs[name_data2plot_i]["values"] = gls_inputs[name_data2plot_i]["values"][idx_sort] * amplitude_fact
                gls_inputs[name_data2plot_i]["errors"] = gls_inputs[name_data2plot_i]["errors"][idx_sort] * amplitude_fact
            
            for name_multidata2plot_i, multidata2plot_i in plotdef.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_multidata2plot_i] = {}
                times = []
                values = []
                errors = []
                for data2plot_i in multidata2plot_i.l_data2plot:
                    # Compute values and errors
                    times_dataset_i = data2plot_i.get_times_dataset(post_instance=post_instance)
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
                gls_inputs[name_multidata2plot_i]["times"] = gls_inputs[name_multidata2plot_i]["times"][idx_sort] * time_fact
                gls_inputs[name_multidata2plot_i]["values"] = concatenate(values)[idx_sort] * amplitude_fact
                gls_inputs[name_multidata2plot_i]["errors"] = concatenate(errors)[idx_sort] * amplitude_fact

            for name_model2plot_i, model2plot_i in plotdef.get_models2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_model2plot_i] = {}
                # Compute values and errors
                times_dataset_i = model2plot_i.get_times_dataset(post_instance=post_instance)
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
                gls_inputs[name_model2plot_i]["times"] = gls_inputs[name_model2plot_i]["times"][idx_sort] * time_fact
                gls_inputs[name_model2plot_i]["values"] = gls_inputs[name_model2plot_i]["values"][idx_sort] * amplitude_fact
                gls_inputs[name_model2plot_i]["errors"] = gls_inputs[name_model2plot_i]["errors"][idx_sort] * amplitude_fact

            for name_multimodel2plot_i, multimodel2plot_i in plotdef.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                gls_inputs[name_multimodel2plot_i] = {}
                times = []
                values = []
                errors = []
                for model2plot_i in multimodel2plot_i.l_model2plot:
                    # Compute values and errors
                    times_dataset_i = model2plot_i.get_times_dataset(post_instance=post_instance)
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
                gls_inputs[name_multimodel2plot_i]["times"] = gls_inputs[name_multimodel2plot_i]["times"][idx_sort] * time_fact
                gls_inputs[name_multimodel2plot_i]["values"] = concatenate(values)[idx_sort] * amplitude_fact
                gls_inputs[name_multimodel2plot_i]["errors"] = concatenate(errors)[idx_sort] * amplitude_fact

            # Create the axis
            # show_WF = GLSP_kwargs.get("show_WF", True)
            ax_glsp = fig.add_subplot(subplotspec_i)

            glsps = {}
            for key in gls_inputs:
                glsps[key] = Gls((gls_inputs[key]["times"], gls_inputs[key]["values"], gls_inputs[key]["errors"]), Pbeg=Pbeg, Pend=Pend, verbose=False)
                            
                # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
                pl_kwargs = copy(plotdef.things2plot[key].pl_kwargs)
                ax_glsp.plot(glsps[key].freq / day2sec * frequence_fact, glsps[key].power, **pl_kwargs)

            if len(glsps) > 0:
                if logscale:
                    ax_glsp.set_xscale("log")
                ax_glsp.set_xlabel(f"Frequency [{frequence_unit}]", fontsize=fontsize)
                freq_lims = plotdef.get_axis_xlims(i_row=i_row, i_col=i_col) 

                # create and set the twiny axis
                ax_glsp_period = ax_glsp.twiny()
                if logscale:
                    ax_glsp_period.set_xscale("log")
                ax_glsp.set_zorder(ax_glsp_period.get_zorder() + 1)  # To make sure that the orginal axis is above the new one
                ax_glsp.patch.set_visible(False)
                ax_glsp_period.tick_params(axis="x", labeltop=True, labelsize=fontsize, which="both", direction="in")
                ax_glsp_period.tick_params(axis="x", which="major", length=4, width=1)
                ax_glsp_period.tick_params(axis="x", which="minor", length=2, width=0.5)
                ax_glsp.tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
                ax_glsp.tick_params(axis="both", which="major", length=4, width=1)
                ax_glsp.tick_params(axis="both", which="minor", length=2, width=0.5)
                ax_glsp.tick_params(axis="x", labelleft=True, labelbottom=True, labelsize=fontsize, which="both", direction="in")
                ax_glsp.tick_params(axis="y", labelleft=True, labelsize=fontsize, which="both", direction="in")
                ax_glsp.yaxis.set_minor_locator(AutoMinorLocator())
                ax_glsp.xaxis.set_minor_locator(AutoMinorLocator())

                # Set ticks and tick labels
                ax_glsp.set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # {gls_inputs[key]['label']}
                ylims = ax_glsp.get_ylim()
                xlims = ax_glsp.get_xlim()
                # Print the period axis
                per_min = min(1 / glsps[key].freq)
                freq_min = min(glsps[key].freq)
                per_max = max(1 / glsps[key].freq)
                freq_max = max(glsps[key].freq)
                per_xlims = [1 / (freq_lim_i / frequence_fact * day2sec) for freq_lim_i in xlims]
                if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
                    per_xlims[0] = per_max
                per_xlims = per_xlims[::-1]
                if not(logscale):
                    ax_glsp_period.plot([freq_min / day2sec * frequence_fact, freq_max / day2sec * frequence_fact],
                                        [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                else:
                    ax_glsp_period.plot([per_min, per_max], [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                    xlims_per = ax_glsp_period.get_xlim()
                    ax_glsp_period.set_xlim(xlims_per[::-1])
                if not(logscale):
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
                    # ax_glsp_period.set_xticks(per_ticks_minor, minor=True)
                    ax_glsp_period.set_xticks([1 / tick / day2sec * frequence_fact for tick in per_ticks_major])
                    if scientific_notation_P_axis:
                        ax_glsp_period.set_xticklabels([fmt_sci_not(tick) if tick != "" else "" for tick in per_ticklabels_major])
                    else:
                        ax_glsp_period.set_xticklabels(per_ticklabels_major)
                    # ax_glsp_period.set_xticks(per_ticks_minor, minor=True)
                    ax_glsp_period.set_xticks([1 / tick / day2sec * frequence_fact for tick in per_ticks_minor], minor=True)

                if freq_lims is None:
                    ax_glsp.set_xlim(xlims)
                    if logscale:
                        ax_glsp_period.set_xlim(xlims_per[::-1])
                    else:
                        ax_glsp_period.set_xlim(xlims)
                else:
                    ax_glsp.set_xlim(freq_lims)
                    if logscale:
                        ax_glsp_period.set_xlim([1 / (freq / frequence_fact * day2sec) for freq in freq_lims])
                    else:
                        ax_glsp_period.set_xlim(freq_lims)

                ylims = ax_glsp.get_ylim()
                xlims = ax_glsp.get_xlim()

                #####################################
                # Vertical lines at specified periods
                #####################################
                for per, dico_per in periods.items():
                    vlines_kwargs = dico_per.get("vlines_kwargs", {})
                    if 'label' not in vlines_kwargs:
                        vlines_kwargs['label'] = str(format_float_positional(per, precision=3, unique=False, fractional=False, trim='k'))
                    freq_4_per = 1 / per / day2sec * frequence_fact
                    lines_per = ax_glsp.vlines(freq_4_per, *ylims, **vlines_kwargs)
                ax_glsp.set_ylim(ylims)

                ##########################################
                # Horizontal lines at specified FAP levels
                ##########################################
                ylims = ax_glsp.get_ylim()
                xlims = ax_glsp.get_xlim()

                default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
                                    1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
                                    10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
                for fap_lvl, dico_fap in default_fap_dict.items():
                    pow_ii = glsps[key].powerLevel(fap_lvl / 100)
                    hlines_kwargs = dico_fap.get("hlines_kwargs", {})
                    if pow_ii < ylims[1]:
                        lines_fap = ax_glsp.hlines(pow_ii, *xlims, **hlines_kwargs)
                        text_kwargs = dico_fap.get("text_kwargs", {}).copy()
                        x_pos = text_kwargs.pop("x_pos", 1.05)
                        y_shift = text_kwargs.pop("y_shift", 0)
                        label = str(text_kwargs.pop("label", fr"{fap_lvl}\%"))
                        color = text_kwargs.pop("color", None)
                        if color is None:
                            color = lines_fap.get_color()[0]
                        ax_glsp.text(xlims[0] + x_pos * (xlims[1] - xlims[0]), pow_ii + y_shift * (ylims[1] - ylims[0]),
                                        label, color=color, fontsize=fontsize, **text_kwargs)

                ax_glsp.set_xlim(xlims)
                #
                ax_glsp.legend(fontsize=fontsize, **legend_param)

                ax_glsp_period.set_xlabel("Period [days]", fontsize=fontsize)

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