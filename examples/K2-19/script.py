#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of K2-19 RV data

@TODO:
"""

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from sys import stdout

from emcee import EnsembleSampler
from corner import corner
import matplotlib.pyplot as pl
from numpy import median
import numpy as np
# from ipdb import set_trace

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
import lisa.tools.stats.distribution_anali as da
import lisa.posterior.exoplanet.model.convert as cv


## logger
logger = getLogger()

level_log = DEBUG
level_hand = INFO

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
post_instance = cpost.Posterior(object_name="K2-19")

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = "default"

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = "default"

logger.info("3. Add datasets (from a file, their is otherways).")
post_instance.dataset_db.add_datasets_from_datasetfile("datasets_K2-19.txt")

logger.info("4. Add a model")
post_instance.define_model(category="GravitionalGroups", name="K2-19", stars=1, planets=3)

logger.info("5. Apply a parametrisation to the model")
post_instance.model.apply_RV_EXOFAST_param(with_jitter=True, with_drift=False, with_DeltaRV=True)

logger.info("6. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py")

input("Modifiy the paramerisation file")

logger.info("7. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("8. Create datasimulator functions")
post_instance.get_datasimulators()

logger.info("9. Create likelihood functions")
post_instance.get_lnlikelihoods(category="jitter multiplicative")

logger.info("10. Create prior functions")
post_instance.get_individal_lnpriors()
post_instance.get_lnpriors()

logger.info("11. Create posterior functions")
post_instance.get_lnposteriors()
l_param_names = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

logger.info("12. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
nwalkers = 64
nthread = 4
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn, threads=nthread)

logger.info("13. Create initial value")
p0 = [post_instance.model.get_initial_values(list_paramnames=arg_list["param"])
      for i in range(nwalkers)]
logger.info("Initial p0 values: {}".format(p0))
# et.explore(sampler, p0, nsteps=100000, width=50, save_to_file="run/K2-19/chain.dat")
# fitted_values = median(sampler.flatchain, axis=0)
# sigma_m, _, sigma_p = da.getconfi(sampler.flatchain, level=1, centre=fitted_values,
#                                   l_param_names=l_param_names)
# FIES_default_jitter: -0.0625227990802113 +0.2500408702113035 -0.22507037228270926
# FIES_default_DeltaRV: -0.03517950404298153 +0.008673149347378645 -0.008200882980438917
# K2-19_A_v0: 7.229357021685565 +0.007077635841379326 -0.007482451459812189
# K2-19_b_K: 0.011397465715731449 +0.0015548232131528568 -0.0014980572205793245
# K2-19_b_secosw: -0.02027431451270454 +0.15406036170480725 -0.13700621007308322
# K2-19_b_sesinw: -0.002980833351028075 +0.12009475355519582 -0.12317666840324178
# K2-19_b_t0: 57422.1108358127 +0.7912480011364096 -0.9471004452207126
# K2-19_b_P: 7.920111578716582 +0.0012877162112232554 -0.0012976388607075506
# K2-19_c_K: 0.004548436453058849 +0.0016837727321609135 -0.001645091780672037
# K2-19_c_secosw: -0.01927077531443768 +0.12082987162341283 -0.09221862576283968
# K2-19_c_sesinw: -0.009340138336164039 +0.09435504245448285 -0.08417585276923875
# K2-19_c_t0: 57424.27565996912 +0.15077056907466613 -0.1523111001442885
# K2-19_c_P: 11.907017682490391 +0.0025375743348803326 -0.0025993987100623173
# K2-19_d_K: 0.0011344059542410987 +0.0012808932258368847 -0.0008168412945550362
# K2-19_d_secosw: -0.0010061434858126064 +0.08068528775030023 -0.07925393842627695
# K2-19_d_sesinw: -0.0059760408756260874 +0.12240709429961648 -0.12110892380531707
# K2-19_d_t0: 56808.92041378899 +0.008480150449031498 -0.00868523215467576
# K2-19_d_P: 2.508504584949818 +0.0004114711927369896 -0.00041835347558150104
# HARPS_default1_jitter: 0.05401465703839099 +0.2914176262115956 -0.2886393167588232
# HARPS_default0_DeltaRV: 0.11078431985464073 +0.007657856721490178 -0.0073822001046248975
# HARPS_default1_DeltaRV: -7.338368810232539 +0.0025294246136615683 -0.0024948619602769284
# PFS_default_jitter: 1.0676109690966047 +0.09273291941244177 -0.08768407881891482
# PFS_default_DeltaRV: -7.22967855257833 +0.007721777507881278 -0.007327709425771545
# SOPHIE_default_jitter: 0.16074463079455198 +0.2197182196424649 -0.20186501814407087
# HARPSN_default_jitter: 0.439022544761805 +0.2658812312970047 -0.24026696213003798
# HARPSN_default_DeltaRV: 0.08430999701866108 +0.008433593474537038 -0.008077349248278784
# HARPS_default0_jitter: 0.9163686069180997 +0.1399371732526119 -0.13035105204442143
# et.plot_chains(sampler, l_param_names)
# pl.savefig("traces.png")
# pl.close("all")
# corner(sampler.flatchain[:, :], labels=l_param_names)
# pl.savefig("corner.png")
# pl.close("all")
# et.overplot_data_model(fitted_values,
#                        post_instance.lnposteriors.dataset_db["all"].arg_list["param"],
#                        post_instance.datasimulators.dataset_db, post_instance.dataset_db,
#                        oversamp=20)
# pl.savefig("data_comparison.png")
# pl.close("all")
# pl.show()
chain_omegab = cv.getomega(sampler.flatchain[:, 3], sampler.flatchain[:, 4])
chain_eccb = cv.getecc(sampler.flatchain[:, 3], sampler.flatchain[:, 4])
fitted_omega_ecc = median(np.concatenate((chain_omegab[:, np.newaxis], chain_eccb[:, np.newaxis]),
                                         axis=1),
                          axis=0)
da.getconfi(np.concatenate((chain_omegab[:, np.newaxis], chain_eccb[:, np.newaxis]), axis=1),
            level=1, centre=fitted_omega_ecc, l_param_names=["K2-19_b_omega", "K2-19_b_ecc"])
# K2-19_b_omega: -1.0589489852656884 +2.5449189652035686 -0.43972301779158807
# K2-19_b_ecc: 0.010888870588374192 +0.02856550262308008 -0.009499207961647136
corner(np.concatenate((chain_omegab[:, np.newaxis], chain_eccb[:, np.newaxis]), axis=1),
       labels=["K2-19_b_omega", "K2-19_b_ecc"])
pl.savefig("corner_omega_ecc_b.png")
chain_omegac = cv.getomega(sampler.flatchain[:, 8], sampler.flatchain[:, 9])
chain_eccc = cv.getecc(sampler.flatchain[:, 8], sampler.flatchain[:, 9])
fitted_omega_eccc = median(np.concatenate((chain_omegac[:, np.newaxis], chain_eccc[:, np.newaxis]),
                           axis=1), axis=0)
da.getconfi(np.concatenate((chain_omegac[:, np.newaxis], chain_eccc[:, np.newaxis]), axis=1),
            level=1, centre=fitted_omega_eccc, l_param_names=["K2-19_c_omega", "K2-19_c_ecc"])
# K2-19_c_omega: -1.323780995645101 +2.853158453181614 -0.20955057245239783
# K2-19_c_ecc: 0.006318397507913465 +0.013664856759846411 -0.005052843770993472
corner(np.concatenate((chain_omegac[:, np.newaxis], chain_eccc[:, np.newaxis]), axis=1),
       labels=["K2-19_c_omega", "K2-19_c_ecc"])
pl.savefig("corner_omega_ecc_c.png")
