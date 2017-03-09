#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_prior module.

The objective of this module is to define the Prior class which will generate the prior functions.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import OrderedDict

from .manager_prior import Manager_Prior
from ....tools.function_w_doc import DocFunction

## logger object
logger = getLogger()
## manager object
manager = Manager_Prior()


class Prior(object):
    """docstring for Prior."""
    def __init__(self):
        raise NotImplementedError("Prior is an interface class it should not be instanciated")

    def create_individual_lnpriors(self):
        """Return a dictionnary providing the individual prior probability density functions.

        This function does:
            1. Look for all the main free parameters in the model (self) and put them in two lists
                marginal and joint dependending on wether they have a marginal or joint prior.
            2. Create a dictionnary whith 2 keys: "marginal": {}, "joint": []
            3. For each parameter in the list of marginal (step 1): Create an entry in
               "marginal" (see step 2) which to the full name of the parameter associate the
                marginal prior function.
            4. For each parameter in the list of joint (step 1): ?
                a. look for the associated parameters defined by ? and check if they are free
                ??
                ?. append a element to "joint" (see step 2) which is a dict with two keys:
                   "Parameters": list of free parameters full name in the order required for the
                                 prior function see "prior"
                   "prior": joint prior functions which included the value of fixe parameters if
                   needed
        """
        # 1.
        marginal = OrderedDict()
        joint = OrderedDict()
        for param in self.get_list_params(main=True, free=True):
            if param.joint:
                joint[param.full_name] = param
            else:
                marginal[param.full_name] = param
        # 2.
        priors = {"marginal": {}, "joint": []}
        # 3.
        for full_name, param in marginal.items():
            prior_func = manager.get_priorfunc_subclass(param.prior_category)(**param.prior_args)
            priors["marginal"][full_name] = prior_func.create_logpdf()
        for full_name, param in joint.items():
            raise NotImplementedError("Joint prior as individual prior for parameters is not "
                                      "implemented yet.")
        return priors

    def create_joint_lnprior(self, list_paramnames, individual_priors=None):
        """Return a joint prior function for the list of parameter provided.

        The parameters have to be provided through their full names.
        This function does:
            1.

        TODO: Implement DocFunction
        """
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()
        # 1.
        list_lnpriors = []
        for param_name in list_paramnames:
            if param_name in individual_priors["marginal"]:
                list_lnpriors.append(individual_priors['marginal'][param_name])
            else:
                logger.error("You try to acces the prior funciton of an unknown parameter or a "
                             "joint parameter: {}".format(param_name))
                raise NotImplementedError("Joint prior as individual prior for parameters is not "
                                          "implemented yet.")

        def joint_lnprior(param_values):
            res = 0
            for i, ln_prior in enumerate(list_lnpriors):
                res += ln_prior(param_values[i])
            return res

        return joint_lnprior
