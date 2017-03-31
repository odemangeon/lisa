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

from .core_noise_model import Core_Noise_Model
from ..model.jitter import check_parametrisation_jitter, jitter_name
from ....tools.function_w_doc import DocFunction


## Logger
logger = getLogger()


class GaussianNoiseModel(Core_Noise_Model):
    """docstring for GaussianNoiseModel."""

    __category__ = "gaussian"
    __allow_multidataset__ = False

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        super(GaussianNoiseModel, self).__init__(datasim_docfunc=datasim_docfunc,
                                                 model_instance=model_instance,
                                                 instmodel_obj=instmodel_obj)
        if jitter_name in instmodel_obj.parameters:
            logger.warning("The noise model of instrument model {} being Gaussian, it should not "
                           "have a {} parameter !".format(instmodel_obj.full_name, jitter_name))
            if instmodel_obj.parameters[jitter_name].main:
                raise ValueError("For GaussianNoiseModel instmodel_obj.jitter should not be a "
                                 "main paramater")

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()

        def lnlike(p, data, data_err, **kwarg_data):
            model = datasim_func(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2)
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

        return DocFunction(function=lnlike, arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, **kwarg_data):
        model = self.get_datasim_function()(p, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2)
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

    @property
    def arg_list(self):
        arg_list = super(GaussianNoiseModel, self).arg_list
        arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
        return arg_list


class GaussianNoiseModel_wdfmjitter(GaussianNoiseModel):
    """docstring for GaussianNoiseModel_wdfmjitter."""

    __category__ = "gaussian_jitter_dfm"

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        super(GaussianNoiseModel, self).__init__(datasim_docfunc=datasim_docfunc,
                                                 model_instance=model_instance,
                                                 instmodel_obj=instmodel_obj)
        self.__instmodel_obj = instmodel_obj
        if not(instmodel_obj.jitter.main):
            raise ValueError("For GaussianNoiseModels with jitter instmodel_obj.jitter should be a "
                             "main paramater")

    @property
    def instmodel_obj(self):
        return self.__instmodel_obj

    @property
    def jitterfree(self):
        """Return a True if the jitter parameter is free."""
        return self.instmodel_obj.jitter.free

    @property
    def jittervalue(self):
        """Return the value of the jitter parameter."""
        return self.instmodel_obj.jitter.value

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()
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
            model = self.get_datasim_function()(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function()(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * self.jittervalue))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))

    @property
    def arg_list(self):
        arg_list = super(GaussianNoiseModel_wdfmjitter, self).arg_list
        if self.jitterfree:
            arg_list["param"] = [self.instmodel_obj.jitter.full_name] + arg_list["param"]
        return arg_list

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For more information see check_parametrisation_jitter."""
        check_parametrisation_jitter(model_instance=model_instance,
                                     instmod_fullname=instmod_fullname)


class GaussianNoiseModel_wjittermulti(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermulti."""

    __category__ = "gaussian_jitter_multi"

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()
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
            model = self.get_datasim_function()(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function()(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.jittervalue))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjittermultiBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "gaussian_jitter_multi_Baluev"

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()
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
            model = self.get_datasim_function()(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function()(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.jittervalue))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                             nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteradd(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_add"

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()
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
            model = self.get_datasim_function()(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.get_datasim_function()(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * self.jitter_value)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteraddBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "gaussian_jitter_add_Baluev"

    def lnlike_creator(self):
        datasim_func = self.get_datasim_function()
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
            model = self.get_datasim_function()(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.get_datasim_function()(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * self.jitter_value)))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff +
                             nplog(inv_sigma2)))
