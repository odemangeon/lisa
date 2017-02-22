#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood module.

The objective of this module is to define the class LikelihoodCreator.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from numpy import sum as npsum
from numpy import log as nplog
from math import exp

from ...tools.function_w_doc import DocFunction


## logger object
logger = getLogger()


class LikelihoodCreator(object):
    """docstring for LikelihoodCreator."""

    _lnlikelihoods = {
        "wo jitter": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2)
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))""",
        "jitter dfm": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * {}))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter multiplicative": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter multiplicative baluev": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
            Bualev_coeff = 1.0 / (1 - len(p)/len(data))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                 nplog(inv_sigma2)))""",
        "jitter additive": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter additive baluev": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
            Bualev_coeff = 1.0 / (1 - (len(p) - 1)/len(data))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                 nplog(inv_sigma2)))"""}

    def _create_lnlikelihood(self, datasimulator, category="wo jitter", jitter_param=None):
                            # **kwarg_data):
        """Return the log likelihood function."""

        datasim_func = datasimulator.function
        function_name = "lnlikelihood"

        def finalize_and_create_lnlike(datasimulator, text_func, jitter_param=None):
            arg_list = datasimulator.arg_list.copy()
            if jitter_param is not None:
                if jitter_param.free:
                    text = text_func.format(function_name, "p[1:]", "p[0]")
                    arg_list["param"] = [jitter_param.full_name] + arg_list["param"]
                else:
                    text = text_func.format(function_name, "p", jitter_param.value)
            else:
                text = text_func.format(function_name)
            arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
            logger.debug("Log likelihood function text: {}".format(text))
            logger.debug("Log likelihood arg_list: {}".format(arg_list))
            ldict = locals().copy()
            ldict["datasim_func"] = datasim_func
            ldict["exp"] = exp
            ldict["nplog"] = nplog
            ldict["npsum"] = npsum
            exec(text, ldict)
            doc_f = DocFunction(function=ldict[function_name], arg_list=arg_list)
            return doc_f

        # lnlikelihood_test()

        if category in self._lnlikelihoods.keys():
            text_func = self._lnlikelihoods[category]
            if category == "wo jitter":
                jitter_cat_ok = jitter_param is None
                if not(jitter_cat_ok):
                    jitter_cat_ok = not(jitter_param.main)
                if jitter_cat_ok:
                    return finalize_and_create_lnlike(datasimulator, text_func)
                else:
                    raise ValueError("For likelihood '{}' the jitter parameter should not be a main"
                                     "parameter.".format(category))
            else:
                jitter_cat_ok = jitter_param.main
                if jitter_cat_ok:
                    return finalize_and_create_lnlike(datasimulator, text_func, jitter_param)
                else:
                    raise ValueError("For likelihood '{}' the jitter parameter should be a main"
                                     "parameter.".format(category))
        else:
            raise ValueError("Category {} not recognized. Avalaible categories are {}"
                             "".format(self._ln_categories))

    def create_lnlikelihoods(self):
        """Return the likelihood for each instrument model used."""
        pass
