"""
Prior functions module.

This module is an update of Suzanne Aigrain's prior module. See copyright below:

    Copyright (C) 2016  Suzanne Aigrain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additions to this modules:
    - add Jeffreys prior, Susana Barros, 28 Sep 2016
    - add Sine prior, Susana Barros, 28 Sep 2016
    - add Metaclass Metaclass_PriorFunction, Olivier Demangeon, 6 Feb. 2017
    - add properties and check_mandatoryargs, Olivier Demangeon, 6 Feb. 2017
    - minor updates to deal with lims=None, Olivier Demangeon, 6 Feb. 2017
    - add create_logpdf for speed improvement, Olivier Demangeon, 6 Feb. 2017

@TODO:
"""
from __future__ import division
from logging import getLogger

from textwrap import dedent
import math as mt

import numpy as np
from numpy import pi, inf
from scipy.stats import reciprocal

from .core_prior import Core_Prior_Function, Core_JointPrior_Function
from ....tools.function_from_text_toolbox import init_arglist_paramnb_arguments_ldict, add_param_argument, par_vec_name, key_param, get_function_arglist
from ....tools.function_w_doc import DocFunction
# from .core.prior.manager_prior import Manager_Prior


## logger object
logger = getLogger()
## manager object
# manager = Manager_Prior()
# manager.load_setup() ## Cannot be done otherwise there is an import loop


class UniformPrior(Core_Prior_Function):

    __category__ = "uniform"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        self.vmin = vmin
        self.vmax = vmax
        self.C = 1. / (vmax - vmin)
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]

    def create_logpdf(self):
        lnC = mt.log(1. / (self.vmax - self.vmin))
        vmin = self.vmin
        vmax = self.vmax

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return lnC
            else:
                return -inf
        return logpdf

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.lnC,
                            -inf)
        else:
            if x >= self.vmin and x <= self.vmax:
                return self.lnC
            else:
                return -inf

    def ravs(self, nb_values=1):
        val = np.random.uniform(self.vmin, self.vmax, size=nb_values)
        if val.size == 1:
            return val[0]
        else:
            return val


class NormalPrior(Core_Prior_Function):

    __category__ = "normal"
    __mandatory_args__ = ["mu", "sigma"]
    __extra_args__ = ["lims", "sigma_lims"]

    def __init__(self, mu, sigma, lims=None, sigma_lims=None):
        self.mu = float(mu)
        self.sigma = float(sigma)
        self._f1 = 1. / mt.sqrt(2. * pi * sigma * sigma)
        self._lf1 = mt.log(self._f1)
        self._f2 = 1. / (2. * sigma * sigma)
        if (lims is not None) and (sigma_lims is not None):
            raise ValueError("You cannot set both lims and sigma_lims")
        elif lims is not None:
            self.lims = np.array(lims)
        elif sigma_lims is not None:
            self.lims = [self.mu - sigma_lims[0] * self.sigma, self.mu + sigma_lims[1] * self.sigma]
        else:
            self.lims = np.array([-inf, inf])
        self.vmin, self.vmax = self.lims
        if self.vmin >= self.vmax:
            raise ValueError("lims should be a 2 element iterable where the first element is "
                             "strictly inferior to the second")

    def create_logpdf(self):
        lf1 = mt.log(1. / mt.sqrt(2. * pi * self.sigma * self.sigma))
        f2 = 1. / (2. * self.sigma * self.sigma)
        vmin = self.vmin
        vmax = self.vmax
        mu = self.mu

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return lf1 - (x - mu) * (x - mu) * f2
            else:
                return -inf
        return logpdf

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self._lf1 - (x - self.mu)**2 * self._f2,
                            -inf)
        else:
            return self._lf1 - (x - self.mu)**2 * self._f2 if self.vmin < x < self.vmax else -inf

    def ravs(self, nb_values=1):
        val = np.random.normal(self.mu, self.sigma, size=nb_values)
        for idx in np.where((val < self.vmin) | (val > self.vmax))[0]:
            while not((self.vmin < val[idx]) and (self.vmax > val[idx])):
                val[idx] = np.random.normal(self.mu, self.sigma)
        if val.size == 1:
            return val[0]
        else:
            return val


class LogNormPrior(Core_Prior_Function):

    __category__ = "lognormal"
    __mandatory_args__ = ["mu", "sigma"]
    __extra_args__ = ["lims"]

    def __init__(self, mu, sigma, lims=None):
        self.lims = np.array(lims) if lims is not None else np.array([0, inf])
        self.vmin, self.vmax = self.lims
        if self.vmin >= self.vmax:
            raise ValueError("lims should be a 2 element iterable where the first element is "
                             "strictly inferior to the second")
        self.mu = mu
        self.sigma = sigma
        self.C = -mt.log(sigma * mt.sqrt(2 * pi))
        self._B = 2 * sigma**2

    def create_logpdf(self):
        C = -mt.log(self.sigma * mt.sqrt(2 * pi))
        mu = self.mu
        B = 2 * self.sigma**2
        vmin = self.vmin
        vmax = self.vmax

        def logpdf(x):
            if x >= vmin and x <= vmax:
                lnx = mt.log(x)
                return -lnx + C - ((lnx * lnx - mu * lnx + mu * mu) / B)
            else:
                return -inf
        return logpdf

    def __logpdf_wcustargs(self, x, mu, C, B):
        lnx = mt.log(x)
        return -lnx + C - ((lnx * lnx - mu * lnx + mu * mu) / B)

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(self, x, self.mu, self.C, self.B),
                            -inf)
        else:
            if (x <= self.vmin) or (x > self.vmax):
                return -inf
            return self.__logpdf_wcustargs(self, x, self.mu, self.C, self.B)

    def ravs(self, nb_values=1):
        val = np.random.lognormal(self.mu, self.sigma, size=nb_values)
        for idx in np.where((val < self.vmin) | (val > self.vmax))[0]:
            while not((self.vmin < val[idx]) and (self.vmax > val[idx])):
                val[idx] = np.random.lognormal(self.mu, self.sigma)
        if val.size == 1:
            return val[0]
        else:
            return val


class JeffreysPrior(Core_Prior_Function):

    __category__ = "jeffreys"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        self.vmin = vmin
        self.vmax = vmax
        self.C = vmax / vmin
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]

    def create_logpdf(self):
        vmin = self.vmin
        vmax = self.vmax
        lnC = self.lnC

        def logpdf(x):
            if x >= vmin and x <= vmax:
                return -mt.log(x * lnC)
            else:
                return -inf
        return logpdf

    def __logpdf_wcustargs(self, x, lnC):
        -mt.log(x * lnC)

    def logpdf(self, x):
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(x, self.lnC),
                            -inf)
        if x >= self.vmin and x <= self.vmax:
            return self.__logpdf_wcustargs(x, self.lnC)
        else:
            return -inf

    def ravs(self, nb_values=1):
        x1 = reciprocal(self.vmin, self.vmax)
        val = x1.rvs(size=nb_values)
        if val.size == 1:
            return val[0]
        else:
            return val


class SinePrior(Core_Prior_Function):

    __category__ = "sine"
    __mandatory_args__ = ["vmin", "vmax"]
    __extra_args__ = []

    def __init__(self, vmin, vmax, rad=True):
        if vmin >= vmax:
            raise ValueError("vmin should be strictly inferior to vmax")
        self.rad = rad
        self.degtorad = pi / 180.0
        if rad:
            if vmin < 0. or vmin > 180.:
                raise ValueError("vmin should between 0. and 180")
            if vmax < 0. or vmax > 180.:
                raise ValueError("vmin should between 0. and 180")
            self.C = 1. / (np.cos(vmin) - np.cos(vmax))
        else:
            if vmin < 0. or vmin > pi:
                raise ValueError("vmin should between 0. and pi")
            if vmax < 0. or vmax > pi:
                raise ValueError("vmin should between 0. and pi")
            self.C = 1. / ((np.cos(vmin * self.degtorad) - np.cos(vmax * self.degtorad)) / self.degtorad)
        self.vmin = vmin
        self.vmax = vmax
        self.lnC = mt.log(self.C)
        self.lims = [vmin, vmax]

    def create_logpdf(self):
        vmin = self.vmin
        vmax = self.vmax
        lnC = self.lnC
        degtorad = self.degtorad

        if self.rad:
            def logpdf(x):
                if x >= vmin and x <= vmax:
                    return mt.log(np.sin(x)) + lnC
                else:
                    return -inf
            return logpdf
        else:
            def logpdf(x):
                if x >= vmin and x <= vmax:
                    return mt.log(np.sin(x * degtorad)) + lnC
                else:
                    return -inf
            return logpdf

    def __logpdf_wcustargs(self, x, lnC, angleconv):
        return mt.log(np.sin(x * angleconv)) + lnC

    def logpdf(self, x):
        if self.rad:
            conv = 1
        else:
            conv = self.degtorad
        if isinstance(x, np.ndarray):
            return np.where((self.vmin < x) & (x < self.vmax),
                            self.__logpdf_wcustargs(x, self.lnC, conv),
                            -inf)
        if x >= self.vmin and x <= self.vmax:
            return self.__logpdf_wcustargs(x, self.lnC, conv)
        else:
            return -inf

    # a random angle x has a probability density function = sin(x)
    def ravs(self, nb_values=1):
        val = np.random.uniform(self.vmin, self.vmax, size=nb_values)
        if val.size == 1:
            return val[0]
        else:
            return val


class PolarPrior(Core_JointPrior_Function):
    """docstring for PolarPrior."""

    __category__ = "polar"
    __mandatory_args__ = []
    __extra_args__ = ['r_prior', 'theta_prior']
    __params__ = ['x', 'y']

    def set_dico_priors_arg(self, r_prior=None, theta_prior=None):
        if r_prior is None:
            r_prior = {"category": "uniform", "args": {"vmin": 0.0, "vmax": 1.}}
        self.dico_priors_arg["r"] = r_prior
        if theta_prior is None:
            theta_prior = {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
        self.dico_priors_arg["theta"] = theta_prior

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.params list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.params
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.dico_priorfunction.items()}
        ldict["dico_logpdf"] = dico_logpdf
        ldict["atan2"] = mt.atan2
        ldict["sqrt"] = mt.sqrt
        dico_text_params = {}
        for param_key in self.params:
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, param_vector_name=par_vec_name)
        function_name = "logpdf_{}".format(self.category)
        text_function = """
        def {function_name}({param_vector_name}):
            r = sqrt({x} * {x} + {y} * {y})
            theta = atan2({y}, {x})
            return dico_logpdf["r"](r) + dico_logpdf["theta"](theta)
        """
        text_function = dedent(text_function)
        text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                             x=dico_text_params["x"], y=dico_text_params["y"])
        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))
        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, x, y):
        dico_logpdf = self.dico_priorfunction

        r = mt.sqrt(x * x + y * y)
        theta = mt.atan2(y, x)
        return dico_logpdf["x"](x) + dico_logpdf["y"](y)

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.params.
        """
        dico_ravs = {}
        for param, dico in self.dico_priors_arg.items():
            value = dico.get("value", None)
            if value is None:
                dico_ravs[param] = dico["priorfunc_instance"].ravs(nb_values=nb_values)
            else:
                dico_ravs[param] = np.ones(nb_values) * value
            if dico_ravs[param].size == 1:
                dico_ravs[param] = dico_ravs[param][0]
        x = dico_ravs["r"] * np.cos(dico_ravs["r"])
        y = dico_ravs["r"] * np.sin(dico_ravs["r"])
        return x, y

    # def __init__(self, r_prior=None, theta_prior=None):
    #     # Set the dico_priors_arg which contains the prior args for the underlying hidden parameters
    #     self.dico_priors_arg = {}
    #     if r_prior is None:
    #         r_prior = {"category": "uniform", "args": {"vmin": 0.0, "vmax": 1.}}
    #     self.dico_priors_arg["r"] = r_prior
    #     if theta_prior is None:
    #         theta_prior = {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
    #     self.dico_priors_arg["theta"] = theta_prior
    #     # Check the prior category and arguments and create the prior function instances
    #     for param, prior_args in self.dico_priors_arg.items():
    #         if manager.is_available_priortype(prior_args["category"]):
    #             priorfunction_subclass = manager.get_priorfunc_subclass(prior_args["category"])
    #             priorfunction_subclass.check_args(list(prior_args["args"].keys()))
    #         else:
    #             raise ValueError("prior_category {} is not in the list of available prior types: {}"
    #                              "".format(prior_args["category"], manager.get_available_priors()))
    #         self.dico_priors_arg[param]["priorfunc_instance"] = priorfunction_subclass(**prior_args["args"])
