#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
import matplotlib.pyplot as pl

from os import getcwd
from os.path import join
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

AandA_fontsize = 8

# matplotlib.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     'font.family': 'serif',
#     'text.usetex': True,
#     'pgf.rcfonts': False})

# Define the object name
obj_name = "target_name"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Define dataset names to be loaded
datasetnames = None

planets = None

kwargs_datasim = {}

load_from_pickle = True
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

create_LC_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval,
                            planets=planets, datasetnames=datasetnames,
                            datasim_kwargs=kwargs_datasim,
                            row4datasetname={f"LC_{obj_name}_TESS_0": 0,
                                             f"LC_{obj_name}_TESS_1": 0,
                                             f"LC_{obj_name}_TESS_2": 0,
                                             },
                            exptime_bin=20 / 60, binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                            one_binning_per_row=True,
                            show_time_from_tic=True, time_fact=24, time_unit="h",
                            sharey=True,
                            create_axes_kwargs=None,
                            pad=None,
                            indicate_y_outliers=None,
                            # pl_kwargs={f"LC_{obj_name}_TESS_0": {'data': {'fmt': 'o', 'color': 'C1', 'mfc': 'C1', 'alpha': 1., 'label': "TESS0"}, },
                            #            f"LC_{obj_name}_TESS_1": {'data': {'fmt': 'o', 'color': 'C1', 'mfc': 'white', 'alpha': 1., 'label': "TESS1"}, },
                            #            f"LC_{obj_name}_TESS_2": {'data': {'fmt': 'o', 'color': 'C2', 'mfc': 'white', 'alpha': 1., 'label': "TESS2"}, },
                            #            "model": {"color": "C2", "linewidth": 0.75},
                            #            "model_binned": {"color": "C4"},
                            #            "data_binned": {"color": "C3"}
                            #            },
                            xlims={'all': (-3, 3)}, force_xlims=False, ylims=None,
                            rms_kwargs={'do': True, 'format': '.2f'},
                            legend_kwargs=None,
                            show_datasetnames=True,
                            suptitle_kwargs=None,
                            LC_fact=1e6,
                            LC_unit="ppm",
                            fontsize=AandA_fontsize,
                            )

pl.show()
# pl.savefig(os.path.join(output_folders["plots"], f"LC_PhaseFold_plot{extension_analysis}_paper.pdf"))
# pl.close("all")
