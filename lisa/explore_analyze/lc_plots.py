"""
Module to create plot specifically for light curve data

@TODO:
"""
from loguru import logger
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

l_valid_model = ["model", "1", "contamination", "stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]

dict_model_false = {key: False for key in l_valid_model[1:]}
dict_model_true = {key: True for key in l_valid_model[1:]}

d_name_component_removed_to_print = {'stellar_var': "Stellar Var", 'inst_var': "Inst Var", 'decorrelation': "Decorrelation",
                                     'decorrelation_likelihood': "Decorrelation Likelihood", 'contamination': "Contamination",
                                     'GP': "GP",
                                     }


def create_LC_phasefolded_plots(post_instance, df_fittedval, datasim_kwargs=None,
                                planets=None, planets_remove_or_add_dict=None, periods=None, periods_remove_or_add_dict=None,
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
    """Produce a clean LC phase folded plots of a system.

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
    remove1             : bool
        If True remove one to get an out of transit level of 0 instead of 1.
    remove_contamination    : bool
        It True the contamination of the light curve is removed. If there is contamination, you should always have
        remove_inst_var and remove contamination to True, inst_var depends strongly in contamination, so any other
        thing would not make sense.
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
    LC_fact        : float
        Factor to apply to the LC (ignore if remove1 is False)
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
    for key, default in zip(["GP", "decorrelation_likelihood", "decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [True, True, True, True, remove_contamination, True, remove1]
                            ):
        remove_dict_data[key] = default
    remove_dict_data_err = OrderedDict()
    for key in ["contamination", ]:
        remove_dict_data_err[key] = remove_dict_data[key]
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
    planets_remove_or_add_dict = {"all": {"add_dict": {"1": not(remove1), "contamination": not(remove_contamination)}}}
    return create_phasefolded_plots(post_instance=post_instance, df_fittedval=df_fittedval,
                                    compute_raw_models_func=compute_raw_models,
                                    remove_add_model_components_func=remove_add_model_components,
                                    kwargs_compute_model_4_key_model=kwargs_compute_model_4_key_model,
                                    l_valid_model=l_valid_model,
                                    y_name=y_name, inst_cat='LC', 
                                    d_name_component_removed_to_print=d_name_component_removed_to_print,
                                    datasim_kwargs=datasim_kwargs, 
                                    planets=planets, planets_remove_or_add_dict=planets_remove_or_add_dict,
                                    periods=periods, periods_remove_or_add_dict=periods_remove_or_add_dict,
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
                                    fig=fig, gs=gs
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
    # Define Y axis quantity name 
    y_name = "$\Delta$F / F" if remove_dict.get("1", True) else "(F + $\Delta$F) / F"
    # Define kwargs_compute_model_4_key_model
    remove_dict_model = OrderedDict()
    for key, default in zip(["decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [False, False, False, False, True]
                            ):
        remove_dict_model[key] = remove_dict.get(key, default)
    remove_dict_data = OrderedDict()
    for key, default in zip(["GP", "decorrelation_likelihood", "decorrelation", "inst_var", "contamination", "stellar_var", "1"],
                            [False, False, False, False, False, False, True]
                            ):
        remove_dict_data[key] = remove_dict.get(key, default)
    remove_dict_data_err = OrderedDict()
    for key in ["contamination", ]:
        remove_dict_data_err[key] = remove_dict_data[key]
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
    # Define default values for pl_kwargs data in TS_kwargs
    if TS_kwargs is None:
        TS_kwargs = {}
    pl_kwargs_TS = TS_kwargs.get("pl_kwargs", {})
    if pl_kwargs_TS is None:
        pl_kwargs_TS = {}
    TS_kwargs["pl_kwargs"] = pl_kwargs_TS
    pl_kwargs_TS_all = pl_kwargs_TS.get("all", {})
    pl_kwargs_TS["all"] = pl_kwargs_TS_all
    pl_kwargs_TS_all_data = pl_kwargs_TS_all.get("data", {})
    pl_kwargs_TS_all["data"] = pl_kwargs_TS_all_data
    if "color" not in pl_kwargs_TS_all_data:
        pl_kwargs_TS_all_data["color"] = 'k'
    if "alpha" not in pl_kwargs_TS_all_data:
        pl_kwargs_TS_all_data["alpha"] = 0.1
    # Call the create_TSNGLSP_plots function
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


def remove_add_model_components(model, remove_dict, add_dict, extension, extension_raw, models, amplitude_fact):
    """
    """
    # Remove components if needed
    for key, do in remove_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['1', 'stellar_var', 'inst_var', 'decorr_add_2_totalflux', 'decorrelation_likelihood', 'GP', 'model', 'data']:
                model -= models[key + extension + extension_raw]
            elif key in ['contamination', 'decorr_multiply_2_totalflux']:
                model /= models[key + extension + extension_raw] / amplitude_fact
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")
    # Add components if needed
    for key, do in add_dict.items():
        if do and ((key + extension + extension_raw) in models):
            if key in ['1', 'stellar_var', 'inst_var', 'decorr_add_2_totalflux', 'decorrelation_likelihood', 'GP', 'model', 'data']:
                model += models[key + extension + extension_raw]
            elif key in ['contamination', 'decorr_multiply_2_totalflux']:
                model *= models[key + extension + extension_raw] / amplitude_fact
            else:
                raise NotImplementedError(f"Remove from model is not implement for component {key}")

    return model


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
                       df_fittedval, datasim_kwargs, exptime, supersamp,
                       get_key_compute_model_func=get_key_compute_model,
                       is_valid_model_available_func=is_valid_model_available,
                       kwargs_is_valid_model_available=None,
                       kwargs_get_key_compute_model=None,
                       ):
    """
    """
    if key_model == "1":
        model = ones_like(tsim)
        model_err = None
        return model, model_err
    else:
        return compute_raw_models_core(tsim=tsim, key_model=key_model, l_valid_model=l_valid_model,
                                       datasetname=datasetname, post_instance=post_instance,
                                       df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                       exptime=exptime, supersamp=supersamp, get_key_compute_model_func=get_key_compute_model_func,
                                       is_valid_model_available_func=is_valid_model_available_func,
                                       kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                       )