from loguru import logger
from copy import copy
from numpy import zeros_like, sqrt
from collections import defaultdict, OrderedDict

from ..posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.likelihood.gaussian_noisemodelconfiguration import apply_jitter_multi, apply_jitter_add
from ..posterior.core.model.core_model import Core_Model

# Key for the whole model
key_whole = Core_Model.key_whole

# Set extension for raw models
extension_raw = '_raw'

# managers
mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


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


def compute_and_plot_model(tsim, key_model, datasetname, post_instance, df_fittedval, datasim_kwargs,
                           include_gp_model, amplitude_fact, compute_raw_models_func, remove_add_model_components_func,
                           remove_dict=None, add_dict=None,
                           exptime_bin=None, supersamp_bin_model=None, fact_tsim_to_xsim=None, xsim=None,
                           plot=True, plot_GP=False, plot_model_wGP=True, ax=None, pl_kwarg=None, key_pl_kwarg=None, show_binned_model=True,
                           models=None, l_valid_model=None, get_key_compute_model_func=get_key_compute_model,
                           is_valid_model_available_func=is_valid_model_available,
                           kwargs_is_valid_model_available=None,
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
    include_gp_model                    : bool
    amplitude_fact                      : float
    compute_raw_models_func             : function
    remove_add_model_components_func    : function
    remove_dict                         : dict of bool
        Dictionary which says which component should be removed from the model being computed (key_model).
        Keys should be valid model keys (str) and the value is True to removed this model to the model being computed.
    add_dict                            : dict of bool
        Dictionary which says which component should be added from the model being computed (key_model)
        Keys should be valid model keys (str) and the value is True to add this model to the model being computed.
    exptime_bin                         : float
    supersamp_bin_model                 : int
    fact_tsim_to_xsim                   : float
        Factor to multiply to tsim to obtain xsim if it is not provided
    xsim                                : array
        x valuess corresponding to the values in tsim for the plot. Superseeds fact_tsim_to_xsim
    plot                                : bool
    plot_GP                             : bool
    plot_model_wGP                      : bool                  
    ax                                  : Axe
    pl_kwarg                            : dict
    key_pl_kwarg                        : str
    show_binned_model                   : bool
    models                              : dict of array
        Dictionary cointaining the models previously computed to avoid having to recompute the same model multiple times.
        Keys are valid model keys (str) and values are array of the model evaluated at tsim
    l_valid_model                       : list of str
    get_key_compute_model_func          : func
    is_valid_model_available_func       : func
    kwargs_is_valid_model_available     : dict
    kwargs_get_key_compute_model        : dict

    Returns
    -------
    models                              : dict
    pl_kwarg                            : dict
    """
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

    # Set xsim the x values for the plot
    if plot:
        if xsim is None:
            xsim = tsim * fact_tsim_to_xsim

    #############################################
    # Compute and plot the model and binned model
    #############################################
    key_pl_kwarg_user = key_pl_kwarg
    for binned in [False, True]:
        # Set exptime, extension and adjust key_pl_kwarg depending on whether we are treating the binned model or not
        if binned:
            if show_binned_model and (exptime_bin > 0.):
                exptime = exptime_bin / fact_tsim_to_xsim
                supersamp = supersamp_bin_model
                extension = '_binned'
            else:
                continue
        else:
            exptime = 0.
            supersamp = 1.
            extension = ''

        ################################################
        # Compute the model (can be different procedure)
        ################################################
        if (key_model + extension + extension_raw) not in models:
            if key_model == 'data':
                model = post_instance.dataset_db[datasetname].get_data()
                model_wGP = gp_pred = gp_pred_var = None
            elif key_model == 'data_err':
                model = post_instance.dataset_db[datasetname].get_data_err()
                model_wGP = gp_pred = gp_pred_var = None
            elif key_model.startswith('zeros'):
                model = zeros_like(tsim)
                model_wGP = gp_pred = gp_pred_var = None
            else:
                (model, model_wGP, gp_pred, gp_pred_var
                 ) = compute_raw_models_func(tsim=tsim, key_model=key_model, l_valid_model=l_valid_model,
                                             datasetname=datasetname, post_instance=post_instance,
                                             df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                             include_gp_model=include_gp_model, exptime=exptime,
                                             supersamp=supersamp,
                                             get_key_compute_model_func=get_key_compute_model_func,
                                             is_valid_model_available_func=is_valid_model_available_func,
                                             kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                             kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                             )

            if model is None:
                logger.warning(f"Model '{key_model}' not available")
                return models, pl_kwarg

            # Apply the amplitude_fact
            if isinstance(model, dict):
                for key in model.keys():
                    model[key] *= amplitude_fact
            else:
                model *= amplitude_fact
            if model_wGP is not None:
                model_wGP *= amplitude_fact
                gp_pred *= amplitude_fact
                gp_pred_var *= amplitude_fact**2

            # Store the raw model in the output (models)
            models[key_model + extension + extension_raw] = copy(model)
            if model_wGP is not None:
                models[f'{key_model}_wGP' + extension + extension_raw] = copy(model_wGP)
                models[f'GP_{key_model}' + extension + extension_raw] = gp_pred
                models[f'GP_var_{key_model}' + extension + extension_raw] = gp_pred_var

        else:
            model = models[key_model + extension + extension_raw]
            if f'{key_model}_wGP' + extension + extension_raw in models:
                model_wGP = models[f'{key_model}_wGP' + extension + extension_raw]
                gp_pred = models[f'GP_{key_model}' + extension + extension_raw]
                gp_pred_var = models[f'GP_var_{key_model}' + extension + extension_raw]
            else:
                model_wGP = None

        ##################################
        # Compute the models to remove/add
        ##################################
        l_model_remove = [key for key, do in remove_dict.items() if do]
        l_model_add = [key for key, do in add_dict.items() if do]
        for key_model_removeoradd in (l_model_remove + l_model_add):
            if key_model_removeoradd + extension + extension_raw not in models:
                if remove_dict.get(key_model_removeoradd, False) or add_dict.get(key_model_removeoradd, False):
                    models, _ = compute_and_plot_model(tsim=tsim, key_model=key_model_removeoradd, datasetname=datasetname,
                                                       post_instance=post_instance, df_fittedval=df_fittedval,
                                                       datasim_kwargs=datasim_kwargs, include_gp_model=False,
                                                       amplitude_fact=amplitude_fact, compute_raw_models_func=compute_raw_models_func,
                                                       remove_add_model_components_func=remove_add_model_components_func,
                                                       exptime_bin=exptime_bin, supersamp_bin_model=supersamp_bin_model, fact_tsim_to_xsim=fact_tsim_to_xsim,
                                                       plot=False, plot_GP=False, plot_model_wGP=False, ax=None, pl_kwarg=None, key_pl_kwarg=None, show_binned_model=True,
                                                       models=models, l_valid_model=l_valid_model,
                                                       get_key_compute_model_func=get_key_compute_model_func,
                                                       is_valid_model_available_func=is_valid_model_available_func,
                                                       kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                       )

        ##########################################
        # Remove/Add model components as requested
        ##########################################
        model, model_wGP = remove_add_model_components_func(model=model, model_wGP=model_wGP, remove_dict=remove_dict,
                                                            add_dict=add_dict, extension=extension,
                                                            extension_raw=extension_raw, models=models,
                                                            amplitude_fact=amplitude_fact
                                                            )

        # Fill computed model into output (models)
        models[key_model + extension] = model
        if model_wGP is not None:
            models[f'{key_model}_wGP' + extension] = model_wGP
            models[f'GP_{key_model}' + extension] = gp_pred
            models[f'GP_var_{key_model}' + extension] = gp_pred_var

        # Plot the model
        if plot:
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
            # Plot the GP
            if (model_wGP is not None) and (plot_GP or plot_model_wGP):
                key_GP = "GP" + extension
                key_GP_err = "GP_err" + extension
                if not("color" in pl_kwarg[datasetname][key_GP]):
                    pl_kwarg[datasetname][key_GP]["color"] = pl_kwarg_to_use["color"]
                if not("color" in pl_kwarg[datasetname]["GP_err"]):
                    pl_kwarg[datasetname][key_GP_err]["color"] = pl_kwarg_to_use["color"]
                if not("alpha" in pl_kwarg[datasetname]["GP"]):
                    pl_kwarg[datasetname][key_GP]["alpha"] = pl_kwarg_to_use["alpha"]
                if not("alpha" in pl_kwarg[datasetname]["GP_err"]):
                    pl_kwarg[datasetname][key_GP_err]["alpha"] = pl_kwarg_to_use["alpha"] / 3
                if plot_model_wGP:
                    pl_kwarg[datasetname][key_GP]["label"] = pl_kwarg_to_use['label'] + " + GP"
                    _ = ax.errorbar(tsim, model_wGP, **pl_kwarg[datasetname][key_GP])
                    _ = ax.fill_between(tsim, model_wGP - sqrt(gp_pred_var), model_wGP + sqrt(gp_pred_var),
                                        **pl_kwarg[datasetname][key_GP_err],
                                        )
                if plot_GP:
                    _ = ax.errorbar(tsim, gp_pred, **pl_kwarg[datasetname][key_GP])
                    _ = ax.fill_between(tsim, gp_pred - sqrt(gp_pred_var), gp_pred + sqrt(gp_pred_var),
                                        **pl_kwarg[datasetname][key_GP_err]
                                        )
    return models, pl_kwarg


def load_datasets_and_models(datasetnames, post_instance, datasim_kwargs, df_fittedval,
                             amplitude_fact,
                             compute_raw_models_func, remove_add_model_components_func,
                             kwargs_compute_model_4_key_model,
                             l_valid_model=None,
                             get_key_compute_model_func=get_key_compute_model,
                             is_valid_model_available_func=is_valid_model_available,
                             kwargs_is_valid_model_available=None,
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
    l_valid_model                       : list of str
    get_key_compute_model_func          : function
    is_valid_model_available_func       : function
    kwargs_is_valid_model_available     : dict
    kwargs_get_key_compute_model        : dict

    Return
    ------
    dico_outputs                        : dict
    kwargs_compute_model_4_key_model    : dict
    """
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
        noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
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
            dico_outputs['dico_jitters'][datasetname]["type"] = copy(noise_model.jitter_type)
            if inst_mod.jitter.free:
                dico_outputs['dico_jitters'][datasetname]["value"] = copy(df_fittedval.loc[inst_mod.jitter.full_name]["value"])
            else:
                dico_outputs['dico_jitters'][datasetname]["value"] = copy(inst_mod.jitter.value)
            if dico_outputs['dico_jitters'][datasetname]["type"] == "multi":
                dico_outputs['data_err_jitters'][datasetname] = sqrt(apply_jitter_multi(dico_outputs['data_err_jitters'][datasetname], dico_outputs['dico_jitters'][datasetname]["value"]))
            elif dico_outputs['dico_jitters'][datasetname]["type"] == "add":
                dico_outputs['data_err_jitters'][datasetname] = sqrt(apply_jitter_add(dico_outputs['data_err_jitters'][datasetname], dico_outputs['dico_jitters'][datasetname]["value"]))
            else:
                raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            dico_outputs['data_err_worwojitters'][datasetname] = dico_outputs['data_err_jitters'][datasetname].copy()
        else:
            dico_outputs['data_err_worwojitters'][datasetname] = dico_outputs['data_errs'][datasetname].copy()

        ################################################################################
        # Apply amplitude fact
        ################################################################################
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
        # Make sure that kwargs_compute_model_4_key_model has at least the model key
        kwargs_compute_model_4_key_model_user = kwargs_compute_model_4_key_model
        kwargs_compute_model_4_key_model = {'model': {'include_gp_model': True, 'remove_dict': None, 'add_dict': None}}
        for key_model in kwargs_compute_model_4_key_model_user:
            if key_model not in kwargs_compute_model_4_key_model:
                kwargs_compute_model_4_key_model[key_model] = kwargs_compute_model_4_key_model_user[key_model]
            else:
                kwargs_compute_model_4_key_model[key_model].update(kwargs_compute_model_4_key_model_user[key_model])
        # Make sure that kwargs_compute_model_4_key_model has the "data" key
        # if "data" not in kwargs_compute_model_4_key_model:
        #     kwargs_compute_model_4_key_model["data"] = {'remove_dict': kwargs_compute_model_4_key_model['model']['remove_dict'],
        #                                                 'add_dict': kwargs_compute_model_4_key_model['model']['add_dict']
        #                                                 }
        for key_model, kwargs in kwargs_compute_model_4_key_model.items():
            if 'include_gp_model' not in kwargs:
                kwargs['include_gp_model'] = True if key_model == 'model' else False
            (dico_outputs['models'][datasetname], _
             ) = compute_and_plot_model(tsim=dico_outputs['times'][datasetname], key_model=key_model,
                                        datasetname=datasetname, post_instance=post_instance, df_fittedval=df_fittedval,
                                        datasim_kwargs=datasim_kwargs, amplitude_fact=amplitude_fact,
                                        compute_raw_models_func=compute_raw_models_func,
                                        remove_add_model_components_func=remove_add_model_components_func,
                                        exptime_bin=None, supersamp_bin_model=None,
                                        fact_tsim_to_xsim=None, plot=False, plot_GP=False, plot_model_wGP=False, ax=None, pl_kwarg=None,
                                        key_pl_kwarg=None, show_binned_model=True, models=dico_outputs['models'][datasetname],
                                        l_valid_model=l_valid_model,
                                        get_key_compute_model_func=get_key_compute_model_func,
                                        is_valid_model_available_func=is_valid_model_available_func,
                                        kwargs_is_valid_model_available=kwargs_is_valid_model_available,
                                        kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                        **kwargs
                                        )

        #################################
        # Remove components from the data
        #################################
        if "data" in dico_outputs['models'][datasetname]:
            # import pdb; pdb.set_trace()
            dico_outputs['datas'][datasetname] = dico_outputs['models'][datasetname]["data"]
        if "data_err" in dico_outputs['models'][datasetname]:
            # import pdb; pdb.set_trace()
            coeff_err = dico_outputs['models'][datasetname]["data_err"] / dico_outputs['data_errs'][datasetname]
            dico_outputs['data_errs'][datasetname] *= coeff_err
            dico_outputs['data_err_jitters'][datasetname] *= coeff_err
            dico_outputs['data_err_worwojitters'][datasetname] *= coeff_err

        #######################
        # Compute the residuals
        #######################
        if kwargs_compute_model_4_key_model['model']['include_gp_model'] and not(kwargs_compute_model_4_key_model['data']['remove_dict'].get('GP_model', False)) and ('model_wGP' in dico_outputs['models'][datasetname]):
            dico_outputs['residuals'][datasetname] = dico_outputs['datas'][datasetname] - dico_outputs['models'][datasetname]['model_wGP']
        else:
            dico_outputs['residuals'][datasetname] = dico_outputs['datas'][datasetname] - dico_outputs['models'][datasetname]['model']

    return dico_outputs, kwargs_compute_model_4_key_model


def compute_raw_models(tsim, key_model, l_valid_model, datasetname, post_instance,
                       df_fittedval, datasim_kwargs, include_gp_model, exptime, supersamp,
                       get_key_compute_model_func=get_key_compute_model,
                       is_valid_model_available_func=is_valid_model_available,
                       kwargs_is_valid_model_available=None,
                       kwargs_get_key_compute_model=None,
                       ):
    """
    Arguments
    ---------
    tsim                                : array
    key_model                           : str
    l_valid_model                       : list of str
    datasetname                         : str
    post_instance                       : Posterior
    df_fittedval                        : DataFrame
    datasim_kwargs                      : dict
    include_gp_model                    : bool
    exptime                             : float
    supersamp                           : int
    get_key_compute_model_func          : function
    is_valid_model_available_func       : function
    kwargs_is_valid_model_available     : dict
    kwargs_get_key_compute_model        : dict

    Returns
    -------
    model       : array
    model_wGP   : array
    gp_pred     : array
    gp_pred_var : array
    """
    kwargs_is_valid_model_available = kwargs_is_valid_model_available if kwargs_is_valid_model_available is not None else {}
    kwargs_get_key_compute_model = kwargs_get_key_compute_model if kwargs_get_key_compute_model is not None else {}
    if key_model in l_valid_model:
        if not(is_valid_model_available_func(key_model, datasetname, post_instance, **kwargs_is_valid_model_available)):
            model = model_wGP = gp_pred = gp_pred_var = None
            return model, model_wGP, gp_pred, gp_pred_var

    if exptime is None:
        exptime = 0.
    if supersamp is None:
        supersamp = 1.

    if key_model == 'decorrelation_likelihood':
        datasim_docfunc_decorr_like = post_instance.datasimulators.dataset_db[f"{datasetname}_decorr_like"]
        p_vect = df_fittedval["value"][datasim_docfunc_decorr_like.param_model_names_list].array
        model = datasim_docfunc_decorr_like.function(p_vect)
        if not(len(model) == len(tsim)):
            model = None
        model_wGP = gp_pred = gp_pred_var = None
    elif key_model.startswith("GP"):
        key_compute_model = key_model[2:]
        (model, model_wGP, gp_pred, gp_pred_var
         ) = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                         param=df_fittedval["value"].values,
                                         l_param_name=list(df_fittedval.index),
                                         key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                         include_gp=True,
                                         supersamp=supersamp, exptime=exptime
                                         )
        return gp_pred, None, None, None
    elif key_model.endswith("_wGP"):
        key_compute_model = key_model[:-4]
        (model, model_wGP, gp_pred, gp_pred_var
         ) = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                         param=df_fittedval["value"].values,
                                         l_param_name=list(df_fittedval.index),
                                         key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                         include_gp=True,
                                         supersamp=supersamp, exptime=exptime
                                         )
        return model_wGP, None, None, None
    else:
        key_compute_model = get_key_compute_model_func(key_model=key_model, **kwargs_get_key_compute_model)
        if include_gp_model:
            (model, model_wGP, gp_pred, gp_pred_var
             ) = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                             param=df_fittedval["value"].values,
                                             l_param_name=list(df_fittedval.index),
                                             key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                             include_gp=include_gp_model,
                                             supersamp=supersamp, exptime=exptime
                                             )
        else:
            model = post_instance.compute_model(tsim=tsim, dataset_name=datasetname,
                                                param=df_fittedval["value"].values,
                                                l_param_name=list(df_fittedval.index),
                                                key_obj=key_compute_model, datasim_kwargs=datasim_kwargs,
                                                include_gp=include_gp_model,
                                                supersamp=supersamp, exptime=exptime
                                                )
            model_wGP = gp_pred = gp_pred_var = None

    return model, model_wGP, gp_pred, gp_pred_var
