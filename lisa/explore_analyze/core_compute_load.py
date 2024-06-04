from loguru import logger
from copy import copy
from numpy import zeros_like, sqrt, linspace
from collections import defaultdict, OrderedDict

from .misc import update_model_binned_label, Model2computeNplot
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.model.core_model import Core_Model

# Key for the whole model
key_whole = Core_Model.key_whole

# Set extension for raw models
extension_raw = '_raw'

# managers
mgr_inst_dst = Manager_Inst_Dataset()


def get_key_compute_model(key_model):
    """Get the correct key for the compute_raw_models function.

    Sometimes it's more convenient to use a more explicit key to designate a model in the user interface,
    but better to use a shorter version in the code. This function convert the explicit key into the shorter
    one when it is needed.

    Argument
    --------
    key_model           : str

    Return
    ------
    key_compute_model   : str
    """
    if key_model == "decorrelation":
        key_compute_model = "decorr"
    elif key_model == "model":
        key_compute_model = key_whole
    else:
        key_compute_model = key_model
    return key_compute_model


def is_valid_model_available(key_model, datasetname, post_instance):
    """Return True is key_model corresponds to an existing model for the dataset in the posterior instance.

    Arguments
    ---------
    key_model           : str
    datasetname         : str
    post_instance       : Posterior

    Return
    ------
    valid   : bool
    """
    if key_model == "model":
        return True
    elif key_model == "decorrelation":
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        return post_instance.model.instcat_models[inst_mod.instrument.category].decorrelation_model_config[inst_mod_fullname]["do"]
    elif key_model == "decorrelation_likelihood":
        return f"{datasetname}_decorr_like" in post_instance.datasimulators.dataset_db
    else:
        return False


def compute_and_plot_model(post_instance, df_fittedval, datasim_kwargs,
                           compute_raw_models_func, remove_add_model_components_func,
                           tsim=None, key_model=None, datasetname=None, model2computeNplot=None, time_fact=None,
                           amplitude_fact=1, 
                           remove_dict=None, add_dict=None, compute_only_raw_models=False, 
                           compute_GP_model=True, split_GP_computation=None,
                           compute_binned=True, exptime_bin=None, supersamp_bin_model=None, fact_tsim_to_xsim=None, xsim=None, time_unit=None,
                           plot_unbinned=True, plot_binned=True, ax=None, pl_kwarg=None, key_pl_kwarg=None,
                           models=None, get_key_compute_model_func=get_key_compute_model,
                           kwargs_get_key_compute_model=None,
                           ):
    """Compute and/or plot a model.

    Arguments
    ---------
    tsim                                : array
        Time at which the model should be computed
    key_model                           : str
        Key of the model to compute. This will be passed directly to compute_raw_models_func
    datasetname                         : str
    post_instance                       : Posterior
    df_fittedval                        : DataFrame
        DataFrame containing the values of the parameters of the model to compute. 
        The indexes are the parameter names and there must be one column called 'value'
    datasim_kwargs                      : dict 
        Kwargs to pass to the datasimulator function
    amplitude_fact                      : float
    compute_raw_models_func             : function
    remove_add_model_components_func    : function
    remove_dict                         : dict of bool
        Dictionary which says which component should be removed from the model being computed (key_model).
        Keys should be valid model keys (str) and the value is True to removed this model to the model being computed.
    add_dict                            : dict of bool
        Dictionary which says which component should be added from the model being computed (key_model)
        Keys should be valid model keys (str) and the value is True to add this model to the model being computed.
    compute_only_raw_models             : bool
    compute_binned                      : bool
        If True the binned model will be computed and added to models independantly of the value of plot_binned.
        If plot_binned_model is True, the binned model will be computed independantly of the value of compute_binned.
    exptime_bin                         : float
    supersamp_bin_model                 : int
    fact_tsim_to_xsim                   : float
        Factor to multiply to tsim to obtain xsim if it is not provided
    xsim                                : array
        x valuess corresponding to the values in tsim for the plot. Superseeds fact_tsim_to_xsim
    time_unit                           : str
    plot_unbinned                       : bool
    plot_binned                         : bool               
    ax                                  : Axe
    pl_kwarg                            : dict
    key_pl_kwarg                        : str
    models                              : dict of array
        Dictionary cointaining the models previously computed to avoid having to recompute the same model multiple times.
        Keys are valid model keys (str) and values are array of the model evaluated at tsim
    get_key_compute_model_func          : func
    is_valid_model_available_func       : func
    kwargs_is_valid_model_available     : dict
    kwargs_get_key_compute_model        : dict

    Returns
    -------
    models                              : dict
    pl_kwarg                            : dict
    """
    if not((tsim is not None) and (key_model is not None) and (datasetname is not None)) and not((model2computeNplot is not None) and (time_fact is not None)):
        raise ValueError(f"You need to provide either tsim, key_model and datasetname or (exclusive) model2computeNplot and time_fact. You provided tsim={tsim}, key_model={key_model}, datasetname={datasetname} and model2computeNplot={model2computeNplot}, time_fact={time_fact}.")
    
    if model2computeNplot is None:
        model2computeNplot = Model2computeNplot(model=key_model, datasetname=datasetname, npt=len(tsim), tlims=(min(tsim), max(tsim)))
    else:
        tsim = linspace(model2computeNplot.tlims[0] / time_fact, model2computeNplot.tlims[1] / time_fact, model2computeNplot.npt, endpoint=True)
        key_model = model2computeNplot.model
        datasetname = model2computeNplot.datasetname

    logger.debug(f"Start compute_and_plot_model for model {key_model} and dataset {datasetname}")
    # Make sure that remove_dict and add_dict have all necessary keys
    if remove_dict is None:
        remove_dict = OrderedDict()
    if add_dict is None:
        add_dict = OrderedDict()

    # Init models if not provided
    if models is None:
        models = {}
        
    # # Define the time vector tsim at which the models will be evaluated
    # tsim = np.linspace(*tlims_model, npt_model)
    # # Define the x vector xsim (corresponding to tsim) at which the models will be plotted
    # if xlims_model is not None:
    #     xsim = np.linspace(*xlims_model, npt_model)
    # else:
    #     xsim = tsim

    # Set exptime_bin if not provided
    if exptime_bin is None:
        exptime_bin = 0.

    # Set fact_tsim_to_xsim if not provided
    if fact_tsim_to_xsim is None:
        fact_tsim_to_xsim = 1.

    # If supersamp_bin_model is not superior to one there is no point in showing the binned model.
    if (supersamp_bin_model is None) or not(supersamp_bin_model > 1):
        plot_binned = False

    # Set xsim the x values for the plot
    if plot_binned or plot_unbinned:
        if xsim is None:
            xsim = tsim * fact_tsim_to_xsim

    #############################################
    # Compute and plot the model and binned model
    #############################################
    key_pl_kwarg_user = key_pl_kwarg
    for binned in [False, True]:
        # Set exptime, extension and adjust key_pl_kwarg depending on whether we are treating the binned model or not
        if binned:
            if (compute_binned or plot_binned) and (exptime_bin > 0.):
                exptime = exptime_bin / fact_tsim_to_xsim
                supersamp = supersamp_bin_model
                extension = '_binned'
            else:
                continue
        else:
            exptime = 0.
            supersamp = 1
            extension = ''

        ################################################
        # Compute the model (can be different procedure)
        ################################################
        if (key_model + extension + extension_raw) not in models:
            if key_model == "model_wGP":
                key_model_compute = "model"
            else:
                key_model_compute = key_model
            if key_model_compute == 'data':
                model = post_instance.dataset_db[datasetname].get_data()
                model_err = None
            elif key_model_compute == 'data_err':
                model = post_instance.dataset_db[datasetname].get_data_err()
                model_err = None
            elif key_model_compute == 'residual':
                model = zeros_like(tsim)
                model_err = None
            elif key_model_compute.startswith('zeros'):
                model = zeros_like(tsim)
                model_err = None
            elif key_model_compute == 'GP' and not(compute_GP_model):
                return models, pl_kwarg
            else:
                model, model_err = compute_raw_models_func(tsim=tsim, key_model=key_model_compute,
                                                           datasetname=datasetname, post_instance=post_instance,
                                                           df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                           exptime=exptime, supersamp=supersamp,
                                                           get_key_compute_model_func=get_key_compute_model_func,
                                                           kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                           split_GP_computation=split_GP_computation
                                                           )
                if model is None:
                    logger.warning(f"Model '{key_model_compute}' not available")
                    return models, pl_kwarg
                
            # Apply the amplitude_fact
            if isinstance(model, dict):
                for key in model.keys(): ## TODO look into this to see if it's needed because it's not fully implemented
                    model[key] *= amplitude_fact
            else:
                model *= amplitude_fact
            if model_err is not None:
                if isinstance(model, dict):
                    for key in model.keys():
                        if model_err[key] is not None:
                            model_err[key] *= amplitude_fact
                else:
                    model_err *= amplitude_fact
            # For model_wGP you need to add the GP
            if key_model == "model_wGP":
                if 'GP' + extension + extension_raw not in models:
                    models, _ = compute_and_plot_model(tsim=tsim, key_model='GP', datasetname=datasetname,
                                                       post_instance=post_instance, df_fittedval=df_fittedval,
                                                       datasim_kwargs=datasim_kwargs,
                                                       amplitude_fact=amplitude_fact, compute_raw_models_func=compute_raw_models_func,
                                                       remove_add_model_components_func=remove_add_model_components_func, 
                                                       remove_dict=None, add_dict=None, compute_only_raw_models=True,
                                                       compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                                       compute_binned=True, exptime_bin=exptime_bin, supersamp_bin_model=supersamp_bin_model, 
                                                       fact_tsim_to_xsim=fact_tsim_to_xsim, time_unit=time_unit,
                                                       plot_unbinned=False, plot_binned=False, ax=None, pl_kwarg=None, key_pl_kwarg=None,
                                                       models=models,
                                                       get_key_compute_model_func=get_key_compute_model_func,
                                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                       )
                # If GP was computed add it 
                if "GP" + extension + extension_raw in models:
                    model = remove_add_model_components_func(model=model, remove_dict={},
                                                             add_dict={'GP': True}, extension=extension,
                                                             extension_raw=extension_raw, 
                                                             models=models, exptime_bin=exptime, supersamp=supersamp,
                                                             amplitude_fact=amplitude_fact
                                                             )
                    _, _, model_err = models['GP' + extension + extension_raw].get_computed_model(exptime_bin=exptime, supersamp=supersamp)
                # Else there is no GP so there should not be a model_wGP either
                else:
                    return models, pl_kwarg
            # Store the raw model in models
            if model_err is None:
                model2computeNplot.set_computed_model(times=tsim, values=model, exptime_bin=exptime, supersamp=supersamp)
            else:
                model2computeNplot.set_computed_model(times=tsim, values=model, values_err=model_err, exptime_bin=exptime, supersamp=supersamp)
            models[key_model + extension + extension_raw] = model2computeNplot
            # if model_err is not None:
            #     models[f'{key_model}_err' + extension + extension_raw] = copy(model_err)
        else:
            model2computeNplot = models[key_model + extension + extension_raw]
            tsim, model, model_err = model2computeNplot.get_computed_model(exptime_bin=exptime, supersamp=supersamp)
            # if f'{key_model}_err' + extension + extension_raw in models:
            #     model_err = models[f'{key_model}_err' + extension + extension_raw]
            # else:
            #     model_err = None

        ##################################
        # Compute the models to remove/add
        ##################################
        if not(compute_only_raw_models):
            if not(compute_GP_model):
                for remove_or_add_dict, remove_or_add in zip([remove_dict, add_dict], ["remove", "add"]):
                    if "GP" in remove_or_add_dict:
                        if remove_or_add_dict["GP"]:
                            remove_or_add_dict["GP"] = False
                            logger.warning(f"Computation of model {key_model} asked to {remove_or_add} the GP, but compute_GP_model is {compute_GP_model}. So GP will not be {remove_or_add}d.")
            l_model_remove = [key for key, do in remove_dict.items() if do]
            l_model_add = [key for key, do in add_dict.items() if do]
            for key_model_removeoradd in (l_model_remove + l_model_add):
                if key_model_removeoradd + extension + extension_raw not in models:
                    models, _ = compute_and_plot_model(tsim=tsim, key_model=key_model_removeoradd, datasetname=datasetname,
                                                       post_instance=post_instance, df_fittedval=df_fittedval,
                                                       datasim_kwargs=datasim_kwargs,
                                                       amplitude_fact=amplitude_fact, compute_raw_models_func=compute_raw_models_func,
                                                       remove_add_model_components_func=remove_add_model_components_func, 
                                                       remove_dict=None, add_dict=None, compute_only_raw_models=True,
                                                       compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                                       compute_binned=True, exptime_bin=exptime_bin, supersamp_bin_model=supersamp_bin_model, 
                                                       fact_tsim_to_xsim=fact_tsim_to_xsim, time_unit=time_unit,
                                                       plot_unbinned=False, plot_binned=False, ax=None, pl_kwarg=None, key_pl_kwarg=None, 
                                                       models=models,
                                                       get_key_compute_model_func=get_key_compute_model_func,
                                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                       )

            ##########################################
            # Remove/Add model components as requested
            ##########################################
            model = remove_add_model_components_func(model=model, remove_dict=remove_dict,
                                                     add_dict=add_dict, extension=extension,
                                                     extension_raw=extension_raw, 
                                                     models=models, exptime_bin=exptime, supersamp=supersamp,
                                                     amplitude_fact=amplitude_fact
                                                     )

            # Fill computed model into output (models)
            models[key_model + extension] = Model2computeNplot(model=key_model, datasetname=datasetname, npt=len(tsim), tlims=(min(tsim), max(tsim)))
            if model_err is None:
                models[key_model + extension].set_computed_model(times=tsim, values=model, values_err=model_err, exptime_bin=exptime_bin, supersamp=supersamp)
            else:
                models[key_model + extension].set_computed_model(times=tsim, values=model, exptime_bin=exptime_bin, supersamp=supersamp)
            # if model_err is not None:
            #     models[f'{key_model}_err' + extension] = model_err

        # Plot the model
        if (plot_unbinned and not(binned)) or (plot_binned and compute_binned and binned):
            if binned:
                update_model_binned_label(pl_kwarg=pl_kwarg, key_model=key_pl_kwarg_user, extension_binned=extension, datasetname=datasetname,
                                          bin_size=exptime_bin, bin_size_unit=time_unit)
            key_pl_kwarg = key_pl_kwarg_user + extension
            if key_pl_kwarg in pl_kwarg[datasetname]:
                pl_kwarg_to_use = pl_kwarg[datasetname][key_pl_kwarg]
            else:
                pl_kwarg_to_use = {"fmt": '', "linestyle": "-", "label": key_pl_kwarg}
            ebconts_lines_labels_model = ax.errorbar(xsim, model, **pl_kwarg_to_use)
            if not("color" in pl_kwarg_to_use):
                pl_kwarg_to_use["color"] = ebconts_lines_labels_model[0].get_color()
            if not("alpha" in pl_kwarg_to_use):
                pl_kwarg_to_use["alpha"] = ebconts_lines_labels_model[0].get_alpha()
                if pl_kwarg_to_use["alpha"] is None:
                    pl_kwarg_to_use["alpha"] = 1.
            # Plot the model_err
            if model_err is not None:
                key_err = key_model + "_err" + extension
                if not("color" in pl_kwarg[datasetname][key_err]):
                    pl_kwarg[datasetname][key_err]["color"] = pl_kwarg_to_use["color"]
                if not("alpha" in pl_kwarg[datasetname][key_err]):
                    pl_kwarg[datasetname][key_err]["alpha"] = pl_kwarg_to_use["alpha"] / 3
                    _ = ax.fill_between(xsim, model - model_err, model + model_err,
                                        **pl_kwarg[datasetname][key_err],
                                        )
    logger.debug(f"Finished compute_and_plot_models for model {key_model} and dataset {datasetname}")
    return models, pl_kwarg


def load_datasets_and_models(datasetnames, post_instance, datasim_kwargs, df_fittedval,
                             amplitude_fact,
                             compute_raw_models_func, remove_add_model_components_func,
                             kwargs_compute_model_4_key_model,
                             compute_GP_model=True,
                             split_GP_computation=None,
                             get_key_compute_model_func=get_key_compute_model,
                             kwargs_get_key_compute_model=None,
                             ):
    """Load the dataset and models for later use by the other two functions ts_and_glsp.create_TSNGLSP_plots and phase_folded.create_phasefolded_plots

    Arguments
    ---------
    datasetnames                        : str
    post_instance                       : Posterior
    datasim_kwargs                      : dict
    df_fittedval                        : DataFrame
    amplitude_fact                      : float
    compute_raw_models_func             : function
    remove_add_model_components_func    : function
    kwargs_compute_model_4_key_model    : dict
    get_key_compute_model_func          : function
    kwargs_get_key_compute_model        : dict

    Return
    ------
    dico_outputs                        : dict
    kwargs_compute_model_4_key_model    : dict
    """
    logger.debug("Start load_datasets_and_models")
    dico_outputs = {# 'dico_datasets': {},
                    'dico_kwargs': {},
                    'dico_nb_dstperinsts': {},
                    'times': {},
                    'datas': {},
                    'rawdatas': {},
                    'data_errs': {},
                    'data_err_jitters': {},
                    'data_err_worwojitters': {},
                    'has_jitters': {},
                    'dico_jitters': {},
                    'residuals': {},
                    'models': {}
                    }
    for datasetname in datasetnames:
        ##########################################
        # Load Data and instrument and noise model
        ##########################################
        # dico_outputs['dico_datasets'][datasetname] = copy(post_instance.dataset_db[datasetname])
        dico_outputs['dico_kwargs'][datasetname] = copy(post_instance.dataset_db[datasetname].get_all_datasetkwargs())
        dico_outputs['times'][datasetname] = copy(post_instance.dataset_db[datasetname].get_datasetkwarg("time"))
        dico_outputs['datas'][datasetname] = copy(post_instance.dataset_db[datasetname].get_datasetkwarg("data"))
        dico_outputs['rawdatas'][datasetname] = copy(post_instance.dataset_db[datasetname].get_datasetkwarg("data"))
        dico_outputs['data_errs'][datasetname] = copy(post_instance.dataset_db[datasetname].get_datasetkwarg("data_err"))
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        noise_model = post_instance.model.get_noise_model(inst_mod.noise_model_category)
        if filename_info["inst_name"] not in dico_outputs['dico_nb_dstperinsts']:
            dico_outputs['dico_nb_dstperinsts'][filename_info["inst_name"]] = 0
        dico_outputs['dico_nb_dstperinsts'][filename_info["inst_name"]] += 1

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        dico_outputs['dico_jitters'][datasetname] = {}
        dico_outputs['data_err_jitters'][datasetname] = copy(post_instance.dataset_db[datasetname].get_datasetkwarg("data_err"))
        dico_outputs['has_jitters'][datasetname] = copy(noise_model.has_jitter)
        if dico_outputs['has_jitters'][datasetname]:
            if inst_mod.jitter.free:
                dico_outputs['dico_jitters'][datasetname]["value"] = copy(df_fittedval.loc[inst_mod.jitter.full_name]["value"])
            else:
                dico_outputs['dico_jitters'][datasetname]["value"] = copy(inst_mod.jitter.value)
            jitter_model = noise_model.get_jitter_model(inst_model_fullname=inst_mod_fullname)
            compute_jitteredvar = jitter_model.get_compute_jitteredvar()
            dico_outputs['data_err_jitters'][datasetname] = sqrt(compute_jitteredvar(data_err=dico_outputs['data_err_jitters'][datasetname], jitter=dico_outputs['dico_jitters'][datasetname]["value"]))
            dico_outputs['data_err_worwojitters'][datasetname] = dico_outputs['data_err_jitters'][datasetname].copy()
        else:
            dico_outputs['data_err_worwojitters'][datasetname] = dico_outputs['data_errs'][datasetname].copy()

        ######################
        # Apply amplitude fact
        ######################
        dico_outputs['datas'][datasetname] *= amplitude_fact
        dico_outputs['rawdatas'][datasetname] *= amplitude_fact
        dico_outputs['data_errs'][datasetname] *= amplitude_fact
        dico_outputs['data_err_worwojitters'][datasetname] *= amplitude_fact
        if dico_outputs['has_jitters'][datasetname]:
            dico_outputs['dico_jitters'][datasetname]["value"] *= amplitude_fact
            dico_outputs['data_err_jitters'][datasetname] *= amplitude_fact

        ############################################################
        # Compute the model components to later remove from the data
        ############################################################
        # Init the dico_outputs['models'] for the datasetname
        dico_outputs['models'][datasetname] = {}
        # Make sure that kwargs_compute_model_4_key_model has at least the model, data, GP and residual keys
        kwargs_compute_model_4_key_model_user = kwargs_compute_model_4_key_model
        kwargs_compute_model_4_key_model = OrderedDict()
        kwargs_compute_model_4_key_model["data"] = {'remove_dict': None, 'add_dict': None}  # The order is important data has to be first then model, GP and residuals
        kwargs_compute_model_4_key_model["model"] = {'remove_dict': None, 'add_dict': None}
        kwargs_compute_model_4_key_model["GP"] = {'remove_dict': None, 'add_dict': None}
        kwargs_compute_model_4_key_model["residual"] = {'remove_dict': {'model': True, 'GP': True, 'decorrelation_likelihood': True}, 'add_dict': {'data': True}}
        for key_model in kwargs_compute_model_4_key_model_user:
            if key_model not in kwargs_compute_model_4_key_model:
                kwargs_compute_model_4_key_model[key_model] = kwargs_compute_model_4_key_model_user[key_model]
            else:
                kwargs_compute_model_4_key_model[key_model].update(kwargs_compute_model_4_key_model_user[key_model])

        for key_model, kwargs in kwargs_compute_model_4_key_model.items():
            if (key_model in ["GP", "model_wGP"]) and not(compute_GP_model):
                continue
            (dico_outputs['models'][datasetname], _
             ) = compute_and_plot_model(tsim=dico_outputs['times'][datasetname], key_model=key_model,
                                        datasetname=datasetname, post_instance=post_instance, df_fittedval=df_fittedval,
                                        datasim_kwargs=datasim_kwargs, amplitude_fact=amplitude_fact,
                                        compute_raw_models_func=compute_raw_models_func,
                                        remove_add_model_components_func=remove_add_model_components_func,
                                        remove_dict=kwargs.get("remove_dict", None), add_dict=kwargs.get("add_dict", None), compute_only_raw_models=False,
                                        compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                                        compute_binned=False, exptime_bin=None, supersamp_bin_model=None,
                                        fact_tsim_to_xsim=None, plot_unbinned=False, plot_binned=False, ax=None, pl_kwarg=None,
                                        key_pl_kwarg=None, models=dico_outputs['models'][datasetname],
                                        get_key_compute_model_func=get_key_compute_model_func,
                                        kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                        )

        ###############################################################
        # Create datas and data_errs key in first level of dico_outputs
        ###############################################################
        if "data" in dico_outputs['models'][datasetname]:
            dico_outputs['datas'][datasetname] = dico_outputs['models'][datasetname]["data"]
        if "data_err" in dico_outputs['models'][datasetname]:
            coeff_err = dico_outputs['models'][datasetname]["data_err"] / dico_outputs['data_errs'][datasetname]
            dico_outputs['data_errs'][datasetname] *= coeff_err
            dico_outputs['data_err_jitters'][datasetname] *= coeff_err
            dico_outputs['data_err_worwojitters'][datasetname] *= coeff_err

        #####################################################
        # Create residuals key in first level of dico_outputs
        #####################################################
        if "residual" in dico_outputs['models'][datasetname]:
            dico_outputs['residuals'][datasetname] = dico_outputs['models'][datasetname]['residual']
    logger.debug("Finished load_datasets_and_models")
    return dico_outputs, kwargs_compute_model_4_key_model


def compute_raw_models(tsim, key_model, datasetname, post_instance,
                       df_fittedval, datasim_kwargs, exptime, supersamp,
                       get_key_compute_model_func=get_key_compute_model,
                       kwargs_get_key_compute_model=None,
                       split_GP_computation=None,
                       ):
    """
    Arguments
    ---------
    tsim                                : array
    key_model                           : str
    datasetname                         : str
    post_instance                       : Posterior
    df_fittedval                        : DataFrame
    datasim_kwargs                      : dict
    exptime                             : float
    supersamp                           : int
    get_key_compute_model_func          : function
    kwargs_get_key_compute_model        : dict

    Returns
    -------
    model       : array
    model_err   : array
    """
    if exptime is None:
        exptime = 0.
    if supersamp is None:
        supersamp = 1.

    if key_model == 'decorrelation_likelihood':
        if f"{datasetname}_decorr_like" in post_instance.datasimulators.dataset_db:
            datasim_docfunc_decorr_like = post_instance.datasimulators.dataset_db[f"{datasetname}_decorr_like"]
            p_vect = df_fittedval["value"][datasim_docfunc_decorr_like.param_model_names_list].array
            model = datasim_docfunc_decorr_like.function(p_vect)
            if not(len(model) == len(tsim)):
                model = None
            model_err = None
        else:
            model = model_err = None
    else:
        kwargs_get_key_compute_model = kwargs_get_key_compute_model if kwargs_get_key_compute_model is not None else {}
        key_compute_model = get_key_compute_model_func(key_model=key_model, **kwargs_get_key_compute_model)
        model, model_err = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                       param=df_fittedval["value"].values,
                                                       l_param_name=list(df_fittedval.index),
                                                       key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                                       supersamp=supersamp, exptime=exptime,
                                                       split_GP_computation=split_GP_computation,
                                                       )
    return model, model_err
