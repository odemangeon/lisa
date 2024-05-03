#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to analysis the chains obtained during the MCMC exploration

@TODO:
"""
import gc

from loguru import logger
from os import getcwd
from os.path import join
from unittest import TestCase
from uncertainties import ufloat

import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
import astropy.units as uu


# from corner import corner

# If needed, add lisa folder to the python path here
# lisa_folder = ".."  # Change this if needed
# if lisa_folder not in sys.path:
#     sys.path.append(lisa_folder)

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.exoplanet.exploration_analysis_tools.secondary_parameters as sp
import lisa.tools.stats.distribution_anali as da

from lisa.tools.chain_interpreter import ChainsInterpret
from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.plot import hist_lnprob
# from lisa.posterior.exoplanet.model.gravgroup.datasim_creator_rv import RVdrift_tref_name

###############################
## Definition of the parameters
###############################
obj_name = "target-name"  # Change
kwargs_datasim = {}

output_folders = get_def_output_folders(run_folder=getcwd())  # Folder for the outputs

# At the end of script_mcmcexploration.py the results of the MCMC exploration and the model are stored
# in pickle files. If these object are not in Memory and the code will load them from the pickle file
extension_exploration = "_initrun"  # extension of your exploration (Needs to be the same than in you script_mcmcexploration)

# Save plots ?
extension_analysis = "_initrun"  # extension of this chain analysis (will be added to the ouput files).

##########################
## Execution of the script
##########################

## logger
if 'sinkid_file_explore' in globals():
    logger.remove(sinkid_file_explore)
    del sinkid_file_explore
if 'sinkid_file_analyze' not in globals():
    sinkid_file_analyze = logger.add(join(output_folders['log'], 'analyze.log'), level='DEBUG')

# Set matplotlib rcparams to the default value to avoid issues with plots
matplotlib.rcParams.update(matplotlib.rcParamsDefault)

# load post_instance, lnprobability, acceptance_fraction, l_param_name if needed
if "post_instance" not in globals():
    post_instance = cpost.Posterior()
    post_instance.configure_posterior(path_config_file="config_file.py")
    post_instance.create_allfunctions()

if any([var not in globals() for var in [ "lnprobability", "l_param_name"]]) or (("chainI" not in globals()) and("chain" not in globals())):
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].param_model_names_list
    chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name, extension_exploration=extension_exploration,
                                                                                   folder=output_folders["pickles_explore"])
    tc = TestCase()
    tc.assertCountEqual(l_param_name_bis, l_param_name)

# Create chainI if needed
if "chainI" not in globals():
    nstep = chain.shape[1]
    nwalker = chain.shape[0]
    lnprobability_name = "lnposterior"
    l_param_chainI = l_param_name + [lnprobability_name]
    chainI = ChainsInterpret(np.dstack((chain, lnprobability)), l_param_chainI)
    del chain
    gc.collect()

if "chainIsec" not in globals():
    from secondary_parameters import sp as sec_params
    chainIsec = sp.get_secondary_chains(chainI_main=chainI, sec_params=sec_params, model=post_instance.model)

    l_param_chainIsec = chainIsec.param_names + [lnprobability_name, ]
    chainIsec = ChainsInterpret(np.dstack((chainIsec, lnprobability)), l_param_chainIsec)


# Load walker selection and burnin if needed
if any(var  not in globals() for var in ['l_walker_PS', 'l_burnin_PS']):
    l_walker_PS, l_burnin_PS = et.load_walkers_and_burnin(obj_name=obj_name, extension_analysis=extension_analysis, folder=output_folders["pickles_analyze"])

# Create Latex table
filename_upper = f"{obj_name}_latex_parameter_table_upperlimit{extension_analysis}.tex"
filename_lower = f"{obj_name}_latex_parameter_table_lowerlimit{extension_analysis}.tex"
l_qs = [0.15, 0.3, 2.5, 5, 16, 32, 50, 68, 84, 95, 97.5, 99.7, 99.85]
qs_index = dict(zip(l_qs, range(len(l_qs))))
latex_underscore = '\\_'

def limits(chainInterp, l_walker, l_burnin, param_idx, l_qs, l_sigma_qs, ff):
    chain_clean_param = et.get_clean_flatchain(chainInterp, l_walker=l_walker, l_burnin=l_burnin, l_param_idx=[param_idx, ], iterations_indexes=None, force_finite=True)
    qs = np.percentile(chain_clean_param, l_qs)
    sigma = qs[qs_index[84]] - qs[qs_index[16]]
    vals = [ufloat(qs[qs_index[qq]], sigma) for qq in l_sigma_qs]
    for jj, val in enumerate(vals):
        val_str = val.__str__()
        if val_str.startswith('('):
            exoponent = val_str.split(')')[-1]
            vv = val_str.split('+/-')[0][1:]
            vals[jj] = vv + exoponent
        else:
            vals[jj] = val_str.split('+/-')[0]
    line = f"{param_name.replace('_', latex_underscore)} & {' & '.join(vals)}\\\\\n"
    ff.write(line)
    print(line)

with open(join(output_folders["tables"], filename_upper), "w") as fup, \
     open(join(output_folders["tables"], filename_lower), "w") as flo:
    for uplo, ff in zip(["up", "lo"], [fup, flo]):
        print(f"{uplo} limit")
        l_sigma_qs = [68, 95, 99.7] if uplo == "up" else [0.3, 5, 32]
        ff.write("\\begin{table}\n\\caption{\\label{}}\n\\begin{tabular}{lc}\\hline\n")
        uplo_symb = "<" if uplo == "up" else "<"
        ff.write(f"Parameters & ${uplo_symb}1\,\sigma$ & ${uplo_symb}2\,\sigma$ & ${uplo_symb}3\,\sigma$\\\\ \\hline\n")
        for ii, param_name in enumerate(chainI.param_names):
            limits(chainInterp=chainI, l_walker=l_walker_PS, l_burnin=l_burnin_PS, param_idx=ii, l_qs=l_qs, l_sigma_qs=l_sigma_qs, ff=ff)
        for ii, param_name in enumerate(chainIsec.param_names):
            limits(chainInterp=chainIsec, l_walker=l_walker_PS, l_burnin=l_burnin_PS, param_idx=ii, l_qs=l_qs, l_sigma_qs=l_sigma_qs, ff=ff)
        ff.write("\\hline\n\\\\")
        ff.write("\\end{tabular}\n")
        ff.write("\\end{table}\n")
