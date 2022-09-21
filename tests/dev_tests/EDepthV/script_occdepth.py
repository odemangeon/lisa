import gc

import numpy as np
import matplotlib.pyplot as pl

from logging import DEBUG, INFO
from os import getcwd
from os.path import join
from unittest import TestCase
from astropy.visualization import hist as hist_astro

import lisa.tools.mylogger as ml
import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.tools.chain_interpreter import ChainsInterpret


obj_name = "WASP-14"  # Change
planet_name = "b"

output_folders = get_def_output_folders(run_folder=getcwd())  # Folder for the outputs

# At the end of script_mcmcexploration.py the results of the MCMC exploration and the model are stored
# in pickle files. If these object are not in Memory and the code will load them from the pickle file
extension_exploration = "_initrun"  # extension of your exploration (Needs to be the same than in you script_mcmcexploration)
extension_analysis = "_initrun_median"

##########################
## Execution of the script
##########################

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file=join(output_folders["log"], f"{obj_name}.log"))


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

if any([var not in globals() for var in ["l_walker_PS", "l_burnin_PS"]]):
    l_walker_PS, l_burnin_PS = et.load_walkers_and_burnin(obj_name=obj_name, extension_analysis=extension_analysis, folder=output_folders["pickles_analyze"])

print("Start comp")
occ_depth_chain = (chainI[f"{obj_name}_{planet_name}_APCcos1"] / 2 + chainI[f"{obj_name}_{planet_name}_FoffsetPCcos1"]) * 1e6
occ_depth_clean_flatchain = et.get_clean_flatchain(occ_depth_chain, l_walker=l_walker_PS, l_burnin=l_walker_PS, force_finite=True)

print("Start Plot")
pl.figure(constrained_layout=True)
pl.hist(occ_depth_clean_flatchain, density=True, bins='auto')
pl.xlabel("Occultation Depth [ppm]")
pl.ylabel("Normalized counts")

pl.show()
