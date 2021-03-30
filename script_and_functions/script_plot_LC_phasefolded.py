#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
from os import getcwd

import matplotlib.pyplot as pl

from logging import DEBUG, INFO

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.lc_plots import create_LC_phasefolded_plots
# from ipdb import set_trace

### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.75

# Define the object name
obj_name = "TOI-175"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Define dataset names to be loaded
datasetnames = None

planets = None

kwargs_datasim = {}

load_from_pickle = False
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

create_LC_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=kwargs_datasim,
                            planets=planets, star_name="A", datasetnames=None,
                            remove_GP=False, remove1=True, LC_fact=1e6,
                            exptime_bin=5 / 60 / 24, binning_stat="mean", supersamp_bin_model=10, show_binned_model=False,
                            show_time_from_tic=True, time_fact=24, time_unit="h",
                            sharey=True,
                            fig_param={'system_name_4_suptitle': "L 98-59",
                                       'x_lims': {"all": (-1.5, 1.5), "b": (-1.5, 1.5), "c": (-1.8, 1.8), "d": (-1.3, 1.3)},
                                       'rms_format': '.0f',
                                       },
                            pl_kwargs={"LC_TOI-175_TESS_0": {"data": {"show_error": False}}
                                       },
                            legend_param={'loc': 'upper left', "idx_planet": 0},
                            LC_unit="ppm",
                            )

pl.show()
