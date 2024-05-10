"""
Script to produce pretty plots of IND time series

@TODO:
"""
from loguru import logger

import os
import matplotlib.pyplot as pl
import dill

# import matplotlib

from os import getcwd
from os.path import join

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.ind_plots import create_IND_TSNGLSP_plots

# import sys
# path_pyGLS = "/Users/olivier/Softwares/PyGLS"
# if path_pyGLS not in sys.path:
#     sys.path.append(path_pyGLS)
# from gls_mod import Gls

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

IND_subcat = "FWHM"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

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
## Load df_fittedval if required
if "df_fittedval" not in globals():
    logger.info("Loading df_fittedval from pickle")
    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                    folder=output_folders["pickles_analyze"])
################################


#####################################
# Parameters of the script (continue)
#####################################

save_outputs = True
load_outputs = True
save_plot = False

kwargs_datasim = {}  # Kwargs for the datasim functions

remove_dict = {'inst_var': True, 'stellar_var': True}  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation_likelihood', 'GP'

show_dict = {'stellar_var': False}  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation_likelihood', 'GP'

datasetnames = None  # e.g. [f"IND-FWHM_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

# Common parameters to TS and GLSP
IND_fact = 1
IND_unit = 'km/s'

# TS parameters
do_TS = True

row4datasetname = None  # e. g. {f"IND-FWHM_{obj_name}_CHEOPS_{ii}": 0 for ii in range(3)} 

datasetname4model4row = None  #  e. g. {"model_wGP": {0: f"IND-FWHM_{obj_name}_CHEOPS_0"}} 

pl_kwargs = None  # e.g. {f"IND-FWHM_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}

t_unit = 'BJD - 2,400,000'
exptime_bin = 20 / 60
binning_stat = "mean"
supersamp_bin_model = 10
show_binned_model = {"model": True}

compute_GP_model = True
split_GP_computation = 1000

tlims = None
force_xlims = False
ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

# GLSP parameters
do_GLSP = False

period_range = (1e-2, 500)

freq_fact = 1e6
freq_unit = "$\mu$Hz"

freq_lims = (0, 400)

periods = {df_fittedval.loc[f"b_P"]["value"]: {"vlines_kwargs": {"color": "C3", "linestyle": "dashed"},
                                                          "text_kwargs": {"label": 'P$_b$', 'y_pos': 0.85, 'x_shift': 0.05}
                                                          },
           }
           
fap = {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"},
             "text_kwargs": {"y_shift": 0.08}
             },
       1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"},
           "text_kwargs": {"y_shift": 0.}
           },
       10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"},
            "text_kwargs": {"y_shift": -0.08}
            },
       }

# These were the most commonly changed parameters.
# There are extra parameters which can be changed in the create_IND_phasefolded_plots below

#########################
# Execution of the script
#########################

if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior()
    post_instance.configure_posterior(path_config_file="config_file.py")
    post_instance.create_allfunctions()

file_name_outputs = f"{obj_name}_outputs_IND-{IND_subcat}_plots{extension_analysis}.pk"
file_path_outputs = os.path.join(output_folders['pickles_analyze'], file_name_outputs) 
if any([var not in globals() for var in [f'outputs_load_datasets_and_models_IND', f'computed_models_4_TS_IND']]):
    loaded_outputs= False
    if load_outputs:
        logger.info("Attempting to Load outputs from pickle")
        if os.path.isfile(file_path_outputs):
            with open(file_path_outputs, "rb") as ff:
                dico_outputs = dill.load(ff)
                outputs_load_datasets_and_models_IND = dico_outputs.get('outputs_load_datasets_and_models', None)
                computed_models_4_TS_IND = dico_outputs.get('computed_models_4_TS', None)
                rms_values_TS_IND = dico_outputs.get('rms_values_TS', None)
                loaded_outputs = True
                del dico_outputs
                logger.info(f"Outputs loaded from file {file_path_outputs}.")
        else:
            logger.info(f"Outputs pickle file not found ({file_path_outputs}).")
if not(loaded_outputs):
    outputs_load_datasets_and_models_IND = None
    computed_models_4_TS_IND = None
    rms_values_TS_IND = None

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

(outputs_load_datasets_and_models_IND, computed_models_4_TS_IND, rms_values_TS_IND
 ) = create_IND_TSNGLSP_plots(fig=fig, post_instance=post_instance, 
                             df_fittedval=df_fittedval,
                             datasim_kwargs=kwargs_datasim,
                             datasetnames=datasetnames, 
                             IND_subcat=IND_subcat,
                             remove_dict=remove_dict,
                             show_dict=show_dict,
                             datasetname4model4row=datasetname4model4row,
                             outputs_load_datasets_and_models=outputs_load_datasets_and_models_IND,
                             computed_models_4_TS=computed_models_4_TS_IND,
                             compute_GP_model=compute_GP_model,
                             split_GP_computation=split_GP_computation,
                             TS_kwargs={"do": do_TS,
                                        "npt_model": 5000,
                                        "exptime_bin": exptime_bin,
                                        "binning_stat": binning_stat,
                                        "supersamp_bin_model": supersamp_bin_model,
                                        "show_binned_model": show_binned_model,
                                        "one_binning_per_row": True,
                                        'row4datasetname': row4datasetname,
                                        'pl_kwargs': pl_kwargs,
                                        'tlims': tlims, 
                                        't_unit': t_unit,
                                        # 't_lims_zoom": (2170.5, 2171.5),
                                        'ylims': ylims,
                                        'indicate_y_outliers': {"data": False, "resi": False}
                                        },
                             GLSP_kwargs={"do": do_GLSP,
                                          "period_range": period_range,
                                          "freq_fact": freq_fact,
                                          "freq_unit": freq_unit,
                                          "freq_lims": freq_lims,
                                          # "freq_lims_zoom": (0, 14),
                                          'show_inst_var': False,
                                          'show_decorrelation': True,
                                          'periods': periods,
                                          'fap': fap,
                                          # 'period_no_ticklabels': [10, ],
                                          'gridspec_kwargs': {"wspace": 0.05},
                                          'axeswithsharex_kwargs': {"hspace": 0.1},
                                           # 'legend_param': {'data': {'loc': 'upper center'},
                                           #                  'model': {'loc': 'upper center'},
                                           #                  'resi': {'loc': 'upper center'},
                                           #                  'WF': {'loc': 'upper center'},
                                           #                  },
                                           },
                              suptitle_kwargs={'do': True, 'show_removed': True, 'show_system_name': True},  # None
                              IND_fact=IND_fact,
                              IND_unit=IND_unit,
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
        dico_outputs['outputs_load_datasets_and_models'] = outputs_load_datasets_and_models_IND
    dico_outputs['computed_models_4_TS'] = computed_models_4_TS_IND
    dico_outputs['rms_values_TS'] = rms_values_TS_IND
    with open(file_path_outputs, "wb") as ff:
        dill.dump(dico_outputs, ff)

############
## Save plot
if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"IND-{IND_subcat}_TS_GLSP_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

