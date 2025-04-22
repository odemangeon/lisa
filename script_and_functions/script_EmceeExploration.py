"""
Script template to perform an MCMC exploration.

@TODO:
"""
import arviz as az
import dill
import json

from loguru import logger
from math import ceil
from os import getcwd
from os.path import join
from copy import copy

from scipy.optimize import minimize
from numpy import zeros_like

from tqdm import tqdm

import emcee
from emcee import EnsembleSampler
from emcee.backends import HDFBackend

# If needed, add lisa folder to the python path here
# lisa_folder = ".."  # Change this if needed
# if lisa_folder not in sys.path:
#     sys.path.append(lisa_folder)

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
from lisa.explore_analyze.misc import get_def_output_folders

###############################
## Definition of the parameters
###############################
obj_name = "target_name"  # Change

run_name = "initrun"  # Change extension to add at the end (before .pk) of the name of the pickle files to save the exploration.

output_folders = get_def_output_folders(run_folder=None)

with_blobs = True

# Pre-minimisation parameters
do_preminimization = False
N_maxiter_preminimization = 1000
xtol_preminimization = 1e-12

##################
# emcee parameters
##################
nwalker_fact = 4  # The number of walkers will be equal to nwalker_fact * nb of free parameters
nsteps_MCMC = 50000  # Number of steps per walker
moves = None # Default: None, ex: [(emcee.moves.DEMove(), 0.8), (emcee.moves.DESnookerMove(), 0.2)]. If you want to use a different move than the default one like. See https://emcee.readthedocs.io/en/stable/user/moves/ and https://emcee.readthedocs.io/en/stable/tutorials/moves/#moves

check_convergence_every = None  # If different from None and > 0, emcee will check the autocorrelation step scale of the chain every 'check_convergence_every' steps
ntau = 100  # If the length of the chain is higher than ntau * autocorrelation step scale of the chains than the emcee exploration will be stopped (even if nsteps_MCMC is not yet reached)
tol = 0.01  # Relative precision on the computation of the autocorrelation timescale required for the emcee exploration to stop

sample_kwargs: dict= {} # Additional arguments to pass to the sample function of emcee: https://emcee.readthedocs.io/en/stable/user/sampler/#emcee.EnsembleSampler.sample

backend_filename = f"{obj_name}_Emcee.h5"  # If backend is different than None than the emcee exploration will be saved to file

cluster = False  # If you run this code on a cluster (not in ipython) change to True

####################################################
# Parameters for the initial position of the walkers
####################################################

# Distribution for the choice of initial parameter values. For now you can only specify gaussian distributions
# Format {"<param_name>": {"mu": <mu_value>, "sigma": <sigma_value>}}
# This superseed the distribution inferred from a previous run (load_from_pickle = True below)
init_distrib: dict = {}

# If you already run a first MCMC and extracted fitted values, you can use them to draw the initial
# values for a new MCMC run
load_fitted_values_from_previous_run_analysis = False
previous_run_name = None
extension_analysis = None

# Restart from previous backended run
restart_run = True
run_name_for_last_state = "burninrun"  # Name of the run to restart from

##########################
## Execution of the script
##########################

## logger
if 'sinkid_file_explore' not in globals():
    sinkid_file_explore = logger.add(join(output_folders['log'], 'exploration.log'), level='DEBUG')

logger.info("########\nNew EMCEE EXPLORATION")

logger.info("Creating Posterior instance")
post_instance = cpost.Posterior()

logger.info("Setting-up Posterior.")
post_instance.configure_posterior(path_config_file="config_file.py")  # Change if needed by the name you gave or want to give to your dataset file.

logger.info("Creating all functions (priors, likelihoods, posteriors)")
post_instance.create_allfunctions(with_blobs=with_blobs)
l_param_name = post_instance.lnposteriors.dataset_db["all"].param_model_names_list
# Save the list of parameter names in a json file
with open(join(output_folders["pickles_explore"], f"{obj_name}_param_names.json"), "w") as file:
    json.dump(l_param_name, file)

logger.info("Getting Emcee sampler inputs")
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
ndim = len(post_instance.lnposteriors.dataset_db["all"].param_model_names_list)
logger.info(f"Number of free parameters (ndim) = {ndim}")
nwalkers = ceil(int(ndim * nwalker_fact) / 2) * 2  # To get an even number of walkers
logger.info(f"Number of Emcee walkers (nwalkers) = {nwalkers}")


if backend_filename is not None:
    logger.info("Creating backend for Emcee sampler")
    backend_filepath = join(output_folders["pickles_explore"], backend_filename)
    backend = HDFBackend(filename=join(output_folders["pickles_explore"], backend_filename), name=run_name) 

if not(restart_run):
    backend.reset(nwalkers=nwalkers, ndim=ndim)
    logger.info("Backend reset")
     
    logger.info("Creating initial value")
    if load_fitted_values_from_previous_run_analysis:
        logger.info(f"Loading fitted parameter values from analysis {extension_analysis} of previous run {previous_run_name}")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                        folder=output_folders["pickles_analyze"])
        init_distrib_frompreviousfit = et.get_init_distrib_from_fitvalues(fitted_values=df_fittedval)
    else:
        init_distrib_frompreviousfit = {}
    init_distrib_final = init_distrib_frompreviousfit.copy()
    if len(init_distrib) > 0:
        logger.info(f"Setting initial distributions according to user input for parameters: {list(init_distrib.keys())}")
        init_distrib_final.update(init_distrib)
    set_prior_distrib = set(l_param_name) - set(init_distrib_final.keys())
    if len(set_prior_distrib) > 0:
        logger.info(f"Setting the initial distribution of the following parameters to the prior distribution: {set_prior_distrib}")
    p0 = et.generate_random_init_pos(nwalker=nwalkers, post_instance=post_instance, init_distrib=init_distrib_final)
    logger.info(f"Created initial values")

    if not load_fitted_values_from_previous_run_analysis and do_preminimization:
        logger.info("Performing AMOEBA minimization")
        initial_state = zeros_like(p0)
        
        if with_blobs:
            def lnpostfnminus(p):
                return -lnpostfn(p)[0]
        else:
            def lnpostfnminus(p):
                return -lnpostfn(p)

        for ii in tqdm(range(nwalkers)):
            res = minimize(lnpostfnminus, p0[ii, :], method='nelder-mead', options={'xatol': xtol_preminimization,
                                                                                    'disp': True, 'maxiter': N_maxiter_preminimization})
            initial_state[ii, :] = res["x"]
    else:
        initial_state = p0
else:
    logger.info(f"Restarting from previous run: {run_name_for_last_state}")
    if 'last_state' in globals():
        initial_state = last_state
    else:
        if run_name_for_last_state != run_name:
            initial_state = HDFBackend(filename=join(output_folders["pickles_explore"], backend_filename), name=run_name_for_last_state).get_last_sample()
        else: 
            initial_state = backend.get_last_sample()

logger.info("Creating Emcee sampler")
if with_blobs:
    blobs_dtype = et.default_blobs_dtype
else:
    blobs_dtype = None
sampler = EnsembleSampler(nwalkers=nwalkers, ndim=ndim, log_prob_fn=lnpostfn, moves=moves, backend=backend, blobs_dtype=blobs_dtype)

logger.info("Performing Emcee exploration")
last_state = et.explore(sampler=sampler, initial_state=initial_state, nsteps=nsteps_MCMC, 
                        check_convergence_every=check_convergence_every, ntau=ntau, tol=tol,
                        sample_kwargs=sample_kwargs,
                        )