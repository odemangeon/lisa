#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Core_Prior functions module.
"""
from ....tools.metaclasses import MandatoryReadOnlyAttr


class Metaclass_PriorFunction(MandatoryReadOnlyAttr):

    @property
    def all_args(cls):
        """Return the name of the prior type."""
        return cls.mandatory_args + cls.extra_args

    def __new__(cls, classname, bases, classdict):
        classdict["all_args"] = property(cls.all_args)
        return super(Metaclass_PriorFunction, cls).__new__(cls, classname, bases, classdict)

    def __init__(cls, name, bases, attrs):
        super(Metaclass_PriorFunction, cls).__init__(name, bases, attrs)
        if cls.__name__ not in ["Core_Prior_Function", "Core_JointPriorFunction"]:
            missing_attrs = ["{}".format(attr) for attr in ["logpdf", "ravs"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Prior_Function(object, metaclass=Metaclass_PriorFunction):
    """Docstring for Prior Prior function class."""

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "joint"]
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


class Core_JointPriorFunction(Core_Prior_Function):
    """docstring for Core_JointPriorFunction."""

    __mandatoryattrs__ = ["category", "mandatory_args", "extra_args", "joint", "params"]
    __joint__ = True

    @classmethod
    def check_param(cls, params, model_instance):
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
                             "".format(self.category, len(unexpected_paramskeys), unexpected_paramskeys,
                                       len(missing_paramskeys), missing_paramskeys))
        else:
            logger.debug("The params keys provided for Joint prior category {} are correct.")
        # Check that the parameter names correspond to existing params and that they are main parameters
        l_main_paramnames = model_instance.get_list_paramnames(main=True, recursive=True, full_name=True)
        for param_name in params.values():
            if param_name not in l_main_paramnames:
                raise ValueError("Parameter name {} doesn't exist in the model.".format(param_name))
        logger.debug("The parameters name provided for Joint prior category all correspond to "
                     "existing parameters")
