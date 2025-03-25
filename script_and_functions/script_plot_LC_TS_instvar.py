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
from lisa.explore_analyze.lc_plots import create_LC_TS_plots
from lisa.explore_analyze.ts_plots import PlotsDefinition_TS

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
## Load post_instance if required
if "post_instance" not in globals():
    logger.info("Loading post_instance from pickle")
    # recreate post_instance object
    post_instance = cpost.Posterior()
    post_instance.configure_posterior(path_config_file="config_file.py")
    post_instance.create_allfunctions()

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

save_computedmodels_db = False
load_computedmodels_db = False
overwrite_computedmodels_db = False
save_rms_values_LC = False
overwrite_rms_values_LC = False
save_plot = False

kwargs_datasim:dict = {}  # Kwargs for the datasim functions
npt_model = 50000
extra_dt_model = None
split_GP_computation = 500

fontsize = AandA_fontsize

time_fact = None # None, 24.
time_unit = 'BJD - 2.457.000'

LC_fact = 1e6
LC_unit = "ppm"

plotdef_TS = PlotsDefinition_TS(nb_rows=1, nb_cols=5)

# This is an example of how to fill plotdef_TS and specify what you want to plot
# Modify it to your needs

l_idxdst_CHEOPS_occ = l_idxdst_CHEOPS_all = list(range(5))

orbit_CHEOPS = 98.7  # CHEOPS orbit in min
cheops = "CHEOPSPIPE"

d_plot = {}

for ii, idx_dst in enumerate(l_idxdst_CHEOPS_all):
    d_plot[ii] = {"l_nb_dst": [l_idxdst_CHEOPS_all[idx_dst]], 'time_limits': None}

for ii, dico_ii in d_plot.items():
    i_row = 0  # ii // 5
    i_col = ii  # ii % 5
    for nb_dst in dico_ii['l_nb_dst']:
        plotdef_TS.add_modelordata_to_grid(name=f"data_CH{nb_dst}", expression="data - decorrelation_likelihood - 1", 
                                           datasetname=f"LC_{obj_name}_{cheops}_{nb_dst}",
                                           pl_kwargs={'color':"k", 'alpha':0.1, 'fmt':'.','show_error': False},
                                           time_factor=time_fact, value_factor=LC_fact,
                                           i_row=i_row, i_col=i_col)
        plotdef_TS.add_modelordata_to_grid(name=f"data_CH{nb_dst}_bin", expression="data - decorrelation_likelihood - 1", 
                                           datasetname=f"LC_{obj_name}_{cheops}_{nb_dst}",
                                           exptime=orbit_CHEOPS/60/24,
                                           pl_kwargs={'color':"k", 'alpha':1, 'fmt':'o','show_error': True, 'label':f"bin: {orbit_CHEOPS:.1f}min"},
                                           time_factor=time_fact, value_factor=LC_fact,
                                           i_row=i_row, i_col=i_col)
        plotdef_TS.add_modelordata_to_grid(name=f"instvar{nb_dst}", expression="inst_var", 
                                           datasetname=f"LC_{obj_name}_{cheops}_{nb_dst}", time_limits=None,
                                           pl_kwargs={'color': 'g', 'label': None},
                                           time_factor=time_fact, value_factor=LC_fact, 
                                           i_row=i_row, i_col=i_col)
    plotdef_TS.add_modelordata_to_grid(name=f"model_row{i_row}col{i_col}", expression="model - 1", 
                                       datasetname=f"LC_{obj_name}_{cheops}_{dico_ii['l_nb_dst'][0]}", time_limits=dico_ii['time_limits'],
                                       pl_kwargs={'color': 'r', 'label': 'planet model'}, 
                                       time_factor=time_fact, value_factor=LC_fact,
                                       i_row=i_row, i_col=i_col)
    plotdef_TS.things2plot[f"data_CH{0}"].pl_kwargs['label'] = "CHEOPS"
    plotdef_TS.things2plot[f"model_row{i_row}col{i_col}"].pl_kwargs['label'] = "Model"
    plotdef_TS.things2plot[f"instvar{0}"].pl_kwargs['label'] = "Inst Var"
    if i_col != 0:
        axes_properties_ii = plotdef_TS.get_axes_properties(i_row=i_row, i_col=i_col)
        axes_properties_ii.ydata.show_label = False
        # axes_properties_ii.ydata.show_ticklabels = False
        axes_properties_ii.yresi.show_label = False
        axes_properties_ii.yresi.show_ticklabels = False

plotdef_TS.set_df_param_value(df_param_value=df_fittedval)

plotdef_TS.set_axes_property(value=False, property="do_legend")
plotdef_TS.set_axes_property(value=True, property="do_legend", i_row=0, i_col=0)
plotdef_TS.set_axis_property(value='Time', property='name', axis='x')
plotdef_TS.set_axis_property(value=time_unit, property='unit', axis='x')
plotdef_TS.set_axis_property(value='$\Delta$F / F', property='name', axis='ydata')
plotdef_TS.set_axis_property(value=LC_unit, property='unit', axis='ydata')
plotdef_TS.set_axis_property(value='O-C', property='name', axis='yresi')
plotdef_TS.set_axis_property(value=LC_unit, property='unit', axis='yresi')

plotdef_TS.set_axis_property(value=(-1000, 1000), property='lims', axis='yresi')

# show_title_TS = True
# indicate_y_outliers = {"data": False, "resi": False}
# legend_kwargs_TS = {"all": {"do": True}}
# pad_TS = None

#########################
# Execution of the script
#########################

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

fig = pl.figure(figsize=(AandA_full_width, AandA_full_width * default_figheight_factor), constrained_layout=True)

(computedmodels_db, rms_values_TS_LC
 ) = create_LC_TS_plots(fig=fig, post_instance=post_instance,
                        datasim_kwargs=kwargs_datasim,
                        plotdef=plotdef_TS,
                        npt_model_default=npt_model,
                        computedmodels_db=computedmodels_db, 
                        split_GP_computation=split_GP_computation,
                        fontsize=fontsize,
                        )
   
###############
## Save outputs

if save_computedmodels_db:
    if os.path.isfile(file_path_computedmodels_db) and not(overwrite_computedmodels_db):
        logger.warning(f"A computedmodels_db file already exists: {file_path_computedmodels_db} and overwrite_computedmodels_db is False !")
    else:
        with open(file_path_computedmodels_db, "wb") as ff:
                dill.dump(computedmodels_db, ff)

if save_rms_values_LC:
    file_path_rms_values_TS_LC = os.path.join(output_folders['pickles_analyze'], f"{obj_name}_rms_values_TS_LC{extension_analysis}.pk") 
    save = True
    if os.path.isfile(file_path_rms_values_TS_LC):
        logger.info(f"An rm_TS_LC file already exists: {file_path_rms_values_TS_LC}.")
        if not overwrite_rms_values_LC:
            save = False
    if save:
        with open(file_path_rms_values_TS_LC, "wb") as ff:
                dill.dump(rms_values_TS_LC, ff)

############
## Save plot
if save_plot:
    pl.savefig(os.path.join(output_folders["plots"], f"RV_TS_plot{extension_analysis}_paper.pdf"))
    pl.close("all")
else:
    pl.show()

