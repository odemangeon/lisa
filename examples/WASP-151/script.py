#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of WASP-151 RV data

@TODO:
"""
from __future__ import print_function
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from sys import stdout


from emcee import EnsembleSampler
from corner import corner
import matplotlib.pyplot as pl
from numpy import median
import numpy as np
import sys
# from ipdb import set_trace

# Add lisa folder to python path
lisa_folder = "/Users/sbarros/Documents/work/python/photodynamic/lisa/"
if lisa_folder not in sys.path:
    sys.path.append(lisa_folder)

import source.posterior.core.posterior as cpost
import source.tools.emcee_tools as et
import source.tools.stats.distribution_anali as da
import source.tools.convert as cv


## logger
logger = getLogger()

level_log = DEBUG
level_hand = DEBUG

if logger.level != level_log:
    logger.setLevel(level_log)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(level_hand)
    formatter_short = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter_detailled = Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s "
                                            "- %(funcName)s() \n%(message)s")
    ch.setFormatter(formatter_detailled)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != level_hand:
        ch.setLevel(level_hand)

logger.info("1. Create a Posterior instance and give it the name of the object studied.")
post_instance = cpost.Posterior(object_name="WASP-151")

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = "default"

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = "default"

logger.info("3. Add datasets from a datasets file.")
post_instance.load_datasetsfile("datasets_WASP-151.txt")

logger.info("4. Add a model")
post_instance.define_model(category="GravitionalGroups", name="WASP-151", stars=1, planets=1,
                           transit_model="pytransit-MandelAgol")

logger.info("5. Create and modify LC parameter file")
post_instance.model.create_LC_param_file(paramfile_path="LC_param_file.py")

input("Modifiy the LC paramerisation file")

logger.info("6. Load the paramerisation file")
post_instance.model.load_LC_param_file()

logger.info("5. Apply a parametrisation to the model")
post_instance.model.apply_RV_LC_EXOFAST_param(with_driftRV=False, with_DeltaRV=True,
                                              with_DeltaOOT=True, with_driftOOT=True)

logger.info("6. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py")

input("Modifiy the paramerisation file")

logger.info("7. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("8. Create datasimulator functions")
post_instance.get_datasimulators()

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
nwalkers = 64
# nthread = 4
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn)

logger.info("13. Create initial value")
p0 = [post_instance.model.get_initial_values(list_paramnames=arg_list["param"])
      for i in range(nwalkers)]
# logger.debug("Initial p0 values: {}".format(p0))
et.explore(sampler, p0, nsteps=1000)
l_walker_acceptfrac, _ = et.acceptancefraction_selection(sampler, sig_fact=2., verbose=1)
l_walker_lnpost, _ = et.lnposterior_selection(sampler, sig_fact=2., verbose=1)
l_walker = list(set(l_walker_acceptfrac) & set(l_walker_lnpost))
logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
            "".format((sampler.chain.shape[0] - len(l_walker)), sampler.chain.shape[0]))
zscores, first_steps = et.geweke_multi(sampler, first=0.1, last=0.40, intervals=50,
                                       l_walker=l_walker)
l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=1.6,
                                                l_walker=l_walker)
fitted_values = et.get_fitted_values(sampler, method="median", l_param_name=l_param_name,
                                     l_walker=l_walker_geweke, l_burnin=l_burnin)
sigma_m, _, sigma_p = da.getconfi(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke,
                                                         l_burnin=l_burnin),
                                  level=1, centre=fitted_values, l_param_name=l_param_name)
# SOPHIE_default_jitter: 0.07390628909168875 +0.07092457023056994 -0.07661313680035657
# WASP-151_A_v0: -12.369079060321306 +0.0024455080593792644 -0.0022291702809340563
# WASP-151_b_K: 0.03701494270414841 +0.0029996564799572925 -0.003242621138187164
# WASP-151_b_secosw: -0.011524976266634243 +0.03680594008156956 -0.038812447556235426
# WASP-151_b_sesinw: 0.009475155023900296 +0.038499815697444734 -0.038550565561430855
# WASP-151_b_tc: 57741.00752174061 +0.0008870884121279232 -0.0016435749785159715
# WASP-151_b_P: 4.533460732028823 +7.417328449577099e-05 -6.427026153055238e-05
# K2_default_jitter: 2.1075500774917666 +0.027959739228607727 -0.03306713415133178
# A_LDKp_ldc1: 0.5500632701363917 +0.0026401049209291427 -0.002497404568402417
# A_LDKp_ldc2: 0.11835867155682295 +0.005592884985978361 -0.006067235897780507
# WASP-151_b_cosinc: 0.02707318020702465 +0.017146066892261287 -0.015311925555136857
# WASP-151_b_Rrat: 0.10105118308635531 +0.0017288716142898897 -0.0009004305596509582
# WASP-151_b_aR: 9.967458319518668 +0.31018483846089673 -0.5501394571610305
et.plot_chains(sampler, l_param_name)
pl.savefig("./images/traces_raw.png")
pl.close("all")
et.plot_chains(sampler, l_param_name, l_walker=l_walker_geweke, l_burnin=l_burnin)
pl.savefig("./images/traces_geweke_select.png")
pl.close("all")
corner(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_name, truths=fitted_values)
pl.savefig("./images/corner.png")
pl.close("all")
et.overplot_data_model(fitted_values, l_param_name,
                       post_instance.datasimulators.dataset_db, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30)
pl.savefig("./images/data_comparison.png")
pl.close("all")
et.overplot_data_model(fitted_values, l_param_name,
                       post_instance.datasimulators.dataset_db, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30, phasefold=True,
                       phasefold_kwargs={"planets": ["b", ],
                                         "P": [4.533460664271991, ],
                                         "tc": [57741.007471378594, ]})
pl.savefig("./images/data_comparison_pholded.png")
pl.close("all")
