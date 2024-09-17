"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from numpy import (linspace, inf, min, max, arange, std, logical_and, zeros, where, sqrt, sum, power,
                   nan, nanstd, concatenate, ones_like, argsort, mean, floor, log10, ceil, format_float_positional
                   )
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.figure import Figure
from scipy.stats import binned_statistic
from loguru import logger
from copy import copy
from pandas import DataFrame
from typing import Callable, Dict, List, Union
from numpy.typing import NDArray

from .misc import (AandA_fontsize, do_suptitle, check_row4datasetname, get_pl_kwargs, update_data_binned_label,
                   check_spec_by_column_or_row, check_spec_data_or_resi,
                   define_x_or_y_lims, check_spec_for_data_or_resi_by_column_or_row, print_rms, check_kwargs_by_column_and_row,
                   set_legend, fmt_sci_not,
                   )
# from .models2computenplot import Models2plotTS, check_Models2plot
from .core_plot import PlotsDefinition, ComputedModels_Database, Expression
from .binning import compute_binning
from .core_compute_load import (load_datasets_and_models, compute_model, get_key_compute_model,
                                is_valid_model_available, compute_data_err_jittered
                                )
from ..emcee_tools import emcee_tools as et
from ..posterior.core.model.core_model import Core_Model
from ..posterior.core.posterior import Posterior

from gls_mod import Gls


key_whole = Core_Model.key_whole


day2sec = 24 * 60 * 60


def create_TSNGLSP_plots(fig:Figure, post_instance:Posterior, df_fittedval:DataFrame,
                         y_name: str, inst_cat: str,
                         compute_raw_models_func: Callable,
                         plotdef_TS:PlotsDefinition,
                         plotdef_GLSP:PlotsDefinition|None=None,
                         computedmodels_db:ComputedModels_Database|None=None,
                         split_GP_computation=None,
                         datasim_kwargs=None,
                         amplitude_fact=1., unit=None,
                         create_axes_kwargs=None,
                         TS_kwargs=None,
                         GLSP_kwargs=None,
                         fontsize=AandA_fontsize,
                         get_key_compute_model_func=get_key_compute_model,
                         kwargs_get_key_compute_model=None
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
    create_axes_kwargs     : dict
    remove_dict   : dict
    TS_kwargs     : None or dict
            - 'npt_model': int (Def: 1000) giving the number of points to use for the model
            - 'extra_dt_model': float (Def: 0)
                Specify the extra time that for which you want to compute the model before and after the
                data.
            - 'time_fact': float (Def: 1)
                Factor to apply to the time
            - 'time_unit': str (Def: days)
                String that is going to be used to give the unit (and reference system) of the time.
            - 'pad': Iterable of 2 floats (Def: (0.1, 0.1))
                Define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
            - 'indicate_y_outliers': boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
            - 'show_title'  : bool
                If True, show the titles (of the main and the zoom)
            - 'legend_kwargs' : dict of dict
                keys are 'all' or int providing the row index ('all' applies to all row, but the row index overwrite it)
                Values are dict whose keys are:
                    'do'    : bool
                        (Default: True) Whether or not to show the legend
                    other keys are passed to the pyplot.legend function
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
    suptitle_kwargs : dict
        Dictionary which defines the properties of the suptitle. See docstring of do_suptitle for details
    amplitude_fact       : float
        Factor to apply to the data
    unit        : str
        String giving the unit of the data

    Returns
    -------
    dico_load       : dict  
        Output of the function core_compute_load.load_datasets_and_models
    computed_models_4_TS : dict
        Outputs of the compute_and_plot_model function calls
    """
    logger.debug("Start create_TSNGLSP_plots")
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")
    # Make sure that create_axes_kwargs is well defined
    create_axes_kwargs_user = create_axes_kwargs if create_axes_kwargs is not None else {}
    create_axes_kwargs = {'main_gridspec': {}, 'gridspec_row_TS': {}, 'gridspec_col_TS': {}, 'add_twoaxeswithsharex_TS': {},
                          'add_axeswithsharex_GLSP': {}
                          }
    for key in create_axes_kwargs_user:
        if key in create_axes_kwargs:
            create_axes_kwargs[key].update(create_axes_kwargs_user[key])
        else:
            raise ValueError(f"{key} is not a valid key for create_axes_kwargs, should be in ['main_gridspec', 'add_axeswithsharex']")

    # Make sure that the TS_kwargs and GLSP_kwargs are well defined
    if TS_kwargs is None:
        TS_kwargs = {}

    if GLSP_kwargs is None:
        GLSP_kwargs = {}

    # Create The GridSpec
    do_TS = plotdef_TS is not None
    do_GLSP = plotdef_GLSP is not None
    gs = GridSpec(nrows=1, ncols=int(do_TS) + int(do_GLSP),
                  figure=fig, **create_axes_kwargs['main_gridspec']
                  )
    if do_TS:
        gs_ts = gs[0]
        if do_GLSP:
            gs_gls = gs[1]
    else:
        gs_gls = gs[0]

    # If no ComputedModels_Database is provided create a new one
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    #############
    # TIME SERIES
    #############
    if do_TS:
        logger.debug("Doing TS plot")

        # Make sure that indicate_y_outliers is well defined
        indicate_y_outliers = check_spec_data_or_resi(spec_user=TS_kwargs.get('indicate_y_outliers', None), l_type_spec=[bool], spec_def=True)

        # Make sure that pad is well defined
        pad = check_spec_data_or_resi(spec_user=TS_kwargs.get('pad', None), l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

        # Create the updated grid space for TS according to the number of rows and cols specified in plotdef_TS
        gs_ts = GridSpecFromSubplotSpec(plotdef_TS.nb_rows, plotdef_TS.nb_cols, subplot_spec=gs_ts, **create_axes_kwargs['gridspec_row_TS'])

        # Make sure that legend_kwargs is well defined
        legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=TS_kwargs.get('legend_kwargs', None),
                                                       l_row_name=list(range(plotdef_TS.nb_rows)),
                                                       l_col_name=list(range(plotdef_TS.nb_cols)),
                                                       kwargs_def={'do': False},
                                                       kwargs_init={0: {i_row: {'do': True} for i_row in range(plotdef_TS.nb_rows)}}
                                                       )

        # Set the binning variables
        time_fact = TS_kwargs.get('time_fact', 1.)
        time_unit = TS_kwargs.get('time_unit', 'days')

        npt_default = TS_kwargs.get('npt_model', 1000)
        extra_dt_model = TS_kwargs.get("extra_dt_model", 0.)

        ##############################################
        # Set the arguments for the plotting functions
        ##############################################
        # (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
        #  ) = get_pl_kwargs(pl_kwargs=TS_kwargs.get('pl_kwargs', None), dico_nb_dstperinsts=dico_load['dico_nb_dstperinsts'], datasetnames=datasetnames,
        #                    bin_size=exptime_bin, one_binning_per_row=one_binning_per_row, nb_rows=nb_rows)


        #######################################################################
        # Make the data, models and residuals plots (full and zoomed if needed)
        #######################################################################
        rms_values = OrderedDict()
        show_title = TS_kwargs.get("show_title", True)
        for i_row in range(plotdef_TS.nb_rows):
            for i_col in range(plotdef_TS.nb_cols):

                logger.debug(f"Doing TS plot for row {i_row}/{plotdef_TS.nb_rows}, column {i_col}/{plotdef_TS.nb_cols}")
                # gs_ts_i = gs_ts_row[i_col]
                gs_ts_i = gs_ts[i_row, i_col]

                # Create the data and residuals axes and set properties ans style
                (axe_data, axe_resi) = et.add_twoaxeswithsharex(gs_ts_i, fig, gs_from_sps_kw=create_axes_kwargs['add_twoaxeswithsharex_TS'])  # gs_from_sps_kw={"wspace": 0.1}

                if show_title and (i_row == 0):
                    axe_data.set_title(f"{inst_cat} time series", fontsize=fontsize)
                axe_resi.set_xlabel(f"time [{time_unit}]", fontsize=fontsize)
                if i_col == 0:
                    ylabel_data = f"{y_name} [{unit}]" if unit is not None else f"{y_name}"
                    ylabel_resi = f"O - C [{unit}]" if unit is not None else "O - C"
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

                #########################################
                # Plot the models specified in plotdef_TS
                #########################################
                for name_model2plot_i, model2plot_i in plotdef_TS.get_models2plot(i_row=i_row, i_col=i_col).items():
                    logger.info(f"Start Plotting model {name_model2plot_i}")
                    times_model2plot_i = model2plot_i.get_times(post_instance=post_instance, npt_default=npt_default, extra_dt=extra_dt_model)
                    # Compute the model
                    model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                            compute_raw_models_func=compute_raw_models_func, 
                                                            expression=model2plot_i.expression, times=times_model2plot_i, datasetname=model2plot_i.datasetname,
                                                            exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                            computedmodels_db=computedmodels_db, 
                                                            get_key_compute_model_func=get_key_compute_model,
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

                #####################################################
                # Plot the data and residuals specified in plotdef_TS
                #####################################################
                dico_data = {}  # Will be used for ylims and y outliers indication 
                dico_resi = {}  # Will be used for ylims and y outliers indication
                dico_times = {}  # Will be used for y outliers indication
                pl_kwarg_to_use = {}  # Will be used for y outliers indication
                for name_data2plot_i, data2plot_i in plotdef_TS.get_datas2plot(i_row=i_row, i_col=i_col).items():    
                    logger.info(f"Start Plotting data {name_data2plot_i}")
                    times_dataset = data2plot_i.get_times_dataset(post_instance=post_instance)
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
                    # Bin the residuals if needed
                    if data2plot_i.exptime > 0:
                        (bins_i, _, bindata_i, bindata_std_i, bindata_std_jitter_i
                         ) = compute_binning(times_dataset=times_dataset, values=data_i, errors=data_err_i, errors_jitter=data_err_jitter_i, exptime=data2plot_i.exptime, method=data2plot_i.method)
                        (_, _, binresi_i, _, _
                         ) = compute_binning(times_dataset=times_dataset, values=residuals_i, errors=data_err_i, errors_jitter=data_err_jitter_i, exptime=data2plot_i.exptime, method=data2plot_i.method)
                        midbins_i = bins_i[:-1] + data2plot_i.exptime / 2
                    # Compute the rms of the residuals
                    if data2plot_i.exptime > 0:
                        rms_values[name_data2plot_i] = std(binresi_i)
                    else:
                        rms_values[name_data2plot_i] = std(residuals_i)
                    logger.info(f"RMS {name_data2plot_i} = {rms_values[name_data2plot_i] * amplitude_fact} {unit} (raw cadence)")
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
                    if not(show_error) or (data_err_i is None):
                        ebcont = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i] * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                        ebcont = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], **pl_kwarg_to_use[name_data2plot_i])
                        color = ebcont[0].get_color()
                        alpha = ebcont[0].get_alpha()
                    else:
                        ebcont = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                        ebcont = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                        color = ebcont[0].get_color()
                        alpha = ebcont[0].get_alpha()
                    if "color" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["color"] = color
                    if "alpha" not in pl_kwarg_to_use[name_data2plot_i]:
                        pl_kwarg_to_use[name_data2plot_i]["alpha"] = alpha
                    if pl_kwarg_to_use[name_data2plot_i]["alpha"] is None:
                        pl_kwarg_to_use[name_data2plot_i]["alpha"] = 1
                    if data_err_jitter_plot_i is not None:
                        pl_kwarg_to_use[name_data2plot_i]["alpha"] /= 3
                        if 'label' in pl_kwarg_to_use[name_data2plot_i]:
                            label = pl_kwarg_to_use[name_data2plot_i].pop('label')
                        _ = axe_data.errorbar(dico_times[name_data2plot_i], y=dico_data[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                        _ = axe_resi.errorbar(dico_times[name_data2plot_i], y=dico_resi[name_data2plot_i], yerr=data_err_jitter_plot_i * amplitude_fact, **pl_kwarg_to_use[name_data2plot_i])
                        pl_kwarg_to_use[name_data2plot_i]["alpha"] *= 3 
                    
                for name_multidata2plot_i, multidata2plot_i in plotdef_TS.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                    raise NotImplementedError("Plotting of MultiData2Plot is not implemented yet")
                
                for name_multimodel2plot_i, multimodel2plot_i in plotdef_TS.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                    raise NotImplementedError("Plotting of MultiModel2Plot is not implemented yet")

                ###################################
                # Set ylims and indicate_y_outliers
                ###################################
                logger.debug(f"Setting ylims and indicating outliers for row {i_row}, column {i_col}")
                # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
                for axe, data_or_resi, points, in zip((axe_data, axe_resi),
                                                      ("data", "resi"),
                                                      (dico_data, dico_resi),
                                                      ):
                    # Set the y axis limits
                    if data_or_resi == "data":
                        y_lims_i = plotdef_TS.get_axis_ylims_data(i_row=i_row, i_col=i_col)
                    else:
                        y_lims_i = plotdef_TS.get_axis_ylims_resi(i_row=i_row, i_col=i_col)
                    if all([y_lims_i[jj] is None for jj in range(2)]) and (pad[data_or_resi] is not None):
                        points_pl_i = concatenate([points[name_data2plot_i] for name_data2plot_i in plotdef_TS.get_datas2plot(i_row=i_row, i_col=i_col)])
                        et.auto_y_lims(points_pl_i, axe, pad=pad[data_or_resi])
                    else:
                        axe.set_ylim(y_lims_i)

                    # Indicate outlier values that are off y-axis with an arrows for raw cadence
                    if indicate_y_outliers[data_or_resi]:
                        for name_data2plot_i, data2plot_i in plotdef_TS.get_datas2plot(i_row=i_row, i_col=i_col).items():
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
                # Set the x axis limits
                # if TS_kwargs.get('force_tlims', False):
                axe_data.set_xlim(plotdef_TS.get_axis_xlims(i_row=i_row, i_col=i_col))
                # else:
                #     x_row = concatenate([dico_times[name_data2plot_i] for name_data2plot_i in plotdef_TS.get_datas2plot(i_row=i_row, i_col=i_col).keys()])
                #     axe_data.set_xlim((min(x_row), max(x_row)))
                logger.debug(f"Done: Set xlims for row {i_row}, column {i_col}")
                ##########################
                # Set the legend if needed
                ##########################
                set_legend(ax=axe_data, legend_kwargs=legend_kwargs[i_col][i_row], fontsize_def=fontsize)
        logger.debug("Done: TS plot")

    ######################################
    # Generalized Lomb-Scargle Periodogram
    ######################################
    if do_GLSP:
        logger.debug("Doing GLSP plot")

        for i_row in range(plotdef_GLSP.nb_rows):
            for i_col in range(plotdef_TS.nb_cols):
                pass
        # # Variable that are always available
        # all_time = concatenate([dico_load['times'][dst] for dst in datasetnames])
        # idx_sort = argsort(all_time)
        # all_time = all_time[idx_sort]
        # all_data = concatenate([dico_load['datas'][dst] for dst in datasetnames])[idx_sort]
        # if GLSP_kwargs.get("use_jitter", True):
        #     all_data_err = concatenate([dico_load['data_err_jitters'][dst] for dst in datasetnames])[idx_sort]
        # else:
        #     all_data_err = concatenate([dico_load['data_errs'][dst] for dst in datasetnames])[idx_sort]
        # all_model = concatenate([dico_load['models'][dst]['model'] for dst in datasetnames])[idx_sort]
        # all_resi = concatenate([dico_load['residuals'][dst] for dst in datasetnames])[idx_sort]
        # gls_inputs = {"data": {"time": all_time, "data": all_data, "err": all_data_err, 'label': "data"},
        #             "model": {"time": all_time, "data": all_model, "err": all_data_err, 'label': "model"},  # sqrt(gp_pred_var_GLS)
        #             "resi": {"time": all_time, "data": all_resi, "err": all_data_err, 'label': "residuals"},
        #             }
        # l_l_WF_key_model = [["data", "model", "resi"], ]
        # l_gls_key = ["data", "model"]
        # # Add component from the show model dict
        # l_extra_key = [key_model for key_model in show_dict if show_dict[key_model]]
        # if "model" in l_extra_key:
        #     l_extra_key.remove("model")
        # for key_model in l_extra_key:
        #     model_time = []
        #     model_value = []
        #     model_value_err = []
        #     for dst in datasetnames:
        #         if key_model in dico_load['models'][dst]:
        #             # Then the model exist for this dataset
        #             model_value.append(dico_load['models'][dst][key_model])
        #             model_time.append(dico_load['times'][dst])
        #             if GLSP_kwargs.get("use_jitter", True):
        #                 model_value_err.append(dico_load['data_err_jitters'][dst])
        #             else:
        #                 model_value_err.append(dico_load['data_errs'][dst])
        #     if len(model_value) > 0:
        #         gls_inputs[key_model] = {}
        #         gls_inputs[key_model]["time"] = concatenate(model_time)
        #         idx_sort = argsort(gls_inputs[key_model]["time"])
        #         gls_inputs[key_model]["time"] = gls_inputs[key_model]["time"][idx_sort]
        #         gls_inputs[key_model]["data"] = concatenate(model_value)[idx_sort]
        #         gls_inputs[key_model]["err"] = concatenate(model_value_err)[idx_sort]
        #         gls_inputs[key_model]["label"] = key_model
        #         for i_WF, l_WF_key_model in enumerate(l_l_WF_key_model):
        #             if (gls_inputs[key_model]["time"] == gls_inputs[l_WF_key_model[0]]["time"]).all():
        #                 l_WF_key_model.append(key_model)
        #                 found_times_axis = True
        #                 break
        #             else:
        #                 found_times_axis = False
        #         if not(found_times_axis):
        #             l_l_WF_key_model.append([key_model, ])
        #         l_gls_key.append(key_model)
                
        # # Add the residuals
        # l_gls_key.append("resi")

        # # model_GLS, _, gp_pred_GLS, gp_pred_var_GLS = post_instance.compute_model(tsim=all_time, dataset_name=l_datasetname_RVrefglobal[0],
        # #                                                                          param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
        # #                                                                          key_obj=key_whole, datasim_kwargs=datasim_kwargs, include_gp=True)
        # # model_GLS *= RV_fact
        # # if gp_pred_GLS is not None:
        # #     gp_pred_GLS *= RV_fact
        # #     gp_pred_var_GLS *= RV_fact**2
        # # if model_wGP is not None:  # WARNING: This assumes that all datasets have (or don't have) GP
        # #     gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
        # #                   "model": {"data": model_GLS, "err": sqrt(gp_pred_var_GLS), 'label': "model"},  # sqrt(gp_pred_var_GLS)
        # #                   "GP": {"data": gp_pred_GLS, "err": sqrt(gp_pred_var_GLS), 'label': "GP"},
        # #                   "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
        # #                   }
        # #     l_gls_key = ["data", "model", "GP", "resi"]
        # # else:
        # #     gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
        # #                   "model": {"data": model_GLS, "err": all_rv_data_err, 'label': "model"},  # sqrt(gp_pred_var_GLS)
        # #                   "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
        # #                   }
        # #     l_gls_key = ["data", "model", "resi"]

        # ###############################
        # # Compute the GLSPs
        # ###############################
        # Pbeg, Pend = GLSP_kwargs.get("period_range", (0.1, 1000))

        # glsps = {}
        # for key in l_gls_key:
        #     glsps[key] = Gls((gls_inputs[key]["time"], gls_inputs[key]["data"], gls_inputs[key]["err"]), Pbeg=Pbeg, Pend=Pend, verbose=False)

        # ###############################
        # # Create additional axe if zoom
        # ###############################
        # if GLSP_kwargs.get("freq_lims_zoom", None) is not None:
        #     gs_gls = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_gls, **TS_kwargs.get('gridspec_kwargs', {}))  # , wspace=0.2, width_ratios=(2, 1)
        #     freq_lims = [GLSP_kwargs.get("freq_lims", None), GLSP_kwargs["freq_lims_zoom"]]
        #     period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), GLSP_kwargs.get("period_no_ticklabels_zoom", [])]
        #     nb_columns = 2
        # else:
        #     gs_gls = [gs_gls, ]
        #     freq_lims = [GLSP_kwargs.get("freq_lims", None), ]
        #     period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), ]
        #     nb_columns = 1

        # ################################################
        # # Create additional axes for data, model, etc...
        # ################################################
        # show_WF = GLSP_kwargs.get("show_WF", True)
        # nb_axes = len(l_gls_key) + int(show_WF) * len(l_l_WF_key_model)
        # freq_fact = GLSP_kwargs.get("freq_fact", 1e6)
        # freq_unit = GLSP_kwargs.get("freq_unit", '$\mu$Hz')
        # logscale = GLSP_kwargs.get("logscale", False)
        # legend_param = GLSP_kwargs.get('legend_param', {})

        # for jj, (gs_gls_j, freq_lims_j, period_no_ticklabels_j) in enumerate(zip(gs_gls, freq_lims, period_no_ticklabels)):
        #     ax_gls = et.add_axeswithsharex(gs_gls_j, fig, nb_axes=nb_axes, gs_from_sps_kw=GLSP_kwargs.get("axeswithsharex_kwargs", {}))  # {"wspace": 0.2})
        #     if jj == 0:
        #         ax_gls[0].set_title("GLS Periodograms", fontsize=fontsize)
        #     if logscale:
        #         ax_gls[-1].set_xscale("log")
        #     # ax_gls[-1].set_xlabel("Period [days]", fontsize=fontsize)
        #     ax_gls[-1].set_xlabel(f"Frequency [{freq_unit}]", fontsize=fontsize)
        #     # create and set the twiny axis
        #     ax_gls_twin = []
        #     for ii, key in enumerate(l_gls_key):
        #         ax_gls_twin.append(ax_gls[ii].twiny())
        #         if logscale:
        #             ax_gls_twin[ii].set_xscale("log")
        #         ax_gls[ii].set_zorder(ax_gls_twin[ii].get_zorder() + 1)  # To make sure that the orginal axis is above the new one
        #         ax_gls[ii].patch.set_visible(False)
        #         labeltop = True if ii == 0 else False
        #         ax_gls_twin[ii].tick_params(axis="x", labeltop=labeltop, labelsize=fontsize, which="both", direction="in")
        #         ax_gls_twin[ii].tick_params(axis="x", which="major", length=4, width=1)
        #         ax_gls_twin[ii].tick_params(axis="x", which="minor", length=2, width=0.5)
        #         ax_gls[ii].tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
        #         ax_gls[ii].tick_params(axis="both", which="major", length=4, width=1)
        #         ax_gls[ii].tick_params(axis="both", which="minor", length=2, width=0.5)
        #         # ax_gls[ii].yaxis.set_label_position("right")
        #         # ax_gls[ii].yaxis.tick_right()
        #         labelleft = True if jj == 0 else False
        #         labelbottom = True if ii == (nb_axes - 1) else False
        #         ax_gls[ii].tick_params(axis="x", labelleft=labelleft, labelbottom=labelbottom, labelsize=fontsize, which="both", direction="in")
        #         ax_gls[ii].tick_params(axis="y", labelleft=labelleft, labelsize=fontsize, which="both", direction="in")
        #         ax_gls[ii].yaxis.set_minor_locator(AutoMinorLocator())
        #         ax_gls[ii].xaxis.set_minor_locator(AutoMinorLocator())

        #         # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
        #         ax_gls[ii].plot(glsps[key].freq / day2sec * freq_fact, glsps[key].power, '-', color="k", label=gls_inputs[key]["label"], linewidth=GLSP_kwargs.get("lw ", 1.))
        #         # Set ticks and tick labels
        #         if jj == 0:
        #             ax_gls[ii].set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # {gls_inputs[key]['label']}

        #         ylims = ax_gls[ii].get_ylim()
        #         xlims = ax_gls[ii].get_xlim()

        #         # Print the period axis
        #         per_min = min(1 / glsps[key].freq)
        #         freq_min = min(glsps[key].freq)
        #         per_max = max(1 / glsps[key].freq)
        #         freq_max = max(glsps[key].freq)
        #         per_xlims = [1 / (freq_lim / freq_fact * day2sec) for freq_lim in xlims]
        #         if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
        #             per_xlims[0] = per_max
        #         per_xlims = per_xlims[::-1]
        #         if not(logscale):
        #             ax_gls_twin[ii].plot([freq_min / day2sec * freq_fact, freq_max / day2sec * freq_fact],
        #                                 [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
        #         else:
        #             ax_gls_twin[ii].plot([per_min, per_max], [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
        #             xlims_per = ax_gls_twin[ii].get_xlim()
        #             ax_gls_twin[ii].set_xlim(xlims_per[::-1])
        #         if not(logscale):
        #             per_decades = [10**(exp) for exp in list(range(int(floor(log10(per_min))), int(ceil(log10(per_max))) + 1))]
        #             per_ticks_major = []
        #             per_ticklabels_major = []
        #             per_ticks_minor = []
        #             for dec in per_decades:
        #                 for fact in range(1, 10):
        #                     tick = dec * fact
        #                     if (tick > per_xlims[0]) and (tick < per_xlims[1]):
        #                         if fact == 1:
        #                             per_ticks_major.append(tick)
        #                             if tick in period_no_ticklabels_j:
        #                                 per_ticklabels_major.append("")
        #                             else:
        #                                 per_ticklabels_major.append(tick)
        #                         else:
        #                             per_ticks_minor.append(tick)
        #             # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
        #             ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_major])
        #             if GLSP_kwargs.get('scientific_notation_P_axis', True):
        #                 ax_gls_twin[ii].set_xticklabels([fmt_sci_not(tick) if tick != "" else "" for tick in per_ticklabels_major])
        #             else:
        #                 ax_gls_twin[ii].set_xticklabels(per_ticklabels_major)
        #             # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
        #             ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_minor], minor=True)

        #         if freq_lims_j is None:
        #             ax_gls[ii].set_xlim(xlims)
        #             if logscale:
        #                 ax_gls_twin[ii].set_xlim(xlims_per[::-1])
        #             else:
        #                 ax_gls_twin[ii].set_xlim(xlims)
        #         else:
        #             ax_gls[ii].set_xlim(freq_lims_j)
        #             if logscale:
        #                 ax_gls_twin[ii].set_xlim([1 / (freq / freq_fact * day2sec) for freq in freq_lims_j])
        #             else:
        #                 ax_gls_twin[ii].set_xlim(freq_lims_j)

        #         ylims = ax_gls[ii].get_ylim()
        #         xlims = ax_gls[ii].get_xlim()

        #         #####################################
        #         # Vertical lines at specified periods
        #         #####################################
        #         for per, dico_per in GLSP_kwargs.get('periods', {}).items():
        #             vlines_kwargs = dico_per.get("vlines_kwargs", {})
        #             if 'label' not in vlines_kwargs:
        #                 vlines_kwargs['label'] = str(format_float_positional(per, precision=3, unique=False, fractional=False, trim='k'))
        #             freq_4_per = 1 / per / day2sec * freq_fact
        #             lines_per = ax_gls[ii].vlines(freq_4_per, *ylims, **vlines_kwargs)
        #         ax_gls[ii].set_ylim(ylims)

        #         ##########################################
        #         # Horizontal lines at specified FAP levels
        #         ##########################################
        #         ylims = ax_gls[ii].get_ylim()
        #         xlims = ax_gls[ii].get_xlim()

        #         default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
        #                             1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
        #                             10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
        #         for fap_lvl, dico_fap in GLSP_kwargs.get('fap', default_fap_dict).items():
        #             pow_ii = glsps[key].powerLevel(fap_lvl / 100)
        #             hlines_kwargs = dico_fap.get("hlines_kwargs", {})
        #             if pow_ii < ylims[1]:
        #                 lines_fap = ax_gls[ii].hlines(pow_ii, *xlims, **hlines_kwargs)
        #                 text_kwargs = dico_fap.get("text_kwargs", {}).copy()
        #                 x_pos = text_kwargs.pop("x_pos", 1.05)
        #                 y_shift = text_kwargs.pop("y_shift", 0)
        #                 label = str(text_kwargs.pop("label", fr"{fap_lvl}\%"))
        #                 color = text_kwargs.pop("color", None)
        #                 if color is None:
        #                     color = lines_fap.get_color()[0]
        #                 if jj == (nb_columns - 1):
        #                     ax_gls[ii].text(xlims[0] + x_pos * (xlims[1] - xlims[0]), pow_ii + y_shift * (ylims[1] - ylims[0]),
        #                                     label, color=color, fontsize=fontsize, **text_kwargs)

        #         ax_gls[ii].set_xlim(xlims)
        #         #
        #         if jj == 0:
        #             ax_gls[ii].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get(key, {}))

        #     ax_gls_twin[0].set_xlabel("Period [days]", fontsize=fontsize)

        #     if GLSP_kwargs.get("show_WF", True):
        #         for i_WF, l_WF_key_model in enumerate(l_l_WF_key_model):
        #             ax_gls[-i_WF - 1].plot(glsps[l_WF_key_model[0]].freq / day2sec * freq_fact, glsps[l_WF_key_model[0]].wf, '-', color="k", label=f"WF {l_WF_key_model}", linewidth=GLSP_kwargs.get("lw ", 1.))
        #             if jj == 0:
        #                 ax_gls[-i_WF - 1].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get("WF", {}))
        #                 ax_gls[-i_WF - 1].set_ylabel("Relative Amplitude")
        #             labelleft = True if jj == 0 else False
        #             ax_gls[-i_WF - 1].tick_params(axis="both", labelleft=labelleft, labelsize=fontsize, right=True, which="both", direction="in")
        logger.debug("Done: GLSP plot")

    if do_TS:
        return computedmodels_db, rms_values
    else:
        return computedmodels_db, None


def create_iTSNGLSP_plots(fig, post_instance, df_fittedval,
                          compute_raw_models_func, remove_add_model_components_func,
                          kwargs_compute_model_4_key_model, 
                          y_name, inst_cat,
                          l_iterative_removal,
                          d_name_component_removed_to_print,
                          l_1_model_4_alldst,
                          models2plot: Models2plotTS|None=None,
                          compute_GP_model=True,
                          split_GP_computation=None,
                          outputs_load_datasets_and_models=None,
                          computed_models_4_iTS=None,
                          datasim_kwargs=None,
                          datasetnames=None,
                          amplitude_fact=1., unit=None,
                          create_axes_kwargs=None,
                          TS_kwargs=None,
                          GLSP_kwargs=None,
                          fontsize=AandA_fontsize,
                          get_key_compute_model_func=get_key_compute_model,
                          kwargs_get_key_compute_model=None
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
    outputs_load_datasets_and_models     : tuple[dict, dict] or None
        The outputs_load_datasets_and_models can be quite long to run especially if there are GP models involved.
        So these are outputed by the function and you can then provide them in this argument to avoid to have to redo the computation
    datasetnames  : list of String
        List providing the datasets to load and use
    create_axes_kwargs     : dict
    remove_dict   : dict
    TS_kwargs     : None or dict
            - 'do': boolean (Def: True)
            - 'row4datasetname'   : dict of int
                Dictionary saying which dataset to plot on which row. The format is:
                {"<dataset_name>": <int giving the row index starting at 0>, ...}
            - 'npt_model': int (Def: 1000) giving the number of points to use for the model
            - 'extra_dt_model': float (Def: 0)
                Specify the extra time that for which you want to compute the model before and after the
                data.
            - 'tlims': None or Iterable of 2 float (Def: None)
                Specificy the time limits for the plot
            - 'tlims_zoom': None or Iterable of 2 float (Def: None)
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
            - 'ylims_data': Define the limits on the data y axis. This override 'pad_data'
            - 'pad_data': Iterable of 2 floats (Def: (0.1, 0.1))
                Define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
            - 'ylims_resi': Define the limits on the residuals y axis. This override 'pad_resi'
            - 'pad_resi': Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
            - 'indicate_y_outliers_data': boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
            - 'indicate_y_outliers_resi': boolean. If True, residuals outliers (outside of the plot) are indicated
                by arrows.
            - 'exptime_bin' : float
                Exposure time for the binning of data in the same unit that the time of the datasets.
                If you don't want to bin put 0.
            - 'binning_stat' : str
                Statitical method used to compute the binned value. Can be "mean" or "median". This is passed to the
                statistic argument of scipy.stats.binned_statistic
            - 'one_binning_per_row' : bool
                If true only one binning per row is performed
            - 'show_title'  : bool
                If True, show the titles (of the main and the zoom)
            - 'legend_kwargs' : dict of dict
                keys are 'all' or int providing the row index ('all' applies to all row, but the row index overwrite it)
                Values are dict whose keys are:
                    'do'    : bool
                        (Default: True) Whether or not to show the legend
                    other keys are passed to the pyplot.legend function
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
    amplitude_fact       : float
        Factor to apply to the data
    unit        : str
        String giving the unit of the data

    Returns
    -------
    dico_load       : dict  
        Output of the function core_compute_load.load_datasets_and_models
    computed_models : dict
        Outputs of the compute_and_plot_model function calls
    outputs_load_datasets_and_models    : tuple[dict, dict]
    """
    logger.debug("Start create_iTSNGLSP_plots")
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")
    # Make sure that create_axes_kwargs is well defined
    create_axes_kwargs_user = create_axes_kwargs if create_axes_kwargs is not None else {}
    create_axes_kwargs = {'main_gridspec': {},
                          }
    for key in create_axes_kwargs_user:
        if key in create_axes_kwargs:
            create_axes_kwargs[key].update(create_axes_kwargs_user[key])
        else:
            raise ValueError(f"{key} is not a valid key for create_axes_kwargs, should be in ['main_gridspec', 'add_axeswithsharex']")

    # Make sure that the TS_kwargs and GLSP_kwargs are well defined
    TS_kwargs_user = TS_kwargs if create_axes_kwargs is not None else {}
    TS_kwargs = {'do': True, }
    TS_kwargs.update(TS_kwargs_user)

    GLSP_kwargs_user = GLSP_kwargs if create_axes_kwargs is not None else {}
    GLSP_kwargs = {'do': True, }
    GLSP_kwargs.update(GLSP_kwargs_user)

    ncols = int(TS_kwargs['do'])
    if GLSP_kwargs['do']:
        ncols +=1
        if GLSP_kwargs.get("freq_lims_zoom", None) is not None:
            ncols +=1

    # Create The GridSpec
    # TODO: Check l_iterative_removal 
    nb_rows_ts = 1 + len(l_iterative_removal)
    if GLSP_kwargs.get("show_WF", True):
        nb_rows_glsp = nb_rows_ts + 1
    else:
        nb_rows_glsp = nb_rows_ts
    gs = GridSpec(nrows=nb_rows_glsp, ncols=ncols, figure=fig,  **create_axes_kwargs['main_gridspec'])

    show_title = TS_kwargs.get("show_title", True)

    if TS_kwargs['do']:
        gs_ts = [gs[i_row, 0] for i_row in range(nb_rows_ts)]

    # If no dataset name is provided get all the available datasets of the provided inst_cat
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat=inst_cat, sortby_instcat=False, sortby_instname=False)

    # Load the defined datasets and check how many dataset there is by instrument.
    if outputs_load_datasets_and_models is None:
        (dico_load, kwargs_compute_model_4_key_model
         ) = load_datasets_and_models(datasetnames=datasetnames, post_instance=post_instance, datasim_kwargs=datasim_kwargs,
                                      df_fittedval=df_fittedval, amplitude_fact=amplitude_fact,
                                      compute_raw_models_func=compute_raw_models_func,
                                      remove_add_model_components_func=remove_add_model_components_func,
                                      kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                      compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                      get_key_compute_model_func=get_key_compute_model_func,
                                      kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                      )
    else:
        dico_load, kwargs_compute_model_4_key_model = outputs_load_datasets_and_models

    # Do the suptitle
    do_suptitle(fig=fig, post_instance=post_instance, datasetnames=datasetnames, fontsize=fontsize,
                dico_models=dico_load["models"], model_removed_or_add_dict=kwargs_compute_model_4_key_model["model"],
                data_remove_or_add_dict=kwargs_compute_model_4_key_model["data"], suptitle_kwargs=suptitle_kwargs
                )
            
    ###############################################
    # Preliminary checks for both TS and GLSP plots
    ###############################################
    # Get the binning variables
    show_binned_model = False
    exptime_bin = TS_kwargs.get("exptime_bin", 0.)
    if exptime_bin is None:
        exptime_bin = 0.
    if exptime_bin > 0:
        show_binned_model = True
    binning_stat = TS_kwargs.get("binning_stat", "mean")
    supersamp_bin_model = TS_kwargs.get('supersamp_bin_model', 1)

    # Set the arguments for the plotting functions
    (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
     ) = get_pl_kwargs(pl_kwargs=TS_kwargs.get('pl_kwargs', None), dico_nb_dstperinsts=dico_load['dico_nb_dstperinsts'], datasetnames=datasetnames,
                       bin_size=exptime_bin, one_binning_per_row=True, nb_rows=nb_rows_ts)

    time_unit = TS_kwargs.get('time_unit', 'days')

    update_data_binned_label(pl_kwarg=pl_kwarg_final, key_data_binned="data_binned", datasetnames=datasetnames, bin_size=exptime_bin,
                             bin_size_unit=time_unit, one_binning_per_row=True,
                             nb_rows=nb_rows_ts)

    # Make sure that legend_kwargs is well defined
    legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=TS_kwargs.get('legend_kwargs', None),
                                                   l_row_name=list(range(nb_rows_ts)),
                                                   l_col_name=list(range(1)),
                                                   kwargs_def={'do': False},
                                                   kwargs_init={0: {i_row: {'do': True} for i_row in range(nb_rows_ts)}}
                                                   )

    # Make sure the models2plot is well define
    models2plot = check_Models2plot(models2plot=models2plot, datasetnames4rowidx={i_row: datasetnames for i_row in range(models2plot.nb_rows)}, l_model_1_per_row=l_1_model_4_alldst)

    # show_dict_user = show_dict if show_dict is not None else {}
    # show_dict = {0: {"model": True, "model_wGP": True}}
    # for i_row, t_key_model in enumerate(l_iterative_removal):
    #     if i_row not in show_dict:
    #         show_dict[i_row] = {}
    #     if show_removed_in_previousrow:
    #         for key_model in t_key_model:
    #             show_dict[i_row][key_model] = True
    # show_dict[i_row + 1] = {}
    # for i_row in show_dict_user:
    #     show_dict[i_row].update(show_dict_user[i_row])

    #####################################
    # Preliminary checks for the TS plots
    #####################################
    if TS_kwargs['do']:    

        # Check some of the TS parameters
            
        # Make sure that indicate_y_outliers is well defined
        indicate_y_outliers = check_spec_data_or_resi(spec_user=TS_kwargs.get('indicate_y_outliers', None), l_type_spec=[bool], spec_def=True)

        # Make sure that pad is well defined
        pad = check_spec_data_or_resi(spec_user=TS_kwargs.get('pad', None), l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

        # check tlims
        tlims = check_spec_by_column_or_row(spec_user=TS_kwargs.get('tlims', None), l_type_spec=[tuple, list],
                                            spec_def=None, l_row_name=list(range(nb_rows_ts)))

        # Make sure that ylims is well defined
        ylims = check_spec_for_data_or_resi_by_column_or_row(spec_user=TS_kwargs.get('ylims', None),
                                                             l_row_name=list(range(nb_rows_ts)),
                                                             l_col_name=list(range(1)),
                                                             l_type_spec=[tuple, list],
                                                             spec_def={'data': None, 'resi': None}
                                                             )
        
        # Get the time fact, time unit,  npt_model, extra_dt_model
        time_fact = TS_kwargs.get('time_fact', 1.)
        npt_model = TS_kwargs.get('npt_model', 1000)
        extra_dt_model = TS_kwargs.get("extra_dt_model", 0.)

        # Init the text_rms
        text_rms = OrderedDict()

        # Compute the time (including time_fact, x_values) corresponding to each point in each dataset and the minimum and maximum of all datasets
        xlims_datas = OrderedDict()
        x_values = OrderedDict()
        for datasetname in datasetnames:
            xlims_datas[datasetname] = [inf, -inf]
            x_values[datasetname] = dico_load['times'][datasetname] * time_fact
            if min(x_values[datasetname]) < xlims_datas[datasetname][0]:
                xlims_datas[datasetname][0] = min(x_values[datasetname])
            if max(x_values[datasetname]) > xlims_datas[datasetname][1]:
                xlims_datas[datasetname][1] = max(x_values[datasetname])
        
        ########################
        # Computed models for TS
        ########################
        if computed_models_4_iTS is None:
            computed_models_4_iTS = []

        for i_row in range(nb_rows_ts):
            for i_model, model_i in enumerate(models2plot.get_model2show(row_idx=i_row)):
                datasetname4compute_and_plot_model = model_i.datasetname
                # If model_i.npt is not specified, use npt_model
                if model_i.npt is None:
                    if model_i.model == 'decorrelation_likelihood':
                        model_i.npt = len(dico_load["times"][datasetname4compute_and_plot_model])
                    else:
                        model_i.npt = npt_model
                # If model_i.tlims is not specified use the min and max time of either model_i.datasetname or all the datasets in the row depending on wither or not model_i.model in in l_model_1_per_row
                if model_i.tlims is None:
                    if model_i.model in l_1_model_4_alldst:
                        datasetnames4autotlims = datasetnames
                    else:
                        datasetnames4autotlims = [model_i.datasetname, ]
                    if model_i.model == 'decorrelation_likelihood':
                        model_i.tlims = (min([xlims_datas[dst][0] for dst in datasetnames4autotlims]) / time_fact,
                                         max([xlims_datas[dst][1] for dst in datasetnames4autotlims]) / time_fact
                                        )
                    else:
                        model_i.tlims = ((min([xlims_datas[dst][0] for dst in datasetnames4autotlims]) - extra_dt_model) / time_fact,
                                        (max([xlims_datas[dst][1] for dst in datasetnames4autotlims]) + extra_dt_model) / time_fact
                                        )
                logger.debug(f"Computing and plotting model '{model_i.model}' ({i_model}/{len(models2plot.get_model2show(row_idx=i_row))}) for (row {i_row}) for "
                             f"dataset {model_i.datasetname}.")
                # Init computed_models_4_TS for this set of datasetname and tlims
                models_4_computed_models_4_iTS = None
                for computed_models_4_iTS_i in computed_models_4_iTS:
                    if (computed_models_4_iTS_i["datasetnames"] == model_i.datasetname) and (computed_models_4_iTS_i["tlims"] == model_i.tlims) and (computed_models_4_iTS_i["npt_model"] == model_i.npt):
                        models_4_computed_models_4_iTS = computed_models_4_iTS_i['models']
                if models_4_computed_models_4_iTS is None:
                    computed_models_4_iTS.append({"datasetnames": model_i.datasetname, "tlims": model_i.tlims, 'npt_model': model_i.npt, 'models': {}})
                    models_4_computed_models_4_iTS = computed_models_4_iTS[-1]['models']
                kwargs_compute_model = kwargs_compute_model_4_key_model.get(model_i.model, {})
                show_binned_model = TS_kwargs.get('show_binned_model', {}).get(model_i.model, True)
                if model_i.pl_kwargs is not None:
                    if model_i.model not in pl_kwarg_final[datasetname4compute_and_plot_model]:
                        pl_kwarg_final[datasetname4compute_and_plot_model][model_i.model] = {}
                    pl_kwarg_final[datasetname4compute_and_plot_model][model_i.model].update(model_i.pl_kwargs)
                if model_i.model == "decorrelation_likelihood":
                    # computed_models_4_iTS[datasetname]["tsim_decorr_like"] = dico_load["times"][datasetname]
                    (models_decorr_like, _
                     ) = compute_and_plot_model(tsim=dico_load["times"][datasetname4compute_and_plot_model],
                                                key_model=model_i.model,
                                                datasetname=datasetname4compute_and_plot_model,
                                                # model2computeNplot=model_i,
                                                time_fact=time_fact,
                                                post_instance=post_instance,
                                                df_fittedval=df_fittedval,
                                                datasim_kwargs=datasim_kwargs,
                                                amplitude_fact=amplitude_fact,
                                                compute_raw_models_func=compute_raw_models_func,
                                                remove_add_model_components_func=remove_add_model_components_func,
                                                key_pl_kwarg=model_i.model,
                                                remove_dict=kwargs_compute_model.get('remove_dict', {}),
                                                add_dict=kwargs_compute_model.get('add_dict', {}),
                                                compute_only_raw_models=False,
                                                compute_GP_model=compute_GP_model,
                                                split_GP_computation=split_GP_computation,
                                                compute_binned=False,
                                                exptime_bin=None,
                                                supersamp_bin_model=None,
                                                fact_tsim_to_xsim=time_fact,
                                                xsim=None, time_unit=None,
                                                plot_unbinned=False, plot_binned=False, ax=None,
                                                pl_kwarg=None,
                                                models=None,
                                                get_key_compute_model_func=get_key_compute_model_func,
                                                kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                )
                    model2plotNcompute_decorr_like = models_decorr_like[model_i.model]
                    tsim_decorr, model_values_decorr, model_values_err_decorr = model2plotNcompute_decorr_like.get_computed_model(exptime_bin=0, supersamp=1)
                    model_i.set_computed_model(times=tsim_decorr, values=model_values_decorr, values_err=model_values_err_decorr, exptime_bin=0, supersamp=1)
                    # computed_models_4_iTS[datasetname][model_i.model] = models_decorr_like[model_i.model]
                else:
                    # if datasetname4model4row[model][i_row] == 'all':
                    #     tsim = computed_models_4_iTS[datasetname]["tsim"]
                    #     models_compute_and_plot_model = computed_models_4_iTS[datasetname]
                    # else:
                    #     tsim = computed_models_4_iTS["tsim_all"]
                    #     if "all" not in computed_models_4_iTS[datasetname]:
                    #         computed_models_4_iTS[datasetname]['all'] = {}
                    #     models_compute_and_plot_model = computed_models_4_iTS[datasetname]['all']
                    (models_4_computed_models_4_iTS, _
                     ) = compute_and_plot_model(tsim=linspace(model_i.tlims[0] / time_fact, model_i.tlims[1] / time_fact, model_i.npt, endpoint=True),
                                                key_model=model_i.model,
                                                datasetname=datasetname4compute_and_plot_model,
                                                model2computeNplot=model_i,
                                                time_fact=time_fact,
                                                post_instance=post_instance,
                                                df_fittedval=df_fittedval,
                                                datasim_kwargs=datasim_kwargs,
                                                amplitude_fact=amplitude_fact,
                                                compute_raw_models_func=compute_raw_models_func,
                                                remove_add_model_components_func=remove_add_model_components_func,
                                                key_pl_kwarg=model_i.model,
                                                remove_dict=kwargs_compute_model.get('remove_dict', {}),
                                                add_dict=kwargs_compute_model.get('add_dict', {}),
                                                compute_only_raw_models=False,
                                                compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                                compute_binned=show_binned_model,
                                                exptime_bin=exptime_bin,
                                                supersamp_bin_model=supersamp_bin_model,
                                                fact_tsim_to_xsim=time_fact,
                                                xsim=None, time_unit=time_unit,
                                                plot_unbinned=False, plot_binned=False,
                                                ax=None,
                                                pl_kwarg=None,
                                                models=models_4_computed_models_4_iTS,
                                                get_key_compute_model_func=get_key_compute_model_func,
                                                kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                )
                logger.debug(f"Done: Compute and plot model {model_i.model} ({i_model}/{len(models2plot.get_model2show(row_idx=i_row))}) for (row {i_row}) for dataset {model_i.datasetname}")
        # Define on which rows the datasets are plots using the row4datasetname input
        # if datasetname4model is not None:
        #     datasetname4model4row = {key_model: {0: dst_name} for key_model, dst_name in datasetname4model.items()}
        # else:
        #     datasetname4model4row = None
        # datasetname4model4row = check_datasetname4model4row(datasetname4model4row=datasetname4model4row,
        #                                                     datasetnames4rowidx=[datasetnames for ii in range(nb_rows_ts)],
        #                                                     l_model_4_rowidx=[list(show_dict_i.keys()) for ii, show_dict_i in show_dict.items()], 
        #                                                     l_model_1_per_row=l_1_model_4_alldst,
        #                                                     )
        # datasetname4model = {key_model: dico_datasetname4row[0] for key_model, dico_datasetname4row in datasetname4model4row.items()}
        # xlims_all = [min([xlims_datas[dst][0] for dst in datasetnames]) - extra_dt_model,
        #              max([xlims_datas[dst][1] for dst in datasetnames]) + extra_dt_model
        #              ]
        # tlims_all = (xlims_all[0] / time_fact, xlims_all[1] / time_fact)
        # computed_models_4_iTS["tsim_all"] = linspace(*tlims_all, npt_model)
        # computed_models_4_iTS["xsim_all"] = computed_models_4_iTS["tsim_all"] * time_fact

        # for datasetname in datasetnames:
        #     # Init computed_models_4_iTS for this dataset
        #     if datasetname not in computed_models_4_iTS:
        #         computed_models_4_iTS[datasetname] = {}

        #     xlims_dataset = [xlims_datas[datasetname][0] - extra_dt_model, xlims_datas[datasetname][1] + extra_dt_model]
        #     tlims_dataset = (xlims_all[0] / time_fact, xlims_all[1] / time_fact)
        #     computed_models_4_iTS[datasetname]["tsim"] = linspace(*tlims_dataset, npt_model)
        #     computed_models_4_iTS[datasetname]["xsim"] = computed_models_4_iTS[datasetname]["tsim"] * time_fact

        #     for i_row in range(nb_rows_ts):                    
        #         for model, show_model in show_dict[i_row].items():
        #             if show_model and ((datasetname4model4row[model][i_row] == datasetname) or (datasetname4model4row[model][i_row] == 'all')) and (model not in computed_models_4_iTS[datasetname]):
        #                 logger.debug(f"Computing model {model} for dataset {datasetname}")
        #                 kwargs_compute_model = kwargs_compute_model_4_key_model.get(model, {})
        #                 if model == "decorrelation_likelihood":
        #                     computed_models_4_iTS[datasetname]["tsim_decorr_like"] = dico_load["times"][datasetname]
        #                     (models_decorr_like, _
        #                     ) = compute_and_plot_model(tsim=dico_load["times"][datasetname],
        #                                                key_model=model,
        #                                                datasetname=datasetname,
        #                                                post_instance=post_instance,
        #                                                df_fittedval=df_fittedval,
        #                                                datasim_kwargs=datasim_kwargs,
        #                                                amplitude_fact=amplitude_fact,
        #                                                compute_raw_models_func=compute_raw_models_func,
        #                                                remove_add_model_components_func=remove_add_model_components_func,
        #                                                key_pl_kwarg=model,
        #                                                remove_dict=kwargs_compute_model.get('remove_dict', {}),
        #                                                add_dict=kwargs_compute_model.get('add_dict', {}),
        #                                                compute_only_raw_models=False,
        #                                                compute_GP_model=compute_GP_model,
        #                                                split_GP_computation=split_GP_computation,
        #                                                compute_binned=False,
        #                                                exptime_bin=None,
        #                                                supersamp_bin_model=None,
        #                                                fact_tsim_to_xsim=time_fact,
        #                                                xsim=None, time_unit=None,
        #                                                plot_unbinned=False, plot_binned=False, ax=None,
        #                                                pl_kwarg=None,
        #                                                models=None,
        #                                                get_key_compute_model_func=get_key_compute_model_func,
        #                                                kwargs_get_key_compute_model=kwargs_get_key_compute_model,
        #                                                )
        #                     computed_models_4_iTS[datasetname][model] = models_decorr_like[model]
        #                 else:
        #                     if datasetname4model4row[model][i_row] == 'all':
        #                         tsim = computed_models_4_iTS[datasetname]["tsim"]
        #                         models_compute_and_plot_model = computed_models_4_iTS[datasetname]
        #                     else:
        #                         tsim = computed_models_4_iTS["tsim_all"]
        #                         if "all" not in computed_models_4_iTS[datasetname]:
        #                             computed_models_4_iTS[datasetname]['all'] = {}
        #                         models_compute_and_plot_model = computed_models_4_iTS[datasetname]['all']
        #                     (models_compute_and_plot_model, _
        #                      ) = compute_and_plot_model(tsim=tsim,
        #                                                 key_model=model,
        #                                                 datasetname=datasetname,
        #                                                 post_instance=post_instance,
        #                                                 df_fittedval=df_fittedval,
        #                                                 datasim_kwargs=datasim_kwargs,
        #                                                 amplitude_fact=amplitude_fact,
        #                                                 compute_raw_models_func=compute_raw_models_func,
        #                                                 remove_add_model_components_func=remove_add_model_components_func,
        #                                                 key_pl_kwarg=model,
        #                                                 remove_dict=kwargs_compute_model.get('remove_dict', {}),
        #                                                 add_dict=kwargs_compute_model.get('add_dict', {}),
        #                                                 compute_only_raw_models=False,
        #                                                 compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
        #                                                 compute_binned=show_binned_model,
        #                                                 exptime_bin=exptime_bin,
        #                                                 supersamp_bin_model=supersamp_bin_model,
        #                                                 fact_tsim_to_xsim=time_fact,
        #                                                 xsim=None, time_unit=time_unit,
        #                                                 plot_unbinned=False, plot_binned=False,
        #                                                 ax=None,
        #                                                 pl_kwarg=None,
        #                                                 models=models_compute_and_plot_model,
        #                                                 get_key_compute_model_func=get_key_compute_model_func,
        #                                                 kwargs_get_key_compute_model=kwargs_get_key_compute_model,
        #                                                 )
        #                 logger.debug(f"Done: Compute and plot model {model} for dataset {datasetname}")

    #######################################
    # Preliminary checks for the GLSP plots
    #######################################
    if GLSP_kwargs['do']:

        # Define Pbeg and Pend for the glsp computation
        Pbeg, Pend = GLSP_kwargs.get("period_range", (0.1, 1000))

        ###############################
        # Create additional axe if zoom
        ###############################
        if GLSP_kwargs.get("freq_lims_zoom", None) is not None:
            nb_cols_gls = 2
            if TS_kwargs['do']:
                gs_gls = [[gs[i_row, 1] for i_row in range(nb_rows_glsp)], [gs[i_row, 2] for i_row in range(nb_rows_glsp)]]
            else:
                gs_gls = [[gs[i_row, 0] for i_row in range(nb_rows_glsp)], [gs[i_row, 1] for i_row in range(nb_rows_glsp)]]
            freq_lims = [GLSP_kwargs.get("freq_lims", None), GLSP_kwargs["freq_lims_zoom"]]
            period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), GLSP_kwargs.get("period_no_ticklabels_zoom", [])]
        else:
            if TS_kwargs['do']:
                gs_gls = [[gs[i_row, 1] for i_row in range(nb_rows_glsp)], ]
            else:
                gs_gls = [[gs[i_row, 0] for i_row in range(nb_rows_glsp)], ]
            freq_lims = [GLSP_kwargs.get("freq_lims", None), ]
            period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), ]
            nb_cols_gls = 1

        ################################################
        # Create additional axes for data, model, etc...
        ################################################
        show_WF = GLSP_kwargs.get("show_WF", True)
        freq_fact = GLSP_kwargs.get("freq_fact", 1e6)
        freq_unit = GLSP_kwargs.get("freq_unit", '$\mu$Hz')
        logscale = GLSP_kwargs.get("logscale", False)
        legend_param = GLSP_kwargs.get('legend_param', {})
        
    ################
    # Iterative loop
    ################
    datas = {}
    models = {}
    text_rms = {}
    text_rms_binned = {}

    for i_row in range(1 + len(l_iterative_removal)):

        # Set l_model_2_remove and l_model_2_remove_nextrow
        if i_row == 0:
            l_model_2_remove = []
            l_model_2_remove_nextrow = l_iterative_removal[i_row]
        elif i_row == len(l_iterative_removal):
            l_model_2_remove = l_iterative_removal[i_row - 1]
            l_model_2_remove_nextrow = []
        else:
            l_model_2_remove = l_iterative_removal[i_row - 1]
            l_model_2_remove_nextrow = l_iterative_removal[i_row]

        ##################
        # Compute the data
        ##################
        for datasetname in datasetnames:
            logger.info(f"Computing the data for row {i_row}.")
            if i_row == 0:
                datas[datasetname] = copy(dico_load['datas'][datasetname])
                data_label = f"{inst_cat} data"
            logger.info(f"Model components to remove from the data in row {i_row} = {l_model_2_remove}.")
            logger.info(f"Model components to visualise in row {i_row} = {[model_i.model for model_i in models2plot.get_model2show(row_idx=i_row)]}.")
            for key_model in list(l_model_2_remove) + list(set([model_i.model for model_i in models2plot.get_model2show(row_idx=i_row)])):
                if key_model in dico_load:
                    model_component = dico_load[key_model][datasetname]
                elif (datasetname in models) and (key_model in models[datasetname]):
                    model_component = models[datasetname][key_model]
                else:
                    kwargs_compute_model = kwargs_compute_model_4_key_model.get(key_model, {})
                    (models[datasetname], _
                        ) = compute_and_plot_model(tsim=dico_load["times"][datasetname],
                                                   key_model=key_model,
                                                   datasetname=datasetname,
                                                   post_instance=post_instance,
                                                   df_fittedval=df_fittedval,
                                                   datasim_kwargs=datasim_kwargs,
                                                   amplitude_fact=amplitude_fact,
                                                   compute_raw_models_func=compute_raw_models_func,
                                                   remove_add_model_components_func=remove_add_model_components_func,
                                                   key_pl_kwarg=key_model,
                                                   remove_dict=kwargs_compute_model.get('remove_dict', {}),
                                                   add_dict=kwargs_compute_model.get('add_dict', {}),
                                                   compute_only_raw_models=False,
                                                   compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                                   compute_binned=False,
                                                   exptime_bin=exptime_bin,
                                                   supersamp_bin_model=supersamp_bin_model,
                                                   fact_tsim_to_xsim=time_fact,
                                                   xsim=None, time_unit=time_unit,
                                                   plot_unbinned=False, plot_binned=False,
                                                   ax=None,
                                                   pl_kwarg=None,
                                                   models=models.get(datasetname, {}),
                                                   get_key_compute_model_func=get_key_compute_model_func,
                                                   kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                   )
                    model_component = models[datasetname][key_model]
                if key_model in l_model_2_remove:
                    datas[datasetname] -= model_component.get_computed_model(exptime_bin=exptime_bin, supersamp=supersamp_bin_model)[1]
                    ext_data_label = f" - {key_model}" 
                    if ext_data_label not in data_label:
                        data_label += ext_data_label
                    logger.info(f"Row {i_row}: Model component {key_model} removed.")
        
        # Compute rms
        tlims_i = tlims.get(i_row, tlims['all'])
        x_row = concatenate([x_values[dst] for dst in datasetnames])
        x_min_data, x_max_data = (min(x_row), max(x_row))
        x_min_rms = x_min_data
        if tlims_i is not None and tlims_i[0] is not None:
            x_min_rms = tlims_i[0]
        x_max_rms = x_max_data
        if tlims_i is not None and tlims_i[1] is not None:
            x_max_rms = tlims_i[1]
        text_rms_template = f"{{:{rms_kwargs['format']}}}"
        text_rms[i_row] = text_rms_template.format(std(concatenate([datas[dst][logical_and(x_values[dst] >= x_min_rms, x_values[dst] <= x_max_rms)] for dst in datasetnames])))
        print(f"RMS row {i_row} = {text_rms[i_row]} {unit} (raw cadence)")

        #############
        # TIME SERIES
        #############
        if TS_kwargs['do']:
            logger.debug(f"Doing TS plot for row {i_row}/{nb_rows_ts}")

            # Create the updated grid space according to the number of rows
            gs_ts_i = gs_ts[i_row]

            if i_row == 0:
                kwargs_add_suplot = {}
            else:
                kwargs_add_suplot = {'sharex': ax_ts_i}
            ax_ts_i = fig.add_subplot(gs_ts_i, **kwargs_add_suplot)

            if show_title and (i_row == 0):
                title = f"{inst_cat} time series\n"
            else:
                title = ""
            title += data_label
            ax_ts_i.set_title(title, fontsize=fontsize)
                                                                      
            # Make the data, models plots                
            tlims_i = tlims.get(i_row, tlims['all'])
            if i_row == (nb_rows_ts - 1):
                ax_ts_i.set_xlabel(f"time [{time_unit}]", fontsize=fontsize)
            ylabel = f"{y_name} [{unit}]" if unit is not None else f"{y_name}"
            ax_ts_i.set_ylabel(ylabel, fontsize=fontsize)
            labelbottom = True if i_row == (nb_rows_ts - 1) else False
            ax_ts_i.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=labelbottom, labelsize=fontsize)
            ax_ts_i.xaxis.set_minor_locator(AutoMinorLocator())
            ax_ts_i.yaxis.set_minor_locator(AutoMinorLocator())
            ax_ts_i.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            ax_ts_i.grid(axis="y", color="black", alpha=.5, linewidth=.5)

            ###############
            # Plot the data
            ###############
            for datasetname in datasetnames:

                # Plot the raw data
                logger.debug(f"Plotting data for dataset {datasetname} (row {i_row})")
                if pl_show_error[datasetname]['data']:
                    ebcont = ax_ts_i.errorbar(x_values[datasetname], y=datas[datasetname],
                                              yerr=dico_load['data_errs'][datasetname], **pl_kwarg_final[datasetname]["data"])  # Plot the data point and error bars without jitter
                    if not("ecolor" in pl_kwarg_jitter[datasetname]):
                        pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
                    if not("color" in pl_kwarg_final[datasetname]):
                        pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
                    if dico_load['has_jitters'][datasetname]:
                        ax_ts_i.errorbar(x_values[datasetname], y=dico_load['datas'][datasetname],
                                         yerr=dico_load['data_err_jitters'][datasetname], **pl_kwarg_jitter[datasetname]["data"])  # Plot the error bars with jitter
                else:
                    ax_ts_i.errorbar(x_values[datasetname], y=dico_load['datas'][datasetname], **pl_kwarg_final[datasetname]["data"])  # Plot the data point and error bars without jitter
                logger.debug(f"Done: Plot data for dataset {datasetname} (row {i_row})")

            # Plot the binned data if necessary
            if exptime_bin > 0:
                logger.debug(f"Plotting binned data for row {i_row}")
                x_row = concatenate([x_values[dst] for dst in datasetnames])
                x_min_data, x_max_data = (min(x_row), max(x_row))
                bins = arange(x_min_data, x_max_data + exptime_bin, exptime_bin)
                midbins = bins[:-1] + exptime_bin / 2
                nbins = len(bins) - 1
                # Compute the binned values
                (bindata, binedges, binnb
                ) = binned_statistic(x_row, concatenate([datas[dst] for dst in datasetnames]),
                                    statistic=binning_stat, bins=bins,
                                    range=(x_min_data, x_max_data))
                # Compute the err on the binned values
                binstd = zeros(nbins)
                if any([dico_load['has_jitters'][dst] for dst in datasetnames]):
                    binstd_jitter = zeros(nbins)
                bincount = zeros(nbins)
                data_err_row = concatenate([dico_load['data_errs'][dst] for dst in datasetnames])
                data_err_jitter_row = concatenate([dico_load['data_err_jitters'][dst] if dico_load['has_jitters'][dst] else ones_like(dico_load['data_errs'][dst]) * nan for dst in datasetnames])
                for i_bin in range(nbins):
                    bincount[i_bin] = len(where(binnb == (i_bin + 1))[0])
                    if bincount[i_bin] > 0.0:
                        binstd[i_bin] = sqrt(sum(power(data_err_row[binnb == (i_bin + 1)], 2.)) /
                                            bincount[i_bin]**2
                                            )
                        if any([dico_load['has_jitters'][dst] for dst in datasetnames]):
                            binstd_jitter[i_bin] = sqrt(sum(power(data_err_jitter_row[binnb == (i_bin + 1)],
                                                                2.
                                                                )
                                                            ) /
                                                        bincount[i_bin]**2
                                                        )
                    else:
                        binstd[i_bin] = nan
                        if any([dico_load['has_jitters'][dst] for dst in datasetnames]):
                            binstd_jitter[i_bin] = nan
                # Plot the binned data
                bin_err = binstd if pl_show_error[f"row{i_row}"] else None
                ebcont_binned = ax_ts_i.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"])
                if not("color" in pl_kwarg_final[f"row{i_row}"]):
                    pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
                if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
                    pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
                if any([dico_load['has_jitters'][dst] for dst in datasetnames]) and pl_show_error[f"row{i_row}"]:
                    _ = ax_ts_i.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"])
                
                # Compute rms of the binned data
                x_min_rms = x_min_data
                if tlims_i is not None and tlims_i[0] is not None:
                    x_min_rms = tlims_i[0]
                x_max_rms = x_max_data
                if tlims_i is not None and tlims_i[1] is not None:
                    x_max_rms = tlims_i[1]
                text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
                text_rms_binned[f"row{i_row}"] = text_rms_binned_template.format(nanstd(bindata[logical_and(midbins >= x_min_rms, midbins <= x_max_rms)]))
                print(f"RMS row {i_row}: {text_rms_binned[f'row{i_row}']} {unit}")
                logger.debug(f"Done: Plot binned data for row {i_row}")     

            ###########
            # Write rms
            ###########
            # WARNING, TO BE IMPROVED for more than one dataset
            if rms_kwargs['do']:
                print_rms(ax=ax_ts_i, text_pos=(0.0, 1.05), row_name=i_row,
                          start_with_rmsequal=True, add_rms_row=True,
                          datasetnames_in_row=datasetnames, pl_kwargs=pl_kwarg_final,
                          text_rms=text_rms, text_rms_binned=text_rms_binned, fontsize=fontsize, unit=unit)

            #########################
            # Plot the models to show
            #########################
            for model_i in models2plot.get_model2show(row_idx=i_row):
                # if datasetname4model4row[key_model][i_row] == 'all':
                #     l_datasetnames_4_plot = datasetnames
                # else:
                #     l_datasetnames_4_plot = [datasetname4model4row[key_model][i_row]]
                    
                # for datasetname in l_datasetnames_4_plot:
                #     if datasetname4model4row[key_model][i_row] == 'all':
                #         if key_model in computed_models_4_iTS[datasetname]:
                #             ymodel = computed_models_4_iTS[datasetname][key_model]
                #         else:
                #             continue
                #         if key_model == "decorrelation_likelihood":
                #             xmodel = computed_models_4_iTS[datasetname]["tsim_decorr_like"]
                #         else:
                #             xmodel = computed_models_4_iTS[datasetname]['xsim']
                #     else:
                #         if key_model in computed_models_4_iTS[datasetname]['all']:
                #             ymodel = computed_models_4_iTS[datasetname]['all'][key_model]
                #         else:
                #             continue
                #         xmodel = computed_models_4_iTS['xsim_all'] 
                tsim_values, model_values, model_values_err = model_i.get_computed_model(exptime_bin=exptime_bin, supersamp=supersamp_bin_model)  
                if key_model in pl_kwarg_final[datasetname]:
                    pl_kwarg_to_use = pl_kwarg_final[datasetname][key_model]
                else:
                    pl_kwarg_to_use = {"fmt": '', "linestyle": "-", "label": key_model}
                ebconts_lines_labels_model = ax_ts_i.errorbar(tsim_values / time_fact, model_values, **pl_kwarg_to_use)
                if not("color" in pl_kwarg_to_use):
                    pl_kwarg_to_use["color"] = ebconts_lines_labels_model[0].get_color()
                if not("alpha" in pl_kwarg_to_use):
                    pl_kwarg_to_use["alpha"] = ebconts_lines_labels_model[0].get_alpha()
                    if pl_kwarg_to_use["alpha"] is None:
                        pl_kwarg_to_use["alpha"] = 1.
                # Plot the model_err
                key_err = key_model + "_err"
                if model_values_err is not None:
                    if not("color" in pl_kwarg_final[datasetname][key_err]):
                        pl_kwarg_final[datasetname][key_err]["color"] = pl_kwarg_to_use["color"]
                    if not("alpha" in pl_kwarg_final[datasetname][key_err]):
                        pl_kwarg_final[datasetname][key_err]["alpha"] = pl_kwarg_to_use["alpha"] / 3
                        _ = ax_ts_i.fill_between(tsim_values, model_values - model_values_err, model_values + model_values_err, **pl_kwarg_final[datasetname][key_err])
                                
            ###################################
            # Set ylims and indicate_y_outliers
            ###################################
            logger.debug(f"Setting ylims and indicating outliers for row {i_row}")
            # Set the y axis limits and indicate outliers for the data at the raw cadence
            ylims_to_use = define_x_or_y_lims(x_or_ylims=ylims['data'], row_name=i_row, col_name=0)
            if (ylims_to_use is None) and (pad['data'] is not None):
                points_pl_i_row = concatenate([datas[dst] for dst in datasetnames])
                et.auto_y_lims(points_pl_i_row, ax_ts_i, pad=pad['data'])
            else:
                ax_ts_i.set_ylim(ylims_to_use)

            # Indicate outlier values that are off y-axis with an arrows for raw cadence
            if indicate_y_outliers['data']:
                for dst in datasetnames:
                    et.indicate_y_outliers(x=x_values[dst], y=datas[dst], ax=ax_ts_i,
                                           color=pl_kwarg_final[datasetname]["data"]["color"],
                                           alpha=pl_kwarg_final[datasetname]["data"]["alpha"])

            # # Draw a horizontal line at 0 in the residual plot
            # axe_resi.hlines(0, *current_xlims, colors="k", linestyles="dashed")
            logger.debug(f"Done: Set ylims and indicate outliers for row {i_row}")

            ############################
            # Set the tlims if provided
            ############################
            logger.debug(f"Setting xlims for row {i_row}")
            # Set the x axis limits
            if TS_kwargs.get('force_tlims', False):
                ax_ts_i.set_xlim(tlims_i)
            else:
                x_row = concatenate([x_values[dst] for dst in datasetnames])
                ax_ts_i.set_xlim((min(x_row), max(x_row)))
            logger.debug(f"Done: Set xlims for row {i_row}")
            ##########################
            # Set the legend if needed
            ##########################
            set_legend(ax=ax_ts_i, legend_kwargs=legend_kwargs[0][i_row], fontsize_def=fontsize)
            logger.debug("Done: TS plot")

        ######################################
        # Generalized Lomb-Scargle Periodogram
        ######################################
        if GLSP_kwargs.get("do", True):

            logger.debug(f"Doing GLSP plot for row {i_row}/{nb_rows_ts}")

            # Set gls_input
            gls_inputs = OrderedDict()
            gls_inputs["data"] = {}
            # Variable that are always available
            gls_inputs["data"]["time"] = concatenate([dico_load['times'][dst] for dst in datasetnames])
            idx_sort = argsort(gls_inputs["data"]["time"])
            gls_inputs["data"]["time"] = gls_inputs["data"]["time"][idx_sort]
            gls_inputs["data"]["value"] = concatenate([datas[dst] for dst in datasetnames])[idx_sort]
            gls_inputs["data"]["label"] = data_label
            if GLSP_kwargs.get("use_jitter", True):
                gls_inputs["data"]["err"] = concatenate([dico_load['data_err_jitters'][dst] for dst in datasetnames])[idx_sort]
            else:
                gls_inputs["data"]["err"] = concatenate([dico_load['data_errs'][dst] for dst in datasetnames])[idx_sort]
            print(f"")
            for model_i in models2plot.get_model2show(row_idx=i_row):
                gls_inputs[key_model] = {}
                gls_inputs[key_model]["time"] = gls_inputs["data"]["time"]
                gls_inputs[key_model]["value"] = concatenate([models[dst][key_model].get_computed_model(exptime_bin=exptime_bin, supersamp=supersamp_bin_model)[1] for dst in datasetnames])[idx_sort]
                gls_inputs[key_model]["err"] = gls_inputs["data"]["err"]
                gls_inputs[key_model]["label"] = key_model

            ###################
            # Compute the GLSPs
            ###################
            glsps = {}
            for key in gls_inputs.keys():
                glsps[key] = Gls((gls_inputs[key]["time"], gls_inputs[key]["value"], gls_inputs[key]["err"]), Pbeg=Pbeg, Pend=Pend, verbose=False)

            ###############
            # Plot the GLSP
            ###############
            for j_col_glsp, (gs_gls_j, freq_lims_j, period_no_ticklabels_j) in enumerate(zip(gs_gls, freq_lims, period_no_ticklabels)):
                if i_row == 0:
                    kwargs_add_suplot = {}
                else:
                    kwargs_add_suplot = {'sharex': ax_gls_i}
                ax_gls_i = fig.add_subplot(gs_gls_j[i_row], **kwargs_add_suplot)
                if (j_col_glsp == 0) and (i_row == 0):
                    ax_gls_i.set_title("GLS Periodograms", fontsize=fontsize)
                if (i_row == 0) and logscale:
                    ax_gls_i.set_xscale("log")
        
                # create and set the twiny axis
                ax_gls_twin_im1 = ax_gls_twin_i if i_row != 0 else None
                ax_gls_twin_i = ax_gls_i.twiny()
                if ax_gls_twin_im1 is not None:
                    ax_gls_twin_im1.sharex(ax_gls_twin_i)
                if logscale:
                    ax_gls_twin_i.set_xscale("log")
                ax_gls_i.set_zorder(ax_gls_twin_i.get_zorder() + 1)  # To make sure that the orginal axis is above the new one
                ax_gls_i.patch.set_visible(False)
                labeltop = True if i_row == 0 else False
                ax_gls_twin_i.tick_params(axis="x", labeltop=labeltop, labelsize=fontsize, which="both", direction="in")
                ax_gls_twin_i.tick_params(axis="x", which="major", length=4, width=1)
                ax_gls_twin_i.tick_params(axis="x", which="minor", length=2, width=0.5)
                ax_gls_i.tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
                ax_gls_i.tick_params(axis="both", which="major", length=4, width=1)
                ax_gls_i.tick_params(axis="both", which="minor", length=2, width=0.5)
                # ax_gls_i.yaxis.set_label_position("right")
                # ax_gls_i.yaxis.tick_right()
                labelleft = True if j_col_glsp == 0 else False
                labelbottom = True if i_row == (nb_rows_glsp - 1) else False
                ax_gls_i.tick_params(axis="x", labelleft=labelleft, labelbottom=labelbottom, labelsize=fontsize, which="both", direction="in")
                ax_gls_i.tick_params(axis="y", labelleft=labelleft, labelsize=fontsize, which="both", direction="in")
                ax_gls_i.yaxis.set_minor_locator(AutoMinorLocator())
                ax_gls_i.xaxis.set_minor_locator(AutoMinorLocator())

                # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
                for key in glsps:
                    if key == "data":
                        alpha = 1
                        color = "k"
                    else:
                        alpha = 0.5
                        color = None
                    ax_gls_i.plot(glsps[key].freq / day2sec * freq_fact, glsps[key].power, '-', color=color, alpha=alpha, label=gls_inputs[key]["label"], linewidth=GLSP_kwargs.get("lw ", 1.))
                # Set ticks and tick labels
                if j_col_glsp == 0:
                    ax_gls_i.set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # here which key doesn't matter as the label['ylabel'] are all the same

                ylims_gls = ax_gls_i.get_ylim()
                xlims_gls = ax_gls_i.get_xlim()

                # Print the period axis
                per_min = min(1 / glsps[key].freq)
                freq_min = min(glsps[key].freq)
                per_max = max(1 / glsps[key].freq)
                freq_max = max(glsps[key].freq)
                per_xlims = [1 / (freq_lim / freq_fact * day2sec) for freq_lim in xlims_gls]
                if per_xlims[0] < 0:  # Sometimes the inferior xlims_gls is negative and it messes up with the rest
                    per_xlims[0] = per_max
                per_xlims = per_xlims[::-1]
                if not(logscale):
                    ax_gls_twin_i.plot([freq_min / day2sec * freq_fact, freq_max / day2sec * freq_fact],
                                        [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                else:
                    ax_gls_twin_i.plot([per_min, per_max], [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                    xlims_per = ax_gls_twin_i.get_xlim()
                    ax_gls_twin_i.set_xlim(xlims_per[::-1])
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
                                    if tick in period_no_ticklabels_j:
                                        per_ticklabels_major.append("")
                                    else:
                                        per_ticklabels_major.append(tick)
                                else:
                                    per_ticks_minor.append(tick)
                    # ax_gls_twin_i.set_xticks(per_ticks_minor, minor=True)
                    ax_gls_twin_i.set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_major])
                    if GLSP_kwargs.get('scientific_notation_P_axis', True):
                        ax_gls_twin_i.set_xticklabels([fmt_sci_not(tick) if tick != "" else "" for tick in per_ticklabels_major])
                    else:
                        ax_gls_twin_i.set_xticklabels(per_ticklabels_major)
                    # ax_gls_twin_i.set_xticks(per_ticks_minor, minor=True)
                    ax_gls_twin_i.set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_minor], minor=True)

                    if freq_lims_j is None:
                        ax_gls_i.set_xlim(xlims_gls)
                        if logscale:
                            ax_gls_twin_i.set_xlim(xlims_per[::-1])
                        else:
                            ax_gls_twin_i.set_xlim(xlims_gls)
                    else:
                        ax_gls_i.set_xlim(freq_lims_j)
                        if logscale:
                            ax_gls_twin_i.set_xlim([1 / (freq / freq_fact * day2sec) for freq in freq_lims_j])
                        else:
                            ax_gls_twin_i.set_xlim(freq_lims_j)

                    ylims_gls = ax_gls_i.get_ylim()
                    xlims_gls = ax_gls_i.get_xlim()

                #####################################
                # Vertical lines at specified periods
                #####################################
                for per, dico_per in GLSP_kwargs.get('periods', {}).items():
                    vlines_kwargs = dico_per.get("vlines_kwargs", {})
                    if 'label' not in vlines_kwargs:
                        vlines_kwargs['label'] = str(format_float_positional(per, precision=3, unique=False, fractional=False, trim='k'))
                    freq_4_per = 1 / per / day2sec * freq_fact
                    lines_per = ax_gls_i.vlines(freq_4_per, *ylims_gls, **vlines_kwargs)
                ax_gls_i.set_ylim(ylims_gls)

                ##########################################
                # Horizontal lines at specified FAP levels
                ##########################################
                ylims_gls = ax_gls_i.get_ylim()
                xlims_gls = ax_gls_i.get_xlim()

                default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
                                    1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
                                    10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
                for fap_lvl, dico_fap in GLSP_kwargs.get('fap', default_fap_dict).items():
                    pow_ii = glsps[key].powerLevel(fap_lvl / 100)
                    hlines_kwargs = dico_fap.get("hlines_kwargs", {})
                    if pow_ii < ylims_gls[1]:
                        lines_fap = ax_gls_i.hlines(pow_ii, *xlims_gls, **hlines_kwargs)
                        text_kwargs = dico_fap.get("text_kwargs", {}).copy()
                        x_pos = text_kwargs.pop("x_pos", 1.05)
                        y_shift = text_kwargs.pop("y_shift", 0)
                        label = str(text_kwargs.pop("label", fr"{fap_lvl}\%"))
                        color = text_kwargs.pop("color", None)
                        if color is None:
                            color = lines_fap.get_color()[0]
                        if j_col_glsp == (nb_cols_gls - 1):
                            ax_gls_i.text(xlims_gls[0] + x_pos * (xlims_gls[1] - xlims_gls[0]), pow_ii + y_shift * (ylims_gls[1] - ylims_gls[0]),
                                            label, color=color, fontsize=fontsize, **text_kwargs)

                ax_gls_i.set_xlim(xlims_gls)
                
                #
                if j_col_glsp == 0:
                    ax_gls_i.legend(fontsize=fontsize, **legend_param.get(key, {}))  # handletextpad=-.1, handlelength=0,

                if i_row == 0:
                    ax_gls_twin_i.set_xlabel("Period [days]", fontsize=fontsize)

                # TODO: This part is just a copy paste from the TSNGLSP function and is currently not working
                if GLSP_kwargs.get("show_WF", True):
                    for i_WF, l_WF_key_model in enumerate(l_l_WF_key_model):
                        ax_gls[-i_WF - 1].plot(glsps[l_WF_key_model[0]].freq / day2sec * freq_fact, glsps[l_WF_key_model[0]].wf, '-', color="k", label=f"WF {l_WF_key_model}", linewidth=GLSP_kwargs.get("lw ", 1.))
                        if j_col_glsp == 0:
                            ax_gls[-i_WF - 1].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get("WF", {}))
                            ax_gls[-i_WF - 1].set_ylabel("Relative Amplitude")
                        labelleft = True if j_col_glsp == 0 else False
                        ax_gls[-i_WF - 1].tick_params(axis="both", labelleft=labelleft, labelsize=fontsize, right=True, which="both", direction="in")
            logger.debug(f"Done: GLSP plot for row {i_row}/{nb_rows_ts}")

    if GLSP_kwargs['do']:
        # Do the WF plot if needed
        ax_gls_i.set_xlabel(f"Frequency [{freq_unit}]", fontsize=fontsize)

    if TS_kwargs['do']:
        return (dico_load, kwargs_compute_model_4_key_model), computed_models_4_iTS
    else:
        return (dico_load, kwargs_compute_model_4_key_model), None