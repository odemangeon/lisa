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
from collections import OrderedDict

from ..model.celestial_bodies import Star
from ..model.stellar_activity import amp_RV, evol_timescal, periodic_timescal, period
from ..model.stellar_activity import check_parametrisation_stellar_activity
from ...core.likelihood.core_noise_model import Core_Noise_Model
from ....tools.function_w_doc import DocFunction


## logger object
logger = getLogger()

stelact_GP_noisemodel = "stellar_activity"


class StellarActNoiseModel(Core_Noise_Model):
    """docstring for StellarActNoiseModel."""

    __category__ = stelact_GP_noisemodel
    __allow_multidataset__ = True

    kernel_text = ("exp({amp_RV})**2.0 * ExpSquaredKernel({evol_timescal}**2) * "
                   "ExpSine2Kernel(2. / ({periodic_timescal})**2.0, {period})")
    lnlikefunc_text = """def {func_name}(p, data, data_err, t):
        model = datasim_func(p[{nb_GP_free_param}:], t)
        gp = GP({kernel})
        gp.compute(t, data_err, sort=True)
        return gp.lnlikelihood(data - model)
        """
    lnlikefunc_text_multidataset = """def {func_name}(p, data, data_err, t):
        model = [datasim_func(p[indexes_dataset], t_dataset)
                 for datasim_func, indexes_dataset, t_dataset in zip(l_func, l_idx_param, t)]
        gp = GP({kernel})
        gp.compute(concatenate(t), concatenate(data_err), sort=True)
        return gp.lnlikelihood(concatenate(data) - concatenate(model))
        """
    function_name = "lnlike"

    __star_param_GP_names = [amp_RV, evol_timescal, periodic_timescal, period]

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        super(StellarActNoiseModel, self).__init__(datasim_docfunc=datasim_docfunc,
                                                   model_instance=model_instance,
                                                   instmodel_obj=instmodel_obj)
        star = model_instance.stars[list(model_instance.stars.keys())[0]]
        if isinstance(star, Star):
            self.__star = star
        else:
            raise ValueError("star should be a Star instance. Got {}".format(type(star)))
        if self.multidataset:
            self.__odict_param_idxs = self.__get_odico_indexes()

    def lnlike_creator(self):
        ldict = locals().copy()
        nb_free = self.nb_params_GP_free
        ker = self.__get_text_define_GP()
        if self.multidataset:
            l_idx_param = [idx_params for idx_params in self.param_idxs.values()]
            ldict["l_idx_param"] = l_idx_param
            ldict["l_func"] = [datasim.function for datasim in self.datasim_docfunc.values()]
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
        return DocFunction(function=ldict[self.function_name], arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, t):
        if self.multidataset:
            arg_list = self.arg_list
            model = []
            for dataset_key, t_dataset in zip(arg_list["kwargs"]["data"], t):
                model.append(self.get_datasim_function(dataset_key)(p[self.param_idxs[dataset_key]],
                                                                    t_dataset))
            gp = self.__define_GP(p)
            gp.compute(concatenate(t), concatenate(data_err))
            return gp.lnlikelihood(concatenate(data) - concatenate(model))
        else:
            model = self.get_datasim_function()(p[self.nb_params_GP_free:], t)
            gp = self.__define_GP(p)
            gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
            return gp.lnlikelihood(data - model)

    def __get_odico_indexes(self):
        res = OrderedDict()
        for dataset_key in self.datasim_docfunc:
            idx_par = []
            for par in self.datasim_docfunc[dataset_key].arg_list["param"]:
                idx_par.append(self.arg_list["param"].index(par))
            res[dataset_key].append(idx_par)
        return res

    @property
    def param_idxs(self):
        """Return the OrderedDict of param indexes"""
        return self.__odict_param_idxs

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

    @property
    def star(self):
        """Return the star object used for this stellar activity noise modelling."""
        return self.__star

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

    @property
    def arg_list(self):
        arg_list = super(StellarActNoiseModel, self).arg_list
        arg_list["param"] = (self.get_star_param_GP_names(free=True, full_name=True) +
                             arg_list["param"])
        return arg_list

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For more information see check_parametrisation_stellar_activity."""
        check_parametrisation_stellar_activity(model_instance=model_instance,
                                               instmod_fullname=instmod_fullname)
