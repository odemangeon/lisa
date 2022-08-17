"""Making plots that show all the RV data on the same plot (with the delta RV and the v0 removed)
modelsNresiduals
"""
import matplotlib.pyplot as pl
import os

import matplotlib

import lisa.posterior.core.posterior as cpost
import lisa.emcee_tools.emcee_tools as et
from lisa.posterior.exoplanet.model.gravgroup.datasim_creator_rv import RVdrift_tref_name
from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.rv_plots import create_RV_TSNGLSP_plots

from logging import DEBUG, INFO
from os.path import join

import lisa.tools.mylogger as ml

# import sys
# path_pyGLS = "/Users/olivier/Softwares/PyGLS"
# if path_pyGLS not in sys.path:
#     sys.path.append(path_pyGLS)
# from gls_mod import Gls

### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.6

AandA_fontsize = 8

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False})

# Define the object name
obj_name = "HD207496"

# Define dataset names to be loaded
datasetnames = None  # [f'RV_{obj_name}_SOPHIEp_0', f'RV_{obj_name}_SOPHIE_0', f'RV_{obj_name}_ELODIE_0', ]  #

planets = None

kwargs_datasim = {}

run_folder = os.getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

extension_analysis = "_initrun_median"

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file=join(output_folders["log"], f"{obj_name}.log"))

if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=output_folders["pickles_explore"])

if "df_fittedval" not in globals():
    logger.info("Loading df_fittedval from pickle")
    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                    folder=output_folders["pickles_analyze"])

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

create_RV_TSNGLSP_plots(fig=fig,
                        post_instance=post_instance, df_fittedval=df_fittedval, planets=planets,
                        datasetnames=datasetnames, datasim_kwargs=kwargs_datasim,
                        remove_inst_var=False, remove_stellar_var=True, remove_decorrelation=True,
                        remove_decorrelation_likelihood=True, remove_GP_dataNmodel=True, remove_GP_residual=True,
                        fig_param={'gridspec_kwargs': {"top": 0.88, 'bottom': 0.08, 'right': 0.95, 'left': 0.07, 'wspace': 0.17},
                                   },
                        TS_kwargs={"do": True,
                                   "exptime_bin": 1,
                                   "binning_stat": 'median',
                                   # 'datasets_per_row': {f"RV_{obj_name}_SOPHIE_0": 0, },
                                   "one_binning_per_row": True,
                                   "pl_kwargs": {# f"RV_{obj_name}_SOPHIEp_0": {'fmt': 'o', 'color': 'C1', 'mfc': 'white', 'alpha': 1., 'label': "SOPHIE+"},  # 'ms': 14, 'mew': 1, "elinewidth": 5
                                                 # f"RV_{obj_name}_SOPHIE_0": {'fmt': 'o', 'color': 'C1', 'mfc': 'C1', 'ms': 4, 'alpha': 1., 'label': "SOPHIE"},
                                                 # f"RV_{obj_name}_ELODIE_0": {'fmt': 'o', 'color': 'C0', 'mfc': 'white', 'ms': 4, 'alpha': 1., 'label': "ELODIE"},
                                                 # "model": {"color": "C2", "linewidth": 0.75},
                                                 },
                                   "t_unit": "BJD - 2,400,000",
                                   # "t_lims_zoom": (58000, 59000),
                                   # 'pad_data': (0.5, 0.5),
                                   # "pad_resi": (0.1, -0.2),
                                   'axeswithsharex_kwargs': {"hspace": 0.1}
                                   },
                        GLSP_kwargs={"do": True,
                                     "period_range": (0.1, 5000),
                                     "freq_fact": 1e6,
                                     "freq_unit": "$\mu$Hz",
                                     "freq_lims": (0, 14),
                                     "freq_lims_zoom": (0, 1e6 / (100 * 24 * 60 * 60)),
                                     'periods': {df_fittedval.loc[f"{obj_name}_b_P"]["value"]: {"vlines_kwargs": {"color": "C3", "linestyle": "dashed"},
                                                                                                "text_kwargs": {"label": 'P$_b$', 'y_pos': 0.85, 'x_shift': 0.05}},
                                                 },
                                     'fap': {0.1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dotted"},
                                                   "text_kwargs": {"y_shift": 0.08}},
                                             1: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashdot"},
                                                 "text_kwargs": {"y_shift": 0.}},
                                             10: {"hlines_kwargs": {"color": "k", "linewidth": 0.8, "linestyle": "dashed"},
                                                  "text_kwargs": {"y_shift": -0.08}},
                                             },
                                     # 'period_no_ticklabels': [100, 10],
                                     # 'gridspec_kwargs': {"wspace": 0.05},
                                     # 'axeswithsharex_kwargs': {"hspace": 0.1},
                                     # 'legend_param': {'data': {'loc': 'upper center'},
                                     #                  'model': {'loc': 'upper center'},
                                     #                  'resi': {'loc': 'upper center'},
                                     #                  'WF': {'loc': 'upper center'},
                                     #                  },
                                     },
                        suptitle_kwargs={'do': True, 'show_removed': True, 'show_system_name': True},  # None
                        RV_fact=1e3,  # 1e3,  # Put the RV in m/s they are originally in km/s
                        RV_unit="m/s",
                        )

pl.show()
# pl.savefig(os.path.join(output_folders["plots"], f"RV_TS_GLSP_plot{extension_analysis}_paper.pdf"))
# pl.close("all")
