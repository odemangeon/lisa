#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to analysis the chains obtained during the MCMC exploration

@TODO:
"""
from logging import DEBUG, INFO
from os import getcwd
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
from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.plot import hist_lnprob


## Definition of the parameters
obj_name = "WASP-151"  # Change
kwargs_datasim = {}
star_kwargs = {"M": {"value": 1.077,
                     "error": 0.081},
               "R": {"value": 1.14,
                     "error": 0.03},
               "Teff": {"value": 5871,
                        "error": 57}
               }

output_folders = get_def_output_folders(run_folder=getcwd())

# At the end of script_mcmcexploration.py the results of the MCMC exploration and the model are stored
# in pickle files. If these object are not in Memory and you want to load them from the pickle file, set
# load_from_pickle to True
load_from_pickle = True

# Save plots ?
save_plots = True

# Histograms Parameters
hist_perc = 10  # The histogram of the ln posterior probability will only be done for the last X% of the chains
n_bins = 1000  # Defin the number of bins in the histograms of the lnposterior is 'auto' cannot be used. (Sometimes auto just takes too much time)
do_hist = True  # Histograms can be very long to produce when the values are very widely spread. So in some cases, it can save you a lot of time

# Raw chains and hist plots
do_RP = True  # Do chain plot and histogram plot for raw chains

# Acceptance fraction selection
do_AFS = True
sig_fact_AFS = 2
quantile_AFS = 75
verbose_AFS = 1
plot_hist_AF = True

# Ln Posterior selection
do_LPS = True
sig_fact_LPS = 2
quantile_LPS = 75
quantile_walker_LPS = 100  # For each walker get as representation ln Posterior value its quantile_walker value
verbose_LPS = 1
plot_hist_Post = True

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
do_geweke_plot = True

# Determine best fit values and error bars
do_bestfit = True
method_bestfit = "median"
save_results_bestfit = True

# Do Corner plot
do_corner = True
sampling_corner = 10

# Do model comparison
do_MComp = True
do_MComp_Folded = True
oversamp_MComp = 30

# Do compute secondary parameters
do_SecParam = True
sampling_corner_sec = 100
units = {"K": "kms"}
omega_0to360 = True
save_results_bestfit_secpar = True

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

logger.info("########\nCHAIN ANALYSIS")

if load_from_pickle:
    logger.info("0. Load from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=output_folders["pickles_explore"])
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
                                                                                   folder=output_folders["pickles_explore"])
    print("l_param_name from posterior:\n{}".format(l_param_name_bis))
    print("l_param_name from pickle:\n{}".format(l_param_name))

nstep = chain.shape[1]
nwalker = chain.shape[0]
l_param_chainI = l_param_name + ["lnposterior"]
chainI = ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)

if do_RP:
    logger.info("1. Plot raw traces and lnpost histogram")
    et.plot_chains(chain, lnprobability, l_param_name)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_raw.pdf"))
    else:
        pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[:, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10 = hist_lnprob(lnprob_val, n_bins=n_bins)
        ax.set_title(f"Histogram of the last {hist_perc}% of the RAW lnprobability")
        if save_plots:
            pl.savefig(join(output_folders["plots"], "lnpost_hist_raw.pdf"))
        else:
            pl.show()
        pl.close("all")

if do_AFS:
    logger.info("2. Select walkers with acceptance_fraction and plot lnpost histogram")
    l_walker_AFS, _ = et.acceptancefraction_selection(acceptance_fraction, sig_fact=sig_fact_AFS, quantile=quantile_AFS,
                                                      verbose=verbose_AFS, plot=plot_hist_AF)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "hist_accept_frac.pdf"))
    else:
        pl.show()
    pl.close("all")
    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_AFS)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_accfrac_select.pdf"))
    else:
        pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker_AFS, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10 = hist_lnprob(lnprob_val, n_bins=n_bins)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low acceptance chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], "lnpost_hist_accefrac_select.pdf"))
        else:
            pl.show()
        pl.close("all")
else:
    l_walker_AFS = np.arange(nwalker)


if do_LPS:
    logger.info("3. Select walkers with ln posterior probability and plot lnpost histogram")
    l_walker_LPS, _ = et.lnposterior_selection(lnprobability, sig_fact=sig_fact_LPS, quantile=quantile_LPS,
                                               quantile_walker=quantile_walker_LPS, verbose=verbose_LPS,
                                               plot=plot_hist_Post)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "hist_lnpost_select.pdf"))
    else:
        pl.show()
    pl.close("all")
    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_LPS)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_lnpost_select.pdf"))
    else:
        pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker_LPS, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10 = hist_lnprob(lnprob_val, n_bins=n_bins)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], "lnpost_hist_lnpost_select.pdf"))
        else:
            pl.show()
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
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_accfrac&lnpost_select.pdf"))
    else:
        pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10 = hist_lnprob(lnprob_val, n_bins=n_bins)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior and acceptance chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], "lnpost_hist_accfrac&lnpost_select.pdf"))
        else:
            pl.show()
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
    if do_geweke_plot:
        et.geweke_plot(zscores, first_steps=l_first_i_step, l_param_name=l_param_chainI, geweke_thres=geweke_thres,
                       plot_height=2, plot_width=8)
        if save_plots:
            pl.savefig(join(output_folders["plots"], "geweke_plot.pdf"))
        else:
            pl.show()
        pl.close("all")

    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_conv,
                   l_burnin=l_burnin)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_geweke_select.pdf"))
    else:
        pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = et.get_clean_flatchain(chainI[:, :, "lnposterior"], l_walker=l_walker_conv,
                                            l_burnin=l_burnin)
        ax, did_log10 = hist_lnprob(lnprob_val, n_bins=n_bins)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior and acceptance chains and burnin")
        if save_plots:
            pl.savefig(join(output_folders["plots"], "lnpost_hist_geweke_select.pdf"))
        else:
            pl.show()
        pl.close("all")

    et.plot_chains(chain, lnprobability, l_param_name, l_walker=l_walker_conv,
                   l_burnin=l_burnin, suppress_burnin=True)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_geweke_select_burnsupress.pdf"))
    else:
        pl.show()
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

    if save_results_bestfit:
        et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                               df_fittedval=df_fittedval, folder=output_folders["pickles_analyze"])

        et.write_latex_table(join(output_folders["tables"], "{}_latex_parameter_table.tex".format(obj_name)), df_fittedval, obj_name)


if do_corner:
    logger.info("7. Do correlation plot for main free parameters")
    corner(et.get_clean_flatchain(chainI, l_walker=l_walker_conv, l_burnin=l_burnin)[::sampling_corner, :],
           labels=l_param_chainI, truths=fitted_values)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "corner.pdf"))
    else:
        pl.show()
    pl.close("all")


if do_MComp:
    logger.info("8. Do data comparison plots")
    et.overplot_data_model(param=fitted_values, l_param_name=l_param_chainI,
                           datasim_dbf=post_instance.datasimulators,
                           datasim_kwargs=kwargs_datasim,
                           dataset_db=post_instance.dataset_db,
                           model_instance=post_instance.model,
                           oversamp=oversamp_MComp)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "data_comparison.pdf"))
    else:
        pl.show()
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
                               datasim_kwargs=kwargs_datasim,
                               dataset_db=post_instance.dataset_db,
                               model_instance=post_instance.model,
                               oversamp=oversamp_MComp, phasefold=True,
                               phasefold_kwargs={"planets": list(periods.keys()),
                                                 "P": periods.values(),
                                                 "tc": tics.values()})
        if save_plots:
            pl.savefig(join(output_folders["plots"], "data_comparison_pholded.pdf"))
        else:
            pl.show()
        pl.close("all")

if do_SecParam:
    logger.info("9. Determine best fit values and error bars for secondary parameters")
    chainIsec, l_param_name_sec = sp.get_secondary_chains(post_instance.model, chainI,
                                                          star_kwargs=star_kwargs,
                                                          units=units
                                                          )
    if omega_0to360:
        # Change the range of omega from -180 to 180 to 0 to 360, because omega seems to be centered around 180.
        mask = np.zeros_like(chainIsec).astype(bool)
        for plnt in list(periods.keys()):
            mask[:, :, chainIsec.paramname_idx[f"{obj_name}_{plnt}_omega"]] = (chainIsec[:, :, f"{obj_name}_{plnt}_omega"] < 0)
            chainIsec[mask] = chainIsec[mask] + 360

    logger.info("Plot raw traces for secondary parameters")
    et.plot_chains(chainIsec, lnprobability, l_param_name_sec)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_secondary_raw.pdf"))
    else:
        pl.show()
    pl.close("all")

    logger.info("Plot geweke select traces for secondary parameters")
    et.plot_chains(chainIsec, lnprobability, l_param_name_sec, l_walker=l_walker_conv, l_burnin=l_burnin)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "traces_secondary_geweke_select.pdf"))
    else:
        pl.show()
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

    if save_results_bestfit_secpar:
        et.save_chain_analysis(obj_name, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                               fitted_values_sec={"array": fitted_values_sec, "l_param": l_param_name_sec},
                               df_fittedval=df_fittedval, folder=output_folders["pickles_analyze"])

        et.write_latex_table(join(output_folders["tables"], "{}_latex_parameter_table_wsecondary.tex".format(obj_name)), df_fittedval, obj_name)

    logger.info("Do correlation plot for secondary free parameters")
    # In this case there is nan values in the D14 and D23 chains and it makes corner crash
    corner(et.get_clean_flatchain(chainIsec, l_walker=l_walker_conv, l_burnin=l_burnin)[::sampling_corner_sec, :],
           labels=l_param_name_sec, truths=fitted_values_sec)
    if save_plots:
        pl.savefig(join(output_folders["plots"], "corner_sec.pdf"))
    else:
        pl.show()
    pl.close("all")
