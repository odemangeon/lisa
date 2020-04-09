#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
function from text creation toolbox module.

The objective of this module is to provide functions to ease the development of function created
from text.
@DONE:
    -

@TODO:
    -
"""
from collections import Iterable, OrderedDict


## Name of the model parameter vector
par_vec_name = "p"

## Keys for the parameter and the keywords arguments in the arg_list dictionary
key_param = "param"
key_mand_kwargs = "mandatory_kwargs"
key_opt_kwargs = "optional_kwargs"

argskwargs = ", *args, **kwargs"


def init_arglist_paramnb_arguments_ldict(key_param, keys=None, key_mand_kwargs=None, key_opt_kwargs=None,
                                         param_vector_name=par_vec_name):
    """Initialise the arg_list, param_nb, ldict dictionaries and the argument string.

    All this variable are used during the creation of the datasim creator function.

    :param string key_param: Key used for the parameters entry of arg_list
    :param list_of_str keys: List of string giving the keys to initialise in arg_list and param_nb
    :param string key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param string key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param str param_vector_name: str giving the name of the vector of parameters argument of the
        datasimulator function.
    :return int/dict_of_int param_nb: If keys is None, it's a int, otherwise it's a dictionary of intself.
        In both cases it gives the current number of parameter in the model. If dictionary:
        key = str key designating part of the system or the whole system
        value = initialise at 0
    :return dict_of_list/dict_of_dict_of_list arg_list: dictionary with
        key = str key designating part of the system or the whole system. If keys is None, this level of
            the dictionary is skipped
        value = dict with three str keys (defined by key_param, key_mand_kwargs, key_opt_kwargs), whose values are
            initialised as two empty lists
    :return str arguments: It is what is provided by param_vector_name, every datasimulator takes at least the vector of parameters as
        argument
    :return dict ldict: dictionary initialised to be used as local dictionary argument of the exec
        function.
    """
    if isinstance(keys, str) or (keys is None):
        l_keys = [keys]
    elif isinstance(keys, Iterable):
        l_keys = keys
    else:
        raise ValueError("key_arglist should be None or a string or in iterable of string")
    arg_list = {}
    param_nb = {}
    for key in l_keys:
        arg_list[key] = OrderedDict()
        arg_list[key][key_param] = []
        if key_mand_kwargs is not None:
            arg_list[key][key_mand_kwargs] = []
        if key_opt_kwargs is not None:
            arg_list[key][key_opt_kwargs] = []
        param_nb[key] = 0
    return param_nb, arg_list, param_vector_name, {}


def add_param_argument(param, arg_list, key_param, param_nb, key_arglist=None,
                       param_vector_name=par_vec_name):
    """Add a model parameter: Get the text associated to it and update the variables.

    If the parameter is free, the text will be "param_vec[i]" where is the index of this parameter
    in the parameter vector and param_vec the name of the parameter vector.
    Otherwise the text will be the fixed value of the parameter.
    The variables updated will be arg_list and paramnb.

    :param Parameter param: Parameter instance of the parameter for which you want to get the text
    :param dict arg_list: dictionary with key = key_arglist, value = dict with
        key = key_param, value = list of parameter full names. If param is a free parameter, its
        full name will be added to this list.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param str/list_of_str key_arglist: key of arg_list to update.
    :param dict_of_int param_nb: dictionary giving the current number of parameter in the model.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param string key_param: Key used for the parameters entry of arg_list
    :param str param_vector_name: str giving the name of the vector of parameters argument of the
        datasimulator function.
    :return str/dict_of_str param_text: dictionary of str giving the parameter in the full vector of
        parameters (ex: "p[0]") if parameter is free otherwise str giving the fixed value of this
        parameter.
    """
    if isinstance(key_arglist, str) or (key_arglist is None):
        l_key_arglist = [key_arglist]
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        raise ValueError("key_arglist should be None or a string or in iterable of string")
    param_text = {}
    if param.free:
        param_name = param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False)
        for key in l_key_arglist:
            if param_name not in arg_list[key][key_param]:
                param_nb[key] += 1
                arg_list[key][key_param].append(param_name)
                param_text[key] = "{}[{}]".format(param_vector_name, param_nb[key])
            else:
                param_text[key] = "{}[{}]".format(param_vector_name, arg_list[key][key_param].index(param_name))
    else:
        for key in l_key_arglist:
            param_text[key] = "{}".format(param.value)
    if key_arglist is None:
        return param_text[key]
    else:
        return param_text


def add_nonparam_argument(arguments, new_arg_name, arg_list, key_mand_kwargs, key_opt_kwargs, ldict,
                          key_arglist=None, add_to_ldict=False, backup_add_to_args=True, new_arg_value=None,
                          def_arg_value=None):
    """Update the text used as arguments for the datasimulator function simulating time series.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    It should also be called after init_arguments since it uses its output.

    :param str arguments: string giving the current text of arguments
    :param str new_arg_name: Str used to design the new argument
    :param bool multi: True if the datasimulator simulate multiple outputs
    :param bool has_dataset: True if the datasimulator should includes datasets values
    :param dict arg_list: dictionary with key = key_whole, value = dict with
        key = key_param, value = list of parameter full names
        key = key_mand_kwargs, value = list of mandatory keyword arguments
        key = key_opt_kwargs, value = list of optional keyword arguments
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param string key_mand_kwargs: Key used for the mandatory keyword argument entry of arg_list
    :param string key_opt_kwargs: Key used for the optional keyword argument entry of arg_list
    :param dict ldict: dictionary to be used as local dictionary argument of the exec function.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    :param str/list_of_str key_arglist: key of arg_list to update.
    :param bool add_to_ldict: If True the new argument and its value will be added to ldict.
        Otherwise the name of the new argument is added to arguments if backup_add_to_args is True.
    :param bool backup_add_to_args: If True the new argument and its default value will be added to
        arguments if add_to_ldict is not True.
    :param ?? new_arg_value: Value of the new argument.
    :param ?? def_arg_value: Default argument value. If None, no default value is provided. If you
        want None as default value, you need to provided "None"
    :return str arguments: Updated string giving the new text of arguments
    :return str/None arg: String giving the name of the new argument (and the default value).
        However if the argument is directly added to ldict and thus is not added to arguments,
        arg is None.
    """
    if isinstance(key_arglist, str) or (key_arglist is None):
        l_key_arglist = [key_arglist]
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        if key_arglist is not None:
            raise ValueError("key_arglist should be a string or in iterable of string")
    if add_to_ldict:
        ldict[new_arg_name] = new_arg_value
        arg = None
    else:
        if def_arg_value is None:
            arg = new_arg_name
            key_kwargs = key_mand_kwargs
        else:
            arg = "{}={}".format(new_arg_name, def_arg_value)
            key_kwargs = key_opt_kwargs
        if backup_add_to_args:
            arguments += ", {}".format(arg)
            for key in l_key_arglist:
                arg_list[key][key_kwargs].append(arg)
    return arguments, arg


def add_argskwargs_argument(arguments):
    """Update the text used as arguments to include *args and **kwargs.

    :param str arguments: string giving the current text of arguments
    :return str arguments: Updated string giving the new text of arguments
    """
    return arguments + argskwargs


def get_function_arglist(full_arg_list, key=None):
    """Return the arg_list dictionary for one function from the full arg_list dictionary.

    The full arg_list dictionary may contain the arg_list for more than than 1 function.

    :param dict full_arg_list: Full arg_list dictionary
    :param str key: Key of the full_arg_list for the function you want.
    """
    return full_arg_list[key]
