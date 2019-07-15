#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Core_Prior functions module.

It contains the three main classes to handle Priors: Core_Prior_Function, Core_JointPrior_Function
and Manager_Prior.

Note: Manager_Prior was initially in a separate module but I had to put the class here, because I am
using the manager in the __init__ of Core_JointPrior_Function.
"""
from logging import getLogger
from numpy import logical_xor  # logical_not

from ....tools.metaclasses import MandatoryReadOnlyAttr, MandatoryMethods
from ....software_parameters import setupfile_prior


## logger object
logger = getLogger()


class Metaclass_PriorFunction(MandatoryReadOnlyAttr, MandatoryMethods):
    """Metaclass for Prior Function class.
    """

    @property
    def all_args(cls):
        """Return the name of the prior type."""
        return cls.mandatory_args + cls.extra_args

    def __new__(cls, classname, bases, classdict):
        classdict["all_args"] = property(cls.all_args)
        return super(Metaclass_PriorFunction, cls).__new__(cls, classname, bases, classdict)

    def __init__(cls, name, bases, attrs):
        MandatoryReadOnlyAttr.__init__(cls, name, bases, attrs)
        MandatoryMethods.__init__(cls, name, bases, attrs)
        # if cls.__name__ not in ["Core_Prior_Function", "Core_JointPrior_Function"]:
        #     missing_attrs = ["{}".format(attr) for attr in ["logpdf", "ravs"]
        #                      if not hasattr(cls, attr)]
        #     if len(missing_attrs) > 0:
        #         raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Metaclass_JointPriorFunction(Metaclass_PriorFunction):
    """Metaclass for Joint Prior Function class.
    """

    @property
    def all_args(cls):
        """Return the name of the prior type."""
        return cls.mandatory_args + cls.extra_args + [ref + cls.hiddenparampriorarg_ext for ref in cls.hidden_param_refs]


class Core_Prior_Function(object, metaclass=Metaclass_PriorFunction):
    """Docstring for Prior Prior function class.

    When creating a new Prior, you need to create a subclass of Core_Prior_Function.
    (For joint prior see Core_JointPrior_Function).

    The Subclass of this Abstract class should all define the following class atrributes (specified
    in the list __mandatoryattrs__ atrribute of this class):
    __category__           : Unique string identifying the Prior. This string will be used in the parameter
        file to select the prior.
    __mandatory_args__     : list of string identifying the mandatory arguments that should be provided
        at the instanciation of the Prior class.
    __extra_args__         : list of string identifying the extra arguments that can be provided
        at the instanciation of the Prior class. The difference between extra and madantory arguments
        is that the extra argument will be attributed a default value if they are not provided. This
        default value is provided by __default_extra_args__.
    __default_extra_args__ : Dictionary giving the default value for each one of the extra arguments
        listed in __extra_args__. If no entry is provided for an extra argument, the default value is
        assumed to be None.
    __joint__              : Specify of the Prior is a joint prior. This is inherited from Core_Prior_Function
        or Core_JointPrior_Function and doesn't need to be redefined in the Subclass.

    The Subclass of this Abstract class should also all define the following methods:
    create_logpdf(self)     : This methods returns the logpdf function of the Prior instance. This
        method should not receive any arguments.
        :return function logpdf: The log pdf function taking as input the value of the parameter and
            returnin the value of the logpdf.
    ravs(self, nb_values=1) : This methods draws random values from the logpdf function of the Prior.
        This method should have one argument 'nb_values' (that should be 1 by default), it is the number
        of values that one wants to draw.
        :param int nb_values: Number of values to draw for each parameter.
        :return float/array_of_float values: Value of the parameter drawn from the prior. If nb_values=1,
            it's a float. If nb_values > 1, it's an array of floats.

    You can override the __init__ method, but it has to create and set an attribute for each mandatory and
    each extra argument (this is automatically done in the __init__ method below with the _set_mandatory_and_extra_attributes
    method).
    """

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "default_extra_args", "joint"]
    __mandatorymeths__ = ["create_logpdf", "ravs"]
    __joint__ = False
    # Key for the dictionary sorting the arguments
    mandatory_key = "mandatory"
    extra_key = "extra"
    l_dico_args_keys = [mandatory_key, extra_key]

    def __init__(self, *args, **kwargs):
        super(Core_Prior_Function, self).__init__()
        # Sort *args and **kwargs into argument categories and store them into dico_args
        self.dico_args = self._check_n_sort_args(*args, **kwargs)
        # Check for mandatory arguments
        self._check_mandatory_args(self.dico_args)
        # Set defaults values for non provided extra_args
        self._set_extraarg_defaultvalues(self.dico_args)
        # Create and set attributes for the madatory and extra arguments.
        self._set_mandatory_and_extra_attributes(self.dico_args)
        # Make Prior_Function an abstract class
        if type(self) is Core_Prior_Function:
            raise NotImplementedError("Core_Prior_Function should not be instanciated!")

    def __call__(self, *args):
        return self.logpdf(*args)

    @classmethod
    def check_args(cls, kwargs_list):
        missing_mandatoryargs = ["{}".format(arg) for arg in cls.mandatory_args
                                 if arg not in kwargs_list]
        if len(missing_mandatoryargs) > 0:
            raise AttributeError("Prior function '{}' requires attribute(s) {}"
                                 "".format(cls.__name__, missing_mandatoryargs))
        unknown_args = ["{}".format(arg) for arg in kwargs_list
                        if arg not in cls.all_args]
        if len(unknown_args) > 0:
            raise AttributeError("Prior function '{}' doesn't recognise attribute(s) {}"
                                 "".format(cls.__name__, unknown_args))

    def _set_mandatory_and_extra_attributes(self, dico_args):
        """Automatically create and set attributes for the mandatory and extra arguments
        """
        # Set atrribute for mandatory arguments
        for attribute, value in dico_args[self.mandatory_key].items():
            setattr(self, attribute, value)
        # Set atrribute for extra arguments
        for attribute, value in dico_args[self.extra_key].items():
            setattr(self, attribute, value)

    @property
    def dicokey4argkey(self):
        """Dictionary giving the type of argument for each possible argument (of __init__).

        The types of arguments are mandatory, extra and hidden_param_prior
        """
        dicokey4argkey = {}
        for arg_key in self.mandatory_args:
            dicokey4argkey[arg_key] = self.mandatory_key
        for arg_key in self.extra_args:
            dicokey4argkey[arg_key] = self.extra_key
        return dicokey4argkey

    def _check_n_sort_args(self, *args, **kwargs):
        """Check and sort *args and **kwargs into arguments categories.

        :return dict_of_dict dico_args: Dictionary containing the arguments provided to __init__ sorted
            into argument categories (mandatory, extra, ...). The structure of this dict is:
            {arg_category: {arg_key: arg_value, },}
        """
        dico_args = {key: {} for key in self.l_dico_args_keys}
        for value, arg_key in zip(args, self.mandatory_args + self.extra_args):
            dico_args[self.dicokey4argkey[arg_key]][arg_key] = value
        for arg_key, value in kwargs.items():
            if arg_key not in self.dicokey4argkey:
                raise ValueError("Argument not recognized: {}".format(arg_key))
            if arg_key in dico_args[self.dicokey4argkey[arg_key]]:
                raise ValueError("{} argument is provided multiple times.".format(arg_key))
            dico_args[self.dicokey4argkey[arg_key]][arg_key] = value
        return dico_args

    def _check_mandatory_args(self, dico_args):
        """Check that mandatory arguments are provided.

        :param dict_of_dict_of_str: dictionary giving the arguments provided to the __init__ method and
            sorted into categories (mandatory and extra).
        """
        for arg_key in self.mandatory_args:
            if arg_key not in dico_args[self.mandatory_key]:
                raise ValueError("{} has to be provided.".format(arg_key))

    def _set_extraarg_defaultvalues(self, dico_args):
        """Set arguments that are not provided to default value.

        :param dict_of_dict_of_str: dictionary giving the arguments provided to the __init__ method and
            sorted into categories (mandatory and extra).
        """
        for arg_key in self.extra_args:
            if arg_key not in dico_args[self.extra_key]:
                dico_args[self.extra_key][arg_key] = self.default_extra_args.get(arg_key, None)


class Core_JointPrior_Function(Core_Prior_Function, metaclass=Metaclass_JointPriorFunction):
    """docstring for Core_JointPrior_Function.

    When creating a new Joint Prior, you need to create a subclass of Core_Prior_Function.
    (For marginal prior see Core_Prior_Function).

    The Subclass of this Abstract class should all define the following class atrributes (specified
    in the list __mandatoryattrs__ atrribute of this class):
    For a description of __category__, __mandatory_args__, __extra_args__, __default_extra_args__, __joint__
    __param_refs__             : list of string giving the internal parameter references (used in the parameter
        file to identify which parameter in the model is used by the joint prior and how).
    __multiple_params__        : list of booleans indicating if each parameter reference in __param_refs__
        can be a list of parameters (True) instead of a single parameter (False).
    __hidden_param_refs__      : list of string giving the internal hidden parameter references (used
        in the definition by the create_logpdf and ravs methods for example)
    __multiple_hidden_params__ : list of booleans indicating if each hidden parameter reference in __hidden_param_refs__
        can be a list of hidden parameter (True) instead of a single hidden parameter (False).
    __default_hidden_priors__   : Dictionary defining the default prior for each hidden parameter reference
        in __hidden_param_refs__. If a given hidden parameter ref can be multiple parameter, only one prior
        can be defined here. key = hidden parameter reference (should be in __hidden_param_refs__),
        value: Marginal prior definition ({'category': prior_category, 'args': {arg_dictionary}})

    The Subclass of this Abstract class should also all define the following methods:
    create_logpdf(self, params) : This methods returns the logpdf function of the Prior instance. This
        method should not receive any arguments. It should use the content of the instance attribute of
        with the names of the mandatory and extra arguments alongs with the hidden prior instances provided
        by self.priorinstance_hiddenparams to create the logpdf function.
        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter references (from self.__param_refs__) and the values are the parameter
            instances as associated in the parameter file. A parameter reference can be associated to
            a list of Parameter instances if it specified as a multiple parameter in self.__multiple_params__.
        :return function logpdf: The log pdf function taking as input the value of the parameter and
            returnin the value of the logpdf.
    ravs(self, nb_values=1)     : This methods draws random values from the logpdf function of the Prior.
        This method should have one argument 'nb_values' (that should be 1 by default), it is the number
        of values that one wants to draw. It should use the content of the instance attribute of
        with the names of the mandatory and extra arguments alongs with the hidden prior instances provided
        by self.priorinstance_hiddenparams to draw values from the prior
        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/tuple_of_array_of_float values: Values of the parameters drawn from the prior.
            If nb_values=1, it's a tuple of float. If nb_values > 1, it's a tuple of arrays of floats.
            The order of the parameters in the tuple is the same than in self.__param_refs__.
    set_hiddenparam_defs(self, **kwargs): Fill self.hiddenparam_defs.
            It's a dictionary which contains the prior instances information of the hidden parameters.
            Keys are hidden parameter references and values are dictionary defining the definition of
            the prior to be used for each hidden parameter. It should follow the following format:
            {"category": priorcat, "args": {"arg1":0, "arg2":1}} like for marginal priors.
            It can also be list of prior definition if the hidden parameter can be multiple (specified
            by self.multiple_hidden_params)

    You can override the __init__ method, but it has to create and set an attribute for each mandatory and
    each extra argument (this is automatically done in the __init__ method below with the _set_mandatory_and_extra_attributes
    method).
    """

    # __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "join", "default_extra_args",
    #                       "param_refs", "multiple_params", "hidden_param_refs", "multiple_hidden_params",
    #                       "default_hidden_priors"]
    __mandatoryattrs__ = Core_Prior_Function.__mandatoryattrs__ + ["param_refs", "multiple_params",
                                                                   "hidden_param_refs", "multiple_hidden_params",
                                                                   "default_hidden_priors"]
    # __mandatorymeths__ = ["create_logpdf", "ravs", "set_dico_priors_arg"]
    __mandatorymeths__ = Core_Prior_Function.__mandatorymeths__ + ["set_hiddenparam_defs", "infer_hiddenparams_nb"]
    __joint__ = True
    # Key for the dictionary sorting the arguments
    hiddenparamprior_key = "hidden_param_prior"
    l_dico_args_keys = Core_Prior_Function.l_dico_args_keys + [hiddenparamprior_key, ]
    # Extension to hidden param reference used for the argument to provide the hidden param prior definition
    hiddenparampriorarg_ext = "_prior"

    def __init__(self, params, *args, **kwargs):
        """Init method for the Core_JointPrior_Function instances

        :param dict params: "params" dictionary from the parameter file. Key = parameter references
            (from self.__param_refs__), value = name (full name) of the model parameter. It can be a
            str or list of str, if the parameter is multiple (specified by self.__multiple_params__).
        Arguments and Keyword arguments are:
        - mandatory_args
        - extra_args
        - hidden_params_prior definition for the hidden prior. These arguments name should be hiddenparam_prior
            where hiddenparam is one element in the self.__hidden_param_refs__ list. The value of this argument
            should a dict {'category': prior_cat, 'args': {dict of prior args and values}} or a list of
            these dictionaries if the hidden parameter can be multiple (specified by self.__multiple_hidden_params__)
        Only mandatory arguments can by *args
        """
        # __init__ method of Core_Prior_Function.
        super(Core_JointPrior_Function, self).__init__(*args, **kwargs)
        # Initialise the dictionary of the model parameter names used by the prior pdf function
        # self.param_name_lists
        self._init_param_name_lists()
        # Set the content of self.param_name_lists
        self._set_param_name_lists(params)
        # Initialise the dictionary of the prior definitions of the hidden parameters
        # self.hiddenparam_defs
        self._init_hiddenparam_defs()
        # Set the content of self.hiddenparam_defs
        self.set_hiddenparam_defs(self.dico_args[self.hiddenparamprior_key])
        # Initialise the dictionary of the prior instances of the hidden parameters
        # self.priorinstance_hiddenparams
        self._init_priorinstance_hiddenparams()
        # Set the content of self.priorinstance_hiddenparams
        # Create the prior function instance of the hidden parameter
        self._set_priorinstance_hiddenparams()

    @classmethod
    def check_params(cls, params, model_instance):
        """Check that the parameters dictionnary provided for the Joint prior is correct.

        Check that the parameters keys provided are the ones required by the definition of the prior.
        Check that the parameters names provided correspond to existing parameters.

        :param dict params: Params dictionary from the parameter file. Key = elements of the self.__param_refs__
            list, value = name (full name) of the model parameter corresponding to the parameter references.
            It can also be a list of model parameters if the parameter can be multiple (specified by
            self.__multiple_params__)
        :param Core_Model model_instance: model instance to be able to check that the parameter names
            provided in params are valid.
        """
        # Check that the parameter keys are good
        set_paramskeys_expected = set(cls.param_refs)
        set_paramskeys_received = set(params.keys())
        if set_paramskeys_expected != set_paramskeys_received:
            unexpected_paramskeys = set_paramskeys_received - set_paramskeys_expected
            missing_paramskeys = set_paramskeys_expected - set_paramskeys_received
            raise ValueError("Wrong parameter keys provided for Joint prior category {}.\n"
                             "Number of unexpected keys: {}, list: {}\n"
                             "Number of unexpected keys: {}, list: {}"
                             "".format(cls.category, len(unexpected_paramskeys), unexpected_paramskeys,
                                       len(missing_paramskeys), missing_paramskeys))
        else:
            logger.debug("The params keys provided for Joint prior category {} are correct.")
        # Check that the parameter names correspond to existing params and that they are main parameters
        dico_params_found = {}
        for param_name, multi in zip(cls.param_refs, cls.multiple_params):
            if multi:
                if isinstance(params[param_name], str):
                    l_param_name = [params[param_name], ]
                elif isinstance(params[param_name], list):
                    l_param_name = params[param_name]
                else:
                    raise ValueError("The value corresponding to {} for be a str giving the reference"
                                     "to a model parameter or a list of references.".format(param_name))
            else:
                l_param_name = [params[param_name], ]
            for ref_param_mdl_name in l_param_name:
                found = model_instance.has_parameter(ref_param_mdl_name, recursive=True)
                dico_params_found[ref_param_mdl_name] = found
        if not(all(list(dico_params_found.values()))):
            raise ValueError("Parameter names {} doesn't exist in the model.".format([param_name for param_name, found in dico_params_found.items() if not(found)]))
        logger.debug("The parameters name provided for Joint prior category all correspond to "
                     "existing parameters")

    @property
    def dicokey4argkey(self):
        """Dictionary giving the type of argument for each possible argument (of __init__).

        The types of arguments are mandatory, extra and hidden_param_prior
        """
        dicokey4argkey = super(Core_JointPrior_Function, self).dicokey4argkey
        for arg_key in self.hidden_param_refs:
            dicokey4argkey[arg_key + self.hiddenparampriorarg_ext] = self.hiddenparamprior_key
        return dicokey4argkey

    @property
    def hiddenparam_defs(self):
        """Dictionary containing the prior function definition for each hidden parameter.

        key = hidden_param_ref (elements of self.__hidden_param_refs__)
        value = dictionary containing the definition of the prior or a list of definition if the hidden
            parameter is multiple (specified by self.__multiple_hidden_params__).
            A prior definition is a dictionary like this {'category': prior_category, 'args': {arg_dictionary}})
        """
        return self.__hiddenparam_defs

    @property
    def priorinstance_hiddenparams(self):
        """Dictionary containing the prior function instances for each hidden parameter.

        key = hidden parameter reference (elements of self.__hidden_param_refs__)
        value = Prior instances for the hidden parameter or a list of Prior instances if the hidden
            parameter is multiple (specified by self.__multiple_hidden_params__).
        """
        return self.__priorinstance_hiddenparams

    @property
    def param_name_lists(self):
        """Dictionary of the lists of parameter names used by the joint pdf function for each parameter reference.

        key = parameter reference (elements of self.__param_refs__).
        value = list of strings giving the parameter names in the model. If the parameter is multiple
            (specified by self.__multiple_params__), this list can have several elements. Otherwise,
            it should have only one element.
        """
        return self.__param_name_lists

    @property
    def param_name_fulllist(self):
        """Return the list or parameter names from the model used by the joint pdf function.
        """
        res = []
        for param_ref, multiple in zip(self.param_refs, self.multiple_params):
            if multiple:
                res.extend(self.param_name_lists[param_ref])
            else:
                res.append(self.param_name_lists[param_ref])
        return res

    def _init_param_name_lists(self):
        """Initialise the lists of parameter names used by the joint prior.

        Initialise self.param_name_lists.
        """
        self.__param_name_lists = {}
        for param_ref, multiple in zip(self.param_refs, self.multiple_params):
            if multiple:
                self.__param_name_lists[param_ref] = []
            else:
                self.__param_name_lists[param_ref] = None

    def _init_hiddenparam_defs(self):
        """Initialise the dictionary of definitions dictionary for the prior of the hidden parameters.

        Initialise self.dico_hiddenparam_defs.
        """
        self.__hiddenparam_defs = self.__get_hidden_param_default_dict(dico_default_values=self.default_hidden_priors)

    def _init_priorinstance_hiddenparams(self):
        """Initialise the dictionary of Prior instances for the hidden parameters.

        Initialise self.dico_priorinstance_hiddenparams.
        """
        self.__priorinstance_hiddenparams = self.__get_hidden_param_default_dict()

    def __get_hidden_param_default_dict(self, dico_default_values=None):
        if dico_default_values is None:
            dico_default_values = {}
        dico = {}
        for hidden_param_ref, multiple in zip(self.hidden_param_refs, self.multiple_hidden_params):
            if multiple:
                nb_hiddenparam = self.infer_hiddenparams_nb(hidden_param_ref=hidden_param_ref)
                dico[hidden_param_ref] = [dico_default_values.get(hidden_param_ref, None) for i in range(nb_hiddenparam)]
            else:
                dico[hidden_param_ref] = dico_default_values.get(hidden_param_ref, None)
        return dico

    def _set_param_name_lists(self, params):
        """Set the list of parameter names used by this joint prior.

        Define the content of the properties self.param_name_lists.

        :param dict params: "params" dictionary from the parameter file. Key = elements of the self.__param_refs__
            list, value = name (full name) of the model parameter(s). It can be a str or list of str,
            if the parameter is multiple (specified by self.__multiple_params__)
        """
        # Set self.param_name_lists
        for param_ref, param_ref_value in params.items():
            # For each parameter reference, check if this can be a multiple parameter reference.
            idx = self.param_refs.index(param_ref)
            if self.multiple_params[idx]:
                # If it is, check if several references are provided and add them to the list of parameter
                # for this parameter reference
                if isinstance(param_ref_value, str):
                    # If only one add it to the list of this parameter
                    self.param_name_lists[param_ref].append(param_ref_value)
                else:
                    self.param_name_lists[param_ref].extend(param_ref_value)
            else:
                self.param_name_lists[param_ref] = param_ref_value

    def _set_priorinstance_hiddenparams(self):
        """Set the dictionary of the Prior instance of the hidden parameters.

        Define the contant of the property self.priorinstance_hiddenparams. This should be used after
        self.set_hiddenparam_defs.
        """
        manager = Manager_Prior()
        for hidden_param_ref, multiple in zip(self.hidden_param_refs, self.multiple_hidden_params):
            if multiple:
                l_paramdef = self.hiddenparam_defs[hidden_param_ref]
            else:
                l_paramdef = [self.hiddenparam_defs[hidden_param_ref], ]
            for ii, paramdef in enumerate(l_paramdef):
                if paramdef is None:
                    priorfunction_subclass = None
                else:
                    if manager.is_available_priortype(paramdef["category"]):
                        priorfunction_subclass = manager.get_priorfunc_subclass(paramdef["category"])
                        priorfunction_subclass.check_args(list(paramdef["args"].keys()))
                    else:
                        raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                         "".format(paramdef["category"], manager.get_available_priors()))
                if priorfunction_subclass is not None:
                    if multiple:
                        self.priorinstance_hiddenparams[hidden_param_ref][ii] = priorfunction_subclass(**paramdef["args"])
                    else:
                        self.priorinstance_hiddenparams[hidden_param_ref] = priorfunction_subclass(**paramdef["args"])

    def get_params_nb(self, param_ref=None, output_in_dict=False):
        """Return the number of parameters of the joint pdf function.

        If param_ref is None, it return the total number of parameters. If it's equal to one of the element
        if self.__param_refs__, it return the number of parameters of this specific reference.

        If you want to get the number of parameters all references included, it's the default behavior:
        self.get_params_nb().

        :param None/str/list_of_str param_ref: If not None, should be in self.__params__
        :param bool output_in_dict: If False result is a number, if True it's a dict of numbers, keys being
            parameters references (in self.__params__) and values being the number of parameters of this
            reference.
        :return int or dict_of_int res_nb/res: Number of parameters
        """
        if param_ref is None:
            l_param_refs = self.param_refs
        else:
            if isinstance(param_ref, list):
                l_param_refs = param_ref
            else:
                l_param_refs = [param_ref, ]
        res = {}
        for param_ref in l_param_refs:
            param_name_or_l_param_name = self.param_name_lists[param_ref]
            if isinstance(param_name_or_l_param_name, str):
                res[param_ref] = 1
            else:
                res[param_ref] = len(param_name_or_l_param_name)
        if output_in_dict:
            return res
        else:
            res_nb = 0
            for nb in res.values():
                res_nb += nb
            return res_nb

    def infer_hiddenparams_nb(self, hidden_param_ref=None, output_in_dict=False):
        """Infer the number of hidden params of each category from self.param_name_lists

        In case of multiple parameters, and if one chose not to explicitly provide the prior for each
        hidden parameters (leaving them to default value or specifying the same for all hidden param
        of a reference), one might have to infer the number of hidden parameters. This function is made
        to do that generically. If you want to have a different behavior overwrite it.

        :param None/str hidden_param_ref: If not None, should be in self.__hidden_param_refs__
        :param bool output_in_dict: If False result is a number, if True it's a dict of numbers, keys being
            parameters references (in self.__params__) and values being the number of parameters of this
            reference.
        """
        # Check this function can be applied
        if sum(self.multiple_params) != sum(self.multiple_hidden_params):
            raise ValueError("The number of multiple parameters and multiple hidden parameters are different."
                             "The automatic get_nb_hiddenparams function cannot apply. Override it.")
        if any(self.multiple_params) or any(self.multiple_hidden_params):
            if any(logical_xor(self.multiple_params, self.multiple_hidden_params)):
                raise ValueError("The multiple_params and multiple_hidden_params list are not identical."
                                 "The automatic get_nb_hiddenparams cannot be applied. Override it.")
        # Set the list of hidden parameter references for which we want to infer the number
        if hidden_param_ref is None:
            l_hiddenparam_refs = self.hidden_param_refs
        else:
            if isinstance(hidden_param_ref, list):
                l_hiddenparam_refs = hidden_param_ref
            else:
                l_hiddenparam_refs = [hidden_param_ref, ]
        # Infer the number of hidden parameters of the references in l_hiddenparam_refs
        res = {}
        if any(self.multiple_params) or any(self.multiple_hidden_params):
            for hidden_param_ref in l_hiddenparam_refs:
                idx = self.hidden_param_refs.index(hidden_param_ref)
                res[hidden_param_ref] = self.get_params_nb(self.param_refs[idx])
        else:
            for hidden_param_ref in l_hiddenparam_refs:
                res[hidden_param_ref] = 1
        if output_in_dict:
            return res
        else:
            res_nb = 0
            for nb in res.values():
                res_nb += nb
            return res_nb

    def get_param_idx(self, param_name):
        """Return the index of the parameter in the list of parameter of the joint pdf function.

        :param str param_name: Name of the parameter (should be in self.param_name_fulllist)
        :return int idx: Index of the parameter in the list of parameter of the joint pdf function.
            Raise ValueError if not found.
        """
        return self.param_name_fulllist.index(param_name)

    def set_hiddenparam_defs(self, hiddenparam_def_provided):
        """Set the content of self.hiddenparam_defs

        Fill self.hiddenparam_defs. It's a dictionary which contains the definition of the priors
        of the hidden parameters. Keys are hidden parameter name and values are dictionary defining
        the prior to be used for each hidden parameter. It should follow the following format:
        {"category": priorcat, "args": {"arg1":0, "arg2":1}} like for marginal priors

        :param dict_of_dict hiddenparam_def_provided: dictionary providing the hidden parameters prior definitions
            provided by the user in the parameter file.
            Structure: {"hidden_param_ref" + "_prior": {"category": prior_cat, "args": {dict of prior arguments}}}
        """
        # I should be able to define a default set_hiddenparam_defs function with
        # self.param_name_lists and self.default_hidden_priors
        # Compare the number of parameters to the number of prior provided for the hidden parameters.
        for hidden_param_ref, multiple in zip(self.hidden_param_refs, self.multiple_hidden_params):
            nb_hiddenparam = self.infer_hiddenparams_nb(hidden_param_ref=hidden_param_ref)
            paramdef_provided = hiddenparam_def_provided.get(hidden_param_ref + self.hiddenparampriorarg_ext, None)
            if isinstance(paramdef_provided, list):
                l_paramdef_provided = paramdef_provided.copy()
            else:
                l_paramdef_provided = [paramdef_provided for i in range(nb_hiddenparam)]
            if len(l_paramdef_provided) != nb_hiddenparam:
                raise ValueError("The hidden parameter prior definition is invalid for a parameter with"
                                 "the following characteristics: multiple={}, nb_hidden_param={}."
                                 "Provided defintion: {} ".format(multiple, nb_hiddenparam, paramdef_provided))
            for ii, paramdef in enumerate(l_paramdef_provided):
                if multiple:
                    if paramdef is not None:
                        self.hiddenparam_defs[hidden_param_ref][ii] = paramdef
                else:
                    if paramdef is not None:
                        self.hiddenparam_defs[hidden_param_ref] = paramdef


# TODO: Store in different place the joint and marginal priors ?
class Manager_Prior(object):
    """docstring for Manager_Prior Singleton class."""

    class __Mgr(object):
        """docstring for __Mgr private class of Singleton class Manager_Prior.

        For more information see Manager_Prior class.
        """
        def __init__(self):
            """__Mgr init method.

            For more information see Manager_Prior init method.
            """
            self.__priors = dict()

        def _reset_priors_database(self):
            """Reset database of available prior functions."""
            self.__priors = dict()

        def load_setup(self):
            """Load the configuration of priors defined in the setup file.

            Association prior type name and Prior_Function subclass.
            """
            f = open(setupfile_prior)
            exec(f.read())
            f.close()
            logger.debug("Setup of Manager_Prior Loaded. Available priors: {}"
                         "".format(self.get_available_priors()))

        def get_available_priors(self):
            """Returns the list of available prior types.
            ----
            Returns:
                list of string, giving the available prior types.
            """
            return list(self.__priors.keys())

        def add_available_prior(self, priorfunction_subclass):
            """Add a Prior_Function subclass to database.

            This method checks that the priorfunction_subclass is indeed a Prior_Function subclass
            before adding it to the database.
            ----
            Arguments:
                priorfunction_subclass : Subclass of Prior_Function,
                    Custom subclass of the Prior_Function Class that you want to add to the
                    database.
            """
            logger.debug("priorfunction_subclass type: {}".format(type(priorfunction_subclass)))
            if not(issubclass(priorfunction_subclass, Core_Prior_Function)):
                raise ValueError("The provided class is not a subclass of the Prior_Function"
                                 " class.")
            self.__priors.update({priorfunction_subclass.category: priorfunction_subclass})

        def get_priorfunc_subclass(self, category):
            """Return Prior_Function Subclass associated to a given prior type.
            ----
            Arguments:
                category : string,
                    Type of the prior function.
            Returns:
                priorfunction_subclass : Subclass of Prior_Function,
                    Sub-class of Prior_Function associated with the prior type.
            """
            if not self.is_available_priortype(category):
                raise ValueError("The prior type {} is not amongst the available priors {}"
                                 "".format(category, self.get_available_priors()))
            return self.__priors[category]

        def is_available_priortype(self, category):
            """Check if category refers to an available subclass of prior.
            ----
            Arguments:
                category : string,
                    Type of the prior.
            Returns:
                True if category is an available Prior_Function subclass. False otherwise.
            """
            return category in self.get_available_priors()

    instance = None

    def __init__(self):
        """Manager_Prior init method (check if singleton exists and creates it if needed).

        The init method of the inside class does:
            1. Initialise the database of available prior types
        """
        if Manager_Prior.instance is None:
            Manager_Prior.instance = Manager_Prior.__Mgr()

    def __getattr__(self, name):
        """Delegate every method or attribute call to the Singleton."""
        return getattr(self.instance, name)
