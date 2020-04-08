#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
gp_lnlike module.

The objective of this module is to define the log likelihood in case you want to use a GP to
model the residuals.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from george.kernels import ExpSquaredKernel, ExpSine2Kernel
from george import GP
from numpy import concatenate, sqrt
from collections import defaultdict
# from collections import OrderedDict

# from ..model.celestial_bodies import Star
from ..dataset_and_instrument.rv import RV_inst_cat
from ..dataset_and_instrument.lc import LC_inst_cat
from ...core.parameter import Parameter
from ...core.likelihood.jitter_noise_model import jitter_name, GaussianNoiseModel_wjitteradd

# from ....tools.function_w_doc import DocFunction


## logger object
logger = getLogger()

stelact_GP_noisemodel = "stellar_activity"

amp = "ampSA"
tau = "tauSA"
gamma = "gammaSA"
logperiod = "lnperiodSA"

param_noisemod_name = "param_noisemod"


class StellarActNoiseModel(GaussianNoiseModel_wjitteradd):
    """docstring for StellarActNoiseModel."""

    __category__ = stelact_GP_noisemodel
    __has_GP__ = True
    __has_jitter__ = False
    __kwargs_needed__ = ["data", "data_err", "t"]

    kernel_text = ("{amp}**2 * ExpSquaredKernel(metric={tau}) * "
                   "ExpSine2Kernel(gamma={gamma}, log_period={log_period})")

    # Comment: There is no need to sort the times because George does it automicatically.
    # Before the version 0.3.1 of george, there was a sort argument (which was True by default) which need to
    # Be True to sort the x values
    lnlikefunc_text = """def {func_name}(model, param_noisemod, l_datakwargs):
        dict_datakwargs = defaultdict(list)
        for datakwargs, jitter in zip(l_datakwargs, {text_l_jitter}):
            dict_datakwargs["t"].append(datakwargs["t"])
            dict_datakwargs["data"].append(datakwargs["data"])
            dict_datakwargs["data_err"].append(sqrt(datakwargs["data_err"]**2 + jitter**2))
        gp = GP({kernel})
        gp.compute(concatenate(dict_datakwargs["t"]), concatenate(dict_datakwargs["data_err"]))
        # print(type(dict_datakwargs["data"]), len(dict_datakwargs["data"]), dict_datakwargs["data"][0].shape)
        # print(type(model), len(model), type(model[0]))
        return gp.log_likelihood((concatenate(dict_datakwargs["data"]) - concatenate(model)).reshape((-1)))
        """

    function_name = "lnlike"

    gpsim_func_text = """def {func_name}(model, param_noisemod, l_datakwargs, tsim):
        dict_datakwargs = defaultdict(list)
        for datakwargs, jitter in zip(l_datakwargs, {text_l_jitter}):
            dict_datakwargs["t"].append(datakwargs["t"])
            dict_datakwargs["data"].append(datakwargs["data"])
            dict_datakwargs["data_err"].append(sqrt(datakwargs["data_err"]**2 + jitter**2))
        gp = GP({kernel})
        gp.compute(concatenate(dict_datakwargs["t"]), concatenate(dict_datakwargs["data_err"]))
        return gp.sample_conditional((concatenate(dict_datakwargs["data"]) - concatenate(model)).reshape((-1)),
                                     tsim)
        """

    gpsim_function_name = "gp_sim"

    __star_param_GP_names = [amp, tau, gamma, logperiod]

    __allowed_inst_cat = [RV_inst_cat, LC_inst_cat]

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """Add in the model the necessary main parameters for the noise model.

        This function is called by Core_Model.set_noisemodels for each instrument model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        # Load the star and inst_model object
        star = model_instance.stars[list(model_instance.stars.keys())[0]]
        inst_model_obj = model_instance.instruments[instmod_fullname]
        inst = inst_model_obj.instrument
        inst_cat = inst.category
        if inst_cat not in cls.__allowed_inst_cat:
            raise ValueError(f"Stellar activity noise model can only be used for instrument category "
                             f"{cls.__allowed_inst_cat}, got {inst_cat}."
                             )
        # Set the star parameters (tau, gamma, logperiod, amp)
        for param_name in cls.__star_param_GP_names:
            if star.has_parameter(name=param_name):
                param = star.get_parameter(name=param_name)
                if not param.main:
                    param.main = True
            else:
                star.add_parameter(Parameter(name=param_name, name_prefix=star.name, main=True))
        # Set the instrument models parameters (jitter)
        super(StellarActNoiseModel, cls).apply_parametrisation(model_instance=model_instance, instmod_fullname=instmod_fullname)

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """Check the parameteristion for the noise model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        # Check the star parameters
        err_msg = ("The noise model of instrument model {} being {}, it must have a {} "
                   "{} parameter !")
        star = cls.get_star(model_instance)
        for param in cls.get_star_params_GP(model_instance):
            if param.get_name() not in star.parameters:
                raise ValueError(err_msg.format(instmod_fullname, cls.category, param.get_name(include_prefix=True,
                                                                                               recursive=True
                                                                                               ),
                                                "")
                                 )
            if not(param.main):
                raise ValueError(err_msg.format(instmod_fullname, cls.category, param.get_name(include_prefix=True,
                                                                                               recursive=True),
                                                "main")
                                 )
        # Check the jitter parameter
        cls.check_parametrisation(model_instance=model_instance, instmod_fullname=instmod_fullname)

    @classmethod
    def get_necessary_datakwargs(cls, dataset):
        """Return the data kwargs necessary for the computation of the likelihood.

        :param Dataset dataset: Dataset instance.
        :return dict datakwargs: dict with keys= datakwargs type (eg. "data"), value= value(s) of
            this datakwarg for this dataset.
        """
        return {"data": dataset.get_data(), "data_err": dataset.get_data_err(),
                "t": dataset.get_time()}

    @classmethod
    def get_star(cls, model_instance):
        """Return the star object used for this stellar activity noise modelling.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :return Star star: Star parameter container.
        """
        return list(model_instance.stars.values())[0]

    # @classmethod
    # def get_star_param_GP_names(cls, model_instance, free=False, full_name=False):
    #     """Return the list of the names of the paramaters of the GP model."""
    #     if full_name:
    #         return [param.get_name(include_prefix=True, recursive=True) for param in cls.get_star_params_GP(model_instance, free=free)]
    #     else:
    #         return [param.get_name() for param in cls.get_star_params_GP(model_instance, free=free)]

    @classmethod
    def get_star_params_GP(cls, model_instance, free=False):
        """Return the list of GP parameters.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param bool free: If True returns only the free parameters.
        """
        star = cls.get_star(model_instance)
        if free:
            return [getattr(star, par) for par in cls.__star_param_GP_names
                    if getattr(star, par).free]
        else:
            return [getattr(star, par) for par in cls.__star_param_GP_names]

    # @classmethod
    # def star_params_GP_isfree(cls, model_instance):
    #     """Return the list of boolean indicating if the GP parameters are free."""
    #     return [param.free for param in cls.get_star_params_GP(model_instance)]

    # @classmethod
    # def nb_params_GP_free(cls, model_instance):
    #     """Return the number of GP parameters that are free."""
    #     return len(cls.get_star_params_GP(free=True))

    @classmethod
    def __get_text_define_GP(cls, model_instance, l_params, l_params_noisemod, l_idx_param_noisemod):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity).
        :param list_of_string l_params: Current list of parameters full names.
        :param list_of_string l_params_noisemod: Current list of parameters full names for the
            noise model only.
        :param list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).

        Returns
        -------
        :return str ker: Text of the kernel. The index in the parameter array p are for the
            noise model parameter array only.
        :return list_of_string l_params_new: Updated list of parameters full names.
        :return list_of_string l_params_noisemod_new: Updated list of parameters full names for the noise model
        :return list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        dico = {}
        i_noisemod = 0
        l_params_new = l_params.copy()
        l_params_noisemod_new = l_params_noisemod.copy()
        l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
        for param in cls.get_star_params_GP(model_instance):
            if param.free:
                dico[param.get_name()] = f"{param_noisemod_name}[{i_noisemod}]"
                i_noisemod += 1
                if param.get_name(include_prefix=True, recursive=True) not in l_params_new:
                    l_params_new.append(param.get_name(include_prefix=True, recursive=True))
                l_idx_param_noisemod_new.append(l_params_new.index(param.get_name(include_prefix=True, recursive=True)))
                l_params_noisemod_new.append(param.get_name(include_prefix=True, recursive=True))
            else:
                dico[param.get_name()] = "{}".format(param.value)
        ker = cls.kernel_text.format(amp=dico[amp], tau=dico[tau],
                                     gamma=dico[gamma],
                                     log_period=dico[logperiod])
        return ker, l_params_new, l_params_noisemod_new, l_idx_param_noisemod_new

    @classmethod
    def __get_text_l_jitter(cls, l_instmod_obj, l_params, l_params_noisemod, l_idx_param_noisemod):
        """Return the text of the white noise array, the list of all parameters.

        Parameters
        ----------
        l_instmod_obj : InstrumentModel/list_of_InstrumentModel
            Instument model or list of instrument model for the ln likelihood to produce.
        l_params : list_of_string
            Current list of parameters full names.

        Returns
        -------
        text_l_jitter : str
            Text giving the list of the indexes of the jitter parameters in the list of the noise model
            parameters for each instrument in the list of instrument models
        l_params_new : list_of_string
            Current list of parameters full names.
        """
        l_params_new = l_params.copy()
        l_params_noisemod_new = l_params_noisemod.copy()
        l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
        l_jitter_paramname = []
        text_l_jitter = "["
        for instmod_obj in l_instmod_obj:
            jitter_param = instmod_obj.parameters[jitter_name]
            l_jitter_paramname.append(jitter_param.get_name(include_prefix=True, recursive=True))
            if jitter_param.free:
                if jitter_param.get_name(include_prefix=True, recursive=True) not in l_params_new:
                    (l_params_new, l_params_noisemod_new,
                     l_idx_param_noisemod_new) = cls._update_lists_params(l_params_new, l_params_noisemod_new,
                                                                          l_idx_param_noisemod_new, jitter_param)
                if jitter_param.get_name(include_prefix=True, recursive=True) not in l_params_noisemod_new:
                    l_params_noisemod_new.append(jitter_param.get_name(include_prefix=True, recursive=True))
                    l_idx_param_noisemod_new.append(l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True)))
            if jitter_param.free:
                text_l_jitter += f"{param_noisemod_name}[{l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))}], "
            else:
                text_l_jitter += f"{jitter_param.value}, "
        text_l_jitter += "]"
        return text_l_jitter, l_params_new, l_params_noisemod_new, l_idx_param_noisemod_new, l_jitter_paramname

    @classmethod
    def get_prefilledlnlike(cls, l_params, model_instance, l_instmod_obj):
        """Return a ln likelihood function prefilled with the fixed parameters.

        This function is used by LikelihoodCreator.Core_model._create_lnlikelihood()

        :param list_of_string l_params: Current list of parameters full names.
        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param Instrument_Model/list_of_InstrumentModel l_instmod_obj: Instument model or list of
            instrument model for the ln likelihood to produce.
        :return function prefilled_lnlike: Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        :return list_of_string l_params_new: Updated list of parameters full names.
        :return list_of_int l_idx_param_noisemod: List of the index of the noise model parameters in
            the updated list of parameters (l_params_new).
        """
        ldict = locals().copy()
        l_params_new = l_params.copy()
        (ker, l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod) = cls.__get_text_define_GP(model_instance=model_instance, l_params=l_params_new,
                                                          l_params_noisemod=[], l_idx_param_noisemod=[])
        (text_l_jitter,
         l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod,
         l_jitter_paramname) = cls.__get_text_l_jitter(l_instmod_obj=l_instmod_obj, l_params=l_params_new,
                                                       l_params_noisemod=l_params_noisemod,
                                                       l_idx_param_noisemod=l_idx_param_noisemod)
        func = cls.lnlikefunc_text.format(func_name=cls.function_name, kernel=ker, text_l_jitter=text_l_jitter)
        ldict["defaultdict"] = defaultdict
        ldict["list"] = list
        ldict["concatenate"] = concatenate
        ldict["logger"] = logger
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["GP"] = GP
        ldict["sqrt"] = sqrt
        logger.debug(f"Likelihood of the stellar activity model:\n {func}\nl_params_noisemod: {l_params_noisemod}, l_idx_param_noisemod: {l_idx_param_noisemod}")
        exec(func, ldict)
        return ldict[cls.function_name], l_params_new, l_params_noisemod, l_idx_param_noisemod

    @classmethod
    def get_gp_simulator(cls, l_params, model_instance, l_instmod_obj):
        """Return the simulated values with the GP at given simulated times.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity).
        :param list_of_string l_params: Current list of parameters full names.
        :return function gp_sim: gp simulator function that return the simulated gp contributions.
            :param list_of_np.array model: Values of the model for each dataset associated which
                this noise model.
            :param list_of_float param_noisemod: List of noise model parameter values.
            :param list_of_dict l_datakwargs:
            :param np.array tsim: Array of time value at which you want to compute the gp prediction
            :return np.array gp_sim_values: Array of the gp simulated values for each tsim values.
        :return list_of_str l_param_noise_mod: List of parameter full name for the noise model.
        """
        ldict = locals().copy()
        l_params_new = l_params.copy()
        (ker, l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod) = cls.__get_text_define_GP(model_instance=model_instance, l_params=l_params_new,
                                                          l_params_noisemod=[], l_idx_param_noisemod=[])
        (text_l_jitter,
         l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod,
         l_jitter_paramname) = cls.__get_text_l_jitter(l_instmod_obj=l_instmod_obj, l_params=l_params_new,
                                                       l_params_noisemod=l_params_noisemod,
                                                       l_idx_param_noisemod=l_idx_param_noisemod)
        func = cls.gpsim_func_text.format(func_name=cls.gpsim_function_name, kernel=ker)
        ldict["defaultdict"] = defaultdict
        ldict["list"] = list
        ldict["concatenate"] = concatenate
        ldict["logger"] = logger
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["GP"] = GP
        ldict["sqrt"] = sqrt
        exec(func, ldict)
        return ldict[cls.gpsim_function_name], [l_params_new[idx] for idx in l_idx_param_noisemod]

    # @classmethod
    # def star_param_GP_indexorval(cls, model_instance, l_params):
    #     """Return
    #
    #     :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
    #         noise model which requires parameter of the object studied (like GP and stellar
    #         activity)
    #     :param list_of_string l_params: Current list of parameters full names.
    #     :return list_of_string_or_float l:
    #     """
    #     i = 0
    #     l_params_new = l_params.copy()
    #     for param in cls.get_star_params_GP(model_instance):
    #         if param.free:
    #             if param not in l_params_new:
    #                 l_params_new.append(param.get_name(include_prefix=True, recursive=True))
    #             i += 1
    #         else:
    #             l.append(param.value)
    #     return l

    # @classmethod
    # def __define_GP(cls, p, model_instance):
    #     l_val = [p[idxorval] if free else idxorval
    #              for idxorval, free in zip(cls.star_param_GP_indexorval(model_instance),
    #                                        cls.star_params_GP_isfree(model_instance))]
    #     kernel = (exp(l_val[0])**2.0 * ExpSquaredKernel(l_val[1]**2) *
    #               ExpSine2Kernel(2. / (l_val[2])**2.0, l_val[3]))
    #     return GP(kernel)  # Define the kernel of the GP

    # def lnlike_creator(self):
    #     ldict = locals().copy()
    #     nb_free = self.nb_params_GP_free
    #     ker = self.__get_text_define_GP()
    #     if self.multidataset:
    #         l_idx_param = []
    #         for dataset in self.l_dataset:
    #             l_idx_param.append(self.get_param_idxs_datasim(dataset))
    #         ldict["l_idx_param"] = l_idx_param
    #         ldict["l_func"] = [self.get_datasim_function(dataset) for dataset in self.l_dataset]
    #         ldict["concatenate"] = concatenate
    #         ldict["logger"] = logger
    #         text_func = self.lnlikefunc_text_multidataset
    #     else:
    #         datasim_func = self.get_datasim_function()
    #         ldict["datasim_func"] = datasim_func
    #         text_func = self.lnlikefunc_text
    #     func = text_func.format(func_name=self.function_name, nb_GP_free_param=nb_free, kernel=ker)
    #     ldict["ExpSquaredKernel"] = ExpSquaredKernel
    #     ldict["ExpSine2Kernel"] = ExpSine2Kernel
    #     ldict["exp"] = exp
    #     ldict["GP"] = GP
    #     exec(func, ldict)
    #     return DocFunction(function=ldict[self.function_name], arg_list=self.get_arg_list())

    # def lnlike(self, p, data, data_err, t):
    #     if self.multidataset:
    #         model = []
    #         for dataset_key, t_dataset in zip(self.l_dataset, t):
    #             model.append(self.get_datasim_function(dataset_key)
    #                          (p[self.get_param_idxs_datasim(dataset_key)], t_dataset))
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(concatenate(t), concatenate(data_err))
    #         return gp.lnlikelihood(concatenate(data) - concatenate(model))
    #     else:
    #         model = self.get_datasim_function()(p[self.get_param_idxs_datasim()], t)
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
    #         return gp.lnlikelihood(data - model)

    # def _get_arg_list_one_dataset(self, dataset_key=None):
    #     arg_list_new = super(StellarActNoiseModel,
    #                          self)._get_arg_list_one_dataset(dataset_key)
    #     arg_list_new["param"] = (self.get_star_param_GP_names(free=True, full_name=True) +
    #                              arg_list_new["param"])
    #     return arg_list_new

    # def gp_simulator(self, p, tsim, data, data_err, t):
    #     """
    #     """
    #     if self.multidataset:
    #         model = []
    #         for dataset_key, t_dataset in zip(self.l_dataset, t):
    #             model.append(self.get_datasim_function(dataset_key)
    #                          (p[self.get_param_idxs_datasim(dataset_key)], t_dataset))
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(concatenate(t), concatenate(data_err))
    #         return gp.sample_conditional(concatenate(data) - concatenate(model), tsim)
    #     else:
    #         model = self.get_datasim_function()(p[self.get_param_idxs_datasim()], t)
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
    #         return gp.sample_conditional(data - model, tsim)

    # def get_param_idxs_datasim(self, dataset_key=None):
    #     """Return the list of param indexes for a datasimulator.
    #
    #     If multidataset dataset_key should not be None, because then you should do it for each
    #     dataset.
    #     """
    #     # Get list of param names for the likelihood then for the datasimulator and final get the
    #     # list of indexes for the datasimulator params
    #     l_param_all = self.get_arg_list()["param"]
    #     l_idx_param = []
    #     for par in self.get_datasim_arg_list(dataset_key)["param"]:
    #         l_idx_param.append(l_param_all.index(par))
    #     return l_idx_param

    # def get_param_idxs_GP(self):
    #     """Return the list of param indexes for the GP model."""
    #     # Get list of param names for the likelihood then for the datasimulator and final get the
    #     # list of indexes for the datasimulator params
    #     l_param_all = self.get_arg_list()["param"]
    #     l_idx_param = []
    #     for par in self.get_star_param_GP_names(free=True, full_name=True):
    #         l_idx_param.append(l_param_all.index(par))
    #     return l_idx_param
