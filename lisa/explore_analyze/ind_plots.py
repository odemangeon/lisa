#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create plots specifically for radial velocity data

@TODO:
"""
import numpy as np
from logging import getLogger

from copy import copy
from collections import defaultdict

from .phase_folded import create_phasefolded_plots
from .ts_and_glsp import create_TSNGLSP_plots
from .misc import AandA_fontsize
from ..posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add
from ..posterior.core.model.core_model import Core_Model


key_whole = Core_Model.key_whole

day2sec = 24 * 60 * 60

# managers
mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()

# logger
logger = getLogger()


remove_dict_def_TS = {'GP_dataNmodel': True, 'poly_inst_var': True, 'poly_sys_var': True, 'GP_residual': True}
remove_dict_def_PF = {'GP_dataNmodel': True, 'poly_inst_var': True, 'poly_sys_var': True, 'GP_residual': True}
add_dict_def_PF = {'GP_dataNmodel': False, 'poly_inst_var': False, 'poly_sys_var': False, 'GP_residual': False}
add_dict_def_TS = {'GP_dataNmodel': False, 'poly_inst_var': False, 'poly_sys_var': False, 'GP_residual': False}

# y_name = "RV"

d_name_component_removed_to_print = {'poly_inst_var': "Poly Inst Var", 'poly_sys_var': "Poly Sys var",
                                     'GP_dataNmodel': "GP",
                                     }


def create_IND_phasefolded_plots(fig, post_instance, df_fittedval, IND_subcat, datasim_kwargs=None,
                                 planets=None,
                                 datasetnames=None, row4datasetname=None,
                                 datasetnameformodel4row=None, npt_model=1000,
                                 phasefold_central_phase=0.,
                                 IND_fact=1.,
                                 show_time_from_tic=False, time_fact=24, time_unit="h",
                                 exptime_bin=0., binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                                 one_binning_per_row=True,
                                 sharey=False, create_axes_kwargs=None, pad=None, indicate_y_outliers=None,
                                 pl_kwargs=None,
                                 xlims=None, force_xlims=False, ylims=None,
                                 rms_kwargs=None,
                                 legend_kwargs=None,
                                 show_datasetnames=True,
                                 suptitle_kwargs=None,
                                 IND_unit="$km/s$",
                                 fontsize=AandA_fontsize,
                                 ):
    """Produce clean IND phase folded plots of a system.

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
    datasetnames  : list of String
        List providing the datasets to load and use
    row4datasetname    : dict of int
        Dictionary saying which dataset to plot on which row. The format is:
        {"<dataset_name>": <int giving the row index starting at 0>, ...}
    datasetnameformodel4row : list of str
        List saying which datasetmodel to use to compute the oversampled model of each row
    npt_model     : int
        Number of points used to simulated the model
    phasefold_central_phase : float
        orbital phase (between 0 and 1) that will be at the center of phase domain for the plot.
        0 correspond to the transit and means that the phases for the plot will go from -0.5 to 0.5
        0.5 correspond to the secondary transit and means that the phases for the plot will go from 0 to 1.
    remove_GP     : Boolean
        If True the GP model is remove from the data for the plot.
    IND_fact       : float
        Factor to apply to the IND
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
        Dictionary with keys a dataset name (ex: "IND-FWHM_HD209458_ESPRESSO_0") or "model" or "modelbinned" or "databinned" and values
        a dictionary that will be passed as keyword arguments associated the plotting functions.
        You can also add a 'jitter' key with value a dictionary that will contain the changes that you
        want to make for the update error bars due to potential jitter.
    xlims       : dict
    force_xlims : bool
        By default, the maximum xlims is the extrema of the data. So if the user provides larger xlims,
        the actual xlims will be reduced. This will not happen if you set force_xlims to True
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
    IND_unit        : str
        String giving the unit of the INDs
    """
    create_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                             load_datasets_and_models_func=load_datasets_and_models_IND,
                             compute_and_plot_oversamp_model_func=compute_and_plot_model_IND,
                             remove_dict={},
                             add_dict={},
                             remove_dict_def=remove_dict_def_PF,
                             add_dict_def=add_dict_def_PF,
                             y_name=IND_subcat, inst_cat=f'IND-{IND_subcat}',
                             d_name_component_removed_to_print=d_name_component_removed_to_print,
                             datasim_kwargs=datasim_kwargs, planets=planets,
                             datasetnames=datasetnames, row4datasetname=row4datasetname,
                             datasetnameformodel4row=datasetnameformodel4row,
                             npt_model=npt_model, phasefold_central_phase=phasefold_central_phase,
                             amplitude_fact=IND_fact, show_time_from_tic=show_time_from_tic, time_fact=time_fact,
                             time_unit=time_unit, exptime_bin=exptime_bin, binning_stat=binning_stat,
                             supersamp_bin_model=supersamp_bin_model, show_binned_model=show_binned_model,
                             one_binning_per_row=one_binning_per_row,
                             sharey=sharey, create_axes_kwargs=create_axes_kwargs, pad=pad, indicate_y_outliers=indicate_y_outliers,
                             pl_kwargs=pl_kwargs, xlims=xlims, force_xlims=force_xlims, ylims=ylims,
                             rms_kwargs=rms_kwargs, legend_kwargs=legend_kwargs, show_datasetnames=show_datasetnames,
                             suptitle_kwargs=suptitle_kwargs,
                             unit=IND_unit, fontsize=fontsize
                             )


def create_IND_TSNGLSP_plots(fig, post_instance, df_fittedval, IND_subcat, datasim_kwargs=None,
                             datasetnames=None,
                             remove_dict=None,
                             show_dict=None, datasetnames4model4row=None,
                             TS_kwargs=None, GLSP_kwargs=None,
                             create_axes_kwargs=None,
                             suptitle_kwargs=None,
                             IND_fact=1., IND_unit="$km/s$", fontsize=AandA_fontsize
                             ):
    """Produce clean IND time series and generalized Lomb-Scargle plots of a system.

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
            - 'gridspec_kwargs': The content of this entry should be a dictionary which will be passed to
                GridSpec (GridSpec(..., **fig_param['gridspec_kwargs'])) instance creation with create the gridspec
                separating the TS and GLSP
            - 'add_axeswithsharex_kw': The content of this entry should be a dictionary which will be
                passed to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., add_axeswithsharex_kw=fig_param['add_axeswithsharex_kw'])
                function creating two axes data and residuals per planet.
            - 'fontsize' : Int specifiying the fontsize
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
            - 't_lims': None or Iterable of 2 float (Def: None)
                Specificy the time limits for the plot
            - 't_lims_zoom': None or Iterable of 2 float (Def: None)
                If provided a zoom on the right of the main plot will be drawn.
                This gives the beginning and end time for the zoom
            - 't_unit': str (Def: days)
                String that is going to be used to give the unit (and reference system) of the time.
            - 'pl_kwargs': dict
                Dictionary with keys a dataset name (ex: "IND-FWHM_HD209458_ESPRESSO_0") or "model" or "GP"
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
    IND_fact       : float
        Factor to apply to the IND
    IND_unit        : str
        String giving the unit of the INDs
    """
    create_TSNGLSP_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                         load_datasets_and_models_func=lambda *args, **kwargs: load_datasets_and_models_IND(IND_subcat=IND_subcat, *args, **kwargs),
                         compute_and_plot_oversamp_model_func=compute_and_plot_model_IND,
                         y_name=IND_subcat, inst_cat=f'IND-{IND_subcat}',
                         d_name_component_removed_to_print=d_name_component_removed_to_print,
                         remove_dict=remove_dict, remove_dict_def=remove_dict_def_TS,
                         add_dict={}, add_dict_def=add_dict_def_TS,
                         show_dict=show_dict, l_model_1_per_row=['model', 'stellar_var', 'GP'],
                         datasetnames4model4row=datasetnames4model4row,
                         datasim_kwargs=datasim_kwargs,
                         datasetnames=datasetnames,
                         amplitude_fact=IND_fact, unit=IND_unit,
                         create_axes_kwargs=create_axes_kwargs,
                         TS_kwargs=TS_kwargs,
                         GLSP_kwargs=GLSP_kwargs,
                         suptitle_kwargs=suptitle_kwargs,
                         fontsize=fontsize,
                         )


def load_datasets_and_models_IND(IND_subcat, datasetnames, post_instance, datasim_kwargs, df_fittedval,
                                 amplitude_fact, remove_dict, add_dict, remove_dict_def, add_dict_def,
                                 ):
    """Load the dataset and models for later use by the other two function
    """
    remove_dict_user = remove_dict
    remove_dict = copy(remove_dict_def)
    remove_dict.update(remove_dict_user)

    add_dict_user = add_dict
    add_dict = copy(add_dict_def)
    add_dict.update(add_dict_user)

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
    poly_inst_vars = {}
    poly_sys_vars = {}
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

        ######################################################################
        # Compute the polynomial variations (poly_sys_vars and poly_inst_vars)
        ######################################################################
        poly_model = post_instance.model.instcat_models["IND"].get_modelclass_4_modelname(model_name='polynomial')

        ############################################################################################
        ## Compute the polynomial variations for the system (sys_vars) to later remove from the data
        ############################################################################################
        if ((poly_model.get_dico_config(param_container=post_instance.model, prefix=IND_subcat, notexist_ok=True, return_None_if_notexist=True) is not None) and
            (poly_model.get_dico_config(param_container=post_instance.model, prefix=IND_subcat, notexist_ok=True, return_None_if_notexist=True)["do"])
            ):
            model_poly_sys_vars = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
                                                              param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                                              key_obj="poly_sys_var",
                                                              datasim_kwargs=datasim_kwargs, include_gp=False
                                                              )

            if model_poly_sys_vars is not None:
                poly_sys_vars[datasetname] = model_poly_sys_vars

        #################################################################################################
        ## Compute the polynomial variations for the isntruments (isntvars) to later remove from the data
        #################################################################################################
        if ((poly_model.get_dico_config(param_container=inst_mod, prefix=None, notexist_ok=True, return_None_if_notexist=True) is not None) and
            (poly_model.get_dico_config(param_container=inst_mod, prefix=None, notexist_ok=True, return_None_if_notexist=True)["do"])
            ):
            model_poly_inst_vars = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
                                                               param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                                               key_obj="poly_inst_var",
                                                               datasim_kwargs=datasim_kwargs, include_gp=False
                                                               )

            if model_poly_inst_vars is not None:
                poly_inst_vars[datasetname] = model_poly_inst_vars

        #######################################
        # Compute the models and GP predictions
        #######################################
        (model, model_wGP, gp_pred, gp_pred_var
         ) = post_instance.compute_model(tsim=times[datasetname], dataset_name=datasetname,
                                         param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
                                         key_obj=key_whole, datasim_kwargs=datasim_kwargs, include_gp=True
                                         )
        if model_wGP is not None:
            gp_preds[datasetname] = gp_pred
            gp_pred_vars[datasetname] = gp_pred_var

        if (model_wGP is not None) and not(remove_dict['GP_dataNmodel']):
            models[datasetname] = model_wGP
        else:
            models[datasetname] = model

        #######################
        # Compute the residuals
        #######################
        if (model_wGP is not None) and remove_dict['GP_residual']:
            residuals[datasetname] = datas[datasetname] - model_wGP
        else:
            residuals[datasetname] = datas[datasetname] - model

        ################################################################################
        # Remove GP (if needed)
        ################################################################################
        if (model_wGP is not None) and remove_dict['GP_dataNmodel']:
            datas[datasetname] -= gp_pred

        ################################################################################
        # Remove/Add poly_sys_vars (if needed)
        ################################################################################
        if datasetname in poly_sys_vars:
            if remove_dict['poly_sys_var']:
                datas[datasetname] -= poly_sys_vars[datasetname]
                models[datasetname] -= poly_sys_vars[datasetname]
            if add_dict['poly_sys_var']:
                datas[datasetname] += poly_sys_vars[datasetname]
                models[datasetname] += poly_sys_vars[datasetname]

        ################################################################################
        # Remove/Add poly_inst_vars (if needed)
        ################################################################################
        if datasetname in poly_inst_vars:
            if remove_dict['poly_inst_var']:
                datas[datasetname] -= poly_inst_vars[datasetname]
                models[datasetname] -= poly_inst_vars[datasetname]
            if add_dict['poly_inst_var']:
                datas[datasetname] += poly_inst_vars[datasetname]
                models[datasetname] += poly_inst_vars[datasetname]

        ################################################################################
        # Apply IND_fact
        ################################################################################
        datas[datasetname] *= amplitude_fact
        data_errs[datasetname] *= amplitude_fact
        data_err_worwojitters[datasetname] *= amplitude_fact
        residuals[datasetname] *= amplitude_fact
        models[datasetname] *= amplitude_fact
        if model_wGP is not None:
            gp_preds[datasetname] *= amplitude_fact
            gp_pred_vars[datasetname] *= amplitude_fact**2
        if has_jitters[datasetname]:
            dico_jitters[datasetname]["value"] *= amplitude_fact
            data_err_jitters[datasetname] *= amplitude_fact

    d_remove_from_model = {'poly_sys_var': 'poly_sys_vars', 'poly_inst_var': 'poly_inst_vars',
                           'GP_dataNmodel': 'gp_preds'
                           }
    d_remove_from_data = {'poly_sys_var': 'poly_sys_vars', 'poly_inst_var': 'poly_inst_vars',
                          'GP_dataNmodel': 'gp_preds',
                          }

    return ({'dico_datasets': dico_datasets, 'dico_kwargs': dico_kwargs, 'dico_nb_dstperinsts': dico_nb_dstperinsts,
             'times': times, 'datas': datas, 'data_errs': data_errs, 'data_err_jitters': data_err_jitters,
             'data_err_worwojitters': data_err_worwojitters, 'has_jitters': has_jitters, 'dico_jitters': dico_jitters,
             'models': models, 'gp_preds': gp_preds, 'gp_pred_vars': gp_pred_vars, 'poly_inst_vars': poly_inst_vars,
             'poly_sys_vars': poly_sys_vars,
             'residuals': residuals,
             },
            d_remove_from_model, d_remove_from_data, remove_dict, add_dict,
            )


def compute_and_plot_model_IND(datasetname,
                               post_instance, df_fittedval, key_compute_model,
                               include_gp_model, datasim_kwargs,
                               remove_dict, add_dict, amplitude_fact,
                               tsim, fact_tsim_to_xsim=None,
                               exptime_bin=None, supersamp_bin_model=None,
                               plot=True, ax=None, pl_kwarg=None, key_pl_kwarg=None, show_binned_model=True
                               ):
    """
    """
    remove_dict_user = remove_dict
    remove_dict = copy({'poly_sys_var': False, 'poly_inst_var': False})
    remove_dict.update(remove_dict_user)

    add_dict_user = add_dict
    add_dict = copy({'poly_sys_var': False, 'poly_inst_var': False})
    add_dict.update(add_dict_user)

    # # Define the time vector tsim at which the models will be evaluated
    # tsim = np.linspace(*tlims_model, npt_model)
    # # Define the x vector xsim (corresponding to tsim) at which the models will be plotted
    # if xlims_model is not None:
    #     xsim = np.linspace(*xlims_model, npt_model)
    # else:
    #     xsim = tsim

    if exptime_bin is None:
        exptime_bin = 0.

    if fact_tsim_to_xsim is None:
        fact_tsim_to_xsim = 1.

    xsim = tsim * fact_tsim_to_xsim

    key_pl_kwarg_user = key_pl_kwarg
    models = {}
    for binned in [False, True]:
        if binned:
            if show_binned_model and (exptime_bin > 0.):
                exptime = exptime_bin / fact_tsim_to_xsim
                extension = '_binned'
            else:
                continue
        else:
            exptime = 0.
            key_pl_kwarg = key_pl_kwarg_user
            extension = ''

        # Compute the model
        if include_gp_model:
            (model, model_wGP, gp_pred, gp_pred_var
             ) = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                             param=df_fittedval["value"].values,
                                             l_param_name=list(df_fittedval.index),
                                             key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                             include_gp=include_gp_model,
                                             supersamp=supersamp_bin_model, exptime=exptime
                                             )
        else:
            model = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                param=df_fittedval["value"].values,
                                                l_param_name=list(df_fittedval.index),
                                                key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                                include_gp=include_gp_model,
                                                supersamp=supersamp_bin_model, exptime=exptime
                                                )
            model_wGP = gp_pred = gp_pred_var = None

        if model is None:
            return models, pl_kwarg

        # Remove/Add poly_sys_var if needed
        if (remove_dict['poly_sys_var'] or add_dict['poly_sys_var']) and (datasetname in dico_output_load['poly_sys_vars']):
            model_poly_sys_var = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                             param=df_fittedval["value"].values,
                                                             l_param_name=list(df_fittedval.index),
                                                             key_obj="sys_var", datasim_kwargs=datasim_kwargs,
                                                             include_gp=False,
                                                             supersamp=supersamp_bin_model, exptime=exptime
                                                             )
            if remove_dict['poly_sys_var']:
                model -= model_poly_sys_var
                if model_wGP is not None:
                    model_wGP -= model_poly_sys_var
            if add_dict['poly_sys_var']:
                model += model_poly_sys_var
                if model_wGP is not None:
                    model_wGP += model_poly_sys_var
        # Remove/Add poly_inst_var if needed
        if (remove_dict['poly_inst_var'] or add_dict['poly_inst_var']) and (datasetname in dico_output_load['poly_inst_vars']):
            model_poly_inst_var = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                              param=df_fittedval["value"].values,
                                                              l_param_name=list(df_fittedval.index),
                                                              key_obj="inst_var", datasim_kwargs=datasim_kwargs,
                                                              include_gp=False,
                                                              supersamp=supersamp_bin_model, exptime=exptime
                                                              )
            if remove_dict['poly_inst_var']:
                model -= model_poly_inst_var
                if model_wGP is not None:
                    model_wGP -= model_poly_inst_var
            if add_dict['poly_inst_var']:
                model += model_poly_inst_var
                if model_wGP is not None:
                    model_wGP += model_poly_inst_var
        # Multiply by IND fact
        model *= amplitude_fact
        models[key_compute_model + extension] = model
        if model_wGP is not None:
            model_wGP *= amplitude_fact
            gp_pred *= amplitude_fact
            gp_pred_var *= amplitude_fact**2
            models['model_wGP' + extension] = model_wGP
            models['GP' + extension] = gp_pred
            models['GP_var' + extension] = gp_pred_var

        # Plot the model
        if plot:
            key_pl_kwarg = key_pl_kwarg_user + extension
            ebconts_lines_labels_model = ax.errorbar(xsim, model, **pl_kwarg[datasetname][key_pl_kwarg])
            if not("color" in pl_kwarg[datasetname][key_pl_kwarg]):
                pl_kwarg[datasetname][key_pl_kwarg]["color"] = ebconts_lines_labels_model[0].get_color()
            if not("alpha" in pl_kwarg[datasetname][key_pl_kwarg]):
                pl_kwarg[datasetname][key_pl_kwarg]["alpha"] = ebconts_lines_labels_model[0].get_alpha()
            # Plot the GP
            if model_wGP is not None:
                key_GP = "GP" + extension
                key_GP_err = "GP_err" + extension
                if not("color" in pl_kwarg[datasetname][key_GP]):
                    pl_kwarg[datasetname][key_GP]["color"] = pl_kwarg[datasetname][key_pl_kwarg]["color"]
                if not("color" in pl_kwarg[datasetname]["GP_err"]):
                    pl_kwarg[datasetname][key_GP_err]["color"] = pl_kwarg[datasetname][key_pl_kwarg]["color"]
                if not("alpha" in pl_kwarg[datasetname]["GP"]):
                    pl_kwarg[datasetname][key_GP]["alpha"] = pl_kwarg[datasetname][key_pl_kwarg]["alpha"]
                if not("alpha" in pl_kwarg[datasetname]["GP_err"]):
                    pl_kwarg[datasetname][key_GP_err]["alpha"] = pl_kwarg[datasetname][key_pl_kwarg]["alpha"] / 3
                if not(remove_dict["GP_dataNmodel"]):
                    pl_kwarg[datasetname][key_GP]["label"] = pl_kwarg[datasetname][key_pl_kwarg]['label'] + " + GP"
                    _ = ax.errorbar(tsim, model_wGP, **pl_kwarg[datasetname][key_GP])
                    _ = ax.fill_between(tsim, model_wGP - np.sqrt(gp_pred_var), model_wGP + np.sqrt(gp_pred_var),
                                        **pl_kwarg[datasetname][key_GP_err],
                                        )
                else:
                    _ = ax.errorbar(tsim, gp_pred, **pl_kwarg[datasetname][key_GP])
                    _ = ax.fill_between(tsim, gp_pred - np.sqrt(gp_pred_var), gp_pred + np.sqrt(gp_pred_var),
                                        **pl_kwarg[datasetname][key_GP_err]
                                        )
    return pl_kwarg
