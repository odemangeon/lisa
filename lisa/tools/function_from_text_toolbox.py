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


def init_arglist_paramnb_arguments_ldict(key_param, keys, key_mand_kwargs=None, key_opt_kwargs=None,
                                         param_vector_name=par_vec_name):
    """Initialise the arg_list, param_nb, ldict dictionaries and the argument string.

    All this variable are used during the creation of the datasim creator function.

    Arguments
    ---------
    key_param           : str
        Key used for the parameters entry of arg_list
    keys                : str or list_of_str
        Str or List of string giving the keys to initialise in arg_list and param_nb
    key_mand_kwargs     : str
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs      : str
        Key used for the optional keyword argument entry of arg_list
    param_vector_name   : str
        str giving the name of the vector of parameters argument of the datasimulator function.

    Returns
    -------
    param_nb    : dict_of_int
        Gives the current number of parameter in the model for all function being built (specified by keys).
        Format:
        - key = str key designating part of the system or the whole system
        - value = initialise at 0
    arg_list    : dict_of_dict_of_list
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
    arguments   : str
        It is what is provided by param_vector_name, every datasimulator takes at least the vector of parameters as
        argument
    ldict       : dict_of_dict
        Dictionary giving the initialised empty dictionary to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = empty dictionary
    """
    if isinstance(keys, str):
        l_keys = [keys]
    elif isinstance(keys, Iterable):
        l_keys = keys
    else:
        raise ValueError("key_arglist should a string or in iterable of string")
    arg_list = {}
    param_nb = {}
    ldict = {}
    for key in l_keys:
        arg_list[key] = OrderedDict()
        arg_list[key][key_param] = []
        if key_mand_kwargs is not None:
            arg_list[key][key_mand_kwargs] = []
        if key_opt_kwargs is not None:
            arg_list[key][key_opt_kwargs] = []
        param_nb[key] = 0
        ldict[key] = {}
    return param_nb, arg_list, param_vector_name, ldict


def add_param_argument(param, arg_list, key_param, param_nb, key_arglist=None,
                       param_vector_name=par_vec_name):
    """Add a model parameter to the functions being produced: Get the text associated to it and update
    the arg_list and param_nb variables.

    If param is a free parameter, the returned text will be f"{param_vector_name}[{ii}]" where ii is the index of
    param in the parameter vector of the function being produced (designated by key_arglist) and param_vector_name
    is the name of the parameter vector provided by param_vector_name.
    If param is a fixed parameter, the returned text will be the fixed value of the parameter.

    The variables updated will be arg_list and param_nb.

    Arguments
    ---------
    param       : Parameter
        Parameter instance of the parameter for which you want to get the text
    arg_list    : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If the parameter provided by param is free. It's name will be added the sub-dictionaries specified by key_arglist
        in the key_param list.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_arglist : str or list_of_str or None
        Name/Ref or list of name/ref of the function being produced for which you want to add param as
        a parameter. These names are keys of the arg_list and param_nb dictionaries
        If key_arglist is None, all available keys in arglist are assumed.
    param_nb    : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_param   : str
        Key used for the parameters entry of arg_list values
    param_vector_name   : int_current_nb_of_model_parameters_of_the_datasimulator
        str giving the name of the vector of parameters argument of the function being produced.

    Returns
    -------
    param_text : str/dict_of_str
        If key_arglist is None than the returned variable is a string else it is a dictionary of strings.
        If param is a free parameter, the string(s) give the the reference to the parameter within the function
        being produced (ex: "p[0]" if param_vector_name = "p").
        If param is a fixed parameter,  the string(s) give the fixed value of this parameter.
    """
    if isinstance(key_arglist, str):
        l_key_arglist = [key_arglist]
    elif key_arglist is None:
        l_key_arglist = list(arg_list.keys())
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        raise ValueError("key_arglist should be None or a string or in iterable of string")
    param_text = {}
    if param.free:
        param_name = param.get_name(include_prefix=True, recursive=True, force_no_duplicate=True)
        for key in l_key_arglist:
            if param_name not in arg_list[key][key_param]:
                arg_list[key][key_param].append(param_name)
                param_text[key] = "{}[{}]".format(param_vector_name, param_nb[key])
                param_nb[key] += 1
            else:
                param_text[key] = "{}[{}]".format(param_vector_name, arg_list[key][key_param].index(param_name))
    else:
        for key in l_key_arglist:
            param_text[key] = "{}".format(param.value)
    return param_text


def add_nonparam_argument(arguments, new_arg_name, arg_list, key_mand_kwargs, key_opt_kwargs, ldict,
                          key_arglist=None, new_arg_value=None, def_arg_value=None, disable_add_to_ldict=False):
    """Update the text used as arguments for a function created from text.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.
    It should also be called after init_arguments since it uses its output.

    There is 3 use cases for this function:
    1. You want to add a non param argument for which you have the value:
        You provide the value via new_arg_value and it will be stored in ldict (dictionary which will
        be used as local environement for the execution of the text of the function)
    2. You want to add a non param argument for which you do not have the value at coding time:
        You don't provide new_arg_value (or you provide None) and the argument name will be added to the
        arguments string and will be required from user at run time
    3. You want to add a non param argument for which the value is function of variable that you do not
        have now but are part of the function.
        In this case you should provide the text which will be used to compute the value at run time
        in new_arg_value. You should also have added function required by this text to ldict if there is any.
        Finally you should set disable_add_to_ldict to True.

    Arguments
    ---------
    arguments           : str
        string giving the current text of arguments
    new_arg_name        : str
        Str used to design the new argument
    arg_list            : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If it's not added to ldict instead the arguments provided by arguments are going to be added to the key_mand_kwargs or key_opt_kwargs
        of sub-dictionaries specified by key_arglist.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_mand_kwargs      : string
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs       : string
        Key used for the optional keyword argument entry of arg_list
    ldict       : dict_of_dict
        Dictionary giving the dictionaries to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = dictionary
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_arglist          : str or list_of_str or None
        Name/Ref or list of name/ref of the function being produced for which you want to add param as
        a parameter. These names are keys of the arg_list and param_nb dictionaries
        If key_arglist is None, all available keys in arglist are assumed.
    new_arg_value        :
        Value of the new argument.
    def_arg_value        :
        Default argument value. If None, no default value is provided. If you want None as default value,
        you need to provided "None"
    disable_add_to_ldict : bool
        This should be set to True only for use case 3 (see above). This prevents the function from adding
        the content of new_arg_value to ldict and affect it to arg instead, also adding new_arg_name to arguments

    Returns
    -------
    arguments         : str
        Updated string giving the new text of arguments
    arg               : str/None
        String giving the name of the new argument (and the default value).
        However if the argument is directly added to ldict and thus is not added to arguments,
        arg is None.
    arguments_element : str/None
        Addition to arguments made. If no addition have been made because the param has been added to ldict
        this returns None
    """
    if isinstance(key_arglist, str):
        l_key_arglist = [key_arglist]
    elif key_arglist is None:
        l_key_arglist = list(arg_list.keys())
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        raise ValueError("key_arglist should be a string or in iterable of string")
    if (new_arg_value is not None) and not(disable_add_to_ldict):
        # Use case 1.
        for key in l_key_arglist:
            ldict[key][new_arg_name] = new_arg_value
            arg = None
            arguments_element = None
    else:
        # Use case 2 or 3.
        arg = new_arg_name
        if def_arg_value is None:
            key_kwargs = key_mand_kwargs
            arguments_element = f"{arg}"
        else:
            key_kwargs = key_opt_kwargs
            arguments_element = f"{arg}={def_arg_value}"
        arguments += f", {arguments_element}"
        for key in l_key_arglist:
            arg_list[key][key_kwargs].append(arg)
    return arguments, arg, arguments_element


def add_argskwargs_argument(arguments):
    """Update the text used as arguments to include *args and **kwargs.

    :param str arguments: string giving the current text of arguments
    :return str arguments: Updated string giving the new text of arguments
    """
    return arguments + argskwargs


def get_function_arglist(arg_list, key_arglist=None):
    """Return the arg_list dictionary for one function from the full arg_list dictionary.

    The full arg_list dictionary may contain the arg_list for more than than 1 function.

    Arguments:
    ----------
    arg_list         : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If the parameter provided by param is free. It's name will be added the sub-dictionaries specified by key_arglist
        in the key_param list.
    key_arglist     : str
        Name/Ref of the function being produced for which you want to get the arglist

    Returns:
    --------
    arg_list_1func  : dict_of_list_of_str
        dictionary giving the arguments of one of the functions (specified by key_arglist) currently being produced
        with the following format:
        dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
    """
    return arg_list[arg_list]
