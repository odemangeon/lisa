"""
polynomial_model module.

The objective of this package is to provides function to implement a polynomial model.

@TODO:
"""
from numbers import Number
from copy import copy
from numpy import ones_like

from ..parameter import Parameter
from ...core.model.datasimulator_timeseries_toolbox import add_time_argument


default_dico = {"do": False, "order": 0, "tref": None}


def get_polymodel(multi, l_inst_model, l_dataset, get_times_from_datasets,
                  tab, time_vec_name, l_time_vec_name,
                  inst_cat_model, dataset_db,
                  function_builder, l_function_shortname,
                  polyonly_func_shortname, ext_func_fullname,
                  name_coeff_const, func_param_name,
                  instrument_per_instrument_model=True, param_container=None, prefix_config=None,
                  ):
    """Get the stellar variation contribution to the RVs including the systemic velocity

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
        Not used right now but there to be able to produce instrumental drift in the future
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
    get_times_from_datasets : bool
        True the datasets should be used to extract the time vectors
        Not used right now but there to be able to produce instrumental drift in the future
    tab                     : str
        String providing the space to put in front of each new line
    time_vec_name           : str
        Str used to design the time vector
        Not used right now but there to be able to produce instrumental drift in the future
    l_time_vec_name         : str
        Str used to design the list of time vector
        Not used right now but there to be able to produce instrumental drift in the future
    Inst_cat_model                 : Inst_Cat_Model
        Instance of a subclass of Instrument_cat_Model
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the all the RV dataset,
        not only the datasets to be simulated.
    function_builder        : FunctionBuilder
        Function builder instance
    l_function_shortname    : list of str
        List of the short name of the functions for which you want to add the instrument variation component
    ext_func_fullname       : str
        Extension to add and the end of the full name of the function simulating the instrumental variation only
        which is defined by this function in the function_builder

    Returns
    -------
    returns     : dict of list of str
        Dictionary of list of str giving the return for stellarvar for each function and each output
    """
    if (instrument_per_instrument_model and (param_container is not None)) or (not(instrument_per_instrument_model) and (param_container is None)):
        raise ValueError("If instrument_per_instrument_model is True, param_container should be None and the reverse.")
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    #########################################
    # Check if the polynomial model is needed
    #########################################
    required = False
    if instrument_per_instrument_model:
        for ii, instmdl in enumerate(l_inst_model):
            dico_config = get_dico_config(param_container=instmdl, prefix=prefix_config, notexist_ok=True, return_None_if_notexist=True)
            if (dico_config is not None) and dico_config["do"]:
                required = True
                break
    else:
        dico_config = get_dico_config(param_container=param_container, prefix=prefix_config, notexist_ok=True, return_None_if_notexist=True)
        if (dico_config is not None) and dico_config["do"]:
            required = True

    if required:
        #################################################
        # Initialise the new function in function_builder
        #################################################
        # Extension for the shortname of the function that do the decorrelation only model
        function_builder.add_new_function(shortname=polyonly_func_shortname)
        if (prefix_config is None) or (prefix_config == inst_cat_model.inst_cat):
            extension = ""
        else:
            extension = prefix_config
        function_builder.set_function_fullname(full_name=f"{inst_cat_model.inst_cat}{extension}_sim_{polyonly_func_shortname}_{ext_func_fullname}", shortname=polyonly_func_shortname)

        ########################################
        # Update the list of function to address
        ########################################
        l_function_shortname += [polyonly_func_shortname, ]

        ################################
        # Do the Model for each function
        ################################
        for function_shortname in l_function_shortname:
            returns[function_shortname] = []

            # Add the time argument
            # Even if the model is a constant you want to generate a vector of constant values that can
            # compared with the data (for the likelihood computation) or plotted without issue
            time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_shortname,
                                              multi=multi, get_times_from_datasets=get_times_from_datasets,
                                              l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                              exist_ok=True)

            # For each instrument model and dataset, ...
            for ii, instmdl in enumerate(l_inst_model):
                returns[function_shortname].append("")
                # Get the dictionary with the configuration of the model
                if instrument_per_instrument_model:
                    param_container = instmdl
                dico_config = get_dico_config(param_container=param_container, prefix=prefix_config, notexist_ok=True, return_None_if_notexist=True)
                # Continue if the dico_config for an instrument is not found (should not append for the model_instance since then required should have been false)
                if (dico_config is None) or not(dico_config["do"]):
                    continue
                order = dico_config["order"]
                # Do the polynomial model
                # Add the constant term
                const_coeff_param = param_container.parameters[name_coeff_const]
                if const_coeff_param.main:
                    function_builder.add_parameter(parameter=const_coeff_param, function_shortname=function_shortname)
                    const_coeff = function_builder.get_text_4_parameter(parameter=const_coeff_param, function_shortname=function_shortname)
                    if const_coeff != 0.0:
                        if order == 0:
                            function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like,
                                                                   function_shortname=function_shortname,
                                                                   exist_ok=True)
                            if multi:
                                returns[function_shortname][ii] += f"{const_coeff} * ones_like({time_arg_name}[{ii}])"
                            else:
                                returns[function_shortname][ii] += f"{const_coeff} * ones_like({time_arg_name})"
                        else:
                            if returns[function_shortname][ii] == "":
                                pretext = ""
                            else:
                                pretext = " + "
                            returns[function_shortname][ii] += f"{pretext}{const_coeff}"
                # Add the drift components
                # ..., For each order in the required polynomial model, ...
                for order_i in range(1, order + 1):
                    # ..., get the name and full name of the parameter for this order
                    drift_param_name = func_param_name(order_i)
                    # ..., If this parameter is a main parameter (it should be), ...
                    if param_container.parameters[drift_param_name].main:
                        function_builder.add_parameter(parameter=param_container.parameters[drift_param_name], function_shortname=function_shortname)
                        drift_param = function_builder.get_text_4_parameter(parameter=param_container.parameters[drift_param_name], function_shortname=function_shortname)
                        # ..., if the parameter is free or the fixed value is not zero, ...
                        if drift_param != 0.0:
                            if returns[function_shortname][ii] == "":
                                pretext = ""
                            else:
                                pretext = " + "
                            returns[function_shortname][ii] += f"{pretext}{drift_param}"
                            # ..., and you need a time reference. There is one time reference
                            # which is automatically set to the time of the first RV measurement
                            timeref_name = f"tref_{param_container.get_name()}"
                            if prefix_config is not None:
                                timeref_name += f"_{prefix_config}"
                            # if this time_reference is not already in the ldict of the function ...
                            if timeref_name not in function_builder.get_ldict(function_shortname=function_shortname):
                                if dico_config["tref"] is None:  # we have to compute its value and add it to the ldict
                                    l_dataset_name = inst_cat_model.get_l_datasetname()
                                    timeref_value = min([min(dataset_db[dataset_name].get_time()) for dataset_name in l_dataset_name])
                                else:
                                    timeref_value = dico_config["tref"]
                                function_builder.add_variable_to_ldict(variable_name=timeref_name, variable_content=timeref_value, function_shortname=function_shortname)
                            if order_i == 1:
                                if multi:
                                    returns[function_shortname][ii] += f" * ({time_arg_name}[{ii}] - {timeref_name})"
                                else:
                                    returns[function_shortname][ii] += f" * ({time_arg_name} - {timeref_name})"
                            elif order_i > 1:
                                if multi:
                                    returns[function_shortname][ii] += (f" * ({time_arg_name}[{ii}] - {timeref_name})**{order_i}")
                                else:
                                    returns[function_shortname][ii] += (f" * ({time_arg_name} - {timeref_name})**{order_i}")

        #####################################
        # Finalize the inst_var only function
        #####################################
        for func_shortname in [polyonly_func_shortname, ]:
            l_return = [output_i if output_i != "" else 'None' for output_i in returns.pop(func_shortname)]
            function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return)}", function_shortname=func_shortname)

    return returns


def set_polymodel_parametrisation(param_container, name_coeff_const, func_param_name, full_category_4_unit,
                                    prefix=None
                                    ):
    """Set the parametrisation for the polynomial modelling to the instrument model.

    Arguments
    ---------
    inst_model_obj  : RV_inst_model object
        WARNING you cannot change the name of this argument for it to work with the __getattr__
        of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
    """
    dico_poly_config = get_dico_config(param_container=param_container, prefix=prefix, notexist_ok=True,
                                       return_None_if_notexist=False)
    do = dico_poly_config['do']
    order = dico_poly_config["order"]
    if do:
        # Constant coefficient
        if name_coeff_const not in param_container.parameters:
            param_container.add_parameter(Parameter(name=name_coeff_const,
                                                    name_prefix=param_container.name,
                                                    main=False, unit=f"[{full_category_4_unit} data unit]"
                                                    )
                                          )
        param_container.parameters[name_coeff_const].main = True
        param_container.parameters[name_coeff_const].value = None
        param_container.parameters[name_coeff_const].free = True
        # Higher order coefficient
        for order in range(1, order + 1):
            param_container.add_parameter(Parameter(name=func_param_name(order),
                                                    name_prefix=param_container.name,
                                                    main=True, unit=f"[{full_category_4_unit} data unit].s^(-{order})"
                                                    )
                                          )


def get_dico_config(param_container, prefix=None, notexist_ok=False, return_None_if_notexist=False):
    """Get the dictionary that configures the polynomial model for the parameter container

    This dictionary is set has an attribute of the param_container instance. Its name is defined via the function
    create_attributename. If the attribute is not present, the function will either raise an error or return the
    default dictionary.

    Arguments
    ---------
    param_container : ParamContainer
        Param container that host the polynomial model configuration (dico_config)
    prefix          : str
        Prefix for the polynomial model (without '_')
    notexist_ok     : bool
        If False raise an error if the attribute doesn't exist. If True return None
        if the attribute doesn't exist.

    Return
    ------
    dico_config : dict
        Dictionary that configures the polynomial model
    """
    attribute_name = create_attributename(prefix=prefix)
    if notexist_ok:
        return_if_notexist = None if return_None_if_notexist else copy(default_dico)
        return getattr(param_container, attribute_name, return_if_notexist)
    else:
        return getattr(param_container, attribute_name)


def create_attributename(prefix=None):
    """
    Arguments
    ---------
    prefix          : str
        Prefix for the polynomial model (without '_')

    Return
    ------
    attribute_name  : str
        Name of the dico configuration for the polynomial model
    """
    if prefix is None:
        attribute_name = 'polynomial'
    else:
        attribute_name = f'{prefix}_polynomial'
    return attribute_name


def set_dico_config(param_container, prefix=None, dico_config=None):
    """Set the dictionary that configures the polynomial model for the parameter container

    This dictionary is set has an attribute of the param_container instance. Its name is defined via the function
    create_attributename.

    Arguments
    ---------
    param_container : ParamContainer
        Param container that will host the parameters of the polynomial model
    prefix          : str
        Prefix for the polynomial model (without '_')
    dico_config     : dict
        Updates that you might want to do to the dico that configure the polynomial model
    """
    # Get the current configuration or initialise it to the default one.
    current_dico_config = get_dico_config(param_container=param_container, prefix=prefix, notexist_ok=True)
    if current_dico_config is None:
        current_dico_config = default_dico.copy()
    # If a new config is provide update the current configuration with the new one
    if dico_config is not None:
        current_dico_config.update(dico_config)
    # Check that the necessary parameters are provided and have correct values
    assert isinstance(current_dico_config["order"], int) and (current_dico_config["order"] >= 0)
    assert isinstance(current_dico_config["do"], bool)
    if current_dico_config["tref"] is not None:
        assert isinstance(current_dico_config["tref"], Number)
    # Set the dictionary as an attribute of the param_container instance
    attribute_name = create_attributename(prefix=prefix)
    setattr(param_container, attribute_name, current_dico_config)
