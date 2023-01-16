#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to analysis the chains obtained during the MCMC exploration

@TODO:
"""
import gc

from logging import DEBUG, INFO
from os import getcwd
from os.path import join
from unittest import TestCase

import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
import astropy.units as uu

from corner import corner

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
# from lisa.posterior.exoplanet.model.gravgroup.datasim_creator_rv import RVdrift_tref_name

###############################
## Definition of the parameters
###############################
obj_name = "WASP-151"  # Change
kwargs_datasim = {}
star_kwargs = {"M": {"value": 1.077,
                     "error": 0.081},
               "R": {"value": 1.14,
                     "error": 0.03},
               "Teff": {"value": 5871,
                        "error": 57}
               }

output_folders = get_def_output_folders(run_folder=getcwd())  # Folder for the outputs

# At the end of script_mcmcexploration.py the results of the MCMC exploration and the model are stored
# in pickle files. If these object are not in Memory and the code will load them from the pickle file
extension_exploration = "_initrun"  # extension of your exploration (Needs to be the same than in you script_mcmcexploration)

# Save plots ?
save_plots = True  # Save all the plots.
extension_outputs = "_initrun_median"  # extension of this chain analysis (will be added to the ouput files).

# Common parameters for the plots of histograms of the lnposterior and the trace plots
hist_perc = 10  # For the histogram after the acceptance fraction and the ln posterior selections
# the histograms of the ln posterior probability will only be done for the last hist_perc% of the chains
# After the Geweke selection, 10% of the sample, uniformly spread will be selected.n_bins = 1000  # Defin the number of bins in the histograms of the lnposterior is 'auto' cannot be used. (Sometimes auto just takes too much time)
sigma_clip_hist = None  # If not None, a sigma clipping will be done on the histogram of the lnposterior before plotting (can avoid to have to waiting a very long time for your histogram)
n_bins = 1000  # Define the number of bins in the histograms of the lnposterior. Can also be 'auto' but sometimes auto just takes too much time.
do_hist = False  # Histograms of the lnposteriors can be very long to produce when the values are very widely spread. So in some cases, it can save you a lot of time not to do them at first
do_traces = False  # Trace plots can also be very long to produce. So in some cases, it can save you a lot of time not to do them at first

# Raw trace plots and hist of the lnposterior
do_RP = False  # Do chain trace plot and histogram of the lnposterior plot for raw chains
thin_RP = 100  # thining factor for the traces plots

# Acceptance fraction selection
# The idea for this step is to remove the chains whose acceptance fraction is too low compared to the rest.
# To use with caution !
# All chain whose acceptance fraction is < quantile_AFS - sig_fact_AFS * MAD(Acceptance fraction of all chains) will be removed
do_AFS = True  # Do the acceptance fraction selection
sig_fact_AFS = 5  # Sigma clipping value.
quantile_AFS = 75  # Quantile of the acceptance fraction of all chains that you want to use as reference
verbose_AFS = 1  # More outputs on screen
plot_hist_AF = True  # Do the diagnostic plot for this step.
thin_AFS = 100  # Thining factor for the trace plots

# Ln Posterior selection
# The idea for this step is to remove the chains whose final lnposterior value is too low compared to the rest.
# So remove unconverged chains or local minima with lower posterior values.
# To use with caution !
# The value of the lnposterior obtianed by each chain will be the quantile (quantile_walker_LPS) of the posterior values of the chain.
# Then all chain whose lnposterior is < quantile_LPS(quantile_walkers_LPS) - sig_fact_LPS * MAD(quantile_walkers_LPS) will be removed
do_LPS = True  # Do the ln posterior selection
sig_fact_LPS = 6  # Sigma clipping value.
quantile_LPS = 100  # Quantile of the quantile_walker_LPS of all chains that you want to use as reference
quantile_walker_LPS = 100  # Each walker get as representation lnposterior value the quantile_walker_LPS quantile of it lnposterior chain
verbose_LPS = 1   # More outputs on screen
plot_hist_Post = True  # Do the diagnostic plot for this step.
thin_LPS = 100  # Thining factor for the trace plots

# Trace plots and hist of the lnposterior after AFS and LPS
do_AFSLPSP = False  # Do chain plot and histogram plot after AFS and LPSs
thin_AFSLPSP = 100

# Convergence and burnin determination
# The idea of this step is to determine the burnin fraction of this chain
# The chain by chain geweke selection algorithm is not always suited to identify stationarity so you have to use it as a diagnostic not as an automatic black box tool.
# Do the analysis in two steps.
# 1. do_GS = True and apply_min_burnin = False
# 2. Identify the burning thanks to the geweke plot
# 3. do_GS = False and apply_min_burnin = True with min_burnin = the burnin that you identified
do_GS = False  # Do the geweke selection diagnostic
geweke_thres = 2.  # Geweke threshold
last_perc_GS = 10  # Percentage of the chains used as final state the chains in the geweke selection.
# The rest of the chains will be used to estimate the moment when convergence is reach,
last_minstep_GS = 50  # Minimum number of steps to use for the final state of the chains
intervals_GS = 100  # Number of intervals in which the first percentage of the chain will be split to address convergence
min_intervals_efficiency_GS = 0.1  # Min ratio between the number of steps in each interval and the number of steps between to intervals
def_intervals_efficiency_GS = 0.5  # If interval efficiency is below min_intervals_efficiency_GS the number of intervals will be change to get this efficiency
interval_perc_GS = 5  # Percentage of the chains used in each intervals to address convergence
interval_step_min_GS = 20  # Minimum number of step in each intervals state of the chains
do_geweke_plot = True  # Do the diagnostic plot. It's your diagnotic to determine the burnin. Do it !
do_hist_after_geweke = True  # Do the histogram of the lnposterior
extra_burnin_4_hist_after_geweke = 0  # apply an an extra burnin to the values identified by the geweke algorithm before doing the lnposterior histogram
sigma_clip_hist_after_geweke = 5  # Sigma clipping for the histogram of the lnposterior
apply_min_burnin = False  # Will apply a given burnin to all chains even if you did the geweke selection first
min_burnin = 100  # Valeu of the burnin to use
thin_GS = 100  # Thining factor for the trace plots

# Parameter based walker selection
# If you have multiple maxima even after all the selection you can use this two separate them
# USe at yuor own risks
do_PS = False
parameters = ["WASP-151_b_ecosw", "WASP-151_b_esinw"]


def inferior(array, value):
    return array < value


def superior(array, value):
    return array > value


select_func = [inferior, superior]
select_arg = [(0.50, ), (0.57, )]
perc_select = 75
plot_hist_PS = True

# Save l_walkers and l_burnin
save_walkersandburnins = True  # Save the walkers selection and burnin values

# Determine best fit values and error bars
do_bestfit = False
method_bestfit = "median"  # Method to use to determine the best values for the parameter. Can be 'median' or 'MAP'
save_results_bestfit = True

# Do Corner plot
do_corner = False
sampling_corner = 100  # thining factor for the corner plot

# Do model comparison
do_MComp = False
oversamp_MComp = 30
load_fitted_val_pickle = False
save_modelsNresiduals = True

# Do compute secondary parameters
do_SecParam = False
force_finite = False
units = {"K": "kms"}
units_dict = {"K": uu.km / uu.s}
omega_0to360 = False
save_results_bestfit_secpar = True
do_corner_sec = True
sampling_corner_sec = 500
thin_SecParam = 100

# Do computation of the BIC
do_compute_BIC = False
load_fitted_val_pickle_BIC = False
only_bestfit_bic = True

##########################
## Execution of the script
##########################

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file=join(output_folders["log"], f"{obj_name}.log"))

# Set matplotlib rcparams to the default value to avoid issues with plots
matplotlib.rcParams.update(matplotlib.rcParamsDefault)

logger.info("########\nCHAIN ANALYSIS")

if any([var not in globals() for var in ["post_instance", "lnprobability", "acceptance_fraction", "l_param_name"]]):
    logger.info("0. Load from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=output_folders["pickles_explore"])
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].param_model_names_list
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name, extension_exploration=extension_exploration,
                                                                                   folder=output_folders["pickles_explore"])
    tc = TestCase()
    tc.assertCountEqual(l_param_name_bis, l_param_name)

if "chainI" not in globals():
    nstep = chain.shape[1]
    nwalker = chain.shape[0]
    lnprobability_name = "lnposterior"
    l_param_chainI = l_param_name + [lnprobability_name]
    chainI = ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)
    del chain
    gc.collect()

if do_RP:
    logger.info("1. Plot raw traces and lnpost histogram")
    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, thin=thin_RP)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_raw{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[:, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10, nb_point_sigma_clip = hist_lnprob(lnprob_val, n_bins=n_bins, sigma_clip=sigma_clip_hist)
        ax.set_title(f"Histogram of the last {hist_perc}% of the RAW lnprobability")
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"lnpost_hist_raw{extension_outputs}.pdf"))
        else:
            pl.show()
        pl.close("all")

if do_AFS:
    logger.info("2. Select walkers with acceptance_fraction and plot lnpost histogram")
    l_walker_AFS, _ = et.acceptancefraction_selection(acceptance_fraction, sig_fact=sig_fact_AFS, quantile=quantile_AFS,
                                                      verbose=verbose_AFS, plot=plot_hist_AF)
    if save_plots:
        pl.savefig(join(output_folders["plots"], f"hist_accept_frac{extension_outputs}.pdf"))
    else:
        pl.show()
    pl.close("all")
    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker_AFS, thin=thin_AFS)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_accfrac_select{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker_AFS, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10, nb_point_sigma_clip = hist_lnprob(lnprob_val, n_bins=n_bins, sigma_clip=sigma_clip_hist)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low acceptance chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"lnpost_hist_accefrac_select{extension_outputs}.pdf"))
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
        pl.savefig(join(output_folders["plots"], f"hist_lnpost_select_{quantile_walker_LPS}-{quantile_LPS}{extension_outputs}.pdf"))
    else:
        pl.show()
    pl.close("all")
    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker_LPS, thin=thin_LPS)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_lnpost_select{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker_LPS, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10, nb_point_sigma_clip = hist_lnprob(lnprob_val, n_bins=n_bins, sigma_clip=sigma_clip_hist)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"lnpost_hist_lnpost_select{extension_outputs}.pdf"))
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
    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker, thin=thin_AFSLPSP)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_accfrac&lnpost_select{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    if do_hist:
        lnprob_val = lnprobability[l_walker, int(nstep * (1 - hist_perc / 100)):].flatten()
        ax, did_log10, nb_point_sigma_clip = hist_lnprob(lnprob_val, n_bins=n_bins, sigma_clip=sigma_clip_hist)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior and acceptance chains")
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"lnpost_hist_accfrac&lnpost_select{extension_outputs}.pdf"))
        else:
            pl.show()
        pl.close("all")

if do_GS:
    logger.info("5. Determine convergence and burnin values and plot lnpost histogram")
    last_step = nstep * last_perc_GS / 100
    if last_step < last_minstep_GS:
        last_step = last_minstep_GS
        logger.warning("The last percentage provided ({last_perc}%) correspond to a number of step ({nb_last}) "
                       "below the specified number ({last_min}). last is forced to {last_min}"
                       "".format(last_perc=last_perc_GS, nb_last=nstep * last_perc_GS, last_min=last_minstep_GS))
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
        interval_perc = interval_step_min_GS / nstep * 100
        logger.warning(f"The number of steps in each interval ({interval_step}) is below the minimum "
                       f"specified ({interval_step_min_GS}). interval_perc is forced to the corresponding "
                       f"value ({interval_perc})")
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
        logger.warning(f"The interval efficiency ({interval_efficiency}) is below the minimum threshold ({min_intervals_efficiency_GS}). "
                       f"The number of interval is forced to {intervals} to obtain an efficiency of {def_intervals_efficiency_GS}"
                       )
    zscores, l_first_i_step = et.geweke_multi(chainI, first=interval_step / nstep, last=last_step / nstep,
                                              intervals=intervals, l_walker=l_walker)
    l_burnin, l_walker_conv = et.geweke_selection(zscores, first_steps=l_first_i_step, geweke_thres=geweke_thres,
                                                  l_walker=l_walker)

    if apply_min_burnin:
        logger.info(f"Mininum burnin of {min_burnin} applied.")
        for ii in range(len(l_burnin)):
            if l_burnin[ii] < min_burnin:
                l_burnin[ii] = min_burnin

    if do_geweke_plot:
        et.geweke_plot(zscores, first_steps=l_first_i_step, l_param_name=l_param_chainI, geweke_thres=geweke_thres,
                       plot_height=2, plot_width=8)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"geweke_plot{extension_outputs}.pdf"))
        else:
            pl.show()
        pl.close("all")
    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker_conv,
                       l_burnin=l_burnin, thin=thin_GS)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_geweke_select{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    if do_hist and do_hist_after_geweke:
        if extra_burnin_4_hist_after_geweke > 0:
            l_burnin_hist_geweke = [bur + extra_burnin_4_hist_after_geweke for bur in l_burnin]
        else:
            l_burnin_hist_geweke = l_burnin
        lnprob_val = et.get_clean_flatchain(chainI[:, :, lnprobability_name], l_walker=l_walker_conv,
                                            l_burnin=l_burnin_hist_geweke)
        ax, did_log10, nb_point_sigma_clip = hist_lnprob(lnprob_val, n_bins=n_bins, sigma_clip=sigma_clip_hist_after_geweke)
        ax.set_title(f"Histogram of the last {hist_perc}% of the lnprobability clean from low posterior and acceptance chains and burnin")
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"lnpost_hist_geweke_select{extension_outputs}.pdf"))
        else:
            pl.show()
        pl.close("all")

    if do_traces:
        et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker_conv,
                       l_burnin=l_burnin, suppress_burnin=True, thin=thin_GS)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_geweke_select_burnsupress{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")
else:
    l_walker_conv = l_walker
    l_burnin = [0 for i in l_walker_conv]
    if apply_min_burnin:
        logger.info(f"Mininum burnin of {min_burnin} applied.")
        for ii in range(len(l_burnin)):
            if l_burnin[ii] < min_burnin:
                l_burnin[ii] = min_burnin
        if do_traces:
            et.plot_chains(chainI, lnprobability, l_param_chainI, l_walker=l_walker_conv,
                           l_burnin=l_burnin, suppress_burnin=True, thin=thin_GS)
            if save_plots:
                pl.savefig(join(output_folders["plots"], f"traces_geweke_select_burnsupress{extension_outputs}.pdf"))
            else:
                pl.show()

# Parameter based walker selection
if do_PS:
    logger.info("6. Select walker ")
    l_criteria = []
    l_walker_PS = []
    l_burnin_PS = []
    logger.debug("Percentage of iteration which validate all conditions")
    for i_walker, i_burn in zip(l_walker_conv, l_burnin):
        array_select = np.ones(chainI[i_walker, i_burn:, :].shape[0]).astype(bool)
        nb_iterations = len(array_select)
        for ii in range(len(parameters)):
            array_select = np.logical_and(array_select, select_func[ii](chainI[i_walker, i_burn:, parameters[ii]], *select_arg[ii]))
        l_criteria.append(np.sum(array_select))
        logger.debug(f"waker {i_walker}: {l_criteria[-1] / nb_iterations * 100:.0f}")
        if (l_criteria[-1] / nb_iterations) > (perc_select / 100):
            l_walker_PS.append(i_walker)
            l_burnin_PS.append(i_burn)
    if plot_hist_PS:
        fig, ax = pl.subplots()
        # Histogram
        ax.hist(np.array(l_criteria) * 100, bins="auto")
        ylims = ax.get_ylim()
        ax.vlines(perc_select, *ylims, color="k", linestyle="dashed",
                  label=f"Selection percentage: {perc_select} %")
        ax.set_ylim(ylims)
        ax.set_xlabel("Percentage of each walker which statisfy the criteria [%]")
        ax.set_ylabel("Counts")
        ax.set_title("Histogram of the selection criteria satisfaction")
        ax.legend()
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"hist_param_selection{extension_outputs}.pdf"))
    logger.info(f"Number of selected walker: {len(l_walker_PS)}/{len(l_walker_conv)}")
else:
    l_walker_PS = l_walker_conv
    l_burnin_PS = l_burnin

if save_walkersandburnins:
    et.save_walkers_and_burnin(obj_name=obj_name, extension_analysis=extension_outputs, l_walker=l_walker_PS,
                               l_burnin=l_burnin_PS, folder=output_folders["pickles_analyze"])

if do_bestfit:
    logger.info("6. Determine best fit values and error bars for main parameters")
    fitted_values, _ = et.get_fitted_values(chainI, method=method_bestfit, l_param_name=l_param_chainI,
                                            l_walker=l_walker_PS, l_burnin=l_burnin_PS,
                                            lnprobability_name=lnprobability_name)

    sigma_p, _, sigma_m, _ = da.getconfi(et.get_clean_flatchain(chainI, l_walker=l_walker_PS,
                                                                l_burnin=l_burnin_PS),
                                         level=1, centre=fitted_values, l_param_name=l_param_chainI)

    df_fittedval = pd.DataFrame(index=l_param_chainI, data={'value': fitted_values, 'sigma-': sigma_m,
                                                            'sigma+': sigma_p})

    if save_results_bestfit:
        et.save_chain_analysis(obj_name, extension_analysis=extension_outputs, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                               df_fittedval=df_fittedval, folder=output_folders["pickles_analyze"])

        et.write_latex_table(join(output_folders["tables"], "{}_latex_parameter_table{}.tex".format(obj_name, extension_outputs)),
                             df_fittedval, obj_name)

if do_corner:
    logger.info("7. Do correlation plot for main free parameters")
    corner(et.get_clean_flatchain(chainI, l_walker=l_walker_PS, l_burnin=l_burnin_PS)[::sampling_corner, :],
           labels=l_param_chainI, truths=fitted_values)
    if save_plots:
        pl.savefig(join(output_folders["plots"], f"corner{extension_outputs}.png"))
    else:
        pl.show()
    pl.close("all")


if do_MComp:
    logger.info("8. Do data comparison plots")
    if load_fitted_val_pickle:
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_outputs,
                                                                                        folder=output_folders["pickles_analyze"])
        fitted_val_plot = np.array([df_fittedval.loc[param_name, "value"] for param_name in l_param_chainI])
    else:
        fitted_val_plot = fitted_values
    modelsNresiduals = et.overplot_data_model(param=fitted_val_plot, l_param_name=l_param_chainI,
                                              datasim_dbf=post_instance.datasimulators,
                                              dataset_db=post_instance.dataset_db,
                                              post_instance=post_instance,
                                              datasim_kwargs=kwargs_datasim,
                                              oversamp=oversamp_MComp, return_modelsNresiduals=True)
    if save_modelsNresiduals:
        et.pickle_stuff(modelsNresiduals, join(output_folders["pickles_analyze"], "{}{}{}.pk".format(obj_name, "_modelsNresiduals", extension_outputs)))
    if save_plots:
        pl.savefig(join(output_folders["plots"], f"data_comparison{extension_outputs}.pdf"))
    else:
        pl.show()
    pl.close("all")

if do_SecParam:
    logger.info("9. Determine best fit values and error bars for secondary parameters")
    from secondary_parameters import sp as sec_params

    chainIsec = sp.get_secondary_chains(chainI_main=chainI, sec_params=sec_params, model=post_instance.model)

    l_param_chainIsec = chainIsec.param_names + [lnprobability_name, ]
    chainIsec = ChainsInterpret(np.dstack((chainIsec, lnprobability)), l_param_chainIsec)

    if omega_0to360:
        # Change the range of omega from -180 to 180 to 0 to 360, because omega seems to be centered around 180.
        for plnt in post_instance.model.planets.values():
            mask = np.zeros_like(chainIsec).astype(bool)
            if plnt.omega.full_name in chainIsec.paramname_idx:
                mask[:, :, chainIsec.paramname_idx[plnt.omega.full_name]] = (chainIsec[:, :, chainIsec.paramname_idx[plnt.omega.full_name]] < 0)
                chainIsec[mask] = chainIsec[mask] + 360

    logger.info("Plot raw traces for secondary parameters")
    if do_traces:
        et.plot_chains(chainIsec, lnprobability, l_param_chainIsec, thin=thin_SecParam)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_secondary_raw{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    logger.info("Plot geweke select traces for secondary parameters")
    if do_traces:
        et.plot_chains(chainIsec, lnprobability, l_param_chainIsec, l_walker=l_walker_PS, l_burnin=l_burnin_PS, thin=thin_SecParam)
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"traces_secondary_geweke_select{extension_outputs}.pdf"))
        else:
            pl.show()
    pl.close("all")

    logger.info("Determine best fit values and error bars for secondary parameters")
    fitted_values_sec, _ = et.get_fitted_values(chainIsec, method=method_bestfit, l_param_name=l_param_chainIsec,
                                                l_walker=l_walker_PS, l_burnin=l_burnin_PS,
                                                lnprobability_name=lnprobability_name, force_finite=force_finite)
    sigma_p_sec, _, sigma_m_sec, _ = da.getconfi(et.get_clean_flatchain(chainIsec,
                                                                        l_walker=l_walker_PS,
                                                                        l_burnin=l_burnin_PS, force_finite=force_finite
                                                                        ),
                                                 level=1, centre=fitted_values_sec, l_param_name=l_param_chainIsec
                                                 )
    df_fittedval = pd.concat([df_fittedval, pd.DataFrame(index=l_param_chainIsec,
                                                         data={'value': fitted_values_sec,
                                                               'sigma-': sigma_m_sec,
                                                               'sigma+': sigma_p_sec})])
    df_fittedval = df_fittedval[~df_fittedval.index.duplicated(keep='last')]

    if save_results_bestfit_secpar:
        et.save_chain_analysis(obj_name, extension_analysis=extension_outputs, fitted_values={"array": fitted_values, "l_param": l_param_chainI},
                               fitted_values_sec={"array": fitted_values_sec, "l_param": l_param_chainIsec},
                               df_fittedval=df_fittedval, folder=output_folders["pickles_analyze"])

        et.write_latex_table(join(output_folders["tables"], "{}_latex_parameter_table_wsecondary{}.tex".format(obj_name, extension_outputs)),
                             df_fittedval, obj_name)

    if do_corner_sec:
        logger.info("Do correlation plot for secondary free parameters")
        # Corner doesn't like when there is non finite values or values that doesn't change over the full chain
        # So Below is to avoid both thing even when force_finite is False.
        if not(force_finite):
            sec_flatchain = et.get_clean_flatchain(chainIsec, l_walker=l_walker_PS, l_burnin=l_burnin_PS, force_finite=force_finite)
            notallnotfinite = np.sum(np.isfinite(sec_flatchain), axis=0, dtype=bool)
            idx_to_plot = np.where(notallnotfinite)[0]
            sec_flatchain_to_plot = sec_flatchain[:, idx_to_plot]
            l_param_chainIsec_to_plot = [l_param_chainIsec[ii] for ii in idx_to_plot]
        else:
            sec_flatchain_to_plot = et.get_clean_flatchain(chainIsec, l_walker=l_walker_PS, l_burnin=l_burnin_PS, force_finite=force_finite)
            idx_to_plot = list(range(chainIsec.shape[2]))
            l_param_chainIsec_to_plot = l_param_chainIsec
        idx_not_identical = np.where(np.logical_not(np.all(sec_flatchain_to_plot == sec_flatchain_to_plot[0], axis=0)))[0]
        idx_corner_plot = [idx_to_plot[ii] for ii in idx_not_identical]
        if not(force_finite):
            sec_flatchain_to_plot = et.get_clean_flatchain(chainIsec, l_walker=l_walker_PS, l_burnin=l_burnin_PS, l_param_idx=idx_corner_plot, force_finite=True)
        else:
            sec_flatchain_to_plot = sec_flatchain_to_plot[:, idx_corner_plot]
        corner(sec_flatchain_to_plot[::sampling_corner_sec], labels=[l_param_chainIsec[ii] for ii in idx_corner_plot],
               truths=fitted_values_sec[idx_corner_plot])
        if save_plots:
            pl.savefig(join(output_folders["plots"], f"corner_sec{extension_outputs}.png"))
        else:
            pl.show()
        pl.close("all")

if do_compute_BIC:
    logger.info("10. Compute the BIC of the model")
    if load_fitted_val_pickle_BIC:
        fitted_values_dic_bic, fitted_values_sec_dic_bic, df_fittedval_bic = et.load_chain_analysis(obj_name, extension_analysis=extension_outputs,
                                                                                                    folder=output_folders["pickles_analyze"])
    else:
        df_fittedval_bic = df_fittedval
    bic, bic_bestfit = et.compute_bic(post_instance=post_instance, df_fittedval=df_fittedval_bic, chaininterpret=chainI,
                                      l_walker=l_walker_PS, l_burnin=l_burnin_PS, only_bestfit_bic=only_bestfit_bic)
