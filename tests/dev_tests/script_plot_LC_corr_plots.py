#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
from os import getcwd
from os.path import join

import matplotlib.pyplot as pl
import numpy as np

from logging import DEBUG, INFO
from scipy.stats import binned_statistic
# from astropy.visualization import hist
from astropy.stats import histogram

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml

from lisa.explore_analyze.misc import get_def_output_folders
# from lisa.explore_analyze.lc_plots import create_LC_phasefolded_plots
# from ipdb import set_trace

### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.75

# Define the object name
obj_name = "WASP-14"

run_folder = getcwd()
output_folders = get_def_output_folders(run_folder=run_folder)

# Define dataset names to be loaded
datasetnames = None

indicator_datasetnames_4_datasetnames = {f"LC_{obj_name}_CHEOPS_{id_visit}": [f'IND-ROLL_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-CX_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-CY_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-SMEAR_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-TF_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-BKG_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-DARK_{obj_name}_CHEOPS_{id_visit}',
                                                                              f'IND-CONTA_{obj_name}_CHEOPS_{id_visit}'
                                                                              ]
                                         for id_visit in [1, 2, 3, 4, 5, 6, 7, 8, 101, 102]
                                         }

binning_kwargs = {}
for id_visit in [1, 2, 3, 4, 5, 6, 7, 8, 101, 102]:
    binning_kwargs_id_visit = {f'IND-ROLL_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-CX_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-CY_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-SMEAR_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-TF_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-BKG_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-DARK_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               f'IND-CONTA_{obj_name}_CHEOPS_{id_visit}': {'statistic': 'mean', 'bins': "blocks"},
                               }
    binning_kwargs.update(binning_kwargs_id_visit)

planets = None

kwargs_datasim = {}

extension_analysis = "_initrun_median"

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

if datasetnames is None:
    datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="LC", sortby_instcat=False, sortby_instname=False)

for datasetname in datasetnames:
    # Do the spline decorrelation plots
    plotdecorr_docf = post_instance.datasimulators.dataset_db[f'{datasetname}_plotdecorr_like']
    p_vect = et.get_param_vector(df_val=df_fittedval, l_param_name=plotdecorr_docf.param_model_names_list)
    plotdecorr_docf(p_vect)

    # Do the correlation plots of the residuals including spline decorrelation with the provided indicators
    nb_ind = len(indicator_datasetnames_4_datasetnames.get(datasetname, {}))
    if nb_ind > 0:
        datasim = post_instance.datasimulators.dataset_db[datasetname]
        data = post_instance.dataset_db[datasetname].get_data()
        p_vect = et.get_param_vector(df_val=df_fittedval, l_param_name=datasim.param_model_names_list)
        resi = data - datasim(p_vect=p_vect)
        key_decorr_like = f'{datasetname}_decorr_like'
        if key_decorr_like in post_instance.datasimulators.dataset_db:
            likedecorr = post_instance.datasimulators.dataset_db[f'{datasetname}_decorr_like']
            p_vect = et.get_param_vector(df_val=df_fittedval, l_param_name=likedecorr.param_model_names_list)
            resi -= likedecorr(p_vect)
        for i_ind, ind_dataset_name in enumerate(indicator_datasetnames_4_datasetnames[datasetname]):
            fig, ax = pl.subplots(constrained_layout=True)
            ind_value = post_instance.dataset_db[ind_dataset_name].get_data()
            ax.plot(ind_value, resi, '.')
            if binning_kwargs[ind_dataset_name] is not None:
                if ("bins" in binning_kwargs[ind_dataset_name]) and isinstance(binning_kwargs[ind_dataset_name]["bins"], str):
                    _, binning_kwargs[ind_dataset_name]["bins"] = histogram(ind_value, bins=binning_kwargs[ind_dataset_name]["bins"])
                bin_stat, bin_edges, bin_nb = binned_statistic(ind_value, resi, **binning_kwargs[ind_dataset_name])
                mid_bins = np.diff(bin_edges) / 2 + bin_edges[:-1]
                ax.plot(mid_bins, bin_stat, '-.')
            ax.set_xlabel(ind_dataset_name)
            ax.set_ylabel("Residuals")
            ax.grid(b=True, which='both', axis='y', alpha=0.5)
            pl.savefig(join(output_folders["plots"], f"ResiCorr_{ind_dataset_name}_{extension_analysis}.pdf"))
            # pl.close()

pl.show()
