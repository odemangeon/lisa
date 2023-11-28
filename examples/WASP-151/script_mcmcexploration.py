"""
Script template to perform an MCMC exploration.

@TODO:
"""
from loguru import logger
from math import ceil
from os import getcwd
from os.path import join

from scipy.optimize import minimize
from numpy import zeros_like

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
obj_name = "WASP-151"  # Change

extension_exploration = "_initrun"  # Change extension to add at the end (before .pk) of the name of the pickle files to save the exploration.

output_folders = get_def_output_folders(run_folder=None)

# Pre-minimisation parameters
do_preminimization = True
N_maxiter_preminimization = 1000
xtol_preminimization = 1e-12

# emcee parameters
nwalker_fact = 4
nsteps_MCMC = 50000
check_convergence_every = 1000
save_to_file = False
cluster = False  # If you run this code on a cluster (not in ipython) change to True

# Distribution for the choice of initial parameter values. For now you can only specify gaussian distributions
# Format {"<param_name>": {"mu": <mu_value>, "sigma": <sigma_value>}}
# This superseed the distribution inferred from a previous run (load_from_pickle = True below)
init_distrib = {}

# If you already run a first MCMC and extracted fitted values, you can use them to draw the initial
# values for a new MCMC run
load_from_pickle = False
extension_analysis = ""

##########################
## Execution of the script
##########################

## logger
if 'sinkid_file_explore' not in globals():
    sinkid_file_explore = logger.add(join(output_folders['log'], 'exploration.log'), level='DEBUG')

logger.info("########\nMCMC EXPLORATION")

logger.info("1. Create a Posterior instance and give it the name of the object studied and the model definition.")
post_instance = cpost.Posterior()

logger.info("2. Define the posterior.")
post_instance.configure_posterior(path_config_file="config_file.py")  # Change if needed by the name you gave or want to give to your dataset file.


logger.info("14. Create datasimulator functions")
post_instance.create_datasimulators()

logger.info("15. Create likelihood functions")
post_instance.create_lnlikelihoods()

logger.info("16. Create prior functions")
post_instance.create_lnpriors()

logger.info("17. Create posterior functions")
post_instance.create_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].param_model_names_list

# logger.info("18. Save posterior instance")
# post_instance.save_post_instance(pickle_folder=output_folders["pickles_explore"])

logger.info("19. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].param_model_names_list)
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = ceil(int(ndim * nwalker_fact) / 2) * 2  # To get an even number of walkers

logger.info("20. Create initial value")
if load_from_pickle:
    if load_from_pickle:
        logger.info("0. Load from pickle")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                        folder=output_folders["pickles_analyze"])
    else:
        pass
    init_distrib_frompreviousfit = et.get_init_distrib_from_fitvalues(fitted_values=df_fittedval)
    init_distrib_final = init_distrib_frompreviousfit.copy()
    init_distrib_final.update(init_distrib)
else:
    init_distrib_final = init_distrib

p0 = et.generate_random_init_pos(nwalker=nwalkers, post_instance=post_instance,
                                 init_distrib=init_distrib_final)

if not load_from_pickle and do_preminimization:
    logger.info("21. AMOEBA minimization")
    p1 = zeros_like(p0)

    def lnpostfnminus(p):
        return -lnpostfn(p)

    for ii in range(nwalkers):
        res = minimize(lnpostfnminus, p0[ii, :], method='nelder-mead', options={'xatol': xtol_preminimization,
                                                                                'disp': True, 'maxiter': N_maxiter_preminimization})
        p1[ii, :] = res["x"]
else:
    p1 = p0

logger.info("22. Perform MCMC exploration")
sampler = et.explore(nwalkers=nwalkers, ndim=ndim, log_prob_fn=lnpostfn, p0=p1, nsteps=nsteps_MCMC,
                     save_to_file=save_to_file, filename=f"{obj_name}_chain.h5", file_folder=output_folders["dats"],
                     check_convergence_every=check_convergence_every, ntau=100, tol=0.01, l_param_name=l_param_name)
et.save_emceesampler(sampler, l_param_name, obj_name, extension_exploration=extension_exploration, folder=output_folders["pickles_explore"])

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction
