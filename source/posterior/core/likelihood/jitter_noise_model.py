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
from collections import OrderedDict

from .core_noise_model import Core_Noise_Model
from ..model.jitter import apply_parametrisation_jitter, jitter_name
from ....tools.function_w_doc import DocFunction


## Logger
logger = getLogger()


class GaussianNoiseModel(Core_Noise_Model):
    """docstring for GaussianNoiseModel."""

    __category__ = "gaussian"

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)

        def lnlike_gaussian(p, data, data_err, **kwarg_data):
            model = datasim_func(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2)
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))

        return lnlike_gaussian

    def lnlike_creator(self):
        if self.multidataset:
            l_func = []
            l_param_idx = []
            l_kwarg_idx = []
            dico_params_idx = OrderedDict()
            for i, dataset in enumerate(self.l_dataset):
                l_kwarg_idx.append(i)
                l_func.append(self._lnlike_dataset_creator(dataset))
                l_param_idx.append(self.get_param_idxs(dataset))
                dico_params_idx[dataset] = self.get_param_idxs(dataset)

            def lnlike(p, data, data_err, **kwarg_data):
                res = 0
                for func, param_idx, kwarg_idx in zip(l_func, l_param_idx, l_kwarg_idx):
                    kwargs_dataset = {}
                    for kwargs_type in kwarg_data:
                        kwargs_dataset[kwargs_type] = kwarg_data[kwargs_type][kwarg_idx]
                    res += func(p[param_idx], data[kwarg_idx], data_err[kwarg_idx],
                                **kwargs_dataset)
                return res

        else:
            lnlike = self._lnlike_dataset_creator()
            dico_params_idx = None

        return DocFunction(function=lnlike, arg_list=self.get_arg_list()), dico_params_idx

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2)
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 -
                             nplog(inv_sigma2)))

    def lnlike(self, p, data, data_err, **kwarg_data):
        if self.multidataset:
            res = 0
            for i, dataset in enumerate(self.l_dataset):
                param_idx = self.get_param_idxs(dataset)
                kwargs_dataset = {}
                for kwargs_type in kwarg_data:
                    kwargs_dataset[kwargs_type] = kwarg_data[kwargs_type][i]
                res += self._lnlike_dataset(p[param_idx], data[i], data_err[i], dataset,
                                            **kwargs_dataset)
            return res
        else:
            return self._lnlike_dataset(p, data, data_err, **kwarg_data)

    def _check_parametrisation_dataset(self, model_instance, dataset_key=None):
        instmod_obj = self.get_instmodel_obj(dataset_key)
        if jitter_name in instmod_obj.parameters:
            logger.warning("The noise model of instrument model {} being Gaussian, it should "
                           "not have a {} parameter !".format(instmod_obj.full_name,
                                                              jitter_name))
            if instmod_obj.parameters[jitter_name].main:
                raise ValueError("For GaussianNoiseModel instmodel_obj.jitter should not be a "
                                 "main paramater")

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """For this noise model there is no additional parameter required.

        But the fonction needs to exist.
        """
        pass


class GaussianNoiseModel_wdfmjitter(GaussianNoiseModel):
    """docstring for GaussianNoiseModel_wdfmjitter."""

    __category__ = "gaussian_jitter_dfm"

    def get_jitterparam(self, dataset_key=None):
        """Return the jitter parameter."""
        if self.multidataset:
            return self.get_instmodel_obj(dataset_key).jitter
        else:
            return self.get_instmodel_obj().jitter

    def _get_arg_list_one_dataset(self, dataset_key=None):
        arg_list_new = super(GaussianNoiseModel_wdfmjitter,
                             self)._get_arg_list_one_dataset(dataset_key)
        if self.get_jitterparam(dataset_key).free:
            arg_list_new["param"] = ([self.get_jitterparam(dataset_key).full_name] +
                                     arg_list_new["param"])
        return arg_list_new

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)
        jitter_free = self.get_jitterparam(dataset_key).free
        jitter_value = self.get_jitterparam(dataset_key).value
        if jitter_free:
            def lnlike_dfmjitter(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * p[0]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        else:
            def lnlike_dfmjitter(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        return lnlike_dfmjitter

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        if self.get_jitterparam(dataset_key).free:
            model = self.get_datasim_function(dataset_key)(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 +
                                model**2 * exp(2 * self.get_jitterparam(dataset_key).value))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """For more information see check_parametrisation_jitter."""
        apply_parametrisation_jitter(model_instance=model_instance,
                                     instmod_fullname=instmod_fullname)

    def _check_parametrisation_dataset(self, model_instance, dataset_key=None):
        instmod_obj = self.get_instmodel_obj(dataset_key)
        err_msg = ("The noise model of instrument model {} being {}, it must have a {} "
                   "{} parameter !")
        if jitter_name not in instmod_obj.parameters:
            raise ValueError(err_msg.format(instmod_obj.full_name, self.category, jitter_name, ""))
        if not(instmod_obj.parameters[jitter_name].main):
            raise ValueError(err_msg.format(instmod_obj.full_name, self.category, jitter_name,
                                            "main"))


class GaussianNoiseModel_wjittermulti(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermulti."""

    __category__ = "gaussian_jitter_multi"

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)
        jitter_free = self.get_jitterparam(dataset_key).free
        jitter_value = self.get_jitterparam(dataset_key).value
        if jitter_free:
            def lnlike_jittermulti(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        else:
            def lnlike_jittermulti(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        return lnlike_jittermulti

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        if self.get_jitterparam(dataset_key).free:
            model = self.get_datasim_function(dataset_key)(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.get_jitterparam(dataset_key).value))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjittermultiBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "gaussian_jitter_multi_Baluev"

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)
        jitter_free = self.get_jitterparam(dataset_key).free
        jitter_value = self.get_jitterparam(dataset_key).value
        if jitter_free:
            def lnlike_jittermultiBaluev(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                     nplog(inv_sigma2)))
        else:
            def lnlike_jittermultiBaluev(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                     nplog(inv_sigma2)))
        return lnlike_jittermultiBaluev

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        if self.get_jitterparam(dataset_key).free:
            model = self.get_datasim_function(dataset_key)(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * p[0]))
        else:
            model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * self.get_jitterparam(dataset_key).value))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteradd(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_add"

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)
        jitter_free = self.get_jitterparam(dataset_key).free
        jitter_value = self.get_jitterparam(dataset_key).value
        if jitter_free:
            def lnlike_jitteradd(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        else:
            def lnlike_jitteradd(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))
        return lnlike_jitteradd

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        if self.get_jitterparam(dataset_key).free:
            model = self.get_datasim_function(dataset_key)(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 +
                                               exp(2 * self.get_jitterparam(dataset_key).value)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))


class GaussianNoiseModel_wjitteraddBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "gaussian_jitter_add_Baluev"

    def _lnlike_dataset_creator(self, dataset_key=None):
        datasim_func = self.get_datasim_function(dataset_key)
        jitter_free = self.get_jitterparam(dataset_key).free
        jitter_value = self.get_jitterparam(dataset_key).value
        if jitter_free:
            def lnlike_jitteraddBaluev(p, data, data_err, **kwarg_data):
                model = datasim_func(p[1:], **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                     nplog(inv_sigma2)))
        else:
            def lnlike_jitteraddBaluev(p, data, data_err, **kwarg_data):
                model = datasim_func(p, **kwarg_data)
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                     nplog(inv_sigma2)))
        return lnlike_jitteraddBaluev

    def _lnlike_dataset(self, p, data, data_err, dataset_key=None, **kwarg_data):
        if self.get_jitterparam(dataset_key).free:
            model = self.get_datasim_function(dataset_key)(p[1:], **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * p[0])))
        else:
            model = self.get_datasim_function(dataset_key)(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 +
                                               exp(2 * self.get_jitterparam(dataset_key).value)))
        Bualev_coeff = 1.0 / (1 - (len(p) / len(data)))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                             nplog(inv_sigma2)))
