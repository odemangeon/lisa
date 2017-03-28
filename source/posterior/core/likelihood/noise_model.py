#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
noise_model module.

The objective of this module is to define the Core_NoiseModel Class and the standard noise models.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from numpy import sum as npsum
from numpy import log as nplog
from math import exp
from copy import deepcopy

from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.function_w_doc import DocFunction
from ..dataset_and_instrument.instrument import Instrument_Model


## Logger
logger = getLogger()


class Metaclass_NoiseModel(MandatoryReadOnlyAttr):

    def __init__(cls, name, bases, attrs):
        super(Metaclass_NoiseModel, cls).__init__(name, bases, attrs)
        if cls.__name__ not in ["Core_NoiseModel", ]:
            missing_attrs = ["{}".format(attr) for attr in ["lnlike_creator", "lnlike"]
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


class GaussianNoiseModel(Core_Noise_Model):
    """docstring for GaussianNoiseModel."""

    __category__ = "Gaussian"

    def __init__(self, datasimulator, instmodel_obj):
        super(GaussianNoiseModel, self).__init__(datasimulator)
        if isinstance(instmodel_obj, Instrument_Model):
            self.instmodel_obj = instmodel_obj
        else:
            raise ValueError("instmodel_obj should be a Instrument_Model instance. Got {}"
                             "".format(type(instmodel_obj)))
        if self.instmodel_obj.jitter.main:
            raise ValueError("For GaussianNoiseModel instmodel_obj.jitter should not be a "
                             "main paramater")

    def lnlike_creator(self):
        datasim_func = self.datasim_function

        def lnlike(p, data, data_err, **kwarg_data):
            model = datasim_func(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2)
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        model = self.datasim_function(p, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2)
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

    @property
    def arg_list(self):
        arg_list = super(GaussianNoiseModel, self).arg_list
        arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
        return arg_list


class GaussianNoiseModel_wdfmjitter(GaussianNoiseModel):
    """docstring for GaussianNoiseModel_wdfmjitter."""

    __category__ = "Gaussian jitter dfm"

    def __init__(self, datasimulator, instmodel_obj):
        super(GaussianNoiseModel_wdfmjitter, self).__init__(datasimulator, instmodel_obj)
        if not(instmodel_obj.jitter.main):
            raise ValueError("For GaussianNoiseModels with jitter instmodel_obj.jitter should be a "
                             "main paramater")

    @property
    def jitterfree(self):
        """Return a True if the jitter parameter is free."""
        return self.instmodel_obj.jitter.free

    @property
    def jittervalue(self):
        """Return the value of the jitter parameter."""
        return self.instmodel_obj.jitter.value

    def lnlike_creator(self):
        datasim_func, arg_list = self._extract_func_and_arglist()
        jitter_value = self.jittervalue

        if self.jitterfree:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * p[0]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))
        else:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.jitterfree:
            model = self.datasim_function(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * p[0]))
        else:
            model = self.datasim_function(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * self.jittervalue))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))

    @property
    def arg_list(self):
        arg_list = super(GaussianNoiseModel_wdfmjitter, self).arg_list
        if self.jitterfree:
            arg_list["param"] = [self.instmodel_obj.jitter.full_name] + arg_list["param"]
        return arg_list


class GaussianNoiseModel_wjittermulti(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermulti."""

    __category__ = "Gaussian jitter multi"

    def lnlike_creator(self):
        datasim_func, arg_list = self._extract_func_and_arglist()
        jitter_value = self.jittervalue

        if self.jitterfree:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))
        else:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.jitterfree:
            model = self.datasim_function(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.datasim_function(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.jittervalue))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjittermultiBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "Gaussian jitter multi Baluev"

    def lnlike_creator(self):
        datasim_func, arg_list = self._extract_func_and_arglist()
        jitter_value = self.jittervalue

        if self.jitterfree:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                                     nplog(inv_sigma2)))
        else:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                                     nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.jitterfree:
            model = self.datasim_function(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.datasim_function(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.jittervalue))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                             nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteradd(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "Gaussian jitter add"

    def lnlike_creator(self):
        datasim_func, arg_list = self._extract_func_and_arglist()
        jitter_value = self.jittervalue

        if self.jitterfree:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))
        else:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.jitterfree:
            model = self.datasim_function(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.datasim_function(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * self.jitter_value)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteraddBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "Gaussian jitter add Baluev"

    def lnlike_creator(self):
        datasim_func, arg_list = self._extract_func_and_arglist()
        jitter_value = self.jittervalue

        if self.jitterfree:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                                     nplog(inv_sigma2)))
        else:
            def lnlike(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                                     nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.jitterfree:
            model = self.datasim_function(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.datasim_function(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * self.jitter_value)))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                             nplog(inv_sigma2)))
