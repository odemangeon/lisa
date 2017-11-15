#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of WASP-153 RV + LC data

@TODO:
"""
from __future__ import print_function
from logging import DEBUG, INFO
from math import ceil

from emcee import EnsembleSampler

# from ipdb import set_trace

import source.posterior.core.posterior as cpost
import source.tools.emcee_tools as et
import source.tools.mylogger as ml


obj_name = "WASP-153"

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

logger.info("########\nMCMC EXPLORATION")

# If needed, load the fitted values dataframe from a previous mcmc exploration analysis
load_from_pickle = False

if load_from_pickle:
    logger.info("0. Load from pickle")
    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                    folder=".")
else:
    pass

logger.info("1. Create a Posterior instance and give it the name of the object studied.")
post_instance = cpost.Posterior(object_name=obj_name)

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = "/Users/olivier/Data/lisa/{}".format(obj_name)

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = "/Users/olivier/Softwares/Specific_Analysis/lisa/{}".format(obj_name)

logger.info("3. Add datasets from a datasets file.")
post_instance.load_datasetsfile("datasets.txt")

logger.info("4. Add a model")
post_instance.define_model(category="GravitionalGroups", name=obj_name, stars=1, planets=1,
                           transit_model="batman", parametrisation=None)

logger.info("5. Create and modify LC parameter file")
post_instance.model.create_LC_param_file(paramfile_path="LC_param_file.py")

input("Modifiy the LC paramerisation file")

logger.info("6. Load the paramerisation file")
post_instance.model.load_LC_param_file()

logger.info("5. Apply a parametrisation to the model")
post_instance.model.apply_parametrisation(with_RVdrift=False, with_DeltaRV=False,
                                          with_OOT_var=False)

logger.info("6. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py")

input("Modifiy the paramerisation file")

logger.info("7. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("8. Create datasimulator functions")
test = post_instance.get_datasimulators()

logger.info("9. Create likelihood functions")
post_instance.get_lnlikelihoods()

logger.info("10. Create prior functions")
post_instance.get_individal_lnpriors()
post_instance.get_lnpriors()

logger.info("11. Create posterior functions")
post_instance.get_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

logger.info("12. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = ceil(int(ndim * 2.5) / 2) * 2  # To get an even number of walkers
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn)

logger.info("13. Create initial value")
if load_from_pickle:
    init_distrib = et.get_init_distrib_from_fitvalues(fitted_values=df_fittedval)
else:
    init_distrib = None
p0 = et.generate_random_init_pos(nwalker=nwalkers, post_instance=post_instance,
                                 init_distrib=init_distrib)
# logger.debug("Initial p0 values: {}".format(p0))

logger.info("14. Perform MCMC exploration")
et.explore(sampler, p0, nsteps=5000)

et.save_emceesampler(sampler, l_param_name, obj_name)
post_instance.save_post_instance()

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction
