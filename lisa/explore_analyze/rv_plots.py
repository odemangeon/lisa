"""
Module to create plots specifically for radial velocity data

@TODO:
"""
from loguru import logger
from collections import OrderedDict

from .phase_folded import create_phasefolded_plots
from .ts_and_glsp import create_TSNGLSP_plots, create_iTSNGLSP_plots
from .misc import AandA_fontsize
from .core_compute_load import get_key_compute_model as get_key_compute_model_core
from .core_compute_load import is_valid_model_available as is_valid_model_available_core
from .core_compute_load import compute_raw_models as compute_raw_models_core

from ..posterior.core.model.core_model import Core_Model


key_whole = Core_Model.key_whole

y_name = "RV"

dict_model_false = {key: False for key in ["stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}
dict_model_true = {key: True for key in ["stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}

d_name_component_removed_to_print = {'inst_var': "Inst Var", 'stellar_var': "Stellar var",
                                     'decorrelation': "Decorrelation",
                                     'decorrelation_likelihood': "Decorrelation Likelihood",
                                     'contamination': "Contamination",
                                     'GP': "GP",
                                     }


def create_RV_phasefolded_plots(post_instance, df_fittedval, datasim_kwargs=None,
                                planets=None, planets_remove_or_add_dict=None, periods=None, periods_remove_or_add_dict=None,
                                datasetnames=None, row4datasetname=None,
                                datasetnameformodel4row=None, npt_model=1000,
                                split_GP_computation=None,
                                phasefold_central_phase=0.,
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
                                RV_fact=1.,
                                RV_unit="$km/s$",
                                fontsize=AandA_fontsize,
                                fig=None,
                                gs=None,
                                ):
    """Produce clean RV phase folded plots of a system.

    WARNING/TODO: Because the plots are done independantly for each planet when sharey is True,
    I am not sure that the indicate_y_outliers function behaves correctly.

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
    phasefold_central_phase : float
        orbital phase (between 0 and 1) that will be at the center of phase domain for the plot.
        0 correspond to the transit and means that the phases for the plot will go from -0.5 to 0.5
        0.5 correspond to the secondary transit and means that the phases for the plot will go from 0 to 1.
    time_fact           : float
        If show_time_from_tic is True, than the time from mid transit is expressed in the same unit than the period
        by defaults. You can provide a factor here that will be applied to the times.
    time_unit           : str
        If show_time_from_tic is True, than you can provide here the unit in which the time from mid transit
        is expressed (knowing that time_fact is applied)
    exptime_bin         : float
        Width of the bins used for the binning the unit of this depends on the value of show_time_from_tic.
        If show_time_from_tic is True, it's a time unit otherwise the unit is orbital phase.
        If it's a time unit then the unit depend on the unit of the data after time_fact is applied.
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
        Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "modelbinned" or "databinned" and values
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
    RV_fact        : float
        Factor to apply to the RV
    RV_unit        : str
        String giving the unit of the RVs
    fig            : Figure
        Figure instance
    gs             : GridSpec
        If provided should have been made from fig, meaning that it doesn't make sense to provide gs without providing fig.
        It should be a Gridspec with ncols=1 and nrows according to row4datasetname
    """
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "stellar_var"],
                            [True, True, True]
                            ):
        remove_dict_model[key] = default
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP", "decorrelation_likelihood", "decorrelation", "inst_var", "stellar_var"],
                            [True, True, True, True, True]
                            ):
        remove_dict_data[key] = default
    remove_dict_data_err = OrderedDict()
    kwargs_compute_model_4_key_model = {"model": {"remove_dict": remove_dict_model,
                                                  'add_dict': dict_model_false
                                                  },
                                        "data": {"remove_dict": remove_dict_data,
                                                 'add_dict': dict_model_false
                                                 },
                                        "data_err": {"remove_dict": remove_dict_data_err,
                                                     'add_dict': dict_model_false
                                                     },
                                        }
    return create_phasefolded_plots(post_instance=post_instance, df_fittedval=df_fittedval,
                                    compute_raw_models_func=compute_raw_models_core,
                                    remove_add_model_components_func=remove_add_model_components,
                                    kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                    y_name=y_name, inst_cat='RV',
                                    d_name_component_removed_to_print=d_name_component_removed_to_print,
                                    datasim_kwargs=datasim_kwargs, 
                                    planets=planets, planets_remove_or_add_dict=planets_remove_or_add_dict,
                                    periods=periods, periods_remove_or_add_dict=periods_remove_or_add_dict,
                                    datasetnames=datasetnames, row4datasetname=row4datasetname,
                                    datasetnameformodel4row=datasetnameformodel4row,
                                    npt_model=npt_model, split_GP_computation=split_GP_computation,
                                    phasefold_central_phase=phasefold_central_phase,
                                    amplitude_fact=RV_fact, show_time_from_tic=show_time_from_tic, time_fact=time_fact,
                                    time_unit=time_unit, exptime_bin=exptime_bin, binning_stat=binning_stat,
                                    supersamp_bin_model=supersamp_bin_model, show_binned_model=show_binned_model,
                                    one_binning_per_row=one_binning_per_row,
                                    sharey=sharey, create_axes_kwargs=create_axes_kwargs, pad=pad, indicate_y_outliers=indicate_y_outliers,
                                    pl_kwargs=pl_kwargs, xlims=xlims, force_xlims=force_xlims, ylims=ylims,
                                    rms_kwargs=rms_kwargs, legend_kwargs=legend_kwargs, show_datasetnames=show_datasetnames,
                                    suptitle_kwargs=suptitle_kwargs, show_title_labels_ticklabels=show_title_labels_ticklabels,
                                    unit=RV_unit, fontsize=fontsize,
                                    get_key_compute_model_func=get_key_compute_model_core,
                                    fig=fig, gs=gs
                                    )


def create_RV_TSNGLSP_plots(fig, post_instance, df_fittedval, datasim_kwargs=None,
                            datasetnames=None,
                            remove_dict=None,
                            kwargs_compute_model_4_key_model=None,
                            compute_GP_model=True,
                            split_GP_computation=None,
                            show_dict=None, datasetname4model4row=None,
                            TS_kwargs=None, GLSP_kwargs=None,
                            create_axes_kwargs=None,
                            suptitle_kwargs=None,
                            RV_fact=1., RV_unit="$km/s$", fontsize=AandA_fontsize
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
    datasetnames  : list of String
        List providing the datasets to load and use
    remove_dict   : dict of bool
    datasetnames4model4row  : dict of dict of
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
                Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "GP"
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
    RV_fact       : float
        Factor to apply to the RV
    RV_unit        : str
        String giving the unit of the RVs

    Returns
    -------
    dico_load       : dict  
        Output of the function core_compute_load.load_datasets_and_models
    computed_models : dict
        Outputs of the compute_and_plot_model function calls
    """
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "stellar_var"],  # WARNING don't put 'GP' here the GP model should not be removed from the model as it's not part of it
                            [False, False, False]
                            ):
        remove_dict_model[key] = remove_dict.get(key, default)
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP", "decorrelation_likelihood", "decorrelation", "inst_var", "stellar_var"],
                            [False, False, False, False, False]
                            ):
        remove_dict_data[key] = remove_dict.get(key, default)
    remove_dict_data_err = OrderedDict()
    kwargs_compute_model_4_key_model_user = kwargs_compute_model_4_key_model if kwargs_compute_model_4_key_model is not None else {}
    kwargs_compute_model_4_key_model = {"model": {"remove_dict": remove_dict_model,
                                                  'add_dict': dict_model_false
                                                  },
                                        "model_wGP": {"remove_dict": remove_dict_model,
                                                      'add_dict': dict_model_false
                                                      },
                                        "data": {"remove_dict": remove_dict_data,
                                                 'add_dict': dict_model_false
                                                 },
                                        "data_err": {"remove_dict": remove_dict_data_err,
                                                     'add_dict': dict_model_false
                                                     },
                                        }
    kwargs_compute_model_4_key_model.update(kwargs_compute_model_4_key_model_user)
    if "model_wGP" not in kwargs_compute_model_4_key_model_user:
        kwargs_compute_model_4_key_model.update(kwargs_compute_model_4_key_model_user.get("model", {}))
    return create_TSNGLSP_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                                y_name=y_name, inst_cat='RV',
                                compute_raw_models_func=compute_raw_models_core,
                                remove_add_model_components_func=remove_add_model_components,
                                kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                compute_GP_model=compute_GP_model,
                                split_GP_computation=split_GP_computation,
                                d_name_component_removed_to_print=d_name_component_removed_to_print,
                                show_dict=show_dict, l_model_1_per_row=['model', 'stellar_var', 'GP'],
                                datasetname4model4row=datasetname4model4row,
                                datasim_kwargs=datasim_kwargs,
                                datasetnames=datasetnames,
                                amplitude_fact=RV_fact, unit=RV_unit,
                                create_axes_kwargs=create_axes_kwargs,
                                TS_kwargs=TS_kwargs,
                                GLSP_kwargs=GLSP_kwargs,
                                suptitle_kwargs=suptitle_kwargs,
                                fontsize=fontsize,
                                # get_key_compute_model_func=get_key_compute_model,
                                )


def create_RV_iTSNGLSP_plots(fig, post_instance, df_fittedval, datasim_kwargs=None,
                             datasetnames=None,
                             remove_dict=None, show_dict=None,
                             show_removed_in_previousrow=True,
                             l_iterative_removal=None,
                             datasetname4model=None,
                             kwargs_compute_model_4_key_model=None,
                             compute_GP_model=True, split_GP_computation=None, 
                             TS_kwargs=None, GLSP_kwargs=None,
                             create_axes_kwargs=None,
                             suptitle_kwargs=None,
                             RV_fact=1., RV_unit="$km/s$", fontsize=AandA_fontsize
                             ):
    """Produce clean iterative RV time series and generalized Lomb-Scargle plots of a system.

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
    datasetnames4model4row  : dict of dict of
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
                Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "GP"
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
    RV_fact       : float
        Factor to apply to the RV
    RV_unit        : str
        String giving the unit of the RVs

    Returns
    -------
    dico_load       : dict  
        Output of the function core_compute_load.load_datasets_and_models
    computed_models : dict
        Outputs of the compute_and_plot_model function calls
    """
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "stellar_var"],  # WARNING don't put 'GP' here the GP model should not be removed from the model as it's not part of it
                            [False, False, False]
                            ):
        remove_dict_model[key] = remove_dict.get(key, default)
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP", "decorrelation_likelihood", "decorrelation", "inst_var", "stellar_var"],
                            [False, False, False, False, False]
                            ):
        remove_dict_data[key] = remove_dict.get(key, default)
    remove_dict_data_err = OrderedDict()
    kwargs_compute_model_4_key_model_user = kwargs_compute_model_4_key_model if kwargs_compute_model_4_key_model is not None else {}
    kwargs_compute_model_4_key_model = {"model": {"remove_dict": remove_dict_model,
                                                  'add_dict': dict_model_false
                                                  },
                                        "model_wGP": {"remove_dict": remove_dict_model,
                                                      'add_dict': dict_model_false
                                                      },
                                        "data": {"remove_dict": remove_dict_data,
                                                 'add_dict': dict_model_false
                                                 },
                                        "data_err": {"remove_dict": remove_dict_data_err,
                                                     'add_dict': dict_model_false
                                                     },
                                        }
    kwargs_compute_model_4_key_model.update(kwargs_compute_model_4_key_model_user)
    if "model_wGP" not in kwargs_compute_model_4_key_model_user:
        kwargs_compute_model_4_key_model.update(kwargs_compute_model_4_key_model_user.get("model", {}))
    return create_iTSNGLSP_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                                 y_name=y_name, inst_cat='RV',
                                 l_iterative_removal=l_iterative_removal,
                                 compute_raw_models_func=compute_raw_models_core,
                                 remove_add_model_components_func=remove_add_model_components,
                                 kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                 compute_GP_model=compute_GP_model,
                                 split_GP_computation=split_GP_computation,
                                 d_name_component_removed_to_print=d_name_component_removed_to_print,
                                 l_1_model_4_alldst=['model', 'stellar_var', 'GP'],
                                 show_dict=show_dict, show_removed_in_previousrow=show_removed_in_previousrow,
                                 datasetname4model=datasetname4model,
                                 datasim_kwargs=datasim_kwargs,
                                 datasetnames=datasetnames,
                                 amplitude_fact=RV_fact, unit=RV_unit,
                                 create_axes_kwargs=create_axes_kwargs,
                                 TS_kwargs=TS_kwargs,
                                 GLSP_kwargs=GLSP_kwargs,
                                 suptitle_kwargs=suptitle_kwargs,
                                 fontsize=fontsize,
                                 # get_key_compute_model_func=get_key_compute_model,
                                 )


def remove_add_model_components(model, remove_dict, add_dict, extension, extension_raw, models, amplitude_fact):
    """
    Arguments
    ---------
    amplitude_fact  : float
        Not used but required for the standardisation of this function. It is used in lc_plots.remove_add_model_components
    """
    # Remove components if needed
    for key, do in remove_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['stellar_var', 'inst_var', 'decorrelation_likelihood', 'GP', 'model', 'data']:
                model -= models[key + extension + extension_raw]
            elif key == 'decorrelation':
                for model_part in models[key + extension + extension_raw]:
                    if model_part == "add_2_totalrv":
                        model -= models[key + extension + extension_raw]['add_2_totalrv']
                    else:
                        logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")
    # Add components if needed
    for key, do in add_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['stellar_var', 'inst_var', 'decorrelation_likelihood', 'GP', 'model', 'data']:
                model += models[key + extension + extension_raw]
            elif key == 'decorrelation':
                for model_part in models[key + extension + extension_raw]:
                    if model_part == "add_2_totalrv":
                        model += models[key + extension + extension_raw]['add_2_totalrv']
                    else:
                        logger.error(f"Decorrelation of model part {model_part} is not currently taken into account by this function.")
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")

    return model


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
    else:
        return is_valid_model_available_core(key_model=key_model, datasetname=datasetname, post_instance=post_instance)
