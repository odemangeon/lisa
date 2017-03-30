#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_noise_model module.

The objective of this module is to define the Core_NoiseModel Class.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from copy import deepcopy

from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.function_w_doc import DocFunction


## Logger
logger = getLogger()


class Metaclass_NoiseModel(MandatoryReadOnlyAttr):

    def __init__(cls, name, bases, attrs):
        super(Metaclass_NoiseModel, cls).__init__(name, bases, attrs)
        l_mandatory_methods = ["lnlike_creator", "lnlike"]
        if cls.__name__ not in ["Core_Noise_Model", ]:
            missing_attrs = ["{}".format(attr) for attr in l_mandatory_methods
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Noise_Model(object, metaclass=Metaclass_NoiseModel):
    """Docstring for Core_Noise_Model class."""

    __mandatoryattrs__ = ["category", ]

    def __init__(self, datasim_docfunc):
        if isinstance(datasim_docfunc, DocFunction):
            self.datasim_docfunc = datasim_docfunc
        else:
            raise ValueError("datasim_docfunc should be a DocFunction instance. Got {}"
                             "".format(type(datasim_docfunc)))
        # Make Core_NoiseModel an abstract class
        if type(self) is Core_Noise_Model:
            raise NotImplementedError("Core_NoiseModel should not be instanciated!")

    def __call__(self, p, data, data_err, **kwarg_data):
        return self.lnlike(p, data, data_err, **kwarg_data)

    @property
    def datasim_function(self):
        """Return the datasim function."""
        return self.datasim_docfunc.function

    @property
    def arg_list(self):
        return deepcopy(self.datasim_docfunc)

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For this noise model there is no additional parameter required.

        If you create your own noise model and you need additional parameter you should superseed
        this method to create those parameter and make them main parameters.
        """
        pass
