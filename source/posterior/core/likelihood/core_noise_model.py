#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_noise_model module.

The objective of this module is to define the Core_NoiseModel Class. This module also provide
the GaussianNoiseModel.
The noise model has to set the parameterisation (add new parameters if needed, for example the
jitter parameters or the GP parameters) and provide the way the likelihood is computed.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import Iterable
from numpy import sum as npsum
from numpy import log as nplog

from ....tools.metaclasses import MandatoryReadOnlyAttr


## Logger
logger = getLogger()


class Metaclass_NoiseModel(MandatoryReadOnlyAttr):

    def __init__(cls, name, bases, attrs):
        super(Metaclass_NoiseModel, cls).__init__(name, bases, attrs)
        l_mandatory_methods = []
        # ["lnlike_creator", "lnlike", "_check_parametrisation_dataset", "apply_parametrisation"]
        if cls.__name__ not in ["Core_Noise_Model", ]:
            missing_attrs = ["{}".format(attr) for attr in l_mandatory_methods
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Noise_Model(object, metaclass=Metaclass_NoiseModel):
    """Docstring for Core_Noise_Model class."""

    __mandatoryattrs__ = ["category", "has_GP", "has_jitter"]
    __kwargs_needed__ = ["data", "data_err"]

    def __init__(self):
        """Init method to make Core_Noise_Model an abstract class (not instantiable).
        """
        # Make Core_NoiseModel an abstract class
        if type(self) is Core_Noise_Model:
            raise NotImplementedError("Noise_Model are abstract class they  should not be "
                                      "instanciated. Use the class itself")

    @classmethod
    def apply_parametrisation(cls, model_instance=None, instmod_fullname=None):
        """Add in the model the necessary main parameters for the noise model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        raise NotImplementedError("You need to implement a apply_parametrisation method for your "
                                  "noise model.")

    @classmethod
    def check_parametrisation(cls, model_instance=None, instmod_fullname=None):
        """Check the parameteristion for the noise model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        raise NotImplementedError("You need to implement a check_parametrisation method for your "
                                  "noise model.")

    @classmethod
    def get_prefilledlnlike(cls, l_params, model_instance=None, l_instmod_obj=None):
        """Return a ln likelihood function prefilled with the fixed parameters.

        :param list_of_string l_params: Current list of parameters full names.
        :param Instrument_Model/list_of_InstrumentModel l_instmod_obj: Instument model or list of
            instrument model for the ln likelihood to produce.
        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_new: Updated list of parameters full names.
        :return list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        raise NotImplementedError("You need to ovewrite the get_prefilledlnlike method for your "
                                  "noise model.")

    @classmethod
    def get_necessary_datakwargs(cls, dataset):
        """Return the data kwargs necessary for the computation of the likelihood.

        :param Dataset dataset: Dataset instance.
        :return dict datakwargs: dict with keys= datakwargs type (eg. "data"), value= value(s) of
            this datakwarg for this dataset.
        """
        raise NotImplementedError("You need to ovewrite the get_necessary_datakwargs method for "
                                  "your noise model.")

    @classmethod
    def _check_l_instmod_obj(cls, l_instmod_obj):
        """Check the l_instmod_obj parameter.

        :param Instrument_Model/list_of_InstrumentModel l_instmod_obj: Instument model or list of
            instrument model for the ln likelihood to produce.
        :return list_of_InstrumentModel l_instmod_obj_new: Return a checked list of instrument model
            object
        """
        from ..dataset_and_instrument.instrument import Instrument_Model
        if isinstance(l_instmod_obj, Instrument_Model):
            return [l_instmod_obj]
        elif isinstance(l_instmod_obj, Iterable):
            if isinstance(l_instmod_obj[0], Instrument_Model):
                return l_instmod_obj
        raise ValueError("l_instmod_obj should be an Instrument_Model or an Iterable of "
                         "Instrument_Models")


class GaussianNoiseModel(Core_Noise_Model):
    """docstring for GaussianNoiseModel."""

    __category__ = "gaussian"
    __has_GP__ = False
    __has_jitter__ = False

    @classmethod
    def apply_parametrisation(cls, **kwargs):
        """For this noise model there is no additional parameter required.

        However this method needs to exist because the model will call it. kwargs is only to accept
        the template function call as define in Core_Noise_Model.
        """
        pass

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For this noise model there is no additional parameter required.

        So nothing to check
        """
        pass

    @classmethod
    def get_prefilledlnlike(cls, l_params, **kwargs):
        """Return a ln likelihood function prefilled with the fixed parameters.

        As there is no parameter for this noise model, it doesn't need a l_instmod_obj or a
        model_instance argument. But as it might be privided one automatically, I put the keyword
        arguments **kwargs.

        :param list_of_string l_params: Current list of parameters full names.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_new: Updated list of parameters full names.
        :return list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        def lnlike(model, param_noisemod, l_datakwargs):
            res = 0
            for ii, datakwargs in enumerate(l_datakwargs):
                inv_sigma2 = 1.0 / (datakwargs["data_err"]**2)
                res += (-0.5 * (npsum((datakwargs["data"] - model[ii])**2 * inv_sigma2 -
                                nplog(inv_sigma2))))
            return res

        return lnlike, l_params, []

    @classmethod
    def get_necessary_datakwargs(cls, dataset):
        """Return the data kwargs necessary for the computation of the likelihood.

        :param Dataset dataset: Dataset instance.
        :return dict datakwargs: dict with keys= datakwargs type (eg. "t"), value= value(s) of this
            datakwarg for this dataset.
        """
        return {"data": dataset.get_data(), "data_err": dataset.get_data_err()}
