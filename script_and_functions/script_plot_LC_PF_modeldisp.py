"""
Script to produce pretty plots of phase folded LC time series

@TODO:
"""
from loguru import logger

import os
import matplotlib.pyplot as pl
import dill
import pandas as pd
import random
import json
import emcee
# import matplotlib

from os import getcwd
from os.path import join
from pandas import DataFrame
from collections import OrderedDict

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.lc_plots import create_LC_PF_plots
from lisa.explore_analyze.pf_plots import PlotsDefinition_PF
from lisa.tools.chain_interpreter import ChainsInterpret

### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.75

AandA_fontsize = 8

# matplotlib.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     'font.family': 'serif',
#     'text.usetex': True,
#     'pgf.rcfonts': False})

##########################
# Parameters of the script
##########################
obj_name = "target_name"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

run_name = "initrun"
extension_analysis = "_initrun"

#########
## logger
if 'sinkid_file_explore' in globals():
    logger.remove(sinkid_file_explore)
    del sinkid_file_explore
if 'sinkid_file_analyze' in globals():
    logger.remove(sinkid_file_analyze)
    del sinkid_file_analyze
if 'sinkid_file_plot' not in globals():
    sinkid_file_plot = logger.add(join(output_folders['log'], 'plot.log'), level='DEBUG')

################################
## Load post_instance if required
if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior()
    post_instance.configure_posterior(path_config_file="config_file.py")
    post_instance.create_allfunctions()

################################
## Load df_fittedval if required
if "df_fittedval" not in globals():
    logger.info("Loading df_fittedval from pickle")
    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                    folder=output_folders["pickles_analyze"])
################################

################################
## Load emcee backend if required
if "backend" not in globals():
    backend_filename = f"{obj_name}_Emcee.h5"
    backend_filepath = join(output_folders["pickles_explore"], backend_filename)
    backend = emcee.backends.HDFBackend(backend_filepath, read_only=True, name=run_name)
    nwalkers, nparams = backend.shape
    print(f"The chain stored in {backend_filename} has {nwalkers} walkers and {nparams} parameters.")
################################

################################
## Load thin and burnin if required
if any([var not in globals() for var in ["thin", "burnin"]]):
    # Open the file for reading
    with open(join(output_folders["pickles_analyze"], f'analysis_params{extension_analysis}.json'), 'r') as json_file:
        # Load the dictionary from the file
        analysis_params = json.load(json_file)
        thin = analysis_params["thin"]
        burnin = analysis_params["burnin"]
################################

################################
## Load parameter names if required
if "l_param_name" not in globals():
    with open(join(output_folders["pickles_explore"], f"{obj_name}_param_names.json"), "r") as file:
        l_param_name = json.load(file)
################################


#####################################
# Parameters of the script (continue)
#####################################

save_computedmodels_db = False
load_computedmodels_db = False
overwrite_computedmodels_db = False
save_rms_values_LC = False
overwrite_rms_values_LC = False
save_plot = False
save_binned_phasefolded_data = False

kwargs_datasim:dict = {}  # Kwargs for the datasim functions
npt_model = 50000
extra_dt_model = None
split_GP_computation = 500

fontsize = AandA_fontsize

show_time_from_T0 = True
time_fact = 24. # None, 24.
time_unit = 'h'

LC_fact = 1e6
LC_unit = 'ppm'

plotdef_PF = PlotsDefinition_PF(nb_rows=1, nb_cols=1)

# This is an example of how to fill plotdef_PF and specify what you want to plot
# Modify it to your needs

l_idxdst_CHEOPS_occ = l_idxdst_CHEOPS_all = list(range(5))

orbit_CH = 98.7 # CHEOPS orbit in min
cheops = "CHEOPSPIPE"

l_planet = ["b", ] 

d_plot = {}

for ii, planet in enumerate(l_planet):
    d_plot[planet] = {"T0": df_fittedval.loc[f'{planet}_tic']['value'], "P": df_fittedval.loc[f'{planet}_P']['value'], "i_row": 0, "i_col": ii, "l_nb_dst": l_idxdst_CHEOPS_occ}

nb_random = 10
l_df_param_value = []
chains = backend.get_chain(flat=True, thin=thin, discard=burnin)
for i in range(nb_random):
    random_iteration = random.randint(a=0, b=chains.shape[0]-1)
    l_df_param_value.append(DataFrame({"value": chains[random_iteration, :]}, index=l_param_name))
del chains

for planet in ["b", ]:
    l_expression_and_datasetname = []
    for nb_dst in d_plot[planet]["l_nb_dst"]:
        # If you fixed the contamination to zero, you should remove contam from the expression
        l_expression_and_datasetname.append(("(data - inst_var) / contam - decorrelation_likelihood - 1", f"LC_{obj_name}_{cheops}_{nb_dst}"))    
    plotdef_PF.set_phasefold_properties(T0=d_plot[planet]["T0"], period=d_plot[planet]["P"], phasefold_centralphase=0.5, show_time_from_T0=show_time_from_T0, i_row=d_plot[planet]["i_row"], i_col=d_plot[planet]["i_col"])
    # If you fixed the contamination to zero, you should remove contam from the expression
    plotdef_PF.add_multimodelordata_to_grid(name="data_CH_all", l_expression_and_datasetname=[("(data - inst_var) / contam - decorrelation_likelihood - 1", f"LC_{obj_name}_{cheops}_{nb_dst}") for nb_dst in l_idxdst_CHEOPS_all], 
                                            i_row=d_plot[planet]["i_row"], i_col=d_plot[planet]["i_col"],
                                            pl_kwargs={'color':"k", 'alpha':0.1, 'fmt':'.','show_error': False, 'label':f"CHEOPS"},
                                            time_factor=time_fact, value_factor=LC_fact,
                                            )
    # If you fixed the contamination to zero, you should remove contam from the expression
    plotdef_PF.add_multimodelordata_to_grid(name="data_CH_all_bin", l_expression_and_datasetname=[("(data - inst_var) / contam - decorrelation_likelihood - 1", f"LC_{obj_name}_{cheops}_{nb_dst}") for nb_dst in l_idxdst_CHEOPS_all], 
                                            i_row=d_plot[planet]["i_row"], i_col=d_plot[planet]["i_col"],
                                            exptime=0.5,
                                            pl_kwargs={'color':"k", 'alpha':1, 'fmt':'o','show_error': True, 'label':f"bin: {orbit_CH:.0f}min"},
                                            time_factor=time_fact, value_factor=LC_fact,
                                            )
    # If you fixed the contamination to zero, you should remove contam from the expression
    plotdef_PF.add_modelordata_to_grid(name=f"model_row{d_plot[planet]['i_row']}col{d_plot[planet]['i_col']}", expression="(model - inst_var) / contam - 1", 
                                       datasetname=f"LC_{obj_name}_{cheops}_{nb_dst}", 
                                       time_limits=(d_plot[planet]["T0"] + (0.38 * d_plot[planet]["P"]), d_plot[planet]["T0"] + (0.62 * d_plot[planet]["P"])),
                                       pl_kwargs={'color': 'r', 'label': 'planet model'}, 
                                       time_factor=time_fact, value_factor=LC_fact,
                                       i_row=d_plot[planet]["i_row"], i_col=d_plot[planet]["i_col"])
    for jj, df_param_value_j in enumerate(l_df_param_value):
        # If you fixed the contamination to zero, you should remove contam from the expression
        plotdef_PF.add_modelordata_to_grid(name=f"model_row{d_plot[planet]['i_row']}col{d_plot[planet]['i_col']}_rand{jj}", expression="(model - inst_var) / contam - 1", 
                                           datasetname=f"LC_{obj_name}_{cheops}_{nb_dst}", 
                                           time_limits=(d_plot[planet]["T0"] + (0.38 * d_plot[planet]["P"]), d_plot[planet]["T0"] + (0.62 * d_plot[planet]["P"])),
                                           df_param_value=df_param_value_j,
                                           pl_kwargs={'color': 'r', 'label': None, 'alpha': 0.2}, 
                                           time_factor=time_fact, value_factor=LC_fact,
                                           i_row=d_plot[planet]["i_row"], i_col=d_plot[planet]["i_col"])

plotdef_PF.set_df_param_value(df_param_value=df_fittedval)

plotdef_PF.set_axis_property(value='Time from T0', property='name', axis='x')
plotdef_PF.set_axis_property(value=time_unit, property='unit', axis='x')
plotdef_PF.set_axis_property(value='$\Delta$F / F', property='name', axis='ydata')
plotdef_PF.set_axis_property(value=LC_unit, property='unit', axis='ydata')
plotdef_PF.set_axis_property(value='O-C', property='name', axis='yresi')
plotdef_PF.set_axis_property(value=LC_unit, property='unit', axis='yresi')

plotdef_PF.set_axis_property(value=(-150, 300), property='lims', axis='ydata')
plotdef_PF.set_axis_property(value=(-250, 250), property='lims', axis='yresi')

# periods = None  # e.g. [46., ]
# periods_remove_or_add_dict = None # e.g. {46.: {'add_dict': {'GP_model': True}}}


# xlims = None
# force_xlims = False
# ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

# These were the most commonly changed parameters.
# There are extra parameters which can be changed in the create_LC_phasefolded_plots below


#########################
# Execution of the script
#########################

file_path_computedmodels_db = os.path.join(output_folders['pickles_analyze'], f"{obj_name}_computedmodels_db{extension_analysis}.pk") 
if 'computedmodels_db' not in globals():
    loaded_computedmodels_db = False
    if load_computedmodels_db:
        logger.info("Attempting to Load computedmodels_db from pickle")
        if os.path.isfile(file_path_computedmodels_db):
            with open(file_path_computedmodels_db, "rb") as ff:
                computedmodels_db = dill.load(ff)
                loaded_computedmodels_db = True
                logger.info(f"computedmodels_db loaded from file {file_path_computedmodels_db}.")
        else:
            logger.info(f"computedmodels_db pickle file not found ({file_path_computedmodels_db}).")
    if not loaded_computedmodels_db:
        computedmodels_db = None

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=True)

(computedmodels_db, rms_values_PF_LC
 ) = create_LC_PF_plots(post_instance=post_instance,
                        plotdef=plotdef_PF,
                        computedmodels_db=computedmodels_db,
                        split_GP_computation=split_GP_computation,
                        datasim_kwargs=kwargs_datasim,
                        npt_model_default=npt_model,
                        fontsize=fontsize,
                        fig=fig,
                        )

###############
## Save outputs

if save_computedmodels_db:
    if os.path.isfile(file_path_computedmodels_db) and not(overwrite_computedmodels_db):
        logger.warning(f"A computedmodels_db file already exists: {file_path_computedmodels_db} and overwrite_computedmodels_db is False !")
    else:
        with open(file_path_computedmodels_db, "wb") as ff:
                dill.dump(computedmodels_db, ff)

if save_rms_values_LC:
    file_path_rms_values_PF_LC = os.path.join(output_folders['pickles_analyze'], f"{obj_name}_rms_values_PF_LC{extension_analysis}.pk") 
    save = True
    if os.path.isfile(file_path_rms_values_PF_LC):
        logger.info(f"An rm_PF_LC file already exists: {file_path_rms_values_PF_LC}.")
        if not overwrite_rms_values_LC:
            save = False
    if save:
        with open(file_path_rms_values_PF_LC, "wb") as ff:
                dill.dump(rms_values_PF_LC, ff)

############
## Save plot
if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_PF_GLSP_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

#################################
## Save binned phase folded curve
if save_binned_phasefolded_data:
    df = pd.DataFrame(data={"time for tic [h]": outputs_load_datasets_and_models_LC[0]["phase_folded_binned_times_0"], "binned data [ppm]": outputs_load_datasets_and_models_LC[0]["phase_folded_binned_datas_0"], "binned data err [ppm]": outputs_load_datasets_and_models_LC[0]["phase_folded_binned_data_errs_0"], "binned data err with jitter [ppm]": outputs_load_datasets_and_models_LC[0]["phase_folded_binned_data_err_jitters_0"]},
                      )
    df.to_csv(path_or_buf=os.path.join(output_folders["tables"], f"binned_LC{extension_analysis}.csv"), index=False)
    pl.errorbar(x=df["time for tic [h]"], y=df["binned data [ppm]"], yerr=df["binned data err with jitter [ppm]"])
    pl.show()