#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to analysis the chains obtained during the MCMC exploration

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


## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format("WASP-153"))

logger.info("########\nCHAIN ANALYSIS")

load_from_pickle = True

if load_from_pickle:
    logger.info("0. Load from pickle")
    obj_name = "WASP-153"
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
chainI = et.ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)

logger.info("1. Plot raw traces and lnpost histogram")
et.plot_chains(chain, lnprobability, l_param_name)
pl.savefig("./images/traces_raw.pdf")
pl.close("all")

pl.figure()
pl.hist(lnprobability[:, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_raw.pdf")
pl.close("all")

logger.info("2. Select walkers with acceptance_fraction and plot lnpost histogram")
l_walker_acceptfrac, _ = et.acceptancefraction_selection(acceptance_fraction,
                                                         sig_fact=2, quantile=50, verbose=1)
# l_walker_acceptfrac = np.arange(nwalker)
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_acceptfrac)
pl.savefig("./images/traces_accfrac_select.pdf")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker_acceptfrac, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_accefrac_select.pdf")
pl.close("all")

logger.info("3. Select walkers with ln posterior probability and plot lnpost histogram")
l_walker_lnpost, _ = et.lnposterior_selection(lnprobability, sig_fact=2, quantile=75,
                                              quantile_walker=90, verbose=1)
# l_walker_lnpost = np.arange(nwalker)
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_lnpost)
pl.savefig("./images/traces_lnpost_select.pdf")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker_lnpost, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_lnpost_select.pdf")
pl.close("all")

logger.info("4. Plot trace after acceptance fraction and ln posterior selection and plot lnpost "
            "histogram")
l_walker = list(set(l_walker_acceptfrac) & set(l_walker_lnpost))
# l_walker = l_walker_acceptfrac
logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
            "".format((nwalker - len(l_walker)), nwalker))
et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker)
pl.savefig("./images/traces_accfrac&lnpost_select.pdf")
pl.close("all")

pl.figure()
pl.hist(lnprobability[l_walker, int(nstep / 2):].flatten(), bins='auto')
pl.savefig("./images/lnpost_hist_accfrac&lnpost_select.pdf")
pl.close("all")

logger.info("5. Determine convergence and burnin values and plot lnpost histogram")
first_length = 50
zscores, first_steps = et.geweke_multi(chainI, first=10 * first_length / nstep, last=0.10,
                                       intervals=int(nstep / first_length), l_walker=l_walker)
l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=2.,
                                                l_walker=l_walker)

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin)
pl.savefig("./images/traces_geweke_select.pdf")
pl.close("all")

pl.figure()
pl.hist(et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_geweke,
                               l_burnin=l_burnin),
        bins='auto')
pl.savefig("./images/lnpost_hist_geweke_select.pdf")
pl.close("all")

et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_geweke,
               l_burnin=l_burnin, suppress_burnin=True)

pl.savefig("./images/traces_geweke_select_burnsupress.pdf")
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

# WASP_default_jitter: -0.05608036418108014 +0.008294545567719781 -0.007712879576845542
# A_LDR_ldc1: 0.4859368857875742 +0.002080629507138443 -0.0020914691894657333
# A_LDR_ldc2: 0.12611378532002132 +0.0052337364913462026 -0.005057118681620967
# WASP-153_b_secosw: 0.004207724387072152 +0.050463402411085045 -0.051477492818537154
# WASP-153_b_sesinw: -0.0008025583347145288 +0.04717895627033512 -0.04758213544993055
# WASP-153_b_cosinc: 0.10240153218910314 +0.011555254562796408 -0.011856919784801037
# WASP-153_b_tc: 53142.54178717672 +0.0030000586702954024 -0.002941706552519463
# WASP-153_b_P: 3.3326087548722105 +2.2716078942330853e-06 -2.3524736354474385e-06
# WASP-153_b_Rrat: 0.09240177900812899 +0.0011049739601065312 -0.0011060615367055326
# WASP-153_b_aR: 6.026009437588692 +0.26339221205403174 -0.2484361035721081
# Liverpool_default_jitter: -1.599615969028475 +0.005633136775220926 -0.005924286371022713
# RISE2_default_jitter: -0.8110257493051454 +0.019535400010825876 -0.018601108427895086
# A_LDVR_ldc1: 0.5487569793978067 +0.0024110999288349255 -0.0024462094833065384
# A_LDVR_ldc2: 0.11761519062914923 +0.006149628972109342 -0.005976909333182137
# SOPHIE_default_jitter: 0.038934140946337924 +0.04162245667797162 -0.04469023497426298
# WASP-153_A_v0: -29.00437548354968 +0.0015339594667835854 -0.0014848621936351947
# WASP-153_b_K: 0.04411787713995913 +0.0019663380105228653 -0.002052766941333918
# lnposterior: 101678.0382416834 +2.528399233298842 -3.2119342899968615

logger.info("7. Do correlation plot for main free parameters")
corner(et.get_clean_flatchain(chainI, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_chainI, truths=fitted_values)

pl.savefig("./images/corner.pdf")
pl.close("all")


logger.info("8. Do data comparision plots")
et.overplot_data_model(fitted_values, l_param_chainI,
                       post_instance.datasimulators, post_instance.dataset_db,
                       post_instance.noisemodels.dataset_db,
                       oversamp=30)

pl.savefig("./images/data_comparison.pdf")
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

pl.savefig("./images/data_comparison_pholded.pdf")
pl.close("all")

logger.info("9. Determine best fit values and error bars for secondary parameters")
# Compute other parameters
# Transit depth, T14, T12, b, i, omega, ecc, Mp, Rp, rho*, rhopl, a, Teff
chainIsec, l_param_name_sec = cv.get_secondary_chains(post_instance.model, chainI,
                                                      # star_kwargs={"M": {"value": 1.20,
                                                      #                    "error": 0.09},
                                                      #              "R": {"value": 1.18,
                                                      #                    "error": 0.20},
                                                      #              "Teff": {"value": 5914,
                                                      #                       "error": 64}
                                                      star_kwargs={"M": {"value": 1.336,
                                                                         "error": 0.086},
                                                                   "rho": {"value": 0.26,
                                                                           "error": 0.04},
                                                                   "Teff": {"value": 5914,
                                                                            "error": 64}
                                                      # star_kwargs={"M": {"value": 1.295,
                                                      #                    "error": 0.077},
                                                      #              "R": {"value": 1.59,
                                                      #                    "error": 0.09},
                                                      #              "Teff": {"value": 5914,
                                                      #                       "error": 64}
                                                                   })
et.plot_chains(chainIsec, lnprobability, l_param_name_sec)
pl.savefig("./images/traces_secondary_raw.pdf")
pl.close("all")

et.plot_chains(chainIsec, lnprobability, l_param_name_sec, l_walker=l_walker_geweke)
pl.savefig("./images/traces_secondary_geweke_select.pdf")
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
df_fittedval = df_fittedval[~df_fittedval.index.duplicated(keep='last')]
df_fittedval.to_pickle("df_fittedval.pk")

et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                       fitted_values_sec={"array": fitted_values_sec, "l_param": l_param_name_sec},
                       df_fittedval=df_fittedval)

# WASP-153_b_Trdepth: 0.008538088763867106 +0.00020542408679551614 -0.00020318073524512245
# WASP-153_b_inc: 84.1225217607033 +0.6825392313703134 -0.665979534922954
# WASP-153_b_ecc: 0.0033990718291421616 +0.005520731364467126 -0.0025329939423387416
# WASP-153_b_omega: -3.955444787325508 +61.53785817858588 -57.0009957067487
# WASP-153_b_b: 0.6169465330850246 +0.041238881168653596 -0.04800386002853796
# WASP-153_b_R: 1.0596844922242181 +0.180827796496567 -0.17748837992010924
# WASP-153_b_D14: 3.843964405466575 +0.049981015222190006 -0.047693356302539236
# WASP-153_b_D23: 2.8340111822120972 +0.05715080850552123 -0.06574816396710625
# WASP-153_b_M: 0.3674543071471764 +0.024732578285066975 -0.024686072486448274
# WASP-153_b_a: 0.04640199999882384 +0.0011283345814186302 -0.001178238335060068
# WASP-153_b_rhostar: 0.26414789221133894 +0.03617351912428168 -0.0313416132202875
# WASP-153_b_loggstar: 3.929353286055247 +0.08861919746365832 -0.09605060694000311
# WASP-153_b_circtime: 0.012989572994406912 +0.019693629258676643 -0.007127536295047438
# WASP-153_b_rho: 0.3083157968082852 +0.22847233176117182 -0.11702593564740332
# WASP-153_b_Teq: 1703.146385670194 +40.889072273823786 -39.85818512661103
# WASP-153_A_L: 1.5218236670480296 +0.5709452502062367 -0.4684523032844745
# WASP-153_b_Fi: 707.9792904668624 +268.71313219752903 -219.5261182155533
# WASP-153_b_H: 793.8224148569486 +303.85770703815274 -247.57514010178704

# WASP-153_b_Trdepth: 0.008538088763867106 +0.00020542408679551614 -0.00020318073524512245
# WASP-153_b_inc: 84.1225217607033 +0.6825392313703134 -0.665979534922954
# WASP-153_b_ecc: 0.0033990718291421616 +0.005520731364467126 -0.0025329939423387416
# WASP-153_b_omega: -3.955444787325508 +61.53785817858588 -57.0009957067487
# WASP-153_b_b: 0.6169465330850246 +0.041238881168653596 -0.04800386002853796
# WASP-153_b_R: 1.5514567801326211 +0.0952877797210685 -0.08112263956832311
# WASP-153_b_D14: 3.843964405466575 +0.049981015222190006 -0.047693356302539236
# WASP-153_b_D23: 2.8340111822120972 +0.05715080850552123 -0.06574816396710625
# WASP-153_b_M: 0.39479034696911985 +0.02471735774765227 -0.024541569806312502
# WASP-153_b_a: 0.04809554208659214 +0.0010055161817508623 -0.0010491220970182125
# WASP-153_b_rhostar: 0.26414789221133894 +0.03617351912428168 -0.0313416132202875
# WASP-153_b_loggstar: 4.097976075311807 +0.06079435908749975 -0.06001690165950535
# WASP-153_b_circtime: 0.002233840753660067 +0.0006325489476665552 -0.0005565679230257309
# WASP-153_b_rho: 0.10565261836555431 +0.0177605181354627 -0.017086825130659095
# WASP-153_b_Teq: 1703.1388950137223 +40.88901417180546 -40.00745993657847
# WASP-153_A_L: 3.266943732199924 +0.4326072961308789 -0.3522994430881421
# WASP-153_b_Fi: 1412.4328162000616 +177.42521081134828 -140.217658252315
# WASP-153_b_H: 1585.77524009763 +215.28879820521888 -172.5410261422387
# WASP-153_A_R: 1.7259112326099997 +0.1039730871358806 -0.08825432367172792

logger.info("10. Print best fit values and error bars in a latex file")
et.write_latex_table("latex_parameter_table.tex", df_fittedval, obj_name)

logger.info("11. Do correlation plot for secondary free parameters")
# In this case there is nan values in the D14 and D23 chains and it makes corner crash
corner(et.get_clean_flatchain(chainIsec, l_walker=l_walker_geweke, l_burnin=l_burnin),
       labels=l_param_name_sec, truths=fitted_values_sec)
pl.savefig("./images/corner_sec.pdf")
pl.close("all")
