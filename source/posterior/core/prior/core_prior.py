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
from ..database_func import DatabaseInstLvlDataset
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

    def __joint_lnprior_creator(self, list_lnpriors, arg_list):
        def joint_lnprior(p):
            res = 0
            # logger.debug("paramnames prior ({}): {}".format(len(arg_list["param"]),
            #                                                 arg_list["param"]))
            # logger.debug("params prior ({}): {}".format(len(p), p))
            for i, ln_prior in enumerate(list_lnpriors):
                res += ln_prior(p[i])
            return res
        return DocFunction(function=joint_lnprior, arg_list=arg_list)

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
        arg_list = OrderedDict()
        arg_list["param"] = list_paramnames.copy()
        arg_list["kwargs"] = []

        # def joint_lnprior(p):
        #     res = 0
        #     # logger.debug("paramnames prior ({}): {}".format(len(arg_list["param"]),
        #     #                                                 arg_list["param"]))
        #     # logger.debug("params prior ({}): {}".format(len(p), p))
        #     for i, ln_prior in enumerate(list_lnpriors):
        #         res += ln_prior(p[i])
        #     return res

        docf = self.__joint_lnprior_creator(list_lnpriors, arg_list)
        return docf

    def create_lnpriors(self, lnlike_db, individual_priors=None, affectinstmodel4dataset=False,
                        lock_db=False):
        """Create the joint prior function from the list of parameters of the lnlike functions."""
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="lnpriors", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        for inst_cat in lnlike_db:
            for inst_name in lnlike_db[inst_cat]:
                for inst_model in lnlike_db[inst_cat][inst_name]:
                    db[inst_cat][inst_name][inst_model] = {}
                    for obj in lnlike_db[inst_cat][inst_name][inst_model]:
                        arg_list = lnlike_db[inst_cat][inst_name][inst_model][obj].arg_list["param"]
                        (db[inst_cat][inst_name][inst_model][obj]
                         ) = self.create_joint_lnprior(list_paramnames=arg_list,
                                                       individual_priors=individual_priors)
        if lock_db:
            db.lock()
        return db

    def create_lnpriors_perdataset(self, individual_priors, lnprior_db, instmodel4dataset):
        """Create the log likelihood function with the data hardcoded."""
        db = {}
        l_func = []
        l_params = []
        l_params_idx = []
        l_allparams = []
        for dataset_name in instmodel4dataset:
            instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
            l_func.append(lnprior_db[instmod_fullname]["whole"].function)
            l_params.append(lnprior_db[instmod_fullname]["whole"].arg_list)
            idx_par = []
            for par in lnprior_db[instmod_fullname]["whole"].arg_list["param"]:
                if par not in l_allparams:
                    l_allparams.append(par)
                idx_par.append(l_allparams.index(par))
            l_params_idx.append(idx_par)

            db[dataset_name] = lnprior_db[instmod_fullname]["whole"]

        lnprior_all = self.create_joint_lnprior(l_allparams, individual_priors=individual_priors)

        arg_list_all = OrderedDict()
        arg_list_all["param"] = l_allparams
        arg_list_all["kwargs"] = []

        db["all"] = DocFunction(function=lnprior_all, arg_list=arg_list_all)

        return db
