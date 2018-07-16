#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of emcee chains

@TODO:
"""
from __future__ import print_function
from logging import DEBUG, INFO

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

from source.tools.chain_interpreter import ChainsInterpret


## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format("WASP-151"))

logger.info("########\nCHAIN ANALYSIS")

load_from_pickle = False

if load_from_pickle:
    logger.info("0. Load from pickle")
    obj_name = "WASP-151"
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle()
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
                                                                                   folder=".")
    print("l_param_name from posterior:\n{}".format(l_param_name_bis))
    print("l_param_name from pickle:\n{}".format(l_param_name))

nstep = chain.shape[1]
nwalker = chain.shape[0]
l_param_chainI = l_param_name + ["lnposterior"]
chainI = ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)

logger.info("1. Plot raw traces and lnpost histogram")
et.plot_chains(chain, lnprobability, l_param_name)
pl.savefig("./images/traces_raw.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[:, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_raw.png")
pl.close("all")

logger.info("2. Select walkers with acceptance_fraction and plot lnpost histogram")
l_walker_acceptfrac, _ = et.acceptancefraction_selection(acceptance_fraction,
                                                         sig_fact=2, quantile=50, verbose=1)
# l_walker_acceptfrac = np.arange(nwalker)
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_acceptfrac)
pl.savefig("./images/traces_accfrac_select.png")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker_acceptfrac, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_accefrac_select.png")
pl.close("all")

logger.info("3. Select walkers with ln posterior probability and plot lnpost histogram")
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

logger.info("4. Plot trace after acceptance fraction and ln posterior selection and plot lnpost "
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

logger.info("5. Determine convergence and burnin values and plot lnpost histogram")
first_length = 50
zscores, first_steps = et.geweke_multi(chainI, first=10 * first_length / nstep, last=0.10,
                                       intervals=int(nstep / first_length), l_walker=l_walker)
l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=3,
                                                l_walker=l_walker)

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin)
pl.savefig("./images/traces_geweke_select.png")
pl.close("all")

pl.figure()
pl.hist(et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_geweke,
                               l_burnin=l_burnin),
        bins='auto')
pl.savefig("./images/lnpost_hist_geweke_select.png")
pl.close("all")

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin, suppress_burnin=True)

pl.savefig("./images/traces_geweke_select_burnsupress.png")
pl.close("all")

logger.info("6. Determine best fit values and error bars for main parameters")
fitted_values = et.get_fitted_values(chainI, method="median", l_param_name=l_param_chainI,
                                     l_walker=l_walker_geweke, l_burnin=l_burnin,
                                     lnprobability=lnprobability)

sigma_p, _, sigma_m = da.getconfi(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke,
                                                         l_burnin=l_burnin),
                                  level=1, centre=fitted_values, l_param_name=l_param_chainI)

df_fittedval = pd.DataFrame(index=l_param_chainI, data={'value': fitted_values, 'sigma-': sigma_m,
                                                        'sigma+': sigma_p})

et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values,
                                                "l_param": l_param_chainI},
                       df_fittedval=df_fittedval)

# CORALIE_default_DeltaRV: 0.05778688769256716 +0.008856203789895802 -0.008204221527165684
# WASP-151_A_v0: -12.368944577952076 +0.002268210960879813 -0.0023075858823560225
# WASP-151_b_K: 0.03769209259641915 +0.0032156586979600332 -0.003497625743969175
# WASP-151_b_secosw: -0.03998227989377329 +0.037482791655467924 -0.0388838016781312
# WASP-151_b_sesinw: -0.058342563177056946 +0.052810329862481964 -0.05569352300902646
# WASP-151_b_tc: 57741.00811636491 +0.00016782111924840137 -0.0001630349361221306
# WASP-151_b_P: 4.53347054177295 +3.6865230663707393e-06 -3.7860360455610476e-06
# IAC80_default2_OOT0: -0.001001478590566569 +0.0005592629831055482 -0.0005756107991678019
# IAC80_default2_OOT1: -0.004397827172877351 +0.006544871071341735 -0.00646673277587775
# IAC80_default0_OOT0: 0.004209814830212023 +0.00039762548169607753 -0.0003859782911181074
# IAC80_default0_OOT1: -0.024349764651820947 +0.003375504235133442 -0.003221924030709214
# IAC80_default3_OOT0: -0.00012362790041629688 +0.0007833263074036075 -0.0008280989883210699
# IAC80_default3_OOT1: 0.02292039660243121 +0.018249693182281854 -0.017084146178486605
# TRAPPIST_default_OOT0: -0.00010449400823809835 +0.0003686528686591064 -0.00035626885039679023
# TRAPPIST_default_OOT1: 0.00896063982293993 +0.004408664983774825 -0.004444343804447719
# A_LDR_ldc1: 0.47852738562823216 +0.0021786920065350324 -0.0022292309114436692
# A_LDR_ldc2: 0.12995706969146598 +0.005955720541100495 -0.005425751391630318
# A_LDKp_ldc1: 0.5478431386222736 +0.0024965670486715164 -0.0023691249234447653
# A_LDKp_ldc2: 0.11346604259425236 +0.00552203692028802 -0.005436500919427295
# A_LDz_ldc1: 0.34120149470773975 +0.001334308234516357 -0.0012275011230082344
# A_LDz_ldc2: 0.12540235724528326 +0.0040773860313259025 -0.004378546855144841
# A_LDNG_ldc1: 0.48644970368129853 +0.002218816278050706 -0.002044161965488178
# A_LDNG_ldc2: 0.13566379204818194 +0.008642111649472178 -0.006660903785327632
# WASP-151_b_cosinc: 0.013689653206099906 +0.007652703261549326 -0.006643437695756944
# WASP-151_b_Rrat: 0.10099528444915948 +0.0004065283542344367 -0.0002800330952723584
# WASP-151_b_aR: 10.281621666633825 +0.1061902625677078 -0.1343000980086959
# CORALIE_default_jitter: 0.007782099818299495 +0.05376926559835969 -0.05454943823619614
# SOPHIE_default_jitter: 0.027331059387258848 +0.04645500496914901 -0.047007248796942756
# IAC80_default2_jitter: -0.22842045314352544 +0.05365674519003824 -0.05227102423320945
# IAC80_default0_jitter: -0.3186523845687991 +0.04823228489133674 -0.049382569619340067
# IAC80_default3_jitter: -0.13268165277553906 +0.04858034310414369 -0.049520299695419656
# K2_default_jitter: 1.7119692053062363 +0.018687945887277513 -0.017753704249603208
# TRAPPIST_default_jitter: -0.005833621625560559 +0.02908163802367659 -0.030162047916249442
# EulerCam_default_jitter: 0.259159745832235 +0.026732276302900426 -0.029074592038908553
# WASP_default_jitter: 0.1141550329019023 +0.007938480310773488 -0.00783416832817345
# lnposterior: 27415.766538621956 +4.8864916331694985 -7.360803247203876

logger.info("7. Do correlation plot for main free parameters")
corner(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_chainI, truths=fitted_values)

pl.savefig("./images/corner.png")
pl.close("all")


logger.info("8. Do data comparision plots")
et.overplot_data_model(param=fitted_values, l_param_name=l_param_chainI,
                       datasim_dbf=post_instance.datasimulators,
                       dataset_db=post_instance.dataset_db,
                       model_instance=post_instance.model,
                       oversamp=30)

pl.savefig("./images/data_comparison.png")
pl.close("all")

planet_name = []
periods = {}
tcs = {}
for planet in post_instance.model.planets.values():
    planet_name.append(planet.name)
    periods[planet.name] = df_fittedval.loc[planet.P.full_name, 'value']
    tcs[planet.name] = df_fittedval.loc[planet.tc.full_name, 'value']

et.overplot_data_model(param=fitted_values, l_param_name=l_param_chainI,
                       datasim_dbf=post_instance.datasimulators,
                       dataset_db=post_instance.dataset_db,
                       model_instance=post_instance.model,
                       oversamp=30, phasefold=True,
                       phasefold_kwargs={"planets": list(periods.keys()),
                                         "P": periods.values(),
                                         "tc": tcs.values()})

pl.savefig("./images/data_comparison_pholded.png")
pl.close("all")

logger.info("9. Determine best fit values and error bars for secondary parameters")
# Compute other parameters
# Transit depth, T14, T12, b, i, omega, ecc, Mp, Rp, rho*, rhopl, a, Teff
chainIsec, l_param_name_sec = cv.get_secondary_chains(post_instance.model, chainI,
                                                      star_kwargs={"M": {"value": 1.14,
                                                                         "error": 0.09},
                                                                   "R": {"value": 1.24,
                                                                         "error": 0.18},
                                                                   "Teff": {"value": 5871,
                                                                            "error": 57}
                                                                   }
                                                      )
et.plot_chains(chainIsec, lnprobability, l_param_name_sec)
pl.savefig("./images/traces_secondary_raw.png")
pl.close("all")

et.plot_chains(chainIsec, lnprobability, l_param_name_sec, l_walker=l_walker_geweke)
pl.savefig("./images/traces_secondary_geweke_select.png")
pl.close("all")

fitted_values_sec = et.get_fitted_values(chainIsec, method="median", l_param_name=l_param_name_sec,
                                         l_walker=l_walker_geweke, l_burnin=l_burnin,
                                         lnprobability=lnprobability)
sigma_p_sec, _, sigma_m_sec = da.getconfi(et.get_clean_flatchain(chainIsec,
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

# WASP-151_b_Trdepth: 0.010200047480966635 +8.22801588479076e-05 -5.64856256899688e-05
# WASP-151_b_inc: 89.2156161472059 +0.3806621017243259 -0.438535948866587
# WASP-151_b_ecc: 0.007398190963457673 +0.009733018508697792 -0.0053476629294743555
# WASP-151_b_omega: 47.61114456825142 +27.136830910796533 -72.84694140291961
# WASP-151_b_b: 0.14080236575613306 +0.0763678000874439 -0.06797630590594453
# WASP-151_b_R: 1.2186722750222962 +0.17546007225676918 -0.1753271612119094
# WASP-151_b_D14: 3.658794746406146 +0.01133218494522037 -0.010338590418367932
# WASP-151_b_D23: 2.9710199082294793 +0.010830109592061099 -0.01435528987149537
# WASP-151_b_M: 0.33359607943288544 +0.034967554346994 -0.03395772536341912
# WASP-151_b_a: 0.056006087200705906 +0.0014289490868612878 -0.0015010069619877803
# WASP-151_b_rhostar: 0.709007024608163 +0.0221964406057803 -0.027422878911913307
# WASP-151_b_loggstar: 4.379762158573844 +0.06061398304074128 -0.06928169013651075
# WASP-151_b_circtime: 0.02144234258397114 +0.02573242852383243 -0.010644406522184839
# WASP-151_b_rho: 0.18394095611302544 +0.11237885444551263 -0.06270780661888206
# WASP-151_b_Teq: 1295.318222310002 +14.951373703595891 -14.391797881410639
# WASP-151_A_L: 1.6344839269955105 +0.5129447684550366 -0.4382785587906384
# WASP-151_b_Fi: 521.8839379373337 +166.9563422570767 -141.20756041166192
# WASP-151_b_H: 880.0620144326377 +295.8865319810071 -245.0490704409898

logger.info("10. Print best fit values and error bars in a latex file")
et.write_latex_table("latex_parameter_table.tex", df_fittedval, obj_name)

logger.info("11. Do correlation plot for secondary free parameters")
# In this case there is nan values in the D14 and D23 chains and it makes corner crash
corner(et.get_clean_flatchain(chainIsec, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_name_sec, truths=fitted_values_sec)
pl.savefig("./images/corner_sec.png")
pl.close("all")
