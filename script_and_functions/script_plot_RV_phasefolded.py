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
from os.path import join

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.rv_plots import create_RV_phasefolded_plots

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
obj_name = "target_name"

run_folder = os.getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Define dataset names to be loaded
datasetnames = None

planets = None

kwargs_datasim = {}  # RVdrift_tref_name: 56040.0

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

create_RV_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                            planets=planets, datasetnames=datasetnames,
                            datasim_kwargs=kwargs_datasim,
                            # row4datasetname={f"RV_{obj_name}_HARPS_0": 0,
                            #                  f"RV_{obj_name}_HARPS_1": 0,
                            #                  f"RV_{obj_name}_PFS_0": 0,
                            #                  },
                            exptime_bin=1 / 15, binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                            show_time_from_tic=False,  # time_fact=24, time_unit="h",
                            sharey=True,
                            create_axes_kwargs=None,
                            pad=None,
                            indicate_y_outliers=None,
                            one_binning_per_row=True,
                            # pl_kwargs={f"RV_{obj_name}_HARPS_0": {'data': {'fmt': 'o', 'color': 'C1', 'mfc': 'C1', 'alpha': 1., 'label': "HARPS0"}, },
                            #            f"RV_{obj_name}_HARPS_1": {'data': {'fmt': 'o', 'color': 'C1', 'mfc': 'white', 'alpha': 1., 'label': "HARPS1"}, },
                            #            f"RV_{obj_name}_PFS_0": {'data': {'fmt': 'o', 'color': 'C2', 'mfc': 'white', 'alpha': 1., 'label': "PFS"}, },
                            #            "model": {"color": "C2", "linewidth": 0.75},
                            #            "model_binned": {"color": "C4"},
                            #            "data_binned": {"color": "C3"}
                            #            },
                            xlims=None, force_xlims=False, ylims=None,
                            rms_kwargs={'do': True, 'format': '.2f'},
                            legend_kwargs=None,
                            show_datasetnames=True,
                            suptitle_kwargs=None,
                            RV_fact=1e3,  # 1e3,  # Put the RV in m/s they are originally in km/s
                            RV_unit="m/s",
                            fontsize=AandA_fontsize,
                            )
pl.show()
# pl.savefig(os.path.join(output_folders["plots"], f"RV_phasefolded_plot{extension_analysis}_paper.pdf"))
# pl.close("all")
