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
from lisa.explore_analyze.rv_plots import create_RV_iTSNGLSP_plots

# import matplotlib.pyplot as pl
# import numpy as np
# import sys
# import os
# # from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
# from matplotlib.ticker import AutoMinorLocator
# from dill import load
# from copy import deepcopy

# import lisa.posterior.core.posterior as cpost
# import lisa.emcee_tools.emcee_tools as et
# from lisa.emcee_tools.emcee_tools import add_twoaxeswithsharex, add_axeswithsharex
# from lisa.posterior.exoplanet.model.datasim_creator_rv import RVdrift_tref_name
# from lisa.explore_analyze.misc import get_def_output_folders

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
save_plot = False

kwargs_datasim = {}  # Kwargs for the datasim functions

datasetnames = None  # e.g. [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

# What to remove to start with: at the first level of the iterative removal process
remove_dict = {'inst_var': False, 'stellar_var': False, 'decorrelation': False,
               'decorrelation_likelihood': False, 'GP': False}  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation', 'decorrelation_likelihood', 'GP'

# List of what to remove for each iteration
l_iterative_removal = [('stellar_var', ), ('GP', ), ('b', ), ]  # List of tuple because can remove more than one model component at

# What to show to start with: at the first level of the iterative removal process
show_dict = {0: {'model_wGP': True, },
             }  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation', 'decorrelation_likelihood', 'GP', 'model_wGP'

datasetname4model4row = None  #  e. g. {"model_wGP": {0: f"LC_{obj_name}_CHEOPS_0"}} 


# Parameter specific to the GLSP computation

# Common parameters to TS and GLSP
RV_fact = 1
RV_unit = 'm/s'

exptime_bin = 0
binning_stat = "mean"
supersamp_bin_model = 10

# TS parameters
do_TS = True

pl_kwargs = None  # e.g. {f"LC_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}

t_unit = 'BJD - 2,400,000'

compute_GP_model = True
split_GP_computation = 1000

tlims = None
force_xlims = False
ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

# GLSP parameters
do_GLSP = True

period_range = (1e-1, 200)

freq_fact = 1e6
freq_unit = "$\mu$Hz"

freq_lims = (0, 40)
logscale = True

periods = {
           df_fittedval.loc["b_P"]["value"]: {"vlines_kwargs": {"color": "C3", "linestyle": "dashed"},
                                              "text_kwargs": {"label": 'P$_b$', 'y_pos': 0.85, 'x_shift': 0.0}
                                              },
        #    df_fittedval.loc["c_P"]["value"]: {"vlines_kwargs": {"color": "C4", "linestyle": "dashed"},
        #                                       "text_kwargs": {"label": 'P$_c$', 'y_pos': 0.85, 'x_shift': 0.0}
        #                                       },
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
# There are extra parameters which can be changed in the create_LC_phasefolded_plots below

#########################
# Execution of the script
#########################

if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior()
    post_instance.configure_posterior(path_config_file="config_file.py")
    post_instance.create_allfunctions()

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

(dico_load, computed_models
 ) = create_RV_iTSNGLSP_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                              datasim_kwargs=kwargs_datasim, datasetnames=datasetnames, 
                              remove_dict=remove_dict, show_dict=show_dict,
                              l_iterative_removal=l_iterative_removal,
                              datasetname4model4row=datasetname4model4row,
                              compute_GP_model=compute_GP_model, split_GP_computation=split_GP_computation,
                              TS_kwargs={"do": do_TS,
                                         "npt_model": 5000,
                                         "exptime_bin": exptime_bin,
                                         "binning_stat": binning_stat,
                                         "supersamp_bin_model": supersamp_bin_model,
                                         # "show_binned_model": show_binned_model,
                                         'pl_kwargs': pl_kwargs,
                                         'tlims': tlims, 
                                         't_unit': t_unit,
                                         # 't_lims_zoom": (2170.5, 2171.5),
                                         'ylims': ylims,
                                         'indicate_y_outliers': {"data": False, "resi": False},
                                         'rms_kwargs': {'do': False}
                                         },
                              GLSP_kwargs={"do": do_GLSP,
                                           "period_range": period_range,
                                           "freq_fact": freq_fact,
                                           "freq_unit": freq_unit,
                                           "freq_lims": freq_lims,
                                           # "freq_lims_zoom": (0, 14),
                                           'periods': periods,
                                           'fap': fap,
                                           'logscale': logscale,
                                           # 'period_no_ticklabels': [10, ],
                                           'gridspec_kwargs': {"wspace": 0.05},
                                           'axeswithsharex_kwargs': {"hspace": 0.1},
                                           # 'legend_param': {'data': {'loc': 'upper center'},
                                           #                  'model': {'loc': 'upper center'},
                                           #                  'resi': {'loc': 'upper center'},
                                           #                  'WF': {'loc': 'upper center'},
                                           #                  },
                                           'show_WF': False
                                           },
                              suptitle_kwargs={'do': True, 'show_removed': True, 'show_system_name': True},  # None
                              RV_fact=RV_fact,
                              RV_unit=RV_unit,
                              )

if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_TS_iTSNGLSP_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()
