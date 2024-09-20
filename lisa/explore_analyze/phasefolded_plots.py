"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from matplotlib.pyplot import figure
from numpy import (linspace, inf, min, max, arange, std, logical_and, zeros, where, sqrt, sum, power,
                   nan, nanstd, concatenate, ones_like, nansum
                   )
from copy import copy
from collections import OrderedDict
from matplotlib.ticker import AutoMinorLocator
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec, SubplotSpec
from matplotlib.figure import Figure
from PyAstronomy.pyasl import foldAt
from loguru import logger
from scipy.stats import binned_statistic
from pandas import DataFrame
from typing import Callable, Dict

from .misc import (AandA_fontsize, check_spec_data_or_resi, check_row4datasetname, check_datasetnameformodel4row,
                   check_spec_by_column_or_row, check_spec_for_data_or_resi_by_column_or_row, do_suptitle,
                   get_pl_kwargs, check_kwargs_by_column_and_row, define_x_or_y_lims, update_data_binned_label,
                   print_rms, set_legend, AandA_full_width, default_figheight_factor
                   )
from .core_plot import PlotsDefinitionPF, ComputedModels_Database, Expression
from .core_compute_load import (load_datasets_and_models, compute_model, get_key_compute_model,
                                is_valid_model_available
                                )
from ..emcee_tools import emcee_tools as et
from ..posterior.core.posterior import Posterior



def create_phasefolded_plots(post_instance:Posterior, df_fittedval:DataFrame,
                             compute_raw_models_func: Callable,
                             plotdef:PlotsDefinitionPF,
                             computedmodels_db:ComputedModels_Database|None=None,
                             split_GP_computation:int|None=None,
                             datasim_kwargs=None,
                             create_axes_main_gridspec:dict|None=None,
                             create_axes_dataresi_gridspec:dict|None=None,
                             show_time_from_T0:bool=False, time_fact:float|None=None, time_unit:str|None=None,
                             indicate_y_outliers:dict|None=None,
                             pad:dict|None=None,
                             legend_kwargs:dict|None=None,
                             npt_model_default:int|None=None,
                             extra_dt_model:float|None=None,
                             fontsize:int=AandA_fontsize,
                             get_key_compute_model_func:Callable=get_key_compute_model,
                             kwargs_get_key_compute_model:Dict|None=None,
                             fig:Figure|None=None,
                             subplotspec:SubplotSpec|None=None,
                             ):
    logger.debug("Start: create_PF_plots")

    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")

    # If no ComputedModels_Database is provided create a new one
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    # Make sure that indicate_y_outliers is well defined
    indicate_y_outliers = check_spec_data_or_resi(spec_user=indicate_y_outliers, l_type_spec=[bool], spec_def=True)

    # Make sure that pad is well defined
    pad = check_spec_data_or_resi(spec_user=pad, l_type_spec=[tuple, list], spec_def=(0.1, 0.1))

    # Create the updated grid space for TS according to the number of rows and cols specified in plotdef
    if create_axes_main_gridspec is None:
        create_axes_main_gridspec = {}
    if subplotspec is None:
        if fig is None:
            fig = Figure()
    if subplotspec is not None:
        gs = GridSpecFromSubplotSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, subplot_spec=subplotspec, **create_axes_main_gridspec)
    else:
        gs = GridSpec(nrows=plotdef.nb_rows, ncols=plotdef.nb_cols, figure=fig, **create_axes_main_gridspec)

    # Make sure that legend_kwargs is well defined
    legend_kwargs = check_kwargs_by_column_and_row(kwargs_user=legend_kwargs, l_row_name=list(range(plotdef.nb_rows)), l_col_name=list(range(plotdef.nb_cols)),
                                                   kwargs_def={'do': False}, kwargs_init={0: {i_row: {'do': True} for i_row in range(plotdef.nb_rows)}}
                                                   )
    
    # Set default values for parameters
    if time_fact is None:
        time_fact = 1.
    if time_unit is None:
        time_unit = 'days'
    if npt_model_default is None:
        npt_model_default = 1000
    if extra_dt_model is None:
        extra_dt_model = 0.
    
    ###########################################
    # Make the data, models and residuals plots
    ###########################################
    rms_values = OrderedDict()
    for i_row in range(plotdef.nb_rows):
        for i_col in range(plotdef.nb_cols):
            logger.debug(f"Doing PF plot for row {i_row}/{plotdef.nb_rows - 1}, column {i_col}/{plotdef.nb_cols - 1}")
            subplotspec_i = gs[i_row, i_col]

            # Create the data and residuals axes and set properties ans style
            (axe_data, axe_resi) = et.add_twoaxeswithsharex(subplotspec_i, fig, gs_from_sps_kw=create_axes_dataresi_gridspec)  # gs_from_sps_kw={"wspace": 0.1}

            axe_resi.set_xlabel(f"time [{time_unit}]", fontsize=fontsize)
            if i_col == 0:
                ylabel_data = plotdef.axes_properties[i_row][i_col]["y_data"].label
                ylabel_resi = plotdef.axes_properties[i_row][i_col]["y_resi"].label
                if ylabel_data is not None:
                    axe_data.set_ylabel(ylabel_data, fontsize=fontsize)
                if ylabel_resi is not None:
                    axe_resi.set_ylabel(ylabel_resi, fontsize=fontsize)
            
            axe_data.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False, labelsize=fontsize)
            axe_data.xaxis.set_minor_locator(AutoMinorLocator())
            axe_data.yaxis.set_minor_locator(AutoMinorLocator())
            axe_data.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axe_data.grid(axis="y", color="black", alpha=.5, linewidth=.5)
            axe_resi.yaxis.set_minor_locator(AutoMinorLocator())
            axe_resi.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelsize=fontsize)
            axe_resi.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axe_resi.grid(axis="y", color="black", alpha=.5, linewidth=.5)

            ######################################
            # Plot the models specified in plotdef
            ######################################


    logger.debug("Done: create_PF_plots")
    return computedmodels_db, rms_values
