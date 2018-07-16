#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script to produce custom plots of CORALIE-153 RV data

@TODO:
"""
from __future__ import print_function

import numpy as np

from logging import DEBUG, INFO
from matplotlib.gridspec import GridSpec
from copy import deepcopy
from collections import OrderedDict
from PyAstronomy.pyasl import foldAt
# from collections import defaultdict

from fig_styler import styler

import source.tools.emcee_tools as et
import source.posterior.core.posterior as cpost
import source.tools.mylogger as ml

from source.posterior.core.likelihood.manager_noise_model import Manager_NoiseModel

# from ipdb import set_trace


mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


@styler
def create_RV_plots(fig, ndataset, planets, periods, tcs, datasim_dbf, dataset_db, model_instance,
                    fitted_values, l_param_name, star,
                    fig_param=None, *args, **kwargs):
    nplanet = len(planets)

    ###########
    # Load Data
    ###########

    # Define dataset names
    dico_datasetname = OrderedDict()
    # 1. SOPHIE
    dico_datasetname["SOPHIE"] = {}
    dico_datasetname["SOPHIE"]["0"] = "RV_WASP-151_SOPHIE_0"
    # 3. CORALIE
    dico_datasetname["CORALIE"] = {}
    dico_datasetname["CORALIE"]["0"] = "RV_WASP-151_CORALIE_0"

    # Load the defined datasets
    dico_dataset = {}
    dico_kwargs = {}
    for inst in dico_datasetname:
        dico_dataset[inst] = {}
        dico_kwargs[inst] = {}
        for key in dico_datasetname[inst]:
            dico_dataset[inst][key] = dataset_db[dico_datasetname[inst][key]]
            dico_kwargs[inst][key] = dico_dataset[inst][key].get_kwargs()

    ###################
    # Plots preparation
    ###################

    # Create the gridspec
    if fig_param is None:
        fig_param = {}
    left = fig_param.get("left", 0.17)
    right = fig_param.get("right", 0.98)
    top = fig_param.get("top", 0.98)
    bottom = fig_param.get("bottom", 0.1)

    gs = GridSpec(nrows=1, ncols=1,
                  left=left, bottom=bottom, right=right, top=top,
                  wspace=None, hspace=None)

    # Set parameters for the instrument gridspec
    gs_from_sps_kw = {"height_ratios": (3, 1)}  # Between the data plot and the resiudals plot

    # Set the plots keywords arguments
    pl_kwarg_data = {"color": None, "fmt": ".", "alpha": 1.}
    pl_kwarg_model = {"color": "k", "fmt": "", "alpha": 1., "linestyle": "-"}

    pl_kwarg = {}
    for inst in dico_datasetname:
        pl_kwarg[inst] = {"model": pl_kwarg_model, "data": {}}
        for key in dico_datasetname[inst]:
            pl_kwarg_data_key = deepcopy(pl_kwarg_data)
            pl_kwarg_data_key["label"] = inst
            pl_kwarg[inst]["data"][key] = pl_kwarg_data_key

    # Create the axes
    (ax_data, ax_resi) = et.add_twoaxeswithsharex_perplanet(gs[0], nplanet=nplanet, fig=fig,
                                                            gs_from_sps_kw=gs_from_sps_kw)
    ax_data0 = ax_data[0]
    ax_resi0 = ax_resi[0]

    # Set the axis labels
    ax_data0.set_ylabel(r"RV [$\kms$]")
    ax_resi0.set_ylabel(r"O - C [$\kms$]")
    for res_ax in ax_resi:
        res_ax.set_xlabel("Orbital phase")

    # Align y labels
    x_ylabel_coord = -0.15  # for y label alignment
    ax_data0.yaxis.set_label_coords(x_ylabel_coord, 0.5)
    ax_resi0.yaxis.set_label_coords(x_ylabel_coord, 0.5)

    # Number of point for plotting the model
    npt_model = 1000

    for i, planet_name in enumerate(planets):
        ax_data_pl = ax_data[i]
        ax_resi_pl = ax_resi[i]

        ax_data_pl.set_title("planet {}".format(planet_name))

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

        for inst in dico_datasetname:
            phases[inst] = OrderedDict()
            for key in dico_datasetname[inst]:
                phases[inst][key] = (foldAt(dico_kwargs[inst][key]["t"], Per, T0=(tc + Per / 2)) -
                                     0.5)

        ########################
        # Load datasim functions
        ########################
        datasim_docfunc = {}
        for inst in dico_datasetname:
            datasim_docfunc[inst] = {}
            for key in dico_datasetname[inst]:
                instmod_fullname_key = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
                datasim_docfunc[inst][key] = datasim_dbf.instrument_db[instmod_fullname_key]

        ##############################################
        # Apply the jitter to the data error if needed
        ##############################################
        data_err = OrderedDict()
        dico_jitter = {}
        for inst in dico_datasetname:
            data_err[inst] = OrderedDict()
            dico_jitter[inst] = {}
            for key in dico_datasetname[inst]:
                dico_jitter[inst][key] = {}
                data_err[inst][key] = dico_kwargs[inst][key]["data_err"]
                inst_mod_fullname = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
                inst_mod = model_instance.instruments[inst_mod_fullname]
                noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
                if noise_model.has_jitter:
                    dico_jitter[inst][key]["type"] = noise_model.jitter_type
                    if inst_mod.jitter.free:
                        idx_jitter = l_param_name.index(inst_mod.jitter.full_name)
                        dico_jitter[inst][key]["value"] = fitted_values[idx_jitter]
                    else:
                        dico_jitter[inst][key]["value"] = inst_mod.jitter.value
                    if dico_jitter[inst][key]["type"] == "multi":
                        data_err[inst][key] *= np.exp(dico_jitter[inst][key]["value"])
                    elif dico_jitter[inst][key]["type"] == "add":
                        data_err[inst][key] = np.sqrt(data_err[inst][key]**2 *
                                                      (1 +
                                                       np.exp(2 * dico_jitter[inst][key]["value"])))
                    else:
                        raise ValueError("Unknown jitter_type: {}".format(noise_model.jitter_type))
                else:
                    dico_jitter[inst][key]["type"] = None
                    dico_jitter[inst][key]["value"] = None

        ####################################################
        # Compute the deltaRV to apply to the data and model
        ####################################################
        deltaRV = OrderedDict()
        RVrefglobal_instname = model_instance.RV_references["global"]
        for inst in dico_datasetname:
            RVref4inst_modname = model_instance.RV_references[inst]
            deltaRV[inst] = OrderedDict()
            for key in dico_datasetname[inst]:
                instmod_fullname_key = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
                instmodobj_key = model_instance.instruments[instmod_fullname_key]
                deltaRV[inst][key] = 0.0
                if inst != RVrefglobal_instname:
                    instmod_RVref4inst = model_instance.instruments["RV"][inst][RVref4inst_modname]
                    if instmod_RVref4inst.DeltaRV.main:
                        if instmod_RVref4inst.DeltaRV.free:
                            idx_deltaRV = l_param_name.index(instmod_RVref4inst.DeltaRV.full_name)
                            deltaRV[inst][key] += fitted_values[idx_deltaRV]
                        else:
                            deltaRV[inst][key] += instmod_RVref4inst.DeltaRV.value
                if instmodobj_key.name != RVref4inst_modname:
                    if instmodobj_key.DeltaRV.main:
                        if instmodobj_key.DeltaRV.free:
                            idx_deltaRV = l_param_name.index(instmodobj_key.DeltaRV.full_name)
                            deltaRV[inst][key] += fitted_values[idx_deltaRV]
                        else:
                            deltaRV[inst][key] += instmodobj_key.DeltaRV.value

        RVrefglobal_modname = model_instance.RV_references[RVrefglobal_instname]
        datasim_RVrefglobal = (datasim_dbf.instrument_db["RV"][RVrefglobal_instname]
                               [RVrefglobal_modname][planet_name])

        ###############
        # Plot the data
        ###############
        idx_star_v0 = l_param_name.index(star.v0.full_name)
        for inst in dico_datasetname:
            for key in dico_datasetname[inst]:
                # Get the datasim for this planet only
                inst_mod_fullname = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
                # datasim_db_docfunc_pl = datasim_dbf.instrument_db[inst_mod_fullname][planet_name]
                # Get the datasims for the other planets
                l_datasim_db_docfunc_others = []
                for pl in planets:
                    if pl == planet_name:
                        continue
                    else:
                        l_datasim_db_docfunc_others.append(datasim_dbf.
                                                           instrument_db[inst_mod_fullname]
                                                           [pl])
                data_pl = dico_kwargs[inst][key]["data"] - deltaRV[inst][key]

                inst_mod_fullname = datasim_dbf.get_instmod_fullname(dico_datasetname[inst][key])
                inst_mod = model_instance.instruments[inst_mod_fullname]
                noise_model = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)

                for datasim_db_docfunc_other in l_datasim_db_docfunc_others:
                    kwargs_dataset = dico_kwargs[inst][key].copy()
                    kwargs_dataset.pop("data_err")
                    kwargs_dataset.pop("data")
                    model, modelwGP, _ = et.compute_model(kwargs_dataset.pop("t"),
                                                          datasim_db_docfunc_other,
                                                          fitted_values, l_param_name,
                                                          datasim_kwargs=kwargs_dataset,
                                                          noise_model=noise_model,
                                                          model_instance=model_instance)
                    data_pl = data_pl - (model - deltaRV[inst][key] - fitted_values[idx_star_v0])

                et.plot_phase_folded_timeserie(t=dico_kwargs[inst][key]["t"],
                                               data=data_pl,
                                               data_err=dico_kwargs[inst][key]["data_err"],
                                               jitter=dico_jitter[inst][key]["value"],
                                               jitter_type=dico_jitter[inst][key]["type"],
                                               P=Per, tc=tc,
                                               ax=ax_data_pl, pl_kwargs=pl_kwarg[inst]["data"][key])

        ################
        # Plot the model
        ################
        et.plot_model(tmin_model, tmax_model, npt_model, datasim_RVrefglobal, fitted_values,
                      l_param_name, plot_phase=True, P=Per, tc=tc,
                      pl_kwargs_model=pl_kwarg[RVrefglobal_instname]["model"],
                      ax=ax_data_pl)

        ####################
        # Plot the residuals
        ####################

        for inst in dico_datasetname:
            for key in dico_datasetname[inst]:
                et.plot_residuals(t=dico_kwargs[inst][key]["t"],
                                  data=dico_kwargs[inst][key]["data"],
                                  data_err=dico_kwargs[inst][key]["data_err"],
                                  jitter=dico_jitter[inst][key]["value"],
                                  jitter_type=dico_jitter[inst][key]["type"],
                                  datasim_db_docfunc=datasim_docfunc[inst][key][planet_name],
                                  param=fitted_values, l_param_name=l_param_name,
                                  plot_phase=True, P=Per, tc=tc,
                                  pl_kwargs_model=pl_kwarg[inst]["data"][key],
                                  ax=ax_resi_pl)

        ###################
        # Finalise the plot
        ###################
        ax_data[0].legend()


if __name__ == "__main__":
    # Define the object name
    obj_name = "WASP-151"

    ## logger
    logger = ml.init_logger(with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                            fh_lvl=DEBUG, fh_file="{}.log".format(obj_name))

    load_from_pickle = True

    logger.info("1. Load from pickle if necessary")
    if load_from_pickle:
        # recreate post_instance object
        post_instance = cpost.Posterior(object_name=obj_name)
        post_instance.init_from_pickle()
        l_param_name_bis = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
        # chain, lnprobability, acceptance_fraction, l_param_name = et.load_emceesampler(obj_name,
        #                                                                                folder=".")
        fitted_values_dic, fitted_values_sec_dic, df_fittedval = et.load_chain_analysis(obj_name,
                                                                                        folder=".")
        fitted_values = fitted_values_dic["array"]
        l_param_name = fitted_values_dic["l_param"]
        planet_name = []
        periods = {}
        tcs = {}
        for planet in post_instance.model.planets.values():
            planet_name.append(planet.name)
            periods[planet.name] = df_fittedval.loc[planet.P.full_name, 'value']
            tcs[planet.name] = df_fittedval.loc[planet.tc.full_name, 'value']

    dataset_db = post_instance.dataset_db
    datasim_dbf = post_instance.datasimulators
    model_instance = post_instance.model

    create_RV_plots(planets=planet_name, ndataset=1, periods=periods, tcs=tcs,
                    datasim_dbf=datasim_dbf, dataset_db=dataset_db, model_instance=model_instance,
                    fitted_values=fitted_values, l_param_name=l_param_name,
                    star=post_instance.model.stars[list(post_instance.model.stars)[0]],
                    figsize=(None, 0.5), tight=False, dpi=200,
                    fig_param={"top": 0.94, "bottom": 0.1, "left": 0.08},
                    type="A&Afw",
                    save="./images/custom_data_comp_RV.png"
                    )
