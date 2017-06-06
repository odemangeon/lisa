#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of HD106315 RV + transit data

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
post_instance = cpost.Posterior(object_name="HD106315less")
object_name="HD106315less"

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
#post_instance.dataset_db.data_folder = "default"
post_instance.dataset_db.data_folder ="/Users/sbarros/Documents/work/python/photodynamic/lisa/data/HD106315new"

logger.info("3. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = "default"

logger.info("4. Add datasets from a datasets file.")
post_instance.load_datasetsfile("datasets_HD106315.txt")

logger.info("5. Add a model")
post_instance.define_model(category="GravitionalGroups", name="HD106315", stars=1, planets=2,
                           transit_model="pytransit-MandelAgol")

logger.info("6. Create and modify LC parameter file")
post_instance.model.create_LC_param_file(paramfile_path="LC_param_file.py")

input("Modifiy the LC paramerisation file")

logger.info("7. Load the paramerisation file")
post_instance.model.load_LC_param_file()

logger.info("8. Apply a parametrisation to the model")
post_instance.model.apply_RV_LC_EXOFAST_param(with_driftRV=False, with_DeltaRV=True,
                                              with_DeltaOOT=True, with_driftOOT=True)

logger.info("9. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py")

input("Modifiy the paramerisation file")

logger.info("10. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("11. Create datasimulator functions")
post_instance.get_datasimulators()

logger.info("12. Create likelihood functions")
post_instance.get_lnlikelihoods()

logger.info("13. Create prior functions")
post_instance.get_individal_lnpriors()
post_instance.get_lnpriors()

logger.info("14. Create posterior functions")
post_instance.get_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

logger.info("15. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = 64
# nthread = 4
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn)

logger.info("16. Create initial value")
p0 = [post_instance.model.get_initial_values(list_paramnames=arg_list["param"])
      for i in range(nwalkers)]
# logger.debug("Initial p0 values: {}".format(p0))

##run the mcmcm
et.explore(sampler, p0, nsteps=6000)

## 17 test is done on the chains to see if they are the same and some are rejected

l_walker_acceptfrac, _ = et.acceptancefraction_selection(sampler, sig_fact=2., verbose=1)
# if it goes bad l_walker_acceptfrac = range(nwalkers)

l_walker_lnpost, _ = et.lnposterior_selection(sampler, sig_fact=2., verbose=1)
l_walker = list(set(l_walker_acceptfrac) & set(l_walker_lnpost))
logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
            "".format((sampler.chain.shape[0] - len(l_walker)), sampler.chain.shape[0]))


zscores, first_steps = et.geweke_multi(sampler, first=0.1, last=0.40, intervals=50,
                                        l_walker=l_walker)
l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=2.0,
                                                l_walker=l_walker)
#l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=1.6,
#l_walker=l_walker)

'''
fitted_values = et.get_fitted_values(sampler, method="median", l_param_name=l_param_name,
                                     l_walker=l_walker_geweke, l_burnin=l_burnin)

sigma_m, _, sigma_p = da.getconfi(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke,
                                                         l_burnin=l_burnin),
                                  level=1, centre=fitted_values, l_param_name=l_param_name)


# when it doesnt work use the full chains to check
fitted_values = et.get_fitted_values(sampler, method="median", l_param_name=l_param_name, l_walker=l_walker)

sigma_m, _, sigma_p = da.getconfi(et.get_clean_flatchain(sampler, l_walker=l_walker), level=1, centre=fitted_values, l_param_name=l_param_name)


'''
# '''
# LCO_default_jitter: 1.387445160297815 +0.09181291887607768 -0.07685456808930335
# HD106315_b_secosw: -0.14575164437989702 +0.06192444292897231 -0.04982585969263226
# HD106315_b_sesinw: 0.05229325067513479 +0.059326788607019405 -0.06333261135994425
# HD106315_b_cosinc: 0.162739669280502 +0.07601606438303099 -0.10580067024162707
# HD106315_b_tc: 57586.545995363726 +0.004329751929617487 -0.0037560079217655584
# HD106315_b_P: 9.54711597104606 +0.0033449310465556437 -0.0017139399236540953
# HD106315_b_Rrat: 0.0198812419128618 +0.057380521019227075 -0.0032981963250899235
# HD106315_b_aR: 12.421565370953218 +11.046874302512759 -5.779226321688214
# HD106315_c_secosw: -0.13948871488873316 +0.04955338451829215 -0.08470996764114935
# HD106315_c_sesinw: -0.34002470620865205 +0.03294853148921423 -0.025309753288445036
# HD106315_c_cosinc: 0.010645780616845266 +0.010963576329495184 -0.008183558788938165
# HD106315_c_tc: 57569.01739142467 +0.0013580781305790879 -0.0014104066940490156
# HD106315_c_P: 21.056937409412942 +0.0003539905322860193 -0.0003606818811334733
# HD106315_c_Rrat: 0.030270368132602896 +0.0009735131889543371 -0.0006323964068336678
# HD106315_c_aR: 30.135854243450446 +1.4663004733354725 -2.8614665689413634
# HEARTS_default_jitter: -0.216013401230524 +0.08328823667824933 -0.07424784072651056
# HEARTS_default_DeltaRV: -0.005805187089926213 +0.002457232977789225 -0.0024550188249396433
# HD106315_A_v0: -3.4634167264437954 +0.0008534200427585681 -0.000718213044500704
# HD106315_b_K: 0.003078339697052979 +0.0011439652315305467 -0.001118991319765544
# HD106315_c_K: 0.00345614404395223 +0.001086475101596433 -0.0009263479526907116
# HARPS_default_jitter: 0.21145725068758703 +0.08869206617731307 -0.11735692643094896
# K2_default_jitter: 1.792820077400536 +0.10882497144427639 -0.27198697781567116


'''
et.plot_chains(sampler, l_param_name)
pl.savefig("./susana/images/"+object_name+"/traces_raw.png")
pl.close("all")
et.plot_chains(sampler, l_param_name, l_walker=l_walker_geweke, l_burnin=l_burnin)
pl.savefig("./susana/images/"+object_name+"/traces_geweke_select.png")
pl.close("all")
corner(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_name, truths=fitted_values)
pl.savefig("./susana/images/"+object_name+"/corner.png")
pl.close("all")
et.overplot_data_model(fitted_values, l_param_name,
                       post_instance.datasimulators.dataset_db, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30)
pl.savefig("./susana/images/"+object_name+"/data_comparison.png")
pl.close("all")
et.overplot_data_model(fitted_values, l_param_name,
                       post_instance.datasimulators.dataset_db, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30, phasefold=True,
                       phasefold_kwargs={"planets": ["b", 'c'],
                                         "P": [9.55244 , 21.056937409412942],
                                         "tc": [57586.5486, 57569.01739142467]})
pl.savefig("./susana/images/"+object_name+"/data_comparison_pholded.png")
pl.close("all")
'''
