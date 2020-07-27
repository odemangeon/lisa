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


## Defintion of the apply jitter functions
def apply_jitter_dfm(data_err, jitter, model):
    """Apply jitter to the data error bar according the Daniel Foreman-Mackey example

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :param array_float model: model values
    :param bool var: If true return Variance, else std
    :return array_float res: new variance
    """
    return data_err**2 + model**2 * exp(2 * jitter)


def apply_jitter_multi(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return (data_err * jitter)**2


def get_Baluev_coeff(nparam, ndata):
    """Apply jitter to the data error bar.

    :param int nparam: Number of model parameters
    :param int ndata: Number of data points
    :return array_float res: new variance
    """
    return 1 - (nparam / ndata)


def apply_jitter_multi_log(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return data_err**2 * exp(2 * jitter)


def apply_jitter_addfrac_log(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return data_err**2 * (1 + exp(2 * jitter))


def apply_jitter_addfrac(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return data_err**2 * (1 + jitter**2)


def apply_jitter_add(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return data_err**2 + jitter**2


def apply_jitter_addlog(data_err, jitter):
    """Apply jitter to the data error bar.

    :param array_float data_err: data error array
    :param float jitter: jitter value
    :return array_float res: new variance
    """
    return data_err**2 + exp(2 * jitter)


## Foreman-Mackey multiplicative jitter. Jitter param in log scale
class GaussianNoiseModel_wdfmjitter(GaussianNoiseModel):
    """docstring for GaussianNoiseModel_wdfmjitter."""

    __mandatoryattrs__ = GaussianNoiseModel.__mandatoryattrs__.copy()
    __mandatoryattrs__.append("jitter_type")
    __category__ = "gaussian_jitter_dfm_log"
    __has_jitter__ = True
    __jitter_type__ = "multi"

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """Check that there is a jitter main parameter in the instrument model.

        This function is called by Core_Model.set_noisemodels

        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        inst_model_obj = model_instance.instruments[instmod_fullname]
        if inst_model_obj.has_parameter(name=jitter_name):
            jitter_param = inst_model_obj.get_parameter(name=jitter_name)
            if not jitter_param.main:
                jitter_param.main = True
        else:
            inst_model_obj.add_parameter(Parameter(name=jitter_name, name_prefix=inst_model_obj.name,
                                                   main=True
                                                   )
                                         )
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
    def get_prefilledlnlike(cls, l_likelihood_param_fullname, l_instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        As this noise model doesn't require any parameters from the model instance, it doesn't need a
        model_instance argument. But as it might be privided one automatically, I put the keyword
        arguments **kwargs.

        Parameters
        ----------
        l_datasim_param_fullname      : list of String
            Current list of parameters full names.
        l_instmod_obj : list of InstrumentModel
            List of instrument model for the lnlikelihood. There is one element per dataset modeled by
            the datasimulator following this noise model.

        Returns
        -------
        prefilled_lnlike     : function
            Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        l_params_new         : list of String
            Updated list of parameters full names.
        l_idx_param_noisemod : list of Integers
            List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        l_func = []
        l_params_new = l_likelihood_param_fullname
        l_params_noisemod = []
        l_idx_param_noisemod = []
        for instmod_obj in l_instmod_obj:
            (lnlike_1instmod, l_params_new, l_params_noisemod,
             l_idx_param_noisemod) = cls.get_prefilledlnlike_1instmod(l_params_new,
                                                                      l_params_noisemod,
                                                                      l_idx_param_noisemod,
                                                                      instmod_obj)
            l_func.append(lnlike_1instmod)

        def lnlike_jitter(sim_data, param_noisemodel, datasets_kwargs):
            res = 0
            for ii, func, datakwargs in zip(range(len(l_func)), l_func, datasets_kwargs):
                res += func(sim_data[ii], param_noisemodel, **datakwargs)
            return res

        return lnlike_jitter, l_params_new, l_params_noisemod, l_idx_param_noisemod

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
            idx_jitter_param = l_params_noisemod_new.index(jitter_param.full_name)

            def lnlike_dfmjitter_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * param_noisemod[idx_jitter_param]))
                inv_sigma2 = 1.0 / apply_jitter_dfm(data_err, param_noisemod[idx_jitter_param], model)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_dfmjitter_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * jitter_value))
                inv_sigma2 = 1.0 / apply_jitter_dfm(data_err, jitter_value, model)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_dfmjitter_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter, model):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :param array_float model: model values
        :return array_float res: new variance
        """
        return apply_jitter_dfm(data_err, jitter, model)


## Multiplicative jitter.

# Jitter param in linear scale

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
                # inv_sigma2 = 1.0 / (data_err * param_noisemod[idx_jitter_param])**2
                inv_sigma2 = 1.0 / apply_jitter_multi(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermulti_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err * jitter_value)**2
                inv_sigma2 = 1.0 / apply_jitter_multi(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermulti_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_multi(data_err, jitter)


class GaussianNoiseModel_wjittermultiBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "gaussian_jitter_multiBaluev"

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
                # inv_sigma2 = 1.0 / (data_err * param_noisemod[idx_jitter_param])**2
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_multi(data_err, param_noisemod[idx_jitter_param])
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermultiBaluev_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err * jitter_value)**2
                # Bualev_coeff = 1.0 / (1 - (nparam / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_multi(data_err, jitter_value)
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermultiBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter, nparam, ndata):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :param int nparam: Number of model parameters
        :param int ndata: Number of data points
        :return array_float res: new variance
        """
        return apply_jitter_multi(data_err, jitter) * get_Baluev_coeff(nparam, ndata)


# Jitter param in log scale

class GaussianNoiseModel_wjittermultilog(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermulti."""

    __category__ = "gaussian_jitter_multi_log"

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
                # inv_sigma2 = 1.0 / (data_err**2 * exp(2 * param_noisemod[idx_jitter_param]))
                inv_sigma2 = 1.0 / apply_jitter_multi_log(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermulti_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                inv_sigma2 = 1.0 / apply_jitter_multi_log(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermulti_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_multi_log(data_err, jitter)


class GaussianNoiseModel_wjittermultiBaluevlog(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjittermultiBaluev."""

    __category__ = "gaussian_jitter_multi_Baluev_log"

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
                # inv_sigma2 = 1.0 / (data_err**2 * exp(2 * param_noisemod[idx_jitter_param]))
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_multi_log(data_err, param_noisemod[idx_jitter_param])
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jittermultiBaluev_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * exp(2 * jitter_value))
                # Bualev_coeff = 1.0 / (1 - (nparam / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_multi_log(data_err, jitter_value)
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jittermultiBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter, nparam, ndata):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :param int nparam: Number of model parameters
        :param int ndata: Number of data points
        :return array_float res: new variance
        """
        return apply_jitter_multi_log(data_err, jitter) * get_Baluev_coeff(nparam, ndata)


## Addtive jitter which add a fraction of the existing error.

# Jitter param in log scale

class GaussianNoiseModel_wjitteraddfraclog(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_addfrac_log"
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
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * param_noisemod[idx_jitter_param])))
                inv_sigma2 = 1.0 / apply_jitter_addfrac_log(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfrac_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                inv_sigma2 = 1.0 / apply_jitter_addfrac_log(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfrac_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_addfrac_log(data_err, jitter)


class GaussianNoiseModel_wjitteraddfracBaluevlog(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "gaussian_jitter_addfracBaluev_log"
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
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * param_noisemod[idx_jitter_param])))
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_addfrac_log(data_err, param_noisemod[idx_jitter_param])
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfracBaluev_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * jitter_value)))
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_addfrac_log(data_err, jitter_value)
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfracBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter, nparam, ndata):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :param int nparam: Number of model parameters
        :param int ndata: Number of data points
        :return array_float res: new variance
        """
        return apply_jitter_addfrac_log(data_err, jitter) * get_Baluev_coeff(nparam, ndata)


# Jitter param in linear scale

class GaussianNoiseModel_wjitteraddfrac(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_addfrac"
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
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + param_noisemod[idx_jitter_param]**2))
                inv_sigma2 = 1.0 / apply_jitter_addfrac(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfrac_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + jitter_value**2))
                inv_sigma2 = 1.0 / apply_jitter_addfrac(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfrac_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_addfrac(data_err, jitter)


class GaussianNoiseModel_wjitteraddfracBaluev(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteraddBaluev."""

    __category__ = "gaussian_jitter_addfracBaluev"
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
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + param_noisemod[idx_jitter_param]**2))
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_addfrac(data_err, param_noisemod[idx_jitter_param])
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteraddfracBaluev_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 * (1 + jitter_value**2))
                # Bualev_coeff = 1.0 / (1 - ((nparam + 1) / len(data)))
                inv_sigma2 = 1.0 / apply_jitter_addfrac(data_err, jitter_value)
                Bualev_coeff = 1.0 / get_Baluev_coeff(nparam, len(data))
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteraddfracBaluev_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

        @classmethod
        def apply_jitter(cls, data_err, jitter, nparam, ndata):
            """Apply jitter to the data error bar.

            :param array_float data_err: data error array
            :param float jitter: jitter value
            :param int nparam: Number of model parameters
            :param int ndata: Number of data points
            :return array_float res: new variance
            """
            return apply_jitter_addfrac(data_err, jitter) * get_Baluev_coeff(nparam, ndata)


## Purely Addtive jitter

# Jitter param in linear scale

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
                # inv_sigma2 = 1.0 / (data_err**2 + param_noisemod[idx_jitter_param]**2)
                inv_sigma2 = 1.0 / apply_jitter_add(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteradd_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 + jitter_value**2)
                inv_sigma2 = 1.0 / apply_jitter_add(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteradd_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_add(data_err, jitter)


# Jitter param in log scale

class GaussianNoiseModel_wjitteraddlog(GaussianNoiseModel_wdfmjitter):
    """docstring for GaussianNoiseModel_wjitteradd."""

    __category__ = "gaussian_jitter_add_log"
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
                # inv_sigma2 = 1.0 / (data_err**2 + exp(2 * param_noisemod[idx_jitter_param]))
                inv_sigma2 = 1.0 / apply_jitter_addlog(data_err, param_noisemod[idx_jitter_param])
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))
        else:
            jitter_value = jitter_param.value

            def lnlike_jitteradd_1instmod(model, param_noisemod, data, data_err):
                # inv_sigma2 = 1.0 / (data_err**2 + exp(2 * jitter_value))
                inv_sigma2 = 1.0 / apply_jitter_addlog(data_err, jitter_value)
                return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(twopi * inv_sigma2)))

        return (lnlike_jitteradd_1instmod, l_params_lnlike_new, l_params_noisemod_new,
                l_idx_param_noisemod_new)

    @classmethod
    def apply_jitter(cls, data_err, jitter):
        """Apply jitter to the data error bar.

        :param array_float data_err: data error array
        :param float jitter: jitter value
        :return array_float res: new variance
        """
        return apply_jitter_addlog(data_err, jitter)


class JitterNoiseModelInterface(object):
    """docstring for JitterNoiseModelInterface."""

    def __init__(self):
        # Update the applyparametrisation4noisemodel dictionary
        l_jitternoisemodel_class = [GaussianNoiseModel_wdfmjitter, GaussianNoiseModel_wjittermulti,
                                    GaussianNoiseModel_wjittermultiBaluev, GaussianNoiseModel_wjittermultilog,
                                    GaussianNoiseModel_wjittermultiBaluevlog, GaussianNoiseModel_wjitteraddfraclog,
                                    GaussianNoiseModel_wjitteraddfracBaluevlog, GaussianNoiseModel_wjitteraddfrac,
                                    GaussianNoiseModel_wjitteraddfracBaluev, GaussianNoiseModel_wjitteradd,
                                    GaussianNoiseModel_wjitteraddlog]
        for jitternoisemod_class in l_jitternoisemodel_class:
            self.applyparametrisation4noisemodel[jitternoisemod_class.category] = self.create_apply_parametrisation_jitternoisemod(jitternoisemod_class)  # applyparametrisation4noisemodel is created in Core_Parametrisation

    def create_apply_parametrisation_jitternoisemod(self, jitter_noisemodel_class):

        def apply_parametrisation_jitternoisemod(self=self):
            for instmod_fullname in self.get_instmodfullnames_using_noisemod(noisemod_cat=jitter_noisemodel_class.category):
                jitter_noisemodel_class.apply_parametrisation(model_instance=self, instmod_fullname=instmod_fullname)

        return apply_parametrisation_jitternoisemod
