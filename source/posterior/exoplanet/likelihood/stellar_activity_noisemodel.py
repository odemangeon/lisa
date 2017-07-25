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
from math import exp
from numpy import concatenate
# from collections import OrderedDict

from ..model.celestial_bodies import Star
from ..model.stellar_activity import amp_RV, evol_timescal, periodic_timescal, period
from ..model.stellar_activity import apply_parametrisation_stellar_activity
from ...core.likelihood.core_noise_model import Core_Noise_Model
from ....tools.function_w_doc import DocFunction


## logger object
logger = getLogger()

stelact_GP_noisemodel = "stellar_activity"


class StellarActNoiseModel(Core_Noise_Model):
    """docstring for StellarActNoiseModel."""

    __category__ = stelact_GP_noisemodel
    __has_GP__ = True
    __has_jitter__ = False
    __kwargs_needed__ = ["data", "data_err", "t"]

    kernel_text = ("exp({amp_RV})**2.0 * ExpSquaredKernel({evol_timescal}**2) * "
                   "ExpSine2Kernel(2. / ({periodic_timescal})**2.0, {period})")
    lnlikefunc_text = """def {func_name}(p, data, data_err, t, **kwargs_data):
        model = datasim_func(p[{nb_GP_free_param}:], **kwargs_data)
        gp = GP({kernel})
        gp.compute(t, data_err, sort=True)
        return gp.lnlikelihood(data - model)
        """

    # logger.debug("model: {{}}".format(model))
    # logger.debug("data: {{}}".format(data))
    # logger.debug("data_err: {{}}".format(data_err))
    # logger.debug("t: {{}}".format(t))
    # logger.debug("l_idx_param: {{}}".format(l_idx_param))

    lnlikefunc_text_multidataset = """def {func_name}(p, data, data_err, t, **kwargs_data):
        kwargs_dataset = []
        for i in range(ndataset):
            kwargs = dict()
            for kwargs_type in kwargs_data:
                kwargs[kwargs_type] = kwargs_data[kwargs_type][i]
            kwargs_dataset.append(kwargs)
        model = [datasim_func(p[indexes_dataset], **kwargs)
                 for datasim_func, indexes_dataset, kwargs in zip(l_func, l_idx_param,
                                                                  kwargs_dataset)]
        gp = GP({kernel})
        gp.compute(concatenate(t), concatenate(data_err), sort=True)
        return gp.lnlikelihood(concatenate(data) - concatenate(model))
        """

    # lnlikefunc_text_multidataset = """def {func_name}(p, data, data_err, t):
    #     model = [datasim_func(p[indexes_dataset], t_dataset)
    #              for datasim_func, indexes_dataset, t_dataset in zip(l_func, l_idx_param, t)]
    #     gp = GP({kernel})
    #     gp.compute(concatenate(t), concatenate(data_err), sort=True)
    #     return gp.lnlikelihood(concatenate(data) - concatenate(model))
    #     """
    function_name = "lnlike"

    __star_param_GP_names = [amp_RV, evol_timescal, periodic_timescal, period]

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        star = model_instance.stars[list(model_instance.stars.keys())[0]]
        if isinstance(star, Star):
            self.__star = star  # This needs to be done before the init for check_parametrisation
        else:
            raise ValueError("star should be a Star instance. Got {}".format(type(star)))
        super(StellarActNoiseModel, self).__init__(datasim_docfunc=datasim_docfunc,
                                                   model_instance=model_instance,
                                                   instmodel_obj=instmodel_obj)

    @property
    def star(self):
        """Return the star object used for this stellar activity noise modelling."""
        return self.__star

    def lnlike_creator(self):
        ldict = locals().copy()
        nb_free = self.nb_params_GP_free
        ker = self.__get_text_define_GP()
        if self.multidataset:
            l_idx_param = []
            ndataset = len(self.l_dataset)
            for dataset in self.l_dataset:
                l_idx_param.append(self.get_param_idxs_datasim(dataset))
            ldict["ndataset"] = ndataset
            ldict["l_idx_param"] = l_idx_param
            ldict["l_func"] = [self.get_datasim_function(dataset) for dataset in self.l_dataset]
            ldict["concatenate"] = concatenate
            ldict["logger"] = logger
            text_func = self.lnlikefunc_text_multidataset
        else:
            datasim_func = self.get_datasim_function()
            ldict["datasim_func"] = datasim_func
            text_func = self.lnlikefunc_text
        func = text_func.format(func_name=self.function_name, nb_GP_free_param=nb_free, kernel=ker)
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["exp"] = exp
        ldict["GP"] = GP
        exec(func, ldict)
        return DocFunction(function=ldict[self.function_name], arg_list=self.get_arg_list())

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
    #     func = text_func.format(func_name=self.function_name, nb_GP_free_param=nb_free,
    #                             kernel=ker)
    #     ldict["ExpSquaredKernel"] = ExpSquaredKernel
    #     ldict["ExpSine2Kernel"] = ExpSine2Kernel
    #     ldict["exp"] = exp
    #     ldict["GP"] = GP
    #     exec(func, ldict)
    #     return DocFunction(function=ldict[self.function_name], arg_list=self.get_arg_list())

    def lnlike(self, p, data, data_err, t, **kwarg_data):
        if self.multidataset:
            model = []
            for i, dataset in enumerate(self.l_dataset):
                kwargs_dataset = {}
                for kwargs_type in kwarg_data:
                    kwargs_dataset[kwargs_type] = kwarg_data[kwargs_type][i]
                model.append(self.get_datasim_function(dataset)
                             (p[self.get_param_idxs_datasim(dataset)], **kwargs_dataset))
            gp = self.__define_GP(p[self.get_param_idxs_GP()])
            gp.compute(concatenate(t), concatenate(data_err))
            return gp.lnlikelihood(concatenate(data) - concatenate(model))
        else:
            model = self.get_datasim_function()(p[self.get_param_idxs_datasim()], **kwarg_data)
            gp = self.__define_GP(p[self.get_param_idxs_GP()])
            gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
            return gp.lnlikelihood(data - model)

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

    def __define_GP(self, p):
        l_val = [p[idxorval] if free else idxorval
                 for idxorval, free in zip(self.star_param_GP_indexorval,
                                           self.star_params_GP_isfree)]
        kernel = (exp(l_val[0])**2.0 * ExpSquaredKernel(l_val[1]**2) *
                  ExpSine2Kernel(2. / (l_val[2])**2.0, l_val[3]))
        return GP(kernel)  # Define the kernel of the GP

    def __get_text_define_GP(self):
        dico = {}
        for param_name, free, idxorval in zip(self.__star_param_GP_names,
                                              self.star_params_GP_isfree,
                                              self.star_param_GP_indexorval):
            if free:
                dico[param_name] = "p[{}]".format(idxorval)
            else:
                dico[param_name] = "{}".format(idxorval)
        ker = self.kernel_text.format(amp_RV=dico[amp_RV], evol_timescal=dico[evol_timescal],
                                      periodic_timescal=dico[periodic_timescal],
                                      period=dico[period])
        return ker

    def get_star_param_GP_names(self, free=False, full_name=False):
        """Return the list of the names of the paramaters of the GP model."""
        if full_name:
            return [param.full_name for param in self.get_star_params_GP(free=free)]
        else:
            return [param.name for param in self.get_star_params_GP(free=free)]

    def get_star_params_GP(self, free=False):
        """Return the list of GP parameters.

        If free is True returns only the free parameters.
        """
        if free:
            return [getattr(self.star, par) for par in self.__star_param_GP_names
                    if getattr(self.star, par).free]
        else:
            return [getattr(self.star, par) for par in self.__star_param_GP_names]

    @property
    def star_params_GP_isfree(self):
        """Return the list of boolean indicating if the GP parameters are free."""
        return [param.free for param in self.get_star_params_GP()]

    @property
    def nb_params_GP_free(self):
        """Return the number of GP parameters that are free."""
        return len(self.get_star_params_GP(free=True))

    @property
    def star_param_GP_indexorval(self):
        l = []
        i = 0
        for param in self.get_star_params_GP():
            if param.free:
                l.append(i)
                i += 1
            else:
                l.append(param.value)
        return l

    def _get_arg_list_one_dataset(self, dataset_key=None):
        arg_list_new = super(StellarActNoiseModel,
                             self)._get_arg_list_one_dataset(dataset_key)
        arg_list_new["param"] = (self.get_star_param_GP_names(free=True, full_name=True) +
                                 arg_list_new["param"])
        return arg_list_new

    def gp_simulator(self, p, tsim, data, data_err, t, **kwarg_data):
        if self.multidataset:
            model = []
            for ii, dataset_key in enumerate(self.l_dataset):
                kwargs_dataset = {}
                for kwargs_type in kwarg_data:
                    kwargs_dataset[kwargs_type] = kwarg_data[kwargs_type][ii]
                model.append(self.get_datasim_function(dataset_key)
                             (p[self.get_param_idxs_datasim(dataset_key)], **kwargs_dataset))
            gp = self.__define_GP(p[self.get_param_idxs_GP()])
            gp.compute(concatenate(t), concatenate(data_err))
            return gp.sample_conditional(concatenate(data) - concatenate(model), tsim)
        else:
            model = self.get_datasim_function()(p[self.get_param_idxs_datasim()],
                                                **kwarg_data)
            gp = self.__define_GP(p[self.get_param_idxs_GP()])
            gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
            return gp.sample_conditional(data - model, tsim)

    def get_param_idxs_datasim(self, dataset_key=None):
        """Return the list of param indexes for a datasimulator.

        If multidataset dataset_key should not be None, because then you should do it for each
        dataset.
        """
        # Get list of param names for the likelihood then for the datasimulator and final get the
        # list of indexes for the datasimulator params
        l_param_all = self.get_arg_list()["param"]
        l_idx_param = []
        for par in self.get_datasim_arg_list(dataset_key)["param"]:
            l_idx_param.append(l_param_all.index(par))
        return l_idx_param

    def get_param_idxs_GP(self):
        """Return the list of param indexes for the GP model."""
        # Get list of param names for the likelihood then for the datasimulator and final get the
        # list of indexes for the datasimulator params
        l_param_all = self.get_arg_list()["param"]
        l_idx_param = []
        for par in self.get_star_param_GP_names(free=True, full_name=True):
            l_idx_param.append(l_param_all.index(par))
        return l_idx_param

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """For more information see apply_parametrisation_stellar_activity."""
        apply_parametrisation_stellar_activity(model_instance=model_instance,
                                               instmod_fullname=instmod_fullname)

    def _check_parametrisation_dataset(self, model_instance, dataset_key=None):
        instmod_obj = self.get_instmodel_obj(dataset_key)
        err_msg = ("The noise model of instrument model {} being {}, it must have a {} "
                   "{} parameter !")
        for param in self.get_star_params_GP():
            print(self.star.parameters)
            if param.name not in self.star.parameters:
                raise ValueError(err_msg.format(instmod_obj.full_name, self.category,
                                                param.full_name, ""))
            if not(param.main):
                raise ValueError(err_msg.format(instmod_obj.full_name, self.category,
                                                param.full_name, "main"))
