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

from ....tools.metaclasses import MandatoryReadOnlyAttr, MandatoryMethods
from ....software_parameters import setupfile_prior


## logger object
logger = getLogger()


class Metaclass_PriorFunction(MandatoryReadOnlyAttr, MandatoryMethods):

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


class Core_Prior_Function(object, metaclass=Metaclass_PriorFunction):
    """Docstring for Prior Prior function class."""

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "joint"]
    __mandatorymeths__ = ["create_logpdf", "ravs"]
    __joint__ = False

    def __init__(self):
        super(Core_Prior_Function, self).__init__()
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


class Core_JointPrior_Function(Core_Prior_Function):
    """docstring for Core_JointPrior_Function.

    When creating a new Joint Prior, you need to create a subclass of Core_JointPrior_Function.
    In this subclass, you should define the class attributes listed below in __mandatoryattrs__:
        - __category__ : Unique string identifying the category of the Prior (used in the parameter
            file to select the prior)
        - __mandatory_args__ : List of string giving the mandatory arguments to be provided when
            initialising the prior.
        - __extra_args__ :  List of string giving additional optional arguments that may be provided
            when initialising the prior.
        - __params__ : List of string giving the internal parameter references (used in the parameter
            file to identify which parameter in the model is used by the joint prior and how).

    In this subclass, you should also define the methods listed below in __mandatorymeths__:
        - def create_logpdf(self, params): Return the logarithmic probability density function for
            the joint prior.
            :param dict params: Dictionnary which contains the Parameter instances required by the prior.
                The keys are parameter keys in the self.params list and the values are the parameter instances
                as associated in the parameter file.
            :return function logpdf: log pdf the order in which the parameter should be provided is
                provided by self.params
        - def ravs(self, nb_values=1): Return values of the parameters drawn from the joint prior.
            :param int nb_values: Number of values to draw for each parameter.
            :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
                for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
                The order of the parameters in the tuple is provided by self.params.
        - set_dico_priors_arg(self, **kwargs): Fill self.dico_priors_arg. It's a dictionary which contains
            the prior information of the hidden parameters. Keys are hidden parameter name and values
            are dictionary defining the prior to be used for each hidden parameter. It should follow the
            following format: {"category": priorcat, "args": {"arg1":0, "arg2":1}} like for marginal priors
    """

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "params"]
    __mandatorymeths__ = ["create_logpdf", "ravs", "set_dico_priors_arg"]
    __joint__ = True

    def __init__(self, **kwargs):
        # Initialise self.dico_priors_arg
        self.dico_priors_arg = {}
        # Fill self.dico_priors_arg with the prior info of the hidden parameters
        self.set_dico_priors_arg(**kwargs)
        # Create the prior function instance of the hidden parameter
        # and store it in self.dico_priors_arg[hidden_param]["priorfunc_instance"]
        manager = Manager_Prior()
        for param, prior_args in self.dico_priors_arg.items():
            if manager.is_available_priortype(prior_args["category"]):
                priorfunction_subclass = manager.get_priorfunc_subclass(prior_args["category"])
                priorfunction_subclass.check_args(list(prior_args["args"].keys()))
            else:
                raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                 "".format(prior_args["category"], manager.get_available_priors()))
            self.dico_priors_arg[param]["priorfunc_instance"] = priorfunction_subclass(**prior_args["args"])

    @classmethod
    def check_params(cls, params, model_instance):
        """Check that the parameters dictionnary provided for the Joint prior is correct.

        Check that the parameters keys provided are the ones required by the definition of the prior.
        Check that the parameters names provided correspond to existing parameters.

        :param dict params: Dictionnary containing as keys the keys defined in the Joint prior
            __params__ attribute and as values the names of the model parameters to be used for each
            key.
        :param Core_Model model_instance: model instance to be able to check the the parameter names
            provided in params are valid.
        """
        # Check that the parameter keys are good
        set_paramskeys_expected = set(cls.params)
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
        for param_key, param_name in params.items():
            found = model_instance.has_parameter(param_name, recursive=True)
            dico_params_found[param_name] = found
        if not(all(list(dico_params_found.values()))):
            raise ValueError("Parameter names {} doesn't exist in the model.".format([param_name for param_name, found in dico_params_found.items() if not(found)]))
        logger.debug("The parameters name provided for Joint prior category all correspond to "
                     "existing parameters")

    @property
    def dico_priorfunction(self):
        """Dictionary containing the prior function instances for each physical parameters.

        The physical parameter keys are Pb, Pc, eb, ec, omegab, omegac
        """
        return {param: self.dico_priors_arg[param]["priorfunc_instance"] for param in self.dico_priors_arg.keys()}


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
