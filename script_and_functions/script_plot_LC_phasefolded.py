"""
Script to produce pretty plots of phase folded LC time series

@TODO:
"""
from loguru import logger

import os
import matplotlib.pyplot as pl
import dill
import pandas as pd

# import matplotlib

from os import getcwd
from os.path import join
 
import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.lc_plots import create_LC_phasefolded_plots

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

extension_analysis = "_initrun"

save_outputs = True
load_outputs = True
save_plot = False
save_binned_phasefolded_data = False

split_GP_computation = 1000

planets = None  # e.g. ['b', ]
periods = None  # e.g. [46., ]
periods_remove_or_add_dict = None # e.g. {46.: {'add_dict': {'GP_model': True}}}

kwargs_datasim = {}  # Kwargs for the datasim functions

remove1 = True
remove_contamination = True

datasetnames = None  # e.g. [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

row4datasetname = None  # e. g. {f"LC_{obj_name}_CHEOPS_{ii}": 0 for ii in range(3)} 

pl_kwargs = None  # e.g. {f"LC_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}

show_time_from_tic = True
time_fact = 24
time_unit = "h"

exptime_bin = 20 / 60
binning_stat = "mean"
supersamp_bin_model = 10
show_binned_model = True

xlims = None
force_xlims = False
ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

LC_fact = 1e6
LC_unit = 'ppm'

# These were the most commonly changed parameters.
# There are extra parameters which can be changed in the create_LC_phasefolded_plots below

#########################
# Execution of the script
#########################

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

#################################
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

file_name_outputs = f"{obj_name}_outputs_LC_plots{extension_analysis}.pk"
file_path_outputs = os.path.join(output_folders['pickles_analyze'], file_name_outputs) 
if any([var not in globals() for var in ['outputs_load_datasets_and_models_LC', 'computed_models_4_PF_LC']]):
    loaded_outputs= False
    if load_outputs:
        logger.info("Attempting to Load outputs from pickle")
        if os.path.isfile(file_path_outputs):
            with open(file_path_outputs, "rb") as ff:
                dico_outputs = dill.load(ff)
                outputs_load_datasets_and_models_LC = dico_outputs.get('outputs_load_datasets_and_models', None)
                computed_models_4_PF_LC = dico_outputs.get('computed_models_4_PF', None)
                rms_values_PF_LC = dico_outputs.get('rms_values_PF', None)
                loaded_outputs = True
                del dico_outputs
                logger.info(f"Outputs loaded from file {file_path_outputs}.")
        else:
            logger.info(f"Outputs pickle file not found ({file_path_outputs}).")
if not(loaded_outputs):
    outputs_load_datasets_and_models_LC = None
    computed_models_4_PF_LC = None
    rms_values_PF_LC = None

##############
## Create plot
fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

(outputs_load_datasets_and_models_LC, computed_models_4_PF_LC
 ) = create_LC_phasefolded_plots(fig=fig, post_instance=post_instance, 
                                 df_fittedval=df_fittedval,
                                 datasim_kwargs=kwargs_datasim,
                                 planets=planets, periods=periods,
                                 periods_remove_or_add_dict=periods_remove_or_add_dict,
                                 datasetnames=datasetnames,
                                 row4datasetname=row4datasetname,
                                 datasetnameformodel4row=None,
                                 npt_model=1000,
                                 split_GP_computation=split_GP_computation,
                                 outputs_load_datasets_and_models=outputs_load_datasets_and_models_LC,
                                 computed_models_4_PF=computed_models_4_PF_LC,
                                 phasefold_central_phase=0.5,
                                 remove1=remove1, remove_contamination=remove_contamination,
                                 show_time_from_tic=show_time_from_tic, time_fact=time_fact, time_unit=time_unit,
                                 exptime_bin=exptime_bin, binning_stat=binning_stat, supersamp_bin_model=supersamp_bin_model, show_binned_model=show_binned_model,
                                 one_binning_per_row=True,
                                 sharey=True,
                                 create_axes_kwargs=None,
                                 pad=None,
                                 indicate_y_outliers={"data": False, "resi": False},
                                 pl_kwargs=pl_kwargs,
                                 xlims=xlims, force_xlims=force_xlims,
                                 ylims=ylims,
                                 rms_kwargs={'do': True, 'format': '.2f'},
                                 legend_kwargs=None,
                                 show_datasetnames=True,
                                 suptitle_kwargs=None,
                                 LC_fact=LC_fact,
                                 LC_unit=LC_unit,
                                 fontsize=AandA_fontsize,
                                 )

###############
## Save outputs
if save_outputs:
    if os.path.isfile(file_path_outputs):
        logger.info(f"An output file already exists: {file_path_outputs}.")
        with open(file_path_outputs, "rb") as ff:
            dico_outputs = dill.load(ff)
            logger.info(f"Output file has been loaded  and will be updated ({file_path_outputs}).") 
    else:
        dico_outputs = {}
    if not loaded_outputs:
        dico_outputs['outputs_load_datasets_and_models'] = outputs_load_datasets_and_models_LC
    dico_outputs['computed_models_4_PF'] = computed_models_4_PF_LC
    with open(file_path_outputs, "wb") as ff:
        dill.dump(dico_outputs, ff)

############
## Save plot
if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"LC_PhaseFold_plot{extension_analysis}_paper.pdf"))
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