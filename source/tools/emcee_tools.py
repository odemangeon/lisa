#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
emcee tools module.

The objective of this module is to provide a toolbox for the exploitation and visualisation of emcee
results.
"""
from logging import getLogger
from matplotlib.pyplot import subplots, subplot, figure, legend  # , figure, plot, show
from numpy import linspace
from sys import stdout
import matplotlib.gridspec as gridspec
from matplotlib.gridspec import GridSpec
from copy import deepcopy
from collections import defaultdict
from tqdm import tqdm


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


def plot_chains(sampler, l_param_names, flat=False,
                plot_height=2, plot_width=8, **kwargs_tl):
    nwalk = sampler.chain.shape[0]
    fig, ax = subplots(nrows=sampler.dim + 1, sharex=True, squeeze=True,
                       figsize=(plot_width, nwalk * plot_height))
    for k in range(nwalk):
        ax[0].set_title("lnpost")
        ax[0].plot(sampler.lnprobability[k, :], alpha=0.5)
    for i in range(sampler.dim):
        ax[i + 1].set_title(l_param_names[i])
        for k in range(nwalk):
            ax[i + 1].plot(sampler.chain[k, :, i], alpha=0.5)
    ax[sampler.dim].set_xlabel("iteration")
    fig.tight_layout(**kwargs_tl)


def overplot_data_model(param, l_param_names, datasim_db, dataset_db, noisemod_db=None, oversamp=10,
                        plot_height=2, plot_width=8, **kwargs_tl):
    """param        np.array
       datasim_db   dataset_db in datasimulators
       dataset_db   dataset_db
       noisemod_db  dictionary giving the noise model instance for each dataset name
    """
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
            idx_par.append(l_param_names.index(par))
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
