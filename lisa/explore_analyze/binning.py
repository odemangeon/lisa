from __future__ import annotations

from numpy import arange, floating, nan, power, sqrt, where, zeros
from numpy.typing import NDArray
from scipy.stats import binned_statistic


def compute_binning(
    times_dataset: NDArray[floating],
    values: NDArray[floating],
    errors: NDArray[floating],
    errors_jitter: NDArray[floating] | None,
    exptime: int | float,
    method: str = "mean",
):
    """Compute the binned data."""
    # Compute the evenly space binned data time vector
    x_min_data, x_max_data = (min(times_dataset), max(times_dataset))
    bins = arange(x_min_data, x_max_data + exptime, exptime)
    midbins = bins[:-1] + exptime / 2
    nbins = len(bins) - 1
    # Compute the binned values
    (bindata, binedges, binnb) = binned_statistic(
        times_dataset, values, statistic=method, bins=bins, range=(x_min_data, x_max_data)
    )
    # Compute the err on the binned values
    binstd = zeros(nbins)
    if errors_jitter is not None:
        binstd_jitter = zeros(nbins)
    else:
        binstd_jitter = None
    bincount = zeros(nbins)
    for i_bin in range(nbins):
        bincount[i_bin] = len(where(binnb == (i_bin + 1))[0])
        if bincount[i_bin] > 0.0:
            binstd[i_bin] = sqrt(
                sum(power(errors[binnb == (i_bin + 1)], 2.0)) / bincount[i_bin] ** 2
            )
            if errors_jitter is not None:
                binstd_jitter[i_bin] = sqrt(
                    sum(power(errors_jitter[binnb == (i_bin + 1)], 2.0)) / bincount[i_bin] ** 2
                )
        else:
            binstd[i_bin] = nan
            if errors_jitter is not None:
                binstd_jitter[i_bin] = nan
    return bins, binedges, bindata, binstd, binstd_jitter


def bin_data_and_resi(
    times_dataset: NDArray,
    data: NDArray,
    data_err: NDArray,
    data_err_jitter: NDArray,
    residuals: NDArray,
    exptime: float | int,
    method: str,
):
    (bins, _, bindata, bindata_std, bindata_std_jitter) = compute_binning(
        times_dataset=times_dataset,
        values=data,
        errors=data_err,
        errors_jitter=data_err_jitter,
        exptime=exptime,
        method=method,
    )
    (_, _, binresi, _, _) = compute_binning(
        times_dataset=times_dataset,
        values=residuals,
        errors=data_err,
        errors_jitter=data_err_jitter,
        exptime=exptime,
        method=method,
    )
    midbins = bins[:-1] + exptime / 2
    return midbins, bindata, bindata_std, bindata_std_jitter, binresi
