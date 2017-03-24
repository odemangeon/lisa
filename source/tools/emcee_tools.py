#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
emcee tools module.

The objective of this module is to provide a toolbox for the exploitation and visualisation of emcee
results.
"""
from logging import getLogger
from matplotlib.pyplot import subplots  # , figure, plot, show
from numpy import linspace
from sys import stdout

## Logger Object
logger = getLogger()


def explore(sampler, p0, nsteps, width=50, save_to_file=None):
    f = open(save_to_file, "w")
    f.close()
    for i, result in enumerate(sampler.sample(p0, iterations=nsteps, storechain=False)):
        position = result[0]
        f = open(save_to_file, "a")
        for k in range(position.shape[0]):
            f.write("{0:4d} {1:s}\n".format(k, " ".join(position[k])))
        f.close()
        n = int((width + 1) * float(i) / nsteps)
        stdout.write("\r[{0}{1}]".format('#' * n, ' ' * (width - n)))
    stdout.write("\n")


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


def overplot_data_model(param, l_param_names, datasim_db, dataset_db, oversamp=10,
                        plot_height=2, plot_width=8, **kwargs_tl):
    """param        np.array
       datasim_db   dataset_db in datasimulators
       dataset_db   dataset_db
    """
    l_datasets = dataset_db.get_datasets()
    ndataset = len(l_datasets)
    fig, ax = subplots(nrows=ndataset, figsize=(plot_width, ndataset * plot_height))
    for i, dataset in enumerate(l_datasets):
        ax[i].set_title(l_datasets[i])
        kwargs = dataset.get_kwargs()
        ax[i].errorbar(kwargs["t"], kwargs["data"], kwargs["data_err"], fmt=".", color="b")
        tmin = kwargs["t"].min()
        tmax = kwargs["t"].max()
        nt = len(kwargs["t"])
        tsamp = (tmax - tmin) / (nt * oversamp)
        tmin_moins = tmin - oversamp * tsamp
        tmax_plus = tmax + oversamp * tsamp
        t = linspace(tmin_moins, tmax_plus, nt * oversamp)
        idx_par = []
        datasim_function = datasim_db[dataset.dataset_name]["whole"].function
        datasim_paramnames = datasim_db[dataset.dataset_name]["whole"].arg_list["param"]
        for par in datasim_paramnames:
            idx_par.append(l_param_names.index(par))
        ax[i].plot(t, datasim_function(param[idx_par], t), "r-")
        ax[i].set_title(dataset.dataset_name)
    fig.tight_layout(**kwargs_tl)
