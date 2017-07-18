#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of emcee chains

@TODO:
"""
from __future__ import print_function
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from sys import stdout

from corner import corner
import matplotlib.pyplot as pl
# from numpy import median, zeros, where, sqrt
import numpy as np
import pandas as pd

# from ipdb import set_trace

# Add lisa folder to python path
# lisa_folder = "/Users/olivier/Softwares/lisa/"
# if lisa_folder not in sys.path:
#     sys.path.append(lisa_folder)

import source.posterior.core.posterior as cpost
import source.tools.emcee_tools as et
import source.tools.stats.distribution_anali as da
import source.tools.convert as cv
import source.tools.mylogger as ml


## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="HD106315.log")


load_from_pickle = True

logger.info("1. Load from pickle if necessary")
if load_from_pickle:
    obj_name = "HD106315"
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle()
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
                                                                                   folder=".")
    print("l_param_name from posterior:\n{}".format(l_param_name_bis))
    print("l_param_name from pickle:\n{}".format(l_param_name))
else:
    chain = sampler.chain
    lnprobability = sampler.lnprobability
    acceptance_fraction = sampler.acceptance_fraction

nstep = chain.shape[1]
nwalker = chain.shape[0]
l_param_chainI = l_param_name + ["lnposterior"]
chainI = et.ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)

logger.info("2. Plot raw traces and lnpost histogram")
et.plot_chains(chain, lnprobability, l_param_name)
pl.savefig("./images/traces_raw.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[:, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_raw.png")
pl.close("all")

logger.info("3. Select walkers with acceptance_fraction and plot lnpost histogram")
l_walker_acceptfrac, _ = et.acceptancefraction_selection(acceptance_fraction,
                                                         sig_fact=2, quantile=75, verbose=1)
# l_walker_acceptfrac = np.arange(nwalker)
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_acceptfrac)
pl.savefig("./images/traces_accfrac_select.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker_acceptfrac, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_accefrac_select.png")
pl.close("all")

logger.info("4. Select walkers with ln posterior probability and plot lnpost histogram")
l_walker_lnpost, _ = et.lnposterior_selection(lnprobability, sig_fact=2, quantile=75,
                                              quantile_walker=90, verbose=1)
# l_walker_lnpost = np.arange(nwalker)
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_lnpost)
pl.savefig("./images/traces_lnpost_select.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker_lnpost, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_lnpost_select.png")
pl.close("all")

logger.info("5. Plot trace after acceptance fraction and ln posterior selection and plot lnpost "
            "histogram")
l_walker = list(set(l_walker_acceptfrac) & set(l_walker_lnpost))
# l_walker = l_walker_acceptfrac
logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
            "".format((nwalker - len(l_walker)), nwalker))
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker)
pl.savefig("./images/traces_accfrac&lnpost_select.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_accfrac&lnpost_select.png")
pl.close("all")

logger.info("6. Determine convergence and burnin values and plot lnpost histogram")
first_length = 50
zscores, first_steps = et.geweke_multi(chainI, first=10 * first_length / nstep, last=0.40,
                                       intervals=int(nstep / first_length), l_walker=l_walker)
l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=1,
                                                l_walker=l_walker)

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin)
pl.savefig("./images/traces_geweke_select.png")
pl.close("all")

# pl.figure()
# pl.hist(et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_geweke,
#                                l_burnin=l_burnin),
#         bins='auto')
# pl.savefig("./images/lnpost_hist_geweke_select.png")
# pl.close("all")

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin, suppress_burnin=True)
pl.savefig("./images/traces_geweke_select_burnsupress.png")
pl.close("all")

logger.info("7. Determine best fit values and error bars for main parameters")
fitted_values = et.get_fitted_values(chainI, method="median", l_param_name=l_param_chainI,
                                     l_walker=l_walker_geweke, l_burnin=l_burnin,
                                     lnprobability=lnprobability)

sigma_m, _, sigma_p = da.getconfi(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke,
                                                         l_burnin=l_burnin),
                                  level=1, centre=fitted_values, l_param_name=l_param_chainI)

df_fittedval = pd.DataFrame(index=l_param_chainI, data={'value': fitted_values, 'sigma-': sigma_m,
                                                        'sigma+': sigma_p})

et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values,
                                                "l_param": l_param_chainI},
                       df_fittedval=df_fittedval)

# A_LDR_ldc1: 0.48564308798332323 +0.002054793596156901 -0.0018749100361998838
# A_LDR_ldc2: 0.12703380220932714 +0.004575440976126471 -0.005315180168329783
# WASP-153_b_secosw: -0.0022078183793049315 +0.043298069896843414 -0.044403184435195836
# WASP-153_b_sesinw: -0.00323052794990469 +0.04706216927796164 -0.04936781477467243
# WASP-153_b_cosinc: 0.055350437075233426 +0.051139607134879674 -0.037882201174943154
# WASP-153_b_tc: 53142.53622274491 +0.003787136505707167 -0.0039350747465505265
# WASP-153_b_P: 3.33261296546394 +3.99122327721102e-06 -3.4293202828550307e-06
# WASP-153_b_Rrat: 0.08916183840630391 +0.004154136388374682 -0.002305334432888273
# WASP-153_b_aR: 7.149557742012522 +0.5844252582680056 -1.1301695739858522
# WASP-153_A_v0: -29.004143709886048 +0.0014451734488325485 -0.0014660033591233912
# WASP-153_b_K: 0.04398792176436185 +0.0018268843367851492 -0.0018524255444154342
# lnposterior: 77072.3338178657 +1.8955530416278634 -2.493650932490709

logger.info("8. Do correlation plot for main free parameters")
corner(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_chainI, truths=fitted_values)

pl.savefig("./images/corner.png")
pl.close("all")


logger.info("9. Do data comparision plots")
et.overplot_data_model(fitted_values, l_param_chainI,
                       post_instance.datasimulators, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30)

pl.savefig("./images/data_comparison.png")
pl.close("all")

planet_name = []
periods = []
tcs = []
for planet in post_instance.model.planets.values():
    planet_name.append(planet.name)
    periods.append(df_fittedval.loc[planet.P.full_name, 'value'])
    tcs.append(df_fittedval.loc[planet.tc.full_name, 'value'])

et.overplot_data_model(fitted_values, l_param_chainI,
                       post_instance.datasimulators, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30, phasefold=True,
                       phasefold_kwargs={"planets": planet_name,
                                         "P": periods,
                                         "tc": tcs})

pl.savefig("./images/data_comparison_pholded.png")
pl.close("all")

logger.info("10. Compute Secondary parameters")

# Compute other parameters
# Transit depth, T14, T12, b, i, omega, ecc, Mp, Rp, rho*, rhopl, a, Teff
chainIsec, l_param_name_sec = cv.get_secondary_chains(post_instance.model, chainI,
                                                      star_kwargs={"M": {"value": 1.20,
                                                                         "error": 0.09},
                                                                   "R": {"value": 1.18,
                                                                         "error": 0.20},
                                                                   "Teff": {"value": 5914,
                                                                            "error": 64}
                                                                   })
et.plot_chains(chainIsec, lnprobability, l_param_name_sec)
pl.savefig("./images/traces_secondary_raw.png")
pl.close("all")

et.plot_chains(chainIsec, lnprobability, l_param_name_sec, l_walker=l_walker_geweke)
pl.savefig("./images/traces_secondary_geweke_select.png")
pl.close("all")

fitted_values_sec = et.get_fitted_values(chainIsec, method="median", l_param_name=l_param_name_sec,
                                         l_walker=l_walker_geweke, l_burnin=l_burnin,
                                         lnprobability=lnprobability)
sigma_m_sec, _, sigma_p_sec = da.getconfi(et.get_clean_flatchain(chainIsec,
                                                                 l_walker=l_walker_geweke,
                                                                 l_burnin=l_burnin),
                                          level=1, centre=fitted_values_sec,
                                          l_param_name=l_param_name_sec)
df_fittedval = pd.concat([df_fittedval, pd.DataFrame(index=l_param_name_sec,
                                                     data={'value': fitted_values_sec,
                                                           'sigma-': sigma_m_sec,
                                                           'sigma+': sigma_p_sec})])
df_fittedval.to_pickle("df_fittedval.pk")

et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                       fitted_values_sec={"array": fitted_values_sec, "l_param": l_param_name_sec},
                       df_fittedval=df_fittedval)

et.write_latex_table("latex_parameter_table.tex", df_fittedval, obj_name)

# WASP-153_b_Trdepth: 0.007949833427991852 +0.0007580377238892398 -0.00040578114544703465
# WASP-153_b_inc: 86.82703199785874 +2.172060902437977 -2.940053173783056
# WASP-153_b_ecc: 0.0029774476859500344 +0.00500570623045885 -0.002257278024404077
# WASP-153_b_omega: -3.262399970234212 +65.62757469667467 -63.35210519355327
# WASP-153_b_b: 0.396780452523599 +0.24764739271490305 -0.26157495489197946
# WASP-153_b_R: 1.0310705469361867 +0.17989972591902115 -0.17782567810170846
# WASP-153_b_D14: 3.635401355231151 +0.15434101206210116 -0.10636592255736677
# WASP-153_b_D23: 2.9026329226256613 +0.09858497178408321 -0.2058050570248997
# WASP-153_b_M: 0.3656292445972623 +0.024115887706813943 -0.024042043504455324
# WASP-153_b_a: 0.04640751903611228 +0.001121906703373872 -0.0011838769756466958
# WASP-153_b_rhostar: 0.4411589494881613 +0.11726939200642278 -0.17787978429452866
# WASP-153_b_loggstar: 4.136163133455721 +0.13627892850195877 -0.2266663128441193
# WASP-153_b_circtime: 0.0148067309639834 +0.02356196526705877 -0.008215806538426927
# WASP-153_b_rho: 0.07947739019696373 +0.06108560951841041 -0.03048814094415561
# WASP-153_b_Teq: 1564.5314491042664 +140.34379222237726 -62.92176588611437

# In this case there is nan values in the D14 and D23 chains and it makes corner crash
corner(et.get_clean_flatchain(chainIsec, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_name_sec, truths=fitted_values_sec)
pl.savefig("./images/corner_sec.png")
pl.close("all")


##########
# Try another analysis with on the highest probability walker

# logger.info("4bis. Select walkers with strict ln posterior probability lower threshold and plot "
#             "lnpost histogram")
#
# l_walker_lnPup, _ = et.lnposterior_selection(lnprobability, sig_fact=0, quantile=50, verbose=1)
#
# pl.figure()
# pl.hist(lnprobability[l_walker_lnPup, int(nstep / 2):].flatten(), bins='auto')
# pl.savefig("./images/lnpost_hist_lnpost_select_Pup.png")
# pl.show(block=False)
# pl.close("all")

# logger.info("6. Determine convergence and burnin values and plot lnpost histogram")
# first_length = 50
# zscores, first_steps = et.geweke_multi(chainI, first=1.5 * first_length / nstep, last=0.40,
#                                        intervals=int(nstep / first_length),
#                                        l_walker=l_walker_lnPup)
# l_burnin_Pup, l_walker_geweke_Pup = et.geweke_selection(zscores, first_steps=first_steps,
#                                                         geweke_thres=2, l_walker=l_walker_lnPup)

# et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke_Pup,
#                l_burnin=l_burnin_Pup)

# pl.savefig("./images/traces_geweke_select_Pup.png")
# pl.close("all")

# pl.figure()
# pl.hist(et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_geweke_Pup,
#                                l_burnin=l_burnin_Pup),
#         bins='auto')
# pl.savefig("./images/lnpost_hist_geweke_select_Pup.png")
# pl.close("all")

# logger.info("7. Determine best fit values and error bars for main parameters")
# fitted_values_Pup = et.get_fitted_values(chainI, method="median", l_param_name=l_param_chainI,
#                                          l_walker=l_walker_geweke_Pup, l_burnin=l_burnin_Pup,
#                                          lnprobability=lnprobability)

# sigma_m_Pup, _, sigma_p_Pup = da.getconfi(et.get_clean_flatchain(chainI,
#                                                                  l_walker=l_walker_geweke_Pup,
#                                                                  l_burnin=l_burnin_Pup),
#                                           level=1, centre=fitted_values_Pup,
#                                           l_param_name=l_param_chainI)

# df_fittedval_Pup = pd.DataFrame(index=l_param_chainI, data={'value': fitted_values_Pup,
#                                                             'sigma-': sigma_m_Pup,
#                                                             'sigma+': sigma_p_Pup})

# et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values_Pup,
#                                                 "l_param": l_param_chainI},
#                        df_fittedval=df_fittedval)

# logger.info("8. Do correlation plot for main free parameters")
# corner(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke_Pup, l_burnin=l_burnin_Pup),
#        labels=l_param_chainI, truths=fitted_values_Pup)
#
# pl.savefig("./images/corner_Pup.png")
# pl.close("all")

# logger.info("9. Do data comparision plots")
# et.overplot_data_model(fitted_values_Pup, l_param_chainI,
#                        post_instance.datasimulators.dataset_db, post_instance.dataset_db,
#                        post_instance.noisemodels.dataset_db,
#                        oversamp=30)
# pl.savefig("./images/data_comparison_Pup.png")
# pl.close("all")
#
# planet_name = []
# periods = []
# tcs = []
# for planet in post_instance.model.planets.values():
#     planet_name.append(planet.name)
#     periods.append(df_fittedval_Pup.loc[planet.P.full_name, 'value'])
#     tcs.append(df_fittedval_Pup.loc[planet.tc.full_name, 'value'])
#
# et.overplot_data_model(fitted_values_Pup, l_param_chainI,
#                        post_instance.datasimulators.dataset_db, post_instance.dataset_db,
#                        post_instance.noisemodels.dataset_db,
#                        oversamp=30, phasefold=True,
#                        phasefold_kwargs={"planets": planet_name,
#                                          "P": periods,
#                                          "tc": tcs})
#
# pl.savefig("./images/data_comparison_pholded_Pup.png")
# pl.close("all")
