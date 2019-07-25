#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce pretty plots of LC data

@TODO:
"""
from os import getcwd, makedirs
from os.path import join

import numpy as np

from logging import DEBUG, INFO
from matplotlib.gridspec import GridSpec
from copy import deepcopy
from collections import OrderedDict
from PyAstronomy.pyasl import foldAt

from fig_styler import styler

import lisa.emcee_tools.emcee_tools as et
import lisa.posterior.core.posterior as cpost
import lisa.tools.mylogger as ml
from lisa.tools.miscellaneous import interpret_data_filename

from scipy.stats import binned_statistic
from matplotlib.offsetbox import AnchoredText
# from pandas import read_table

from lisa.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from lisa.posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add

# from ipdb import set_trace

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


@styler
def create_LC_plots(fig, datasetnames, planets, periods, tcs, datasim_dbf, dataset_db, model_instance,
                    fitted_values, l_param_name, star, exptime_bin=0.005555555556, supersamp_bin_model=10,
                    fig_param=None, pl_kwargs=None, show_legend=True, legend_param=None, *args, **kwargs):
    """Produce a clean LC plot.

    :param fig: Figure instance (provided by the styler)
    :param datasetnames: List providing the datasets to load and use
    :param list_of_str planets: List of planet names (used to infer the number of planets and create the good number of subplots)
    :param periods: Orbital periods for each planets (used to phase fold)
    :param tcs: Time of inferior conjunction for each planet (used to phase fold)
    :param model_instance: Core_Model subclass instance
    :param fitted_values: Fitted values
    :param list_of_str l_param_name: List of parameter names
    :param star: Star instance
    :param float exptime_bin: Width of the bins used for the binning in days (default 0.005555555556 days, 8 min)
    :param int supersamp_bin_model: Supersampling factor for the binned model (default 10 days, 8 min)
    :param dict fig_param: Dictionary providing keyword arguments for the figure definition and settings:
        - 'right', 'left', 'bottom', 'top' keywords can be defined and they will be passed to the GridSpec init function
        - 'x_ylabel_coord' to shift from the y axis to the label
        - 'add_axeswithsharex_kw' dictionary of kwargs to pass to add_axeswithsharex which creates the
           data + residuals axes.
        - 'gs_from_sps_kw' dictionary of kwargs which will be passed on to add_twoaxeswithsharex_perplanet.
        - 'pad_data': float of Iterable of 2 floats which define the bottom and top pad to apply for data axes.
        - 'pad_resi': float of Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
        - 'y_unit': unit of RVs
        - 'phase_lims': dictionary with for possible keys "all" or any of the planet names. The values are
           tuples giving the minimum and maximum phases for all planets or a specific ones.
    :param dict pl_kwargs: Dictionary with keys a instrument name (ex: "ESPRESSO") and values
        a dictionary with 4 possible keys "data", "databinned", "model" and "modelbinned" that will be
        passed as keyword arguments to the plotting functions
    :param bool show_legend: If True, show the legend
    :param legend_param: Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True)
    :param bool show_xlabel: If True, show the x label
    :param bool show_ylabel: If True, show the y labels
    """

    nplanet = len(planets)
    ndataset = len(datasetnames)

    ###########
    # Load Data
    ###########

    # Load the defined datasets
    dico_dataset = {}
    dico_kwargs = {}
    for datasetname in datasetnames:
        dico_dataset[datasetname] = dataset_db[datasetname]
        dico_kwargs[datasetname] = dico_dataset[datasetname].get_kwargs()

    ###################
    # Plots preparation
    ###################

    fontsize = 5

    # Create the gridspec
    if fig_param is None:
        fig_param = {}
    left = fig_param.get("left", 0.17)
    right = fig_param.get("right", 0.98)
    top = fig_param.get("top", 0.98)
    bottom = fig_param.get("bottom", 0.05)
    hspace = fig_param.get("hspace", 0.05)
    # hspaceothers_fact = fig_param.get("hspaceothers", 0.12)
    h_dataset = (1 - (1 - top) - bottom - 3 / 4 * hspace * (1 + ndataset)) / (1 + 4 / 3 * ndataset)

    x_ylabel_coord = fig_param.get("x_ylabel_coord", -0.15)
    phase_lims = fig_param.get("phase_lims", {})
    phase_min_all, phase_max_all = phase_lims.get("all", (-0.5, 0.5))

    gs = GridSpec(nrows=ndataset, ncols=1,
                  left=left, bottom=bottom, right=right, top=top,
                  wspace=None, hspace=(hspace / 2 / (4 / 3 * h_dataset + (ndataset - 1) *
                                       hspace / 2)))

    # Set parameters for the instrument gridspec
    add_axeswithsharex_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot
    add_axeswithsharex_kw.update(fig_param.get("add_axeswithsharex_kw", {}))
    gs_from_sps_kw = {"wspace": 0.2}
    gs_from_sps_kw.update(fig_param.get("gs_from_sps_kw", {}))

    # Set the plots keywords arguments
    pl_kwarg_data = {"color": None, "fmt": ".", "alpha": 0.05}
    pl_kwarg_databinned = {"color": "r", "fmt": ".", "alpha": 1.0}

    pl_kwarg_modelraw = {"color": "k", "fmt": '', "alpha": 1., "linestyle": "--", "label": "model"}
    pl_kwarg_modelbinned = {"color": "k", "fmt": '', "alpha": 1., "label": "model: bin={:.2f}h".format(exptime_bin * 24)}  # , "linestyle": "-"

    # Get the units of the LCs
    y_unit = fig_param.get("y_unit", r"w/o unit")

    # Set the keywords arguments for the plot function (color, alpha, ...)
    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    for datasetname in datasetnames:
        filename_info = interpret_data_filename(datasetname)
        pl_kwarg_final[datasetname] = {"model": deepcopy(pl_kwarg_modelraw),
                                       "modelbinned": deepcopy(pl_kwarg_modelbinned),
                                       "data": {"label": "data", },
                                       "databinned": {"label": "data: bin={:.2f}h".format(exptime_bin * 24), }
                                       }
        pl_kwarg_final[datasetname]["data"].update(deepcopy(pl_kwarg_data))
        pl_kwarg_final[datasetname]["databinned"].update(deepcopy(pl_kwarg_databinned))
        # Update with the user's inputs
        pl_kwarg_final[datasetname]["data"].update(pl_kwargs.get(datasetname, {}).get('data', {}))
        pl_kwarg_final[datasetname]["databinned"].update(pl_kwargs.get(datasetname, {}).get('databinned', {}))
        pl_kwarg_final[datasetname]["model"].update(pl_kwarg_final.get(datasetname, {}).get('model', {}))
        pl_kwarg_final[datasetname]["modelbinned"].update(pl_kwarg_final.get(datasetname, {}).get('modelbinned', {}))

    # Create the axes per planet and set the titles and labels and the ArchorBox with the instrument name
    axes_data, axes_resi = {}, {}
    for ii, datasetname in enumerate(datasetnames):
        # Create the axes
        (axes_data[datasetname], axes_resi[datasetname]
         ) = et.add_twoaxeswithsharex_perplanet(gs[ii], nplanet=nplanet, fig=fig, gs_from_sps_kw=gs_from_sps_kw,
                                                add_axeswithsharex_kw=add_axeswithsharex_kw)
        # Format ticks, labels, titles
        for jj, planet_name in enumerate(planets):
            # set ticks
            axes_data[datasetname][jj].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_resi[datasetname][jj].tick_params(axis='both', which='major', labelsize=fontsize)
            # Set title with planet name on the first row
            if ii == 0:
                axes_data[datasetname][jj].set_title("{}{}".format(star.name.prefix.get(), planet_name), fontsize=fontsize)
            # Set x label for the last row
            if ii == ndataset - 1:
                axes_resi[datasetname][jj].set_xlabel("Orbital phase", fontsize=fontsize)
            # Set y labels on the first column and align them, also set the Anchor boxes
            if jj == 0:
                axes_data[datasetname][jj].set_ylabel(r"Normalised Flux [{}]".format(y_unit), fontsize=fontsize)
                axes_resi[datasetname][jj].set_ylabel(r"O - C [{}]".format(y_unit), fontsize=fontsize)
                axes_data[datasetname][jj].yaxis.set_label_coords(x_ylabel_coord, 0.5)
                axes_resi[datasetname][jj].yaxis.set_label_coords(x_ylabel_coord, 0.5)

                filename_info = interpret_data_filename(datasetname)
                anchored_text_inst = AnchoredText(filename_info["inst_name"] + "({})".format(filename_info["number"]),
                                                  loc=3)  # loc=3 is 'lower left'
                anchored_text_inst.set_alpha(0.5)
                axes_data[datasetname][jj].add_artist(anchored_text_inst)

    # Number of point for plotting the model
    npt_model = 1000

    for jj, planet_name in enumerate(planets):

        ##################################################
        # Compute the phases associated to the time values
        ##################################################

        phases = OrderedDict()
        Per = periods[planet_name]
        tc = tcs[planet_name]
        # print(Per, tc)

        phase_min_pl, phase_max_pl = phase_lims.get(planet_name, (phase_min_all, phase_max_all))

        phase_min_data = np.inf
        phase_max_data = -np.inf
        for datasetname in datasetnames:
            phases[datasetname] = (foldAt(dico_kwargs[datasetname]["t"], Per, T0=(tc + Per / 2)) - 0.5)
            if np.min(phases[datasetname]) < phase_min_data:
                phase_min_data = np.min(phases[datasetname])
            if np.max(phases[datasetname]) > phase_max_data:
                phase_max_data = np.max(phases[datasetname])

        if phase_min_data < phase_min_pl:
            phase_min_data = phase_min_pl
        if phase_max_data > phase_max_pl:
            phase_max_data = phase_max_pl

        # Define t and phase min and max for plotting the model
        tmin_model = tc + Per * phase_min_data
        tmax_model = tc + Per * phase_max_data

        ########################
        # Load datasim functions
        ########################
        datasim_docfunc = {}
        for datasetname in datasetnames:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname)
            datasim_docfunc[datasetname] = datasim_dbf.instrument_db[instmod_fullname_key]

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        data_err = OrderedDict()
        dico_jitter = {}
        for datasetname in datasetnames:
            dico_jitter[datasetname] = {}
            data_err[datasetname] = dico_kwargs[datasetname]["data_err"]
            inst_mod_fullname = datasim_dbf.get_instmod_fullname(datasetname)
            inst_mod = model_instance.instruments[inst_mod_fullname]
            noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
            if noise_model.has_jitter:
                dico_jitter[datasetname]["type"] = noise_model.jitter_type
                if inst_mod.jitter.free:
                    idx_jitter = l_param_name.index(inst_mod.jitter.get_name(include_prefix=True, recursive=True))
                    dico_jitter[datasetname]["value"] = fitted_values[idx_jitter]
                else:
                    dico_jitter[datasetname]["value"] = inst_mod.jitter.value
                if dico_jitter[datasetname]["type"] == "multi":
                    data_err[datasetname] = np.sqrt(apply_jitter_multi(data_err[datasetname], dico_jitter[datasetname]["value"]))
                elif dico_jitter[datasetname]["type"] == "add":
                    data_err[datasetname] = np.sqrt(apply_jitter_add(data_err[datasetname], dico_jitter[datasetname]["value"]))
                else:
                    raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            else:
                dico_jitter[datasetname]["type"] = None
                dico_jitter[datasetname]["value"] = None

        ###################
        # Load OOT_var info
        ###################
        OOT_var = OrderedDict()
        # For each dataset
        for datasetname in datasetnames:
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname)
            instmodobj_key = model_instance.instruments[instmod_fullname_key]
            if instmodobj_key.get_with_OOT_var():
                OOT_var[datasetname] = np.zeros_like(dico_kwargs[datasetname]["t"])
                for order in range(instmodobj_key.get_OOT_var_order() + 1):
                    OOT_var_name = instmodobj_key.get_OOT_param_name(order)
                    OOT_var_param = instmodobj_key.parameters[OOT_var_name]
                    OOT_var_paramname = OOT_var_param.full_name
                    if OOT_var_param.free:
                        idx = l_param_name.index(OOT_var_paramname)
                        OOT_var_paramvalue = fitted_values[idx]
                    else:
                        OOT_var_paramvalue = OOT_var_param.value
                    OOT_var[datasetname] += OOT_var_paramvalue * (dico_kwargs[datasetname]["t"] -
                                                                  dico_kwargs[datasetname]["tref"])**order
            else:
                OOT_var[datasetname] = None

        ##############
        # Bin the data
        ##############
        # Define the phase bins for the binned data/resi plot
        bin_size = exptime_bin / Per

        bins = {}
        binval = {}
        binstd = {}
        midbins = {}
        for datasetname in datasetnames:
            binval[datasetname] = {}
            nb_key = len(dico_kwargs[datasetname])
            bins[datasetname] = np.arange(phase_min_data - (ii * bin_size / nb_key),
                                          phase_max_data + bin_size, bin_size)
            midbins[datasetname] = bins[datasetname][:-1] + bin_size / 2
            # Bin the data
            if OOT_var[datasetname] is None:
                data_inst_key = dico_kwargs[datasetname]["data"]
            else:
                data_inst_key = dico_kwargs[datasetname]["data"] - OOT_var[datasetname]
            filename_info = interpret_data_filename(datasetname)
            if filename_info["inst_name"] == "WASP":  # For the WASP data the transit is not visible in mean but is in
                # median
                binning_stat = "median"
            else:
                binning_stat = "mean"
            (binval[datasetname]["corr"],  # This corr binned values are not used right decide if it makes sense to keep it for inst_name plot only
             binedges_inst,
             binnb_inst) = binned_statistic(phases[datasetname], data_inst_key,
                                            statistic=binning_stat, bins=bins[datasetname],
                                            range=(phase_min_data, phase_max_data))
            (binval[datasetname]["uncorr"],
             binedges_inst,
             binnb_inst) = binned_statistic(phases[datasetname], dico_kwargs[datasetname]["data"],
                                            statistic=binning_stat, bins=bins[datasetname],
                                            range=(phase_min_data, phase_max_data))

            # Compute the error bars on the binned data
            nbin_inst_key = len(bins[datasetname]) - 1
            binstd[datasetname] = np.zeros(nbin_inst_key)
            bincount_inst = np.zeros(nbin_inst_key)
            for ii in range(nbin_inst_key):
                bincount_inst[ii] = len(np.where(binnb_inst == (ii + 1))[0])
                if bincount_inst[ii] > 0.0:
                    binstd[datasetname][ii] = np.sqrt(np.sum(np.power((data_err[datasetname]
                                                                       [binnb_inst == (ii + 1)]),
                                                                      2.)) /
                                                      bincount_inst[ii]**2)
                else:
                    binstd[datasetname][ii] = np.nan

        ###############################
        # Plot the data and binned data
        ###############################
        data_pl = OrderedDict()
        databinned_pl = OrderedDict()
        pad_data = fig_param.get("pad_data", (0.1, 0.1))
        for datasetname in datasetnames:
            # The data to plot for a planet and an instrument are the raw data to which you substract
            # the other planet contributions

            # Remove the other planets contributions
            # Get the current instrument model and noise model
            inst_mod_fullname = datasim_dbf.get_instmod_fullname(datasetname)
            inst_mod = model_instance.instruments[inst_mod_fullname]
            noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)

            # Get the datasims for the other planets
            l_datasim_db_docfunc_others = []
            for plnt in planets:
                if plnt == planet_name:
                    continue
                else:
                    l_datasim_db_docfunc_others.append(datasim_dbf.instrument_db[inst_mod_fullname][plnt + "_only"])

            # Compute and remove the other planet contribution
            data_pl[datasetname] = dico_kwargs[datasetname]["data"]
            for datasim_db_docfunc_other in l_datasim_db_docfunc_others:
                kwargs_dataset = dico_kwargs[datasetname].copy()
                kwargs_dataset.pop("data_err")
                kwargs_dataset.pop("data")
                model, _, _ = et.compute_model(kwargs_dataset.pop("t"),
                                               datasim_db_docfunc_other,
                                               fitted_values, l_param_name,
                                               datasim_kwargs=kwargs_dataset,
                                               noise_model=noise_model,
                                               model_instance=model_instance)
                modelbinned, _, _ = et.compute_model(midbins[datasetname], datasim_db_docfunc_other,
                                                     fitted_values, l_param_name,
                                                     datasim_kwargs=kwargs_dataset, supersamp=supersamp_bin_model,
                                                     exptime=exptime_bin,
                                                     noise_model=noise_model,
                                                     model_instance=model_instance)
                data_pl[datasetname] = data_pl[datasetname] - model
                databinned_pl[datasetname] = binval[datasetname]["uncorr"] - modelbinned

            # Plot the data
            # print(dico_jitter[datasetname])
            ebcont, _, _ = et.plot_phase_folded_timeserie(t=dico_kwargs[datasetname]["t"],
                                                          data=data_pl[datasetname],
                                                          data_err=dico_kwargs[datasetname]["data_err"],
                                                          jitter=dico_jitter[datasetname]["value"],
                                                          jitter_type=dico_jitter[datasetname]["type"],
                                                          Per=Per, tref=tc,
                                                          ax=axes_data[datasetname][jj],
                                                          pl_kwargs=pl_kwarg_final[datasetname]["data"],
                                                          )
            ebcont_binned = axes_data[datasetname][jj].errorbar(midbins[datasetname], databinned_pl[datasetname],
                                                                yerr=binstd[datasetname],
                                                                **pl_kwarg_final[datasetname]["databinned"])
            if pl_kwarg_final[datasetname]["data"]["color"] is None:
                pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
            if pl_kwarg_final[datasetname]["databinned"]["color"] is None:
                pl_kwarg_final[datasetname]["databinned"]["color"] = ebcont_binned[0].get_color()
            # Set the y axis limits
            et.auto_y_lims(data_pl[datasetname], axes_data[datasetname][jj], pad=pad_data)
            # Indicate values that are off y-axis with anarrows
            et.indicate_y_outliers(x=phases[datasetname], y=data_pl[datasetname], ax=axes_data[datasetname][jj],
                                   color=pl_kwarg_final[datasetname]["data"]["color"],
                                   alpha=pl_kwarg_final[datasetname]["data"]["alpha"])
            et.indicate_y_outliers(x=midbins[datasetname], y=binval[datasetname]["uncorr"], ax=axes_data[datasetname][jj],
                                   color=pl_kwarg_final[datasetname]["databinned"]["color"],
                                   alpha=pl_kwarg_final[datasetname]["databinned"]["alpha"])

        #################################
        # Plot the model and binned model
        #################################
        for datasetname in datasetnames:
            et.plot_model(tmin_model, tmax_model, npt_model, datasim_docfunc[datasetname][planet_name],
                          fitted_values, l_param_name, plot_phase=True, Per=Per, tref=tc,
                          pl_kwargs_model=pl_kwarg_final[datasetname]["model"],
                          ax=axes_data[datasetname][jj])
            et.plot_model(tmin_model, tmax_model, npt_model, datasim_docfunc[datasetname][planet_name],
                          fitted_values, l_param_name, supersamp=supersamp_bin_model, exptime=exptime_bin,
                          plot_phase=True, Per=Per, tref=tc,
                          # noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                          pl_kwargs_model=pl_kwarg_final[datasetname]["modelbinned"],
                          ax=axes_data[datasetname][jj])

        ####################
        # Plot the residuals
        ####################
        residual_pl = OrderedDict()
        residual_wGP_pl = OrderedDict()
        residual_binned_pl = OrderedDict()
        residual_binned_wGP_pl = OrderedDict()
        pad_resi = fig_param.get("pad_resi", (0.1, 0.1))
        for datasetname in datasetnames:
            (residual_pl[datasetname], residual_wGP_pl[datasetname], ebconts, labels
             ) = et.plot_residuals(t=dico_kwargs[datasetname]["t"],
                                   data=data_pl[datasetname],
                                   data_err=dico_kwargs[datasetname]["data_err"],
                                   jitter=dico_jitter[datasetname]["value"],
                                   jitter_type=dico_jitter[datasetname]["type"],
                                   datasim_db_docfunc=datasim_docfunc[datasetname][planet_name],
                                   param=fitted_values, l_param_name=l_param_name,
                                   plot_phase=True, Per=Per, tref=tc,
                                   pl_kwargs_model=pl_kwarg_final[datasetname]["data"],
                                   ax=axes_resi[datasetname][jj])
            phase_tref = foldAt(dico_kwargs[datasetname]["tref"], Per, T0=(tc + Per / 2)) - 0.5
            (residual_binned_pl[datasetname], residual_binned_wGP_pl[datasetname], ebconts, labels
             ) = et.plot_residuals(t=dico_kwargs[datasetname]["tref"] + Per * (midbins[datasetname] - phase_tref),
                                   data=binval[datasetname]["uncorr"],
                                   data_err=binstd[datasetname],
                                   datasim_db_docfunc=datasim_docfunc[datasetname][planet_name],
                                   datasim_kwargs={"tref": dico_kwargs[datasetname]["tref"]},
                                   param=fitted_values, l_param_name=l_param_name,
                                   supersamp=supersamp_bin_model, exptime=exptime_bin,
                                   plot_phase=True, Per=Per, tref=tc,
                                   # noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                                   pl_kwargs_model=pl_kwarg_final[datasetname]["databinned"],
                                   ax=axes_resi[datasetname][jj])
            # Set the y axis limits
            if residual_wGP_pl[datasetname] is not None:
                residuals_all = np.concatenate([residual_pl[datasetname], residual_wGP_pl[datasetname]])
            else:
                residuals_all = residual_pl[datasetname]
            if residual_binned_wGP_pl[datasetname] is not None:
                residuals_binned_all = np.concatenate([residual_binned_pl[datasetname], residual_binned_wGP_pl[datasetname]])
            else:
                residuals_binned_all = residual_binned_pl[datasetname]
            et.auto_y_lims(residuals_all, axes_resi[datasetname][jj], pad=pad_resi)
            # Indicate values that are off y-axis with arrows
            et.indicate_y_outliers(x=phases[datasetname], y=residual_pl[datasetname], ax=axes_resi[datasetname][jj],
                                   color=pl_kwarg_final[datasetname]["data"]["color"],
                                   alpha=pl_kwarg_final[datasetname]["data"]["alpha"])
            # Compute rms of the residuals and print it on the top of the residuals graphs
            rms_resi = "{:.1e}".format(np.std(residual_pl[datasetname][np.logical_and(phases[datasetname] > phase_min_data, phases[datasetname] < phase_max_data)]))
            rms_resi_binned = "{:.1e}".format(np.std(residual_binned_pl[datasetname][np.logical_and(midbins[datasetname] > phase_min_data, midbins[datasetname] < phase_max_data)]))
            filename_info = interpret_data_filename(datasetname)
            rms_resi_label = filename_info["inst_name"] + "({})".format(filename_info["number"])
            axes_resi[datasetname][jj].text(0.0, 1.05, "rms = {rms}; rms({exptime:.2f}h) ="
                                                       " {rms_bin} {unit}"
                                                       "".format(rms=rms_resi, unit=y_unit, rms_bin=rms_resi_binned,
                                                                 inst=rms_resi_label, exptime=exptime_bin * 24),
                                            fontsize=fontsize, transform=axes_resi[datasetname][jj].transAxes)

        ###################
        # Finalise the plot
        ###################
        # Set the xlims
        for datasetname in datasetnames:
            axes_data[datasetname][jj].set_xlim((phase_min_data, phase_max_data))
            axes_resi[datasetname][jj].set_xlim((phase_min_data, phase_max_data))
        # Show legend
        if show_legend:
            if legend_param is None:
                legend_param = {"fontsize": fontsize}
            axes_data[datasetnames[0]][0].legend(**legend_param)


if __name__ == "__main__":
    # Define the object name
    obj_name = "TOI-175"

    # Define dataset names to be loaded
    datasetnames = ["LC_TOI-175_TESS_0", ]

    chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
    plot_folder = join(chain_analysis_output_folder, "plots")
    makedirs(plot_folder, exist_ok=True)

    load_from_pickle = True
    exploration_output_folder = join(getcwd(), "outputs/exploration")
    exploration_pickle_folder = join(exploration_output_folder, "pickles")
    chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
    chain_analysis_pickle_folder = join(chain_analysis_output_folder, "pickles")
    chain_analysis_plots_folder = join(chain_analysis_output_folder, "plots")

    ## logger
    logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                            fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

    logger.info("1. Load from pickle if necessary")
    if load_from_pickle:
        # recreate post_instance object
        post_instance = cpost.Posterior(object_name=obj_name)
        post_instance.init_from_pickle(pickle_folder=exploration_pickle_folder)
        l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]

        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                        folder=chain_analysis_pickle_folder)
        fitted_values = fitted_values_dic["array"]
        l_param_name = fitted_values_dic["l_param"]
        planet_name = []
        periods = {}
        tics = {}
        for planet in post_instance.model.planets.values():
            planet_name.append(planet.get_name())
            periods[planet.get_name()] = df_fittedval.loc[planet.P.get_name(include_prefix=True, recursive=True), 'value']
            tics[planet.get_name()] = df_fittedval.loc[planet.tic.get_name(include_prefix=True, recursive=True), 'value']

    dataset_db = post_instance.dataset_db
    datasim_dbf = post_instance.datasimulators
    model_instance = post_instance.model
    star = post_instance.model.stars[list(post_instance.model.stars)[0]]

    create_LC_plots(
                    # fig=fig,
                    datasetnames=datasetnames, planets=planet_name, periods=periods, tcs=tics,
                    datasim_dbf=datasim_dbf, dataset_db=dataset_db, model_instance=model_instance,
                    fitted_values=fitted_values, l_param_name=l_param_name, star=star,
                    figsize=(2, 1), tight=True,
                    # dpi=200,
                    dpi=300,
                    fig_param={"top": 0.97, "bottom": 0.04, "left": 0.08, 'x_ylabel_coord': -0.2,
                               'pad_data': (0.05, 0.05), 'pad_resi': (-0.1, -0.1),
                               "y_unit": "w/o unit", "gs_from_sps_kw": {"wspace": 0.2},
                               'phase_lims': {"all": (-0.03, 0.03), "b": (-0.029, 0.029), "c": (-0.022, 0.022), "d": (-0.0075, 0.0075)}},
                    pl_kwargs={},
                    type="A&Afw",
                    save=join(chain_analysis_plots_folder, "custom_data_comp_LC.pdf")
                    )
