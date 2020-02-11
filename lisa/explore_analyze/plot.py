from matplotlib.pyplot import subplots
from numpy import sign, log10, logspace, isfinite


def hist_lnprob(lnprobability, n_bins=None, ax=None):
    """
    :param array_of_float lnprobability: lnprobability values for the histogram
    :param None/int n_bins: Number of bins to use if it cannot be automatically chosen
    :param AxesSubplot/None ax: AxesSubplot instance to use to plot the histogram
    :return AxesSubplot ax: AxesSubplot instance used to plot the histogram
    :return bool did_log10: True if the log10 of lnprobability has been used for the plot
    """
    if ax is None:
        fig, ax = subplots()
    lnprobability_plot = lnprobability.copy()
    # Remove non finite values that would make the plot crash.
    lnprobability_plot = lnprobability_plot[isfinite(lnprobability_plot)]
    min_log10 = sign(lnprobability_plot.min()) * log10(abs(lnprobability_plot.min()))
    max_log10 = sign(lnprobability_plot.max()) * log10(abs(lnprobability_plot.max()))
    if sign(max_log10) * sign(min_log10) < 0:
        log_scale = False
        if (max_log10 - min_log10) > 1:
            bins = 'auto'
        else:
            bins = None
    elif (max_log10 - min_log10) > 1.5:
        log_scale = True
        bins = None
    else:
        log_scale = False
        bins = 'auto'
    if bins is None:
        if log_scale:
            if sign(min_log10) > 0:
                bins = logspace(min_log10, max_log10, n_bins)
            else:
                bins = - logspace(abs(max_log10), abs(min_log10), n_bins)[::-1]
    if log_scale:
        if sign(min_log10) > 0:
            did_log10 = False
            ax.hist(lnprobability_plot, bins=bins)
            ax.set_xscale("log")
            ax.set_xlabel("lnprobability_plot")
        else:
            did_log10 = True
            ax.hist(sign(lnprobability_plot) * log10(abs(lnprobability_plot)), bins=sign(bins) * log10(abs(bins)))
            ax.set_xlabel("log10(lnprobability_plot)")
    else:
        did_log10 = False
        ax.hist(lnprobability_plot, bins=bins)
        ax.set_xlabel("lnprobability_plot")
    return ax, did_log10
