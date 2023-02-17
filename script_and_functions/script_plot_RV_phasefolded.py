"""
Script to produce pretty plots of phase folded RV time series

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
from lisa.explore_analyze.rv_plots import create_RV_phasefolded_plots

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

save_outputs = True
save_plot = False

planets = None  # e.g. ['b', ]
periods = None  # e.g. [46., ]
periods_remove_or_add_dict = None # e.g. {46.: {'add_dict': {'GP_model': True}}}

kwargs_datasim = {}  # Kwargs for the datasim functions

remove1 = True
remove_contamination = True

datasetnames = None  # e.g. [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

row4datasetname = None  # e. g. {f"LC_{obj_name}_CHEOPS_{ii}": 0 for ii in range(3)} 

pl_kwargs = None  # e.g. {f"LC_{obj_name}_CHEOPS_{ii}": {'data': {"label": None}} for ii in range(3)}

show_time_from_tic = False
time_fact = None
time_unit = None

exptime_bin = 1 / 15
binning_stat = "mean"
supersamp_bin_model = 10
show_binned_model = True

xlims = None
force_xlims = False
ylims = None  # e.g. {"data": {"all": (-250, 500)}, "resi": {"all": (-375, 375)}} 

RV_fact = 1e3
RV_unit = 'm/s'

# These were the most commonly changed parameters.
# There are extra parameters which can be changed in the create_LC_phasefolded_plots below

#########################
# Execution of the script
#########################

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

(dico_load, computed_models
 ) = create_RV_phasefolded_plots(fig=fig, post_instance=post_instance,
                                 df_fittedval=df_fittedval,
                                 datasim_kwargs=kwargs_datasim,
                                 planets=planets, periods=periods,
                                 periods_remove_or_add_dict=periods_remove_or_add_dict,
                                 datasetnames=datasetnames,
                                 row4datasetname=row4datasetname,
                                 datasetnameformodel4row=None,
                                 npt_model=1000,
                                 phasefold_central_phase=0.,
                                 show_time_from_tic=show_time_from_tic, time_fact=time_fact, time_unit=time_unit,
                                 exptime_bin=exptime_bin, binning_stat=binning_stat, supersamp_bin_model=supersamp_bin_model, show_binned_model=show_binned_model,
                                 one_binning_per_row=True,
                                 sharey=True,
                                 create_axes_kwargs=None,
                                 pad=None,
                                 indicate_y_outliers={"data": False, "resi": False},
                                 pl_kwargs=pl_kwargs,
                                 xlims=xlims, force_xlims=force_xlims,
                                 ylims=ylims,
                                 rms_kwargs={'do': True, 'format': '.2f'},
                                 legend_kwargs=None,
                                 show_datasetnames=True,
                                 suptitle_kwargs=None,
                                 RV_fact=RV_fact,
                                 RV_unit=RV_unit,
                                 fontsize=AandA_fontsize,
                                 )

if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_phasefolded_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

if save_outputs:
    # Save chain in a pickle
    with open(os.path.join(output_folders["pickles_analyze"], f"RV_tsnglsp_ouputs{extension_analysis}.pkl"), "wb") as fpickle:
        dill.dump((dico_load, computed_models), fpickle)