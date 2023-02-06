#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create phase folded plots

@TODO:
"""
from numpy import (linspace, inf, min, max, arange, std, logical_and, zeros, where, sqrt, sum, power,
                   nan, nanstd, concatenate, ones_like, argsort, mean, floor, log10, ceil, format_float_positional
                   )
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from scipy.stats import binned_statistic

from .misc import (AandA_fontsize, do_suptitle, check_row4datasetname, get_pl_kwargs, update_binned_label,
                   check_spec_by_column_or_row, check_spec_data_or_resi, check_datasetname4model4row,
                   define_x_or_y_lims, check_spec_for_data_or_resi_by_column_or_row, print_rms, check_kwargs_by_column_and_row,
                   set_legend, fmt_sci_not
                   )
from .core_compute_load import (load_datasets_and_models, compute_and_plot_model, get_key_compute_model,
                                is_valid_model_available
                                )
from ..emcee_tools import emcee_tools as et
from ..posterior.core.model.core_model import Core_Model

import sys
path_pyGLS = "/Users/olivier/Softwares/PyGLS"
if path_pyGLS not in sys.path:
    sys.path.append(path_pyGLS)
from gls_mod import Gls


key_whole = Core_Model.key_whole


day2sec = 24 * 60 * 60


def create_TSNGLSP_plots(fig, post_instance, df_fittedval,
                         compute_raw_models_func, remove_add_model_components_func,
                         kwargs_compute_model_4_key_model, l_valid_model,
                         y_name, inst_cat,
                         d_name_component_removed_to_print,
                         show_dict, l_model_1_per_row,
                         datasetnames4model4row=None,
                         datasim_kwargs=None,
                         datasetnames=None,
                         amplitude_fact=1., unit=None,
                         create_axes_kwargs=None,
                         TS_kwargs=None,
                         GLSP_kwargs=None,
                         suptitle_kwargs=None,
                         fontsize=AandA_fontsize,
                         get_key_compute_model_func=get_key_compute_model,
                         is_valid_model_available_func=is_valid_model_available,
                         kwargs_is_valid_model_available=None,
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
            - 'rms_kwargs'  : dict
                keys are:
                    'do'            : bool
                        (Default: True) Show the rms in between the data and residuals axes
                    'rms_format'    :
                        (Default: '.0f') Format that will be used to format the rms values
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
    computed_models : dict
        Outputs of the compute_and_plot_model function calls
    """
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
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
    TS_kwargs_user = TS_kwargs if create_axes_kwargs is not None else {}
    TS_kwargs = {'do': True, }
    TS_kwargs.update(TS_kwargs_user)

    GLSP_kwargs_user = GLSP_kwargs if create_axes_kwargs is not None else {}
    GLSP_kwargs = {'do': True, }
    GLSP_kwargs.update(GLSP_kwargs_user)

    # Create The GridSpec
    gs = GridSpec(nrows=1, ncols=int(TS_kwargs['do']) + int(GLSP_kwargs['do']),
                  figure=fig, **create_axes_kwargs['main_gridspec']
                  )
    if TS_kwargs['do']:
        gs_ts = gs[0]
        if GLSP_kwargs['do']:
            gs_gls = gs[1]
    else:
        gs_gls = gs[0]

    # If no dataset name is provided get all the available RV datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat=inst_cat, sortby_instcat=False, sortby_instname=False)

    # Load the defined datasets and check how many dataset there is by instrument.
    (dico_load, kwargs_compute_model_4_key_model
     ) = load_datasets_and_models(datasetnames=datasetnames, post_instance=post_instance, datasim_kwargs=datasim_kwargs,
                                  df_fittedval=df_fittedval, amplitude_fact=amplitude_fact,
                                  compute_raw_models_func=compute_raw_models_func,
                                  remove_add_model_components_func=remove_add_model_components_func,
                                  kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                  l_valid_model=l_valid_model,
                                  get_key_compute_model_func=get_key_compute_model_func,
                                  is_valid_model_available_func=is_valid_model_available_func,
                                  kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                  kwargs_get_key_compute_model=kwargs_get_key_compute_model
                                  )

    # Do the suptitle
    do_suptitle(fig=fig, post_instance=post_instance, datasetnames=datasetnames, fontsize=fontsize,
                dico_models=dico_load["models"], model_removed_or_add_dict=kwargs_compute_model_4_key_model["model"],
                data_remove_or_add_dict=kwargs_compute_model_4_key_model["data"], suptitle_kwargs=suptitle_kwargs
                )

    # Make sure the show_dict is well define
    show_dict_user = show_dict if show_dict is not None else {}
    show_dict = {"model": True, "GP_model": True}
    show_dict.update(show_dict_user)

    #############
    # TIME SERIES
    #############
    if TS_kwargs['do']:

        # Make sure that rms_kwargs is well defined
        rms_kwargs_user = TS_kwargs.get('rms_kwargs', None) if TS_kwargs.get('rms_kwargs', None) is not None else {}
        rms_kwargs = {'do': True, 'format': '.1e'}
        rms_kwargs.update(rms_kwargs_user)

        # Make sure that indicate_y_outliers is well defined
        indicate_y_outliers = check_spec_data_or_resi(spec_user=TS_kwargs.get('indicate_y_outliers', None), l_type_spec=[bool], spec_def=True)

        # Make sure that pad is well defined
        pad = check_spec_data_or_resi(spec_user=TS_kwargs.get('pad', None), l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

        # Define on which rows the datasets are plots using the row4datasetname input
        row4datasetname, datasetnames4rowidx = check_row4datasetname(row4datasetname=TS_kwargs.get("row4datasetname", None), datasetnames=datasetnames)
        nb_rows = len(datasetnames4rowidx)
        datasetname4model4row = check_datasetname4model4row(datasetname4model4row=datasetnames4model4row,
                                                            datasetnames4rowidx=datasetnames4rowidx,
                                                            l_model=list(show_dict.keys()), l_model_1_per_row=l_model_1_per_row,
                                                            )

        # Create the updated grid space according to the number of rows
        gs_ts = GridSpecFromSubplotSpec(nb_rows, 1, subplot_spec=gs_ts, **create_axes_kwargs['gridspec_row_TS'])

        # Determine which rows require a zoom.
        tlims = check_spec_by_column_or_row(spec_user=TS_kwargs.get('tlims', None), l_type_spec=[tuple, list],
                                            spec_def=None, l_row_name=list(range(nb_rows)))

        tlims_zoom = check_spec_by_column_or_row(spec_user=TS_kwargs.get('tlims_zoom', None), l_type_spec=[tuple, list],
                                                 spec_def=None, l_row_name=list(range(nb_rows)))

        # Infer from tlims_zoom how many columns are required
        if any([zoom is not None for zoom in tlims_zoom.values()]):
            nb_cols = 2
        else:
            nb_cols = 1

        # Make sure that ylims is well defined
        ylims = check_spec_for_data_or_resi_by_column_or_row(spec_user=TS_kwargs.get('ylims', None),
                                                             l_row_name=list(range(nb_rows)),
                                                             l_col_name=list(range(nb_cols)),
                                                             l_type_spec=[tuple, list],
                                                             spec_def={'data': None, 'resi': None}
                                                             )

        # Make sure that legend_kwargs is well defined
        legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=TS_kwargs.get('legend_kwargs', None),
                                                       l_row_name=list(range(nb_rows)),
                                                       l_col_name=list(range(nb_cols)),
                                                       kwargs_def={'do': False},
                                                       kwargs_init={0: {i_row: {'do': True} for i_row in range(nb_rows)}}
                                                       )

        # Set the binning variables
        one_binning_per_row = TS_kwargs.get("one_binning_per_row", False)
        exptime_bin = TS_kwargs.get("exptime_bin", 0.)
        binning_stat = TS_kwargs.get("binning_stat", "mean")
        supersamp_bin_model = TS_kwargs.get('supersamp_bin_model', 10)
        time_fact = TS_kwargs.get('time_fact', 1.)
        time_unit = TS_kwargs.get('time_unit', 'days')

        npt_model = TS_kwargs.get('npt_model', 1000)
        extra_dt_model = TS_kwargs.get("extra_dt_model", 0.)

        ##############################################
        # Set the arguments for the plotting functions
        ##############################################
        (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
         ) = get_pl_kwargs(pl_kwargs=TS_kwargs.get('pl_kwargs', None), dico_nb_dstperinsts=dico_load['dico_nb_dstperinsts'], datasetnames=datasetnames,
                           bin_size=exptime_bin, one_binning_per_row=one_binning_per_row,
                           nb_rows=nb_rows, alpha_def_data=1, color_def_data=None, show_error_data_def=True)

        update_binned_label(pl_kwarg_final=pl_kwarg_final, datasetnames=datasetnames, bin_size=exptime_bin,
                            bin_size_unit=f" {time_unit}", one_binning_per_row=one_binning_per_row,
                            nb_rows=nb_rows)

        #################################
        # Init the output computed_models
        #################################
        computed_models = {}

        #############################################################
        # Make the data and residuals plots (full and zoomed if needed)
        #############################################################
        text_rms = OrderedDict()
        text_rms_binned = OrderedDict()
        show_title = TS_kwargs.get("show_title", True)
        for i_row in range(nb_rows):
            # Create gs for all and for zoom
            gs_ts_row = GridSpecFromSubplotSpec(1, nb_cols, subplot_spec=gs_ts[i_row], **create_axes_kwargs['gridspec_col_TS'])

            for i_col in range(nb_cols):
                gs_ts_i = gs_ts_row[i_col]
                if i_col == 0:
                    tlims_i = tlims.get(i_row, tlims['all'])
                else:  # i_col == 1
                    tlims_i = tlims_zoom.get(i_row, tlims['all'])

                # Compute the time (including time_fact, x_values) corresponding to each point in each dataset and the minimum and maximum of all dataset for the row
                xlims_datas = OrderedDict()
                x_values = OrderedDict()
                for datasetname in datasetnames4rowidx[i_row]:
                    xlims_datas[datasetname] = [inf, -inf]
                    x_values[datasetname] = dico_load['times'][datasetname] * time_fact
                    if min(x_values[datasetname]) < xlims_datas[datasetname][0]:
                        xlims_datas[datasetname][0] = min(x_values[datasetname])
                    if max(x_values[datasetname]) > xlims_datas[datasetname][1]:
                        xlims_datas[datasetname][1] = max(x_values[datasetname])

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

                for datasetname in datasetnames4rowidx[i_row]:
                    # Init computed_models for this dataset
                    computed_models[datasetname] = {}

                    ####################
                    # Compute the models
                    ####################
                    for model, show_model in show_dict.items():
                        if model == "GP_model":
                            continue
                        if show_model and ((datasetname4model4row[model][i_row] == datasetname) or (datasetname4model4row[model][i_row] == 'all')):
                            if datasetname4model4row[model][i_row] == 'all':
                                xlims_model = (xlims_datas[datasetname][0] - extra_dt_model, xlims_datas[datasetname][1] + extra_dt_model)
                            else:
                                xlims_model = (min([xlims_datas[dst][0] for dst in datasetnames4rowidx[i_row]]) - extra_dt_model,
                                               max([xlims_datas[dst][1] for dst in datasetnames4rowidx[i_row]]) + extra_dt_model
                                               )
                            if tlims_i is not None:
                                if (tlims_i[0] is not None) and (tlims_i[0] > xlims_model[0]):
                                    xlims_model[0] = tlims_i[0]
                                if (tlims_i[1] is not None) and (tlims_i[1] < xlims_model[1]):
                                    xlims_model[1] = tlims_i[1]
                            tlims_model = (xlims_model[0] / time_fact, xlims_model[1] / time_fact)
                            # include_gp_model = True if ((model == "model") and show_dict["GP"]) else False
                            kwargs_compute_model = kwargs_compute_model_4_key_model.get(model, {})
                            if 'include_gp_model' in kwargs_compute_model:
                                include_gp_model = kwargs_compute_model['include_gp_model']
                            else:
                                if model == 'model':
                                    include_gp_model = True
                                else:
                                    include_gp_model = False
                            # import pdb; pdb.set_trace()
                            show_binned_model = TS_kwargs.get('show_binned_model', {}).get(model, True)
                            if model == "decorrelation_likelihood":
                                computed_models[datasetname]["tsim_decorr_like"] = dico_load["times"][datasetname]
                                (models_decorr_like, pl_kwarg_final
                                 ) = compute_and_plot_model(tsim=dico_load["times"][datasetname],
                                                            key_model=model,
                                                            datasetname=datasetname,
                                                            post_instance=post_instance,
                                                            df_fittedval=df_fittedval,
                                                            datasim_kwargs=datasim_kwargs,
                                                            include_gp_model=include_gp_model,
                                                            amplitude_fact=amplitude_fact,
                                                            compute_raw_models_func=compute_raw_models_func,
                                                            remove_add_model_components_func=remove_add_model_components_func,
                                                            key_pl_kwarg=model,
                                                            remove_dict=kwargs_compute_model.get('remove_dict', {}),
                                                            add_dict=kwargs_compute_model.get('add_dict', {}),
                                                            exptime_bin=0.,
                                                            supersamp_bin_model=1.,
                                                            fact_tsim_to_xsim=time_fact,
                                                            xsim=None,
                                                            plot=True, ax=axe_data,
                                                            pl_kwarg=pl_kwarg_final,
                                                            show_binned_model=False,
                                                            models=None,
                                                            l_valid_model=l_valid_model,
                                                            get_key_compute_model_func=get_key_compute_model_func,
                                                            is_valid_model_available_func=is_valid_model_available_func,
                                                            kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                                            kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                            )
                                computed_models[datasetname]["decorr_like"] = models_decorr_like["decorr_like"]
                            else:
                                computed_models[datasetname]["tsim"] = linspace(*tlims_model, npt_model)
                                computed_models[datasetname]["xsim"] = computed_models[datasetname]["tsim"] * time_fact
                                (computed_models[datasetname], pl_kwarg_final
                                 ) = compute_and_plot_model(tsim=computed_models[datasetname]["tsim"],
                                                            key_model=model,
                                                            datasetname=datasetname,
                                                            post_instance=post_instance,
                                                            df_fittedval=df_fittedval,
                                                            datasim_kwargs=datasim_kwargs,
                                                            include_gp_model=include_gp_model,
                                                            amplitude_fact=amplitude_fact,
                                                            compute_raw_models_func=compute_raw_models_func,
                                                            remove_add_model_components_func=remove_add_model_components_func,
                                                            key_pl_kwarg=model,
                                                            remove_dict=kwargs_compute_model.get('remove_dict', {}),
                                                            add_dict=kwargs_compute_model.get('add_dict', {}),
                                                            exptime_bin=exptime_bin,
                                                            supersamp_bin_model=supersamp_bin_model,
                                                            fact_tsim_to_xsim=time_fact,
                                                            xsim=None,
                                                            plot=True, ax=axe_data,
                                                            pl_kwarg=pl_kwarg_final,
                                                            show_binned_model=show_binned_model,
                                                            models=computed_models[datasetname],
                                                            l_valid_model=l_valid_model,
                                                            get_key_compute_model_func=get_key_compute_model_func,
                                                            is_valid_model_available_func=is_valid_model_available_func,
                                                            kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                                            kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                            )

                    ###############
                    # Plot the data
                    ###############
                    if pl_show_error[datasetname]['data']:
                        ebcont = axe_data.errorbar(x_values[datasetname], y=dico_load['datas'][datasetname],
                                                   yerr=dico_load['data_errs'][datasetname], **pl_kwarg_final[datasetname]["data"])  # Plot the data point and error bars without jitter
                        if not("ecolor" in pl_kwarg_jitter[datasetname]):
                            pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
                        if not("color" in pl_kwarg_final[datasetname]):
                            pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
                        if dico_load['has_jitters'][datasetname]:
                            axe_data.errorbar(x_values[datasetname], y=dico_load['datas'][datasetname],
                                              yerr=dico_load['data_err_jitters'][datasetname], **pl_kwarg_jitter[datasetname]["data"])  # Plot the error bars with jitter

                    else:
                        axe_data.errorbar(x_values[datasetname], y=dico_load['datas'][datasetname], **pl_kwarg_final[datasetname]["data"])  # Plot the data point and error bars without jitter

                    ####################
                    # Plot the residuals
                    ####################
                    if pl_show_error[datasetname]['data']:
                        if dico_load['has_jitters'][datasetname]:
                            axe_resi.errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], yerr=dico_load['data_err_jitters'][datasetname], **pl_kwarg_jitter[datasetname]["data"])  # Plot the error bars with jitter
                        axe_resi.errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], yerr=dico_load['data_errs'][datasetname], **pl_kwarg_final[datasetname]["data"])
                    else:
                        axe_resi.errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], **pl_kwarg_final[datasetname]["data"])
                    # Compute rms of the residuals and print it on the top of the residuals graphs
                    x_min_rms = xlims_datas[datasetname][0]
                    if tlims_i is not None and tlims_i[0] is not None:
                        x_min_rms = tlims_i[0]
                    x_max_rms = xlims_datas[datasetname][1]
                    if tlims_i is not None and tlims_i[1] is not None:
                        x_max_rms = tlims_i[1]
                    text_rms_template = f"{{:{rms_kwargs['format']}}}"
                    text_rms[datasetname] = text_rms_template.format(std(dico_load['residuals'][datasetname][logical_and(x_values[datasetname] >= x_min_rms, x_values[datasetname] <= x_max_rms)]))
                    print(f"RMS {datasetname} = {text_rms[datasetname]} {unit} (raw cadence)")

                    ################################################################################
                    # Compute and Plot the binned data and residuals if one_binning_per_row is False
                    ################################################################################
                    if not(one_binning_per_row) and (exptime_bin > 0.):
                        x_min_data, x_max_data = (min(x_values[datasetname]), max(x_values[datasetname]))
                        bins = arange(x_min_data, x_max_data + exptime_bin, exptime_bin)
                        midbins = bins[:-1] + exptime_bin / 2
                        nbins = len(bins) - 1
                        # Compute the binned values
                        (bindata, binedges, binnb
                         ) = binned_statistic(dico_load['times'][datasetname], dico_load['datas'][datasetname],
                                              statistic=binning_stat, bins=bins,
                                              range=(x_min_data, x_max_data))
                        (binresi, binedges, binnb
                         ) = binned_statistic(dico_load['times'][datasetname], dico_load['residuals'][datasetname],
                                              statistic=binning_stat, bins=bins,
                                              range=(x_min_data, x_max_data))
                        # Compute the err on the binned values
                        binstd = zeros(nbins)
                        if dico_load['has_jitters'][datasetname]:
                            binstd_jitter = zeros(nbins)
                        bincount = zeros(nbins)
                        for i_bin in range(nbins):
                            bincount[i_bin] = len(where(binnb == (i_bin + 1))[0])
                            if bincount[i_bin] > 0.0:
                                binstd[i_bin] = sqrt(sum(power((dico_load['data_errs'][datasetname]
                                                                         [binnb == (i_bin + 1)]
                                                                ),
                                                               2.
                                                               )
                                                         ) /
                                                     bincount[i_bin]**2
                                                     )
                                if dico_load['has_jitters'][datasetname]:
                                    binstd_jitter[i_bin] = sqrt(sum(power((dico_load['data_err_jitters'][datasetname]
                                                                                    [binnb == (i_bin + 1)]
                                                                           ),
                                                                          2.
                                                                          )
                                                                    ) /
                                                                bincount[i_bin]**2
                                                                )
                            else:
                                binstd[i_bin] = nan
                                if dico_load['has_jitters'][datasetname]:
                                    binstd_jitter[i_bin] = nan
                        # Plot the binned data
                        bin_err = binstd if pl_show_error[datasetname]["databinned"] else None
                        ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                        if not("color" in pl_kwarg_final[datasetname]["databinned"]):
                            pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
                        if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
                            pl_kwarg_jitter[datasetname]["databinned"] = pl_kwarg_final[datasetname]["databinned"]["color"]
                        _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                        if dico_load['has_jitters'][datasetname] and pl_show_error[datasetname]["databinned"]:
                            _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"])
                            _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"])
                        # Compute rms of the binned residuals
                        x_min_rms = x_min_data
                        if tlims_i is not None and tlims_i[0] is not None:
                            x_min_rms = tlims_i[0]
                        x_max_rms = x_max_data
                        if tlims_i is not None and tlims_i[1] is not None:
                            x_max_rms = tlims_i[1]
                        text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
                        text_rms_binned[datasetname] = text_rms_binned_template.format(nanstd(binresi[logical_and(midbins >= x_min_rms, midbins <= x_max_rms)]))
                        print(f"RMS {datasetname}: {text_rms_binned[datasetname]} {unit}")

                ################################################################################
                # Compute and Plot the binned data and residuals if one_binning_per_row is True
                ################################################################################
                if one_binning_per_row and (exptime_bin > 0.):
                    x_row = concatenate([x_values[dst] for dst in datasetnames4rowidx[i_row]])
                    x_min_data, x_max_data = (min(x_row), max(x_row))
                    bins = arange(x_min_data, x_max_data + exptime_bin, exptime_bin)
                    midbins = bins[:-1] + exptime_bin / 2
                    nbins = len(bins) - 1
                    # Compute the binned values
                    (bindata, binedges, binnb
                     ) = binned_statistic(x_row, concatenate([dico_load['datas'][dst] for dst in datasetnames4rowidx[i_row]]),
                                          statistic=binning_stat, bins=bins,
                                          range=(x_min_data, x_max_data))
                    (binresi, binedges, binnb
                     ) = binned_statistic(x_row, concatenate([dico_load['residuals'][dst] for dst in datasetnames4rowidx[i_row]]),
                                          statistic=binning_stat, bins=bins,
                                          range=(x_min_data, x_max_data))
                    # Compute the err on the binned values
                    binstd = zeros(nbins)
                    if any([dico_load['has_jitters'][datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                        binstd_jitter = zeros(nbins)
                    bincount = zeros(nbins)
                    data_err_row = concatenate([dico_load['data_errs'][dst] for dst in datasetnames4rowidx[i_row]])
                    data_err_jitter_row = concatenate([dico_load['data_err_jitters'][dst] if dico_load['has_jitters'][dst] else ones_like(dico_load['data_errs'][dst]) * nan for dst in datasetnames4rowidx[i_row]])
                    for i_bin in range(nbins):
                        bincount[i_bin] = len(where(binnb == (i_bin + 1))[0])
                        if bincount[i_bin] > 0.0:
                            binstd[i_bin] = sqrt(sum(power(data_err_row[binnb == (i_bin + 1)], 2.)) /
                                                 bincount[i_bin]**2
                                                 )
                            if any([dico_load['has_jitters'][datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                                binstd_jitter[i_bin] = sqrt(sum(power(data_err_jitter_row[binnb == (i_bin + 1)],
                                                                      2.
                                                                      )
                                                                ) /
                                                            bincount[i_bin]**2
                                                            )
                        else:
                            binstd[i_bin] = nan
                            if any([dico_load['has_jitters'][datasetname] for datasetname in datasetnames4rowidx[i_row]]):
                                binstd_jitter[i_bin] = nan
                    # Plot the binned data
                    bin_err = binstd if pl_show_error[f"row{i_row}"] else None
                    ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"])
                    if not("color" in pl_kwarg_final[f"row{i_row}"]):
                        pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
                    if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
                        pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
                    _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"])
                    if any([dico_load['has_jitters'][dst] for dst in datasetnames4rowidx[i_row]]) and pl_show_error[f"row{i_row}"]:
                        _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"])
                        _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"])
                    # Compute rms of the binned residuals
                    x_min_rms = x_min_data
                    if tlims_i is not None and tlims_i[0] is not None:
                        x_min_rms = tlims_i[0]
                    x_max_rms = x_max_data
                    if tlims_i is not None and tlims_i[1] is not None:
                        x_max_rms = tlims_i[1]
                    text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
                    text_rms_binned[f"row{i_row}"] = text_rms_binned_template.format(nanstd(binresi[logical_and(midbins >= x_min_rms, midbins <= x_max_rms)]))
                    print(f"RMS row {i_row}: {text_rms_binned[f'row{i_row}']} {unit}")

                # Draw a horizontal line at the level of reference stellar RV level
                # current_xlims = axe_data.get_xlim()
                # if remove_stellar_var:
                #     reference_stellar_RV = 0
                #     axe_data.hlines(reference_stellar_RV, *current_xlims, colors="k", linestyles="dashed")

                ###########
                # Write rms
                ###########
                # WARNING, TO BE IMPROVED for more than one dataset
                if rms_kwargs['do']:
                    print_rms(ax=axe_resi, text_pos=(0.0, 1.05), row_name=i_row,
                              start_with_rmsequal=(i_col == 0), add_rms_row=True,
                              datasetnames_in_row=datasetnames4rowidx[i_row], pl_kwargs=pl_kwarg_final,
                              text_rms=text_rms, text_rms_binned=text_rms_binned, fontsize=fontsize, unit=unit)

                ###################################
                # Set ylims and indicate_y_outliers
                ###################################
                # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
                for axe, data_or_resi, points, in zip((axe_data, axe_resi),
                                                      ("data", "resi"),
                                                      (dico_load['datas'], dico_load['residuals']),
                                                      ):
                    # Set the y axis limits
                    ylims_to_use = define_x_or_y_lims(x_or_ylims=ylims[data_or_resi], row_name=i_row, col_name=i_col)
                    if (ylims_to_use is None) and (pad[data_or_resi] is not None):
                        points_pl_i_row = concatenate([points[datasetname] for datasetname in datasetnames4rowidx[i_row]])
                        et.auto_y_lims(points_pl_i_row, axe, pad=pad[data_or_resi])
                    else:
                        axe.set_ylim(ylims_to_use)

                    # Indicate outlier values that are off y-axis with an arrows for raw cadence
                    if indicate_y_outliers[data_or_resi]:
                        for datasetname in datasetnames4rowidx[i_row]:
                            et.indicate_y_outliers(x=x_values[datasetname], y=points[datasetname], ax=axe,
                                                   color=pl_kwarg_final[datasetname]["data"]["color"],
                                                   alpha=pl_kwarg_final[datasetname]["data"]["alpha"])

                # # Draw a horizontal line at 0 in the residual plot
                # axe_resi.hlines(0, *current_xlims, colors="k", linestyles="dashed")

                ############################
                # Set the tlims if provided
                ############################
                # Set the x axis limits
                if (i_col == 1) or TS_kwargs.get('force_tlims', False):
                    axe_data.set_xlim(tlims_i)
                else:
                    x_row = concatenate([x_values[dst] for dst in datasetnames4rowidx[i_row]])
                    axe_data.set_xlim((min(x_row), max(x_row)))

                ##########################
                # Set the legend if needed
                ##########################
                set_legend(ax=axe_data, legend_kwargs=legend_kwargs[i_col][i_row], fontsize_def=fontsize)

    ######################################
    # Generalized Lomb-Scargle Periodogram
    ######################################
    if GLSP_kwargs.get("do", True):
        # Variable that are always available
        all_time = concatenate([dico_load['times'][dst] for dst in datasetnames])
        idx_sort = argsort(all_time)
        all_data = concatenate([dico_load['datas'][dst] for dst in datasetnames])[idx_sort]
        if GLSP_kwargs.get("use_jitter", True):
            all_data_err = concatenate([dico_load['data_err_jitters'][dst] for dst in datasetnames])[idx_sort]
        else:
            all_data_err = concatenate([dico_load['data_errs'][dst] for dst in datasetnames])[idx_sort]
        all_model = concatenate([dico_load['models'][dst]['model'] for dst in datasetnames])[idx_sort]
        all_resi = concatenate([dico_load['residuals'][dst] for dst in datasetnames])[idx_sort]
        gls_inputs = {"data": {"time": all_time, "data": all_data, "err": all_data_err, 'label': "data"},
                      "model": {"time": all_time, "data": all_model, "err": all_data_err, 'label': "model"},  # sqrt(gp_pred_var_GLS)
                      "resi": {"time": all_time, "data": all_resi, "err": all_data_err, 'label': "residuals"},
                      }
        l_gls_key = ["data", "model", "resi"]
        # Add the GP
        # Add the inst vars
        # Add the stellar vars
        # Add the decorrelation model
        # Add the decorrelation lieklihood

        # model_GLS, _, gp_pred_GLS, gp_pred_var_GLS = post_instance.compute_model(tsim=all_time, dataset_name=l_datasetname_RVrefglobal[0],
        #                                                                          param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
        #                                                                          key_obj=key_whole, datasim_kwargs=datasim_kwargs, include_gp=True)
        # model_GLS *= RV_fact
        # if gp_pred_GLS is not None:
        #     gp_pred_GLS *= RV_fact
        #     gp_pred_var_GLS *= RV_fact**2
        # if model_wGP is not None:  # WARNING: This assumes that all datasets have (or don't have) GP
        #     gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
        #                   "model": {"data": model_GLS, "err": sqrt(gp_pred_var_GLS), 'label': "model"},  # sqrt(gp_pred_var_GLS)
        #                   "GP": {"data": gp_pred_GLS, "err": sqrt(gp_pred_var_GLS), 'label': "GP"},
        #                   "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
        #                   }
        #     l_gls_key = ["data", "model", "GP", "resi"]
        # else:
        #     gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err, 'label': "data"},
        #                   "model": {"data": model_GLS, "err": all_rv_data_err, 'label': "model"},  # sqrt(gp_pred_var_GLS)
        #                   "resi": {"data": all_resi, "err": all_rv_data_err, 'label': "residuals"},
        #                   }
        #     l_gls_key = ["data", "model", "resi"]

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
                per_min = min(1 / glsps[key].freq)
                freq_min = min(glsps[key].freq)
                per_max = max(1 / glsps[key].freq)
                freq_max = max(glsps[key].freq)
                per_xlims = [1 / (freq_lim / freq_fact * day2sec) for freq_lim in xlims]
                if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
                    per_xlims[0] = per_max
                per_xlims = per_xlims[::-1]
                if not(logscale):
                    ax_gls_twin[ii].plot([freq_min / day2sec * freq_fact, freq_max / day2sec * freq_fact],
                                         [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                else:
                    ax_gls_twin[ii].plot([per_min, per_max], [mean(glsps[key].power), mean(glsps[key].power)], "k", alpha=0)
                    xlims_per = ax_gls_twin[ii].get_xlim()
                    ax_gls_twin[ii].set_xlim(xlims_per[::-1])
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
                    # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
                    ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_major])
                    if GLSP_kwargs.get('scientific_notation_P_axis', True):
                        ax_gls_twin[ii].set_xticklabels([fmt_sci_not(tick) if tick != "" else "" for tick in per_ticklabels_major])
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
                        label = str(text_kwargs.pop("label", format_float_positional(per, precision=3, unique=False, fractional=False, trim='k')))
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

    return dico_load, computed_models