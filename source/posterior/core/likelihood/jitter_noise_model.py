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
from numpy import pi
from math import exp
# from collections import OrderedDict

from .core_noise_model import GaussianNoiseModel
from ...core.parameter import Parameter


## Logger
logger = getLogger()

jitter_name = "jitter"

twopi = 2 * pi


## Foreman-Mackey multiplicative jitter. Jitter param in log scale

class GaussianNoiseModel_wdfmjitter(GaussianNoiseModel):
    """docstring for GaussianNoiseModel_wdfmjitter."""

    __mandatoryattrs__ = GaussianNoiseModel.__mandatoryattrs__.copy()
    __mandatoryattrs__.append("jitter_type")
    __category__ = "gaussian_jitter_dfm"
    __has_jitter__ = True
    __jitter_type__ = "multi"

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """Check that there is a jitter main parameter in the instrument model.

        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        inst_model_obj = model_instance.instruments[instmod_fullname]
        if jitter_name in inst_model_obj.parameters:
            jitter_param = inst_model_obj.parameters[jitter_name]
            jitter_param.main = True
        else:
            inst_model_obj.add_parameter(Parameter(name=jitter_name,
                                                   name_prefix=inst_model_obj.name, main=True))
            logger.debug("{} main parameter added in instruments model {}."
                         "".format(jitter_name, instmod_fullname))

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """"""
        instmod_obj = model_instance.instruments[instmod_fullname]
        err_msg = ("The noise model of instrument model {} being {}, it must have a {} "
                   "{} parameter !")
        if jitter_name not in instmod_obj.parameters:
            raise ValueError(err_msg.format(instmod_obj.get_name(include_prefix=True, recursive=True), cls.category, jitter_name, ""))
        if not(instmod_obj.parameters[jitter_name].main):
            raise ValueError(err_msg.format(instmod_obj.get_name(include_prefix=True, recursive=True), cls.category, jitter_name,
                                            "main"))

    @classmethod
    def get_prefilledlnlike(cls, l_params, l_instmod_obj, **kwargs):
        """Return a ln likelihood function prefilled with the fixed parameters.

        As this noise model doesn't require any parameters from the object model it doesn't need a
        model_instance argument. But as it might be privided one automatically, I put the keyword
        arguments **kwargs.

        :param InstrumentModel/list_of_InstrumentModel l_instmod_obj: Instument model or list of
            instrument model for the ln likelihood to produce.
        :param list_of_string l_params: Current list of parameters full names.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_new: Updated list of parameters full names.
        :return list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        l_func = []
        l_params_new = l_params
        l_params_noisemod = []
        l_idx_param_noisemod = []
        for instmod_obj in l_instmod_obj:
            (lnlike_1instmod, l_params_new, l_params_noisemod,
             l_idx_param_noisemod) = cls.get_prefilledlnlike_1instmod(l_params_new,
                                                                      l_params_noisemod,
                                                                      l_idx_param_noisemod,
                                                                      instmod_obj)
            l_func.append(lnlike_1instmod)

        def lnlike_jitter(model, param_noisemod, l_datakwargs):
            res = 0
            for ii, func, datakwargs in zip(range(len(l_func)), l_func, l_datakwargs):
                res += func(model[ii], param_noisemod, **datakwargs)
            return res

        return lnlike_jitter, l_params_new, l_idx_param_noisemod

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_dfmjitter_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * param_noisemod[idx_jitter_param]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_dfmjitter_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_dfmjitter_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def _update_lists_params(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                             jitter_param):
        """Update the list of parameters adding the jitter parameter if necessary.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :return list_of_string l_params_lnlike: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod: Updated List of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        if jitter_param.free and (jitter_param.get_name(include_prefix=True, recursive=True) not in l_params_lnlike):
            l_params_lnlike_new = l_params_lnlike.copy()
            l_params_lnlike_new.append(jitter_param.get_name(include_prefix=True, recursive=True))
            l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
            l_idx_param_noisemod_new.append(l_params_lnlike_new.index(jitter_param.get_name(include_prefix=True, recursive=True)))
            l_params_noisemod_new = l_params_noisemod.copy()
            l_params_noisemod_new.append(jitter_param.get_name(include_prefix=True, recursive=True))
        else:
            l_params_lnlike_new = l_params_lnlike
            l_idx_param_noisemod_new = l_idx_param_noisemod
            l_params_noisemod_new = l_params_noisemod
        return l_params_lnlike_new, l_params_noisemod_new, l_idx_param_noisemod_new


## Multiplicative jitter. Jitter param in log scale

class GaussianNoiseModel_wjittermulti(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermulti."""

    __category__ = "gaussian_jitter_multi"

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_jittermulti_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * param_noisemod[idx_jitter_param]))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermulti_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermulti_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)


class GaussianNoiseModel_wjittermultiBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "gaussian_jitter_multi_Baluev"

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        nparam = len(l_params_lnlike) - len(l_params_noisemod)  # For the Baluev Coefficient
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_jittermultiBaluev_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * param_noisemod[idx_jitter_param]))
                Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermultiBaluev_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                Bualev_coeff = 1.0 / (1 - (nparam / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermultiBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)


## Addtive jitter which add a fraction of the existing error. Jitter param in log scale

class GaussianNoiseModel_wjitteraddfrac(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_add_frac"
    __jitter_type__ = "add"

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_jitteraddfrac_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * param_noisemod[idx_jitter_param])))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfrac_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfrac_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)


class GaussianNoiseModel_wjitteraddfracBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "gaussian_jitter_add_frac_Baluev"
    __jitter_type__ = "add"

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        nparam = len(l_params_lnlike) - len(l_params_noisemod)  # For the Baluev Coefficient
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_jitteraddfracBaluev_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * param_noisemod[idx_jitter_param])))
                Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfracBaluev_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfracBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)


## Purely Addtive jitter which add a fraction of the existing error. Jitter param in LINEAR scale

class GaussianNoiseModel_wjitteradd(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_add"
    __jitter_type__ = "add"

    @classmethod
    def get_prefilledlnlike_1instmod(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                                     instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params_lnlike: Current list of parameters full names for the
            lnlikehood function.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        :param InstrumentModel instmod_obj: Instument_Model for which we want to produce the ln
            likelihood.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_lnlike_new: Updated list of parameters full names for the
            lnlikehood function.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the
            noise model only.
        :return list_of_int l_idx_param_noisemod_new: Updated list of the index of the noise model
            parameters in the updated list of parameters (l_params_new).
        """
        # Get jitter parameter for the instrument model
        jitter_param = instmod_obj.parameters[jitter_name]
        (l_params_lnlike_new, l_params_noisemod_new,
         l_idx_param_noisemod_new) = cls._update_lists_params(l_params_lnlike, l_params_noisemod,
                                                              l_idx_param_noisemod, jitter_param)

        # Produce the lnlike dfmjitter for one instrument if the jitter param is free or not.
        if jitter_param.free:
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))

            def lnlike_jitteradd_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 + param_noisemod[idx_jitter_param]**2)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteradd_1instmod(model, param_noisemod, data, data_err):
                inv_sigma2 = 1.0 / (data_err**2 + jitter_value**2)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteradd_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)
