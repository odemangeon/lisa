from matplotlib.pyplot import subplots
from numpy import sign, log10, logspace, isfinite, where, median, delete
from scipy.stats import median_abs_deviation as mad


def hist_lnprob(lnprobability, n_bins=None, sigma_clip=5, ax=None, **hist_kwargs):
    """Function to produce the histogram of the lnposterior chains

    It can make the histogram of the log10(lnprobability) when the value are too spread.
    It also can perform sigma clipping of too low values to avoid to spread histogram that can crash python.
    Usually the problem comes from values that are too low, before the chain has really converged and
    not values that are too high.

    Arguments
    ---------
    lnprobability : array_of_float
        lnprobability values for the histogram
    n_bins : None/int
        Number of bins to use if it cannot be automatically chosen
    ax : AxesSubplot/None
        AxesSubplot instance to use to plot the histogram
    hist_kwargs : dict
        Keyword arguments to pass to the hist function
    sigma_clip : None/positive integer
        Sigma clipping factor

    Returns
    -------
    ax : AxesSubplot
        AxesSubplot instance used to plot the histogram
    did_log10 : bool
        True if the log10 of lnprobability has been used for the plot
    nb_point_sigma_clip : Int
        Number of point which have been sigma clipped
    """
    if hist_kwargs is None:
        hist_kwargs = {}
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
    # Perform the sigma clipping
    if sigma_clip is not None and (sigma_clip > 0):
        mask = lnprobability_plot < (median(lnprobability_plot) - sigma_clip * mad(lnprobability_plot))
        nb_point_sigma_clip = sum(mask)
        lnprobability_plot = delete(lnprobability_plot, where(mask)[0])
    else:
        nb_point_sigma_clip = 0
    if log_scale:
        if sign(min_log10) > 0:
            did_log10 = False
            ax.hist(lnprobability_plot, bins=bins, **hist_kwargs)
            ax.set_xscale("log")
            ax.set_xlabel("lnprobability")
        else:
            did_log10 = True
            ax.hist(sign(lnprobability_plot) * log10(abs(lnprobability_plot)), bins=sign(bins) * log10(abs(bins)), **hist_kwargs)
            ax.set_xlabel("log10(lnprobability)")
    else:
        did_log10 = False
        ax.hist(lnprobability_plot, bins=bins, **hist_kwargs)
        ax.set_xlabel("lnprobability")
    return ax, did_log10, nb_point_sigma_clip
