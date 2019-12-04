#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to analysis the chains obtained during the MCMC exploration

@TODO:
"""
from logging import DEBUG, INFO
from os import getcwd, makedirs
from os.path import join

from corner import corner
import matplotlib.pyplot as pl
# from numpy import median, zeros, where, sqrt
import numpy as np
import pandas as pd

# If needed, add lisa folder to the python path here
# lisa_folder = ".."  # Change this if needed
# if lisa_folder not in sys.path:
#     sys.path.append(lisa_folder)

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.exoplanet.exploration_analysis_tools.secondary_parameters as sp
import lisa.tools.stats.distribution_anali as da
import lisa.tools.mylogger as ml
from lisa.tools.chain_interpreter import ChainsInterpret


## Definition of the parameters
obj_name = "WASP-151"  # Change
kwargs_datasim = {}

chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
makedirs(chain_analysis_output_folder, exist_ok=True)
plot_folder = join(chain_analysis_output_folder, "plots")
makedirs(plot_folder, exist_ok=True)
chain_analysis_pickle_folder = join(chain_analysis_output_folder, "pickles")
makedirs(chain_analysis_pickle_folder, exist_ok=True)
table_folder = join(chain_analysis_output_folder, "tables")
makedirs(table_folder, exist_ok=True)

# Raw chains and hist plots
do_RP = True  # Do chain plot and histogram plot for raw chains

# Acceptance fraction selection
do_AFS = True
sig_fact_AFS = 2
quantile_AFS = 75
verbose_AFS = 1

# Ln Posterior selection
do_LPS = True
sig_fact_LPS = 2
quantile_LPS = 75
quantile_walker_LPS = 100  # For each walker get as representation ln Posterior value its quantile_walker value
verbose_LPS = 1

# Chains and hist plots after AFS and LPS
do_AFSLPSP = True  # Do chain plot and histogram plot after AFS and LPSs

# Convergence and burnin determination
do_GS = True
geweke_thres = 2.
last_perc_GS = 10  # Percentage of the chains used as final state the chains in the geweke selection.
# The rest of the chains will be used to estimate the moment when convergence is reach,
last_min_GS = 50  # Minimum number of steps to use for the final state of the chains
intervals_GS = 100  # Number of intervals in which the first percentage of the chain will be split to address convergence
min_intervals_efficiency_GS = 0.1  # Min ratio between the number of steps in each interval and the number of steps between to intervals
def_intervals_efficiency_GS = 0.5  # If interval efficiency is below min_intervals_efficiency_GS the number of intervals will be change to get this efficiency
interval_perc_GS = 50  # Percentage of the chains used in each intervals to address convergence
interval_step_min_GS = 20  # Minimum number of step in each intervals state of the chains

# Determine best fit values and error bars
do_bestfit = True
method_bestfit = "median"

# Do Corner plot
do_corner = True
sampling_corner = 10

# Do model comparison
do_MComp = True
do_MComp_Folded = True

# Do compute secondary parameters
do_SecParam = True
sampling_corner_sec = 100
units = {"K": "kms"}

# At the end of script_mcmcexploration.py the results of the MCMC exploration and the model are stored
# in pickle files. If these object are not in Memory and you want to load them from the pickle file, set
# load_from_pickle to True
load_from_pickle = False
exploration_output_folder = join(getcwd(), "outputs/exploration")
exploration_pickle_folder = join(exploration_output_folder, "pickles")

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

logger.info("########\nCHAIN ANALYSIS")

if load_from_pickle:
    logger.info("0. Load from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=exploration_pickle_folder)
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
                                                                                   folder=exploration_pickle_folder)
    print("l_param_name from posterior:\n{}".format(l_param_name_bis))
    print("l_param_name from pickle:\n{}".format(l_param_name))

nstep = chain.shape[1]
nwalker = chain.shape[0]
l_param_chainI = l_param_name + ["lnposterior"]
chainI = ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)

if do_RP:
    logger.info("1. Plot raw traces and lnpost histogram")
    et.plot_chains(chain, lnprobability, l_param_name)
    pl.savefig(join(plot_folder, "traces_raw.pdf"))
    pl.close("all")

    pl.figure()
    pl.hist(lnprobability[:, int(nstep / 2):].flatten(), bins='auto')
    pl.savefig(join(plot_folder, "lnpost_hist_raw.pdf"))
    pl.close("all")


if do_AFS:
    logger.info("2. Select walkers with acceptance_fraction and plot lnpost histogram")
    l_walker_AFS, _ = et.acceptancefraction_selection(acceptance_fraction, sig_fact=sig_fact_AFS, quantile=quantile_AFS,
                                                      verbose=verbose_AFS)
    # l_walker_acceptfrac = np.arange(nwalker)
    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_AFS)
    pl.savefig(join(plot_folder, "traces_accfrac_select.pdf"))
    pl.close("all")

    pl.figure()
    pl.hist(lnprobability[l_walker_AFS, int(nstep / 2):].flatten(), bins='auto')
    pl.savefig(join(plot_folder, "lnpost_hist_accefrac_select.pdf"))
    pl.close("all")
else:
    l_walker_AFS = np.arange(nwalker)


if do_LPS:
    logger.info("3. Select walkers with ln posterior probability and plot lnpost histogram")
    l_walker_LPS, _ = et.lnposterior_selection(lnprobability, sig_fact=sig_fact_LPS, quantile=quantile_LPS,
                                               quantile_walker=quantile_walker_LPS, verbose=verbose_LPS)
    # l_walker_lnpost = np.arange(nwalker)
    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_LPS)
    pl.savefig(join(plot_folder, "traces_lnpost_select.pdf"))
    pl.close("all")

    pl.figure()
    pl.hist(lnprobability[l_walker_LPS, int(nstep / 2):].flatten(), bins='auto')
    pl.savefig(join(plot_folder, "lnpost_hist_lnpost_select.pdf"))
    pl.close("all")
else:
    l_walker_LPS = np.arange(nwalker)


l_walker = list(set(l_walker_AFS) & set(l_walker_LPS))
if do_AFSLPSP:
    logger.info("4. Plot trace after acceptance fraction and ln posterior selection and plot lnpost "
                "histogram")
    logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
                "".format((nwalker - len(l_walker)), nwalker))
    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker)
    pl.savefig(join(plot_folder, "traces_accfrac&lnpost_select.pdf"))
    pl.close("all")

    pl.figure()
    pl.hist(lnprobability[l_walker, int(nstep / 2):].flatten(), bins='auto')
    pl.savefig(join(plot_folder, "lnpost_hist_accfrac&lnpost_select.pdf"))
    pl.close("all")

if do_GS:
    logger.info("5. Determine convergence and burnin values and plot lnpost histogram")
    last_step = nstep * last_perc_GS / 100
    if last_step < last_min_GS:
        last_step = last_min_GS
        logger.warning("The last percentage provided ({last_perc}%) correspond to a number of step ({nb_last}) "
                       "below the specified number ({last_min}). last is forced to {last_min}"
                       "".format(last_perc=last_perc_GS, nb_last=nstep * last_perc_GS, last_min=last_min_GS))
    first_step = (nstep - last_step)
    nstep_between_intervals = first_step / intervals_GS
    if nstep_between_intervals < 1:
        intervals = first_step
        logger.warning("The number of intervals provided ({intervals}) is higher than the number of steps in the "
                       "first portion of the chains ({first_step}). intervals is forced to {first_step}"
                       "".format(intervals=intervals_GS, first_step=first_step))
        nstep_between_intervals = first_step / intervals
    else:
        intervals = intervals_GS
    interval_step = nstep * interval_perc_GS / 100
    if interval_step < interval_step_min_GS:
        interval_perc = interval_step_min_GS / nstep
        logger.warning("The number of steps in each interval ({interval_step}) is below the minimum "
                       "specified ({interval_step_min}). interval_perc is forced to the corresponding "
                       "value ({interval_perc})".format(interval_step=interval_step, interval_step_min=interval_step_min_GS,
                                                        interval_perc=interval_perc))
        interval_step = nstep * interval_perc / 100
    else:
        interval_perc = interval_perc_GS
    if def_intervals_efficiency_GS < min_intervals_efficiency_GS:
        raise ValueError("def_intervals_efficiency_GS ({}) cannot be below min_intervals_efficiency_GS ({})"
                         "".format(def_intervals_efficiency_GS, min_intervals_efficiency_GS))
    interval_efficiency = interval_step / nstep_between_intervals
    if interval_efficiency < min_intervals_efficiency_GS:
        nstep_between_intervals = interval_step / def_intervals_efficiency_GS
        intervals = int(nstep / nstep_between_intervals)
        logger.warning("The interval efficiency ({interval_eff}) is below the minimum threshold (interval_eff_min). "
                       "The number of interval is forced to {intervals} to obtain an efficiency of {def_interval_eff_def}"
                       "".format(interval_eff=interval_efficiency, interval_eff_min=min_intervals_efficiency_GS, intervals=intervals, def_interval_eff_def=def_intervals_efficiency_GS))
    zscores, l_first_i_step = et.geweke_multi(chainI, first=interval_step / nstep, last=last_step / nstep,
                                              intervals=intervals, l_walker=l_walker)
    l_burnin, l_walker_conv = et.geweke_selection(zscores, first_steps=l_first_i_step, geweke_thres=geweke_thres,
                                                  l_walker=l_walker)

    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_conv,
                   l_burnin=l_burnin)
    pl.savefig(join(plot_folder, "traces_geweke_select.pdf"))
    pl.close("all")

    pl.figure()
    pl.hist(et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_conv,
                                   l_burnin=l_burnin),
            bins='auto')
    pl.savefig(join(plot_folder, "lnpost_hist_geweke_select.pdf"))
    pl.close("all")

    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_conv,
                   l_burnin=l_burnin, suppress_burnin=True)

    pl.savefig(join(plot_folder, "traces_geweke_select_burnsupress.pdf"))
    pl.close("all")
else:
    l_walker_conv = l_walker
    l_burnin = [0 for i in l_walker_conv]


if do_bestfit:
    logger.info("6. Determine best fit values and error bars for main parameters")
    fitted_values = et.get_fitted_values(chainI, method=method_bestfit, l_param_name=l_param_chainI,
                                         l_walker=l_walker_conv, l_burnin=l_burnin,
                                         lnprobability=lnprobability)

    sigma_p, _, sigma_m = da.getconfi(et.get_clean_flatchain(chainI, l_walker=l_walker_conv,
                                                             l_burnin=l_burnin),
                                      level=1, centre=fitted_values, l_param_name=l_param_chainI)

    df_fittedval = pd.DataFrame(index=l_param_chainI, data={'value': fitted_values, 'sigma-': sigma_m,
                                                            'sigma+': sigma_p})

    et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                           df_fittedval=df_fittedval, folder=chain_analysis_pickle_folder)

    et.write_latex_table(join(table_folder, "{}_latex_parameter_table.tex".format(obj_name)), df_fittedval, obj_name)


if do_corner:
    logger.info("7. Do correlation plot for main free parameters")
    corner(et.get_clean_flatchain(chainI, l_walker=l_walker_conv, l_burnin=l_burnin)[::sampling_corner, :],
           labels=l_param_chainI, truths=fitted_values)

    pl.savefig(join(plot_folder, "corner.pdf"))
    pl.close("all")


if do_MComp:
    logger.info("8. Do data comparison plots")
    et.overplot_data_model(param=fitted_values, l_param_name=l_param_chainI,
                           datasim_dbf=post_instance.datasimulators,
                           datasim_kwargs=kwargs_datasim,
                           dataset_db=post_instance.dataset_db,
                           model_instance=post_instance.model,
                           oversamp=30)

    pl.savefig(join(plot_folder, "data_comparison.pdf"))
    pl.close("all")

    if do_MComp_Folded:
        planet_name = []
        periods = {}
        tics = {}
        for planet in post_instance.model.planets.values():
            planet_name.append(planet.get_name())
            periods[planet.get_name()] = df_fittedval.loc[planet.P.get_name(include_prefix=True, recursive=True), 'value']
            tics[planet.get_name()] = df_fittedval.loc[planet.tic.get_name(include_prefix=True, recursive=True), 'value']

        et.overplot_data_model(param=fitted_values, l_param_name=l_param_chainI,
                               datasim_dbf=post_instance.datasimulators,
                               # datasim_kwargs=dict(tref_dyn=tref_dyn),
                               dataset_db=post_instance.dataset_db,
                               model_instance=post_instance.model,
                               oversamp=30, phasefold=True,
                               phasefold_kwargs={"planets": list(periods.keys()),
                                                 "P": periods.values(),
                                                 "tc": tics.values()})

        pl.savefig(join(plot_folder, "data_comparison_pholded.pdf"))
        pl.close("all")

if do_SecParam:
    logger.info("9. Determine best fit values and error bars for secondary parameters")
    chainIsec, l_param_name_sec = sp.get_secondary_chains(post_instance.model, chainI,
                                                          # star_kwargs={"M": {"value": 1.20,
                                                          #                    "error": 0.09},
                                                          #              "R": {"value": 1.18,
                                                          #                    "error": 0.20},
                                                          #              "Teff": {"value": 5914,
                                                          #                       "error": 64}
                                                          #              },
                                                          star_kwargs={"M": {"value": 1.336,
                                                                             "error": 0.086},
                                                                       "rho": {"value": 0.26,
                                                                               "error": 0.04},
                                                                       "Teff": {"value": 5914,
                                                                                "error": 64}
                                                                       },
                                                          # star_kwargs={"M": {"value": 1.295,
                                                          #                    "error": 0.077},
                                                          #              "R": {"value": 1.59,
                                                          #                    "error": 0.09},
                                                          #              "Teff": {"value": 5914,
                                                          #                       "error": 64}
                                                          #              },
                                                           units=units
                                                          )
    logger.info("Plot raw traces for secondary parameters")
    et.plot_chains(chainIsec, lnprobability, l_param_name_sec)
    pl.savefig(join(plot_folder, "traces_secondary_raw.pdf"))
    pl.close("all")

    logger.info("Plot geweke select traces for secondary parameters")
    et.plot_chains(chainIsec, lnprobability, l_param_name_sec, l_walker=l_walker_conv, l_burnin=l_burnin)
    pl.savefig(join(plot_folder, "traces_secondary_geweke_select.pdf"))
    pl.close("all")

    logger.info("Determine best fit values and error bars for secondary parameters")
    fitted_values_sec = et.get_fitted_values(chainIsec, method="median", l_param_name=l_param_name_sec,
                                             l_walker=l_walker_conv, l_burnin=l_burnin,
                                             lnprobability=lnprobability)
    sigma_p_sec, _, sigma_m_sec = da.getconfi(et.get_clean_flatchain(chainIsec,
                                                                     l_walker=l_walker_conv,
                                                                     l_burnin=l_burnin),
                                              level=1, centre=fitted_values_sec,
                                              l_param_name=l_param_name_sec)
    df_fittedval = pd.concat([df_fittedval, pd.DataFrame(index=l_param_name_sec,
                                                         data={'value': fitted_values_sec,
                                                               'sigma-': sigma_m_sec,
                                                               'sigma+': sigma_p_sec})])
    df_fittedval = df_fittedval[~df_fittedval.index.duplicated(keep='last')]

    et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                           fitted_values_sec={"array": fitted_values_sec, "l_param": l_param_name_sec},
                           df_fittedval=df_fittedval, folder=chain_analysis_pickle_folder)

    et.write_latex_table(join(table_folder, "{}_latex_parameter_table_wsecondary.tex".format(obj_name)), df_fittedval, obj_name)

    logger.info("Do correlation plot for secondary free parameters")
    # In this case there is nan values in the D14 and D23 chains and it makes corner crash
    corner(et.get_clean_flatchain(chainIsec, l_walker=l_walker_conv, l_burnin=l_burnin)[::sampling_corner_sec, :],
           labels=l_param_name_sec, truths=fitted_values_sec)
    pl.savefig(join(plot_folder, "corner_sec.pdf"))
    pl.close("all")
