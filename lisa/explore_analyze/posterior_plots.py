import arviz as az
import matplotlib.pyplot as pl

from matplotlib.axes._axes import Axes
from matplotlib import ticker


def posterior_plot(samples, values_wkwargs, intervals_wkwargs, xlabel:str|None=None, show_ylabel:bool=True, show_legend:bool=False, ax:Axes|None=None):
    if ax is None:
        fig, ax = pl.subplots(nrows=1, ncols=1)
    az.plot_dist(samples, kind='hist', color="k", hist_kwargs={'bins': "sturges", 'density': True, 'histtype': 'step'},
                 ax=ax
                 )
    ylims = ax.get_ylim()
    for val_i, kwargs in values_wkwargs:
        kwargs = kwargs if kwargs is not None else {}
        ax.vlines(x=val_i, ymin=ylims[0], ymax=ylims[1], **kwargs)
    for interval_i, kwargs in intervals_wkwargs:
        kwargs = kwargs if kwargs is not None else {}
        ax.axvspan(*interval_i, **kwargs)
    ax.set_ylim(ylims)

    yticks = ticker.MaxNLocator(5)
    ax.xaxis.set_major_locator(yticks)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if show_ylabel:
        ax.set_ylabel("Posterior PDF")
    if show_legend:
        ax.legend()
    return ax