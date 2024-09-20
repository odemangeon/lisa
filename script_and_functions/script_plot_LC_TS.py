"""
Script to produce pretty plots of LC time series

@TODO:
"""
from loguru import logger

import os
import matplotlib.pyplot as pl
import dill
import collections

# import matplotlib

from os import getcwd
from os.path import join

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost

from lisa.explore_analyze.misc import get_def_output_folders
from lisa.explore_analyze.lc_plots import create_LC_TSNGLSP_plots
from lisa.explore_analyze.core_plot import PlotsDefinition

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

save_computedmodels_db = True
load_computedmodels_db = True
overwrite_computedmodels_db = True
save_rms_values_TS_LC = True
overwrite_rms_values_TS_LC = False
save_plot = False

kwargs_datasim:dict = {}  # Kwargs for the datasim functions

# datasetnames = None # None  # e.g. [f"LC_{obj_name}_CHEOPS_{ii}" for ii in range(3)]

# remove_dict = {'1': True, 'contamination': True, 'inst_var': True, 'stellar_var': False, 'decorrelation': False,
#                'decorrelation_likelihood': True, 'GP': False}  # Possible keys are 'inst_var', 'stellar_var', 'decorrelation', 'decorrelation_likelihood', 'GP'

# Common parameters to TS and GLSP
LC_fact = 1e6
LC_unit = 'ppm'

fontsize = AandA_fontsize

# TS parameters
plotdef_TS = PlotsDefinition()

# This is an example of how to fill plotdef_TS and specify what you want to plot
# Modify it to your needs
for nb_dst in range(1100, 1104):
    plotdef_TS.add_modelordata_to_grid(name=f"data_CH{nb_dst}", expression="(data - inst_var) / contam - decorrelation_likelihood - 1", datasetname=f"LC_{obj_name}_CHEOPS_{nb_dst}",
                                    pl_kwargs={'color':"C0", 'alpha':0.005, 'fmt':'.','show_error': False})
    plotdef_TS.add_modelordata_to_grid(name=f"data_bin_CH{nb_dst}", expression="(data - inst_var) / contam - decorrelation_likelihood - 1", datasetname=f"LC_{obj_name}_CHEOPS_{nb_dst}", exptime=1 / 24, 
                                    pl_kwargs={'color':"C0", 'fmt':'.'})
plotdef_TS.things2plot[f"data_CH{1100}"].pl_kwargs['label'] = "CHEOPS"  
plotdef_TS.things2plot[f"data_bin_CH{1100}"].pl_kwargs['label'] = "CHEOPS bin=1h"  
plotdef_TS.add_modelordata_to_grid(name=f"data_T{56}", expression="(data - inst_var) / contam - decorrelation_likelihood - 1", datasetname=f"LC_{obj_name}_TESS_{56}",
                                pl_kwargs={'color':"C1", 'alpha':0.005, 'fmt':'.', 'label': 'TESS', 'show_error': False})
plotdef_TS.add_modelordata_to_grid(name=f"data_bin_T{56}", expression="(data - inst_var) / contam - decorrelation_likelihood - 1", datasetname=f"LC_{obj_name}_TESS_{56}", exptime=1 / 24,
                                pl_kwargs={'color':"C1", 'fmt':'.', 'label': 'TESS bin=1h'})
plotdef_TS.add_modelordata_to_grid(name="model", expression="(model - inst_var) / contam - 1", datasetname=f"LC_{obj_name}_CHEOPS_{1100}", time_limits=(2805.6,2853.2),
                                pl_kwargs={'color': 'k', 'label': 'planet model'})
plotdef_TS.add_modelordata_to_grid(name="model+GP CH", expression="(model - inst_var) / contam + GP - 1 ", datasetname=f"LC_{obj_name}_CHEOPS_{1100}", time_limits=(2805.6,2841.5),
                                pl_kwargs={'color': 'C0', 'label': 'star+planet model (CHEOPS)'})
plotdef_TS.add_modelordata_to_grid(name="model+GP T", expression="(model - inst_var) / contam + GP - 1 ", datasetname=f"LC_{obj_name}_TESS_{56}",
                                pl_kwargs={'color': 'C1', 'label': 'star+planet model (TESS)'})

plotdef_TS.set_axis_lims(lims=(-1000,1000), i_row=0, i_col=0, which="y_data")
plotdef_TS.set_axis_lims(lims=(-400,400), i_row=0, i_col=0, which="y_resi")

t_unit = 'BJD - 2,457,000'
time_fact = 1.
npt_model = None 
extra_dt_model = None

show_title_TS = True
indicate_y_outliers = {"data": False, "resi": False}
legend_kwargs_TS = {"all": {"do": True}}
pad_TS = None

split_GP_computation = 500

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

file_path_computedmodels_db = os.path.join(output_folders['pickles_analyze'], f"{obj_name}_computedmodels_db{extension_analysis}.pk") 
if 'computedmodels_db' not in globals():
    loaded_computedmodels_db = False
    if load_computedmodels_db:
        logger.info("Attempting to Load computedmodels_db from pickle")
        if os.path.isfile(file_path_computedmodels_db):
            with open(file_path_computedmodels_db, "rb") as ff:
                computedmodels_db = dill.load(ff)
                loaded_computedmodels_db = True
                logger.info(f"computedmodels_db loaded from file {file_path_computedmodels_db}.")
        else:
            logger.info(f"computedmodels_db pickle file not found ({file_path_computedmodels_db}).")
    if not loaded_computedmodels_db:
        computedmodels_db = None

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=False)

TS_kwargs = {}
for key, value in {'npt_model': npt_model,
                   'extra_dt_model': extra_dt_model,
                   't_unit': t_unit,
                   'time_fact': time_fact,
                   'show_title': show_title_TS, 
                   'pad': pad_TS,
                   'indicate_y_outliers': indicate_y_outliers,
                   'legend_kwargs': legend_kwargs_TS 
                   }.items():
    if value is not None:
        TS_kwargs[key] = value

(computedmodels_db, rms_values_TS_LC
 ) = create_LC_TSNGLSP_plots(fig=fig, post_instance=post_instance, 
                             df_fittedval=df_fittedval,
                             datasim_kwargs=kwargs_datasim,
                             plotdef_TS=plotdef_TS,
                             computedmodels_db=computedmodels_db, 
                             split_GP_computation=split_GP_computation,
                             TS_kwargs=TS_kwargs,
                             fontsize=fontsize,
                             LC_fact=LC_fact,
                             LC_unit=LC_unit,
                             )

###############
## Save outputs

if save_computedmodels_db:
    if os.path.isfile(file_path_computedmodels_db) and not(overwrite_computedmodels_db):
        logger.warning(f"A computedmodels_db file already exists: {file_path_computedmodels_db} and overwrite_computedmodels_db is False !")
    else:
        with open(file_path_computedmodels_db, "wb") as ff:
                dill.dump(computedmodels_db, ff)

if save_rms_values_TS_LC:
    file_path_rms_values_TS_LC = os.path.join(output_folders['pickles_analyze'], f"{obj_name}_rms_values_TS_LC{extension_analysis}.pk") 
    save = True
    if os.path.isfile(file_path_rms_values_TS_LC):
        logger.info(f"An rm_TS_LC file already exists: {file_path_rms_values_TS_LC}.")
        if not overwrite_rms_values_TS_LC:
            save = False
    if save:
        with open(file_path_rms_values_TS_LC, "wb") as ff:
                dill.dump(rms_values_TS_LC, ff)

############
## Save plot
if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_TS_GLSP_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

