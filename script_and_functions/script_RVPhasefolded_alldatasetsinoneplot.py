#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of RV data

@TODO:
"""

import os
import matplotlib
import matplotlib.pyplot as pl

from logging import DEBUG, INFO

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.rv_plots import create_RV_phasefolded_plots
from lisa.posterior.exoplanet.model.datasim_creator_rv import RVdrift_tref_name

### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.75

AandA_fontsize = 8

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False})

# Define the object name
obj_name = "HD27969"

# Define dataset names to be loaded
datasetnames = ['RV_HD27969_SOPHIEp_0', ]

planets = None

kwargs_datasim = {}  # RVdrift_tref_name: 56040.0

run_folder = os.getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

load_from_pickle = True
extension_analysis = "_initrun_median"

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=INFO, fh_file="{}.log".format(obj_name))

logger.info("1. Load from pickle if necessary")
if load_from_pickle:
    # recreate post_instance object
    post_instance = cpost.Posterior(object_name=obj_name)
    post_instance.init_from_pickle(pickle_folder=output_folders["pickles_explore"])
    l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

    fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name, extension_analysis=extension_analysis,
                                                                                    folder=output_folders["pickles_analyze"])

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=True)

create_RV_phasefolded_plots(fig=fig,
                            post_instance=post_instance, df_fittedval=df_fittedval, planets=planets,
                            datasetnames=datasetnames,
                            datasim_kwargs=kwargs_datasim,
                            remove_GP=False,
                            phase_binsize=1 / 15, binning_stat="mean", supersamp_bin_model=10, show_binned_model=False,
                            RV_fact=1e3,  # 1e3,  # Put the RV in m/s they are originally in km/s
                            sharey=True,
                            fig_param={'rms_format': '.1f',  # "pad_data": {"b": (0.75, 0.1)}, "pad_resi": (0.2, 0.1)
                                       },
                            pl_kwargs={"RV_HD27969_SOPHIEp_0": {'fmt': 'o', 'color': 'C1', 'mfc': 'white', 'alpha': 1., 'label': "SOPHIE+"},  # 'ms': 14, 'mew': 1, "elinewidth": 5
                                       "model": {"color": "C2", "linewidth": 0.75},
                                       # "modelbinned": {"color": "C4"},
                                       "databinned": {"color": "C3"}  # 'ms': 14, "elinewidth": 5
                                       },
                            # legend_param={"idx_planet": 0, "loc": 1},
                            show_system_name_in_suptitle=True,
                            show_rms_residuals_in_suptitle=True,
                            RV_unit="m/s",
                            )
pl.show()
# pl.savefig(os.path.join(output_folders["plots"], "RV_phasefolded_plot_initrun_median_paper.pdf"))
# pl.close("all")
