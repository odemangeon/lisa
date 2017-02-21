#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood module.

The objective of this module is to define the likelihood function.

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

ln_categories = ["wo jitter", "jitter dfm", "jitter multiplicative", "jitter multiplicative baluev",
                 "jitter additive", "jitter additive baluev"]


def create_lnlikelihood(datasimulator, category="wo jitter", jitter_param=None):
                        # **kwarg_data):
    """Return the log likelihood function."""

    datasim_func = datasimulator.function
    function_name = "lnlikelihood"
    text_w_jitter_dfm = """def {}(p, data, data_err, **kwarg_data):
        model = datasim_func({}, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * {}))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))"""

    text_w_jitter_additive = """def {}(p, data, data_err, **kwarg_data):
        model = datasim_func({}, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))"""

    text_w_jitter_additive_baluev = """def {}(p, data, data_err, **kwarg_data):
        model = datasim_func({}, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
        Bualev_coeff = 1.0 / (1 - (len(p) - 1)/len(data))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(inv_sigma2)))"""

    text_w_jitter_multiplicative = """def {}(p, data, data_err, **kwarg_data):
        model = datasim_func({}, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))"""

    text_w_jitter_multiplicative_baluev = """def {}(p, data, data_err, **kwarg_data):
        model = datasim_func({}, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
        Bualev_coeff = 1.0 / (1 - len(p)/len(data))
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff - nplog(inv_sigma2)))"""

    # def lnlikelihood_test():
    #     print("lnlikelihood_test")
    #     print(locals().keys())
    #     print(globals().keys())
    #     print("datasim_func in locals : {}".format("datasim_func" in locals()))
    #     print("datasim_func in globals : {}".format("datasim_func" in globals()))
    #     print(datasim_func)

    def lnlikelihood_wo_jitter(p, data, data_err, **kwarg_data):
        # print("lnlikelihood_wo_jitter")
        # print("datasim_func in locals : {}".format("datasim_func" in locals()))
        # print("datasim_func in globals : {}".format("datasim_func" in globals()))
        model = datasim_func(p, **kwarg_data)
        inv_sigma2 = 1.0 / (data_err**2)
        return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))

    def finalize_and_create_lnlike(datasimulator, text_func, jitter_param):
        arg_list = datasimulator.arg_list.copy()
        if jitter_param.free:
            text = text_func.format(function_name, "p[1:]", "p[0]")
            arg_list["param"] = [jitter_param.full_name] + arg_list["param"]
        else:
            text = text_func.format(function_name, "p", jitter_param.value)
        arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
        logger.debug("Log likelihood function text: {}".format(text))
        logger.debug("Log likelihood arg_list: {}".format(arg_list))
        ldict = locals().copy()
        ldict["datasim_func"] = datasim_func
        ldict["exp"] = exp
        ldict["nplog"] = nplog
        ldict["npsum"] = npsum
        # print("finalize_and_create_lnlike")
        # print(locals().keys())
        # print(globals().keys())
        # print("datasim_func in locals : {}".format("datasim_func" in locals()))
        # print("datasim_func in globals : {}".format("datasim_func" in globals()))
        # exec(text, globals(), locals())
        # exec(text)
        exec(text, ldict)
        # print(locals().keys())
        # print(globals().keys())
        # print(ldict.keys())
        doc_f = DocFunction(function=ldict[function_name], arg_list=arg_list)
        return doc_f

    # lnlikelihood_test()

    if category == "wo jitter":
        arg_list = datasimulator.arg_list.copy()
        arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
        doc_f = DocFunction(function=lnlikelihood_wo_jitter, arg_list=arg_list)
        return doc_f
    elif category == "jitter dfm":
        return finalize_and_create_lnlike(datasimulator, text_w_jitter_dfm, jitter_param)
    elif category == "jitter multiplicative":
        return finalize_and_create_lnlike(datasimulator, text_w_jitter_multiplicative, jitter_param)
    elif category == "jitter multiplicative baluev":
        return finalize_and_create_lnlike(datasimulator, text_w_jitter_multiplicative_baluev, jitter_param)
    elif category == "jitter additive":
        return finalize_and_create_lnlike(datasimulator, text_w_jitter_additive, jitter_param)
    elif category == "jitter additive baluev":
        return finalize_and_create_lnlike(datasimulator, text_w_jitter_additive_baluev, jitter_param)
    else:
        raise ValueError("Category {} not recognized. Avalaible categories are {}"
                         "".format(ln_categories))
