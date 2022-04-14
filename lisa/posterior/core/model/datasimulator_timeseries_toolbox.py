#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator creator time series toolbox module.

The objective of this module is to provide functions to ease the development of datasimulator
creator function for time series datasets.
@DONE:
    -

@TODO:
    -
"""
from ....tools.function_from_text_toolbox import add_nonparam_argument

## String used for the time vector
time_vec = "t"

## String used for the list of time vectors
l_time_vec = "l_{}".format(time_vec)

## String used for the reference time
time_ref = "tref"

## String used for the list of reference times
l_time_ref = "l_{}".format(time_ref)


def add_time_argument(function_builder, function_shortname, multi, get_times_from_datasets, l_dataset, time_vec_name=time_vec,
                      l_time_vec_name=l_time_vec, exist_ok=False):
    """Add time to the argument in the function_builder for a function

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    If multi is True l_time_vec_name will be added, otherwise time_vec_name will be.

    Arguments
    ---------
    function_builder        : FunctionBuilder
        Function builder instance
    function_shortname      : str
        Short name of the function in function_builder for which you want to add time as argument
    multi: bool
        True if the datasimulator simulate multiple outputs
    get_times_from_datasets : bool
        True the datasets should be used to extract the time vectors
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s) or None.
    time_vec_name           : str
        Str used to design the time vector
    l_time_vec_name         : str
        Str used to design the list of time vector
    exist_ok                : bool
        If True the function will not produce a warning if the time argument already exists in the function

    Returns
    -------
    time_arg_name: str
        String giving the name of the new time argument.
    """
    if multi:
        time_arg_name = l_time_vec_name
        if get_times_from_datasets:
            time_content = []
            for dst in l_dataset:
                time_content.append(dst.get_time())
    else:
        time_arg_name = time_vec_name
        if get_times_from_datasets:
            time_content = l_dataset[0].get_time()
    if get_times_from_datasets:
        function_builder.add_variable_to_ldict(variable_name=time_arg_name, variable_content=time_content, function_shortname=function_shortname, exist_ok=True)
    else:
        function_builder.add_mandatory_argument(argument_name=time_arg_name, function_shortname=function_shortname, exist_ok=True)
    return time_arg_name


def add_timeref_arguments(arguments, multi, vect_for_multi, use_dataset, arg_list, key_arglist, key_mand_kwargs,
                          key_opt_kwargs, ldict, get_time_ref=None, time_ref_val=None,
                          l_dataset=None, timeref_name=time_ref, l_timeref_name=l_time_ref):
    """Add time reference to the arguments text and update arg_list and ldict.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    If vect_for_multi is True and multi is True l_timeref will be added, otherwise timeref will be.

    Arguments:
    ----------
    arguments       : Str
        string giving the current text of arguments
    multi           : bool
        True if the datasimulator simulate multiple outputs
    vect_for_multi  : bool
        If True then the time ref will be a list of time references if multi is True, otherwise it's
        the same time reference for all outputs (datasets).
    use_dataset     : bool
        Only effective if add_to_ldict is True. If True, get_time_ref should be
        a function and the time will be computed applying it to the time vector extracted from
        l_dataset. If False, get_time_ref should be the time ref value itself.
    arg_list        : dict
        Dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_arglist     : str/list_of_str
        key of arg_list to update.
    key_mand_kwargs : str
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs  : str
        Key used for the optional keyword argument entry of arg_list
    ldict       : dict_of_dict
        Dictionary giving the dictionaries to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = dictionary
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    get_time_ref    : function
        Function allowing to compute time ref from the vector of times if has_dataset and use_dataset
        are True. Otherwise, it's not used.
        If multi and vect_for_multi are True, this function will be applied to the list
        of time vectors directly (not to element element)
    time_ref_val    : float or list of float if multi and vector_for_multi are True
        Value of the time reference to use, if use_dataset is False
    l_dataset       : list_of_Dataset
        Checked list of Dataset instance(s) or None.
    timeref_name    : str
        Str used to design the time vector
    l_timeref_name  : str
        Str used to design the list of time vector

    Returns:
    --------
    arguments                : str
        Updated string giving the new text of arguments
    timeref_arg_name         : str
        String giving the name of the new time reference argument.
    timeref_arg              : str/None
        String giving the argument (same as timeref_arg_name).
        However if it is directly added to ldict and thus is not added to arguments, timeref_arg is None.
    timeref_arg_in_arguments : str/None
        Addition to arguments made. So the argument name and eventually the default value.
        If no addition have been made because the param has been added to ldict this returns None
    """
    disable_add_to_ldict = False  # Input of add_nonparam_argument that should be False expect if the
    # time reference is computed from the time vector at run time
    # If multi and vect_for_multi, then time ref is a list of time references
    if multi and vect_for_multi:
        timeref_arg_name = l_timeref_name
        # If use_dataset then the list of time references is computed from the time vector of the datasets
        # using get_time_ref
        if use_dataset:
            assert get_time_ref is not None, "If you want to use the dataset to compute the time reference, you need to provide get_time_ref"
            l_tref = get_time_ref([dst.get_time() for dst in l_dataset])
        else:
            l_tref = time_ref_val
        (arguments, timeref_arg, timeref_arg_in_arguments
         ) = add_nonparam_argument(arguments=arguments, new_arg_name=l_timeref_name, arg_list=arg_list,
                                   key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                   ldict=ldict, key_arglist=key_arglist, new_arg_value=l_tref, disable_add_to_ldict=disable_add_to_ldict)
    else:
        # In this case there is only one time reference even if multi is True
        timeref_arg_name = timeref_name
        # If use_dataset then the time references is computed from the time vector of the datasets
        # using get_time_ref
        if use_dataset:
            assert get_time_ref is not None, "If you want to use the dataset to compute the time reference, you need to provide get_time_ref"
            if multi:
                tref = get_time_ref([dst.get_time() for dst in l_dataset])
            else:
                tref = get_time_ref(l_dataset[0].get_time())
        else:
            # If you don't want to use the datasets than use the provided time references ()
            tref = time_ref_val
        (arguments, timeref_arg, timeref_arg_in_arguments
         ) = add_nonparam_argument(arguments=arguments, new_arg_name=timeref_name, arg_list=arg_list,
                                   key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs, ldict=ldict,
                                   key_arglist=key_arglist, new_arg_value=tref, disable_add_to_ldict=disable_add_to_ldict)
    return arguments, timeref_arg_name, timeref_arg, timeref_arg_in_arguments
