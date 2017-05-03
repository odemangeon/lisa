#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
emcee tools module.

The objective of this module is to provide a toolbox for the exploitation and visualisation of emcee
results.
"""
from logging import getLogger
from matplotlib.pyplot import subplots, subplot, figure  # , figure, plot, show
from numpy import linspace, median, where, array, argmax, unravel_index, ones, nan, sqrt, argsort
# from sys import stdout
import matplotlib.gridspec as gridspec
from matplotlib.gridspec import GridSpec
# from copy import deepcopy
from collections import defaultdict
from tqdm import tqdm
from PyAstronomy.pyasl import foldAt
from .stats.loc_scale_estimator import mad


## Logger Object
logger = getLogger()


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

def explore(sampler, p0, nsteps):
    with tqdm(total=nsteps) as pbar:
        previous_i = -1
        for i, result in enumerate(sampler.sample(p0, iterations=nsteps, storechain=True)):
            pbar.update(i - previous_i)
            previous_i = i


def plot_chains(sampler, l_param_name=None, l_walker=None, l_burnin=None,
                plot_height=2, plot_width=8, **kwargs_tl):
    fig, ax = subplots(nrows=sampler.dim + 1, sharex=True, squeeze=True,
                       figsize=(plot_width, sampler.dim * plot_height))
    l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=sampler.chain.shape[0])
    l_param_name = __get_default_l_param_name(l_param_name=l_param_name, ndim=sampler.dim)
    l_burnin = __get_default_l_burnin(l_burnin=l_burnin, nwalker=sampler.chain.shape[0])
    lnprob_min = sampler.lnprobability[l_walker, ...].min()
    lnprob_max = sampler.lnprobability[l_walker, ...].max()
    for walker, burnin in zip(l_walker, l_burnin):
        ax[0].set_title("lnpost")
        line = ax[0].plot(sampler.lnprobability[walker, :], alpha=0.5)
        ax[0].vlines(burnin, lnprob_min, lnprob_max, color=line[0].get_color(), linestyles="dashed",
                     alpha=0.5)
    for i in range(sampler.dim):
        ax[i + 1].set_title(l_param_name[i])
        vmin = sampler.chain[l_walker, :, i].min()
        vmax = sampler.chain[l_walker, :, i].max()
        for walker, burnin in zip(l_walker, l_burnin):
            line = ax[i + 1].plot(sampler.chain[walker, :, i], alpha=0.5)
            ax[i + 1].vlines(burnin, vmin, vmax, color=line[0].get_color(), linestyles="dashed",
                             alpha=0.5)
    ax[sampler.dim].set_xlabel("iteration")
    fig.tight_layout(**kwargs_tl)


def overplot_data_model_init(param, l_param_name, datasim_db, dataset_db, noisemod_db=None,
                             oversamp=10, plot_height=2, plot_width=8, **kwargs_tl):
    """param        np.array
       datasim_db   dataset_db in datasimulators
       dataset_db   dataset_db
       noisemod_db  dictionary giving the noise model instance for each dataset name
    """
    raise Warning("This function is depreceated and has been replaced by overplot_data_model")
    # Get the list of all datasets names and the number of datasets
    l_datasets = dataset_db.get_datasets()
    ndataset = len(l_datasets)

    # Create the figure and grid which will harbor the plots for each dataset
    fig = figure(figsize=(plot_width, ndataset * plot_height))
    gs = GridSpec(nrows=ndataset, ncols=1)

    # Create and fill the dictionary which for each noise_model_name return the dict of kwargs.
    dico_noisemod_allkwargs = dict()
    for dataset_name, noise_mod in noisemod_db.items():
        if noise_mod is None:
            continue
        dico_noisemod_allkwargs[noise_mod.category] = defaultdict(list)
        if noise_mod.has_GP:
            for dataset_name in noise_mod.l_dataset:
                dataset = dataset_db[dataset_name]
                kwargs = dataset.get_kwargs()
                for karg_type, kwarg_value in kwargs.items():
                    dico_noisemod_allkwargs[noise_mod.category][karg_type].append(kwarg_value)

    for i, dataset in enumerate(l_datasets):
        # Create the two Axes for the comparison data/model and the residuals and set the title.
        ax_data, ax_resi = add_twoaxeswithsharex(gs[i], gs_from_sps_kw={"height_ratios": (3, 1)})
        ax_data.set_title(dataset.dataset_name)

        # plot the data
        kwargs = dataset.get_kwargs()
        ax_data.errorbar(kwargs["t"], kwargs["data"], kwargs["data_err"], fmt=".", color="b")

        # plot the model and residuals
        tmin = kwargs["t"].min()
        tmax = kwargs["t"].max()
        nt = len(kwargs["t"])
        tsamp = (tmax - tmin) / (nt * oversamp)
        tmin_moins = tmin - oversamp * tsamp
        tmax_plus = tmax + oversamp * tsamp
        t = linspace(tmin_moins, tmax_plus, nt * oversamp)
        noise_model = noisemod_db[dataset.dataset_name]
        idx_par = []
        datasim_function = datasim_db[dataset.dataset_name]["whole"].function
        datasim_paramnames = datasim_db[dataset.dataset_name]["whole"].arg_list["param"]
        for par in datasim_paramnames:
            idx_par.append(l_param_name.index(par))
        datasim_t = datasim_function(param[idx_par], t)
        datasim_tdata = datasim_function(param[idx_par], kwargs["t"])
        ax_data.plot(t, datasim_t, "g-", label="model")
        ax_resi.errorbar(kwargs["t"], kwargs["data"] - datasim_tdata, kwargs["data_err"],
                         fmt=".", color="g")
        if noise_model.has_GP:
            gpsim_func = noise_model.gp_simulator
            datasim_GP_t = (datasim_t +
                            gpsim_func(param, t, **dico_noisemod_allkwargs[noise_model.category]))
            datasim_GP_tdata = (datasim_tdata +
                                gpsim_func(param, kwargs["t"],
                                           **dico_noisemod_allkwargs[noise_model.category]))
            ax_data.plot(t, datasim_GP_t, "r-", label="model+GP")
            ax_resi.errorbar(kwargs["t"], kwargs["data"] - datasim_GP_tdata, kwargs["data_err"],
                             fmt=".", color="r")
        ax_data.legend(loc='upper right', shadow=True)
        # Draw a line y=0 for the residuals
        xmin, xmax = ax_resi.get_xlim()
        ax_resi.hlines(y=0.0, xmin=xmin, xmax=xmax, linestyles="dashed", linewidth=1)
        ax_resi.set_xlim(xmin, xmax)
    fig.tight_layout(**kwargs_tl)


def overplot_data_model(param, l_param_name, datasim_db, dataset_db, noisemod_db=None, oversamp=10,
                        phasefold=False, phasefold_kwargs=None,
                        plot_height=2, plot_width=8, **kwargs_tl):
    """param        np.array
       datasim_db   dataset_db in datasimulators
       dataset_db   dataset_db
       noisemod_db  dictionary giving the noise model instance for each dataset name
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

    # Create and fill the dictionary which for each noise_model_name return the dict of kwargs.
    dico_noisemod_allkwargs = dict()
    for dataset_name, noise_mod in noisemod_db.items():
        if noise_mod is None:
            continue
        dico_noisemod_allkwargs[noise_mod.category] = defaultdict(list)
        if noise_mod.has_GP:
            for dataset_name in noise_mod.l_dataset:
                dataset = dataset_db[dataset_name]
                kwargs = dataset.get_kwargs()
                for karg_type, kwarg_value in kwargs.items():
                    dico_noisemod_allkwargs[noise_mod.category][karg_type].append(kwarg_value)

    for i, dataset in enumerate(l_datasets):
        datasim_db_docfunc = datasim_db[dataset.dataset_name]["whole"]
        noise_model = noisemod_db[dataset.dataset_name]
        noisemod_allkwargs = dico_noisemod_allkwargs[noise_model.category]
        kwargs = dataset.get_kwargs()
        t = kwargs["t"]
        nt = len(t)
        data = kwargs["data"]
        data_err = kwargs["data_err"]
        if phasefold:
            # Create the Axes for the comparison data/model and the residuals and set the title.
            # and plot the data
            (axes_data,
             axes_resi) = add_twoaxeswithsharex_perplanet(gs[i],
                                                          nplanet=len(phasefold_kwargs["planets"]),
                                                          gs_from_sps_kw={"height_ratios": (3, 1)})
            title_printed = False
            for planet_name, P, tc, ax_data, ax_resi in zip(phasefold_kwargs["planets"],
                                                            phasefold_kwargs["P"],
                                                            phasefold_kwargs["tc"],
                                                            axes_data, axes_resi):
                if not(title_printed):
                    ax_data.set_title(dataset.dataset_name)
                    title_printed = True
                # Plot the data
                errorbar_kwarg = {"color": "b", "fmt": "."}
                _, phases = plot_phase_folded_timeserie(t=t, data=data, P=P, tc=tc,
                                                        data_err=data_err, ax=ax_data,
                                                        errorbar_kwarg=errorbar_kwarg)

                # Plot the model
                phasemin = phases.min()
                phasemax = phases.max()
                tmin = tc + P * phasemin
                tmax = tc + P * phasemax
                plot_model(tmin, tmax, nt, datasim_db_docfunc, param, l_param_name,
                           oversamp=oversamp,
                           plot_phase=True, P=P, tc=tc,
                           noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                           ax=ax_data)
                # Plot the model and residuals
                plot_residuals(t, data, datasim_db_docfunc, param, l_param_name, data_err=data_err,
                               plot_phase=True, P=P, tc=tc,
                               noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                               ax=ax_resi)
        else:
            # Create the Axes for the comparison data/model and the residuals and set the title.
            # and plot the data
            ax_data, ax_resi = add_twoaxeswithsharex(gs[i],
                                                     gs_from_sps_kw={"height_ratios": (3, 1)})
            ax_data.set_title(dataset.dataset_name)

            # Plot the data
            ax_data.errorbar(t, data, data_err, fmt=".", color="b")

            # Plot the model
            tmin = t.min()
            tmax = t.max()
            plot_model(tmin, tmax, nt, datasim_db_docfunc, param, l_param_name, oversamp=oversamp,
                       plot_phase=False,
                       noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                       ax=ax_data)

            # Plot the residuals
            plot_residuals(t, data, datasim_db_docfunc, param, l_param_name, data_err=data_err,
                           plot_phase=False,
                           noise_model=noise_model, noisemod_allkwargs=noisemod_allkwargs,
                           ax=ax_resi)

        # Plot the legend
        ax_data.legend(loc='upper right', shadow=True)

    fig.tight_layout(**kwargs_tl)


def plot_model(tmin, tmax, nt, datasim_db_docfunc, param, l_param_name, oversamp=1,
               plot_phase=False, P=None, tc=None,
               noise_model=None, noisemod_allkwargs=None,
               ax=None):
    # Create the time sampling (tsamp) and the tmin and tmax for the model computation (tmin_moins,
    # tmax_plus), the model time vector (t)
    tsamp = (tmax - tmin) / (nt * oversamp)
    tmin_moins = tmin - oversamp * tsamp
    tmax_plus = tmax + oversamp * tsamp
    t = linspace(tmin_moins, tmax_plus, nt * oversamp)

    # Compute the model values for each time
    idx_par = []
    datasim_function = datasim_db_docfunc.function
    datasim_paramnames = datasim_db_docfunc.arg_list["param"]
    for par in datasim_paramnames:
        idx_par.append(l_param_name.index(par))
    model = datasim_function(param[idx_par], t)

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Plot the model
    errorbar_kwarg = {"label": "model", "color": "g", "fmt": "-"}
    if plot_phase:
        plot_phase_folded_timeserie(t, model, P, tc, ax=ax, errorbar_kwarg=errorbar_kwarg)
    else:
        ax.errorbar(t, model, **errorbar_kwarg)

    # Plot the model + GP
    if noise_model is not None:
        if noise_model.has_GP:
            gpsim_func = noise_model.gp_simulator
            model_wGP = model + gpsim_func(param, t, **noisemod_allkwargs)
            errorbar_kwarg = {"label": "model+GP", "color": "r", "fmt": "-"}
            if plot_phase:
                plot_phase_folded_timeserie(t, model_wGP, P, tc, ax=ax,
                                            errorbar_kwarg=errorbar_kwarg)
            else:
                ax.errorbar(t, model_wGP, **errorbar_kwarg)


def plot_residuals(t, data, datasim_db_docfunc, param, l_param_name, data_err=None,
                   plot_phase=False, P=None, tc=None,
                   noise_model=None, noisemod_allkwargs=None,
                   ax=None):

    # Compute the residuals values for each time
    idx_par = []
    datasim_function = datasim_db_docfunc.function
    datasim_paramnames = datasim_db_docfunc.arg_list["param"]
    for par in datasim_paramnames:
        idx_par.append(l_param_name.index(par))
    model = datasim_function(param[idx_par], t)
    residual = data - model

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Plot the residuals
    errorbar_kwarg = {"label": "model", "color": "g", "fmt": "."}
    if plot_phase:
        plot_phase_folded_timeserie(t, residual, P, tc, data_err=data_err, ax=ax,
                                    errorbar_kwarg=errorbar_kwarg)
    else:
        ax.errorbar(t, residual, data_err, **errorbar_kwarg)

    # Plot the model + GP
    if noise_model is not None:
        if noise_model.has_GP:
            gpsim_func = noise_model.gp_simulator
            model_wGP = model + gpsim_func(param, t, **noisemod_allkwargs)
            residual_wGP = data - model_wGP
            errorbar_kwarg = {"label": "model+GP", "color": "r", "fmt": "."}
            if plot_phase:
                plot_phase_folded_timeserie(t, residual_wGP, P, tc, ax=ax,
                                            errorbar_kwarg=errorbar_kwarg)
            else:
                ax.errorbar(t, residual_wGP, data_err, **errorbar_kwarg)

    # Draw a line y=0 for the residuals
    xmin, xmax = ax.get_xlim()
    ax.hlines(y=0.0, xmin=xmin, xmax=xmax, linestyles="dashed", linewidth=1)
    ax.set_xlim(xmin, xmax)


def plot_phase_folded_timeserie(t, data, P, tc, data_err=None, ax=None, errorbar_kwarg=None):
    """Plot a phase folded representation of a lc

    :param Dataset dataset: LC dataset
    :param float P: Period of the planet
    :param float tc: Time of inferior conjuction of the planet

    P and tc needs to have the same unit than the time in dataset.
    """
    # Obtain the phases with respect to some ephemerid P and tc
    phases = foldAt(t, P, T0=(tc + P / 2))

    # Sort with respect to phase
    # First, get the order of indices ...
    sortIndi = argsort(phases)
    # ... and, second, rearrange the arrays.
    phases = phases[sortIndi] - 0.5
    flux = data[sortIndi]
    if data_err is not None:
        flux_err = data_err[sortIndi]

    # Create a new figure and ax if needed
    ax = __get_default_ax(ax=ax)

    # Check the errorbar kwargs
    kw = dict() if errorbar_kwarg is None else errorbar_kwarg.copy()
    if "fmt" not in kw:
        kw["fmt"] = "-"
    if "color" not in kw:
        kw["color"] = "r"

    # Plot the phase folded data
    if data_err is not None:
        line = ax.errorbar(phases, flux, flux_err, **kw)
    else:
        line = ax.errorbar(phases, flux, **kw)
    return line, phases


def add_twoaxeswithsharex(subplotspec, gs_from_sps_kw=None):
    """Add two axes to a subplotspec (created with gridspec) for data and residual plot. """
    # Set the default values for GridSpecFromSubplotSpec
    kw = dict() if gs_from_sps_kw is None else gs_from_sps_kw.copy()
    if "hspace" not in kw:
        kw["hspace"] = 0.1
    if "height_ratios" not in kw:
        kw["height_ratios"] = (4, 1)

    # Create the two axes, share x axis and set the ticks and ticks label properties
    gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=subplotspec, **kw)
    ax0 = subplot(gs[0])
    ax1 = subplot(gs[1], sharex=ax0)
    ax0.tick_params(axis="both", which="both", direction="in", length=2, bottom="on", left="on",
                    top="on", right="on", reset=True, labelbottom="off")
    ax0.locator_params(axis="y", tight=True, nbins=3)
    ax1.tick_params(axis="both", which="both", direction="in", length=2, bottom="on", left="on",
                    top="on", right="on", reset=True)
    ax1.locator_params(axis="y", tight=True, nbins=3)

    # Return the two axes
    return ax0, ax1


def add_twoaxeswithsharex_perplanet(subplotspec, nplanet, gs_from_sps_kw=None):
    """Add two axes per planet to a subplotspec (created with gridspec) for data and residual plot.
    """
    # Create the nplanet axes
    gs = gridspec.GridSpecFromSubplotSpec(1, nplanet, subplot_spec=subplotspec)

    # Create the two axes for the data and the residuals for each planet
    axes_data = []
    axes_resi = []
    for gs_elem in gs:
        ax_data, ax_resi = add_twoaxeswithsharex(gs_elem, gs_from_sps_kw=gs_from_sps_kw)
        axes_data.append(ax_data)
        axes_resi.append(ax_resi)
    return axes_data, axes_resi


def apply_mask(x=None):
    '''
    Returns the outlier mask, an array of indices corresponding to the non-outliers.

    :param numpy.ndarray x: If specified, returns the masked version of :py:obj:`x` instead.
       Default :py:obj:`None`

    WORK IN PROGRESS
    '''

    if x is None:
        return np.delete(np.arange(len(self.time)), self.mask)
    else:
        return np.delete(x, self.mask, axis=0)


def acceptancefraction_selection(sampler, sig_fact=3., verbose=1):
    """Return selected walker based on the acceptance fraction.

    :param emcee.EnsembleSampler sampler:
    :param float sig_fact: acceptance fraction below mean - sig_fact * sigma will be rejected
    :param int verbose: if 1 speaks otherwise not
    """
    median_acceptance_frac = median(sampler.acceptance_fraction)
    mad_acceptance_frac = mad(sampler.acceptance_fraction)
    if verbose == 1:
        logger.info("Acceptance fraction of the walkers: {}\nmedian: {}, MAD:{}"
                    "".format(sampler.acceptance_fraction, median_acceptance_frac,
                              mad_acceptance_frac))
    l_selected_walker = where(sampler.acceptance_fraction > (median_acceptance_frac -
                                                             sig_fact * mad_acceptance_frac))[0]
    nb_rejected = sampler.chain.shape[0] - len(l_selected_walker)
    if verbose == 1:
        logger.info("Number of rejected walkers: {}/{}".format(nb_rejected, sampler.chain.shape[0]))
    return l_selected_walker, nb_rejected


def lnposterior_selection(sampler, sig_fact=3., verbose=1):
    """Return selected walker based on the acceptance fraction.

    :param emcee.EnsembleSampler sampler:
    :param float sig_fact: acceptance fraction below mean - sig_fact * sigma will be rejected
    :param int verbose: if 1 speaks otherwise not
    """
    median_lnposterior = median(sampler.lnprobability)
    mad_lnposterior = mad(sampler.lnprobability)
    walkers_median_lnposterior = median(sampler.lnprobability, axis=1)
    if verbose == 1:
        logger.info("lnposterior of the walkers: {}\nmedian: {}, MAD:{}"
                    "".format(walkers_median_lnposterior, median_lnposterior, mad_lnposterior))
    l_selected_walker = where(walkers_median_lnposterior >
                              (median_lnposterior - (sig_fact * mad_lnposterior)))[0]
    nb_rejected = sampler.chain.shape[0] - len(l_selected_walker)
    if verbose == 1:
        logger.info("Number of rejected walkers: {}/{}".format(nb_rejected, sampler.chain.shape[0]))
    return l_selected_walker, nb_rejected


def get_fitted_values(sampler, method="MAP", l_param_name=None, l_walker=None, l_burnin=None,
                      verbose=1):
    """Return the fitted values from the sampler.

    :param emcee.EnsembleSampler sampler:
    :param string method: method used to extract the fitted values ["MAP", "median"]
    :param int_iteratable l_walkers: list of valid walkers
    :param int burnin: index of the first iteration to consider.
    :param int verbose: if 1 speaks otherwise not
    """
    ndim = sampler.dim
    if method == "median":
        res = median(get_clean_flatchain(sampler, l_walker=l_walker, l_burnin=l_burnin), axis=0)
    elif method == "MAP":
        if (l_walker is not None) or (l_burnin is not None):
            logger.warning("With method MAP the l_walker and l_burnin arguments are ignored.")
        walker, it = unravel_index(argmax(sampler.lnprobability), dims=sampler.lnprobability.shape)
        res = array([sampler.chain[walker, it, dim] for dim in range(ndim)])
    else:
        raise ValueError("Method {} is not recognised".format(method))
    if verbose == 1:
        l_param_names = __get_default_l_param_name(l_param_name, ndim)
        text = "\n"
        for i, param_name in enumerate(l_param_names):
            text += "{} = {}\n".format(param_name, res[i])
        logger.info(text)
    return res


def get_clean_flatchain(sampler, l_walker=None, l_burnin=None):
    """Return a flatchain with only the selected walkers and iteration after the burnin.

    :param emcee.EnsembleSampler sampler:
    :param int_iteratable l_walkers: list of valid walkers
    :param int_iteratable l_burnin: list of burnin iterations for each valid walker
    """
    if (l_walker is None) and (l_burnin is None):
        return sampler.flatchain
    else:
        l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=sampler.chain.shape[0])
    if l_burnin is None:
        s = sampler.chain[l_walker, ...].shape
        return sampler.chain[l_walker, ...].reshape(s[0] * s[1], s[2])
    else:
        l_burnin = __get_default_l_burnin(l_burnin=l_burnin, nwalker=sampler.chain.shape[0])
    ndim = sampler.dim
    res = []
    for dim in range(ndim):
        res.append([])
        for walker, burnin in zip(l_walker, l_burnin):
            res[dim].extend(sampler.chain[walker, burnin:, dim])
    return array(res).transpose()


def geweke_multi(sampler, first=0.1, last=0.5, intervals=20, l_walker=None):
    """Adapted the geweke test for multiple wlaker exploration.

    :param emcee.EnsembleSampler sampler:
    :param float last: first portion of the chain to be used in the Geweke diagnostic.
        Default to 0.1 (i.e. first 10 % of the chain)
    :param float last: last portion of the chain to be used in the Geweke diagnostic.
        Default to 0.5 (i.e. last 50 % of the chain)
    :param int intervals: Number of sub-chains to analyze. Defaults to 20.
    :param int_iteratable l_walker: list of valid walkers
    """
    # Get the list of valid walkers (l_walker), the number of parameters (ndim) and the number of
    # steps for each walker (nsteps)
    l_walker = __get_default_l_walker(l_walker=l_walker, nwalker=sampler.chain.shape[0])
    nwalker = len(l_walker)
    ndim = sampler.dim
    nsteps = sampler.chain.shape[1]

    # Compute the start step of the last part of the chain and compute median and MAD of the last
    # part of the chain for each parameter
    last_start_step = int(nsteps * last)
    l_med_last = [median(sampler.chain[l_walker, last_start_step:, dim]) for dim in range(ndim)]
    print("l_med_last: {}".format(l_med_last))
    l_mad_last = [mad(sampler.chain[l_walker, last_start_step:, dim]) for dim in range(ndim)]
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
                med_first = median(sampler.chain[walker, first_start:(first_start + first_length),
                                                 dim])
                mad_first = mad(sampler.chain[walker, first_start:(first_start + first_length),
                                              dim])
                zscores[i, j, dim] = (med_first - med_last) / (sqrt(mad_first**2 + mad_last**2))
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
