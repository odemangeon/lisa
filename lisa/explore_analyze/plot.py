from matplotlib.pyplot import subplots
from numpy import sign, log10, logspace


def hist_lnprob(lnprobability, n_bins=None, ax=None):
    """
    """
    if ax is None:
        fig, ax = subplots()
    min_log10 = sign(lnprobability.min()) * log10(abs(lnprobability.min()))
    max_log10 = sign(lnprobability.max()) * log10(abs(lnprobability.max()))
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
            ax.hist(lnprobability, bins=bins)
            ax.set_xscale("log")
            ax.set_xlabel("lnprobability")
        else:
            ax.hist(sign(lnprobability) * log10(abs(lnprobability)), bins=sign(bins) * log10(abs(bins)))
            ax.set_xlabel("log10(lnprobability)")
    else:
        ax.hist(lnprobability, bins=bins)
        ax.set_xlabel("lnprobability")
    return ax
