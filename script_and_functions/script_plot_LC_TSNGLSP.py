"""
Script to produce pretty plots of LC time series

@TODO:
"""
import os
import matplotlib.pyplot as pl
import dill

# import matplotlib

from os import getcwd
from os.path import join
from logging import DEBUG, INFO

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.lc_plots import create_LC_TSNGLSP_plots

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

extension_analysis = "_initrun_median"

################################
## Load logger and df_fittedval if required
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file=join(output_folders["log"], f"{obj_name}.log"))
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

remove_dict = {'1': True, 'contamination': False, 'inst_var': True, 'stellar_var': False, 'decorrelation': False,
               'decorrelation_likelihood': False, 'GP_model': True}  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation', 'decorrelation_likelihood', 'GP_model'

show_dict = {'inst_var': False, 'stellar_var': False, 'decorrelation': False,
             'decorrelation_likelihood': False, 'GP_model': False, 'model_wGP': True, 
             }  # Possible keys are 'contamination', 'inst_var', 'stellar_var', 'decorrelation', 'decorrelation_likelihood', 'GP_model', 'model_wGP'

datasetnames = None  # e.g. [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

# Common parameters to TS and GLSP
LC_fact = 1e6
LC_unit = 'ppm'

# TS parameters
do_TS = True

row4datasetname = None  # e. g. {f"LC_{obj_name}_CHEOPS_{ii}": 0 for ii in range(3)} 

pl_kwargs = None  # e.g. {f"LC_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}

t_unit = 'BJD - 2,400,000'
exptime_bin = 20 / 60
binning_stat = "mean"
supersamp_bin_model = 10
show_binned_model = {"model": True}

tlims = None
force_xlims = False
ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

# GLSP parameters
do_GLSP = False

period_range = (1e-1, 200)

freq_fact = 1e6
freq_unit = "$\mu$Hz"

freq_lims = (0, 120)

periods = {df_fittedval.loc[f"{obj_name}_b_P"]["value"]: {"vlines_kwargs": {"color": "C3", "linestyle": "dashed"},
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
# There are extra parameters which can be changed in the create_LC_phasefolded_plots below

#########################
# Execution of the script
#########################

if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=output_folders["pickles_explore"])

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

(dico_load, computed_models
 ) = create_LC_TSNGLSP_plots(fig=fig, post_instance=post_instance, 
                             df_fittedval=df_fittedval,
                             datasim_kwargs=kwargs_datasim,
                             datasetnames=datasetnames, 
                             remove_dict=remove_dict,
                             show_dict=show_dict,
                             datasetnames4model4row=None,
                             TS_kwargs={"do": do_TS,
                                        "npt_model": 10000,
                                        "exptime_bin": exptime_bin,
                                        "binning_stat": binning_stat,
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
                             LC_fact=LC_fact,
                             LC_unit=LC_unit,
                             )

if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_TS_GLSP_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

if save_outputs:
    # Save chain in a pickle
    if os.path.isfile(os.path.join(output_folders["pickles_analyze"], f"LC_tsnglsp_ouputs{extension_analysis}.pkl")):
        with open(os.path.join(output_folders["pickles_analyze"], f"LC_tsnglsp_ouputs{extension_analysis}.pkl"), "rb") as fpickle:
            _, computed_models_old = dill.load(fpickle)
    else:
        computed_models_old = None
    if computed_models is None:
        computed_models = computed_models_old
    with open(os.path.join(output_folders["pickles_analyze"], f"LC_tsnglsp_ouputs{extension_analysis}.pkl"), "wb") as fpickle:
        dill.dump((dico_load, computed_models), fpickle)