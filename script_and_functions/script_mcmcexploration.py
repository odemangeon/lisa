#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to perform an MCMC exploration.

@TODO:
"""
from logging import DEBUG, INFO
from math import ceil
from os import getcwd
from os.path import join

from scipy.optimize import minimize
from numpy import zeros_like
from emcee import EnsembleSampler

# If needed, add lisa folder to the python path here
# lisa_folder = ".."  # Change this if needed
# if lisa_folder not in sys.path:
#     sys.path.append(lisa_folder)

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
import lisa.tools.mylogger as ml
from lisa.explore_analyze.misc import get_def_output_folders

## Definition of the parameters
obj_name = "WASP-151"  # Change
extension_exploration = ""  # Change extension to add at the end (before .pk) of the name of the pickle files to save the exploration.
model_category = "GravitionalGroups"
nb_planet = 1
rv_model = "radvel"  # None will select the default model being radvel
transit_model = "batman"  # None will select the default model being batman
parametrisation = "EXOFAST"  # None will select the default parametrisation which is EXOFAST for this model
with_DeltaRV = True
kwargs_post = {}

data_folder = join(getcwd(), "data")  # Change if needed: Folder where the data are located
run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Pre-minimisation parameters
do_preminimization = True
N_maxiter_preminimization = 100
xtol_preminimization = 1e-12

# emcee parameters
nwalker_fact = 2.5
nsteps_MCMC = 10000
save_to_file = False
cluster = False  # If you run this code on a cluster (not in ipython) change to True

# If you already run a first MCMC and extracted fitted values, you can use them to draw the initial
# values for a new MCMC run
load_from_pickle = False
extension_analysis = ""

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

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
post_instance.define_model(category=model_category, name=obj_name, stars=1, planets=nb_planet,
                           rv_model=rv_model, transit_model=transit_model)

logger.info("5. Create inst_cat specific parameter file")
if cluster:
    post_instance.model.create_instcat_paramfile(paramfile_path=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_instcat_paramfile(paramfile_path=None)  # paramfile_path=None the names are automatically chosen.

    if len(post_instance.model.paramfile4instcat) > 0:
        input("Modifiy the inst_cat specific paramerisation file: {}".format(post_instance.model.paramfile4instcat))

logger.info("6. Load inst_cat specific parameter file")
post_instance.model.load_instcat_paramfile()

logger.info("7. Set parametrisation of the model")
post_instance.model.set_parametrisation(parametrisation=parametrisation, with_DeltaRV=with_DeltaRV)

logger.info("8. Create and modify the paramerisation file")
if cluster:
    post_instance.model.create_parameter_file("param_file.py", answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_parameter_file("param_file.py")

    input("Modifiy the paramerisation file")

logger.info("9. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("10. Create datasimulator functions")
test = post_instance.get_datasimulators()

logger.info("11. Create likelihood functions")
post_instance.get_lnlikelihoods()

logger.info("12. Create prior functions")
post_instance.get_individal_lnpriors()
post_instance.get_lnpriors()

logger.info("13. Create posterior functions")
post_instance.get_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

logger.info("14. Save posterior instance")
post_instance.save_post_instance(pickle_folder=output_folders["pickles_explore"])

logger.info("15. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = ceil(int(ndim * nwalker_fact) / 2) * 2  # To get an even number of walkers
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn, kwargs=kwargs_post)

logger.info("16. Create initial value")
if load_from_pickle:
    if load_from_pickle:
        logger.info("0. Load from pickle")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                        folder=output_folders["pickles_analyze"])
    else:
        pass
    init_distrib = et.get_init_distrib_from_fitvalues(fitted_values=df_fittedval)
else:
    init_distrib = None
p0 = et.generate_random_init_pos(nwalker=nwalkers, post_instance=post_instance,
                                 init_distrib=init_distrib)

if not load_from_pickle and do_preminimization:
    logger.info("17. AMOEBA minimization")
    p1 = zeros_like(p0)

    def lnpostfnminus(p):
        return -lnpostfn(p, **kwargs_post)

    for ii in range(nwalkers):
        res = minimize(lnpostfnminus, p0[ii, :], method='nelder-mead', options={'xatol': xtol_preminimization,
                                                                                'disp': True, 'maxiter': N_maxiter_preminimization})
        p1[ii, :] = res["x"]
else:
    p1 = p0

logger.info("18. Perform MCMC exploration")
logger4emceerun = logger if cluster else None
et.explore(sampler, p1, nsteps=nsteps_MCMC, save_to_file=save_to_file, filename_chain="{}_chain.dat".format(obj_name),
           filename_acceptfrac="{}_acceptfrac.dat".format(obj_name), dat_folder=output_folders["dats"], l_param_name=l_param_name, logger=logger4emceerun)
et.save_emceesampler(sampler, l_param_name, obj_name, extension_exploration=extension_exploration, folder=output_folders["pickles_explore"])

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction
