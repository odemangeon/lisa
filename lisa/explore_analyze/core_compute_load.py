from __future__ import annotations

from loguru import logger
from copy import copy
from numpy import zeros_like, sqrt, linspace, size, ones_like, float_
from numpy.typing import NDArray
from collections import defaultdict, OrderedDict
from pandas import DataFrame

from .misc import update_model_binned_label
from .core_plot import ComputedModels_Database, Expression, ComputedModel, ModelBinning
from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.model.core_model import Core_Model
from ..posterior.core.posterior import Posterior

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


def compute_model(post_instance, df_fittedval, datasim_kwargs,
                  compute_raw_models_func,
                  expression:Expression,
                  times, 
                  datasetname:str,
                  exptime,
                  supersampling,
                  computedmodels_db:ComputedModels_Database,
                  get_key_compute_model_func=get_key_compute_model,
                  kwargs_get_key_compute_model=None,
                  split_GP_computation=None,
                  ):
    """Compute a model.

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
    logger.info(f"Start compute_model for expression {expression.expression} and dataset {datasetname}")
    
    # Init models if not provided
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    # Check if the model is already in computedmodels_db
    (computedmodel, _, times_found
     ) = computedmodels_db.find_computed_model(expression=expression.expression, datasetname=datasetname, 
                                               binning=ModelBinning(exptime=exptime, supersampling=supersampling), times=times
                                               )
    if times_found is not None:
        times = times_found

    if computedmodel is None:
        # The model was not found you have to compute it
        # Get the list of model components
        components = {}
        for component_i in expression.components:
            (computedmodel_component_i, _, _
             ) = computedmodels_db.find_computed_model(expression=component_i, datasetname=datasetname, 
                                                       binning=ModelBinning(exptime=exptime, supersampling=supersampling), times=times
                                                       )
            if computedmodel_component_i is None:
                logger.info(f"Computing component {component_i} for dataset {datasetname}")
                if component_i == 'data':
                    model = post_instance.dataset_db[datasetname].get_data()
                    model_err = post_instance.dataset_db[datasetname].get_data_err()
                elif component_i == 'data_err':
                    model = post_instance.dataset_db[datasetname].get_data_err()
                    model_err = None
                else:
                    model, model_err = compute_raw_models_func(tsim=times, key_model=component_i,
                                                               datasetname=datasetname, post_instance=post_instance,
                                                               df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                                               exptime=exptime, supersamp=supersampling,
                                                               get_key_compute_model_func=get_key_compute_model_func,
                                                               kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                                               split_GP_computation=split_GP_computation
                                                               )
                if model is None:
                    logger.warning(f"Component {component_i} could not be computed for dataset {datasetname} and is set to zero.")
                    components[component_i] = {"values": 0., "errors": model_err}
                else:
                    computedmodels_db.store_computed_model(expression=component_i, datasetname=datasetname, binning=ModelBinning(exptime=exptime, supersampling=supersampling),
                                                           times=times, values=model, errors=model_err)
                    components[component_i] = {"values": model, "errors": model_err}
            else:
                components[component_i] = {"values": computedmodel_component_i.values, "errors": computedmodel_component_i.errors}
        
        (computedmodel, _, _
         ) = computedmodels_db.find_computed_model(expression=expression.expression, datasetname=datasetname, 
                                                   binning=ModelBinning(exptime=exptime, supersampling=supersampling), times=times
                                                   )
        if computedmodel is None:
            d_globals = {component_i: components[component_i]["values"] for component_i in expression.components}
            exec(f"result = {expression.expression}", d_globals)
            model = d_globals["result"]
            if size(model) == 1:
                model = ones_like(times) * model
            d_globals = {component_i: components[component_i]["errors"] if components[component_i]["errors"] is not None else 0. for component_i in expression.components}
            d_globals['sqrt'] = sqrt
            exec(f"result = {expression.expression_err}", d_globals)
            model_err = d_globals["result"]
            if size(model_err) == 1:
                if model_err == 0.:
                    model_err = None
                else:
                    model_err = ones_like(times) * model_err
            computedmodels_db.store_computed_model(expression=expression.expression, datasetname=datasetname, binning=ModelBinning(exptime=exptime, supersampling=supersampling),
                                                times=times, values=model, errors=model_err)
    else:
        model = computedmodel.values
        model_err = computedmodel.errors
    
    logger.debug(f"Done compute_model for expression {expression.expression} and dataset {datasetname}")
    return model, model_err, computedmodels_db


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

def compute_data_err_jittered(data_err:NDArray[float_], post_instance:Posterior, datasetname:str, df_fittedval:DataFrame) -> NDArray[float_]|None:
    inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
    inst_mod = post_instance.model.instruments[inst_mod_fullname]
    noise_model = post_instance.model.get_noise_model(inst_mod.noise_model_category)
    if noise_model.has_jitter:
        if inst_mod.jitter.free:
            jitter_value = copy(df_fittedval.loc[inst_mod.jitter.full_name]["value"])
        else:
            jitter_value = copy(inst_mod.jitter.value)
        jitter_model = noise_model.get_jitter_model(inst_model_fullname=inst_mod_fullname)
        compute_jitteredvar = jitter_model.get_compute_jitteredvar()
        data_err_jitter= sqrt(compute_jitteredvar(data_err=copy(data_err), jitter=jitter_value))
    else:
        data_err_jitter = None
    return data_err_jitter