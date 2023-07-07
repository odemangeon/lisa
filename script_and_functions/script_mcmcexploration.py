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

## Definition of the parameters
obj_name = "target_name"  # Change
extension_exploration = "_initrun"  # Change extension to add at the end (before .pk) of the name of the pickle files to save the exploration.
model_category = "GravitionalGroups"
nb_planet = 1
kwargs_post = {}

data_folder = join(getcwd(), "data")  # Change if needed: Folder where the data are located
run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

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

# logger
sinkid_file_explore = logger.add(join(output_folders['log'], 'exploration.log'), level='DEBUG')

logger.info("########\nMCMC EXPLORATION")

logger.info("1. Create a Posterior instance and give it the name of the object studied.")
post_instance = cpost.Posterior(object_name=obj_name)

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = data_folder

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = run_folder

logger.info("3. Add datasets from a datasets file.")
post_instance.load_datasetsfile("datasets.txt")  # Change if needed by the name you gave or want to give to your dataset file.

logger.info("4. Add a model")
post_instance.define_model(category=model_category, name=obj_name, stars=1, planets=nb_planet)

logger.info("5. Create model specific parameter file")
if cluster:
    post_instance.model.create_model_paramfile(paramfile=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_model_paramfile(paramfile=None)  # paramfile=None the names are automatically chosen.

    input("If there are a model specific paramerisation file please check it")

logger.info("6. Load model specific parameter file")
post_instance.model.load_parameter_file_model()

logger.info("7. Create inst_cat specific parameter file")
if cluster:
    post_instance.model.create_instcat_paramfiles(paramfile_path=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_instcat_paramfiles(paramfile_path=None)  # paramfile_path=None the names are automatically chosen.

    input("If there are any inst_cat specific paramerisation file please check them")

logger.info("8. Load inst_cat specific parameter file")
post_instance.model.load_instcat_paramfile()

logger.info("9. Create noise model specific parameter file")
if cluster:
    post_instance.model.create_noisemodcat_paramfile(paramfile_path=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_noisemodcat_paramfile(paramfile_path=None)  # paramfile_path=None the names are automatically chosen.

    if len(post_instance.model.paramfile4noisemodcat) > 0:
        input("Modifiy the noise model specific paramerisation file: {}".format(post_instance.model.paramfile4noisemodcat))

logger.info("10. Load noise model category specific parameter file")
post_instance.model.load_noisemodcat_paramfile()

logger.info("11. Set parametrisation of the model")
post_instance.model.set_parametrisation()

logger.info("12. Create and modify the paramerisation file")
if cluster:
    post_instance.model.create_parameter_file("param_file.py", answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_parameter_file("param_file.py")

    input("Modifiy the paramerisation file")

logger.info("13. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("14. Create datasimulator functions")
test = post_instance.get_datasimulators()

logger.info("15. Create likelihood functions")
post_instance.get_lnlikelihoods()

logger.info("16. Create prior functions")
post_instance.get_lnpriors()

logger.info("17. Create posterior functions")
post_instance.get_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].param_model_names_list

logger.info("18. Save posterior instance")
post_instance.save_post_instance(pickle_folder=output_folders["pickles_explore"])

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
        return -lnpostfn(p, **kwargs_post)

    for ii in range(nwalkers):
        res = minimize(lnpostfnminus, p0[ii, :], method='nelder-mead', options={'xatol': xtol_preminimization,
                                                                                'disp': True, 'maxiter': N_maxiter_preminimization})
        p1[ii, :] = res["x"]
else:
    p1 = p0

logger.info("22. Perform MCMC exploration")
sampler = et.explore(nwalkers=nwalkers, ndim=ndim, log_prob_fn=lnpostfn, p0=p1, nsteps=nsteps_MCMC, kwargs_prob_fn=kwargs_post,
                     save_to_file=save_to_file, filename=f"{obj_name}_chain.h5", file_folder=output_folders["dats"],
                     check_convergence_every=check_convergence_every, ntau=100, tol=0.01, l_param_name=l_param_name)
et.save_emceesampler(sampler, l_param_name, obj_name, extension_exploration=extension_exploration, folder=output_folders["pickles_explore"])

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction
