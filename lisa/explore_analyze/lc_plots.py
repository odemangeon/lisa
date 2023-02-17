#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create plot specifically for light curve data

@TODO:
"""
from logging import getLogger
from numpy import ones_like
from collections import OrderedDict

from .phase_folded import create_phasefolded_plots
from .ts_and_glsp import create_TSNGLSP_plots
from .misc import AandA_fontsize
from .core_compute_load import get_key_compute_model as get_key_compute_model_core
from .core_compute_load import is_valid_model_available as is_valid_model_available_core
from .core_compute_load import compute_raw_models as compute_raw_models_core

from ..posterior.core.model.core_model import Core_Model


key_whole = Core_Model.key_whole

# logger
logger = getLogger()


# remove_dict_def_PF = {'1': True, 'decorrelation': True, 'decorrelation_likelihood': True, 'GP_dataNmodel': True,
#                       'stellar_var': True, 'inst_var': True, 'contamination': True, 'GP_residual': True}
# add_dict_def_PF = {'1': False, 'decorrelation': False, 'decorrelation_likelihood': False, 'GP_dataNmodel': False,
#                    'stellar_var': False, 'inst_var': False, 'contamination': False, 'GP_residual': False}
# remove_dict_def_TS = {'1': True, 'decorrelation': True, 'decorrelation_likelihood': True, 'GP_dataNmodel': True,
#                       'stellar_var': True, 'inst_var': True, 'contamination': True, 'GP_residual': True}
# add_dict_def_TS = {'1': False, 'decorrelation': False, 'decorrelation_likelihood': False, 'GP_dataNmodel': False,
#                    'stellar_var': False, 'inst_var': False, 'contamination': False, 'GP_residual': False}

l_valid_model = ["model", "1", "contamination", "stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]

dict_model_false = {key: False for key in l_valid_model[1:]}
dict_model_true = {key: True for key in l_valid_model[1:]}

d_name_component_removed_to_print = {'stellar_var': "Stellar Var", 'inst_var': "Inst Var", 'decorrelation': "Decorrelation",
                                     'decorrelation_likelihood': "Decorrelation Likelihood", 'contamination': "Contamination",
                                     'GP_dataNmodel': "GP",
                                     }


def create_LC_phasefolded_plots(post_instance, df_fittedval, datasim_kwargs=None,
                                planets=None, periods=None, periods_remove_or_add_dict=None,
                                datasetnames=None, row4datasetname=None,
                                datasetnameformodel4row=None, npt_model=1000,
                                phasefold_central_phase=0.,
                                remove1=True, remove_contamination=True,
                                show_time_from_tic=False, time_fact=24, time_unit="h",
                                exptime_bin=0.0, binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                                one_binning_per_row=True,
                                sharey=False, create_axes_kwargs=None, pad=None, indicate_y_outliers=None,
                                pl_kwargs=None,
                                xlims=None, force_xlims=False, ylims=None,
                                rms_kwargs=None,
                                legend_kwargs=None,
                                show_datasetnames=True,
                                suptitle_kwargs=None,
                                show_title_labels_ticklabels=None,
                                LC_fact=1.,
                                LC_unit=None,
                                fontsize=AandA_fontsize,
                                fig=None, 
                                gs=None,
                                ):
    """Produce a clean LC plot.

    Arguments
    ---------
    post_instance       : Posterior instance
    df_fittedval        : DataFrame
        Dataframe containing the parameter estimates (index=Parameter_fullname, columns=[value, sigma-, sigma+] )
    datasim_kwargs : dict
        Dictionary of keyword arguments for the datasimulator.
    planets             : list_of_str or None
        List of the names of the planets for which you want a phase pholded curve. If None all planets are used
    periods             : list of floats
        Period at which you want to phase fold (which are not planet orbital periods)
    periods_remove_or_add_dict : dict of dict
        Dictionary which keys the should be elements of periods.
        The values associated to each period should be a dictionary with up to two keys 'add_dict' and 'remove_dict'.
        The value associated with these two keys will be passed as the add_dict and remove_dict to the compute_and_plot_model
        if you want to add or remove components to the data when phase-folding at the given period.
    datasetnames        : list of String
        List providing the datasets to load and use
    row4datasetname    : dict of int
        Dictionary saying which dataset to plot on which row. The format is:
        {"<dataset_name>": <int giving the row index starting at 0>, ...}
    datasetnameformodel4row : list of str
        List saying which datasetmodel to use to compute the oversampled model of each row
    npt_model           : int
        Number of points used to simulated the model
    remove1             : bool
        If True remove one to get an out of transit level of 0 instead of 1.
    remove_inst_var  : bool (Def: True)
        If True remove the instrumental variations. If there is contamination, you should always have
        remove_inst_var and remove contamination to True, inst_var depends strongly in contamination, so any other
        thing would not make sense.
    remove_decorrelation    : bool
        It True remove the decorrelation model
    remove_contamination    : bool
        It True the contamination of the light curve is removed. If there is contamination, you should always have
        remove_inst_var and remove contamination to True, inst_var depends strongly in contamination, so any other
        thing would not make sense.

    remove_GP_data           : Boolean
        If True the GP model is remove from the data for the plot.
    remove_GP_residual       : Boolean
        If True the GP model is remove from the residuals for the plot.
    LC_fact             : float
        Factor to apply to the LC (ignore if remove1 is False)
    show_time_from_tic : bool
        If True than the phase folded light curve are show as a function of the time from the mid transit time.
    time_fact           : float
        If show_time_from_tic is True, than the time from mid transit is expressed in the same unit than the period
        by defaults. You can provide a factor here that will be applied to the times.
    time_unit           : str
        If show_time_from_tic is True, than you can provide here the unit in which the time from mid transit
        is expressed (knowing that time_fact is applied)
    exptime_bin         : float
        Width of the bins used for the binning the unit of this depends on the value of show_time_from_tic.
        If show_time_from_tic is True, it's a time unit otherwise the unit is orbital phase.
        If it's a time unit than the unit depend on the unit of the data after time_fact is applied.
        For example if the time unit of the data is days and time_fact=24, the unit of exptime_bin is hours.
    binning_stat        : str
        Statitical method used to compute the binned value. Can be "mean" or "median". This is passed to the
        statistic argument of scipy.stats.binned_statistic
    supersamp_bin_model : int
        Supersampling factor for the binned model.
    show_binned_model   : bool
        If True the binned model is shown.
    sharey        : bool
    create_axes_kwargs : dict
        keys are 'main_gridspec', 'add_axeswithsharex', 'gs_from_sps'.
        Values are dict that will be passed to the functions creating the different axes.
        'main_gridspec' is passed (**gridspecs_kwargs['main_gridspec']) to the GridSpec function used
            to divide the figure into the different rows
        'add_axeswithsharex', 'gs_from_sps' are passed as arguments of the same name to the function
            add_twoaxeswithsharex_perplanet
    pad                 : Iterable of 2 floats (Def: (0.1, 0.1))
                Define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
    indicate_y_outliers: boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
    fontsize : Int specifiying the fontsize
    pl_kwargs    : dict
        Dictionary with keys a dataset name (ex: "LC_HD209458_CHEOPS_0") or "model" or "binned_data" and values
        a dictionary that will be passed as keyword arguments associated the plotting functions.
        You can also add a 'jitter' key with value a dictionary that will contain the changes that you
        want to make for the update error bars due to potential jitter.
    xlims       : dict
    force_xlims : bool
        By default, the maximum xlims is the extrema of the data. So if the user provides larger xlims,
        the actual xlims will be reduced. This will not happen if you set force_xlims to True
    ylims       : dict
    rms_kwargs  : dict
        keys are:
            'do'            : bool
                (Default: True) Show the rms in between the data and residuals axes
            'rms_format'    :
                (Default: '.0f') Format that will be used to format the rms values
    legend_kwargs  : dict
    show_datasetnames  : bool
        If True, show the datasetnames in the corner of the plots
    suptitle_kwargs : dict
        Dictionary which defines the properties of the suptitle. See docstring of do_suptitle for details
    show_title_labels_ticklabels : dict of bool
        Defines whether or not to show the title, xlabel, ylabel, xticklabels, yticklabels.
    LC_unit        : str or None
        String giving the unit of the LCs
    fig            : Figure
        Figure instance
    gs             : GridSpec
        If provided should have been made from fig, meaning that it doesn't make sense to provide gs without providing fig.
        It should be a Gridspec with ncols=1 and nrows according to row4datasetname
    """
    y_name = "$\Delta$F / F" if remove1 else "(F + $\Delta$F) / F"
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [True, True, remove_contamination, True, remove1]
                            ):
        remove_dict_model[key] = default
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP_model", "decorrelation_likelihood", "decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [True, True, True, True, remove_contamination, True, remove1]
                            ):
        remove_dict_data[key] = default
    remove_dict_data_err = OrderedDict()
    for key in ["contamination", ]:
        remove_dict_data_err[key] = remove_dict_data[key]
    kwargs_compute_model_4_key_model = {"model": {'include_gp_model': True, "remove_dict": remove_dict_model,
                                                  'add_dict': dict_model_false
                                                  },
                                        "data": {'include_gp_model': True, "remove_dict": remove_dict_data,
                                                 'add_dict': dict_model_false
                                                 },
                                        "data_err": {'include_gp_model': False, "remove_dict": remove_dict_data_err,
                                                     'add_dict': dict_model_false
                                                     },
                                        }
    return create_phasefolded_plots(post_instance=post_instance, df_fittedval=df_fittedval,
                                    compute_raw_models_func=compute_raw_models,
                                    remove_add_model_components_func=remove_add_model_components,
                                    kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                    l_valid_model=l_valid_model,
                                    y_name=y_name, inst_cat='LC', d_name_component_removed_to_print=d_name_component_removed_to_print,
                                    datasim_kwargs=datasim_kwargs, planets=planets, periods=periods,
                                    periods_remove_or_add_dict=periods_remove_or_add_dict,
                                    datasetnames=datasetnames, row4datasetname=row4datasetname,
                                    datasetnameformodel4row=datasetnameformodel4row,
                                    npt_model=npt_model, phasefold_central_phase=phasefold_central_phase,
                                    amplitude_fact=LC_fact, show_time_from_tic=show_time_from_tic, time_fact=time_fact,
                                    time_unit=time_unit, exptime_bin=exptime_bin, binning_stat=binning_stat,
                                    supersamp_bin_model=supersamp_bin_model, show_binned_model=show_binned_model,
                                    one_binning_per_row=one_binning_per_row,
                                    sharey=sharey, create_axes_kwargs=create_axes_kwargs, pad=pad, indicate_y_outliers=indicate_y_outliers,
                                    pl_kwargs=pl_kwargs, xlims=xlims, force_xlims=force_xlims, ylims=ylims,
                                    rms_kwargs=rms_kwargs, legend_kwargs=legend_kwargs, show_datasetnames=show_datasetnames,
                                    suptitle_kwargs=suptitle_kwargs, show_title_labels_ticklabels=show_title_labels_ticklabels, 
                                    unit=LC_unit, fontsize=fontsize,
                                    get_key_compute_model_func=get_key_compute_model,
                                    is_valid_model_available_func=is_valid_model_available,
                                    fig=fig, gs=gs,
                                    )


def create_LC_TSNGLSP_plots(fig, post_instance, df_fittedval, datasim_kwargs=None,
                            datasetnames=None,
                            remove_dict=None,
                            kwargs_compute_model_4_key_model=None,
                            show_dict=None, datasetnames4model4row=None,
                            TS_kwargs=None, GLSP_kwargs=None,
                            create_axes_kwargs=None,
                            suptitle_kwargs=None,
                            LC_fact=1e6, LC_unit="ppm", fontsize=AandA_fontsize
                            ):
    """Produce clean LC time series and generalized Lomb-Scargle plots of a system.

    Arguments
    ---------
    fig           :
        Figure instance (provided by the styler)
    post_instance : Posterior instance
    df_fittedval  : DataFrame
        Dataframe containing the parameter estimates (index=Parameter_fullname, columns=[value, sigma-, sigma+] )
    datasim_kwargs : dict
        Dictionary of keyword arguments for the datasimulator.
    datasetnames  : list of String
        List providing the datasets to load and use
    remove_dict   : dict of bool
    TS_kwargs     : None or dict
            - 'do': boolean (Def: True)
            - 'row4datasetname'   : dict of int
                Dictionary saying which dataset to plot on which row. The format is:
                {"<dataset_name>": <int giving the row index starting at 0>, ...}
            - 'npt_model': int (Def: 1000) giving the number of points to use for the model
            - 'extra_dt_model': float (Def: 0)
                Specify the extra time that for which you want to compute the model before and after the
                data.
            - 't_lims': None or Iterable of 2 float or dict of Iterable of 2 float (Def: None)
                This gives the beginning and end time for the zoom. If there is more than one row (see row4datasetname).
                You must provide a dictionary with the following format:
                {"<int giving the row index>": <Iterable of two float providing the min and max for the time axis>, ...}
            - 't_lims_zoom': None or Iterable of 2 float or dict of Iterable of 2 float (Def: None)
                If provided a zoom on the right of the main plot will be drawn. This gives the beginning
                and end time for the zoom. If there is more than one row (see row4datasetname).
                You must provide a dictionary with the following format:
                {"<int giving the row index>": <Iterable of two float providing the min and max for the zoom>, ...}
            - 't_unit': str (Def: days)
                String that is going to be used to give the unit (and reference system) of the time.
            - 'pl_kwargs': dict
                Dictionary with keys a dataset name (ex: "LC_HD209458_CHEOPS_0") or "model" or "GP"
                and values a dictionary that will be passed as keyword arguments associated the plotting functions.
                For the dictionaries corresponding to a dataset, You can also add a 'jitter' key with value
                a dictionary that will contain the changes that you want to make for the update error bars
                due to potential jitter.
                You can also add a 'binned' key with value a dictionary that will contain the changes that you
                want to make for ploting the binned data and residuals
                You can use the 'show_error' and 'show_binned_error' key with value True or False to specify if you want
                the error bars of the data and binned data to be plotted to be plotted.
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
            - 'show_inst_var': boolean (Def: True),
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
    LC_fact       : float
        Factor to apply to the LC
    LC_unit        : str
        String giving the unit of the LCs

    Returns
    -------
    dico_load       : dict  
        Output of the function core_compute_load.load_datasets_and_models
    computed_models : dict
        Outputs of the compute_and_plot_model function calls
    """
    y_name = "$\Delta$F / F" if remove_dict.get("1", True) else "(F + $\Delta$F) / F"
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [False, False, False, False, True]
                            ):
        remove_dict_model[key] = remove_dict.get(key, default)
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP_model", "decorrelation_likelihood", "decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [False, False, False, False, False, False, True]
                            ):
        remove_dict_data[key] = remove_dict.get(key, default)
    remove_dict_data_err = OrderedDict()
    for key in ["contamination", ]:
        remove_dict_data_err[key] = remove_dict_data[key]
    kwargs_compute_model_4_key_model_user = kwargs_compute_model_4_key_model if kwargs_compute_model_4_key_model is not None else {}
    kwargs_compute_model_4_key_model = {"model": {'include_gp_model': True, "remove_dict": remove_dict_model,
                                                  'add_dict': dict_model_false
                                                  },
                                        "data": {'include_gp_model': True, "remove_dict": remove_dict_data,
                                                 'add_dict': dict_model_false
                                                 },
                                        "data_err": {'include_gp_model': False, "remove_dict": remove_dict_data_err,
                                                     'add_dict': dict_model_false
                                                     },
                                        }
    kwargs_compute_model_4_key_model.update(kwargs_compute_model_4_key_model_user)
    return create_TSNGLSP_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                                y_name=y_name, inst_cat='LC',
                                compute_raw_models_func=compute_raw_models,
                                remove_add_model_components_func=remove_add_model_components,
                                kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                l_valid_model=l_valid_model,
                                d_name_component_removed_to_print=d_name_component_removed_to_print,
                                show_dict=show_dict, l_model_1_per_row=['model', 'stellar_var', 'GP'],
                                datasetnames4model4row=datasetnames4model4row,
                                datasim_kwargs=datasim_kwargs,
                                datasetnames=datasetnames,
                                amplitude_fact=LC_fact, unit=LC_unit,
                                create_axes_kwargs=create_axes_kwargs,
                                TS_kwargs=TS_kwargs,
                                GLSP_kwargs=GLSP_kwargs,
                                suptitle_kwargs=suptitle_kwargs,
                                fontsize=fontsize,
                                get_key_compute_model_func=get_key_compute_model,
                                is_valid_model_available_func=is_valid_model_available,
                                )


def remove_add_model_components(model, model_wGP, remove_dict, add_dict, extension, extension_raw, models, amplitude_fact):
    """
    """
    # Remove components if needed
    for key, do in remove_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['1', 'stellar_var', 'inst_var', 'decorr_add_2_totalflux', 'decorrelation_likelihood', 'GP_model']:
                model -= models[key + extension + extension_raw]
                if (model_wGP is not None) and (key != 'GP_model'):
                    model_wGP -= models[key + extension + extension_raw]
            elif key in ['contamination', 'decorr_multiply_2_totalflux']:
                model /= models[key + extension + extension_raw] / amplitude_fact
                if (model_wGP is not None) and (key != 'GP_model'):
                    model_wGP /= models[key + extension + extension_raw] / amplitude_fact
            # elif key in ['1', ]:
            #     model -= 1
            #     if (model_wGP is not None) and (key != 'GP_model'):
            #         model_wGP -= 1
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")
    # Add components if needed
    for key, do in add_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['1', 'stellar_var', 'inst_var', 'decorr_add_2_totalflux', 'decorrelation_likelihood', 'GP_model']:
                model += models[key + extension + extension_raw]
                if (model_wGP is not None) and (key != 'GP_model'):
                    model_wGP += models[key + extension + extension_raw]
            elif key in ['contamination', 'decorr_multiply_2_totalflux']:
                model *= models[key + extension + extension_raw] / amplitude_fact
                if (model_wGP is not None) and (key != 'GP_model'):
                    model_wGP *= models[key + extension + extension_raw] / amplitude_fact
            # elif key in ['1', ]:
            #     model += 1
            #     if (model_wGP is not None) and (key != 'GP_model'):
            #         model_wGP += 1
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")

    return model, model_wGP


def get_key_compute_model(key_model):
    """
    """
    if key_model == "contamination":
        key_compute_model = "contam"
    else:
        key_compute_model = get_key_compute_model_core(key_model=key_model)
    return key_compute_model


def is_valid_model_available(key_model, datasetname, post_instance):
    """
    """
    if key_model == "stellar_var":
        star = post_instance.model.stars[list(post_instance.model.stars.keys())[0]]
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        return ((star.get_dico_config_polymodel(inst_cat=inst_mod.instrument.category, notexist_ok=True, return_None_if_notexist=True) is not None) and
                star.get_dico_config_polymodel(inst_cat=inst_mod.instrument.category, notexist_ok=True, return_None_if_notexist=True)["do"]
                )
    elif key_model == "inst_var":
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        return ((inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True) is not None) and
                inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True)["do"]
                )
    elif key_model == "contamination":
        return True
    else:
        return is_valid_model_available_core(key_model=key_model, datasetname=datasetname, post_instance=post_instance)


def compute_raw_models(tsim, key_model, l_valid_model, datasetname, post_instance,
                       df_fittedval, datasim_kwargs, include_gp_model, exptime, supersamp,
                       get_key_compute_model_func=get_key_compute_model,
                       is_valid_model_available_func=is_valid_model_available,
                       kwargs_is_valid_model_available=None,
                       kwargs_get_key_compute_model=None,
                       ):
    """
    """
    if key_model == "1":
        model = ones_like(tsim)
        model_wGP = gp_pred = gp_pred_var = None
        return model, model_wGP, gp_pred, gp_pred_var
    else:
        return compute_raw_models_core(tsim=tsim, key_model=key_model, l_valid_model=l_valid_model,
                                       datasetname=datasetname, post_instance=post_instance,
                                       df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs, include_gp_model=include_gp_model,
                                       exptime=exptime, supersamp=supersamp, get_key_compute_model_func=get_key_compute_model_func,
                                       is_valid_model_available_func=is_valid_model_available_func,
                                       kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                       )

# def load_datasets_and_models_LC(datasetnames, post_instance, datasim_kwargs, df_fittedval,
#                                 amplitude_fact, remove_dict, add_dict, remove_dict_def, add_dict_def
#                                 ):
#     """Load the dataset and models for later use by the other two function
#     """
#     remove_dict_user = remove_dict
#     remove_dict = copy(remove_dict_def)
#     remove_dict.update(remove_dict_user)
#
#     add_dict_user = add_dict
#     add_dict = copy(add_dict_def)
#     add_dict.update(add_dict_user)
#
#     dico_datasets = {}
#     dico_kwargs = {}
#     dico_nb_dstperinsts = defaultdict(lambda: 0)
#     times = {}
#     datas = {}
#     data_errs = {}
#     data_err_jitters = {}
#     data_err_worwojitters = {}
#     has_jitters = {}
#     dico_jitters = {}
#     models = {}
#     gp_preds = {}
#     gp_pred_vars = {}
#     inst_vars = {}
#     stellar_vars = {}
#     decorrs = {}
#     decorr_likelihoods = {}
#     contams = {}
#     residuals = {}
#     for datasetname in datasetnames:
#         ##########################################
#         # Load Data and instrument and noise model
#         ##########################################
#         dico_datasets[datasetname] = post_instance.dataset_db[datasetname]
#         dico_kwargs[datasetname] = dico_datasets[datasetname].get_all_datasetkwargs()
#         times[datasetname] = dico_datasets[datasetname].get_datasetkwarg("time")
#         datas[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data")
#         data_errs[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data_err")
#         filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
#         inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
#         inst_mod = post_instance.model.instruments[inst_mod_fullname]
#         noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
#         dico_nb_dstperinsts[filename_info["inst_name"]] += 1
#
#         ##############################################
#         # Apply the jitter to the data error if needed
#         ##############################################
#         dico_jitters[datasetname] = {}
#         data_err_jitters[datasetname] = dico_datasets[datasetname].get_datasetkwarg("data_err")
#         has_jitters[datasetname] = noise_model.has_jitter
#         if has_jitters[datasetname]:
#             dico_jitters[datasetname]["type"] = noise_model.jitter_type
#             if inst_mod.jitter.free:
#                 dico_jitters[datasetname]["value"] = df_fittedval.loc[inst_mod.jitter.full_name]["value"]
#             else:
#                 dico_jitters[datasetname]["value"] = inst_mod.jitter.value
#             if dico_jitters[datasetname]["type"] == "multi":
#                 data_err_jitters[datasetname] = np.sqrt(apply_jitter_multi(data_err_jitters[datasetname], dico_jitters[datasetname]["value"]))
#             elif dico_jitters[datasetname]["type"] == "add":
#                 data_err_jitters[datasetname] = np.sqrt(apply_jitter_add(data_err_jitters[datasetname], dico_jitters[datasetname]["value"]))
#             else:
#                 raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
#             data_err_worwojitters[datasetname] = data_err_jitters[datasetname].copy()
#         else:
#             data_err_worwojitters[datasetname] = data_errs[datasetname].copy()
#
#         ###############################################################################
#         # Compute the stellar variations (stellar_vars) to later remove from the data
#         ###############################################################################
#         # For each dataset
#         # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
#         # and remove drift
#         star = post_instance.model.stars[list(post_instance.model.stars.keys())[0]]
#         if (star.get_dico_config_polymodel(inst_cat="LC", notexist_ok=True, return_None_if_notexist=True) is not None) and (star.get_dico_config_polymodel(inst_cat="LC", notexist_ok=True, return_None_if_notexist=True)["do"]):
#             model_stellar_vars = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                                              param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
#                                                              key_obj="stellar_var",
#                                                              datasim_kwargs=datasim_kwargs, include_gp=False
#                                                              )
#
#             if model_stellar_vars is not None:
#                 stellar_vars[datasetname] = model_stellar_vars
#
#         ###############################################################################
#         # Compute the instrumental variations (inst_vars) to later remove from the data
#         ###############################################################################
#         # For each dataset
#         # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
#         # and remove drift
#         if (inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True) is not None) and (inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True)["do"]):
#             model_inst_var = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                                          param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
#                                                          key_obj="inst_var",
#                                                          datasim_kwargs=datasim_kwargs, include_gp=False
#                                                          )
#             if model_inst_var is not None:
#                 inst_vars[datasetname] = model_inst_var
#
#         #########################################################################
#         # Compute the decorrelation models (decorr) to later remove from the data
#         #########################################################################
#         if post_instance.model.instcat_models["LC"].decorrelation_model_config[inst_mod_fullname]["do"]:
#             model_decorr = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                                        param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
#                                                        key_obj="decorr",
#                                                        datasim_kwargs=datasim_kwargs, include_gp=False
#                                                        )
#             decorrs[datasetname] = {}
#             for model_part in post_instance.model.instcat_models["LC"].decorrelation_model_config[inst_mod_fullname]['what to decorrelate']:
#                 if model_part == "add_2_totalflux":
#                     model_decorr = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                                                param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
#                                                                key_obj="decorr",
#                                                                datasim_kwargs=datasim_kwargs, include_gp=False
#                                                                )
#                     decorrs[datasetname][model_part] = model_decorr['add_2_totalflux']
#                 else:
#                     logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
#
#         #########################################################################
#         # Compute the contamination models (contam) to later remove from the data
#         #########################################################################
#         model_contam = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                                    param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
#                                                    key_obj="contam",
#                                                    datasim_kwargs=datasim_kwargs, include_gp=False
#                                                    )
#         if model_contam is not None:
#             contams[datasetname] = model_contam
#
#         #######################################
#         # Compute the models and GP predictions
#         #######################################
#         (model, model_wGP, gp_pred, gp_pred_var
#          ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
#                                          param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
#                                          key_obj=key_whole, datasim_kwargs=datasim_kwargs, include_gp=True)
#         if model_wGP is not None:
#             gp_preds[datasetname] = gp_pred
#             gp_pred_vars[datasetname] = gp_pred_var
#
#         if (model_wGP is not None) and not(remove_dict['GP_dataNmodel']):
#             models[datasetname] = model_wGP
#         else:
#             models[datasetname] = model
#
#         ###################################################
#         # Compute the likelihood decorrelation contribution
#         ###################################################
#         if f"{datasetname}_decorr_like" in post_instance.datasimulators.dataset_db:  # remove_dict['decorrelation_likelihood'] and
#             datasim_docfunc_decorr_like = post_instance.datasimulators.dataset_db[f"{datasetname}_decorr_like"]
#             p_vect = df_fittedval["value"][datasim_docfunc_decorr_like.param_model_names_list].values
#             decorr_likelihoods[datasetname] = datasim_docfunc_decorr_like.function(p_vect)
#
#         #######################
#         # Compute the residuals
#         #######################
#         if (model_wGP is not None) and remove_dict['GP_residual']:
#             residuals[datasetname] = datas[datasetname] - model_wGP
#         else:
#             residuals[datasetname] = datas[datasetname] - model
#
#         ################################################################################
#         # Remove GP (if needed)
#         ################################################################################
#         if (model_wGP is not None) and remove_dict['GP_dataNmodel']:
#             datas[datasetname] -= gp_pred
#
#         ################################################################################
#         # Remove/Add stellar_vars (if needed)
#         ################################################################################
#         if datasetname in stellar_vars:
#             if remove_dict['stellar_var']:
#                 datas[datasetname] -= stellar_vars[datasetname]
#                 models[datasetname] -= stellar_vars[datasetname]
#             if add_dict['stellar_var']:
#                 datas[datasetname] += stellar_vars[datasetname]
#                 models[datasetname] += stellar_vars[datasetname]
#
#         ################################################################################
#         # Remove/Add inst_vars (if needed)
#         ################################################################################
#         if datasetname in inst_vars:
#             if remove_dict['inst_var']:
#                 datas[datasetname] -= inst_vars[datasetname]
#                 models[datasetname] -= inst_vars[datasetname]
#             if add_dict['inst_var']:
#                 datas[datasetname] += inst_vars[datasetname]
#                 models[datasetname] += inst_vars[datasetname]
#
#         ################################################################################
#         # Remove/Add decorrelation (if needed)
#         ################################################################################
#         if datasetname in decorrs:
#             for model_part in decorrs[datasetname]:
#                 if model_part == "add_2_totalflux":
#                     if remove_dict['decorrelation']:
#                         datas[datasetname] -= decorrs[datasetname]['add_2_totalflux']
#                         models[datasetname] -= decorrs[datasetname]['add_2_totalflux']
#                     if add_dict['decorrelation']:
#                         datas[datasetname] += decorrs[datasetname]['add_2_totalflux']
#                         models[datasetname] += decorrs[datasetname]['add_2_totalflux']
#                 else:
#                     logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
#
#         ################################################################################
#         # Remove/Add decorrelation likelihood (if needed)
#         ################################################################################
#         if datasetname in decorr_likelihoods:
#             if remove_dict['decorrelation_likelihood']:
#                 datas[datasetname] -= decorr_likelihoods[datasetname]
#             if add_dict['decorrelation_likelihood']:
#                 datas[datasetname] += decorr_likelihoods[datasetname]
#
#         ################################################################################
#         # Remove contamination (if needed)
#         ################################################################################
#         if datasetname in contams:
#             if remove_dict['contamination']:
#                 datas[datasetname] /= contams[datasetname]
#                 models[datasetname] /= contams[datasetname]
#             if add_dict['contamination']:
#                 datas[datasetname] *= contams[datasetname]
#                 models[datasetname] *= contams[datasetname]
#
#         ################################################################################
#         # Remove 1 (if needed)
#         ################################################################################
#         if remove_dict['1']:
#             datas[datasetname] -= 1
#             models[datasetname] -= 1
#         if add_dict['1']:
#             datas[datasetname] += 1
#             models[datasetname] += 1
#
#         ################################################################################
#         # Apply LC_fact
#         ################################################################################
#         datas[datasetname] *= amplitude_fact
#         data_errs[datasetname] *= amplitude_fact
#         data_err_worwojitters[datasetname] *= amplitude_fact
#         residuals[datasetname] *= amplitude_fact
#         models[datasetname] *= amplitude_fact
#         if model_wGP is not None:
#             gp_preds[datasetname] *= amplitude_fact
#             gp_pred_vars[datasetname] *= amplitude_fact**2
#         if has_jitters[datasetname]:
#             dico_jitters[datasetname]["value"] *= amplitude_fact
#             data_err_jitters[datasetname] *= amplitude_fact
#
#     d_remove_from_model = {'stellar_var': 'stellar_vars', 'inst_var': 'inst_vars', 'decorrelation': 'decorrs', 'contamination': 'contams'}
#     d_remove_from_data = {'stellar_var': 'stellar_vars', 'inst_var': 'inst_vars', 'decorrelation': 'decorrs', 'decorrelation_likelihood': 'decorr_likelihoods',
#                           'contamination': 'contams'
#                           }
#
#     return ({'dico_datasets': dico_datasets, 'dico_kwargs': dico_kwargs, 'dico_nb_dstperinsts': dico_nb_dstperinsts,
#              'times': times, 'datas': datas, 'data_errs': data_errs, 'data_err_jitters': data_err_jitters,
#              'data_err_worwojitters': data_err_worwojitters, 'has_jitters': has_jitters, 'dico_jitters': dico_jitters,
#              'models': models, 'gp_preds': gp_preds, 'gp_pred_vars': gp_pred_vars, 'inst_vars': inst_vars,
#              'stellar_vars': stellar_vars, 'decorrs': decorrs, 'decorr_likelihoods': decorr_likelihoods,
#              'contams': contams, 'residuals': residuals
#              },
#             d_remove_from_model, d_remove_from_data, remove_dict, add_dict,
#             )


# def compute_and_plot_model_LC(datasetname,
#                               post_instance, df_fittedval, key_compute_model,
#                               include_gp_model, datasim_kwargs,
#                               remove_dict, add_dict, amplitude_fact,
#                               tsim, fact_tsim_to_xsim=None,
#                               exptime_bin=None, supersamp_bin_model=None,
#                               plot=True, ax=None, pl_kwarg=None, key_pl_kwarg=None, show_binned_model=True
#                               ):
#     """
#     """
#     remove_dict_user = remove_dict
#     remove_dict = copy({'1': False, 'contamination': False, 'stellar_var': False, 'inst_var': False, 'decorrelation': False})
#     remove_dict.update(remove_dict_user)
#
#     add_dict_user = add_dict
#     add_dict = copy({'1': False, 'contamination': False, 'stellar_var': False, 'inst_var': False, 'decorrelation': False})
#     add_dict.update(add_dict_user)
#
#     # Define the time vector tsim at which the models will be evaluated
#     # tsim = np.linspace(*tlims_model, npt_model)
#     # # Define the x vector xsim (corresponding to tsim) at which the models will be plotted
#     # if xlims_model is not None:
#     #     xsim = np.linspace(*xlims_model, npt_model)
#     # else:
#     #     xsim = tsim
#
#     if exptime_bin is None:
#         exptime_bin = 0.
#
#     if fact_tsim_to_xsim is None:
#         fact_tsim_to_xsim = 1.
#
#     xsim = tsim * fact_tsim_to_xsim
#
#     key_pl_kwarg_user = key_pl_kwarg
#     models = {}
#     for binned in [False, True]:
#         if binned:
#             if show_binned_model and (exptime_bin > 0.):
#                 exptime = exptime_bin / fact_tsim_to_xsim
#                 extension = '_binned'
#             else:
#                 continue
#         else:
#             exptime = 0.
#             key_pl_kwarg = key_pl_kwarg_user
#             extension = ''
#
#         # Compute the model
#         if include_gp_model:
#             (model, model_wGP, gp_pred, gp_pred_var
#              ) = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                              param=df_fittedval["value"].values,
#                                              l_param_name=list(df_fittedval.index),
#                                              key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
#                                              include_gp=include_gp_model,
#                                              supersamp=supersamp_bin_model, exptime=exptime
#                                              )
#         else:
#             model = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                 param=df_fittedval["value"].values,
#                                                 l_param_name=list(df_fittedval.index),
#                                                 key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
#                                                 include_gp=include_gp_model,
#                                                 supersamp=supersamp_bin_model, exptime=exptime
#                                                 )
#             model_wGP = gp_pred = gp_pred_var = None
#
#         if model is None:
#             return models, pl_kwarg
#
#         # Remove/Add contamination if needed
#         if remove_dict['1']:
#             model -= 1
#             if model_wGP is not None:
#                 model_wGP -= 1
#         if add_dict['1']:
#             model += 1
#             if model_wGP is not None:
#                 model_wGP += 1
#         # Remove/Add contamination if needed
#         if (remove_dict['contamination'] or add_dict['contamination']) and (datasetname in dico_output_load['contams']):
#             model_contam = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                        param=df_fittedval["value"].values,
#                                                        l_param_name=list(df_fittedval.index),
#                                                        key_obj="contam", datasim_kwargs=datasim_kwargs,
#                                                        include_gp=False,
#                                                        supersamp=supersamp_bin_model, exptime=exptime
#                                                        )
#             if model_contam is not None:
#                 if remove_dict['contamination']:
#                     model /= model_contam
#                     if model_wGP is not None:
#                         model_wGP /= model_contam
#                 if add_dict['contamination']:
#                     model *= model_contam
#                     if model_wGP is not None:
#                         model_wGP *= model_contam
#         # Remove/Add stellar_var if needed
#         if (remove_dict['stellar_var'] or add_dict['stellar_var']) and (datasetname in dico_output_load['stellar_vars']):
#             model_stellarvar = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                            param=df_fittedval["value"].values,
#                                                            l_param_name=list(df_fittedval.index),
#                                                            key_obj="stellar_var",
#                                                            datasim_kwargs=datasim_kwargs,
#                                                            include_gp=False,
#                                                            supersamp=supersamp_bin_model, exptime=exptime
#                                                            )
#             if remove_dict['stellar_var']:
#                 model -= model_stellarvar
#                 if model_wGP is not None:
#                     model_wGP -= model_stellarvar
#             if add_dict['stellar_var']:
#                 model += model_stellarvar
#                 if model_wGP is not None:
#                     model_wGP += model_stellarvar
#         # Remove/Add inst_var if needed
#         if (remove_dict['inst_var'] or add_dict['inst_var']) and (datasetname in dico_output_load['inst_vars']):
#             model_instvar = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                         param=df_fittedval["value"].values,
#                                                         l_param_name=list(df_fittedval.index),
#                                                         key_obj="inst_var", datasim_kwargs=datasim_kwargs,
#                                                         include_gp=False,
#                                                         supersamp=supersamp_bin_model, exptime=exptime
#                                                         )
#             if remove_dict['inst_var']:
#                 model -= model_instvar
#                 if model_wGP is not None:
#                     model_wGP -= model_instvar
#             if add_dict['inst_var']:
#                 model += model_instvar
#                 if model_wGP is not None:
#                     model_wGP += model_instvar
#         # Remove/Add decorrelation if needed
#         if (remove_dict['decorrelation'] or add_dict['decorrelation']) and (datasetname in dico_output_load['decorrs']):
#             model_decorr = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                        param=df_fittedval["value"].values,
#                                                        l_param_name=list(df_fittedval.index),
#                                                        key_obj="decorr", datasim_kwargs=datasim_kwargs,
#                                                        include_gp=False,
#                                                        supersamp=supersamp_bin_model, exptime=exptime
#                                                        )
#             for model_part in model_decorr:
#                 if model_part == "add_2_totalflux":
#                     if remove_dict['decorrelation']:
#                         model -= model_decorr['add_2_totalflux']
#                         if model_wGP is not None:
#                             model_wGP -= model_decorr['add_2_totalflux']
#                     if add_dict['decorrelation']:
#                         model += model_decorr['add_2_totalflux']
#                         if model_wGP is not None:
#                             model_wGP += model_decorr['add_2_totalflux']
#                 else:
#                     logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
#         # Multiply by LC fact
#         model *= amplitude_fact
#         models[key_compute_model + extension] = model
#         if model_wGP is not None:
#             model_wGP *= amplitude_fact
#             gp_pred *= amplitude_fact
#             gp_pred_var *= amplitude_fact**2
#             models['model_wGP' + extension] = model_wGP
#             models['GP' + extension] = gp_pred
#             models['GP_var' + extension] = gp_pred_var
#
#         # Plot the model
#         if plot:
#             key_pl_kwarg = key_pl_kwarg_user + extension
#             ebconts_lines_labels_model = ax.errorbar(xsim, model, **pl_kwarg[datasetname][key_pl_kwarg])
#             if not("color" in pl_kwarg[datasetname][key_pl_kwarg]):
#                 pl_kwarg[datasetname][key_pl_kwarg]["color"] = ebconts_lines_labels_model[0].get_color()
#             if not("alpha" in pl_kwarg[datasetname][key_pl_kwarg]):
#                 pl_kwarg[datasetname][key_pl_kwarg]["alpha"] = ebconts_lines_labels_model[0].get_alpha()
#             # Plot the GP
#             if model_wGP is not None:
#                 key_GP = "GP" + extension
#                 key_GP_err = "GP_err" + extension
#                 if not("color" in pl_kwarg[datasetname][key_GP]):
#                     pl_kwarg[datasetname][key_GP]["color"] = pl_kwarg[datasetname][key_pl_kwarg]["color"]
#                 if not("color" in pl_kwarg[datasetname]["GP_err"]):
#                     pl_kwarg[datasetname][key_GP_err]["color"] = pl_kwarg[datasetname][key_pl_kwarg]["color"]
#                 if not("alpha" in pl_kwarg[datasetname]["GP"]):
#                     pl_kwarg[datasetname][key_GP]["alpha"] = pl_kwarg[datasetname][key_pl_kwarg]["alpha"]
#                 if not("alpha" in pl_kwarg[datasetname]["GP_err"]):
#                     pl_kwarg[datasetname][key_GP_err]["alpha"] = pl_kwarg[datasetname][key_pl_kwarg]["alpha"] / 3
#                 if not(remove_dict["GP_dataNmodel"]):
#                     pl_kwarg[datasetname][key_GP]["label"] = pl_kwarg[datasetname][key_pl_kwarg]['label'] + " + GP"
#                     _ = ax.errorbar(tsim, model_wGP, **pl_kwarg[datasetname][key_GP])
#                     _ = ax.fill_between(tsim, model_wGP - np.sqrt(gp_pred_var), model_wGP + np.sqrt(gp_pred_var),
#                                         **pl_kwarg[datasetname][key_GP_err],
#                                         )
#                 else:
#                     _ = ax.errorbar(tsim, gp_pred, **pl_kwarg[datasetname][key_GP])
#                     _ = ax.fill_between(tsim, gp_pred - np.sqrt(gp_pred_var), gp_pred + np.sqrt(gp_pred_var),
#                                         **pl_kwarg[datasetname][key_GP_err]
#                                         )
#     return models, pl_kwarg


# def create_LC_TSNGLSP_plots(fig, post_instance, df_fittedval, datasim_kwargs=None, planets=None, star_name="A",
#                             datasetnames=None,
#                             remove1=True, remove_inst_var=False,
#                             remove_decorrelation=True, remove_decorrelation_likelihood=True,
#                             remove_contamination=False,
#                             fig_param=None, TS_kwargs=None, GLSP_kwargs=None,
#                             suptitle_kwargs=None,
#                             LC_fact=1e6, LC_unit="ppm",
#                             ):
#     """Produce clean LC time series and generalized Lomb-Scargle plots of a system.
#
#     Arguments
#     ---------
#     fig           :
#         Figure instance (provided by the styler)
#     post_instance : Posterior instance
#     df_fittedval  : DataFrame
#         Dataframe containing the parameter estimates (index=Parameter_fullname, columns=[value, sigma-, sigma+] )
#     datasim_kwargs : dict
#         Dictionary of keyword arguments for the datasimulator.
#     planets : list_of_str or None
#         List of the names of the planets for which you want a phase pholded curve. If None all planets are used
#     star_name     : String
#     datasetnames  : list of String
#         List providing the datasets to load and use
#     fig_param     : dict
#         Dictionary providing keyword arguments for the figure definition and settings. The possible keys are
#             - 'gridspec_kwargs': The content of this entry should be a dictionary which will be passed to
#                 GridSpec (GridSpec(..., **fig_param['gridspec_kwargs'])) instance creation with create the gridspec
#                 separating the TS and GLSP
#             - 'add_axeswithsharex_kw': The content of this entry should be a dictionary which will be
#                 passed to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., add_axeswithsharex_kw=fig_param['add_axeswithsharex_kw'])
#                 function creating two axes data and residuals per planet.
#             - 'fontsize' : Int specifiying the fontsize
#     remove1         : bool
#         If True remove one to get an out of transit level of 0 instead of 1.
#     remove_inst_var  : bool (Def: True)
#         If True remove the instrumental variations
#     remove_decorrelation    : bool
#         If True remove the decorrelation model
#     remove_decorrelation_likelihood    : bool
#         If True remove the decorrelation model
#     remove_contamination    : bool
#         If True remove the contamination model
#     TS_kwargs     : None or dict
#             - 'do': boolean (Def: True)
#             - 'row4datasetname'   : dict of int
#                 Dictionary saying which dataset to plot on which row. The format is:
#                 {"<dataset_name>": <int giving the row index starting at 0>, ...}
#             - 'npt_model': int (Def: 1000) giving the number of points to use for the model
#             - 'extra_dt_model': float (Def: 0)
#                 Specify the extra time that for which you want to compute the model before and after the
#                 data.
#             - 't_lims': None or Iterable of 2 float or dict of Iterable of 2 float (Def: None)
#                 This gives the beginning and end time for the zoom. If there is more than one row (see row4datasetname).
#                 You must provide a dictionary with the following format:
#                 {"<int giving the row index>": <Iterable of two float providing the min and max for the time axis>, ...}
#             - 't_lims_zoom': None or Iterable of 2 float or dict of Iterable of 2 float (Def: None)
#                 If provided a zoom on the right of the main plot will be drawn. This gives the beginning
#                 and end time for the zoom. If there is more than one row (see row4datasetname).
#                 You must provide a dictionary with the following format:
#                 {"<int giving the row index>": <Iterable of two float providing the min and max for the zoom>, ...}
#             - 't_unit': str (Def: days)
#                 String that is going to be used to give the unit (and reference system) of the time.
#             - 'pl_kwargs': dict
#                 Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "GP"
#                 and values a dictionary that will be passed as keyword arguments associated the plotting functions.
#                 For the dictionaries corresponding to a dataset, You can also add a 'jitter' key with value
#                 a dictionary that will contain the changes that you want to make for the update error bars
#                 due to potential jitter.
#                 You can also add a 'binned' key with value a dictionary that will contain the changes that you
#                 want to make for ploting the binned data and residuals
#                 You can use the 'show_error' and 'show_binned_error' key with value True or False to specify if you want
#                 the error bars of the data and binned data to be plotted to be plotted.
#             - 'ylims_data': Define the limits on the data y axis. This override 'pad_data'
#             - 'pad_data': Iterable of 2 floats (Def: (0.1, 0.1))
#                 Define the bottom and top pad to apply for data axes.
#                 Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
#                 allows to provide different pad_data for different planets.
#             - 'ylims_resi': Define the limits on the residuals y axis. This override 'pad_resi'
#             - 'pad_resi': Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
#             - 'indicate_y_outliers_data': boolean. If True, data outliers (outside of the plot) are indicated
#                 by arrows.
#             - 'indicate_y_outliers_resi': boolean. If True, residuals outliers (outside of the plot) are indicated
#                 by arrows.
#             - 'exptime_bin' : float
#                 Exposure time for the binning of data in the same unit that the time of the datasets.
#                 If you don't want to bin put 0.
#             - 'binning_stat' : str
#                 Statitical method used to compute the binned value. Can be "mean" or "median". This is passed to the
#                 statistic argument of scipy.stats.binned_statistic
#             - 'one_binning_per_row' : bool
#                 If true only one binning per row is performed
#             - 'show_title'  : bool
#                 If True, show the titles (of the main and the zoom)
#             - 'legend_kwargs' : dict of dict
#                 keys are 'all' or int providing the row index ('all' applies to all row, but the row index overwrite it)
#                 Values are dict whose keys are:
#                     'do'    : bool
#                         (Default: True) Whether or not to show the legend
#                     other keys are passed to the pyplot.legend function
#             - 'rms_kwargs'  : dict
#                 keys are:
#                     'do'            : bool
#                         (Default: True) Show the rms in between the data and residuals axes
#                     'rms_format'    :
#                         (Default: '.0f') Format that will be used to format the rms values
#             - 'gridspec_kwargs': dict
#                 The content of this entry should be a dictionary which will be passed to
#                 GridSpecFromSubplotSpec (GridSpecFromSubplotSpec(..., **TS_kwargs['gridspec_kwargs'])) which
#                 create the gridspec separating the full and zoom GLSP columns
#             - 'axeswithsharex_kwargs': dict
#                 The content of this entry should be a dictionary which will be passed to
#                 et.add_twoaxeswithsharex(... gs_from_sps_kw=TS_kwargs['axeswithsharex_kwargs']) which
#                 creates the data and residuals axes.
#     GLSP_kwargs   : None or dict
#             - 'do': boolean (Def: True)
#             - 'use_jitter': boolen (Def: True)
#                 If True it uses the error bars with jitter to compute the GLSP and the FAP levels
#             - 'period_range': Iterable of 2 float providing the beginning and end period for the computation
#                 of the GLSP
#             - 'freq_fact': float (Def: 1e6)
#                 Factor to apply to the frequency for example to plot them in micro Hertz
#             - 'freq_unit': str  (Def: "$\\mu$Hz"),
#                 Unit to display on the frequency axis. Must be coherent with freq_fact !
#             - 'freq_lims': None or Iterable of 2 float (Def: None)
#                 Specificy the frequency limits for the plot in freq_unit
#             - 'logscale': boolean (Def: False),
#             - 'show_WF': boolean (Def: True),
#             - 'show_inst_var': boolean (Def: True),
#             - 'periods': dict
#                 Specify the periods for which you want to draw a vertical line.
#                 The keys are the period values and the values are dict that can be empty or specify the
#                 values of the following keywords:
#                 - 'color': str giving the color of the line
#                 - 'linestyle': str giving the style of the line
#                 - 'label': str giving the label to plot
#                 - 'align': str ('left', 'right', 'center') the horizontal alignment of the label compared to the vertical line
#                 - 'xshift': float x shift of the label
#                 - 'yshift': float y shift of the label
#             - 'fap': dict
#                 Specify the fap levels for which you want to draw a horizontal line.
#                 The keys are the fap level values and the values are dict that can be empty or specify the
#                 values of the following keywords:
#                 - 'color': str giving the color of the line
#                 - 'linestyle': str giving the style of the line
#                 - 'label': int (0: don't show, 1: only the fap value, 2: fap value followed by %)
#                 - 'align': str ('top', 'center', 'bottom') the horizontal alignment of the label compared to the vertical line
#                 - 'xshift': float x shift of the label
#                 - 'yshift': float y shift of the label
#             - 'freq_lims_zoom': None or Iterable of 2 float (Def: None)
#                 If provided a zoom on the right of the main plot will be drawn.
#                 This gives the beginning and end time for the zoom
#             - 'scientific_notation_P_axis': boolean (default: True)
#                 If True the tick label on the period axis are in scientific notations
#             - 'period_no_ticklabels': list of int
#                 list of decades to for which you don't want to show the tick label
#             - 'period_no_ticklabels_zoom': list of int
#                 list of decades to for which you don't want to show the tick label for the zoom
#             - 'gridspec_kwargs': dict
#                 The content of this entry should be a dictionary which will be passed to
#                 GridSpecFromSubplotSpec (GridSpecFromSubplotSpec(..., **GLSP_kwargs['gridspec_kwargs'])) which
#                 create the gridspec separating the full and zoom GLSP columns
#             - 'axeswithsharex_kwargs': dict
#                 The content of this entry should be a dictionary which will be passed to
#                 et.add_axeswithsharex(... gs_from_sps_kw=TS_kwargs['axeswithsharex_kwargs']) which
#                 creates the different GLSP axes for the data, model ...
#             - 'legend_param': dict of dict
#                 Dictionary with key in ('data', 'model', 'resi', 'GP', 'WF') and values dictionaries that
#                 will be passed on to legend ( legend(.., **GLSP_kwargs['legend_param'][key]))
#     suptitle_kwargs : dict
#         Dictionary which defines the properties of the suptitle. See docstring of do_suptitle for details
#     LC_fact       : float
#         Factor to apply to the LC
#     LC_unit        : str
#         String giving the unit of the LCs
#     """
#     # star = post_instance.model.stars[star_name]
#
#     ##############################################
#     # Setup figure structure and common parameters
#     ##############################################
#     if fig_param is None:
#         fig_param = {}
#
#     fontsize = fig_param.get("fontsize", AandA_fontsize)
#
#     # Make sure that the TS_kwargs and GLSP_kwargs are dictionaries
#     TS_kwargs = {} if TS_kwargs is None else TS_kwargs
#     GLSP_kwargs = {} if GLSP_kwargs is None else GLSP_kwargs
#
#     # Create The GridSpec
#     gs = GridSpec(nrows=1, ncols=int(TS_kwargs.get("do", True)) + int(GLSP_kwargs.get("do", True)),
#                   figure=fig, **fig_param.get('gridspec_kwargs', {}))
#     if TS_kwargs.get("do", True):
#         gs_ts = gs[0]
#         if GLSP_kwargs.get("do", True):
#             gs_gls = gs[1]
#     else:
#         gs_gls = gs[0]
#
#     # If no dataset name is provided get all the available LC datasets
#     if datasetnames is None:
#         datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="LC", sortby_instcat=False, sortby_instname=False)
#
#     # Load the defined datasets and check how many dataset there is by instrument.
#     (dico_datasets, dico_kwargs, dico_nb_dstperinsts, times, datas, data_errs, data_err_jitters, data_err_worwojitters,
#      has_jitters, dico_jitters, models, gp_preds, gp_pred_vars, inst_vars, decorrs, decorr_likelihoods,
#      contams, residuals
#      ) = load_datasets_and_models_LC(datasetnames=datasetnames, post_instance=post_instance, datasim_kwargs=datasim_kwargs,
#                                      df_fittedval=df_fittedval, remove1=remove1, LC_fact=LC_fact, remove_inst_var=remove_inst_var,
#                                      remove_decorrelation=remove_decorrelation, remove_decorrelation_likelihood=remove_decorrelation_likelihood,
#                                      remove_contamination=remove_contamination, remove_GP_dataNmodel=False, remove_GP_residual=False)
#
#     # Do the suptitle
#     do_suptitle(fig=fig, post_instance=post_instance, fontsize=fontsize,
#                 t_l_removed_from_model=(["Inst var", "Decorrelation", "Contamination"],
#                                         [remove_inst_var, remove_decorrelation, remove_contamination],
#                                         [inst_vars, decorrs, contams],
#                                         ),
#                 t_l_removed_from_data=(["Inst var", "Decorrelation", "Decorrelation Likelihood", "Contamination"],
#                                        [remove_inst_var, remove_decorrelation, remove_decorrelation_likelihood, remove_contamination],
#                                        [inst_vars, decorrs, decorr_likelihoods, contams],
#                                        ),
#                 suptitle_kwargs=suptitle_kwargs)
#
#     ################
#     # LC TIME SERIES
#     ################
#     if TS_kwargs.get("do", True):
#
#         ################################################
#         # Create additional axe if zoom and several rows
#         ################################################
#         # Define on which rows the datasets are plots using the row4datasetname input
#         row4datasetname, datasetnames4rowidx = check_row4datasetname(row4datasetname=TS_kwargs.get("row4datasetname", None), datasetnames=datasetnames)
#         nb_rows = len(datasetnames4rowidx)
#         # Create the updated grid space according to the number of rows
#         gs_ts = GridSpecFromSubplotSpec(nb_rows, 1, subplot_spec=gs_ts, **TS_kwargs.get('gridspec_kwargs', {}))
#         # Determine which rows require a zoom.
#         if TS_kwargs.get("t_lims", None) is None:
#             t_lims = [None for row in range(nb_rows)]
#         else:
#             if isinstance(TS_kwargs["t_lims"], dict):
#                 t_lims = [TS_kwargs["t_lims"][row] for row in range(nb_rows)]
#             else:
#                 if nb_rows == 1:
#                     t_lims = [TS_kwargs["t_lims"], ]
#                 else:
#                     raise ValueError("Since theer is more than one row, TS_kwargs['t_lims'] should be a dictionary.")
#         if TS_kwargs.get("t_lims_zoom", None) is None:
#             t_lims_zoom = [None for row in range(nb_rows)]
#         else:
#             if isinstance(TS_kwargs["t_lims_zoom"], dict):
#                 t_lims_zoom = [TS_kwargs["t_lims_zoom"][row] for row in range(nb_rows)]
#             else:
#                 if nb_rows == 1:
#                     t_lims_zoom = [TS_kwargs["t_lims_zoom"], ]
#                 else:
#                     raise ValueError("Since theer is more than one row, TS_kwargs['t_lims_zoom'] should be a dictionary.")
#         # Infer from t_lims_zoom how many columns are required
#         if any([zoom is not None for zoom in t_lims_zoom]):
#             nb_cols = 2
#         else:
#             nb_cols = 1
#
#         # Set the binning variables
#         one_binning_per_row = TS_kwargs.get("one_binning_per_row", False)
#         exptime_bin = TS_kwargs.get("exptime_bin", 0.)
#         binning_stat = TS_kwargs.get("binning_stat", "mean")
#         time_unit = TS_kwargs.get('t_unit', 'days')
#
#         ##############################################
#         # Set the arguments for the plotting functions
#         ##############################################
#         pl_kwargs = TS_kwargs.get('pl_kwargs', {})
#         (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
#          ) = get_pl_kwargs(pl_kwargs=pl_kwargs, dico_nb_dstperinsts=dico_nb_dstperinsts,
#                            datasetnames=datasetnames, bin_size=exptime_bin, one_binning_per_row=one_binning_per_row,
#                            nb_rows=nb_rows, alpha_def_data=0.1, color_def_data="k", show_error_data_def=False)
#         update_binned_label(pl_kwarg_final=pl_kwarg_final, datasetnames=datasetnames, bin_size=exptime_bin,
#                             bin_size_unit=f" {time_unit}", one_binning_per_row=one_binning_per_row,
#                             nb_rows=nb_rows)
#
#         #############################################################
#         # Make the LC and residuals plots (full and zoomed if needed)
#         #############################################################
#         rms_kwargs = {'do': True, 'format': '.1e'}
#         rms_kwargs.update(TS_kwargs.get('rms_kwargs', {}))
#         text_rms = OrderedDict()
#         text_rms_binned = OrderedDict()
#         show_title = TS_kwargs.get("show_title", True)
#         for i_row in range(nb_rows):
#             gs_ts_row = GridSpecFromSubplotSpec(1, nb_cols, subplot_spec=gs_ts[i_row], **TS_kwargs.get('gridspec_kwargs', {}))
#             for i_col in range(nb_cols):
#                 gs_ts_i = gs_ts_row[i_col]
#                 if i_col == 0:
#                     t_lims_i = t_lims[i_row]
#                 else:  # i_col == 1
#                     t_lims_i = t_lims_zoom[i_row]
#                 # Create the data and residuals axes and set properties ans style
#                 (axe_data, axe_resi) = et.add_twoaxeswithsharex(gs_ts_i, fig, gs_from_sps_kw=TS_kwargs.get('axeswithsharex_kwargs', {}))  # gs_from_sps_kw={"wspace": 0.1}
#
#                 if show_title and (i_row == 0):
#                     axe_data.set_title("LC time series", fontsize=fontsize)
#                 axe_resi.set_xlabel(f"time [{time_unit}]", fontsize=fontsize)
#                 if i_col == 0:
#                     y_str = "$\Delta$F / F" if remove1 else "(F + $\Delta$F) / F"
#                     ylabel_data = f"{y_str} [{LC_unit}]" if LC_unit is not None else f"{y_str}"
#                     ylabel_resi = f"O - C [{LC_unit}]" if LC_unit is not None else "O - C"
#                     axe_data.set_ylabel(ylabel_data, fontsize=fontsize)
#                     axe_resi.set_ylabel(ylabel_resi, fontsize=fontsize)
#
#                 axe_data.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False, labelsize=fontsize)
#                 axe_data.xaxis.set_minor_locator(AutoMinorLocator())
#                 axe_data.yaxis.set_minor_locator(AutoMinorLocator())
#                 axe_data.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
#                 axe_data.grid(axis="y", color="black", alpha=.5, linewidth=.5)
#                 axe_resi.yaxis.set_minor_locator(AutoMinorLocator())
#                 axe_resi.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelsize=fontsize)
#                 axe_resi.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
#                 axe_resi.grid(axis="y", color="black", alpha=.5, linewidth=.5)
#
#                 for datasetname in datasetnames4rowidx[i_row]:
#                     if t_lims_i is None:
#                         lims_time_dst = [times[datasetname].min(), times[datasetname].max()]
#                     else:
#                         lims_time_dst = t_lims_i
#                     ###################
#                     # Compute the models
#                     ###################
#                     npt_model = TS_kwargs.get("npt_model", 1000)
#                     tsim = np.linspace(np.min(times[datasetname]) - TS_kwargs.get("extra_dt_model", 0.),
#                                        np.max(times[datasetname]) + TS_kwargs.get("extra_dt_model", 0.),
#                                        npt_model)
#                     # Full model
#                     model, model_wGP, gp_pred, gp_pred_var = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                                                          param=df_fittedval["value"].values,
#                                                                                          l_param_name=list(df_fittedval.index),
#                                                                                          key_obj=key_whole,
#                                                                                          datasim_kwargs=datasim_kwargs,
#                                                                                          include_gp=True)
#                     # inst_var
#                     if (datasetname in inst_vars):
#                         model_instvar = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                                     param=df_fittedval["value"].values,
#                                                                     l_param_name=list(df_fittedval.index),
#                                                                     key_obj="inst_var",
#                                                                     datasim_kwargs=datasim_kwargs,
#                                                                     include_gp=False)
#                     # decorr
#                     if (datasetname in decorrs):
#                         model_decorr = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                                    param=df_fittedval["value"].values,
#                                                                    l_param_name=list(df_fittedval.index),
#                                                                    key_obj="decorr",
#                                                                    datasim_kwargs=datasim_kwargs,
#                                                                    include_gp=False)
#                     # contam
#                     if (datasetname in contams):
#                         model_contam = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
#                                                                    param=df_fittedval["value"].values,
#                                                                    l_param_name=list(df_fittedval.index),
#                                                                    key_obj="contam",
#                                                                    datasim_kwargs=datasim_kwargs,
#                                                                    include_gp=False)
#                     # Remove the decorrelation:
#                     if (datasetname in decorrs) and remove_decorrelation:
#                         for model_part in model_decorr:
#                             if model_part == "add_2_totalflux":
#                                 model -= model_decorr['add_2_totalflux']
#                                 if model_wGP is not None:
#                                     model_wGP -= model_decorr['add_2_totalflux']
#                             else:
#                                 logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
#
#                     # Remove the inst_var if required
#                     if (datasetname in inst_vars) and remove_inst_var:
#                         model -= model_instvar
#                         if model_wGP is not None:
#                             model_wGP -= model_instvar
#                     # Remove the contamination
#                     if (datasetname in contams) and remove_contamination:
#                         model /= model_contam
#                         if model_wGP is not None:
#                             model_wGP /= model_contam
#                     # remove 1 if required
#                     if remove1:
#                         model -= 1
#                         if model_wGP is not None:
#                             model_wGP -= 1
#                     else:
#                         model_instvar += 1
#                         if (datasetname in decorrs):
#                             for model_part in model_decorr:
#                                 if model_part == "add_2_totalflux":
#                                     model_decorr["add_2_totalflux"] += 1
#                             # Else is already addressed above
#                     # Multiply by LC fact
#                     model *= LC_fact
#                     if (datasetname in inst_vars):
#                         model_instvar *= LC_fact
#                     if (datasetname in decorrs):
#                         for model_part in model_decorr:
#                             if model_part == "add_2_totalflux":
#                                 model_decorr["add_2_totalflux"] *= LC_fact
#                         # Else is already addressed above
#                     if model_wGP is not None:
#                         model_wGP *= LC_fact
#                         gp_pred *= LC_fact
#                         gp_pred_var *= LC_fact**2
#
#                     #####################################
#                     # Plot the model and the GP if needed
#                     #####################################
#                     line_model = axe_data.errorbar(tsim, model, **pl_kwarg_final[datasetname]["model"], zorder=20)
#                     if not("color" in pl_kwarg_final[datasetname]["model"]):
#                         pl_kwarg_final[datasetname]["model"]["color"] = line_model[0].get_color()
#                     if not("alpha" in pl_kwarg_final[datasetname]["model"]):
#                         pl_kwarg_final[datasetname]["model"]["alpha"] = line_model[0].get_alpha()
#                     if model_wGP is not None:
#                         if not("color" in pl_kwarg_final[datasetname]["GP"]):
#                             pl_kwarg_final[datasetname]["GP"]["color"] = pl_kwarg_final[datasetname]["model"]["color"]
#                         if not("alpha" in pl_kwarg_final[datasetname]["GP"]):
#                             pl_kwarg_final[datasetname]["GP"]["alpha"] = pl_kwarg_final[datasetname]["model"]["alpha"] / 2
#                         _ = axe_data.fill_between(tsim, model_wGP - np.sqrt(gp_pred_var), model_wGP + np.sqrt(gp_pred_var),
#                                                   color=pl_kwarg_final[datasetname]["GP"]["color"], alpha=pl_kwarg_final[datasetname]["GP"]["alpha"],
#                                                   label=pl_kwarg_final[datasetname]["GP"]["label"],  # **kwarg_GP_pred_var
#                                                   zorder=0
#                                                   )
#
#                     #############################
#                     # Plot the inst_var if needed
#                     #############################
#                     if (datasetname in inst_vars) and not(remove_inst_var):
#                         _ = axe_data.plot(tsim, model_instvar, **pl_kwarg_final[datasetname]["inst_var"])
#
#                     ########################################
#                     # Plot the decorrelation model if needed
#                     ########################################
#                     if (datasetname in decorrs) and not(remove_decorrelation):
#                         for model_part in decorrs[datasetname]:
#                             if model_part == "add_2_totalflux":
#                                 pl_kwarg_final_decorr_model_part = deepcopy(pl_kwarg_final[datasetname]["decorr"])
#                                 pl_kwarg_final_decorr_model_part.update(pl_kwargs.get(f"decorr_{model_part}", {}))
#                                 _ = axe_data.plot(tsim, model_decorr["add_2_totalflux"], **pl_kwarg_final_decorr_model_part)
#                             # Else is already addressed above
#
#                     ###############
#                     # Plot the data
#                     ###############
#                     if pl_show_error[datasetname]['data']:
#                         ebcont = axe_data.errorbar(times[datasetname], y=datas[datasetname],
#                                                    yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)  # Plot the data point and error bars without jitter
#                         if not("ecolor" in pl_kwarg_jitter[datasetname]):
#                             pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
#                         if not("color" in pl_kwarg_final[datasetname]):
#                             pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
#                         if has_jitters[datasetname]:
#                             axe_data.errorbar(times[datasetname], y=datas[datasetname],
#                                               yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"], zorder=1)  # Plot the error bars with jitter
#
#                     else:
#                         axe_data.errorbar(times[datasetname], y=datas[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)  # Plot the data point and error bars without jitter
#
#                     ####################
#                     # Plot the residuals
#                     ####################
#                     if pl_show_error[datasetname]['data']:
#                         axe_resi.errorbar(times[datasetname], y=residuals[datasetname], yerr=data_errs[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)
#                         if has_jitters[datasetname]:
#                             axe_resi.errorbar(times[datasetname], y=residuals[datasetname], yerr=data_err_jitters[datasetname], **pl_kwarg_jitter[datasetname]["data"], zorder=1)  # Plot the error bars with jitter
#                     else:
#                         axe_resi.errorbar(times[datasetname], y=residuals[datasetname], **pl_kwarg_final[datasetname]["data"], zorder=10)
#                     # Compute rms of the residuals and print it on the top of the residuals graphs
#                     text_rms_template = f"{{:{rms_kwargs['format']}}}"
#                     text_rms[datasetname] = text_rms_template.format(np.std(residuals[datasetname][np.logical_and(times[datasetname] > lims_time_dst[0], times[datasetname] < lims_time_dst[1])]))
#                     print(f"RMS {datasetname} = {text_rms[datasetname]} {LC_unit} (raw cadence)")
#
#                     ################################################################################
#                     # Compute and Plot the binned data and residuals if one_binning_per_row is False
#                     ################################################################################
#                     if not(one_binning_per_row) and (exptime_bin > 0.):
#                         t_min_data, t_max_data = (min(times[datasetname]), max(times[datasetname]))
#                         bins = np.arange(t_min_data, t_max_data + exptime_bin, exptime_bin)
#                         midbins = bins[:-1] + exptime_bin / 2
#                         nbins = len(bins) - 1
#                         # Compute the binned values
#                         (bindata, binedges, binnb
#                          ) = binned_statistic(times[datasetname], datas[datasetname],
#                                               statistic=binning_stat, bins=bins,
#                                               range=(t_min_data, t_max_data))
#                         (binresi, binedges, binnb
#                          ) = binned_statistic(times[datasetname], residuals[datasetname],
#                                               statistic=binning_stat, bins=bins,
#                                               range=(t_min_data, t_max_data))
#                         # Compute the err on the binned values
#                         binstd = np.zeros(nbins)
#                         if has_jitters[datasetname]:
#                             binstd_jitter = np.zeros(nbins)
#                         bincount = np.zeros(nbins)
#                         for i_bin in range(nbins):
#                             bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
#                             if bincount[i_bin] > 0.0:
#                                 binstd[i_bin] = np.sqrt(np.sum(np.power((data_errs[datasetname]
#                                                                          [binnb == (i_bin + 1)]),
#                                                                         2.)) /
#                                                         bincount[i_bin]**2)
#                                 if has_jitters[datasetname]:
#                                     binstd_jitter[i_bin] = np.sqrt(np.sum(np.power((data_err_jitters[datasetname]
#                                                                                     [binnb == (i_bin + 1)]),
#                                                                                    2.)) /
#                                                                    bincount[i_bin]**2)
#                             else:
#                                 binstd[i_bin] = np.nan
#                                 if has_jitters[datasetname]:
#                                     binstd_jitter[i_bin] = np.nan
#                         # Plot the binned data
#                         bin_err = binstd if pl_show_error[datasetname]["databinned"] else None
#                         ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
#                         if not("color" in pl_kwarg_final[datasetname]["databinned"]):
#                             pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
#                         if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
#                             pl_kwarg_jitter[datasetname]["databinned"] = pl_kwarg_final[datasetname]["databinned"]["color"]
#                         _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"], zorder=40)
#                         if has_jitters[datasetname] and pl_show_error[datasetname]["databinned"]:
#                             _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)
#                             _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"], zorder=30)
#                         # Compute rms of the binned residuals
#                         text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
#                         text_rms_binned[datasetname] = text_rms_binned_template.format(np.nanstd(binresi[np.logical_and(midbins > lims_time_dst[0], midbins < lims_time_dst[1])]))
#                         print(f"RMS {datasetname}: {text_rms_binned[datasetname]} {LC_unit}")
#
#                 ################################################################################
#                 # Compute and Plot the binned data and residuals if one_binning_per_row is True
#                 ################################################################################
#                 if one_binning_per_row and (exptime_bin > 0.):
#                     t_row = np.concatenate([times[dst] for dst in datasetnames4rowidx[i_row]])
#                     t_min_data, t_max_data = (min(t_row), max(t_row))
#                     if t_lims_i is None:
#                         lims_time_row = [t_row.min(), t_row.max()]
#                     else:
#                         lims_time_row = t_lims_i
#                     bins = np.arange(t_min_data, t_max_data + exptime_bin, exptime_bin)
#                     midbins = bins[:-1] + exptime_bin / 2
#                     nbins = len(bins) - 1
#                     # Compute the binned values
#                     (bindata, binedges, binnb
#                      ) = binned_statistic(t_row, np.concatenate([datas[dst] for dst in datasetnames4rowidx[i_row]]),
#                                           statistic=binning_stat, bins=bins,
#                                           range=(t_min_data, t_max_data))
#                     (binresi, binedges, binnb
#                      ) = binned_statistic(t_row, np.concatenate([residuals[dst] for dst in datasetnames4rowidx[i_row]]),
#                                           statistic=binning_stat, bins=bins,
#                                           range=(t_min_data, t_max_data))
#                     # Compute the err on the binned values
#                     binstd = np.zeros(nbins)
#                     if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
#                         binstd_jitter = np.zeros(nbins)
#                     bincount = np.zeros(nbins)
#                     data_err_row = np.concatenate([data_errs[dst] for dst in datasetnames4rowidx[i_row]])
#                     data_err_jitter_row = np.concatenate([data_err_jitters[dst] if has_jitters[dst] else np.ones_like(data_errs[dst]) * np.nan for dst in datasetnames4rowidx[i_row]])
#                     for i_bin in range(nbins):
#                         bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
#                         if bincount[i_bin] > 0.0:
#                             binstd[i_bin] = np.sqrt(np.sum(np.power((data_err_row
#                                                                      [binnb == (i_bin + 1)]),
#                                                                     2.)) /
#                                                     bincount[i_bin]**2)
#                             if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
#                                 binstd_jitter[i_bin] = np.sqrt(np.sum(np.power((data_err_jitter_row
#                                                                                 [binnb == (i_bin + 1)]),
#                                                                                2.)) /
#                                                                bincount[i_bin]**2)
#                         else:
#                             binstd[i_bin] = np.nan
#                             if any([has_jitters[datasetname] for datasetname in datasetnames4rowidx[i_row]]):
#                                 binstd_jitter[i_bin] = np.nan
#                     # Plot the binned data
#                     bin_err = binstd if pl_show_error[f"row{i_row}"] else None
#                     ebcont_binned = axe_data.errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
#                     if not("color" in pl_kwarg_final[f"row{i_row}"]):
#                         pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
#                     if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
#                         pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
#                     _ = axe_resi.errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"], zorder=40)
#                     if any([has_jitters[dst] for dst in datasetnames4rowidx[i_row]]) and pl_show_error[f"row{i_row}"]:
#                         _ = axe_data.errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)
#                         _ = axe_resi.errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"], zorder=30)
#                     # Compute rms of the binned residuals
#                     text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
#                     text_rms_binned[f"row{i_row}"] = text_rms_binned_template.format(np.nanstd(binresi[np.logical_and(midbins > lims_time_row[0], midbins < lims_time_row[1])]))
#                     print(f"RMS row {i_row}: {text_rms_binned[f'row{i_row}']} {LC_unit}")
#
#                 # Draw a horizontal line at the level of reference stellar flux level
#                 xlims = axe_data.get_xlim()
#                 reference_stellar_flux = 0 if remove_inst_var else 1
#                 axe_data.hlines(reference_stellar_flux, *xlims, colors="k", linestyles="dashed")
#
#                 # Adjust the y lims for the data plot
#                 ylims_data = TS_kwargs.get("ylims_data", None)
#                 if ylims_data is None:
#                     pad_data = TS_kwargs.get("pad_data", (0.1, 0.1))
#                     et.auto_y_lims(np.concatenate([datas[dst] for dst in datasetnames]), axe_data,
#                                    pad=pad_data)
#                 else:
#                     axe_data.set_ylim(ylims_data)
#
#                 # Indicate values that are off y-axis with an arrows in the data plot
#                 # This should be here an not in the previous for datasetname in datasetnames4rowidx[i_row] loop because the
#                 # y_lims can change after each dataset
#                 if TS_kwargs.get("indicate_y_outliers_data", True):
#                     for datasetname in datasetnames4rowidx[i_row]:
#                         et.indicate_y_outliers(x=times[datasetname], y=datas[datasetname],
#                                                ax=axe_data, color=pl_kwarg_final[datasetname]["data"].get("color", None),
#                                                alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))
#
#                 # Draw a horizontal line at 0 in the residual plot
#                 axe_resi.hlines(0, *xlims, colors="k", linestyles="dashed")
#
#                 # Adjust the y lims for the residuals plot
#                 ylims_resi = TS_kwargs.get("ylims_resi", None)
#                 if ylims_resi is None:
#                     pad_resi = TS_kwargs.get("pad_resi", (0.1, 0.1))
#                     et.auto_y_lims(np.concatenate([residuals[dst] for dst in datasetnames]), axe_resi,
#                                    pad=pad_resi)
#                 else:
#                     axe_resi.set_ylim(ylims_resi)
#
#                 # Indicate values that are off y-axis with an arrows in the residuals plot
#                 # This should be here an not in the previous for datasetname in datasetnames4rowidx[i_row] loop because the
#                 # y_lims can change after each dataset
#                 if TS_kwargs.get("indicate_y_outliers_resi", True):
#                     for datasetname in datasetnames:
#                         et.indicate_y_outliers(x=times[datasetname], y=residuals[datasetname],
#                                                ax=axe_resi, color=pl_kwarg_final[datasetname]["data"].get("color", None),
#                                                alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))
#
#                 ############################
#                 # Set the t_lims if provided
#                 ############################
#                 if t_lims_i is None:
#                     axe_resi.set_xlim(xlims)
#                 else:
#                     axe_resi.set_xlim(t_lims_i)
#
#                 ###########
#                 # Write rms
#                 ###########
#                 # WARNING, TO BE IMPROVED for more than one dataset
#                 if (i_col == 0) and rms_kwargs['do']:
#                     text_rms_to_plot = ""
#                     for i_dst, datasetname in enumerate(datasetnames4rowidx[i_row]):
#                         # text_rms_to_plot_dst = f"{pl_kwarg_final[datasetname]['data']['label']}: {text_rms[datasetname]}"
#                         text_rms_to_plot_dst = f"{pl_kwarg_final[datasetname]['data']['label']}: {text_rms[datasetname]}"
#                         if datasetname in text_rms_binned:
#                             text_rms_to_plot_dst += f", {text_rms_binned[datasetname]} (bin)"
#                         if i_dst == 0:
#                             text_rms_to_plot_dst = "rms = " + text_rms_to_plot_dst
#                         if LC_unit is not None:
#                             text_rms_to_plot_dst += f" {LC_unit}"
#                         text_rms_to_plot += text_rms_to_plot_dst + "; "
#                     if f"row{i_row}" in text_rms_binned:
#                         text_rms_to_plot += "\n"
#                         text_rms_to_plot += f"rms bin = {text_rms_binned[f'row{i_row}']} {LC_unit}"
#                     axe_resi.text(0.0, 1.05, text_rms_to_plot, fontsize=fontsize, transform=axe_resi.transAxes)
#
#                 ##########################
#                 # Set the legend if needed
#                 ##########################
#                 legend_kwargs_i_row = TS_kwargs.get('legend_kwargs', {}).get('all', {'do': True})
#                 legend_kwargs_i_row.update(TS_kwargs.get('legend_kwargs', {}).get(i_row, {}))
#                 if (i_col == 0) and legend_kwargs_i_row.get('do', True):
#                     legend_kwargs_i_row.pop('do')
#                     axe_data.legend(fontsize=fontsize, **legend_kwargs_i_row)
#
#     #########
#     # LC GLSP
#     #########
#     if GLSP_kwargs.get("do", True):
#         # Create the all_time array which gathers the times from all datasets
#         # WARNING:
#         all_time = np.concatenate([times[dst] for dst in datasetnames])
#         idx_sort = np.argsort(all_time)
#         all_time = all_time[idx_sort]
#         all_data = np.concatenate([datas[dst] for dst in datasetnames])[idx_sort]
#         all_resi = np.concatenate([residuals[dst] for dst in datasetnames])[idx_sort]
#         if GLSP_kwargs.get("use_jitter", True):
#             all_data_err = np.concatenate([data_err_worwojitters[dst] for dst in datasetnames])[idx_sort]
#         else:
#             all_data_err = np.concatenate([data_errs[dst] for dst in datasetnames])[idx_sort]
#         all_model = np.concatenate([models[dst] for dst in datasetnames])[idx_sort]
#         all_time_gp = []
#         all_gp_pred = []
#         all_gp_pred_var = []
#         for dst in datasetnames:
#             if dst in gp_preds:
#                 all_time_gp.append(times[dst])
#                 all_gp_pred.append(gp_preds[dst])
#                 all_gp_pred_var.append(gp_pred_vars[dst])
#         if len(all_time_gp) > 0:
#             all_time_gp = np.concatenate(all_time_gp)
#             idx_sort_gp = np.argsort(all_time_gp)
#             all_time_gp = all_time_gp[idx_sort_gp]
#             all_gp_pred = np.concatenate(all_gp_pred)[idx_sort_gp]
#             all_gp_pred_var = np.concatenate(all_gp_pred_var)[idx_sort_gp]
#         all_time_inst_var = []
#         all_inst_var = []
#         for dst in datasetnames:
#             if dst in inst_vars:
#                 all_time_inst_var.append(times[dst])
#                 all_inst_var.append(inst_vars[dst])
#         if len(all_time_inst_var) > 0:
#             all_time_inst_var = np.concatenate(all_time_inst_var)
#             idx_sort_inst_var = np.argsort(all_time_inst_var)
#             all_time_inst_var = all_time_inst_var[idx_sort_inst_var]
#             all_inst_var = np.concatenate(all_inst_var)[idx_sort_inst_var]
#         all_time_decorrs = {}
#         all_decorrs = {}
#         if len(decorrs) > 0:
#             for dst in datasetnames:
#                 for model_part in decorrs[dst]:
#                     if model_part in ["add_2_totalflux", ]:
#                         if model_part not in all_time_decorrs:
#                             all_decorrs[model_part] = []
#                             all_time_decorrs[model_part] = []
#                         all_decorrs[model_part].append(decorrs[dst][model_part])
#                         all_time_decorrs[model_part].append(times[dst])
#                     else:
#                         logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
#             for model_part in all_decorrs:
#                 all_time_decorrs[model_part] = np.concatenate(all_time_decorrs[model_part])
#                 idx_sort_decorrs_model_part = np.argsort(all_time_decorrs[model_part])
#                 all_time_decorrs[model_part] = all_time_decorrs[model_part][idx_sort_decorrs_model_part]
#                 all_decorrs[model_part] = np.concatenate(all_decorrs[model_part])
#                 all_decorrs[model_part] = all_decorrs[model_part][idx_sort_decorrs_model_part]
#
#         gls_inputs = {}
#         l_gls_key = []
#         gls_inputs["data"] = {"time": all_time, "data": all_data, "err": all_data_err, 'label': "data"}
#         l_gls_key.append("data")
#         gls_inputs["model"] = {"time": all_time, "data": all_model, "err": all_data_err, 'label': "model"}
#         l_gls_key.append("model")
#         if len(all_gp_pred_var) > 0:
#             gls_inputs["GP"] = {"time": all_time_gp, "data": all_gp_pred, "err": np.sqrt(all_gp_pred_var), 'label': "GP"}
#             l_gls_key.append("GP")
#         if len(all_inst_var) > 0 and GLSP_kwargs.get("show_inst_var", True):
#             gls_inputs["inst"] = {"time": all_time_inst_var, "data": all_inst_var, "err": all_data_err, 'label': "inst"}
#             l_gls_key.append("inst")
#         for model_part in all_decorrs:
#             if GLSP_kwargs.get("show_decorrelation", True):
#                 gls_inputs[f"decorr_{model_part}"] = {"time": all_time_decorrs[model_part], "data": all_decorrs[model_part], "err": all_data_err, 'label': f"decorr: {model_part.replace('_', ' ')}"}
#                 l_gls_key.append(f"decorr_{model_part}")
#         gls_inputs["resi"] = {"time": all_time, "data": all_resi, "err": all_data_err, 'label': "residuals"}
#         l_gls_key.append("resi")
#
#         ###############################
#         # Compute the GLSPs
#         ###############################
#         Pbeg, Pend = GLSP_kwargs.get("period_range", (0.1, 1000))
#
#         glsps = {}
#         for ii, key in enumerate(l_gls_key):
#             glsps[key] = Gls((gls_inputs[key]["time"], gls_inputs[key]["data"], gls_inputs[key]["err"]), Pbeg=Pbeg, Pend=Pend, verbose=False)
#
#         ###############################
#         # Create additional axe if zoom
#         ###############################
#         if GLSP_kwargs.get("freq_lims_zoom", None) is not None:
#             gs_gls = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_gls, **TS_kwargs.get('gridspec_kwargs', {}))  # , wspace=0.2, width_ratios=(2, 1)
#             freq_lims = [GLSP_kwargs.get("freq_lims", None), GLSP_kwargs["freq_lims_zoom"]]
#             period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), GLSP_kwargs.get("period_no_ticklabels_zoom", [])]
#             nb_columns = 2
#         else:
#             gs_gls = [gs_gls, ]
#             freq_lims = [GLSP_kwargs.get("freq_lims", None), ]
#             period_no_ticklabels = [GLSP_kwargs.get("period_no_ticklabels", []), ]
#             nb_columns = 1
#
#         ################################################
#         # Create additional axes for data, model, etc...
#         ################################################
#         show_WF = GLSP_kwargs.get("show_WF", True)
#         nb_axes = len(l_gls_key) + int(show_WF)
#         freq_fact = GLSP_kwargs.get("freq_fact", 1e6)
#         freq_unit = GLSP_kwargs.get("freq_unit", '$\mu$Hz')
#         logscale = GLSP_kwargs.get("logscale", False)
#         legend_param = GLSP_kwargs.get('legend_param', {})
#
#         for jj, (gs_gls_j, freq_lims_j, period_no_ticklabels_j) in enumerate(zip(gs_gls, freq_lims, period_no_ticklabels)):
#             ax_gls = et.add_axeswithsharex(gs_gls_j, fig, nb_axes=nb_axes, gs_from_sps_kw=GLSP_kwargs.get("axeswithsharex_kwargs", {}))  # {"wspace": 0.2})
#             if jj == 0:
#                 ax_gls[0].set_title("GLS Periodograms", fontsize=fontsize)
#             if logscale:
#                 ax_gls[-1].set_xscale("log")
#             # ax_gls[-1].set_xlabel("Period [days]", fontsize=fontsize)
#             ax_gls[-1].set_xlabel(f"Frequency [{freq_unit}]", fontsize=fontsize)
#             # create and set the twiny axis
#             ax_gls_twin = []
#             for ii, key in enumerate(l_gls_key):
#                 ax_gls_twin.append(ax_gls[ii].twiny())
#                 if logscale:
#                     ax_gls_twin[ii].set_xscale("log")
#                 ax_gls[ii].set_zorder(ax_gls_twin[ii].get_zorder() + 1)  # To make sure that the orginal axis is above the new one
#                 ax_gls[ii].patch.set_visible(False)
#                 labeltop = True if ii == 0 else False
#                 ax_gls_twin[ii].tick_params(axis="x", labeltop=labeltop, labelsize=fontsize, which="both", direction="in")
#                 ax_gls_twin[ii].tick_params(axis="x", which="major", length=4, width=1)
#                 ax_gls_twin[ii].tick_params(axis="x", which="minor", length=2, width=0.5)
#                 ax_gls[ii].tick_params(axis="both", direction="in", which="both", bottom=True, top=False, left=True, right=True, labelsize=fontsize)
#                 ax_gls[ii].tick_params(axis="both", which="major", length=4, width=1)
#                 ax_gls[ii].tick_params(axis="both", which="minor", length=2, width=0.5)
#                 # ax_gls[ii].yaxis.set_label_position("right")
#                 # ax_gls[ii].yaxis.tick_right()
#                 labelleft = True if jj == 0 else False
#                 labelbottom = True if ii == (nb_axes - 1) else False
#                 ax_gls[ii].tick_params(axis="x", labelleft=labelleft, labelbottom=labelbottom, labelsize=fontsize, which="both", direction="in")
#                 ax_gls[ii].tick_params(axis="y", labelleft=labelleft, labelsize=fontsize, which="both", direction="in")
#                 ax_gls[ii].yaxis.set_minor_locator(AutoMinorLocator())
#                 ax_gls[ii].xaxis.set_minor_locator(AutoMinorLocator())
#
#                 # Plot the GLS in frequency (freq are in 1 / unit of the time vector provided)
#                 ax_gls[ii].plot(glsps[key].freq / day2sec * freq_fact, glsps[key].power, '-', color="k", label=gls_inputs[key]["label"], linewidth=GLSP_kwargs.get("lw ", 1.))
#                 # Set ticks and tick labels
#                 if jj == 0:
#                     ax_gls[ii].set_ylabel(f"{glsps[key].label['ylabel']}", fontsize=fontsize)  # {gls_inputs[key]['label']}
#
#                 ylims = ax_gls[ii].get_ylim()
#                 xlims = ax_gls[ii].get_xlim()
#
#                 # Print the period axis
#                 per_min = np.min(1 / glsps[key].freq)
#                 freq_min = np.min(glsps[key].freq)
#                 per_max = np.max(1 / glsps[key].freq)
#                 freq_max = np.max(glsps[key].freq)
#                 per_xlims = [1 / (freq_lim / freq_fact * day2sec) for freq_lim in xlims]
#                 if per_xlims[0] < 0:  # Sometimes the inferior xlims is negative and it messes up with the rest
#                     per_xlims[0] = per_max
#                 per_xlims = per_xlims[::-1]
#                 if not(logscale):
#                     ax_gls_twin[ii].plot([freq_min / day2sec * freq_fact, freq_max / day2sec * freq_fact],
#                                          [np.mean(glsps[key].power), np.mean(glsps[key].power)], "k", alpha=0)
#                 else:
#                     ax_gls_twin[ii].plot([per_min, per_max], [np.mean(glsps[key].power), np.mean(glsps[key].power)], "k", alpha=0)
#                     xlims_per = ax_gls_twin[ii].get_xlim()
#                     ax_gls_twin[ii].set_xlim(xlims_per[::-1])
#                 if not(logscale):
#                     per_decades = [10**(exp) for exp in list(range(int(np.floor(np.log10(per_min))), int(np.ceil(np.log10(per_max))) + 1))]
#                     per_ticks_major = []
#                     per_ticklabels_major = []
#                     per_ticks_minor = []
#                     for dec in per_decades:
#                         for fact in range(1, 10):
#                             tick = dec * fact
#                             if (tick > per_xlims[0]) and (tick < per_xlims[1]):
#                                 if fact == 1:
#                                     per_ticks_major.append(tick)
#                                     if tick in period_no_ticklabels_j:
#                                         per_ticklabels_major.append(None)
#                                     else:
#                                         per_ticklabels_major.append(tick)
#                                 else:
#                                     per_ticks_minor.append(tick)
#                     # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
#                     ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_major])
#                     if GLSP_kwargs.get('scientific_notation_P_axis', True):
#                         ax_gls_twin[ii].set_xticklabels([fmt_sci_not(tick) if tick is not None else "" for tick in per_ticklabels_major])
#                     else:
#                         ax_gls_twin[ii].set_xticklabels(per_ticklabels_major)
#                     # ax_gls_twin[ii].set_xticks(per_ticks_minor, minor=True)
#                     ax_gls_twin[ii].set_xticks([1 / tick / day2sec * freq_fact for tick in per_ticks_minor], minor=True)
#
#                 if freq_lims_j is None:
#                     ax_gls[ii].set_xlim(xlims)
#                     if logscale:
#                         ax_gls_twin[ii].set_xlim(xlims_per[::-1])
#                     else:
#                         ax_gls_twin[ii].set_xlim(xlims)
#                 else:
#                     ax_gls[ii].set_xlim(freq_lims_j)
#                     if logscale:
#                         ax_gls_twin[ii].set_xlim([1 / (freq / freq_fact * day2sec) for freq in freq_lims_j])
#                     else:
#                         ax_gls_twin[ii].set_xlim(freq_lims_j)
#
#                 ylims = ax_gls[ii].get_ylim()
#                 xlims = ax_gls[ii].get_xlim()
#
#                 #####################################
#                 # Vertical lines at specified periods
#                 #####################################
#                 for per, dico_per in GLSP_kwargs.get('periods', {}).items():
#                     vlines_kwargs = dico_per.get("vlines_kwargs", {})
#                     lines_per = ax_gls[ii].vlines(1 / per / day2sec * freq_fact, *ylims, **vlines_kwargs)
#                     if key == "data":
#                         text_kwargs = dico_per.get("text_kwargs", {}).copy()
#                         x_shift = text_kwargs.pop("x_shift", 0)
#                         y_pos = text_kwargs.pop("y_pos", 0.9)
#                         label = str(text_kwargs.pop("label", np.format_float_positional(per, precision=3, unique=False, fractional=False, trim='k')))
#                         color = text_kwargs.pop("color", None)
#                         if color is None:
#                             color = lines_per.get_color()[0]
#                         ax_gls_twin[ii].text(1 / (per) / day2sec * freq_fact + x_shift * (xlims[1] - xlims[0]),
#                                              ylims[0] + y_pos * (ylims[1] - ylims[0]), label, color=color,
#                                              fontsize=fontsize, **text_kwargs)
#                 ax_gls[ii].set_ylim(ylims)
#
#                 ##########################################
#                 # Horizontal lines at specified FAP levels
#                 ##########################################
#                 ylims = ax_gls[ii].get_ylim()
#                 xlims = ax_gls[ii].get_xlim()
#
#                 default_fap_dict = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"}, },
#                                     1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"}, },
#                                     10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"}, }, }
#                 for fap_lvl, dico_fap in GLSP_kwargs.get('fap', default_fap_dict).items():
#                     pow_ii = glsps[key].powerLevel(fap_lvl / 100)
#                     hlines_kwargs = dico_fap.get("hlines_kwargs", {})
#                     if pow_ii < ylims[1]:
#                         lines_fap = ax_gls[ii].hlines(pow_ii, *xlims, **hlines_kwargs)
#                         text_kwargs = dico_fap.get("text_kwargs", {}).copy()
#                         x_pos = text_kwargs.pop("x_pos", 1.05)
#                         y_shift = text_kwargs.pop("y_shift", 0)
#                         label = str(text_kwargs.pop("label", f"{fap_lvl}\%"))
#                         color = text_kwargs.pop("color", None)
#                         if color is None:
#                             color = lines_fap.get_color()[0]
#                         if jj == (nb_columns - 1):
#                             ax_gls[ii].text(xlims[0] + x_pos * (xlims[1] - xlims[0]), pow_ii + y_shift * (ylims[1] - ylims[0]),
#                                             label, color=color, fontsize=fontsize, **text_kwargs)
#
#                 ax_gls[ii].set_xlim(xlims)
#                 #
#                 if jj == 0:
#                     ax_gls[ii].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get(key, {}))
#
#             ax_gls_twin[0].set_xlabel("Period [days]", fontsize=fontsize)
#
#             if GLSP_kwargs.get("show_WF", True):
#                 ax_gls[-1].plot(glsps[key].freq / day2sec * freq_fact, glsps[key].wf, '-', color="k", label="WF", linewidth=GLSP_kwargs.get("lw ", 1.))
#                 if jj == 0:
#                     ax_gls[-1].legend(handletextpad=-.1, handlelength=0, fontsize=fontsize, **legend_param.get("WF", {}))
#                     ax_gls[-1].set_ylabel("Relative Amplitude")
#                 labelleft = True if jj == 0 else False
#                 ax_gls[-1].tick_params(axis="both", labelleft=labelleft, labelsize=fontsize, right=True, which="both", direction="in")
#
#                 # ax_gls_twin[-1].tick_params(axis="x", which="both", top=False, direction="in")
