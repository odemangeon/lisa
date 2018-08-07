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
    def check_param(cls, params):
        pass    
