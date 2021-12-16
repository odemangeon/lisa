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
from copy import copy
from logging import getLogger

logger = getLogger()


## Name of the model parameter vector
par_vec_name = "p"

## Keys for the parameter and the keywords arguments in the arg_list dictionary
key_param = "param"
key_mand_kwargs = "mandatory_kwargs"
key_opt_kwargs = "optional_kwargs"

argskwargs = ", *args, **kwargs"


class FunctionBuilder(object):
    """docstring for FunctionBuilder."""

    def __init__(self, parameter_vector_name=par_vec_name):
        """Classes designed to keep track of the arguments of the functions that will be produced.

        Instances from this class can be used to deal with several functions at the same time.
        It stores the definition of the arguments of the future function and its name

        The arguments of the function are divided in three category:
        - The parameter vector: one single argument wich is the first argument of the function and is
        a numpy array containing all the jumping parameters of the model. The name of this parameter
        vector is provided via parameter_vector_name;
        - The mandatory arguments: as many arguments as need that are not jumping parameter of the model
        These arguments are mandatory in the sense that they don't have a default value;
        - The optional arguments: as many arguments as need that are not jumping parameter of the model
        These arguments are optional in the sense that they have a default value if they are not provided;

        All these informations are stored in the _database attribute of the instance, but this should
        in principle not be accessed directly, but queried and filled with the following methods:
        - TBD

        Arguments
        ---------
        parameter_vector_name   : str
            Str to be used for the parameter vector of the model
        """
        super(FunctionBuilder, self).__init__()
        self.__parameter_vector_name = parameter_vector_name
        self._database = OrderedDict()  # The keys are a short name for the function to be created

    @property
    def parameter_vector_name(self):
        """str of the model parameter vector in the argument of the functions
        """
        return self.__parameter_vector_name

    @property
    def l_function_shortname(self):
        """List of the short names of the functions being tracked
        """
        return list(self._database.keys())

    def add_new_function(self, shortname, parameters=None, mandatory_args=None, optional_args=None, full_function_name=None,
                         ldict=None):
        """Add new function to track

        Arguments
        ---------
        shortname           : str / None
            Short name of the function
        parameters          : List of Parameter / None
            List of the parameters in the model parameter vector
        mandatory_args      : List of str / None
            List of the mandatory argument names
        optional_args       : dictionary
            Pair of optional argument name and their default value
        full_function_name  : str
            Full name of the function
        ldict               : dictionary
            Local dictionary of the function
        """
        self._database[shortname] = {"parameters": [],  # List of the model (jumping) parameter instances for which the value should be provided to the in the parameter vector that is provided to the model
                                     "mandatory_args": [],  # List of the str with the name of the other mandatory arguments (besides the parameter vector) of by the function.
                                     "optional_args": OrderedDict(),  # List of tuples with two arguments: a str giving the name of the other optional arguments of by the function and their default value
                                     "full_name": None,  # function full name, if None full name equal short name
                                     "ldict": [],  # Local dictionary for the function
                                     "body_text": ""  # Text of the body of the function
                                     }
        if parameters is not None:
            for parameter in parameters:
                self.add_parameter(parameter=parameter, function_shortname=shortname)
        if mandatory_args is not None:
            for argument_name in mandatory_args:
                self.add_mandatory_argument(argument_name=argument_name, function_shortname=shortname)
        if optional_args is not None:
            for argument_name, default_value in optional_args:
                self.add_optional_argument(argument_name=argument_name, default_value=default_value,
                                           function_shortname=shortname)
        if full_function_name is not None:
            self.set_function_fullname(full_name=full_function_name, shortname=shortname)
        if ldict is not None:
            for key, value in ldict.items():
                self.add_variable_to_ldict(variable_name=key, variable_content=value, shortname=shortname)

    def copy_function(self, shortname_src, shortname_copy, full_function_name_copy=None):
        """Copy a function

        Arguments
        ---------
        shortname_src           : str
            Short name of the source function that you want to copy
        shortname_copy          : str
            Short name of the new function that you want to the source function to by copied into
        full_function_name_copy : str
            Full name of the new function that you want to the source function to by copied into
        """
        self.add_new_function(shortname=shortname_copy, parameters=self.get_parameter_vector(function_shortname=shortname_src),
                              mandatory_args=self.get_l_mandatory_argument(function_shortname=shortname_src),
                              optional_args={arg: self.get_default_value_4_arg(argument_name=arg, function_shortname=shortname_src) for arg in self.get_l_optional_argument_name(function_shortname=shortname_src)},
                              full_function_name=full_function_name_copy,
                              ldict=self.get_ldict(shortname=shortname_src))

    def add_parameter(self, parameter, function_shortname, exist_ok=False):
        """Add a parameter to the parameter vector of a function

        Arguments
        ---------
        parameter           : Parameter
            Parameter of the model
        function_shortname  : str
            Short name of the function.
        exist_ok            : bool
            If True the function will not produce a warning if the parameter already exists in the function
        """
        if parameter not in self._database[function_shortname]["parameters"]:
            self._database[function_shortname]["parameters"].append(parameter)
        else:
            if not(exist_ok):
                logger.warning(f"Parameter {parameter} already exists for function {function_shortname}")

    def add_mandatory_argument(self, argument_name, function_shortname, exist_ok=False):
        """Add a mandatory argument to a function

        Arguments
        ---------
        argument_name       : str
            Name of the argument to add
        function_shortname  : str
            Short name of the function
        exist_ok            : bool
            If True the function will not produce a warning if the argument already exists in the function
        """
        if argument_name not in self._database[function_shortname]["mandatory_args"]:
            self._database[function_shortname]["mandatory_args"].append(argument_name)
        else:
            if not(exist_ok):
                logger.warning(f"Mandatory argument {argument_name} already exists for function {function_shortname}")

    def add_optional_argument(self, argument_name, default_value, function_shortname):
        """Add an optional argument to a function

        Arguments
        ---------
        argument_name       : str
            Name of the argument to add
        default_value       : "value"
            Default value of the argument
        function_shortname  : str
            Short name of the function
        """
        if argument_name not in self._database[function_shortname]["optional_args"]:
            self._database[function_shortname]["optional_args"][argument_name] = default_value
        else:
            if default_value == self.get_default_value_4_argument(argument_name=argument_name,
                                                                  function_shortname=function_shortname):
                logger.warning(f"Optional argument {argument_name} already exists for function {function_shortname}")
            else:
                logger.error(f"Optional argument {argument_name} already exists for function {function_shortname} with a different default value")

    def get_parameter_vector(self, function_shortname):
        """Return the list of parameters in the parameter vector of a function

        Arguments
        ---------
        function_shortname  : str
            Short name of the function

        Return
        ------
        l_parameter : List of Parameter
            List of Model parameter
        """
        return copy(self._database[function_shortname]["parameters"])

    def get_l_mandatory_argument(self, function_shortname):
        """Return the list of mandatory arguments of a function

        Arguments
        ---------
        function_shortname  : str
            Short name of the function

        Return
        ------
        l_argument_name : list of str
            List of the name of the mandatory arguments
        """
        return copy(self._database[function_shortname]["mandatory_args"])

    def get_l_optional_argument_name(self, function_shortname):
        """Return the list of the name of the optional arguments of a function

        Arguments
        ---------
        function_shortname  : str
            Short name of the function

        Return
        ------
        l_argument_name : list of str
            List of the name of the optional arguments
        """
        return list(self._database[function_shortname]["optional_args"].keys())

    def get_default_value_4_argument(self, argument_name, function_shortname):
        """Return the default value for an given optional argument

        Arguments
        ---------
        argument_name       : str
            Name of the argument
        function_shortname  : str
            Short name of the function

        Return
        ------
        default_value   : ?
            Default value of the argument
        """
        return self._database[function_shortname]["optional_args"][argument_name]

    def get_function_fullname(self, shortname):
        """Return the full name of a function

        Arguments
        ---------
        shortname   : str
            Short name of the function

        Return
        ------
        full_name   : str
            Full name of the function
        """
        if self._database[shortname]["full_name"] is not None:
            return self._database[shortname]["full_name"]
        else:
            return shortname

    def set_function_fullname(self, full_name, shortname):
        """Set the full name of a function

        Arguments
        ---------
        full_name   : str
            Full name of the function
        shortname   : str
            Short name of the function
        """
        self._database[shortname]["full_name"] = full_name

    def add_variable_to_ldict(self, variable_name, variable_content, function_shortname):
        """Add a variable to the local dictionary of a function

        Arguments
        ---------
        variable_name       : str
            Variable name
        variable_content    : ?
            Content of the variable
        function_shortname  : str
            Short name of the function
        """
        if variable_name not in self._database[function_shortname]["ldict"]:
            self._database[function_shortname]["ldict"][variable_name] = variable_content
        else:
            if self._database[function_shortname]["ldict"][variable_name] == variable_content:
                logger.warning(f"Variable {variable_name} already exists in ldict of function {function_shortname}")
            else:
                logger.warning(f"Variable {variable_name} already exists in ldict of function {function_shortname} with a different content")

    def get_ldict(self, shortname):
        """Get the local dictionary of a function

        Arguments
        ---------
        shortname   : str
            Short name of the function

        Return
        ------
        ldict   : dictionary
            local dictionary of the function
        """
        return copy(self._database[shortname]["ldict"])

    def get_function_header(self, shortname):
        """Return the string of the function header

        Arguments
        ---------
        shortname  : str
            Short name of the function

        Return
        ------
        function header : str
            Str giving the header (1st line) of the function definition
        """
        mand_args = ','.join(self.get_l_mandatory_argument(function_shortname=shortname))
        if mand_args != "":
            mand_args = ", " + mand_args
        opt_args = ','.join([f"{arg}={self.get_default_value_4_arg(argument_name=arg, function_shortname=shortname)}" for arg in self.get_l_optional_argument_name(function_shortname=shortname)])
        if opt_args != "":
            opt_args = ", " + opt_args
        return f"def {self.get_function_fullname(shortname=shortname)}({self.parameter_vector_name}{mand_args}{opt_args}):"

    def get_text_4_parameter(self, parameter, function_shortname):
        """Return the text for the model parameter of a function

        Arguments
        ---------
        parameter           : Parameter
            Model parameter
        function_shortname  : str
            Short name of the function

        Return
        ------
        parameter_in_param_vect : str
            Str providing the parameter in the model parameter vector
        """
        return f"{self.parameter_vector_name}[{self.get_parameter_vector(function_shortname=function_shortname).index(parameter)}]"

    def get_body_text(self, function_shortname):
        """Return the text of the body of the function

        Arguments
        ---------
        function_shortname  : str
            Short name of the function

        Return
        ------
        body_text   : str
            Text of the body of the function
        """
        return copy(self._database[function_shortname]["body_text"])

    def add_to_body_text(self, text, function_shortname):
        """Return the text of the body of the function

        Arguments
        ---------
        text                : str
            Text to be added to the body of the function
        function_shortname  : str
            Short name of the function
        """
        self._database[function_shortname]["body_text"] += text


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
        String giving the name of the new argument. However if the argument is directly added to ldict
        and thus is not added to arguments, arg is None.
    arguments_element : str/None
        Addition to arguments made. So 'arg' or 'arg=<default_value>' if there is a default value.
        If no addition have been made because the param has been added to ldict this returns None.
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
