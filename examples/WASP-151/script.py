#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script for the analysis of WASP-151 RV data

@TODO:
"""
import sys
from logging import DEBUG, INFO
from math import ceil
from os import getcwd

from scipy.optimize import minimize
from numpy import zeros_like
from emcee import EnsembleSampler

# Add lisa folder to python path
lisa_folder = "../.."
if lisa_folder not in sys.path:
    sys.path.append(lisa_folder)

import lisa.posterior.core.posterior as cpost
import lisa.tools.emcee_tools as et
import lisa.tools.mylogger as ml

## Definition of the parameters
obj_name = "WASP-151"
model_category = "GravitionalGroups"
nb_planet = 1
parametrisation = "EXOFAST"
kwargs_post = {}
data_folder = "./data/"

# Pre-minimisation parameters
do_preminimization = False
N_maxiter_preminimization = 100
xtol_preminimization = 1e-12

# emcee parameters
nwalker_fact = 2.5
nsteps_MCMC = 10000
save_to_file = True
cluster = False  # If you run this code on a cluster (not in ipython) change to True

# If you already run a first MCMC and extracted fitted values, you can use them to draw the initial
# values for a new MCMC run
load_from_pickle = False

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

logger.info("########\nMCMC EXPLORATION")

logger.info("1. Create a Posterior instance and give it the name of the object studied.")
post_instance = cpost.Posterior(object_name=obj_name)

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = data_folder

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = getcwd()

logger.info("3. Add datasets from a datasets file.")
post_instance.load_datasetsfile("datasets.txt")

logger.info("4. Add a model")
post_instance.define_model(category=model_category, name=obj_name, stars=1, planets=nb_planet,
                           parametrisation=parametrisation, rv_model="radvel", transit_model="batman")

logger.info("5. Create and modify LC parameter file")
post_instance.model.create_LC_param_file(paramfile_path="LC_param_file.py", answer_overwrite="n", answer_create=None)

logger.info("6. Load the paramerisation file")
post_instance.model.load_LC_param_file()

logger.info("7. Apply a parametrisation to the model")
post_instance.model.apply_parametrisation(with_DeltaRV=True)

logger.info("8. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py", answer_overwrite="n", answer_create=None)

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
post_instance.save_post_instance()

logger.info("15. Create sampler")
ndim = len(post_instance.lnposteriors.dataset_db["all"].arg_list["param"])
lnpostfn = post_instance.lnposteriors.dataset_db["all"].function
arg_list = post_instance.lnposteriors.dataset_db["all"].arg_list
lnpriorfn = post_instance.lnpriors.dataset_db["all"].function
lnlikefn = post_instance.lnlikelihoods.dataset_db["all"].function
nwalkers = ceil(int(ndim * nwalker_fact) / 2) * 2  # To get an even number of walkers
sampler = EnsembleSampler(nwalkers=nwalkers, dim=ndim, lnpostfn=lnpostfn)

logger.info("16. Create initial value")
if load_from_pickle:
    logger.info("0. Load from pickle")
    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                    folder=".")
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
           filename_acceptfrac="{}_acceptfrac.dat".format(obj_name), l_param_name=l_param_name, logger=logger4emceerun)
et.save_emceesampler(sampler, l_param_name, obj_name)

chain = sampler.chain
lnprobability = sampler.lnprobability
acceptance_fraction = sampler.acceptance_fraction

# l_walker_acceptfrac, _ = et.acceptancefraction_selection(sampler, sig_fact=2., verbose=1)
# l_walker_lnpost, _ = et.lnposterior_selection(sampler, sig_fact=2., verbose=1)
# l_walker = list(set(l_walker_acceptfrac) & set(l_walker_lnpost))
# logger.info("Number of walker rejected by acceptance fraction or lnposterior: {}/{}"
#             "".format((sampler.chain.shape[0] - len(l_walker)), sampler.chain.shape[0]))
# zscores, first_steps = et.geweke_multi(sampler, first=0.1, last=0.40, intervals=50,
#                                        l_walker=l_walker)
# l_burnin, l_walker_geweke = et.geweke_selection(zscores, first_steps=first_steps, geweke_thres=1.6,
#                                                 l_walker=l_walker)
# fitted_values = et.get_fitted_values(sampler, method="median", l_param_name=l_param_name,
#                                      l_walker=l_walker_geweke, l_burnin=l_burnin)
# sigma_m, _, sigma_p = da.getconfi(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke,
#                                                          l_burnin=l_burnin),
#                                   level=1, centre=fitted_values, l_param_name=l_param_name)
# # SOPHIE_default_jitter: 0.07390628909168875 +0.07092457023056994 -0.07661313680035657
# # WASP-151_A_v0: -12.369079060321306 +0.0024455080593792644 -0.0022291702809340563
# # WASP-151_b_K: 0.03701494270414841 +0.0029996564799572925 -0.003242621138187164
# # WASP-151_b_secosw: -0.011524976266634243 +0.03680594008156956 -0.038812447556235426
# # WASP-151_b_sesinw: 0.009475155023900296 +0.038499815697444734 -0.038550565561430855
# # WASP-151_b_tc: 57741.00752174061 +0.0008870884121279232 -0.0016435749785159715
# # WASP-151_b_P: 4.533460732028823 +7.417328449577099e-05 -6.427026153055238e-05
# # K2_default_jitter: 2.1075500774917666 +0.027959739228607727 -0.03306713415133178
# # A_LDKp_ldc1: 0.5500632701363917 +0.0026401049209291427 -0.002497404568402417
# # A_LDKp_ldc2: 0.11835867155682295 +0.005592884985978361 -0.006067235897780507
# # WASP-151_b_cosinc: 0.02707318020702465 +0.017146066892261287 -0.015311925555136857
# # WASP-151_b_Rrat: 0.10105118308635531 +0.0017288716142898897 -0.0009004305596509582
# # WASP-151_b_aR: 9.967458319518668 +0.31018483846089673 -0.5501394571610305
# et.plot_chains(sampler, l_param_name)
# pl.savefig("./images/traces_raw.png")
# pl.close("all")
# et.plot_chains(sampler, l_param_name, l_walker=l_walker_geweke, l_burnin=l_burnin)
# pl.savefig("./images/traces_geweke_select.png")
# pl.close("all")
# corner(et.get_clean_flatchain(sampler, l_walker=l_walker_geweke, l_burnin=l_burnin),
#        labels=l_param_name, truths=fitted_values)
# pl.savefig("./images/corner.png")
# pl.close("all")
# et.overplot_data_model(fitted_values, l_param_name,
#                        post_instance.datasimulators.dataset_db, post_instance.dataset_db,
#                        post_instance.noisemodels.dataset_db,
#                        oversamp=30)
# pl.savefig("./images/data_comparison.png")
# pl.close("all")
# et.overplot_data_model(fitted_values, l_param_name,
#                        post_instance.datasimulators.dataset_db, post_instance.dataset_db,
#                        post_instance.noisemodels.dataset_db,
#                        oversamp=30, phasefold=True,
#                        phasefold_kwargs={"planets": ["b", ],
#                                          "P": [4.533460664271991, ],
#                                          "tc": [57741.007471378594, ]})
# pl.savefig("./images/data_comparison_pholded.png")
# pl.close("all")
