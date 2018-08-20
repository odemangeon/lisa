#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
model_prior module.

The objective of this module is to define the Model_Prior class which will generate the prior functions.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import OrderedDict
from textwrap import dedent

from .manager_prior import Manager_Prior
from ..database_func import DatabaseInstLvlDataset
from ....tools.function_w_doc import DocFunction
from ....tools.miscellaneous import spacestring_like


## logger object
logger = getLogger()
## manager object
manager = Manager_Prior()
manager.load_setup()

## Name of the joint prior dictionary for the parameter file
joint_prior_name = 'joint_prior'


class Model_Prior(object):
    """docstring for Model_Prior."""
    def __init__(self, paramfile_info):
        """Initialise the information related to the Prior for the Model instance.

        This should be called from the Core_Model.__init__ method.
        This class is not meant to be instanciated directly (except for test purposes).

        :param dict paramfile_info: Dictionary containing the name of information that the parameter
            file provides for each parameter
        """
        # Initialise the joint_prior_container
        self.__joint_priors = OrderedDict()
        # Update paramfile_info with the name of the information related to the joint priors
        paramfile_info["joint_prior"] = ['category', 'args', 'params']

    @property
    def joint_prior_container(self):
        """Container where the information regarding the joint priors are stored.

        It's an OrderedDict with as keys the joint prior reference used in the parameter file and as
        values a dictionary with three keys: "category" which contain the joint prior category,
        "args": which contains the arguments to use for the initialisation of the joint prior instance,
        "params": with a dictionary which associate its keys which are the param keys define in the
        Joint prior class, to its value which the name of the parameter chosen for these param keys.
        """
        return self.__joint_priors

    def get_paramfile_section_jointprior(self):
        """Return the text for the section to define joint priors in the parameter file."""
        text_joint_param_distrib = """
        # Joint parameters
        # Define below the joint parameter distributions.
        {joint_prior_name} = {{# Example:
        {tab}# 'priorhkP': {{'category': 'hkP', 'args': {{'Pb_prior': {{'category': 'uniform', 'args': {{'vmin': 0.0, 'vmax': 1.0}} }} }},
        {tab}#              'params': {{'hplus': 'K219_hplus', 'hminus': 'K219_hminus',
        {tab}#                         'kplus': 'K219_kplus', 'kminus': 'K219_kminus',
        {tab}#                         'Pb': 'K219_b_P', 'Pc': 'K219_c_P'}}
        {tab}#              }}
        {tab}}}
        """.format(joint_prior_name=joint_prior_name,
                   tab=spacestring_like("{} = {{".format(joint_prior_name)))
        return dedent(text_joint_param_distrib)

    def load_jointprior_config(self, dico_config):
        """load the configuration for joint priors specified by the dictionary into joint_prior_container

        :param dict dico_config: Dictionnary containing the joint priors information.
        """
        dico_config_jointprior = dico_config[joint_prior_name]
        self.joint_prior_container.clear()
        logger.debug("joint prior container cleared.")
        for joint_prior_ref, dico_jointprior in dico_config_jointprior.items():
            # Check that the joint prior category is available
            if manager.is_available_priortype(dico_jointprior["category"]):
                priorfunction_subclass = manager.get_priorfunc_subclass(dico_jointprior["category"])
                # Check that this is a joint prior
                if not priorfunction_subclass.joint:
                    raise ValueError("Prior category {} is not a joint prior category".format(dico_jointprior["category"]))
                # Check that the arguments are fine
                priorfunction_subclass.check_args(list(dico_jointprior["args"].keys()))
                # Check the parameters
                priorfunction_subclass.check_params(dico_jointprior["params"], self)
            else:
                raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                 "".format(dico_jointprior["category"], manager.get_available_priors()))
            self.joint_prior_container[joint_prior_ref] = {"category": dico_jointprior["category"],
                                                           "args": dico_jointprior["args"],
                                                           "params": dico_jointprior["params"]}
            logger.info("Joint prior {} of category {} added to the joint prior container."
                        "".format(joint_prior_ref, dico_jointprior["category"]))

    def create_individual_lnpriors(self):
        """Return a dictionnary providing the individual prior probability density functions.

        :return dict priors: Return the dictionary containing all the elementary priors (marginal and joints)
            for all the main and free parameters of the model.
        """
        # Look for all the main free parameters in the model (self) and put them in two dict
        # marginal and joint dependending on wether they have a marginal or joint prior.
        marginal = OrderedDict()
        joint = OrderedDict()
        for param in self.get_list_params(main=True, free=True, recursive=True):
            if param.joint:
                joint[param.get_name(include_prefix=True, recursive=True)] = param
            else:
                marginal[param.get_name(include_prefix=True, recursive=True)] = param
        # Create a dict to receive the priors with two keys: marginal and joint
        priors = {"marginal": {}, "joint": {"logpdf": {}, "param_names": {}}}
        # For each parameter in the list of marginal (step 1): Create an entry in
        # "marginal" (see step 2) which to the full name of the parameter associate the
        # marginal prior function.
        for full_name, param in marginal.items():
            prior_func = manager.get_priorfunc_subclass(param.prior_category)(**param.prior_args)
            priors["marginal"][full_name] = prior_func.create_logpdf()
        # For each parameter in the list of joint (step 1):
        # Check if the joint prior references is already in the priors["joint"] dictionary meaning
        # that it has already been created for another parameter.
        # If not, get the info from self.joint_prior_container, create the joint prior instance
        # Create the logpdf
        for full_name, param in joint.items():
            if param.joint_prior_ref not in priors["joint"]:
                joint_prior_info = self.joint_prior_container[param.joint_prior_ref]
                joint_prior_func = manager.get_priorfunc_subclass(joint_prior_info["category"])(**joint_prior_info["args"])
                params = {param_ref: self.get_parameter(param_name, recursive=True) for param_ref, param_name in joint_prior_info["params"].items()}
                priors["joint"]["logpdf"][param.joint_prior_ref] = joint_prior_func.create_logpdf(params)
                priors["joint"]["param_names"][full_name] = param.joint_prior_ref
        return priors

    def __joint_lnprior_creator(self, lnpriors_and_indexes, arg_list):
        """Create and return the joint prior function.

        :param list_of_tuple lnpriors_and_indexes: List of tuples of 2 elements. Each element
            contain the a prior function as its element 0 and an index or a list of indexes as its element 1.
            If there the prior function is the marginal prior of a parameter, the second element is
            be one int giving the index of the parameter in the input array. If the prior function is
            a joint prior of several parameters, the second element is a list of int giving the indexes
            of these parameters in the input array.
        :param dict_of_list arg_list: dictionary with two keys "param" and "kwargs". "param" contain
            the list of parameter full names giving the order in which the parameter values should be provided
            in the input array of the output joint prior function.
        :return DocFunction func: Joint prior function.
        """
        def joint_lnprior(p):
            res = 0
            # logger.debug("paramnames prior ({}): {}".format(len(arg_list["param"]),
            #                                                 arg_list["param"]))
            # logger.debug("params prior ({}): {}".format(len(p), p))
            for ln_prior, ii in lnpriors_and_indexes:
                res += ln_prior(p[ii])
            return res
        return DocFunction(function=joint_lnprior, arg_list=arg_list)

    def create_joint_lnprior(self, list_paramnames, individual_priors=None):
        """Return a joint prior function for the list of parameter provided.

        :param list_of_str list_paramnames: List of parameters full names (include_prefix and recursive)
        :param dict individual_priors: Dictionary produced by the create_individual_lnpriors method.
            If None it will created with this method.
        :return DocFunction docf: DocFunction giving the joint ln prior
        """
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()

        marginal_lnpriors = []
        joint_lnpriors = OrderedDict()
        for ii, param_name in enumerate(list_paramnames):
            if param_name in individual_priors["marginal"]:
                marginal_lnpriors.append((individual_priors['marginal'][param_name], ii))
            elif param_name in individual_priors["joint"]["param_names"]:
                joint_prior_ref = individual_priors["joint"]["param_names"][param_name]
                if joint_prior_ref in joint_lnpriors:
                    joint_lnpriors[joint_prior_ref][1].append(ii)
                else:
                    joint_lnpriors[joint_prior_ref] = (individual_priors["joint"]["logpdf"][joint_prior_ref], [ii])
            else:
                raise ValueError("Parameter {} doesn't exist in the individual priors dictionary."
                                 "".format(param_name))
        arg_list = OrderedDict()
        arg_list["param"] = list_paramnames.copy()
        arg_list["kwargs"] = []
        docf = self.__joint_lnprior_creator(marginal_lnpriors + list(joint_lnpriors.values()), arg_list)
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
