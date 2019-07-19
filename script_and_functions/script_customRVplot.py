#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce custom plots of CORALIE-153 RV data

@TODO:
"""
from os import getcwd, makedirs
from os.path import join

import numpy as np
import matplotlib.pyplot as pl

from logging import DEBUG, INFO
from matplotlib.gridspec import GridSpec
from copy import deepcopy
from collections import OrderedDict
from PyAstronomy.pyasl import foldAt

from fig_styler import styler

import source.tools.emcee_tools as et
import source.posterior.core.posterior as cpost
import source.tools.mylogger as ml
from source.tools.miscellaneous import interpret_data_filename

from source.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from source.posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add

# from ipdb import set_trace

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


@styler
def create_RV_plots(fig, datasetnames, planets, periods, tcs, datasim_dbf, dataset_db, model_instance,
                    fitted_values, l_param_name, star,
                    fig_param=None, pl_kwargs=None, show_legend=True, legend_param=None, *args, **kwargs):
    nplanet = len(planets)
    """Produce a clean RV plot.

    :param fig: Figure instance (provided by the styler)
    :param datasetnames: List providing the datasets to load and use
    :param list_of_str planets: List of planet names (used to infer the number of planets and create the good number of subplots)
    :param periods: Orbital periods for each planets (used to phase fold)
    :param tcs: Time of inferior conjunction for each planet (used to phase fold)
    :param model_instance: Core_Model subclass instance
    :param fitted_values: Fitted values
    :param list_of_str l_param_name: List of parameter names
    :param star: Star instance
    :param dict fig_param: Dictionary providing keyword arguments for the figure definition and settings:
        - 'right', 'left', 'bottom', 'top' keywords can be defined and they will be passed to the GridSpec init function
        - 'x_ylabel_coord' to shift from the y axis to the label
        - 'add_axeswithsharex_kw' dictionary of kwargs to pass to add_axeswithsharex which creates the
           data + residuals axes.
        - 'gs_from_sps_kw' dictionary of kwargs which will be passed on to add_twoaxeswithsharex_perplanet.
        - 'pad_data': float of Iterable of 2 floats which define the bottom and top pad to apply for data axes.
        - 'pad_resi': float of Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
        - 'y_unit': unit of RVs
    :param dict pl_kwargs: Dictionary with keys a instrument name (ex: "ESPRESSO") and values
        ""
        a dictionary that will be passed as kew
    :param bool show_legend: If True, show the legend
    :param legend_param: Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True)
    :param bool show_xlabel: If True, show the x label
    :param bool show_ylabel: If True, show the y labels
    """

    nplanet = len(planets)

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
    bottom = fig_param.get("bottom", 0.1)
    x_ylabel_coord = fig_param.get("x_ylabel_coord", -0.15)

    gs = GridSpec(nrows=1, ncols=1,
                  left=left, bottom=bottom, right=right, top=top,
                  wspace=None, hspace=None)

    # Set parameters for the instrument gridspec
    add_axeswithsharex_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot
    add_axeswithsharex_kw.update(fig_param.get("add_axeswithsharex_kw", {}))
    gs_from_sps_kw = {"wspace": 0.2}
    gs_from_sps_kw.update(fig_param.get("gs_from_sps_kw", {}))

    # Set the plots keywords arguments
    pl_kwarg_data = {"color": None, "fmt": ".", "alpha": 1.}
    pl_kwarg_model = {"color": "k", "fmt": "", "alpha": 1., "linestyle": "-"}

    # Get the units of the RVs
    y_unit = fig_param.get("y_unit", r"$\kms$")

    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    for datasetname in datasetnames:
        filename_info = interpret_data_filename(datasetname)
        pl_kwarg_final[datasetname] = {"model": deepcopy(pl_kwarg_model),
                                       "data": {"label": filename_info["inst_name"], }}
        pl_kwarg_final[datasetname]["data"].update(deepcopy(pl_kwarg_data))
        # Update with the user's inputs
        pl_kwarg_final[datasetname]["data"].update(pl_kwargs.get(datasetname, {}).get('data', {}))
        pl_kwarg_final[datasetname]["model"].update(pl_kwarg_final.get(datasetname, {}).get('model', {}))

    # Create the axes
    (ax_data, ax_resi) = et.add_twoaxeswithsharex_perplanet(gs[0], nplanet=nplanet, fig=fig,
                                                            gs_from_sps_kw=gs_from_sps_kw,
                                                            add_axeswithsharex_kw=add_axeswithsharex_kw)
    ax_data0 = ax_data[0]
    ax_resi0 = ax_resi[0]

    # Set the axis labels
    ax_data0.set_ylabel(r"RV [{}]".format(y_unit), fontsize=fontsize)
    # ax_data0.set_ylabel("RV [m.s-1]", fontsize=fontsize)
    ax_resi0.set_ylabel(r"O - C [{}]".format(y_unit), fontsize=fontsize)
    # ax_resi0.set_ylabel("O - C [m.s-1]", fontsize=fontsize)
    for res_ax in ax_resi:
        res_ax.set_xlabel("Orbital phase", fontsize=fontsize)

    # Align y labels
    ax_data0.yaxis.set_label_coords(x_ylabel_coord, 0.5)
    ax_resi0.yaxis.set_label_coords(x_ylabel_coord, 0.5)

    # Number of point for plotting the model
    npt_model = 1000

    for ii, planet_name in enumerate(planets):
        ax_data_pl = ax_data[ii]
        ax_resi_pl = ax_resi[ii]

        ax_data_pl.set_title("{}{}".format(star.name.prefix.get(), planet_name), fontsize=fontsize)
        ax_data_pl.tick_params(axis='both', which='major', labelsize=fontsize)
        ax_resi_pl.tick_params(axis='both', which='major', labelsize=fontsize)

        ##################################################
        # Compute the phases associated to the time values
        ##################################################

        phases = OrderedDict()
        Per = periods[planet_name]
        tc = tcs[planet_name]
        # print(Per, tc)

        # Define t and phase min and max for plotting the model
        phase_min_mod = -0.5
        phase_max_mod = 0.5
        tmin_model = tc + Per * phase_min_mod
        tmax_model = tc + Per * phase_max_mod

        for datasetname in datasetnames:
            phases[datasetname] = (foldAt(dico_kwargs[datasetname]["t"], Per, T0=(tc + Per / 2)) - 0.5)

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

        ####################################################
        # Compute the deltaRV to apply to the data and model
        ####################################################
        deltaRV = OrderedDict()
        RVrefglobal_instname = model_instance.RV_references["global"]
        # For each dataset
        for datasetname in datasetnames:
            filename_info = interpret_data_filename(datasetname)
            RVref4inst_modname = model_instance.RV_references[filename_info["inst_name"]]
            instmod_fullname_key = datasim_dbf.get_instmod_fullname(datasetname)
            instmodobj_key = model_instance.instruments[instmod_fullname_key]
            deltaRV[datasetname] = 0.0
            # If the current instrument is not the instrument of the global reference:
            # Add to Delta_RV the values of delta RV of the current instrument model reference to the global reference.
            if filename_info['inst_name'] != RVrefglobal_instname:
                instmod_RVref4inst = model_instance.instruments["RV"][filename_info['inst_name']][RVref4inst_modname]
                if instmod_RVref4inst.DeltaRV.main:
                    if instmod_RVref4inst.DeltaRV.free:
                        idx_deltaRV = l_param_name.index(instmod_RVref4inst.DeltaRV.get_name(include_prefix=True, recursive=True))
                        deltaRV[datasetname] += fitted_values[idx_deltaRV]
                    else:
                        deltaRV[datasetname] += instmod_RVref4inst.DeltaRV.value
            # If the current instrument model is not the reference instrument model for the instrument:
            # Add to Delta_RV the values of delta RV of the current instrument model to the current instrument model reference.
            if instmodobj_key.get_name() != RVref4inst_modname:
                if instmodobj_key.DeltaRV.main:
                    if instmodobj_key.DeltaRV.free:
                        idx_deltaRV = l_param_name.index(instmodobj_key.DeltaRV.get_name(include_prefix=True, recursive=True))
                        deltaRV[datasetname] += fitted_values[idx_deltaRV]
                    else:
                        deltaRV[datasetname] += instmodobj_key.DeltaRV.value

        RVrefglobal_modname = model_instance.RV_references[RVrefglobal_instname]
        datasim_RVrefglobal = (datasim_dbf.instrument_db["RV"][RVrefglobal_instname]
                               [RVrefglobal_modname][planet_name])

        ###############
        # Plot the data
        ###############
        idx_star_v0 = l_param_name.index(star.v0.get_name(include_prefix=True, recursive=True))
        data_pl = OrderedDict()
        for datasetname in datasetnames:
            # The data to plot for a planet and an instrument are the raw data to which you substract
            # the delta RV to the global reference (deltaRV[inst][key]) and then to which you substract the

            # Remove the DeltaRV to the global RV reference
            data_pl[datasetname] = dico_kwargs[datasetname]["data"] - deltaRV[datasetname]

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
                    l_datasim_db_docfunc_others.append(datasim_dbf.
                                                       instrument_db[inst_mod_fullname]
                                                       [plnt])

            # Compute and remove the other planet contribution
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
                data_pl[datasetname] = data_pl[datasetname] - (model - deltaRV[datasetname] - fitted_values[idx_star_v0])

            # Plot the data
            # print(dico_jitter[datasetname])
            ebcont, _ = et.plot_phase_folded_timeserie(t=dico_kwargs[datasetname]["t"],
                                                       data=data_pl[datasetname],
                                                       data_err=dico_kwargs[datasetname]["data_err"],
                                                       jitter=dico_jitter[datasetname]["value"],
                                                       jitter_type=dico_jitter[datasetname]["type"],
                                                       P=Per, tc=tc,
                                                       ax=ax_data_pl, pl_kwargs=pl_kwarg_final[datasetname]["data"],
                                                       )
            if pl_kwarg_final[datasetname]["data"]["color"] is None:
                pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
        # Set the y axis limits
        pad_data = fig_param.get("pad_data", (0.1, 0.1))
        et.auto_y_lims(np.concatenate([y for y in data_pl.values()]), ax_data_pl, pad=pad_data)
        # Indicate values that are off y-axis with anarrows
        for datasetname in datasetnames:
            et.indicate_y_outliers(x=phases[datasetname], y=data_pl[datasetname], ax=ax_data_pl, color=pl_kwarg_final[datasetname]["data"]["color"],
                                   alpha=pl_kwarg_final[datasetname]["data"]["alpha"])

        ################
        # Plot the model
        ################
        et.plot_model(tmin_model, tmax_model, npt_model, datasim_RVrefglobal, fitted_values,
                      l_param_name, plot_phase=True, P=Per, tc=tc,
                      pl_kwargs_model=pl_kwarg_final[datasetname]["model"],
                      ax=ax_data_pl)

        ####################
        # Plot the residuals
        ####################
        residual_pl = OrderedDict()
        residual_wGP_pl = OrderedDict()
        for datasetname in datasetnames:
            (residual_pl[datasetname],
             residual_wGP_pl[datasetname]
             ) = et.plot_residuals(t=dico_kwargs[datasetname]["t"],
                                   data=data_pl[datasetname] + deltaRV[datasetname],  # dico_kwargs[inst][key]["data"],
                                   data_err=dico_kwargs[datasetname]["data_err"],
                                   jitter=dico_jitter[datasetname]["value"],
                                   jitter_type=dico_jitter[datasetname]["type"],
                                   datasim_db_docfunc=datasim_docfunc[datasetname][planet_name],
                                   param=fitted_values, l_param_name=l_param_name,
                                   plot_phase=True, P=Per, tc=tc,
                                   pl_kwargs_model=pl_kwarg_final[datasetname]["data"],
                                   ax=ax_resi_pl)
        # Set the y axis limits
        y_residuals = np.concatenate([y for y in residual_pl.values()])
        if any([res is not None for res in residual_wGP_pl.values()]):
            y_residuals_wGP = np.concatenate([y for y in residual_wGP_pl.values() if y is not None])
            y_residuals_all = np.concatenate([y_residuals, y_residuals_wGP])
        else:
            y_residuals_all = y_residuals
        pad_resi = fig_param.get("pad_resi", (0.1, 0.1))
        et.auto_y_lims(y_residuals_all, ax_resi_pl, pad=pad_resi)
        # Indicate values that are off y-axis with anarrows
        if ii == 0:
            rms_resi = []
            rms_resi_label = []
        for datasetname in datasetnames:
            et.indicate_y_outliers(x=phases[datasetname], y=residual_pl[datasetname], ax=ax_resi_pl, color=pl_kwarg_final[datasetname]["data"]["color"],
                                   alpha=pl_kwarg_final[datasetname]["data"]["alpha"])
            if ii == 0:
                rms_resi.append("{:.2f}".format(np.std(residual_pl[datasetname])))
                filename_info = interpret_data_filename(datasetname)
                rms_resi_label.append(filename_info["inst_name"] + "({})".format(filename_info["number"]))
        if ii == 0:
            ax_resi_pl.text(0.0, 1.05, r"rms = {} {} ({})".format(", ".join(rms_resi), y_unit, ", ".join(rms_resi_label)),
                            fontsize=fontsize, transform=ax_resi_pl.transAxes)

        ###################
        # Finalise the plot
        ###################
        if show_legend:
            if legend_param is None:
                legend_param = {"fontsize": fontsize}

            ax_data[0].legend(**legend_param)


if __name__ == "__main__":
    # Define the object name
    obj_name = "TOI-175"

    # Define dataset names to be loaded
    datasetnames = ["RV_TOI-175_HARPS_0", "RV_TOI-175_ESPRESSO_0"]

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
    star = post_instance.model.stars[list(post_instance.model.stars.keys())[0]]

    # fig = pl.figure()

    create_RV_plots(
                    # fig=fig,
                    datasetnames=datasetnames, planets=planet_name, periods=periods, tcs=tics,
                    datasim_dbf=datasim_dbf, dataset_db=dataset_db, model_instance=model_instance,
                    fitted_values=fitted_values, l_param_name=l_param_name,
                    star=post_instance.model.stars[list(post_instance.model.stars)[0]],
                    figsize=(2, 1), tight=True,
                    # dpi=200,
                    dpi=300,
                    fig_param={"top": 0.97, "bottom": 0.04, "left": 0.08, 'x_ylabel_coord': -0.2, 'pad_data': (0.1, 0.1),
                               "y_unit": r"$\ms$", "gs_from_sps_kw": {"wspace": 0.2}},
                    pl_kwargs={"RV_TOI-175_HARPS_0": {"data": {"alpha": 0.3}}},
                    type="A&Afw",
                    save=join(chain_analysis_plots_folder, "custom_data_comp_RV.pdf")
                    )
