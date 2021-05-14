#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module to create plot specifically for light curve data

@TODO:
"""
import numpy as np

from copy import deepcopy, copy
from collections import OrderedDict, defaultdict
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator
from matplotlib.offsetbox import AnchoredText
from scipy.stats import binned_statistic
from PyAstronomy.pyasl import foldAt

import lisa.emcee_tools.emcee_tools as et
from lisa.posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from lisa.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
from lisa.posterior.core.likelihood.jitter_noise_model import apply_jitter_multi, apply_jitter_add


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

### for the A&A article class
AandA_fontsize = 8


def create_LC_phasefolded_plots(fig, post_instance, df_fittedval, datasim_kwargs=None, planets=None, star_name="A",
                                datasetnames=None,
                                remove_GP=False, remove1=False, LC_fact=1.,
                                show_time_from_tic=False, time_fact=24, time_unit="h",
                                exptime_bin=0.0, binning_stat="mean", supersamp_bin_model=10, show_binned_model=True,
                                sharey=False,
                                fig_param=None, pl_kwargs=None, show_legend=True, legend_param=None, show_system_name_in_suptitle=True,
                                LC_unit=None, *args, **kwargs):
    """Produce a clean LC plot.

    Arguments
    ---------
    fig                 :
        Figure instance (provided by the styler)
    post_instance       : Posterior instance
    df_fittedval        : DataFrame
        Dataframe containing the parameter estimates (index=Parameter_fullname, columns=[value, sigma-, sigma+] )
    datasim_kwargs : dict
        Dictionary of keyword arguments for the datasimulator.
    planets             : list_of_str or None
        List of the names of the planets for which you want a phase pholded curve. If None all planets are used
    star_name           : String
    datasetnames        : list of String
        List providing the datasets to load and use
    remove_GP           : Boolean
        If True the GP model is remove from the data for the plot.
    remove1             : bool
        If True remove one to get an out of transit level of 0 instead of 1.
    LC_fact             : float
        Factor to apply to the LC (ignore if remove1 is False)
    show_time_from_tic : bool
        If True than the phase folded light curve are show as a function of the time from the mid transit time.
    time_fact           : float
        If show_time_from_tic is True, than the time from mid transit is expressed in the same unit than the period
        by defaults. You can provide a factor here that will be applied to the times.
    time_unit           : str
        If show_time_from_tic is True, than you can provide here the unit in which the time from mid transit
        is expressed (knowing that time_fact is applied)
    exptime_bin         : float
        Width of the bins used for the binning in days (default 0.005555555556 days, 8 min)
    binning_stat        : str
        Statitical method used to compute the binned value. Can be "mean" or "median". This is passed to the
        statistic argument of scipy.stats.binned_statistic
    exptime_bin         : float
        Exposure time for the binning data and model in the same unit that the time of the datasets.
        If you don't want to bin put 0.
    binning_stat        : string
        Binning method to use "mean" or "median"
    supersamp_bin_model : int
        Supersampling factor for the binned model.
    show_binned_model   : bool
        If True the binned model is shown.
    sharey        : bool
    fig_param     : dict
        Dictionary providing keyword arguments for the figure definition and settings. The possible keys are
            - 'system_name_4_suptitle': Name that you want to use for the suptitle if different from the post_instance name
            - 'main_gridspec': The content of this entry should be a dictionary which will be passed to
                GridSpec (GridSpec(..., **fig_param['main_gridspec'])) instance creation with create the main gridspec
            - 'add_axeswithsharex_kw': The content of this entry should be a dictionary which will be
                passed to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., add_axeswithsharex_kw=fig_param['add_axeswithsharex_kw'])
                function creating two axes data and residuals per planet.
            - 'gs_from_sps_kw': The content of this entry should be a dictionary which will be passed
                to add_twoaxeswithsharex_perplanet (add_twoaxeswithsharex_perplanet(..., gs_from_sps_kw=fig_param['gs_from_sps_kw'])
                function creating two axes data and residuals per planet.
            - 'pad_data': Iterable of 2 floats which define the bottom and top pad to apply for data axes.
                Can also be a dictionary of Iterable of 2 floats with for keys the planet_name. This
                allows to provide different pad_data for different planets.
            - 'pad_resi': Iterable of 2 floats which define the bottom and top pad to apply for residuals axes.
            - 'indicate_y_outliers_data': boolean. If True, data outliers (outside of the plot) are indicated
                by arrows.
            - 'indicate_y_outliers_resi': boolean. If True, residuals outliers (outside of the plot) are indicated
                by arrows.
            - 'fontsize' : Int specifiying the fontsize
            - 'phasefold_central_phase': float between 0 and 1 which specify the central phase for the phase folding.
                For example if 0, the phase while be computed between -0.5 and 0.5. If 0.5 they will be computed
                between 0 and 1.
            - 'x_lims': dictionary with for possible keys "all" or any of the planet names. The values are
               tuples giving the minimum and maximum phases or time from mid-transit (depending on show_time_from_tic)
               for all planets or a specific ones. If show_time_from_tic is True than the provided times
               should also include the time_fact
            - 'rms_format': Format that will be used to format the rms values (for example '.0f')
    pl_kwargs    : dict
        Dictionary with keys a dataset name (ex: "RV_HD209458_ESPRESSO_0") or "model" or "binned_data" and values
        a dictionary that will be passed as keyword arguments associated the plotting functions.
        You can also add a 'jitter' key with value a dictionary that will contain the changes that you
        want to make for the update error bars due to potential jitter.
    show_legend  : bool
        If True, show the legend
    legend_param : dict
        Dictionary providing keyword arguments for the pyplot.legend function (if show_legend is True)
        Can also contains another entries that will not be passed to pyplot.legend:
        'idx_planet': index of the planet plot on which you want to show the legend()
        'idx_dataset': index of the dataaset plot on which you want to show the legend()
    show_system_name_in_suptitle : bool
        If True show the system name in the suptitle
    LC_unit        : str or None
        String giving the unit of the LCs
    """
    all_planets = list(post_instance.model.planets.keys())
    all_planets.sort()
    if planets is None:
        planets = copy(all_planets)
    nplanet = len(planets)

    # star = post_instance.model.stars[star_name]

    ###########
    # Load Data
    ###########
    # If no dataset name is provided get all the available RV datasets
    if datasetnames is None:
        datasetnames = post_instance.dataset_db.get_datasetnames(inst_fullcat="LC", sortby_instcat=False, sortby_instname=False)
    # Load the defined datasets and check how many dataset there is by instrument.
    dico_dataset = {}
    dico_kwargs = {}
    dico_nb_dstperinst = defaultdict(lambda: 0)
    for datasetname in datasetnames:
        dico_dataset[datasetname] = post_instance.dataset_db[datasetname]
        dico_kwargs[datasetname] = dico_dataset[datasetname].get_kwargs()
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        dico_nb_dstperinst[filename_info["inst_name"]] += 1
        # # Remove 1 if needed
        # if remove1:
        #     dico_kwargs[datasetname]["data"] -= 1.
        # # apply the RV fact to LC and LC_err
        # if (LC_fact != 1.) and not(remove1):
        #     LC_fact = 1.
        # dico_kwargs[datasetname]["data"] *= LC_fact
        # dico_kwargs[datasetname]["data_err"] *= LC_fact

    ###################
    # Plots preparation
    ###################

    # Create the gridspec
    if fig_param is None:
        fig_param = {}

    fontsize = fig_param.get("fontsize", AandA_fontsize)

    if show_system_name_in_suptitle:
        system_name = fig_param.get('system_name_4_suptitle', post_instance.full_name)
        fig.suptitle(f"{system_name} system", fontsize=fontsize)

    # Create the gridspec
    if fig_param is None:
        fig_param = {}

    gs = GridSpec(figure=fig, nrows=1, ncols=1, **fig_param.get('main_gridspec', {}))

    x_lims = fig_param.get("x_lims", {})
    x_lims_all_def = (-0.5, 0.5) if not(show_time_from_tic) else (- 10 / 24 * time_fact, 10 / 24 * time_fact)
    x_min_all, x_max_all = x_lims.get("all", x_lims_all_def)

    # Set parameters for the instrument gridspec
    add_axeswithsharex_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot
    add_axeswithsharex_kw.update(fig_param.get("add_axeswithsharex_kw", {}))
    gs_from_sps_kw = {}
    gs_from_sps_kw.update(fig_param.get("gs_from_sps_kw", {}))

    # Set the plots keywords arguments
    # Define the default values
    pl_kwarg_data = {"color": "k", "fmt": ".", "alpha": 0.05}
    pl_kwarg_databinned = {"color": "r", "fmt": ".", "alpha": 1.0, 'label': f"bin({exptime_bin * 24 * 60:.0f} min)"}
    pl_kwarg_modelraw = {"color": "k", "fmt": '', "alpha": 1., "linestyle": "-", "label": "model"}
    pl_kwarg_modelbinned = {"color": "r", "fmt": '', "lw": 0.8, "alpha": 1., "label": f"model: bin={exptime_bin * 24 * 60:.0f} min"}  # , "linestyle": "-"
    show_error_data = False
    show_error_databinned = True

    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    pl_kwarg_jitter = {}
    pl_show_error = {}

    for datasetname in datasetnames:
        # Set the labels
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        if dico_nb_dstperinst[filename_info["inst_name"]] == 1:
            label_dst = filename_info["inst_name"]
        else:
            label_dst = filename_info["inst_name"] + "({})".format(filename_info["number"])
        pl_kwarg_final[datasetname] = {"label": label_dst, }
        pl_kwarg_final[datasetname] = {"model": deepcopy(pl_kwarg_modelraw),
                                       "modelbinned": deepcopy(pl_kwarg_modelbinned),
                                       "data": {"label": "data", },
                                       "databinned": {"label": "data: bin={:.2f}h".format(exptime_bin * 24), }
                                       }
        pl_kwarg_final[datasetname]["model"].update(pl_kwarg_final.get(datasetname, {}).get('model', {}))
        pl_kwarg_final[datasetname]["modelbinned"].update(pl_kwarg_final.get(datasetname, {}).get('modelbinned', {}))
        pl_kwarg_jitter[datasetname] = {}
        pl_show_error[datasetname] = {"data": show_error_data, "databinned": show_error_databinned}
        for dataordatabinned, pl_kwarg_def in zip(["data", "databinned"], [pl_kwarg_data, pl_kwarg_databinned]):
            # Load default values in pl_kwarg_final[datasetname]
            pl_kwarg_final[datasetname][dataordatabinned].update(deepcopy(pl_kwarg_def))
            # Update with the user's inputs
            pl_kwarg_final[datasetname][dataordatabinned].update(pl_kwargs.get(datasetname, {}).get(dataordatabinned, {}))
            # Init pl_kwarg_jitter[datasetname]
            pl_kwarg_jitter[datasetname][dataordatabinned] = deepcopy(pl_kwarg_final[datasetname][dataordatabinned])
            # Update with the user's inputs
            if "jitter" in pl_kwarg_final[datasetname][dataordatabinned]:
                dico_jitter = pl_kwarg_final[datasetname][dataordatabinned].pop("jitter")
            else:
                dico_jitter = {}
            dico_jitter["fmt"] = "none"  # To ensure that only the error bars are drawn
            pl_kwarg_jitter[datasetname][dataordatabinned].update(dico_jitter)
            pl_kwarg_jitter[datasetname][dataordatabinned].pop("label")  # To ensure that a second label doesn't appear on the legend
            # default value for alpha jitter
            if "alpha" not in dico_jitter:
                if "alpha" in pl_kwarg_jitter[datasetname][dataordatabinned]:
                    pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] = pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] / 2
                else:
                    pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] = 0.5
            # default value for ecolor
            if ("ecolor" not in pl_kwarg_jitter[datasetname][dataordatabinned]) and ("color" in pl_kwarg_jitter[datasetname][dataordatabinned]):
                pl_kwarg_jitter[datasetname][dataordatabinned]["ecolor"] = pl_kwarg_jitter[datasetname][dataordatabinned]["color"]
            # Update pl_show_error[datasetname] with user input
            if "show_error" in pl_kwarg_final[datasetname][dataordatabinned]:
                pl_show_error[datasetname][dataordatabinned] = pl_kwarg_final[datasetname][dataordatabinned].pop("show_error")
    # Create the axes per planet and set the titles and labels and the ArchorBox with the instrument name
    axes_data, axes_resi = {}, {}
    for ii, datasetname in enumerate(datasetnames):
        # Create the axes
        (axes_data[datasetname], axes_resi[datasetname]
         ) = et.add_twoaxeswithsharex_perplanet(gs[ii], nplanet=nplanet, fig=fig, sharey=sharey,
                                                gs_from_sps_kw=gs_from_sps_kw,
                                                add_axeswithsharex_kw=add_axeswithsharex_kw)
        # Format ticks, labels, titles
        for jj, planet_name in enumerate(planets):
            # set ticks
            axes_data[datasetname][jj].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_data[datasetname][jj].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False)
            axes_data[datasetname][jj].xaxis.set_minor_locator(AutoMinorLocator())
            axes_data[datasetname][jj].yaxis.set_minor_locator(AutoMinorLocator())
            axes_data[datasetname][jj].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_data[datasetname][jj].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            axes_resi[datasetname][jj].tick_params(axis='both', which='major', labelsize=fontsize)
            axes_resi[datasetname][jj].yaxis.set_minor_locator(AutoMinorLocator())
            axes_resi[datasetname][jj].tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True)
            axes_resi[datasetname][jj].tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
            axes_resi[datasetname][jj].grid(axis="y", color="black", alpha=.5, linewidth=.5)
            if jj != 0:
                axes_data[datasetname][jj].tick_params(axis="both", labelleft=False)
                axes_resi[datasetname][jj].tick_params(axis="both", labelleft=False)
            # Set title with planet name on the first row
            if ii == 0:
                axes_data[datasetname][jj].set_title("{} {}".format("Planet", planet_name), fontsize=fontsize)
            # Set x label for the last row
            if ii == len(datasetnames) - 1:
                if show_time_from_tic:
                    axes_resi[datasetname][jj].set_xlabel(f"Time from mid-transit [{time_unit}]", fontsize=fontsize)
                else:
                    axes_resi[datasetname][jj].set_xlabel("Orbital phase", fontsize=fontsize)
            # Set y labels on the first column and align them, also set the Anchor boxes
            if jj == 0:
                ylabel_data = f"Normalised Flux [{LC_unit}]" if LC_unit is not None else "Normalised Flux"
                ylabel_resi = f"O - C [{LC_unit}]" if LC_unit is not None else "O - C"
                axes_data[datasetname][jj].set_ylabel(ylabel_data, fontsize=fontsize)
                axes_resi[datasetname][jj].set_ylabel(ylabel_resi, fontsize=fontsize)
                # Align y labels
                # axes_data[datasetname][jj].yaxis.set_label_coords(x_ylabel_coord, 0.5)
                # axes_resi[datasetname][jj].yaxis.set_label_coords(x_ylabel_coord, 0.5)

                filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
                anchored_text_inst = AnchoredText(filename_info["inst_name"] + "({})".format(filename_info["number"]),
                                                  loc=3, prop={"fontsize": fontsize})  # loc=3 is 'lower left'
                anchored_text_inst.set_alpha(0.5)
                axes_data[datasetname][jj].add_artist(anchored_text_inst)

    phasefold_central_phase = fig_param.get("phasefold_central_phase", 0.)

    # Number of point for plotting the model
    npt_model = 5000

    for jj, planet_name in enumerate(planets):

        ##################################################
        # Compute the x_values (time or phase depending on show_time_from_tic) associated to the time values
        ##################################################

        x_values = OrderedDict()
        Per = df_fittedval.loc[post_instance.model.planets[planet_name].P.full_name]["value"]
        tc = df_fittedval.loc[post_instance.model.planets[planet_name].tic.full_name]["value"]
        # print(Per, tc)

        x_min_pl, x_max_pl = x_lims.get(planet_name, (x_min_all, x_max_all))

        x_min_data = np.inf
        x_max_data = -np.inf
        for datasetname in datasetnames:
            phases_dst = (foldAt(dico_kwargs[datasetname]["t"], Per, T0=(tc + Per * (phasefold_central_phase - 0.5))) + (phasefold_central_phase - 0.5))
            x_values[datasetname] = phases_dst * Per * time_fact if show_time_from_tic else phases_dst
            if np.min(x_values[datasetname]) < x_min_data:
                x_min_data = np.min(x_values[datasetname])
            if np.max(x_values[datasetname]) > x_max_data:
                x_max_data = np.max(x_values[datasetname])

        if x_min_data < x_min_pl:
            x_min_data = x_min_pl
        if x_max_data > x_max_pl:
            x_max_data = x_max_pl

        # Define t and phase min and max for plotting the model
        tmin_model = tc + x_min_data if show_time_from_tic else tc + Per * x_min_data
        tmax_model = tc + x_max_data if show_time_from_tic else tc + Per * x_max_data

        ###################
        # Load OOT_var info
        ###################
        OOT_var = OrderedDict()
        # For each dataset
        for datasetname in datasetnames:
            instmod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
            instmodobj = post_instance.model.instruments[instmod_fullname]
            if instmodobj.get_with_OOT_var():
                OOT_var[datasetname] = np.zeros_like(dico_kwargs[datasetname]["t"])
                for order in range(instmodobj.get_OOT_var_order() + 1):
                    OOT_var_name = instmodobj.get_OOT_param_name(order)
                    OOT_var_param = instmodobj.parameters[OOT_var_name]
                    if OOT_var_param.free:
                        OOT_var_paramvalue = df_fittedval.loc[OOT_var_param.full_name]["value"]
                    else:
                        OOT_var_paramvalue = OOT_var_param.value
                    OOT_var[datasetname] += OOT_var_paramvalue * (dico_kwargs[datasetname]["t"] -
                                                                  dico_kwargs[datasetname]["tref"])**order
                # Apply RV_fact to deltaRV
                # OOT_var[datasetname] *= LC_fact
            else:
                OOT_var[datasetname] = None

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        data_err_jitter = OrderedDict()
        dico_jitter = {}
        for datasetname in datasetnames:
            dico_jitter[datasetname] = {}
            data_err_jitter[datasetname] = dico_kwargs[datasetname]["data_err"].copy()
            inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
            inst_mod = post_instance.model.instruments[inst_mod_fullname]
            noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
            if noise_model.has_jitter:
                dico_jitter[datasetname]["type"] = noise_model.jitter_type
                if inst_mod.jitter.free:
                    dico_jitter[datasetname]["value"] = df_fittedval.loc[inst_mod.jitter.full_name]["value"]  # * LC_fact
                else:
                    dico_jitter[datasetname]["value"] = inst_mod.jitter.value
                if dico_jitter[datasetname]["type"] == "multi":
                    data_err_jitter[datasetname] = np.sqrt(apply_jitter_multi(data_err_jitter[datasetname], dico_jitter[datasetname]["value"]))
                elif dico_jitter[datasetname]["type"] == "add":
                    data_err_jitter[datasetname] = np.sqrt(apply_jitter_add(data_err_jitter[datasetname], dico_jitter[datasetname]["value"]))
                else:
                    raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
            else:
                dico_jitter[datasetname]["type"] = None
                dico_jitter[datasetname]["value"] = None
                data_err_jitter[datasetname] = None

        ###############
        # Plot the data
        ###############
        data_pl = OrderedDict()
        for datasetname in datasetnames:
            # import pdb; pdb.set_trace()
            # The data to plot for a planet and an instrument are the raw data to which you substract
            # the other planet contributions adn the OOT var

            # Get the kwargs of the dataset which will be used for remove_GP and remove other planets contributions
            # and remove RV_drift
            kwargs_dataset = dico_kwargs[datasetname].copy()
            t_dst = kwargs_dataset.pop("t")
            kwargs_dataset.pop("data")
            kwargs_dataset.pop("data_err")
            kwargs_dataset.update(datasim_kwargs.copy())

            # Init data_pl
            data_pl[datasetname] = dico_kwargs[datasetname]["data"]

            # Compute and remove the other planet contribution
            for plnt in all_planets:
                if plnt == planet_name:
                    continue
                else:
                    (model_pl_only, _, _, _
                     ) = post_instance.compute_model(tsim=t_dst, dataset_name=datasetname, param=df_fittedval["value"],
                                                     l_param_name=list(df_fittedval.index), key_obj=f"{plnt}_only", datasim_kwargs=kwargs_dataset
                                                     )
                    # Apply RV_fact to models, model planet only has an out of transit level of 0
                    # model_pl_only *= LC_fact
                    data_pl[datasetname] = data_pl[datasetname] - model_pl_only

            # Remove the OOT_var
            if OOT_var[datasetname] is not None:
                data_pl[datasetname] /= (1 + OOT_var[datasetname])

            # Remove GP model
            if remove_GP:
                (_, _, GP_pred, GP_pred_var
                 ) = post_instance.compute_model(tsim=t_dst, dataset_name=datasetname, param=df_fittedval["value"],
                                                 l_param_name=list(df_fittedval.index), key_obj="whole", datasim_kwargs=kwargs_dataset
                                                 )
                if GP_pred is not None:
                    # GP_pred *= LC_fact
                    # Correct data from GP pred
                    data_pl[datasetname] -= GP_pred

            # Plot the data
            if pl_show_error[datasetname]["data"]:
                data_err = dico_kwargs[datasetname]["data_err"]
                data_err *= LC_fact
            else:
                data_err = None

            # Remove 1 if needed
            if remove1:
                # dico_kwargs[datasetname]["data"] -= 1.
                data_pl[datasetname] -= 1
            # apply the RV fact to LC and LC_err
            if (LC_fact != 1.) and not(remove1):
                LC_fact = 1.
            data_pl[datasetname] *= LC_fact
            data_err_jitter[datasetname] *= LC_fact

            ebcont, _, _ = et.plot_phase_folded_timeserie(t_data=dico_kwargs[datasetname]["t"],
                                                          data=data_pl[datasetname],
                                                          data_err=data_err,
                                                          Per=Per, tref=tc, phasefold_central_phase=phasefold_central_phase,
                                                          show_time_from_tref=show_time_from_tic, time_fact=time_fact,
                                                          ax=axes_data[datasetname][jj],
                                                          pl_kwargs=pl_kwarg_final[datasetname]["data"],
                                                          )
            if not("color" in pl_kwarg_final[datasetname]["data"]):
                pl_kwarg_final[datasetname]["data"]["color"] = ebcont[0].get_color()
            if not("ecolor" in pl_kwarg_jitter[datasetname]["data"]):
                pl_kwarg_jitter[datasetname]["data"]["ecolor"] = pl_kwarg_final[datasetname]["data"]["color"]
            if pl_show_error[datasetname]["data"]:
                ebcont, _, _ = et.plot_phase_folded_timeserie(t_data=dico_kwargs[datasetname]["t"],
                                                              data=data_pl[datasetname],
                                                              data_err=data_err_jitter[datasetname],
                                                              only_errorbar=True,
                                                              Per=Per, tref=tc, phasefold_central_phase=phasefold_central_phase,
                                                              show_time_from_tref=show_time_from_tic, time_fact=time_fact,
                                                              ax=axes_data[datasetname][jj],
                                                              pl_kwargs=pl_kwarg_jitter[datasetname]["data"],
                                                              )
            # Set the y axis limits
            pad_data_default = (0.1, 0.1)  # This pad_data is here to allow to have different pad depending on the dataset in the future
            if planet_name in fig_param.get("pad_data", {}):
                pad_data = fig_param["pad_data"][planet_name]
            else:
                pad_data_content = fig_param.get("pad_data", pad_data_default)
                if isinstance(pad_data_content, dict):
                    pad_data = pad_data_default
                else:
                    pad_data = pad_data_content
            et.auto_y_lims(data_pl[datasetname], axes_data[datasetname][jj], pad=pad_data)
            # Indicate values that are off y-axis with anarrows
            if fig_param.get("indicate_y_outliers_data", True):
                et.indicate_y_outliers(x=x_values[datasetname], y=data_pl[datasetname], ax=axes_data[datasetname][jj],
                                       color=pl_kwarg_final[datasetname]["data"]["color"],
                                       alpha=pl_kwarg_final[datasetname]["data"]["alpha"])

        ################
        # Plot the model
        ################
        if remove1:  # The model planet only has an out of transit at 0 and cannot be used which plot_model if remove1 is False
            key_obj = f"{planet_name}_only"
        else:
            key_obj = "whole"  # WARNING: There might be a problem with that if there happens to be a double transit at the times chosen for the model

        for datasetname in datasetnames:  # f"{planet_name}_only",  "whole"
            ebconts_lines_labels_model = et.plot_model(tmin=tmin_model, tmax=tmax_model, nt=npt_model,
                                                       dataset_name=datasetname, param=df_fittedval["value"],
                                                       l_param_name=list(df_fittedval.index), post_instance=post_instance,
                                                       key_obj=key_obj, datasim_kwargs=kwargs_dataset,
                                                       multiplication_factor=LC_fact,
                                                       plot_phase=True, Per=Per, tref=tc, phasefold_central_phase=phasefold_central_phase,
                                                       show_time_from_tref=show_time_from_tic, time_fact=time_fact,
                                                       pl_kwargs_model=pl_kwarg_final[datasetname]["model"], pl_kwargs_modelandGP=pl_kwarg_final[datasetname]["model"],
                                                       show_modelandGP=not(remove_GP), force_plot_phase_GP=False,
                                                       ax=axes_data[datasetname][jj])
            if not("color" in pl_kwarg_final[datasetname]["model"]):
                pl_kwarg_final[datasetnames]["model"]["color"] = ebconts_lines_labels_model["model"]["ebcont or line"][0].get_color()

            # Plot binned model  f"{planet_name}_only"
            if show_binned_model:
                ebconts_lines_labels_model = et.plot_model(tmin=tmin_model, tmax=tmax_model, nt=npt_model,
                                                           dataset_name=datasetname, param=df_fittedval["value"],
                                                           l_param_name=list(df_fittedval.index), post_instance=post_instance,
                                                           key_obj=key_obj, datasim_kwargs=kwargs_dataset,
                                                           multiplication_factor=LC_fact,
                                                           supersamp=supersamp_bin_model, exptime=exptime_bin,
                                                           plot_phase=True, Per=Per, tref=tc, phasefold_central_phase=phasefold_central_phase,
                                                           show_time_from_tref=show_time_from_tic, time_fact=time_fact,
                                                           pl_kwargs_model=pl_kwarg_final[datasetname]["modelbinned"], pl_kwargs_modelandGP=pl_kwarg_final[datasetname]["modelbinned"],
                                                           show_modelandGP=not(remove_GP), force_plot_phase_GP=False,
                                                           ax=axes_data[datasetname][jj])
            if not("color" in pl_kwarg_final[datasetname]["modelbinned"]):
                pl_kwarg_final[datasetnames]["modelbinned"]["color"] = ebconts_lines_labels_model["model"]["ebcont or line"][0].get_color()

        #################################
        # Plot the residuals of the model
        #################################
        residual_pl = OrderedDict()
        residual_wGP_pl = OrderedDict()
        y_residuals_all = OrderedDict()
        for datasetname in datasetnames:
            (_, _, _, _, _, residual_pl[datasetname], residual_wGP_pl[datasetname], ebconts_lines_labels
             ) = et.plot_residuals(dataset_name=datasetname, param=df_fittedval["value"], l_param_name=list(df_fittedval.index),
                                   post_instance=post_instance, key_obj="whole", datasim_kwargs=kwargs_dataset,
                                   multiplication_factor=LC_fact,
                                   plot_phase=True, Per=Per, tref=tc, phasefold_central_phase=phasefold_central_phase,
                                   show_time_from_tref=show_time_from_tic, time_fact=time_fact,
                                   pl_kwargs_model=pl_kwarg_final[datasetname]["data"], show_model=not(remove_GP),
                                   show_error_model=pl_show_error[datasetname]["data"],
                                   pl_kwargs_modelandGP=pl_kwarg_final[datasetname]["data"], show_modelandGP=remove_GP,
                                   show_error_modelandGP=pl_show_error[datasetname]["data"],
                                   ax=axes_resi[datasetname][jj])
            y_residuals_all[datasetname] = []
            if (residual_wGP_pl[datasetname] is None) or not(remove_GP):
                y_residuals_all[datasetname].append(residual_pl[datasetname])
            else:
                y_residuals_all[datasetname].append(residual_wGP_pl[datasetname])
            # Set the y axis limits
            pad_resi_default = (0.1, 0.1)
            if planet_name in fig_param.get("pad_resi", {}):
                pad_resi = fig_param["pad_resi"][planet_name]
            else:
                pad_resi_content = fig_param.get("pad_resi", pad_data_default)
                if isinstance(pad_resi_content, dict):
                    pad_resi = pad_resi_default
                else:
                    pad_resi = pad_resi_content
            et.auto_y_lims(np.concatenate(y_residuals_all[datasetname]), axes_resi[datasetname][jj], pad=pad_resi)
            # Indicate values that are off y-axis with arrows
            if fig_param.get("indicate_y_outliers_resi", True):
                if (residual_wGP_pl[datasetname] is None) or not(remove_GP):
                    et.indicate_y_outliers(x=x_values[datasetname], y=residual_pl[datasetname], ax=axes_resi[datasetname][jj],
                                           color=pl_kwarg_final[datasetname]["data"]["color"],
                                           alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))
                else:
                    et.indicate_y_outliers(x=x_values[datasetname], y=residual_wGP_pl[datasetname], ax=axes_resi[datasetname][jj],
                                           color=pl_kwarg_final[datasetname]["data"]["color"],
                                           alpha=pl_kwarg_final[datasetname]["data"].get("alpha", 1))
            # Compute rms of the residuals and print it on the top of the residuals graphs
            rms_format = fig_param.get("rms_format", ".1e")
            text_rms = f"{{:{rms_format}}}"
            text_rms = text_rms.format(np.std(residual_pl[datasetname][np.logical_and(x_values[datasetname] > x_min_data, x_values[datasetname] < x_max_data)]))

        ##########################################
        # Bin the data and residuals and plot them
        ##########################################
        if exptime_bin > 0.:
            bin_size = exptime_bin * time_fact if show_time_from_tic else exptime_bin / Per
            bins = {}
            binval = {}
            binval_resi = {}
            binstd = {}
            binstd_jitter = {}
            midbins = {}
            for ii, datasetname in enumerate(datasetnames):
                # define the bins, it's currently the same for all datasets, but I will want to be able to group datasets in the same plot in the future.
                bins[datasetname] = np.arange(x_min_data, x_max_data + bin_size, bin_size)
                midbins[datasetname] = bins[datasetname][:-1] + bin_size / 2
                # Bin the data and residuals
                # import pdb; pdb.set_trace()
                # binval[datasetname] = {}
                # binval_resi[datasetname] = {}
                (binval[datasetname], binedges, binnb
                 ) = binned_statistic(x_values[datasetname], data_pl[datasetname],
                                      statistic=binning_stat, bins=bins[datasetname],
                                      range=(x_min_data, x_max_data))
                resi_pl_dst = residual_wGP_pl[datasetname] if (remove_GP and (residual_wGP_pl[datasetname] is not None)) else residual_pl[datasetname]
                (binval_resi[datasetname], _, _
                 ) = binned_statistic(x_values[datasetname], resi_pl_dst,
                                      statistic=binning_stat, bins=bins[datasetname],
                                      range=(x_min_data, x_max_data))
                # Compute the error bars on the binned data (and residuals)
                nbins = len(bins[datasetname]) - 1
                binstd[datasetname] = np.zeros(nbins)
                binstd_jitter[datasetname] = np.zeros(nbins) if (data_err_jitter[datasetname] is not None) else None
                bincount = np.zeros(nbins)
                for i_bin in range(nbins):
                    bincount[i_bin] = len(np.where(binnb == (i_bin + 1))[0])
                    if bincount[i_bin] > 0.0:
                        binstd[datasetname][i_bin] = np.sqrt(np.sum(np.power((dico_kwargs[datasetname]["data_err"]
                                                                              [binnb == (i_bin + 1)]),
                                                                             2.)) /
                                                             bincount[i_bin]**2)
                        if data_err_jitter[datasetname] is not None:
                            binstd_jitter[datasetname][i_bin] = np.sqrt(np.sum(np.power((data_err_jitter[datasetname]
                                                                                         [binnb == (i_bin + 1)]),
                                                                               2.)) /
                                                                        bincount[i_bin]**2)

                    else:
                        binstd[datasetname][i_bin] = np.nan
                        if data_err_jitter[datasetname] is not None:
                            binstd_jitter[datasetname][i_bin] = np.nan
                # Plot the binned data
                if pl_show_error[datasetname]["databinned"]:
                    bin_err = binstd[datasetname]
                    bin_err *= LC_fact
                else:
                    bin_err = None
                ebcont_binned = axes_data[datasetname][jj].errorbar(midbins[datasetname], binval[datasetname], yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                if not("color" in pl_kwarg_final[datasetname]["databinned"]):
                    pl_kwarg_final[datasetname]["databinned"] = ebcont_binned[0].get_color()
                if not("ecolor" in pl_kwarg_jitter[datasetname]["databinned"]):
                    pl_kwarg_jitter[datasetname]["databinned"]["ecolor"] = pl_kwarg_final[datasetname]["databinned"]
                if (binstd_jitter[datasetname] is not None) and pl_show_error[datasetname]["databinned"]:
                    ebcont_binned = axes_data[datasetname][jj].errorbar(midbins[datasetname], binval[datasetname], yerr=binstd_jitter[datasetname], **pl_kwarg_jitter[datasetname]["databinned"])
                # Indicate values that are off y-axis with arrows
                et.indicate_y_outliers(x=midbins[datasetname], y=binval[datasetname], ax=axes_data[datasetname][jj],
                                       color=pl_kwarg_final[datasetname]["databinned"]["color"],
                                       alpha=pl_kwarg_final[datasetname]["databinned"]["alpha"])
                # Plot the binned residuals
                ebcont_binned = axes_resi[datasetname][jj].errorbar(midbins[datasetname], binval_resi[datasetname], yerr=bin_err, **pl_kwarg_final[datasetname]["databinned"])
                if (binstd_jitter[datasetname] is not None) and pl_show_error[datasetname]["databinned"]:
                    ebcont_binned = axes_resi[datasetname][jj].errorbar(midbins[datasetname], binval_resi[datasetname], yerr=binstd_jitter[datasetname], **pl_kwarg_jitter[datasetname]["databinned"])
                # Compute rms of the binned residuals
                text_rms_binned = f"{{:{rms_format}}} (bin={exptime_bin * 24 * 60:.0f} min)"
                text_rms_binned = text_rms_binned.format(np.std(binval_resi[datasetname][np.logical_and(midbins[datasetname] > x_min_data, midbins[datasetname] < x_max_data)]))
                # Indicate values that are off y-axis with arrows
                et.indicate_y_outliers(x=midbins[datasetname], y=binval_resi[datasetname], ax=axes_resi[datasetname][jj],
                                       color=pl_kwarg_final[datasetname]["databinned"]["color"],
                                       alpha=pl_kwarg_final[datasetname]["databinned"]["alpha"])

        ###########
        # Write rms
        ###########
        for ii, datasetname in enumerate(datasetnames):
            text_rms_to_plot = f"{text_rms}, {text_rms_binned}" if (exptime_bin > 0.) else f"rms = {text_rms}"
            if jj == 0:
                text_rms_to_plot = "rms = " + text_rms_to_plot
            if LC_unit is not None:
                text_rms_to_plot += f" {LC_unit}"
            axes_resi[datasetname][jj].text(0.0, 1.05, text_rms_to_plot, fontsize=fontsize, transform=axes_resi[datasetname][jj].transAxes)

    ###################
    # Finalise the plot
    ###################
    # Set the xlims
    for jj, planet_name in enumerate(planets):
        for datasetname in datasetnames:
            axes_data[datasetname][jj].set_xlim((x_min_data, x_max_data))
            # axes_resi[datasetname][jj].set_xlim((x_min_data, x_max_data))
    # Show legend
    if show_legend:
        legend_kwargs = {"fontsize": fontsize, "idx_planet": 0, "idx_dataset": 0}
        if legend_param is not None:
            legend_kwargs.update(legend_param)
        idx_planet = legend_kwargs.pop("idx_planet")
        idx_dataset = legend_kwargs.pop("idx_dataset")
        axes_data[datasetnames[idx_dataset]][idx_planet].legend(**legend_kwargs)
