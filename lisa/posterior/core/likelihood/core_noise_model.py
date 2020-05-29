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
    """Docstring for Core_Noise_Model class.

    This class deal with the choice and the parametrisation of the noise models. It also provides
    the functions to compute the likelihood.

    Methods
    -------
    apply_parametrisation: Create and set to main the parameters required by the noise model
        This function is called by the Core_Model.set_noisemodels method
    check_parametrisation: Check that the parameters required by the noise model exists and set to main
    """

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

        This function is called by Core_Model.set_noisemodels for each instrument model.

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
    def create_lnlikelihood_and_formatinputs(cls, model_instance, l_idx_simdata, l_instmod_obj, l_dataset_obj, l_likelihood_param_fullname):
        """Create the prefilled lnlikehood function (without the datasim) for the noise model and provide the function to format the inputs and provide the dataset_kwargs

        This function might not be convenient for your noise model, in wich case you should overload it.

        The these output are then used by Core_likelihood.__likelihood_creator
        to finalise the lnlikelihood. In this function the pre-filled lnlikelihood for each noise model is used as follow:
        lnlike_function(sim_data=f_format_simdata(sim_data),
                        param_noisemodel=f_format_param(p),
                        datasets_kwargs=datasets_kwargs)

        Arguments
        ---------
        model_instance            : Core Model subclass
        l_idx_simdata            : list of Integers
            List of indexes in the sim_data list (output of the datasimulator function this likelihood function is associated with) which correspond to dataset that should be modeled with this noise model
        l_instmod_obj             : list of Instrument_Model instances
            List of instrument model objects that are used for the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_dataset_obj             : list of Dataset instances
            List of dataset objects that are simulated by the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_likelihood_param_fullname  : list of String
            Current list of parameter full names for the likelihood.

        Returns
        -------
        lnlike_function  : function
            function with the following arguments
                sim_data         : sim_data using this noise model, and only these, the exact format is defined by f_format_simdata
                param_noisemodel : param of the current noise model, and only these, the exact format is defined by f_format_param
                dataset_kwargs   : dataset keyword arguments used by this noise model, and only these, the exact format is defined by this function.
        f_format_param   : function
            Function to extract and format the parameter of this noise model from the vector of all the parameters of the likelihood function
        f_format_simdata : function
            Function extract and format the simulated data of the datasets using this noise model.
        datasets_kwargs  : ??
            Dataset keyword arguments of the datasets using this noise model
        l_likelihood_param_fullname_new : list of String
            New list of parameter full names for the likelihood which the l_likelihood_param_fullname +  the parameters for this noise model
        """
        lnlike_jitter, l_params_new, params_noisemod, l_idx_param_noisemod = cls.get_prefilledlnlike(l_likelihood_param_fullname, l_instmod_obj)

        def f_format_param(param_likelihood):
            return param_likelihood[l_idx_param_noisemod]

        def f_format_simdata(sim_data):
            return [sim_data[ii] for ii in l_idx_datasim]

        dataset_kwargs = []
        for dataset in l_dataset_obj:
            dataset_kwargs.append(cls.get_necessary_datakwargs(dataset))

        return lnlike_jitter, f_format_param, f_format_simdata, dataset_kwargs, l_params_new

    @classmethod
    def get_prefilledlnlike(cls, l_params, model_instance=None, l_instmod_obj=None):
        """Return a ln likelihood function prefilled with the fixed parameters.

        This function is used by LikelihoodCreator.Core_model._create_lnlikelihood()

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

    @classmethod
    def _update_lists_params(cls, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
                             param_obj):
        """Update the list of parameters of the lnlike and the noise model adding the parameter if necessary.

        This is a convenience function to be used in the subclass and especially in the get_prefilledlnlike methods to properly update the list of parameters.

        Arguments
        ---------
        l_params_lnlike      : list of String
            Current list of parameters full names for the lnlikehood function.
        l_params_noisemod    : list of String
            Current list of parameters full names for the noise model only.
        l_idx_param_noisemod : List of Integer
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        param_obj            : Parameter
            Parameter object that might be added to the lists of parameters

        Returns
        -------
        l_params_lnlike_new      : list of String
            Updated list of parameters full names for the lnlikehood function.
        l_params_noisemod_new    : list of String
            Updated list of parameters full names for the noise model only.
        l_idx_param_noisemod_new : List of Integer
            Updated List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        """
        if param_obj.free and (param_obj.full_name not in l_params_lnlike):
            l_params_lnlike_new = l_params_lnlike.copy()
            l_params_lnlike_new.append(param_obj.get_name(include_prefix=True, recursive=True))
            l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
            l_idx_param_noisemod_new.append(l_params_lnlike_new.index(param_obj.get_name(include_prefix=True, recursive=True)))
            l_params_noisemod_new = l_params_noisemod.copy()
            l_params_noisemod_new.append(param_obj.get_name(include_prefix=True, recursive=True))
        else:
            l_params_lnlike_new = l_params_lnlike
            l_idx_param_noisemod_new = l_idx_param_noisemod
            l_params_noisemod_new = l_params_noisemod
        return l_params_lnlike_new, l_params_noisemod_new, l_idx_param_noisemod_new

    @classmethod
    def apply_jitter(cls, data_err):
        """Apply jitter to the data error bar.

        But default this function doesn't do anything, if your noise model include jitter model
        and thus a modification of the error bars, you should overwrite this method.

        :param array_float data_err: data error array
        :return array_float res: new variance
        """
        return data_err**2


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
