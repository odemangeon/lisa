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
        for param in self.get_list_params(main=True, free=True, recursive=True):
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

        :param list_of_str list_paramnames: List of parameters full names
        :param dict individual_priors: Dictionary produced by the create_individual_lnpriors method.
            If None it will created with this method.
        :return DocFunction docf: DocFunction giving the joint ln prior
        """
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()

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

    def create_lnpriors_perdataset(self, individual_priors, lnlike_db_dtst):
        """Create the ln prior functions associated to the lnlikelihood of each dataset.

        :param dict individual_priors: Dictionary produced by the create_individual_lnpriors method.
        :param dict lnlike_db_dtst: Dictionary with key = dataset name, value = LikelihoodDocFunc
            giving the likelihood doc function for the dataset
        :return dict db: Dictionary with key = dataset name, value = DocFunction
            giving the likelihood doc function for the dataset
        """
        db = {}
        for dataset_name, lnlike_docfunc in lnlike_db_dtst.items():
            db[dataset_name] = self.create_joint_lnprior(lnlike_docfunc.params_model,
                                                         individual_priors=individual_priors)
        return db
