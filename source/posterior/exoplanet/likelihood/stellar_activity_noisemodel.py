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

    kernel_text = ("exp({amp_RV})**2.0 * ExpSquaredKernel({evol_timescal}**2) * "
                   "ExpSine2Kernel(2. / ({periodic_timescal})**2.0, {period})")
    lnlikefunc_text = """def {func_name}(p, data, data_err, t):
        model = datasim_func(p[{nb_GP_free_param}:], t)
        gp = GP({kernel})
        gp.compute(t, data_err)
        return gp.lnlikelihood(data - model)
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

    def lnlike_creator(self):
        datasim_func = self.datasim_function
        nb_free = self.nb_params_GP_free
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
        func = self.lnlikefunc_text.format(func_name=self.function_name,
                                           nb_GP_free_param=nb_free, kernel=ker)
        ldict = locals().copy()
        ldict["datasim_func"] = datasim_func
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["exp"] = exp
        ldict["GP"] = GP
        exec(func, ldict)
        return DocFunction(function=ldict[self.function_name], arg_list=self.arg_list)

    def lnlike(self, p, data, data_err, t):
        model = self.datasim_function(p[self.nb_params_GP_free:], t)
        l_val = [p[idxorval] if free else idxorval
                 for idxorval, free in zip(self.star_param_GP_indexorval,
                                           self.star_params_GP_isfree)]
        kernel = (exp(l_val[0])**2.0 * ExpSquaredKernel(l_val[1]**2) *
                  ExpSine2Kernel(2. / (l_val[2])**2.0, l_val[3]))
        gp = GP(kernel)  # Define the kernel of the GP
        gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
        return gp.lnlikelihood(data - model)

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
        arg_list["kwargs"] = ["data", "data_err", "t"]
        return arg_list

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For more information see check_parametrisation_stellar_activity."""
        check_parametrisation_stellar_activity(model_instance=model_instance,
                                               instmod_fullname=instmod_fullname)
