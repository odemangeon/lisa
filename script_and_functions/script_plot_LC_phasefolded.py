#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
import matplotlib
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

# matplotlib.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     'font.family': 'serif',
#     'text.usetex': True,
#     'pgf.rcfonts': False})

# Define the object name
obj_name = "TOI-175"

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

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=True)

create_LC_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=kwargs_datasim,
                            planets=planets, star_name="A", datasetnames=datasetnames,
                            # row4datasetname={f"LC_{obj_name}_TESS_0": 0,
                            #                  },
                            remove_GP=False, remove1=True, remove_contamination=False, remove_inst_var=True, remove_decorrelation=True,
                            remove_decorrelation_likelihood=True,
                            LC_fact=1e6,
                            exptime_bin=20 / 60, binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                            one_binning_per_row=True,
                            show_time_from_tic=True, time_fact=24, time_unit="h",
                            # fig_param={'x_lims': {"all": (0, 1.)},
                            #            'ylims_data': (-400, 500),
                            #            'ylims_resi': (-500, 500),
                            #            'pad_data': (-0.86, -0.08),
                            #            'pad_resi': (-0.44, -0.46),
                            #            'indicate_y_outliers_data': False, 'indicate_y_outliers_resi': False,
                            #            'phasefold_central_phase': 0.5,
                            #            },
                            # pl_kwargs={f"LC_{obj_name}_TESS_0": {"data": {'color': 'k', 'alpha': 0.2}, },
                            #            },
                            sharey=True,
                            LC_unit="ppm",
                            )

pl.show()
# pl.savefig(os.path.join(output_folders["plots"], f"LC_PhaseFold_plot{extension_analysis}_paper.pdf"))
# pl.close("all")
