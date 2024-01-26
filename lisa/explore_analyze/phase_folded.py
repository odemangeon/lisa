"""
Module to create phase folded plots

@TODO:
"""
from matplotlib.pyplot import figure
from numpy import (linspace, inf, min, max, arange, std, logical_and, zeros, where, sqrt, sum, power,
                   nan, nanstd, concatenate, ones_like, nansum
                   )
from copy import copy
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec
from PyAstronomy.pyasl import foldAt
from scipy.stats import binned_statistic

from .misc import (AandA_fontsize, check_spec_data_or_resi, check_row4datasetname, check_datasetnameformodel4row,
                   check_spec_by_column_or_row, check_spec_for_data_or_resi_by_column_or_row, do_suptitle,
                   get_pl_kwargs, check_kwargs_by_column_and_row, define_x_or_y_lims, update_data_binned_label,
                   print_rms, set_legend, AandA_full_width, default_figheight_factor
                   )
from .core_compute_load import (load_datasets_and_models, compute_and_plot_model, get_key_compute_model,
                                is_valid_model_available
                                )
from ..emcee_tools import emcee_tools as et


def create_phasefolded_plots(post_instance, df_fittedval,
                             compute_raw_models_func, remove_add_model_components_func,
                             kwargs_compute_model_4_key_model, l_valid_model,
                             y_name, inst_cat,
                             d_name_component_removed_to_print=None,
                             datasim_kwargs=None, planets=None, planets_remove_or_add_dict=None, periods=None,
                             periods_remove_or_add_dict=None,
                             datasetnames=None, row4datasetname=None,
                             datasetnameformodel4row=None, npt_model=1000,
                             phasefold_central_phase=0.,
                             amplitude_fact=1., unit=None,
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
                             fontsize=AandA_fontsize,
                             get_key_compute_model_func=get_key_compute_model,
                             is_valid_model_available_func=is_valid_model_available,
                             kwargs_is_valid_model_available=None,
                             kwargs_get_key_compute_model=None,
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
        Dictionary of kwargs that will be passed to check_kwargs_by_column_and_row in arg kwargs_user to be properly define for each
        column (planet name) and each row (index of the row) and then passed to set_legend for each column and each row.
    show_datasetnames  : bool
        If True, show the datasetnames in the corner of the plots
    suptitle_kwargs : dict
        Dictionary which defines the properties of the suptitle. See docstring of do_suptitle for details
    show_title_labels_ticklabels : dict of bool
        Defines whether or not to show the title, xlabel, ylabel, xticklabels, yticklabels.
    LC_unit        : str or None
        String giving the unit of the LCs
    fig            : Figure
        Figure instance (provided by the styler)
    gs             : GridSpec
        If provided should have been made from fig, meaning that it doesn't make sense to provide gs without providing fig.
        It should be a Gridspec with ncols=1 and nrows according to row4datasetname

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
    # Create figure if needed
    if fig is None:
        fig = figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor))

    # Make sure that create_axes_kwargs is well defined
    create_axes_kwargs_user = create_axes_kwargs if create_axes_kwargs is not None else {}
    create_axes_kwargs = {'main_gridspec': {}, 'add_axeswithsharex': {"height_ratios": (3, 1)}, 'gs_from_sps': {}}
    for key in create_axes_kwargs_user:
        if key in create_axes_kwargs:
            create_axes_kwargs[key].update(create_axes_kwargs_user[key])
        else:
            raise ValueError(f"{key} is not a valid key for create_axes_kwargs, should be in ['main_gridspec', 'add_axeswithsharex', 'gs_from_sps']")

    # Make sure that rms_kwargs is well defined
    rms_kwargs_user = rms_kwargs if rms_kwargs is not None else {}
    rms_kwargs = {'do': True, 'format': '.1e'}
    rms_kwargs.update(rms_kwargs_user)

    # Make sure that indicate_y_outliers is well defined
    indicate_y_outliers = check_spec_data_or_resi(spec_user=indicate_y_outliers, l_type_spec=[bool], spec_def=True)

    # Make sure that pad is well defined
    pad = check_spec_data_or_resi(spec_user=pad, l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

    # If no dataset name is provided get all the available LC datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat=inst_cat, sortby_instcat=False, sortby_instname=False)

    # Define on which rows the datasets are plots using the row4datasetname input
    row4datasetname, datasetnames4rowidx = check_row4datasetname(row4datasetname=row4datasetname, datasetnames=datasetnames)
    nb_rows = len(datasetnames4rowidx)
    datasetnameformodel4row = check_datasetnameformodel4row(datasetnameformodel4row=datasetnameformodel4row, datasetnames4rowidx=datasetnames4rowidx)

    # Create the GridSpec
    gs_provided = not(gs is None)
    if not(gs_provided):
        gs = GridSpec(figure=fig, nrows=nb_rows, ncols=1, **create_axes_kwargs['main_gridspec'])
    else:
        if nb_rows > 1:
            raise ValueError("You can only provide gs if there is only one row requireds")
        
    # If no planet name is provided get all the available LC datasets and get all the planets in the model
    all_planets = list(post_instance.model.planets.keys())
    all_planets.sort()
    if planets is None:
        planets = copy(all_planets)
    nplanet = len(planets)

    # Make sure that periods is well defined
    if periods is None:
        periods = []
    nperiod = len(periods)

    # Make sure that planets_remove_or_add_dict is well defined
    if planets_remove_or_add_dict is None:
        planets_remove_or_add_dict = {}

    # Make sure that periods_remove_or_add_dict is well defined
    if periods_remove_or_add_dict is None:
        periods_remove_or_add_dict = {}

    # Make sure that xlims is well defined
    xlims = check_spec_by_column_or_row(spec_user=xlims, l_row_name=list(range(nb_rows)), l_col_name=planets,
                                        l_type_spec=[tuple, list], spec_def=(None, None)
                                        )

    # Make sure that ylims is well defined
    ylims = check_spec_for_data_or_resi_by_column_or_row(spec_user=ylims, l_row_name=list(range(nb_rows)),
                                                         l_col_name=planets, l_type_spec=[tuple, list],
                                                         spec_def={'data': None, 'resi': None}
                                                         )
    # Make sure that legend_kwargs is well defined
    legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=legend_kwargs, l_row_name=list(range(nb_rows)),
                                                   l_col_name=list(range(nplanet + nperiod)), kwargs_def={'do': False},
                                                   kwargs_init={0: {0: {'do': True}}}
                                                   )
    
    # Make sure that show_title_labels_ticklabels is well define
    if show_title_labels_ticklabels is None:
        show_title_labels_ticklabels = {}

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
                                  kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                  )

    # Do the suptitle
    do_suptitle(fig=fig, post_instance=post_instance, datasetnames=datasetnames, fontsize=fontsize,
                dico_models=dico_load["models"], model_removed_or_add_dict=kwargs_compute_model_4_key_model["model"],
                data_remove_or_add_dict=kwargs_compute_model_4_key_model["data"], suptitle_kwargs=suptitle_kwargs
                )

    # Set the plots keywords arguments for each dataset
    # Define the default values
    (pl_kwarg_final, pl_kwarg_jitter, pl_show_error
     ) = get_pl_kwargs(pl_kwargs=pl_kwargs, dico_nb_dstperinsts=dico_load['dico_nb_dstperinsts'], datasetnames=datasetnames,
                       bin_size=exptime_bin, one_binning_per_row=one_binning_per_row,
                       nb_rows=nb_rows, alpha_def_data=0.1, color_def_data="k", show_error_data_def=False)

    # Init the outputs
    computed_models = {}

    #################################
    # Main row loop: For each row ...
    #################################
    axes_data, axes_resi = {}, {}
    remove_or_add_dict_planet_default = planets_remove_or_add_dict.get("all", {})
    for i_row in range(nb_rows):

        #################################################################
        # Create one pair (data, residuals) of axes per planet and period
        #################################################################
        if gs_provided:
            subplotspec = gs
        else:
            subplotspec=gs[i_row]
        (axes_data[i_row], axes_resi[i_row]
         ) = et.add_twoaxeswithsharex_perplanet(subplotspec=subplotspec, nplanet=nplanet + nperiod, fig=fig, sharey=sharey,
                                                gs_from_sps_kw=create_axes_kwargs['gs_from_sps'],
                                                add_axeswithsharex_kw=create_axes_kwargs['add_axeswithsharex']
                                                )

        #######################################
        # Main planet loop: For each planet ...
        #######################################
        for i_col, (planetorperiod_name, is_planet) in enumerate(zip(planets + periods, [True for pl_name in planets] + [False for per in periods])):

            ####################################
            # Init the outputs per period/planet
            ####################################
            if planetorperiod_name not in computed_models:
                computed_models[planetorperiod_name] = {}

            #####################################
            # Format ticks, set labels and titles
            #####################################
            # Set ticks
            axes_data[i_row][i_col].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_data[i_row][i_col].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False)
            axes_data[i_row][i_col].xaxis.set_minor_locator(AutoMinorLocator())
            axes_data[i_row][i_col].yaxis.set_minor_locator(AutoMinorLocator())
            axes_data[i_row][i_col].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_data[i_row][i_col].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            axes_resi[i_row][i_col].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_resi[i_row][i_col].yaxis.set_minor_locator(AutoMinorLocator())
            axes_resi[i_row][i_col].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True)
            axes_resi[i_row][i_col].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_resi[i_row][i_col].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            if i_col != 0:
                axes_data[i_row][i_col].tick_params(axis="both", labelleft=False)
                axes_resi[i_row][i_col].tick_params(axis="both", labelleft=False)
            # Set title with planet name on the first row
            if (i_row == 0) and show_title_labels_ticklabels.get('title', True):
                if is_planet:
                    axes_data[i_row][i_col].set_title(f"Planet {planetorperiod_name}", fontsize=fontsize)
                else:
                    axes_data[i_row][i_col].set_title(f"Period {planetorperiod_name:.2f}", fontsize=fontsize)
            # Set x label for the last row
            if (i_row == nb_rows - 1) and show_title_labels_ticklabels.get('xlabel', True):
                if show_time_from_tic:
                    axes_resi[i_row][i_col].set_xlabel(f"Time from mid-transit [{time_unit}]", fontsize=fontsize)
                else:
                    axes_resi[i_row][i_col].set_xlabel("Orbital phase", fontsize=fontsize)
            # Set y labels on the first column and align them, also set the Anchor boxes
            if (i_col == 0) and show_title_labels_ticklabels.get('ylabel', True):
                ylabel_data = f"{y_name} [{unit}]" if unit is not None else f"{y_name}"
                ylabel_resi = f"O - C [{unit}]" if unit is not None else "O - C"
                axes_data[i_row][i_col].set_ylabel(ylabel_data, fontsize=fontsize)
                axes_resi[i_row][i_col].set_ylabel(ylabel_resi, fontsize=fontsize)
            # Hide tick labels if needed
            if not(show_title_labels_ticklabels.get('xticklabels', True)):
                axes_data[i_row][i_col].xaxis.set_tick_params(labelbottom=False)
                axes_resi[i_row][i_col].xaxis.set_tick_params(labelbottom=False)
            if not(show_title_labels_ticklabels.get('yticklabels', True)):
                axes_data[i_row][i_col].yaxis.set_tick_params(labelleft=False)
                axes_resi[i_row][i_col].yaxis.set_tick_params(labelleft=False)

            ####################################################################################################
            # Compute the x_values (time or phase depending on show_time_from_tic) associated to the time values
            ####################################################################################################
            # Get the period and time of inferior conjunction
            if is_planet:
                Per = df_fittedval.loc[post_instance.model.planets[planetorperiod_name].P.full_name]["value"]
                tc = df_fittedval.loc[post_instance.model.planets[planetorperiod_name].tic.full_name]["value"]
            else:
                Per = planetorperiod_name
                tc = 0

            # Get the limits for the x axis for all planets and all row and set the default values
            x_min, x_max = define_x_or_y_lims(x_or_ylims=xlims, row_name=i_row, col_name=planetorperiod_name)

            # Compute the phase or time (x_values) corresponding to each point in each dataset and the minimum and maximum of all dataset for the row
            x_values = OrderedDict()
            x_min_data = inf
            x_max_data = -inf
            for datasetname in datasetnames4rowidx[i_row]:
                phases_dst = (foldAt(dico_load['times'][datasetname], Per, T0=(tc + Per * (phasefold_central_phase - 0.5))) + (phasefold_central_phase - 0.5))
                x_values[datasetname] = phases_dst * Per * time_fact if show_time_from_tic else phases_dst
                if min(x_values[datasetname]) < x_min_data:
                    x_min_data = min(x_values[datasetname])
                if max(x_values[datasetname]) > x_max_data:
                    x_max_data = max(x_values[datasetname])

            if x_min is not None:
                if x_min_data < x_min:
                    x_min_data = x_min
            if x_max is not None:
                if x_max_data > x_max:
                    x_max_data = x_max

            # Define the bins
            if exptime_bin > 0.:
                bin_size_unit = f"{time_unit}" if show_time_from_tic else "orb. phase"
                update_data_binned_label(pl_kwarg=pl_kwarg_final, key_data_binned="data_binned", datasetnames=datasetnames, bin_size=exptime_bin,
                                         bin_size_unit=bin_size_unit, one_binning_per_row=one_binning_per_row,
                                         nb_rows=nb_rows)
                bins = arange(x_min_data, x_max_data + exptime_bin, exptime_bin)
                midbins = bins[:-1] + exptime_bin / 2
                nbins = len(bins) - 1

            # Define time for evaluating the plotting the model
            tmin_model = tc + x_min_data / time_fact if show_time_from_tic else tc + Per * x_min_data
            tmax_model = tc + x_max_data / time_fact if show_time_from_tic else tc + Per * x_max_data

            #####################################################
            # Main dataset loop for the row: For each dataset ...
            #####################################################
            data_plorper = OrderedDict()
            text_rms = OrderedDict()
            text_rms_binned = OrderedDict()
            for datasetname in datasetnames4rowidx[i_row]:
                # Init computed_models[planetorperiod_name] for the dataset
                computed_models[planetorperiod_name][datasetname] = {}

                ################################################################################
                # Compute the data for the planet (removing the contribution from other planets)
                ################################################################################
                data_plorper[datasetname] = dico_load['datas'][datasetname].copy()
                # Compute and remove the other planet contribution
                for plnt in all_planets:
                    if plnt == planetorperiod_name:
                        continue
                    else:
                        model_pl_only = post_instance.compute_model(tsim=dico_load['times'][datasetname], dataset_name=datasetname,
                                                                    param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                                                    key_obj=f"{plnt}", datasim_kwargs=datasim_kwargs,
                                                                    include_gp=False
                                                                    )
                        model_pl_only *= amplitude_fact
                        data_plorper[datasetname] = data_plorper[datasetname] - model_pl_only

                # Add the data for this planet to dico_load
                if f'datas_{planetorperiod_name}' not in dico_load:
                    dico_load[f'datas_{planetorperiod_name}'] = {}
                dico_load[f'datas_{planetorperiod_name}'][datasetname] = data_plorper[datasetname].copy()

                ###############
                # Plot the data
                ###############
                if pl_show_error[datasetname]["data"]:
                    ebcont = axes_data[i_row][i_col].errorbar(x_values[datasetname], y=data_plorper[datasetname],
                                                              yerr=dico_load['data_errs'][datasetname], **pl_kwarg_final[datasetname]['data'])
                    if not("ecolor" in pl_kwarg_jitter[datasetname]["data"]):
                        pl_kwarg_jitter[datasetname]["data"]["ecolor"] = ebcont[0].get_color()
                    if not("color" in pl_kwarg_final[datasetname]["data"]):
                        pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
                    if dico_load['has_jitters'][datasetname]:
                        axes_data[i_row][i_col].errorbar(x_values[datasetname], y=data_plorper[datasetname],
                                                        yerr=dico_load['data_err_jitters'][datasetname], **pl_kwarg_jitter[datasetname]["data"])
                else:
                    axes_data[i_row][i_col].errorbar(x_values[datasetname], y=data_plorper[datasetname], **pl_kwarg_final[datasetname]['data'])

                # Store phasefolded times and datas in dico_load
                if f'phase_folded_times_{planetorperiod_name}' not in dico_load:
                    dico_load[f'phase_folded_times_{planetorperiod_name}'] = {"show_time_from_tic": show_time_from_tic}
                    dico_load[f'phase_folded_datas_{planetorperiod_name}'] = {}
                dico_load[f'phase_folded_times_{planetorperiod_name}'][datasetname] = x_values[datasetname]
                dico_load[f'phase_folded_datas_{planetorperiod_name}'][datasetname] = data_plorper[datasetname]

                ####################
                # Plot the residuals
                ####################
                if pl_show_error[datasetname]["data"]:
                    ebcont = axes_resi[i_row][i_col].errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], yerr=dico_load['data_errs'][datasetname], **pl_kwarg_final[datasetname]['data'])
                    if dico_load['has_jitters'][datasetname]:
                        axes_resi[i_row][i_col].errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], yerr=dico_load['data_err_jitters'][datasetname], **pl_kwarg_jitter[datasetname]["data"])
                else:
                    axes_resi[i_row][i_col].errorbar(x_values[datasetname], y=dico_load['residuals'][datasetname], **pl_kwarg_final[datasetname]['data'])
                # Compute rms of the residuals and print it on the top of the residuals graphs
                text_rms_template = f"{{:{rms_kwargs['format']}}}"
                text_rms[datasetname] = text_rms_template.format(std(dico_load['residuals'][datasetname][logical_and(x_values[datasetname] > x_min_data, x_values[datasetname] < x_max_data)]))
                if is_planet:
                    text = f'planet {planetorperiod_name}'
                else:
                    text = f'period {planetorperiod_name:.2f}'
                print(f"RMS {datasetname} (plot {text}) = {text_rms[datasetname]} {unit} (raw cadence)")

                #########################################
                # Compute and plot the oversampled models
                #########################################
                if is_planet:
                    if (datasetnameformodel4row[i_row] == datasetname) or (datasetnameformodel4row[i_row] == 'all'):
                        remove_dict = planets_remove_or_add_dict.get(planetorperiod_name, remove_or_add_dict_planet_default).get("remove_dict", {})
                        add_dict = planets_remove_or_add_dict.get(planetorperiod_name, remove_or_add_dict_planet_default).get("add_dict", {})
                        computed_models[planetorperiod_name][datasetname]['tsim'] = linspace(tmin_model, tmax_model, npt_model)
                        computed_models[planetorperiod_name][datasetname]['xsim'] = linspace(x_min_data, x_max_data, npt_model)
                        (computed_models[planetorperiod_name][datasetname], pl_kwarg_final
                        ) = compute_and_plot_model(tsim=computed_models[planetorperiod_name][datasetname]['tsim'],
                                                   key_model=planetorperiod_name,
                                                   datasetname=datasetname, post_instance=post_instance,
                                                   df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                   amplitude_fact=amplitude_fact,
                                                   compute_raw_models_func=compute_raw_models_func,
                                                   remove_add_model_components_func=remove_add_model_components_func,
                                                   key_pl_kwarg="model",
                                                   remove_dict=remove_dict,
                                                   add_dict=add_dict, compute_binned=show_binned_model,
                                                   exptime_bin=exptime_bin, supersamp_bin_model=supersamp_bin_model,
                                                   fact_tsim_to_xsim=(time_fact if show_time_from_tic else 1 / Per),  # I think this is useless since xsim superseeds it
                                                   xsim=computed_models[planetorperiod_name][datasetname]['xsim'],
                                                   time_unit=time_unit,
                                                   plot_unbinned=True, plot_binned=show_binned_model, ax=axes_data[i_row][i_col],
                                                   pl_kwarg=pl_kwarg_final,
                                                   models=computed_models[planetorperiod_name][datasetname],
                                                   l_valid_model=l_valid_model,
                                                   get_key_compute_model_func=get_key_compute_model_func,
                                                   is_valid_model_available_func=is_valid_model_available_func,
                                                   kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                                   kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                   )
                else:
                    # Add/Remove the component requested in periods_remove_or_add_dict
                    (computed_models[planetorperiod_name][datasetname], pl_kwarg_final
                     ) = compute_and_plot_model(tsim=dico_load['times'][datasetname], key_model=f'zeros_{planetorperiod_name}', datasetname=datasetname, post_instance=post_instance, 
                                                df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs, amplitude_fact=amplitude_fact,
                                                compute_raw_models_func=compute_raw_models_func, remove_add_model_components_func=remove_add_model_components_func,
                                                remove_dict=periods_remove_or_add_dict[planetorperiod_name].get('remove_dict', None), 
                                                add_dict=periods_remove_or_add_dict[planetorperiod_name].get('add_dict', None), compute_binned=False,
                                                exptime_bin=None, supersamp_bin_model=None, fact_tsim_to_xsim=None, xsim=None, time_unit=None,
                                                plot_unbinned=False, plot_binned=False, ax=None, pl_kwarg=None, key_pl_kwarg=None,
                                                models=dico_load["models"][datasetname], l_valid_model=l_valid_model, get_key_compute_model_func=get_key_compute_model_func,
                                                is_valid_model_available_func=is_valid_model_available_func, kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                                kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                )

                ################################################################################
                # Compute and Plot the binned data and residuals if one_binning_per_row is False
                ################################################################################
                if not(one_binning_per_row) and (exptime_bin > 0.):
                    # Compute the binned values
                    (bindata, binedges, binnb
                     ) = binned_statistic(x_values[datasetname], data_plorper[datasetname],
                                          statistic=binning_stat, bins=bins,
                                          range=(x_min_data, x_max_data))
                    (binresi, binedges, binnb
                     ) = binned_statistic(x_values[datasetname], dico_load['residuals'][datasetname],
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
                    ebcont_binned = axes_data[i_row][i_col].errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                    if not("color" in pl_kwarg_final[datasetname]["databinned"]):
                        pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
                    if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
                        pl_kwarg_jitter[datasetname]["databinned"]["ecolor"] = pl_kwarg_final[datasetname]["databinned"]["color"]
                    _ = axes_resi[i_row][i_col].errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                    if dico_load['has_jitters'][datasetname] and pl_show_error[datasetname]["databinned"]:
                        _ = axes_data[i_row][i_col].errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"])
                        _ = axes_resi[i_row][i_col].errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[datasetname]["databinned"])

                    # Store phasefolded binned times, data and data errors in dico_load
                    if f'phase_folded_binned_times_{planetorperiod_name}' not in dico_load:
                        dico_load[f'phase_folded_binned_times_{planetorperiod_name}']= {"show_time_from_tic": show_time_from_tic}
                        dico_load[f'phase_folded_binned_datas_{planetorperiod_name}']= {}
                        dico_load[f'phase_folded_binned_data_errs_{planetorperiod_name}']= {}
                        dico_load[f'phase_folded_binned_data_err_jitters_{planetorperiod_name}']= {}
                    dico_load[f'phase_folded_binned_times_{planetorperiod_name}'][datasetname] = midbins
                    dico_load[f'phase_folded_binned_datas_{planetorperiod_name}'][datasetname] = bindata
                    dico_load[f'phase_folded_binned_data_errs_{planetorperiod_name}'][datasetname] = bin_err
                    if dico_load['has_jitters'][datasetname]:
                        dico_load["phase_folded_binned_data_err_jitters"][planetorperiod_name][datasetname] = binstd_jitter

                    # Compute rms of the binned residuals
                    text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
                    text_rms_binned[datasetname] = text_rms_binned_template.format(nanstd(binresi[logical_and(midbins > x_min_data, midbins < x_max_data)]))
                    print(f"RMS {datasetname}: {text_rms_binned[datasetname]} {unit}")

            ################################################################################
            # Compute and Plot the binned data and residuals if one_binning_per_row is True
            ################################################################################
            if one_binning_per_row and (exptime_bin > 0.):
                x_values_row = concatenate([x_values[dst] for dst in datasetnames4rowidx[i_row]])
                # Compute the binned values
                (bindata, binedges, binnb
                 ) = binned_statistic(x_values_row, concatenate([data_plorper[dst] for dst in datasetnames4rowidx[i_row]]),
                                      statistic=binning_stat, bins=bins,
                                      range=(x_min_data, x_max_data))
                (binresi, binedges, binnb
                 ) = binned_statistic(x_values_row, concatenate([dico_load['residuals'][dst] for dst in datasetnames4rowidx[i_row]]),
                                      statistic=binning_stat, bins=bins,
                                      range=(x_min_data, x_max_data))
                # Compute the err on the binned values
                binstd = zeros(nbins)
                if any([dico_load['has_jitters'][dst] for dst in datasetnames4rowidx[i_row]]):
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
                        if any([dico_load['has_jitters'][dst] for dst in datasetnames4rowidx[i_row]]):
                            binstd_jitter[i_bin] = sqrt(nansum(power(data_err_jitter_row[binnb == (i_bin + 1)],
                                                                     2.
                                                                     )
                                                               ) /
                                                        bincount[i_bin]**2
                                                        )
                    else:
                        binstd[i_bin] = nan
                        if any([dico_load['has_jitters'][dst] for dst in datasetnames4rowidx[i_row]]):
                            binstd_jitter[i_bin] = nan
                # Plot the binned data
                bin_err = binstd if pl_show_error[f"row{i_row}"] else None
                ebcont_binned = axes_data[i_row][i_col].errorbar(midbins, bindata, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"])
                if not("color" in pl_kwarg_final[f"row{i_row}"]):
                    pl_kwarg_final[f"row{i_row}"]["color"] = ebcont_binned[0].get_color()
                if not("ecolor" in pl_kwarg_jitter[f"row{i_row}"]):
                    pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_final[f"row{i_row}"]["color"]
                _ = axes_resi[i_row][i_col].errorbar(midbins, binresi, yerr=bin_err, **pl_kwarg_final[f"row{i_row}"])
                if any([dico_load['has_jitters'][dst] for dst in datasetnames4rowidx[i_row]]) and pl_show_error[f"row{i_row}"]:
                    _ = axes_data[i_row][i_col].errorbar(midbins, bindata, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"])
                    _ = axes_resi[i_row][i_col].errorbar(midbins, binresi, yerr=binstd_jitter, **pl_kwarg_jitter[f"row{i_row}"])

                # Store phasefolded binned times, data and data errors in dico_load
                if f'phase_folded_binned_times_{i_row}' not in dico_load:
                    dico_load[f'phase_folded_binned_times_{i_row}']= {"show_time_from_tic": show_time_from_tic}
                    dico_load[f'phase_folded_binned_datas_{i_row}']= {}
                    dico_load[f'phase_folded_binned_data_errs_{i_row}']= {}
                    dico_load[f'phase_folded_binned_data_err_jitters_{i_row}']= {}
                dico_load[f'phase_folded_binned_times_{i_row}'] = midbins
                dico_load[f'phase_folded_binned_datas_{i_row}'] = bindata
                dico_load[f'phase_folded_binned_data_errs_{i_row}'] = bin_err
                if dico_load['has_jitters'][datasetname]:
                    dico_load[f"phase_folded_binned_data_err_jitters_{i_row}"] = binstd_jitter

                # Compute rms of the binned residuals
                text_rms_binned_template = f"{{:{rms_kwargs['format']}}} (bin)"
                text_rms_binned[f"row{i_row}"] = text_rms_binned_template.format(nanstd(binresi[logical_and(midbins > x_min_data, midbins < x_max_data)]))
                print(f"RMS row {i_row}: {text_rms_binned[f'row{i_row}']} {unit}")

            ###########
            # Write rms
            ###########
            # WARNING, TO BE IMPROVED for more than one dataset
            if rms_kwargs['do']:
                print_rms(ax=axes_resi[i_row][i_col], text_pos=(0.0, 1.05), row_name=i_row,
                          start_with_rmsequal=(i_col == 0), add_rms_row=(i_col == 0),
                          datasetnames_in_row=datasetnames4rowidx[i_row], pl_kwargs=pl_kwarg_final,
                          text_rms=text_rms, text_rms_binned=text_rms_binned, fontsize=fontsize, unit=unit)

            ###################################
            # Set ylims and indicate_y_outliers
            ###################################
            # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
            for axe, data_or_resi, points, in zip((axes_data[i_row][i_col], axes_resi[i_row][i_col]),
                                                  ("data", "resi"),
                                                  (data_plorper, dico_load['residuals']),
                                                  ):
                # Set the y axis limits
                ylims_to_use = define_x_or_y_lims(x_or_ylims=ylims[data_or_resi], row_name=i_row, col_name=planetorperiod_name)
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

            # Set the x axis limits
            if force_xlims:
                axes_data[i_row][i_col].set_xlim((x_min, x_max))
            else:
                axes_data[i_row][i_col].set_xlim((x_min_data, x_max_data))

            ##########################
            # Set the legend if needed
            ##########################
            set_legend(ax=axes_data[i_row][i_col], legend_kwargs=legend_kwargs[i_col][i_row], fontsize_def=fontsize)

    return dico_load, computed_models
