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


def add_time_argument(arguments, multi, has_dataset, arg_list, key_arglist, key_mand_kwargs,
                      key_opt_kwargs, ldict, l_dataset, time_vec_name=time_vec,
                      l_time_vec_name=l_time_vec, add_to_ldict=True, backup_add_to_args=True):
    """Add time to the arguments text and update arg_list and ldict.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    If multi is True l_time_vecwill be added, otherwise time_vec will be.

    :param str arguments: string giving the current text of arguments
    :param bool multi: True if the datasimulator simulate multiple outputs
    :param bool has_dataset: True if the datasimulator should includes datasets values
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param str/list_of_str key_arglist: key of arg_list to update.
    :param str key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param str key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param dict ldict: dictionary to be used as local dictionary argument of the exec function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s) or None.
    :param str time_vec_name: Str used to design the time vector
    :param str l_time_vec_name: Str used to design the list of time vector
    :param ?? new_arg_value: Value of the new argument.
    :param bool add_to_ldict: If True the time argument and its value will be added to ldict if
        has_dataset is True. Otherwise it's not added
    :param bool backup_add_to_args: Decide wether or not to add the time to arguments, if the case
        where has_dataset is True but add_to_ldict is False.
    :return str arguments: Updated string giving the new text of arguments
    :return str time_arg_name: String giving the name of the new time argument.
    :return str/None time_arg: String giving the argument and eventually the default value.
        However if it is directly added to ldict and thus is not added to arguments,
        time_arg is None.
    """
    if multi:
        if has_dataset:
            l_t = []
            for dst in l_dataset:
                l_t.append(dst.get_time())
        else:
            l_t = None
        time_arg_name = l_time_vec_name
        (arguments, time_arg
         ) = add_nonparam_argument(arguments, l_time_vec_name, arg_list, key_arglist,
                                   key_mand_kwargs, key_opt_kwargs, ldict,
                                   add_to_ldict=(has_dataset and add_to_ldict),
                                   backup_add_to_args=(backup_add_to_args or not(has_dataset)),
                                   new_arg_value=l_t)
    else:
        if has_dataset:
            tt = l_dataset[0].get_time()
        else:
            tt = None
        time_arg_name = time_vec_name
        (arguments, time_arg
         ) = add_nonparam_argument(arguments, time_vec_name, arg_list, key_arglist, key_mand_kwargs,
                                   key_opt_kwargs, ldict,
                                   add_to_ldict=(has_dataset and add_to_ldict),
                                   backup_add_to_args=(backup_add_to_args or not(has_dataset)),
                                   new_arg_value=tt)
    return arguments, time_arg_name, time_arg


def add_timeref_arguments(arguments, multi, arg_list, key_arglist, key_mand_kwargs,
                          key_opt_kwargs, ldict, get_time_ref, add_to_ldict, use_dataset,
                          l_dataset=None, timeref_name=time_ref, l_timeref_name=l_time_ref):
    """Add time reference to the arguments text and update arg_list and ldict.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    If vect_for_multi is True and multi is True l_timeref will be added, otherwise timeref will be.

    :param str arguments: string giving the current text of arguments
    :param bool multi: True if the datasimulator simulate multiple outputs
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param str/list_of_str key_arglist: key of arg_list to update.
    :param str key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param str key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param dict ldict: dictionary to be used as local dictionary argument of the exec function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param function/value get_time_ref: Function allowing to compute time ref from the vector of
        times if has_dataset is True.
    :param bool add_to_ldict: If True the time ref or list of time ref will be added to ldict,
        otherwise not.
    :param bool use_dataset: Only effective if add_to_ldict is True. If True, get_time_ref should be
        a function and the time will be computed applying it to the time vector extracted from
        l_dataset. If False, get_time_ref should be the time ref value itself.
    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s) or None.
    :param str timeref_name: Str used to design the time vector
    :param str l_timeref_name: Str used to design the list of time vector
    :return str arguments: Updated string giving the new text of arguments
    :return str timeref_arg_name: String giving the name of the new time reference argument.
    :return str/None timeref_arg: String giving the argument and eventually the default value.
        However if it is directly added to ldict and thus is not added to arguments,
        time_arg is None.
    """
    if multi:
        if add_to_ldict:
            if use_dataset:
                l_tref = []
                for dst in l_dataset:
                    l_tref.append(get_time_ref(dst.get_time()))
            else:
                tref = get_time_ref
        else:
            if use_dataset:
                l_tref = None
            else:
                tref = None
        timeref_arg_name = l_timeref_name
        if use_dataset:
            (arguments, timeref_arg
             ) = add_nonparam_argument(arguments, l_timeref_name, arg_list, key_arglist,
                                       key_mand_kwargs, key_opt_kwargs, ldict,
                                       add_to_ldict=add_to_ldict, new_arg_value=l_tref)
        else:
            (arguments, timeref_arg
             ) = add_nonparam_argument(arguments, timeref_name, arg_list, key_arglist,
                                       key_mand_kwargs, key_opt_kwargs, ldict,
                                       add_to_ldict=add_to_ldict, new_arg_value=tref)
    else:
        if add_to_ldict:
            if use_dataset:
                tref = get_time_ref(l_dataset[0].get_time())
            else:
                tref = get_time_ref
        else:
            tref = None
        timeref_arg_name = timeref_name
        (arguments, timeref_arg
         ) = add_nonparam_argument(arguments, timeref_name, arg_list, key_arglist, key_mand_kwargs,
                                   key_opt_kwargs, ldict, add_to_ldict=add_to_ldict,
                                   new_arg_value=tref)
    return arguments, timeref_arg_name, timeref_arg
