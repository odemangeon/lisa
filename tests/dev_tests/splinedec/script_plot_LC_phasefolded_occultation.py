#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
from os import getcwd
from os.path import join

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

AandA_fontsize = 8

# Define the object name
obj_name = "WASP-76"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Define dataset names to be loaded
datasetnames = None

planets = None

kwargs_datasim = {}

extension_analysis = "_fuprun2_median"

## logger
logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                        fh_lvl=DEBUG, fh_file=join(output_folders["log"], f"{obj_name}.log"))

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

datasetnames = [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]  # PC datasets
datasetnames += [f"LC_{obj_name}_CHEOPS_{100 + ii}" for ii in range(20)]  # Occ datasets
row4datasetname = {f"LC_{obj_name}_CHEOPS_{ii}": 0 for ii in range(3)}  # PC datasets
row4datasetname.update({f"LC_{obj_name}_CHEOPS_{100 + ii}": 0 for ii in range(20)})  # Occ datasets
pl_kwargs = {f"LC_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}
pl_kwargs.update({f"LC_{obj_name}_CHEOPS_{100 + ii}": {'data': {"label": None}} for ii in range(6)})
pl_kwargs[f"LC_{obj_name}_CHEOPS_0"]['data']["label"] = "CHEOPS"

create_LC_phasefolded_plots(fig=fig, post_instance=post_instance, df_fittedval=df_fittedval, datasim_kwargs=kwargs_datasim,
                            planets=planets, periods=None,
                            datasetnames=datasetnames,
                            row4datasetname=row4datasetname,
                            datasetnameformodel4row=None, npt_model=1000,
                            phasefold_central_phase=0.5,
                            remove1=True, remove_contamination=True,
                            LC_fact=1e6,
                            show_time_from_tic=True, time_fact=24, time_unit="h",
                            exptime_bin=20 / 60, binning_stat="mean", supersamp_bin_model=10, show_binned_model=False,
                            one_binning_per_row=True,
                            sharey=True,
                            create_axes_kwargs=None, pad=None, indicate_y_outliers={"data": False, "resi": False},
                            pl_kwargs=pl_kwargs,
                            xlims={"all": (-5 + df_fittedval.loc[f"{obj_name}_b_P"]["value"] * 24 / 2, 5 + df_fittedval.loc[f"{obj_name}_b_P"]["value"] * 24 / 2)},
                            force_xlims=True, ylims={"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}},
                            rms_kwargs=None,
                            legend_kwargs=None,
                            show_datasetnames=True,
                            suptitle_kwargs=None,
                            LC_unit="ppm",
                            fontsize=AandA_fontsize
                            )

pl.show()
