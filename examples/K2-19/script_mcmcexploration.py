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
obj_name = "K2-19"  # Change
extension_exploration = "_initrun"  # Change extension to add at the end (before .pk) of the name of the pickle files to save the exploration.
model_category = "GravitionalGroupsDynamic"
nb_planet = 2
parametrisation = "Np"  # None will select the default parametrisation which is EXOFAST for this model
with_RVdrift = False
with_DeltaRV = True
with_OOT_var = False
kwargs_post = {"tref_dyn": 56813.0}

data_folder = join(getcwd(), "data")  # Change if needed: Folder where the data are located
run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Pre-minimisation parameters
do_preminimization = False
N_maxiter_preminimization = 1000
xtol_preminimization = 1e-5

# emcee parameters
nwalker_fact = 2.5
nsteps_MCMC = 1000
save_to_file = False
cluster = False  # If you run this code on a cluster (not in ipython) change to True

# Distribution for the choice of initial parameter values. For now you can only specify gaussian distributions
# Format {"<param_name>": {"mu": <mu_value>, "sigma": <sigma_value>}}
# This superseed the distribution inferred from a previous run (load_from_pickle = True below)
# init_distrib = {}
init_distrib = {'K2-19_A_LDKp_ldc1': {"mu": 0.44236956228322283, "sigma": 0.03839799373290648},
                'K2-19_A_LDKp_ldc2': {"mu": 0.2687115557371168, "sigma": 0.08096213566981952},
                'K2-19_A_LDC2PU_ldc1': {"mu": 0.5329462776262925, "sigma": 0.07977304668058205},
                'K2-19_A_LDC2PU_ldc2': {"mu": 0.2868724865757065, "sigma": 0.1055025420532239},
                'K2-19_A_LDBalesta_ldc1': {"mu": 0.3975311982943123, "sigma": 0.08511737684750714},
                'K2-19_A_LDBalesta_ldc2': {"mu": 0.22799858880251223, "sigma": 0.10202025211249577},
                'K2-19_A_LDNITES_ldc1': {"mu": 0.43924762726300537, "sigma": 0.11691540483814045},
                'K2-19_A_LDNITES_ldc2': {"mu": 0.2035523882712532, "sigma": 0.0990145338386933},
                'HARPSN_def_DeltaRV': {"mu": 0.0806784127854377, "sigma": 0.003947479323083133},
                'K2-19_A_v0': {"mu": 7.232895345100348, "sigma": 0.004030235537191729},
                'FIES_def_DeltaRV': {"mu": -0.039346837709316185, "sigma": 0.005244076593386132},
                'PFS_def_DeltaRV': {"mu": -7.23380747259805, "sigma": 0.00398741305442929},
                'HARPS_0_DeltaRV': {"mu": 0.10721970560538635, "sigma": 0.004155766531387439},
                'HARPS_1_DeltaRV': {"mu": -7.337635393891596, "sigma": 0.0016391322725679558},
                'K2-19_A_M': {"mu": 0.8697532854055399, "sigma": 0.08402770845098373},
                'K2-19_A_R': {"mu": 1.0097956668298746, "sigma": 0.04779137685654633},
                'K2-19_b_Rrat': {"mu": 0.07387378614212943, "sigma": 0.0006184894048535949},
                'K2-19_c_Rrat': {"mu": 0.04478542588443111, "sigma": 0.00038480714302717434},
                'K2-19_qplus': {"mu": 0.00015974428277621598, "sigma": 1.01445280574555e-05},
                'K2-19_qp': {"mu": 0.42654267778795685, "sigma": 0.05413196650278318},
                'K2-19_hplus': {"mu": 0.05528471813860483, "sigma": 0.03347389566609989},
                'K2-19_hminus': {"mu": -0.016789918284163652, "sigma": 0.00534044070605251},
                'K2-19_kplus': {"mu": 0.19956076235911888, "sigma": 0.04489138694597464},
                'K2-19_kminus': {"mu": 0.09105764275184651, "sigma": 0.010519297983949391},
                'K2-19_b_P': {"mu": 7.918651423864348, "sigma": 0.0001356978062441172},
                'K2-19_b_tic': {"mu": 56813.384329306195, "sigma": 0.00023663795582251623},
                'K2-19_b_inc': {"mu": 1.5504843779566448, "sigma": 0.007222724717454332},
                'K2-19_c_P': {"mu": 11.910718825208841, "sigma": 0.0005905492666258283},
                'K2-19_c_tic': {"mu": 56817.27300497582, "sigma": 0.0006813613799749874},
                'K2-19_c_inc': {"mu": 1.5449912923504083, "sigma": 0.0028581268465537324},
                'K2-19_c_OMEGA': {"mu": 2.413249539701598, "sigma": 0.1358649211715699},
                }

# If you already run a first MCMC and extracted fitted values, you can use them to draw the initial
# values for a new MCMC run
load_from_pickle = False
extension_analysis = ""

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file="{}.log".format(obj_name))

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
                           transit_model="batman")

logger.info("5. Create inst_cat specific parameter file")
if cluster:
    post_instance.model.create_instcat_paramfile(paramfile_path=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_instcat_paramfile(paramfile_path=None)  # paramfile_path=None the names are automatically chosen.

    if len(post_instance.model.paramfile4instcat) > 0:
        input("Modifiy the inst_cat specific paramerisation file: {}".format(post_instance.model.paramfile4instcat))

logger.info("6. Load inst_cat specific parameter file")
post_instance.model.load_instcat_paramfile()

logger.info("7. Create noise model specific parameter file")
if cluster:
    post_instance.model.create_noisemodcat_paramfile(paramfile_path=None, answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_noisemodcat_paramfile(paramfile_path=None)  # paramfile_path=None the names are automatically chosen.

    if len(post_instance.model.paramfile4noisemodcat) > 0:
        input("Modifiy the noise model specific paramerisation file: {}".format(post_instance.model.paramfile4noisemodcat))

logger.info("8. Load noise model category specific parameter file")
post_instance.model.load_noisemodcat_paramfile()

logger.info("9. Set parametrisation of the model")
post_instance.model.set_parametrisation(parametrisation=parametrisation, with_DeltaRV=with_DeltaRV)

logger.info("10. Create and modify the paramerisation file")
if cluster:
    post_instance.model.create_parameter_file("param_file.py", answer_overwrite="n", answer_create=None)
else:
    post_instance.model.create_parameter_file("param_file.py")

    input("Modifiy the paramerisation file")

logger.info("11. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("12. Create datasimulator functions")
test = post_instance.get_datasimulators()

logger.info("13. Create likelihood functions")
post_instance.get_lnlikelihoods()

logger.info("14. Create prior functions")
post_instance.get_individal_lnpriors()
post_instance.get_lnpriors()

logger.info("15. Create posterior functions")
post_instance.get_lnposteriors()
l_param_name = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

logger.info("16. Save posterior instance")
post_instance.save_post_instance(pickle_folder=output_folders["pickles_explore"])

logger.info("17. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = ceil(int(ndim * nwalker_fact) / 2) * 2  # To get an even number of walkers
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn, kwargs=kwargs_post)

logger.info("18. Create initial value")
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
    logger.info("19. AMOEBA minimization")
    p1 = zeros_like(p0)

    def lnpostfnminus(p):
        return -lnpostfn(p, **kwargs_post)

    for ii in range(nwalkers):
        res = minimize(lnpostfnminus, p0[ii, :], method='nelder-mead', options={'xatol': xtol_preminimization,
                                                                                'disp': True, 'maxiter': N_maxiter_preminimization})
        p1[ii, :] = res["x"]
else:
    p1 = p0

logger.info("19. Perform MCMC exploration")
logger4emceerun = logger if cluster else None
et.explore(sampler, p1, nsteps=nsteps_MCMC, save_to_file=save_to_file, filename_chain="{}_chain.dat".format(obj_name),
           filename_acceptfrac="{}_acceptfrac.dat".format(obj_name), dat_folder=output_folders["dats"], l_param_name=l_param_name, logger=logger4emceerun)
et.save_emceesampler(sampler, l_param_name, obj_name, extension_exploration=extension_exploration, folder=output_folders["pickles_explore"])

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction
