#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
emcee tools module.

The objective of this module is to provide a toolbox for the exploitation and visualisation of emcee
results.
"""
from logging import getLogger
from matplotlib.pyplot import subplots, figure, Subplot  # , figure, plot, show
import numpy as np
from numpy import linspace, median, where, array, argmax, unravel_index, ones, nan, sqrt, argsort
from numpy import percentile, exp
# from sys import stdout
import matplotlib.gridspec as gridspec
from matplotlib.gridspec import GridSpec
# from copy import deepcopy
# from collections import defaultdict
from tqdm import tqdm
from PyAstronomy.pyasl import foldAt
from dill import dump, load
from os.path import isfile, join
# import pprint

from .stats.loc_scale_estimator import mad
from .time_series_toolbox import get_time_supersampled, average_supersampled_values
from ..posterior.core.likelihood.jitter_noise_model import jitter_name
from ..posterior.core.likelihood.manager_noise_model import Manager_NoiseModel
# from ..posterior.core.posterior import alldtst_key


# from ipdb import set_trace


## Logger Object
logger = getLogger()

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


exptime_Kepler = 0.02043402778  # days


# The incremental saving doesn't work because, it writes to the fiel but then I don't know how to
# load it.
# def explore(sampler, p0, nsteps, width=50, save_to_file=None):
#     f = open(save_to_file, "w")
#     f.close()
#     for i, result in enumerate(sampler.sample(p0, iterations=nsteps, storechain=False)):
#         position = result[0]
#         f = open(save_to_file, "a")
#         for k in range(position.shape[0]):
#             f.write("{0:4d} {1:s}\n".format(k, " ".join([str(x) for x in position[k]])))
#         f.close()
#         n = int((width + 1) * float(i) / nsteps)
#         stdout.write("\r[{0}{1}]".format('#' * n, ' ' * (width - n)))
#     stdout.write("\n")

def get_init_distrib_from_fitvalues(fitted_values):
    """Generate the init_distrib dictionary for generate_random_init_pos from fitted_values.
    :param pd.DataFrame fitted_values: Fitted values from a previous run rows are parameter names
        columns are value, sigma+, sigma-

    :return dict init_distrib: dictionary of dictionary specifying the parameters "mu" and "sigma"
        of the normal distribution to use for each parameter. First level keys are parameter full
        name. Second is "sigma" and "mu".
    """
    init_distrib = {}
    for param, row in fitted_values.iterrows():
        init_distrib[param] = {"mu": row["value"], "sigma": np.mean([row["sigma+"], row["sigma-"]])}
    return init_distrib


def generate_random_init_pos(nwalker, post_instance, init_distrib=None):
    """Generate initial position from for the walkers.

    :param int nwalker: number of walkers
    :param Posterior post_instance: Instance of the posterior class
    :param dict init_distrib: dictionary of dictionary specifying the parameters "mu" and "sigma" of
        the normal distribution to use for each parameter. First level keys are parameter full name.
        Second is "sigma" and "mu".

    :return np.ndarray p0: Ndarray containing the initial positions for all the walkers
    """
    l_param_name = post_instance.lnposteriors.dataset_db["all"].arg_list["param"]
    p0 = []
    if init_distrib is None:
        return np.asarray([post_instance.model.get_initial_values(list_paramnames=l_param_name)
                           for i in range(nwalker)])
    else:
        for param in l_param_name:
            if param in init_distrib:
                p0.append(np.random.normal(loc=init_distrib[param]["mu"],
                                           scale=init_distrib[param]["sigma"],
                                           size=nwalker))
            else:
                p0.append(np.squeeze(np.asarray([post_instance.model.
                                                 get_initial_values(list_paramnames=[param])
                                                 for i in range(nwalker)])))
        return np.asarray(p0).transpose()


def explore(sampler, p0, nsteps):
    with tqdm(total=nsteps) as pbar:
        previous_i = -1
        for i, result in enumerate(sampler.sample(p0, iterations=nsteps, storechain=True)):
            pbar.update(i - previous_i)
            previous_i = i
    return result


def plot_chains(chains, lnprobability, l_param_name=None, l_walker=None, l_burnin=None,
                suppress_burnin=False, plot_height=2, plot_width=8, **kwargs_tl):
    ndim = chains.shape[-1]
    nwalker = chains.shape[0]
    fig, ax = subplots(nrows=ndim + 1, sharex=True, squeeze=True,
                       figsize=(plot_width, ndim * plot_height))
    l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=nwalker)
    l_param_name = __get_default_l_param_name(l_param_name=l_param_name, ndim=ndim)
    l_burnin = __get_default_l_burnin(l_burnin=l_burnin, nwalker=nwalker)
    lnprob_min = lnprobability[l_walker, ...].min()
    lnprob_max = lnprobability[l_walker, ...].max()
    for walker, burnin in zip(l_walker, l_burnin):
        ax[0].set_title("lnpost")
        line = ax[0].plot(lnprobability[walker, :], alpha=0.5)
        ax[0].vlines(burnin, lnprob_min, lnprob_max, color=line[0].get_color(), linestyles="dashed",
                     alpha=0.5)
    for i in range(ndim):
        ax[i + 1].set_title(l_param_name[i])
        vmin = chains[l_walker, :, i].min()
        vmax = chains[l_walker, :, i].max()
        for walker, burnin in zip(l_walker, l_burnin):
            if suppress_burnin:
                line = ax[i + 1].plot(chains[walker, burnin:, i], alpha=0.5)
            else:
                line = ax[i + 1].plot(chains[walker, :, i], alpha=0.5)
                ax[i + 1].vlines(burnin, vmin, vmax, color=line[0].get_color(), linestyles="dashed",
                                 alpha=0.5)
    ax[ndim].set_xlabel("iteration")
    fig.tight_layout(**kwargs_tl)


def overplot_data_model(param, l_param_name, datasim_dbf, dataset_db, datasim_kwargs={},
                        model_instance=None, oversamp=10, supersamp_model=1, exptime=exptime_Kepler,
                        phasefold=False, phasefold_kwargs=None,
                        plot_height=2, plot_width=8, kwargs_tl={}):
    """
    :param np.array param:
    :param list_of_string l_param_name:
    :param  datasim_dbf:
    :param DatasetDatabase dataset_db:
    :param Core_Model model_instance: Core_Model instance
    :param int oversamp: The model will computed in oversamp times more points than the data
    :param int supersamp_model: The model will computed in supersamp_model times more points and
                                then averaged over bins of supersamp_model to take into account an
                                increased exposure time.
    :param float exptime:
    :param bool phasefold:
    :param dict phasefold_kwargs:
    """
    # Check that if phasefold is True phasefold_kwargs is not None
    if phasefold and (phasefold_kwargs is None):
        raise ValueError("If you want to phase fold, you have to provide the phasefold_kwargs")

    # Get the list of all datasets names and the number of datasets
    l_datasets = dataset_db.get_datasets()
    ndataset = len(l_datasets)

    # Create the figure and grid which will harbor the plots for each dataset
    fig = figure(figsize=(plot_width, ndataset * plot_height))
    gs = GridSpec(nrows=ndataset, ncols=1)

    for ii, dataset in enumerate(l_datasets):
        inst_mod_fullname = datasim_dbf.get_instmod_fullname(dataset.dataset_name)
        datasim_db_docfunc = datasim_dbf.instrument_db[inst_mod_fullname]["whole"]
        inst_mod = model_instance.instruments[inst_mod_fullname]
        noise_mod = mgr_noisemodel.get_noisemodel_subclass(inst_mod.noise_model)
        kwargs = dataset.get_kwargs()
        t = kwargs.pop("t")
        nt = len(t)
        data = kwargs.pop("data")
        data_err = kwargs.pop("data_err")
        kwargs.update(datasim_kwargs)

        if noise_mod.has_jitter:
            jitter_param_fullname = inst_mod.parameters[jitter_name].full_name
            if inst_mod.parameters[jitter_name].free:
                idx_jitter = l_param_name.index(jitter_param_fullname)
                jitter = param[idx_jitter]
            else:
                jitter = inst_mod.parameters[jitter_name].value
            jitter_type = noise_mod.jitter_type
        else:
            jitter = None
            jitter_type = None

        if phasefold:
            # Create the Axes for the comparison data/model and the residuals and set the title.
            # and plot the data
            (axes_data,
             axes_resi) = add_twoaxeswithsharex_perplanet(gs[ii],
                                                          nplanet=len(phasefold_kwargs["planets"]),
                                                          fig=fig,
                                                          gs_from_sps_kw={"height_ratios": (3, 1)})
            title_printed = False
            for planet_name, P, tc, ax_data, ax_resi in zip(phasefold_kwargs["planets"],
                                                            phasefold_kwargs["P"],
                                                            phasefold_kwargs["tc"],
                                                            axes_data, axes_resi):
                # Get the datasim for this planet only
                datasim_db_docfunc_pl = datasim_dbf.instrument_db[inst_mod_fullname][planet_name]

                # Get the datasims for the other planets
                l_datasim_db_docfunc_others = []
                for pl in phasefold_kwargs["planets"]:
                    if pl == planet_name:
                        continue
                    else:
                        l_datasim_db_docfunc_others.append(datasim_dbf.
                                                           instrument_db[inst_mod_fullname]
                                                           [pl])

                if not(title_printed):
                    ax_data.set_title(dataset.dataset_name)
                    title_printed = True
                # Plot the data
                data_pl = data.copy()
                pl_kwargs = {"color": "b", "fmt": "."}

                for datasim_db in l_datasim_db_docfunc_others:
                    model, modelwGP, _ = compute_model(t, datasim_db, param, l_param_name,
                                                       datasim_kwargs=kwargs,
                                                       supersamp=supersamp_model, exptime=exptime,
                                                       noise_model=noise_mod,
                                                       model_instance=model_instance)
                    data_pl = data_pl - model
                _, phases = plot_phase_folded_timeserie(t=t, data=data_pl, P=P, tc=tc,
                                                        data_err=data_err,
                                                        jitter=jitter, jitter_type=jitter_type,
                                                        ax=ax_data,
                                                        pl_kwargs=pl_kwargs)

                # Plot the model
                phasemin = phases.min()
                phasemax = phases.max()
                tmin = tc + P * phasemin
                tmax = tc + P * phasemax
                plot_model(tmin, tmax, nt * oversamp, datasim_db_docfunc_pl, param, l_param_name,
                           supersamp=supersamp_model, exptime=exptime,
                           datasim_kwargs={'tref': tmin}, plot_phase=True, P=P, tc=tc,
                           noise_model=noise_mod,
                           model_instance=model_instance,
                           ax=ax_data)
                # Plot residuals
                plot_residuals(t, data, datasim_db_docfunc_pl, param, l_param_name,
                               data_err=data_err, jitter=jitter, jitter_type=jitter_type,
                               supersamp=supersamp_model, exptime=exptime,
                               datasim_kwargs=kwargs, plot_phase=True, P=P, tc=tc,
                               noise_model=noise_mod,
                               model_instance=model_instance,
                               ax=ax_resi)
        else:
            # Create the Axes for the comparison data/model and the residuals and set the title.
            # and plot the data
            ax_data, ax_resi = add_twoaxeswithsharex(gs[ii], fig=fig,
                                                     gs_from_sps_kw={"height_ratios": (3, 1)})
            ax_data.set_title(dataset.dataset_name)

            if jitter is None:
                data_err_new = data_err
            else:
                if jitter_type == "multi":
                    data_err_new = data_err * exp(jitter)
                elif jitter_type == "add":
                    data_err_new = sqrt(data_err**2 * (1 + exp(2 * jitter)))
                else:
                    raise ValueError("jitter_type should be in ['multi', 'add']")

            ax_data.errorbar(t, data, data_err_new, fmt=".", color="b")

            # Plot the model
            tmin = t.min()
            tmax = t.max()
            plot_model(tmin, tmax, nt * oversamp, datasim_db_docfunc, param, l_param_name,
                       datasim_kwargs=kwargs, supersamp=supersamp_model, exptime=exptime,
                       plot_phase=False, noise_model=noise_mod,
                       model_instance=model_instance, ax=ax_data)

            # Plot the residuals
            plot_residuals(t, data, datasim_db_docfunc, param, l_param_name, data_err=data_err,
                           jitter=jitter, jitter_type=jitter_type,
                           datasim_kwargs=kwargs, supersamp=supersamp_model, exptime=exptime,
                           plot_phase=False, noise_model=noise_mod,
                           model_instance=model_instance, ax=ax_resi)

        # Plot the legend
        ax_data.legend(loc='upper right', shadow=True)

    fig.tight_layout(**kwargs_tl)


def compute_model(t, datasim_db_docfunc, param, l_param_name, datasim_kwargs=None,
                  supersamp=1, exptime=exptime_Kepler,
                  noise_model=None, model_instance=None):
    # Supersample the time if needed
    if supersamp > 1:
        t_model = get_time_supersampled(t, supersamp, exptime)
    else:
        t_model = t

    # If datasim_kwargs is None affect an empty dict and no additional arguments will be passed to
    # the datasim function
    if datasim_kwargs is None:
        datasim_kwargs = {}

    # Compute the model values for each time
    idx_par = []
    datasim_function = datasim_db_docfunc.function
    datasim_paramnames = datasim_db_docfunc.params_model
    for par in datasim_paramnames:
        idx_par.append(l_param_name.index(par))
    model = datasim_function(param[idx_par], t_model, **datasim_kwargs)
    if supersamp > 1:
        model = average_supersampled_values(model, supersamp)

    # Compute the model + GP
    if noise_model is not None:
        if noise_model.has_GP:
            datasim_all = (model_instance.
                           create_datasimulator_alldatasets(dataset_db=model_instance.dataset_db))
            idx_datasim = []
            for param_name in datasim_all.params_model:
                idx_datasim.append(l_param_name.index(param_name))
            model_all = datasim_all.function(param[idx_datasim])
            l_instmod_noisemod_cat = []
            for inst_mod in model_instance.get_instmodels_used():
                if inst_mod.noise_model == noise_model.category:
                    l_instmod_noisemod_cat.append(inst_mod.full_name)
            idx_noisemod_GP = [ii for ii, instmod_fullname in
                               enumerate(datasim_all.instmodel_fullname)
                               if instmod_fullname in l_instmod_noisemod_cat]
            l_dataset_noisemod_cat = datasim_all.dataset.iloc[idx_noisemod_GP]
            model_noisemodel_GP = [mod_ii for ii, mod_ii in enumerate(model_all)
                                   if ii in idx_noisemod_GP]
            (gpsim_func,
             l_param_noisemod) = (noise_model.
                                  get_gp_simulator(model_instance,
                                                   l_param_name)
                                  )
            idx_noisemod = []
            for param_name in l_param_noisemod:
                idx_noisemod.append(l_param_name.index(param_name))
            l_datakwargs_noisemod = []
            for dataset_name in l_dataset_noisemod_cat:
                dataset = model_instance.dataset_db[dataset_name]
                l_datakwargs_noisemod.append(noise_model.get_necessary_datakwargs(dataset))
            gp_model = gpsim_func(model_noisemodel_GP, param[idx_noisemod],
                                  l_datakwargs_noisemod,
                                  t_model)
            if supersamp > 1:
                gp_model = np.mean(gp_model.reshape(-1, supersamp), axis=1)
            model_wGP = model + gp_model
        else:
            model_wGP = None
    else:
        model_wGP = None

    return model, model_wGP, t_model


def plot_model(tmin, tmax, nt, datasim_db_docfunc, param, l_param_name, datasim_kwargs=None,
               supersamp=1, exptime=exptime_Kepler,
               plot_phase=False, P=None, tc=None,
               noise_model=None, model_instance=None,
               pl_kwargs_model=None, pl_kwargs_modelandGP=None,
               ax=None):
    # Create the time sampling (tsamp) and the tmin and tmax for the model computation (tmin_moins,
    # tmax_plus), the model time vector (t)
    tsamp = (tmax - tmin) / (nt - 1)  # nt - 1 because this the number of intervals
    tmin_moins = tmin - tsamp  # Add 1 point before tmin
    tmax_plus = tmax + tsamp  # Add 1 point after tmax
    nt += 2
    t_plot = linspace(tmin_moins, tmax_plus, nt)
    model, model_wGP, _ = compute_model(t_plot, datasim_db_docfunc, param, l_param_name,
                                        datasim_kwargs=datasim_kwargs, supersamp=supersamp,
                                        exptime=exptime,
                                        noise_model=noise_model,
                                        model_instance=model_instance)

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Plot the model
    kwarg_model = {"label": "model", "color": "g", "fmt": "-", "alpha": 0.6}
    if pl_kwargs_model is not None:
        kwarg_model.update(pl_kwargs_model)
    if plot_phase:
        line, _ = plot_phase_folded_timeserie(t_plot, model, P, tc, ax=ax, pl_kwargs=kwarg_model)
    else:
        line = ax.errorbar(t_plot, model, **kwarg_model)

    # Plot the model + GP
    if model_wGP is not None:
        kwarg_GP = {"label": "model+GP", "color": "r", "fmt": "-", "alpha": 0.6}
        if pl_kwargs_modelandGP is not None:
            kwarg_GP.update(pl_kwargs_modelandGP)
        if plot_phase:
            line_wGP, _ = plot_phase_folded_timeserie(t_plot, model_wGP, P, tc, ax=ax,
                                                      pl_kwargs=kwarg_GP)
        else:
            line_wGP = ax.errorbar(t_plot, model_wGP, **kwarg_GP)
    else:
        line_wGP = None
    return line, line_wGP


def plot_residuals(t, data, datasim_db_docfunc, param, l_param_name,
                   datasim_kwargs=None, data_err=None, jitter=None, jitter_type=None,
                   supersamp=1, exptime=exptime_Kepler, plot_phase=False, P=None, tc=None,
                   noise_model=None, model_instance=None,
                   pl_kwargs_model=None, show_model=True,
                   pl_kwargs_modelandGP=None, show_modelandGP=True,
                   ax=None):

    model, model_wGP, _ = compute_model(t, datasim_db_docfunc, param, l_param_name,
                                        datasim_kwargs=datasim_kwargs, supersamp=supersamp,
                                        exptime=exptime,
                                        noise_model=noise_model,
                                        model_instance=model_instance)

    residual = data - model

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Plot the residuals
    kwarg_model = {"label": "model", "color": "g", "fmt": "."}
    if noise_model is None:
        noise_modelGP = False
    else:
        noise_modelGP = noise_model.has_GP

    if show_model or not(noise_modelGP):
        if pl_kwargs_model is not None:
            kwarg_model.update(pl_kwargs_model)
        if plot_phase:
            plot_phase_folded_timeserie(t, residual, P, tc,
                                        data_err=data_err, jitter=jitter, jitter_type=jitter_type,
                                        ax=ax, pl_kwargs=kwarg_model)
        else:
            if jitter is None:
                ax.errorbar(t, residual, data_err, **kwarg_model)
            else:
                if jitter_type == "multi":
                    ax.errorbar(t, residual, data_err * exp(jitter), **kwarg_model)
                elif jitter_type == "add":
                    ax.errorbar(t, residual, sqrt(data_err**2 * (1 + exp(2 * jitter))),
                                **kwarg_model)
                else:
                    raise ValueError("jitter_type should be in ['multi', 'add']")

    # Plot the model + GP
    if noise_model is not None:
        if noise_model.has_GP and show_modelandGP:
            residual_wGP = data - model_wGP
            kwarg_GP = {"label": "model+GP", "color": "r", "fmt": ".", "alpha": 0.6}
            if pl_kwargs_modelandGP is not None:
                kwarg_GP.update(pl_kwargs_modelandGP)
            if plot_phase:
                plot_phase_folded_timeserie(t, residual_wGP, P, tc, data_err=data_err,
                                            jitter=jitter, jitter_type=jitter_type,
                                            ax=ax, pl_kwargs=kwarg_GP)
            else:
                if jitter is None:
                    ax.errorbar(t, residual_wGP, data_err, **kwarg_GP)
                else:
                    if jitter_type == "multi":
                        ax.errorbar(t, residual_wGP, data_err * exp(jitter), **kwarg_GP)
                    elif jitter_type == "add":
                        ax.errorbar(t, residual_wGP, sqrt(data_err**2 * (1 + exp(2 * jitter))),
                                    **kwarg_GP)
                    else:
                        raise ValueError("jitter_type should be in ['multi', 'add']")

    # Draw a line y=0 for the residuals
    xmin, xmax = ax.get_xlim()
    ax.hlines(y=0.0, xmin=xmin, xmax=xmax, linestyles="dashed", linewidth=1)
    ax.set_xlim(xmin, xmax)


def plot_phase_folded_timeserie(t, data, P, tc, data_err=None, jitter=None, jitter_type=None,
                                ax=None, pl_kwargs=None):
    """Plot a phase folded representation of a lc

    :param Dataset dataset: LC dataset
    :param float P: Period of the planet
    :param float tc: Time of inferior conjuction of the planet

    P and tc needs to have the same unit than the time in dataset.
    """
    # Obtain the phases with respect to some ephemerid P and tc
    phases = foldAt(t, P, T0=(tc + P / 2)) - 0.5

    # Sort with respect to phase
    sortIndi = argsort(phases)

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Check the errorbar kwargs
    kw = dict() if pl_kwargs is None else pl_kwargs.copy()
    if "fmt" not in kw:
        kw["fmt"] = "-"
    if "color" not in kw:
        kw["color"] = "r"

    # Plot the phase folded data
    if data_err is not None:
        if jitter is None:
            line = ax.errorbar(phases[sortIndi], data[sortIndi], data_err[sortIndi], **kw)
        else:
            if jitter_type == "multi":
                line = ax.errorbar(phases[sortIndi], data[sortIndi],
                                   data_err[sortIndi] * exp(jitter), **kw)
            elif jitter_type == "add":
                line = ax.errorbar(phases[sortIndi], data[sortIndi],
                                   sqrt(data_err[sortIndi]**2 * (1 + exp(2 * jitter))), **kw)
            else:
                raise ValueError("jitter_type should be in ['multi', 'add']")
    else:
        line = ax.errorbar(phases[sortIndi], data[sortIndi], **kw)
    return line, phases


def add_twoaxeswithsharex(subplotspec, fig, gs_from_sps_kw=None):
    """Add two axes to a subplotspec (created with gridspec) for data and residual plot. """
    # Set the default values for GridSpecFromSubplotSpec
    kw = dict() if gs_from_sps_kw is None else gs_from_sps_kw.copy()
    if "hspace" not in kw:
        kw["hspace"] = 0.1
    if "height_ratios" not in kw:
        kw["height_ratios"] = (4, 1)

    # Create the two axes, share x axis and set the ticks and ticks label properties
    gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=subplotspec, **kw)
    ax0 = Subplot(fig, gs[0])
    ax0.locator_params(axis="y", tight=True, nbins=4)
    ax0.tick_params(labelbottom="off")
    fig.add_subplot(ax0)
    ax1 = Subplot(fig, gs[1], sharex=ax0)
    fig.add_subplot(ax1)
    ax1.locator_params(axis="y", tight=True, nbins=4)

    # Return the two axes
    return ax0, ax1


def add_twoaxeswithsharex_perplanet(subplotspec, nplanet, fig, gs_from_sps_kw=None):
    """Add two axes per planet to a subplotspec (created with gridspec) for data and residual plot.
    """
    # Create the nplanet axes
    gs = gridspec.GridSpecFromSubplotSpec(1, nplanet, subplot_spec=subplotspec)

    # Create the two axes for the data and the residuals for each planet
    axes_data = []
    axes_resi = []
    for gs_elem in gs:
        ax_data, ax_resi = add_twoaxeswithsharex(gs_elem, fig, gs_from_sps_kw=gs_from_sps_kw)
        axes_data.append(ax_data)
        axes_resi.append(ax_resi)
    return axes_data, axes_resi


# Work in Progress to detect outliers before plotting
# def apply_mask(x=None):
#     '''
#     Returns the outlier mask, an array of indices corresponding to the non-outliers.
#
#     :param numpy.ndarray x: If specified, returns the masked version of :py:obj:`x` instead.
#        Default :py:obj:`None`
#
#     WORK IN PROGRESS
#     '''
#
#     if x is None:
#         return np.delete(np.arange(len(self.time)), self.mask)
#     else:
#         return np.delete(x, self.mask, axis=0)


def acceptancefraction_selection(acceptance_fraction, sig_fact=3., quantile=75, verbose=1):
    """Return selected walker based on the acceptance fraction.

    :param emcee.EnsembleSampler sampler:
    :param float sig_fact: acceptance fraction below mean - sig_fact * sigma will be rejected
    :param int verbose: if 1 speaks otherwise not
    """
    percentile_acceptance_frac = percentile(acceptance_fraction, quantile)
    mad_acceptance_frac = mad(acceptance_fraction)
    if verbose == 1:
        logger.info("Acceptance fraction of the walkers: {}\nquantile {}%: {}, MAD:{}"
                    "".format(acceptance_fraction, quantile, percentile_acceptance_frac,
                              mad_acceptance_frac))
    l_selected_walker = where(acceptance_fraction > (percentile_acceptance_frac -
                                                     sig_fact * mad_acceptance_frac))[0]
    nb_rejected = acceptance_fraction.shape[0] - len(l_selected_walker)
    if verbose == 1:
        logger.info("Number of rejected walkers: {}/{}".format(nb_rejected,
                                                               acceptance_fraction.shape[0]))
    return l_selected_walker, nb_rejected


def lnposterior_selection(lnprobability, sig_fact=3., quantile=75, quantile_walker=50, verbose=1):
    """Return selected walker based on the acceptance fraction.

    :param emcee.EnsembleSampler sampler:
    :param float sig_fact: acceptance fraction below mean - sig_fact * sigma will be rejected
    :param int verbose: if 1 speaks otherwise not
    :return list_of_int l_selected_walker: list of selected walker
    :return int nb_rejected:  number of rejected walker
    """
    walkers_percentile_lnposterior = percentile(lnprobability, quantile_walker, axis=1)
    percentile_lnposterior = percentile(walkers_percentile_lnposterior, quantile)
    mad_lnposterior = mad(walkers_percentile_lnposterior)
    if verbose == 1:
        logger.info("lnposterior of the walkers: {}\nquantile {}%: {}, MAD:{}"
                    "".format(walkers_percentile_lnposterior, quantile, percentile_lnposterior,
                              mad_lnposterior))
    l_selected_walker = where(walkers_percentile_lnposterior >
                              (percentile_lnposterior - (sig_fact * mad_lnposterior)))[0]
    nb_rejected = lnprobability.shape[0] - len(l_selected_walker)
    if verbose == 1:
        logger.info("Number of rejected walkers: {}/{}".format(nb_rejected, lnprobability.shape[0]))
    return l_selected_walker, nb_rejected


def get_fitted_values(chainI, method="MAP", l_param_name=None, l_walker=None, l_burnin=None,
                      lnprobability=None, verbose=1):
    """Return the fitted values from the sampler.

    :param ChainInterpret chainI:
    :param string method: method used to extract the fitted values ["MAP", "median"]
    :param int_iteratable l_walkers: list of valid walkers
    :param int burnin: index of the first iteration to consider.
    :param int verbose: if 1 speaks otherwise not
    """
    ndim = chainI.dim
    if method == "median":
        res = np.nanmedian(get_clean_flatchain(chainI, l_walker=l_walker, l_burnin=l_burnin),
                           axis=0)
    elif method == "MAP":
        if (l_walker is not None) or (l_burnin is not None):
            logger.warning("With method MAP the l_walker and l_burnin arguments are ignored.")
        walker, it = unravel_index(argmax(lnprobability), dims=lnprobability.shape)
        res = array([chainI[walker, it, dim] for dim in range(ndim)])
    else:
        raise ValueError("Method {} is not recognised".format(method))
    if verbose == 1:
        l_param_names = __get_default_l_param_name(l_param_name, ndim)
        text = "\n"
        for i, param_name in enumerate(l_param_names):
            text += "{} = {}\n".format(param_name, res[i])
        logger.info(text)
    return res


def get_clean_flatchain(chainI, l_walker=None, l_burnin=None):
    """Return a flatchain with only the selected walkers and iteration after the burnin.

    :param ChainInterpret chainI:
    :param int_iteratable l_walkers: list of valid walkers
    :param int_iteratable l_burnin: list of burnin iterations for each valid walker
    :return np.array res: cleaned flat chain
    """
    if (l_walker is None) and (l_burnin is None):
        return chainI.flatchain
    else:
        l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=chainI.shape[0])
    if l_burnin is None:
        s = chainI[l_walker, ...].shape
        return chainI[l_walker, ...].reshape(s[0] * s[1], s[2])
    else:
        l_burnin = __get_default_l_burnin(l_burnin=l_burnin, nwalker=chainI.shape[0])
    ndim = chainI.dim
    res = []
    if ndim == 1:
        for walker, burnin in zip(l_walker, l_burnin):
            res.extend(chainI[walker, burnin:])
        return array(res).transpose()
    else:
        for dim in range(ndim):
            res.append([])
            for walker, burnin in zip(l_walker, l_burnin):
                res[dim].extend(chainI[walker, burnin:, dim])
        return array(res).transpose()


def geweke_multi(chains, first=0.1, last=0.5, intervals=20, l_walker=None):
    """Adapted the geweke test for multiple wlaker exploration.

    :param emcee.EnsembleSampler sampler:
    :param float last: first portion of the chain to be used in the Geweke diagnostic.
        Default to 0.1 (i.e. first 10 % of the chain)
    :param float last: last portion of the chain to be used in the Geweke diagnostic.
        Default to 0.5 (i.e. last 50 % of the chain)
    :param int intervals: Number of sub-chains to analyze. Defaults to 20.
    :param int_iteratable l_walker: list of valid walkers
    """
    nwalker = chains.shape[0]
    ndim = chains.shape[-1]
    # Get the list of valid walkers (l_walker), the number of parameters (ndim) and the number of
    # steps for each walker (nsteps)
    l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=nwalker)
    nwalker = len(l_walker)
    nsteps = chains.shape[1]

    # Compute the start step of the last part of the chain and compute median and MAD of the last
    # part of the chain for each parameter
    last_start_step = nsteps - int(nsteps * last)
    l_med_last = [median(chains[l_walker, last_start_step:, dim]) for dim in range(ndim)]
    print("l_med_last: {}".format(l_med_last))
    l_mad_last = [mad(chains[l_walker, last_start_step:, dim]) for dim in range(ndim)]
    print("l_mad_last: {}".format(l_mad_last))

    # Compute the start steps of all the first parts of the chains that we will use for the Geweke
    # diagnostic (first_start_steps) and length of those first part (first_length).
    first_start_steps = [int(i * (last_start_step / intervals)) for i in range(intervals)]
    first_length = int(nsteps * first)
    # Then for each parameter and for each walker and for each first part compute the Geweke z-score
    zscores = ones((nwalker, intervals, ndim)) * nan
    for dim, med_last, mad_last in zip(range(ndim), l_med_last, l_mad_last):
        for i, walker in enumerate(l_walker):
            for j, first_start in enumerate(first_start_steps):
                med_first = median(chains[walker, first_start:(first_start + first_length), dim])
                mad_first = mad(chains[walker, first_start:(first_start + first_length), dim])
                # Compute the zscore, but if the dispersion of the first part is too big compared to
                # the last part, I don't consider the first part as converge what the zscore.
                if mad_first < (5 * mad_last):
                    zscores[i, j, dim] = (med_first - med_last) / (sqrt(mad_first**2 + mad_last**2))
                else:
                    zscores[i, j, dim] = np.inf
    return zscores, first_start_steps


def geweke_plot(zscores, first_steps=None, l_param_name=None,
                plot_height=2, plot_width=8, **kwargs_tl):
    ndim = zscores.shape[-1]
    nwalker = zscores.shape[0]
    fig, ax = subplots(nrows=ndim, sharex=True, squeeze=True,
                       figsize=(plot_width, ndim * plot_height))
    l_param_name = __get_default_l_param_name(l_param_name=l_param_name, ndim=ndim)
    first_steps = __get_default_first_steps(first_steps=first_steps, intervals=zscores.shape[1])
    xmin = min(first_steps)
    xmax = max(first_steps)
    for i in range(ndim):
        ax[i].set_title(l_param_name[i])
        for k in range(nwalker):
            ax[i].plot(first_steps, zscores[k, :, i], alpha=0.5)

        ax[i].hlines([-2, 2], xmin, xmax, linestyles="dashed")
    ax[ndim - 1].set_xlabel("iteration")
    fig.tight_layout(**kwargs_tl)


def geweke_selection(zscores, first_steps=None, geweke_thres=2., l_walker=None, verbose=1):
    """Compute the burnin for each valid walker based on their zscores.

    :param numpy.ndarray zscores:
    :param int_iteratable l_walker: list of valid walkers
    """
    res = abs(zscores) <= geweke_thres
    nwalker = zscores.shape[0]
    intervals = zscores.shape[1]
    first_steps = __get_default_first_steps(first_steps=first_steps, intervals=intervals)
    l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=nwalker)
    l_burnin = []
    l_walker_new = []
    for i in range(nwalker):
        for j in range(intervals):
            if res[i, j:, :].all():
                l_burnin.append(first_steps[j])
                l_walker_new.append(l_walker[i])
                break
    if verbose == 1:
        logger.info("List of burnin for valid walker: {}".format(dict(zip(l_walker, l_burnin))))
        logger.info("Number of walkers invalid walkers found: {}/{}"
                    "".format(len(l_walker) - len(l_walker_new), len(l_walker)))
    return l_burnin, l_walker_new


def __get_default_l_walker(l_walker, nwalker):
    if l_walker is None:
        l_walker = [i for i in range(nwalker)]
    return l_walker


def __get_default_l_param_name(l_param_name, ndim):
    if l_param_name is None:
        l_param_name = [str(i) for i in range(ndim)]
    return l_param_name


def __get_default_l_burnin(l_burnin, nwalker):
    if l_burnin is None:
        l_burnin = [0 for i in range(nwalker)]
    return l_burnin


def __get_default_first_steps(first_steps, intervals):
    return __get_default_l_walker(first_steps, intervals)


def __get_default_ax(ax):
    if ax is None:
        fig, ax = subplots(nrows=1, ncols=1, squeeze=True)
    return ax


def write_latex_table(filename, df_fitval, obj_name=None):
    """Write a TeX file with a table giving the fitted values."""
    if obj_name is None:
        obj_name = ''
    # Create Latex table
    with open(filename, "w") as f:
        f.write("\\begin{table}\n\\caption{\\label{}}\n\\begin{tabular}{lc}\\hline\n")
        f.write("Parameters & {}\\\\ \\hline\n".format(obj_name))
        for par in df_fitval.index:
            f.write("{} & ${}_{{-{}}}^{{+{}}}$\\\\\n".format(par.replace('_', '\\_'),
                                                             df_fitval.loc[par, 'value'],
                                                             df_fitval.loc[par, 'sigma-'],
                                                             df_fitval.loc[par, 'sigma+']))
        f.write("\\hline\n\\\\")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


extension_pickle = {"chain": "_chain.pk",
                    "lnpost": "_lnprobability.pk",
                    "acceptfrac": "_acceptance_fraction.pk",
                    "l_param_name": "_l_param_name.pk",
                    "df_fittedval": "_df_fittedval.pk",
                    "fitted_values": "_fitted_values.pk",
                    "fitted_values_sec": "_fitted_values_sec.pk",
                    }


def save_emceesampler(sampler, l_param_name, obj_name):
    """Save Emcee sampler elements."""

    # Save chain in a pickle
    with open("{}{}".format(obj_name, extension_pickle["chain"]), "wb") as fchain:
        dump(sampler.chain, fchain)

    # Save lnprobability in a pickle
    with open("{}{}".format(obj_name, extension_pickle["lnpost"]), "wb") as flnprob:
        dump(sampler.lnprobability, flnprob)

    # Save acceptance_fraction in a pickle
    with open("{}{}".format(obj_name, extension_pickle["acceptfrac"]), "wb") as faccfrac:
        dump(sampler.acceptance_fraction, faccfrac)

    # Save l_param_name in a pickle
    with open("{}{}".format(obj_name, extension_pickle["l_param_name"]), "wb") as flparam:
        dump(l_param_name, flparam)


def save_chain_analysis(obj_name, fitted_values=None, fitted_values_sec=None, df_fittedval=None):
    """Save Emcee sampler elements."""

    # Save df_fittedval in a pickle
    if df_fittedval is not None:
        with open("{}{}".format(obj_name, extension_pickle["df_fittedval"]), "wb") as fdffitval:
            dump(df_fittedval, fdffitval)

    # Save fitted_values in a pickle
    if fitted_values is not None:
        if "array" not in fitted_values or "l_param" not in fitted_values:
            raise ValueError("fitted_values should be a dictionary with 2 keys 'array' and "
                             "'l_param'")
        with open("{}{}".format(obj_name, extension_pickle["fitted_values"]), "wb") as ffitval:
            dump(fitted_values, ffitval)

    # Save fitted_values in a pickle
    if fitted_values_sec is not None:
        if "array" not in fitted_values or "l_param" not in fitted_values:
            raise ValueError("fitted_values should be a dictionary with 2 keys 'array' and "
                             "'l_param'")
        with open("{}{}".format(obj_name, extension_pickle["fitted_values_sec"]), "wb") as ffitvals:
            dump(fitted_values_sec, ffitvals)


def load_emceesampler(obj_name, folder="."):
    """Save Emcee sampler elements."""

    # Save chain in a pickle
    with open("{}{}".format(obj_name, extension_pickle["chain"]), "rb") as fchain:
        chain = load(fchain)

    # Save lnprobability in a pickle
    with open("{}{}".format(obj_name, extension_pickle["lnpost"]), "rb") as flnprob:
        lnprobability = load(flnprob)

    # Save acceptance_fraction in a pickle
    with open("{}{}".format(obj_name, extension_pickle["acceptfrac"]), "rb") as faccfrac:
        acceptance_fraction = load(faccfrac)

    # Save l_param_name in a pickle
    with open("{}{}".format(obj_name, extension_pickle["l_param_name"]), "rb") as flparam:
        l_param_name = load(flparam)

    return chain, lnprobability, acceptance_fraction, l_param_name


def load_chain_analysis(obj_name, folder="."):
    """Save Emcee sampler elements."""

    # load df_fittedval from a pickle
    file_df_fittedval = "{}{}".format(obj_name, extension_pickle["df_fittedval"])
    if isfile(join(folder, file_df_fittedval)):
        with open(join(folder, file_df_fittedval), "rb") as fdffitval:
            df_fittedval = load(fdffitval)
    else:
        df_fittedval = None

    # Load fitted_values from a pickle
    file_fitted_values = "{}{}".format(obj_name, extension_pickle["fitted_values"])
    if isfile(join(folder, file_fitted_values)):
        with open(join(folder, file_fitted_values), "rb") as ffitval:
            fitted_values = load(ffitval)
    else:
        fitted_values = None

    # Load fitted_values_sec from a pickle
    file_fitted_values_sec = "{}{}".format(obj_name, extension_pickle["fitted_values_sec"])
    if isfile(join(folder, file_fitted_values_sec)):
        with open(join(folder, file_fitted_values_sec), "rb") as ffitvals:
            fitted_values_sec = load(ffitvals)
    else:
        fitted_values_sec = None

    return fitted_values, fitted_values_sec, df_fittedval
