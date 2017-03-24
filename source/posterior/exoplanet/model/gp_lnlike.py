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


## logger object
logger = getLogger()

def finalize_and_create_lnlike_gp(datasimulator, text_func, gp_type):
    arg_list = datasimulator.arg_list.copy()
    if gp_type is "ExpSquared+ExpSine":
        kernel_text = ("exp(p[0])**2.0 * ExpSquaredKernel(p[1]**2) * "
                       "ExpSine2Kernel(2. / (p[2])**2.0, p[3])")
        model_param_text = "p[4:]"
    text_func.format(function_name, model_param_text, kernel_text)
        # define the kernel

        # Pre-compute the factorization of the matrix.
        # Compute the log likelihood
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
