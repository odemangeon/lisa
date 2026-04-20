"""
Module to create phase folded plots

@TODO:
"""
from __future__ import annotations
from numpy import std, concatenate, isfinite
from collections import OrderedDict
from matplotlib.gridspec import SubplotSpec
from matplotlib.figure import Figure
from loguru import logger
from copy import copy
from pandas import DataFrame
from typing import Callable, Dict
from numpy.typing import NDArray

from .misc import AandA_fontsize, set_legend, create_gridspec, create_data_and_residual_axes, setup_data_and_residual_axes_style
# from .models2computenplot import Models2plotTS, check_Models2plot
from .core_plot import Axes_Properties, YAxis_Properties, PlotsDefinition, ComputedModels_Database, Expression, plot_data_and_resi
from .binning import bin_data_and_resi
from .core_compute_load import compute_model, get_key_compute_model, compute_data_and_resi_for_data2plots
from ..emcee_tools import emcee_tools as et
from ..posterior.core.model.core_model import Core_Model
from ..posterior.core.posterior import Posterior


def create_TS_plots(post_instance:Posterior,
                    compute_raw_models_func: Callable,
                    plotdef:PlotsDefinition_TS,
                    computedmodels_db:ComputedModels_Database|None=None,
                    split_GP_computation:int|None=None,
                    datasim_kwargs:dict|None=None,
                    create_axes_main_gridspec:dict|None=None,
                    create_axes_dataresi_gridspec:dict|None=None,
                    npt_model_default:int|None=None,
                    extra_dt_model:float|None=None,
                    fontsize:int=AandA_fontsize,
                    get_key_compute_model_func:Callable=get_key_compute_model,
                    kwargs_get_key_compute_model:Dict|None=None,
                    fig:Figure|None=None,
                    subplotspec:SubplotSpec|None=None,
                    ):
    logger.debug("Start: create_TS_plots")
    ##############################################
    # Setup figure structure and common parameters
    ##############################################
    logger.debug("Setup figure structure and common parameters")

    # If no ComputedModels_Database is provided create a new one
    if computedmodels_db is None:
        computedmodels_db = ComputedModels_Database()

    # If no fig is provided create a new one
    if fig is None:
        fig = Figure()

    # Create the updated gridspec according to the number of rows and cols specified in plotdef
    gs = create_gridspec(nb_rows=plotdef.nb_rows, nb_cols=plotdef.nb_cols, fig=fig, subplotspec=subplotspec, create_axes_main_gridspec=create_axes_main_gridspec)

    # Set default values for parameters npt_model_default and extra_dt_model
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
            # If there is nothing to plot, just continue
            if not(plotdef.has_something2plot(i_row=i_row, i_col=i_col)):
                continue

            logger.debug(f"Doing TS plot for row {i_row}/{plotdef.nb_rows - 1}, column {i_col}/{plotdef.nb_cols - 1}")
            subplotspec_i = gs[i_row, i_col]

            # Create the data and residuals axes and set properties and style
            axes_properties_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col)
            od_axe = create_data_and_residual_axes(do_residual_axis=axes_properties_i.residuals, fig=fig, subplotspec=subplotspec_i, create_axes_dataresi_gridspec=create_axes_dataresi_gridspec)
            setup_data_and_residual_axes_style(od_axe=od_axe, axes_properties=axes_properties_i, fontsize=fontsize)

            ######################################
            # Plot the models specified in plotdef
            ######################################
            for name_model2plot_i, model2plot_i in plotdef.get_models2plot(i_row=i_row, i_col=i_col).items():
                logger.info(f"Start Plotting model {name_model2plot_i}")
                npt = model2plot_i.npt
                if npt is None:
                    npt = npt_model_default
                if model2plot_i.expression == Expression(expression="decorrelation_likelihood"):
                    times_model2plot_i = model2plot_i.get_times_dataset(post_instance=post_instance)
                else:
                    times_model2plot_i = model2plot_i.get_times(post_instance=post_instance, npt=npt, extra_dt=extra_dt_model)
                # Compute the model
                model_i, model_err_i, _ = compute_model(post_instance=post_instance, df_param_value=model2plot_i.df_param_value, datasim_kwargs=datasim_kwargs,
                                                        compute_raw_models_func=compute_raw_models_func, 
                                                        expression=model2plot_i.expression, times=times_model2plot_i, datasetname=model2plot_i.datasetname,
                                                        exptime=model2plot_i.exptime, supersampling=model2plot_i.supersampling,
                                                        computedmodels_db=computedmodels_db, 
                                                        get_key_compute_model_func=get_key_compute_model_func,
                                                        kwargs_get_key_compute_model=None,
                                                        split_GP_computation=split_GP_computation)
                # Plot
                # Plot the model values
                pl_kwarg_to_use = copy(model2plot_i.pl_kwargs)
                # You are plot data or a modified version of the data
                ebcont = od_axe['data'].errorbar(times_model2plot_i * model2plot_i.pl_factors.time_factor, y=model_i * model2plot_i.pl_factors.value_factor,
                                                 **pl_kwarg_to_use)
                color = ebcont[0].get_color()
                alpha = ebcont[0].get_alpha()
                # Plot the model uncertainty region for models that do not involve data 
                if (model_err_i is not None) and model2plot_i.show_error:
                    pl_kwarg_to_use = copy(model2plot_i.pl_kwargs_error)
                    if not("color" in pl_kwarg_to_use):
                        pl_kwarg_to_use["color"] = color
                    if not("alpha" in pl_kwarg_to_use):
                        if alpha is None:
                            alpha = 1.
                        pl_kwarg_to_use["alpha"] = alpha / 3
                        _ = od_axe['data'].fill_between(times_model2plot_i * model2plot_i.pl_factors.time_factor, (model_i - model_err_i) * model2plot_i.pl_factors.value_factor, (model_i + model_err_i) * model2plot_i.pl_factors.value_factor,
                                                    **pl_kwarg_to_use)

            ##################################################
            # Plot the data and residuals specified in plotdef
            ##################################################
            dico_data = {}  # Will be used for ylims and y outliers indication 
            dico_resi = {}  # Will be used for ylims and y outliers indication
            dico_times = {}  # Will be used for y outliers indication
            pl_kwarg_to_use = {}  # Will be used for y outliers indication

            for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():    
                logger.info(f"Start processing data2plot {name_data2plot_i}")
                # Compute the data, errors and residuals
                (times_dataset_i, data_i, data_err_i, data_err_jitter_i, residuals_i
                 ) = compute_data_and_resi_for_data2plots(data2plot=data2plot_i, post_instance=post_instance, 
                                                          datasim_kwargs=datasim_kwargs, compute_raw_models_func=compute_raw_models_func,
                                                          computedmodels_db=computedmodels_db, 
                                                          get_key_compute_model_func=get_key_compute_model_func, 
                                                          kwargs_get_key_compute_model=kwargs_get_key_compute_model, 
                                                          split_GP_computation=split_GP_computation, 
                                                          name_data2plot=name_data2plot_i)
                # Apply time factor
                times_dataset_i *= data2plot_i.pl_factors.time_factor
                # Apply amplitude factor
                data_i *= data2plot_i.pl_factors.value_factor
                data_err_i *= data2plot_i.pl_factors.value_factor
                data_err_jitter_i *= data2plot_i.pl_factors.value_factor
                residuals_i *= data2plot_i.pl_factors.value_factor
                # Compute the binned data, errors and residuals
                if data2plot_i.exptime > 0:
                    (midbins_i, bindata_i, bindata_std_i, bindata_std_jitter_i, binresi_i
                     ) = bin_data_and_resi(times_dataset=times_dataset_i, data=data_i, data_err=data_err_i, data_err_jitter=data_err_jitter_i, 
                                           residuals=residuals_i, exptime=data2plot_i.exptime, method=data2plot_i.method)
                # Compute the rms of the residuals
                if data2plot_i.exptime > 0:
                    rms_values[name_data2plot_i] = std(binresi_i)
                else:
                    rms_values[name_data2plot_i] = std(residuals_i)
                logger.info(f"RMS {name_data2plot_i} = {rms_values[name_data2plot_i]} {plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.unit} (raw cadence)")
                # Plot the data or binned data
                if data2plot_i.exptime > 0:
                    data_plot_i = bindata_i
                    resi_plot_i = binresi_i
                    data_err_plot_i = bindata_std_i
                    data_err_jitter_plot_i = bindata_std_jitter_i
                    time_plot_i = midbins_i
                else:
                    data_plot_i = data_i
                    resi_plot_i = residuals_i
                    data_err_plot_i = data_err_i
                    data_err_jitter_plot_i = data_err_jitter_i
                    time_plot_i = times_dataset_i
                dico_data[name_data2plot_i] = data_plot_i
                dico_resi[name_data2plot_i] = resi_plot_i 
                dico_times[name_data2plot_i] = time_plot_i
                pl_kwarg_to_use[name_data2plot_i] = plot_data_and_resi(x=dico_times[name_data2plot_i], data=dico_data[name_data2plot_i], 
                                                                       data_err=data_err_plot_i, data_err_jitter=data_err_jitter_plot_i,
                                                                       residuals=dico_resi[name_data2plot_i],
                                                                       dataormulitdata2plot=data2plot_i,
                                                                       axe_data=od_axe["data"], axe_resi=od_axe.get("resi", None))
            
            ##############################################################
            # Plot the multi data and their residuals specified in plotdef
            ##############################################################
            
            for name_multidata2plot_i, multidata2plot_i in plotdef.get_multidatas2plot(i_row=i_row, i_col=i_col).items():
                logger.info(f"Start processing multidata2plot {name_multidata2plot_i}")
                # Compute the data, errors and residuals
                l_data2plot = multidata2plot_i.l_data2plot
                l_name_data2plot = [f"{name_multidata2plot_i}_{ii}" for ii in range(len(l_data2plot))]
                times_dataset_i = []
                data_i = []
                data_err_i = []
                data_err_jitter_i = []
                residuals_i = []
                for name_data2plot_j, data2plot_j in zip(l_name_data2plot, l_data2plot):
                    (times_dataset_j, data_j, data_err_j, data_err_jitter_j, residuals_j
                     ) = compute_data_and_resi_for_data2plots(data2plot=data2plot_j, post_instance=post_instance,
                                                              datasim_kwargs=datasim_kwargs, compute_raw_models_func=compute_raw_models_func,
                                                              computedmodels_db=computedmodels_db, 
                                                              get_key_compute_model_func=get_key_compute_model_func, 
                                                              kwargs_get_key_compute_model=kwargs_get_key_compute_model, 
                                                              split_GP_computation=split_GP_computation, 
                                                              name_data2plot=name_data2plot_j)
                    times_dataset_i.append(times_dataset_j * data2plot_j.pl_factors.time_factor)
                    data_i.append(data_j * data2plot_j.pl_factors.value_factor)
                    data_err_i.append(data_err_j * data2plot_j.pl_factors.value_factor)
                    data_err_jitter_i.append(data_err_jitter_j * data2plot_j.pl_factors.value_factor)
                    residuals_i.append(residuals_j * data2plot_j.pl_factors.value_factor)
                times_dataset_i = concatenate(times_dataset_i)
                data_i = concatenate(data_i)
                data_err_i = concatenate(data_err_i)
                data_err_jitter_i = concatenate(data_err_jitter_i)
                residuals_i = concatenate(residuals_i)
                # Compute the binned data, errors and residuals
                if multidata2plot_i.exptime > 0:
                    (midbins_i, bindata_i, bindata_std_i, bindata_std_jitter_i, binresi_i
                     ) = bin_data_and_resi(times_dataset=times_dataset_i, data=data_i, data_err=data_err_i, data_err_jitter=data_err_jitter_i, 
                                           residuals=residuals_i, exptime=multidata2plot_i.exptime, method=multidata2plot_i.method)
                # Compute the rms of the residuals
                if multidata2plot_i.exptime > 0:
                    rms_values[name_multidata2plot_i] = std(binresi_i)
                else:
                    rms_values[name_multidata2plot_i] = std(residuals_i)
                logger.info(f"RMS {name_multidata2plot_i} = {rms_values[name_multidata2plot_i]} {plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.unit} (raw cadence)")
                # Plot the data or binned data
                if multidata2plot_i.exptime > 0:
                    data_plot_i = bindata_i
                    resi_plot_i = binresi_i
                    data_err_plot_i = bindata_std_i
                    data_err_jitter_plot_i = bindata_std_jitter_i
                    time_plot_i = midbins_i
                else:
                    data_plot_i = data_i
                    resi_plot_i = residuals_i
                    data_err_plot_i = data_err_i
                    data_err_jitter_plot_i = data_err_jitter_i
                    time_plot_i = times_dataset_i
                dico_data[name_multidata2plot_i] = data_plot_i
                dico_resi[name_multidata2plot_i] = resi_plot_i 
                dico_times[name_multidata2plot_i] = time_plot_i
                pl_kwarg_to_use[name_multidata2plot_i] = plot_data_and_resi(x=dico_times[name_multidata2plot_i], data=dico_data[name_multidata2plot_i], 
                                                                            data_err=data_err_plot_i, data_err_jitter=data_err_jitter_plot_i,
                                                                            residuals=dico_resi[name_multidata2plot_i],
                                                                            dataormulitdata2plot=multidata2plot_i,
                                                                            axe_data=od_axe["data"], axe_resi=od_axe.get("resi", None))

            for name_multimodel2plot_i, multimodel2plot_i in plotdef.get_multimodels2plot(i_row=i_row, i_col=i_col).items():
                raise NotImplementedError("Plotting of MultiModel2Plot is not implemented yet")

            ###################################
            # Set ylims and indicate_y_outliers
            ###################################
            logger.debug(f"Setting ylims and indicating outliers for row {i_row}, column {i_col}")
            # Set the y axis limits and indicate outliers for the data and the residuals for the raw cadence
            for axe, data_or_resi, points, pad, indicate_outliers in zip((od_axe['data'], od_axe['resi']), ("data", "resi"), (dico_data, dico_resi), 
                                                                         (plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.pad, plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.pad),
                                                                         (plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.indicate_outliers, plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.indicate_outliers),
                                                                         ):
                # Set the y axis limits
                if data_or_resi == "data":
                    y_lims_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col).ydata.lims
                else:
                    y_lims_i = plotdef.get_axes_properties(i_row=i_row, i_col=i_col).yresi.lims
                if y_lims_i is not None:
                    axe.set_ylim(y_lims_i)

                # Indicate outlier values that are off y-axis with an arrows for raw cadence
                if indicate_outliers:
                    for name_data2plot_i, data2plot_i in plotdef.get_datas2plot(i_row=i_row, i_col=i_col).items():
                        et.indicate_y_outliers(x=dico_times[name_data2plot_i], y=points[name_data2plot_i], ax=axe,
                                                color=pl_kwarg_to_use[name_data2plot_i]["color"],
                                                alpha=pl_kwarg_to_use[name_data2plot_i]["alpha"])

            # # Draw a horizontal line at 0 in the residual plot
            # od_axe['resi'].hlines(0, *current_xlims, colors="k", linestyles="dashed")
            logger.debug(f"Done: Set ylims and indicate outliers for row {i_row}, column {i_col}")

            ############################
            # Set the tlims if provided
            ############################
            logger.debug(f"Setting xlims for row {i_row}, column {i_col}")
            od_axe['data'].set_xlim(plotdef.get_axes_properties(i_row=i_row, i_col=i_col).x.lims)
            logger.debug(f"Done: Set xlims for row {i_row}, column {i_col}")

            ##########################
            # Set the legend if needed
            ##########################
            if plotdef.get_axes_properties(i_row=i_row, i_col=i_col).do_legend:
                set_legend(ax=od_axe['data'], legend_kwargs=plotdef.get_axes_properties(i_row=i_row, i_col=i_col).legend_kwargs, fontsize_def=fontsize)

    logger.debug("Done: TS plot")
    return computedmodels_db, rms_values


class Axes_Properties_TS(Axes_Properties):
    """Class to specify the properties of a plot to be used in plot definition 
    """

    def __init__(self):
        self.__residuals = True
        super(Axes_Properties_TS, self).__init__()

    @property
    def residuals(self):
        return self.__residuals
    
    @residuals.setter
    def residuals(self, new:bool):
        if not(isinstance(new, bool)):
            raise TypeError(f"residuals should be a bool. Got {type(new)}")
        self.__residuals = new
    
    def _init_axes(self):
        self.__ydata = YAxis_Properties()
        if self.residuals:
            self.__yresi = YAxis_Properties()

    @property
    def ydata(self) -> YAxis_Properties:
        return self.__ydata
    
    @property
    def yresi(self) -> YAxis_Properties:
        if self.residuals:
            return self.__yresi
        else:
            raise ValueError(f"Axes_Properties_TS with residuals=False doesn't have a yresi attribute")

class PlotsDefinition_TS(PlotsDefinition):

    def __init__(self, nb_rows:int|None=None, same4allrows:bool=False, nb_cols:int|None=None, same4allcols:bool=False):
        super(PlotsDefinition_TS, self).__init__(nb_rows=nb_rows, same4allrows=same4allrows, nb_cols=nb_cols, same4allcols=same4allcols)

    # Init axes_properties
    def _init_axes_properties(self, nb_rows:int, nb_cols:int):
        self.__axes_properties:tuple[tuple[Axes_Properties_TS, ...], ...] = tuple([tuple([Axes_Properties_TS() for _ in range(nb_cols)]) for _ in range(nb_rows)])

    def get_axes_properties(self, i_row:int|None=None, i_col:int|None=None) -> Axes_Properties_TS:
        """Grid (in the form of a tuple of tuple) of Axes_Properties_TS instances"""
        return self.__axes_properties[self._get_i(idx=i_row, roworcol="row")][self._get_i(idx=i_col, roworcol="col")]

    def set_residuals(self, value, i_row:int|None=None, i_col:int|None=None):
        l_i_row = self._get_l_i(idx=i_row, roworcol='row')
        l_i_col = self._get_l_i(idx=i_col, roworcol='col')
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                self.get_axes_properties(i_row=i_row, i_col=i_col).residuals = value