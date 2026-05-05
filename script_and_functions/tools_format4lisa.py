from __future__ import annotations

import glob
import math
import os
import pprint
import re
from collections.abc import Callable, Iterable
from copy import copy
from typing import Any, Literal, NotRequired, Required, TypedDict

import astropy.stats
import astropy.units as uu
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import ascii as astro_ascii
from astropy.io import fits
from astropy.stats import sigma_clip
from astropy.table import Table
from loguru import logger
from numpy.typing import NDArray
from sklearn.neighbors import KernelDensity
from wotan import flatten

FLAG_POSITIONS = {
    "SAA": 0,
    "TEMP": 1,
    "EARTH": 2,
    "MOON": 3,
    "SUN": 4,
    "COSMICS": 5,
    "POINTING_JITTER": 6,
}


def read_flag(flag_number: int, which_flag: str) -> int:
    """
    Read a specific flag from the flag number

    Arguments:
        flag_number: int
        which_flag: string with the flag to be read
    """
    flag_value = (flag_number // 10 ** FLAG_POSITIONS[which_flag]) % 10
    return flag_value


def read_flag_array(
    flag_array: NDArray[np.long], which_flag: str | None, index: int | None = None
) -> NDArray[int] | int:
    """
    Read the flag array from the event_flagging product

    Arguments:
        flag_array:
        which_flag: string with the flag to be read
        index: index of the exposure for which you want the specified flag to be read (if None, read all indexes)
    """
    if which_flag is None:
        if index is None:
            return flag_array
        else:
            return flag_array[index]
    else:
        if index is None:
            return np.array([read_flag(flag_number, which_flag) for flag_number in flag_array])
        else:
            return read_flag(flag_array[index], which_flag)


def look_for_available_visits(data_folder: str):
    visit_folders = {}
    p_id_visit = re.compile(r"_TG[\d]+_")
    p_version_visit = re.compile(r"_V[\d]+")
    p_program_visit = re.compile(r"PR[\d]+_")
    for folder_path in glob.glob(data_folder):
        #     print(folder_path)
        search_id_visit = p_id_visit.search(folder_path)
        search_version_visit = p_version_visit.search(folder_path)
        search_program_visit = p_program_visit.search(folder_path)
        if search_id_visit is not None:
            id_visit = int(search_id_visit.group()[3:-1])
            version = int(search_version_visit.group()[2:])
            program = int(search_program_visit.group()[2:-1])
            if program not in visit_folders:
                visit_folders[program] = {}
            if id_visit not in visit_folders[program]:
                visit_folders[program][id_visit] = {}
            visit_folders[program][id_visit][version] = folder_path
    logger.info(f"Found {len(visit_folders)} programs")
    for program in visit_folders:
        logger.info(f"{program}: Found {len(visit_folders[program])} visits:")
        for id_visit in visit_folders[program]:
            logger.info(
                f"In program {program}, visit {id_visit}, Found {len(visit_folders[program][id_visit])} versions found:\n{pprint.pformat(visit_folders[program][id_visit])}"
            )
    return visit_folders


p_aperture = re.compile(r"_Lightcurve-[A-Z\d]+_")  # "_Lightcurve-[a-z]+_V"
p_pipversion = re.compile(r"_V[\d]+.fits")
p_filekey = re.compile(r"CH_PR[\d]{6,6}_TG[\d]{6,6}")


def get_LC_file(
    visit_folder_path: str,
    aperture: str,
    version: int | None = None,
    file_key: str | None = None,
) -> tuple[str, str, int]:
    path_LC_file = None
    version_found = None
    file_key_found = None
    for file_path in glob.iglob(os.path.join(visit_folder_path, "*Lightcurve*.fits")):
        basename = os.path.basename(file_path)
        search_res_aperture = p_aperture.search(basename)
        if search_res_aperture is None or aperture != search_res_aperture.group()[12:-1]:
            continue

        search_res_version = p_pipversion.search(basename)
        if search_res_version is None:
            continue
        version_current = int(search_res_version.group()[2:-5])
        if version is not None and version != version_current:
            continue

        search_res_filekey = p_filekey.match(basename)
        if search_res_filekey is None:
            continue
        file_key_current = search_res_filekey.group()
        if file_key is not None and file_key != file_key_current:
            continue

        path_LC_file = file_path
        version_found = version_current
        file_key_found = file_key_current
        logger.debug(
            f"Found file for aperture {aperture} and version {version_found}: Filekey={file_key_found}, path={file_path}"
        )
        break
    if path_LC_file is None or version_found is None or file_key_found is None:
        version_msg = f"version {version}" if version is not None else "any version"
        if file_key is None:
            err_msg = f"LC File for aperture {aperture} and {version_msg} not found !"
        else:
            err_msg = f"LC File for aperture {aperture}, {version_msg} and file key {file_key} not found !"
        raise ValueError(err_msg)
    return path_LC_file, file_key_found, version_found


DataLvL = Literal["RAW", "CAL", "COR"]


def get_SubArray_file(
    visit_folder_path: str,
    lvl: DataLvL = "RAW",
    version: int | None = None,
    file_key: str | None = None,
) -> tuple[str, str, int]:
    path_SubArray_file = None
    version_found = None
    file_key_found = None
    for file_path in glob.iglob(os.path.join(visit_folder_path, f"*SCI_{lvl}_SubArray*.fits")):
        basename = os.path.basename(file_path)
        search_res_version = p_pipversion.search(basename)
        if search_res_version is None:
            continue
        version_current = int(search_res_version.group()[2:-5])
        if version is not None and version != version_current:
            continue

        search_res_filekey = p_filekey.match(basename)
        if search_res_filekey is None:
            continue
        file_key_current = search_res_filekey.group()
        if file_key is not None and file_key != file_key_current:
            continue

        path_SubArray_file = file_path
        version_found = version_current
        file_key_found = file_key_current
        logger.debug(
            f"Found {lvl} SubArray file for version {version_found}: Filekey={file_key_found}, path={file_path}"
        )
        break
    if path_SubArray_file is None or version_found is None or file_key_found is None:
        version_msg = f"version {version}" if version is not None else "any version"
        if file_key is None:
            err_msg = f"{lvl} SubArray File for {version_msg} not found !"
        else:
            err_msg = f"{lvl} SubArray File for {version_msg} and file key {file_key} not found !"
        raise ValueError(err_msg)
    return path_SubArray_file, file_key_found, version_found


def load_LC_file(path_LC_file: str) -> tuple[Table, uu.Quantity]:
    with fits.open(path_LC_file) as hdul:
        table_LC = Table.read(hdul["SCI_COR_Lightcurve"])
        texptime = hdul["SCI_COR_Lightcurve"].header["TEXPTIME"] * uu.s
    return table_LC, texptime


def load_metada(path_SubArray_file: str, lvl: DataLvL = "RAW") -> Table:
    with fits.open(path_SubArray_file) as hdul:
        table_metadata = Table.read(hdul[f"SCI_{lvl}_ImageMetadata"])
    return table_metadata


CorrelationMethod = Literal["pearson", "spearman", "kendall"]


def compute_detrending_correlations(
    table_LC: Table,
    table_metada: Table,
    vector_names: Iterable[str] = [
        "FLUX",
        "ROLL_ANGLE",
        "CONTA_LC",
        "CENTROID_X",
        "CENTROID_Y",
        "BACKGROUND",
        "SMEARING_LC",
        "thermFront_2",
    ],
    method: CorrelationMethod = "spearman",
    drop_nan: bool = True,
) -> pd.DataFrame:
    """
    Compute the correlation matrix between flux and detrending vectors.

    Parameters
    ----------
    flux : np.ndarray
        Flux time series.
    detrending_vectors : dict[str, np.ndarray]
        Dictionary containing detrending vectors. Expected keys may include
        BKG, SMEARING, CONTAMINATION, THERMFRONT2, CENTROIDX, CENTROIDY, ROLL.
    method : {"pearson", "spearman", "kendall"}, optional
        Correlation method passed to pandas.DataFrame.corr.
    drop_nan : bool, optional
        If True, rows with NaNs in any column are removed before computing
        correlations.

    Returns
    -------
    pd.DataFrame
        Correlation matrix.
    """

    data = {}
    for name in vector_names:
        if name in table_LC.columns:
            data[name] = table_LC[name]
        elif name in table_metada.columns:
            data[name] = table_metada[name]
        else:
            logger.warning(f"Columns {name} is not found in either the LC or the metadata columns")

    lengths = {name: len(vector) for name, vector in data.items()}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"All input vectors must have the same length. Got {lengths}")

    df = pd.DataFrame(data)

    if drop_nan:
        df = df.dropna(axis=0, how="any")

    if df.empty:
        raise ValueError("No valid data points remain after NaN filtering.")

    return df.corr(method=method)


def plot_correlation_matrix(
    corr: pd.DataFrame,
    title: str = "Flux and detrending-vector correlations",
    figsize: tuple[float, float] = (8.0, 6.5),
    annotate: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot a correlation matrix as a heatmap.

    Parameters
    ----------
    corr : pd.DataFrame
        Correlation matrix.
    title : str, optional
        Plot title.
    figsize : tuple[float, float], optional
        Figure size.
    annotate : bool, optional
        If True, write correlation values inside the cells.

    Returns
    -------
    tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes.
    """
    fig, ax = plt.subplots(figsize=figsize)

    image = ax.imshow(corr.values, vmin=-1.0, vmax=1.0)

    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.index)

    ax.set_title(title)

    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Correlation coefficient")

    if annotate:
        for row_idx in range(corr.shape[0]):
            for col_idx in range(corr.shape[1]):
                value = corr.iloc[row_idx, col_idx]
                ax.text(
                    col_idx,
                    row_idx,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                )

    fig.tight_layout()
    return fig, ax


def extract_corr(corr: pd.DataFrame, vector_name: str) -> pd.Series:
    """
    Extract correlations between a given vector and all others.

    Parameters
    ----------
    corr : pd.DataFrame
        Correlation matrix containing a FLUX row/column.
    vector_name: str
        Name of the vector you want to extract

    Returns
    -------
    pd.Series
        Correlations with FLUX, sorted by absolute correlation strength.
    """
    if vector_name not in corr.index:
        raise KeyError(f"Correlation matrix does not contain a '{vector_name}' entry.")

    corr_vector = corr.loc[vector_name].drop(labels=vector_name)
    return corr_vector.reindex(corr_vector.abs().sort_values(ascending=False).index)


def plot_flux_vs_vectors(
    table_LC: Table,
    table_metada: Table,
    vector_names: Iterable[str],
    max_cols: int = 3,
    figsize: tuple[float, float] = (8.0, 8.0),
    alpha: float = 0.5,
    s: float = 10.0,
    show_trend: bool = False,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Create scatter plots of FLUX versus each detrending vector.

    Parameters
    ----------
    flux : np.ndarray
        Flux time series.
    detrending_vectors : dict[str, np.ndarray]
        Dictionary of detrending vectors.
    max_cols : int
        Maximum number of subplot columns.
    figsize : tuple
        Figure size.
    alpha : float
        Marker transparency.
    s : float
        Marker size.
    show_trend : bool
        If True, overlay a linear trend line.

    Returns
    -------
    fig, axes
    """
    n = len(vector_names)

    ncols = min(max_cols, n)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)

    for i, name in enumerate(vector_names):
        row, col = divmod(i, ncols)
        ax = axes[row, col]

        if name in table_LC.columns:
            x = table_LC[name]
        elif name in table_metada.columns:
            x = table_metada[name]
        else:
            logger.warning(f"Columns {name} is not found in either the LC or the metadata columns")
            continue
        y = table_LC["FLUX"]

        ax.scatter(x, y, alpha=alpha, s=s)

        if show_trend:
            mask = np.isfinite(x) & np.isfinite(y)
            if np.sum(mask) > 2:
                coeffs = np.polyfit(x[mask], y[mask], deg=1)
                x_line = np.linspace(np.nanmin(x), np.nanmax(x), 100)
                y_line = np.polyval(coeffs, x_line)
                ax.plot(x_line, y_line)

        ax.set_xlabel(name)
        ax.set_ylabel("FLUX")
        ax.set_title(f"FLUX vs {name}")

    # Hide unused axes
    for j in range(i + 1, nrows * ncols):
        row, col = divmod(j, ncols)
        axes[row, col].axis("off")

    fig.tight_layout()
    return fig, axes


def plot_roll_vs_vectors(
    table_LC: Table,
    table_metada: Table,
    vector_names: Iterable[str],
    max_cols: int = 3,
    figsize: tuple[float, float] = (12.0, 8.0),
    alpha: float = 0.5,
    s: float = 10.0,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Scatter plots of ROLL versus detrending vectors.
    """
    n = len(vector_names)

    ncols = min(max_cols, n)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)

    for i, name in enumerate(vector_names):
        row, col = divmod(i, ncols)
        ax = axes[row, col]

        if name in table_LC.columns:
            x = table_LC[name]
        elif name in table_metada.columns:
            x = table_metada[name]
        else:
            logger.warning(f"Columns {name} is not found in either the LC or the metadata columns")
            continue
        y = table_LC["ROLL_ANGLE"]

        ax.scatter(x, y, alpha=alpha, s=s)

        ax.set_xlabel(name)
        ax.set_ylabel("ROLL")
        ax.set_title(f"ROLL vs {name}")

    # Hide unused axes
    for j in range(i + 1, nrows * ncols):
        row, col = divmod(j, ncols)
        axes[row, col].axis("off")

    fig.tight_layout()
    return fig, axes


def compute_visit_duration_efficiency(
    time_vector: NDArray[np.floating], time_unit: uu.Unit, texptime: uu.Quantity
) -> tuple(uu.Quantity, float):
    # Compute the visit efficiency
    visit_duration = (max(time_vector) - min(time_vector)) * time_unit
    # print(f"visit duration = {visit_duration} = {visit_duration.to(uu.h)}")
    effective_obs_time = len(time_vector) * texptime
    # print(
    #     f"effective amount of observing time = {effective_obs_time.to(uu.day)} = {effective_obs_time.to(uu.h)}"
    # )
    efficiency_woutliers = (effective_obs_time / visit_duration).decompose()
    # print(f"Efficiency = {efficiency_woutliers * 100} %")
    return visit_duration, efficiency_woutliers


# def make_visit_overview():


def_kwargs_sigma_clip = {"maxiters": 10, "return_bounds": True, "masked": True}


def detect_outliers(
    table_LC,
    table_metadata,
    detect_outliers_params,
    plot=False,
    show_plot=True,
    pre_mask=None,
    save_plot_file_name=None,
):
    """
    Detect outliers in light curve data based on various methods.

    Parameters:
    - table_LC: Astropy table with light curve data
    - table_metadata: Astropy table with metadata
    - detect_outliers_params: Dict with outlier detection parameters
    - FLAG_POSITIONS: Dict for flag positions
    - plot: Bool, whether to generate plots
    - kwargs_sigma_clip: Dict, kwargs for sigma_clip
    - save_plot_file_name: Str, path to save plot if plotting

    Returns:
    - masks: Dict of masks for each detection method
    - fig: Matplotlib figure if plot=True, else None
    """
    masks = {}
    if pre_mask is None:
        base_mask = np.zeros_like(np.asarray(table_LC["BJD_TIME"]), dtype=bool)
    else:
        base_mask = np.asarray(pre_mask, dtype=bool)

    if plot:
        fig, axes = plt.subplots(
            nrows=len(detect_outliers_params) + 2,
            figsize=(6, 3 * len(detect_outliers_params)),
            sharex=True,
            squeeze=False,
            constrained_layout=True,
        )
        fig.suptitle("Outlier detection")
        axes[0, 0].plot(
            table_LC["BJD_TIME"],
            (table_LC["FLUX"] / np.median(table_LC["FLUX"]) - 1) * 1e6,
            ".",
        )
        axes[0, 0].set_ylabel("flux [ppm]")
    else:
        fig = None

    for idx, (det_name, dico) in enumerate(detect_outliers_params.items()):
        column = dico["col"]
        empty_mask = np.zeros_like(np.asarray(table_LC["BJD_TIME"]), dtype=bool)
        pre_mask = copy(base_mask)
        if column in FLAG_POSITIONS.keys():
            vector_col = read_flag_array(table_LC["EVENT"], which_flag=column)
            unit = "flag"
            if dico["method"] == ">=":
                mask = np.logical_and(vector_col >= dico["threshold"], ~pre_mask)
                str_details = f"equal to {dico['threshold']} or higher."
            elif dico["method"] == ">":
                mask = np.logical_and(vector_col > dico["threshold"], ~pre_mask)
                str_details = f"higher than {dico['threshold']}."
            else:
                raise ValueError(
                    f"method {dico['method']} not implemented for flag columns, only '>=' and '>' are implemented."
                )
        else:
            if column in table_LC.columns:
                vector_col = table_LC[column]
                unit = table_LC[column].unit
            elif column in table_metadata.columns:
                vector_col = table_metadata[column]
                unit = table_metadata.columns[column].unit
            else:
                logger.warning(
                    f"Columns {column} is not found in either the LC or the metadata columns"
                )
                continue

            for outlier_detect_method in dico.get("pre mask", []):
                pre_mask = np.logical_or(pre_mask, masks[outlier_detect_method])
            if dico["method"] == "sigma clip":
                if dico.get("kwargs_sigma_clip", None) is None:
                    dico["kwargs_sigma_clip"] = def_kwargs_sigma_clip
                masked_array, low_cut, high_cut = sigma_clip(
                    vector_col[~pre_mask],
                    dico["lvl"],
                    **dico["kwargs_sigma_clip"],
                )
                mask = copy(empty_mask)
                mask[~pre_mask] = masked_array.mask
                if unit == "ppm":
                    str_details = f"at more than {dico['lvl']} from the median of {column}, {((high_cut - low_cut) / 2) / np.median(vector_col[~pre_mask]) * 1e6:.2f} {unit} away."
                else:
                    str_details = f"at more than {dico['lvl']} from the median of {column}, {(high_cut - low_cut) / 2:.2f} {unit} away."
            elif dico["method"] == "sigma clip flatten":
                dico["flatten_kwargs"]["return_trend"] = True
                if dico.get("factor", None) is not None:
                    vector_col = dico["factor"] * vector_col
                flatten_lc, trend_lc = flatten(
                    table_LC["BJD_TIME"][~pre_mask],
                    vector_col[~pre_mask],
                    **dico["flatten_kwargs"],
                )
                if plot:
                    if unit == "ppm":
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~pre_mask],
                            trend_lc / np.median(trend_lc) * 1e6,
                            color="C2",
                            zorder=10,
                            label="spline fit",
                        )
                    else:
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~pre_mask],
                            trend_lc,
                            color="C2",
                            zorder=10,
                            label="trend",
                        )
                if dico.get("kwargs_sigma_clip", None) is None:
                    dico["kwargs_sigma_clip"] = def_kwargs_sigma_clip
                masked_array, low_cut, high_cut = sigma_clip(
                    flatten_lc, dico["lvl"], **dico["kwargs_sigma_clip"]
                )
                mask = copy(empty_mask)
                mask[~pre_mask] = masked_array.mask
                if unit == "ppm":
                    str_details = f"at more than {dico['lvl']} from the median of {column}, {((high_cut - low_cut) / 2) / np.median(vector_col[~pre_mask]) * 1e6:.2f} {unit} away."
                else:
                    str_details = f"at more than {dico['lvl']} from the median of {column}, {(high_cut - low_cut) / 2:.2f} {unit} away."
            elif dico["method"] == "sigma clip and sigma flatten":
                dico["flatten_kwargs"]["return_trend"] = True
                if dico.get("kwargs_sigma_clip", None) is None:
                    dico["kwargs_sigma_clip"] = def_kwargs_sigma_clip
                masked_array, low_cut, high_cut = sigma_clip(
                    vector_col[~pre_mask], dico["lvl_1"], **dico["kwargs_sigma_clip"]
                )
                mask_temp = copy(pre_mask)
                mask_temp[~pre_mask] = masked_array.mask
                mask = copy(empty_mask)
                mask[~pre_mask] = masked_array.mask
                if plot:
                    if unit == "ppm":
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][mask],
                            vector_col[mask] / np.median(trend_lc) * 1e6,
                            "+",
                            color="C6",
                            zorder=10,
                            label="first_masked",
                        )
                    else:
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][mask],
                            vector_col[mask],
                            "+",
                            color="C6",
                            zorder=10,
                            label="first_masked",
                        )
                str_first_detection = f"{sum(mask)} outliers detected with the first iteration."
                if dico.get("factor", None) is not None:
                    vector_col = dico["factor"] * vector_col
                flatten_lc, trend_lc = flatten(
                    table_LC["BJD_TIME"][~mask_temp],
                    vector_col[~mask_temp],
                    **dico["flatten_kwargs"],
                )
                if plot:
                    if unit == "ppm":
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~mask_temp],
                            trend_lc / np.median(trend_lc) * 1e6,
                            color="C2",
                            zorder=10,
                            label="trend",
                        )
                    else:
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~mask_temp],
                            trend_lc,
                            color="C2",
                            zorder=10,
                            label="trend",
                        )
                masked_array_2, low_cut, high_cut = sigma_clip(
                    flatten_lc, dico["lvl_2"], **dico["kwargs_sigma_clip"]
                )
                mask[~mask_temp] = masked_array_2.mask
                if unit == "ppm":
                    str_details = f"at more than {dico['lvl_2']} from the median of {column}, {((high_cut - low_cut) / 2) / np.median(vector_col[~pre_mask]) * 1e6:.2f} {unit} away. {str_first_detection}"
                else:
                    str_details = f"at more than {dico['lvl_2']} from the median of {column}, {(high_cut - low_cut) / 2:.2f} {unit} away. {str_first_detection}"
            elif dico["method"] == "sigma flatten and sigma flatten":
                dico["flatten_kwargs_1"]["return_trend"] = True
                dico["flatten_kwargs_2"]["return_trend"] = True
                if dico.get("factor", None) is not None:
                    vector_col = dico["factor"] * vector_col
                flatten_lc, trend_lc = flatten(
                    table_LC["BJD_TIME"][~pre_mask],
                    vector_col[~pre_mask],
                    **dico["flatten_kwargs_1"],
                )
                if dico.get("kwargs_sigma_clip", None) is None:
                    dico["kwargs_sigma_clip"] = def_kwargs_sigma_clip
                masked_array_1, low_cut, high_cut = sigma_clip(
                    flatten_lc, dico["lvl_1"], **dico["kwargs_sigma_clip"]
                )
                mask_temp = copy(pre_mask)
                mask_temp[~pre_mask] = masked_array_1.mask
                mask = copy(empty_mask)
                mask[~pre_mask] = masked_array_1.mask
                if plot:
                    if unit == "ppm":
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~pre_mask],
                            trend_lc / np.median(trend_lc) * 1e6,
                            color="C3",
                            zorder=10,
                            label="pre-trend",
                        )
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][mask],
                            vector_col[mask] / np.median(trend_lc) * 1e6,
                            "+",
                            color="C6",
                            zorder=10,
                            label="first_masked",
                        )
                    else:
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~pre_mask],
                            trend_lc,
                            color="C3",
                            zorder=10,
                            label="pre-trend",
                        )
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][mask],
                            vector_col[mask],
                            "+",
                            color="C6",
                            zorder=10,
                            label="first_masked",
                        )
                str_first_detection = f"{sum(mask)} outliers detected with the first iteration."
                flatten_lc, trend_lc = flatten(
                    table_LC["BJD_TIME"][~mask_temp],
                    vector_col[~mask_temp],
                    **dico["flatten_kwargs_2"],
                )
                masked_array_2, low_cut, high_cut = sigma_clip(
                    flatten_lc, dico["lvl_2"], **dico["kwargs_sigma_clip"]
                )
                if plot:
                    if unit == "ppm":
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~mask_temp],
                            trend_lc / np.median(trend_lc) * 1e6,
                            color="C2",
                            zorder=10,
                            label="trend",
                        )
                    else:
                        axes[idx + 1, 0].plot(
                            table_LC["BJD_TIME"][~mask_temp],
                            trend_lc,
                            color="C2",
                            zorder=10,
                            label="trend",
                        )
                mask[~mask_temp] = masked_array_2.mask
                if unit == "ppm":
                    str_details = f"at more than {dico['lvl_2']} from the median of {column}, {((high_cut - low_cut) / 2) / np.median(vector_col[~pre_mask]) * 1e6:.2f} {unit} away. {str_first_detection}"
                else:
                    str_details = f"at more than {dico['lvl_2']} from the median of {column}, {(high_cut - low_cut) / 2:.2f} {unit} away. {str_first_detection}"
            elif dico["method"] == "flux fraction":
                masked = vector_col[~pre_mask] > (np.median(table_LC["FLUX"]) * dico["lvl"])
                mask = copy(empty_mask)
                mask[~pre_mask] = masked
                str_details = f"at more than {dico['lvl']} flux level."
            elif dico["method"] == "hist_blocks":
                hist, bins_edges = astropy.stats.histogram(vector_col[~pre_mask], bins="blocks")
                mask_bin = hist < dico.get("count_min", 30)
                if not (mask_bin[0]):
                    val_low_cut = bins_edges[0]
                else:
                    val_low_cut = bins_edges[np.where(np.diff(mask_bin))[0][0] + 1]
                if not (mask_bin[-1]):
                    val_high_cut = bins_edges[-1]
                else:
                    val_high_cut = bins_edges[np.where(np.diff(mask_bin))[0][-1] + 1]
                masked = np.logical_or(
                    vector_col[~pre_mask] < val_low_cut,
                    vector_col[~pre_mask] > val_high_cut,
                )
                mask = copy(empty_mask)
                mask[~pre_mask] = masked
                str_details = (
                    f"histogram block method with at least {dico.get('count_min', 30)} counts."
                )
            elif dico["method"] == "KDE":
                X = vector_col[~pre_mask, np.newaxis]
                X_min = X.min()
                X_max = X.max()
                X_span = X_max - X_min
                X_plot = np.linspace(
                    X_min - 0.10 * X_span,
                    X_max + 0.10 * X_span,
                    dico.get("npt_samp", 1000),
                )[:, np.newaxis]
                thresh_prob = dico.get("prob_threshold", None)
                if thresh_prob is None:
                    thresh_prob = dico.get("count_threshold", 30) / X.shape[0]
                kde = KernelDensity(
                    kernel=dico.get("kernel", "gaussian"),
                    bandwidth=X_span / dico.get("bandwidth", 50),
                ).fit(X)
                dens = np.exp(kde.score_samples(X_plot))
                prob_min = 0
                i_min = 0
                while prob_min < thresh_prob:
                    prob_min += dens[i_min] * np.diff(X_plot[:, 0])[i_min]
                    i_min += 1
                val_low_cut = X_plot[:, 0][i_min]
                prob_max = 0
                i_max = X_plot.shape[0] - 1
                while prob_max < thresh_prob:
                    prob_max += dens[i_max] * np.diff(X_plot[:, 0])[i_max - 1]
                    i_max -= 1
                val_high_cut = X_plot[:, 0][i_max]
                masked = np.logical_or(
                    vector_col[~pre_mask] < val_low_cut,
                    vector_col[~pre_mask] > val_high_cut,
                )
                mask = copy(empty_mask)
                mask[~pre_mask] = masked
                str_details = f"probability threshold {dico.get('prob_threshold', None)} (kernel = {dico.get('kernel', 'gaussian')}, bandwitdh = {dico.get('bandwidth', 50)}, npt_samp = {dico.get('npt_samp', 1000)})."
            elif dico["method"] == ">=":
                mask = np.logical_and(vector_col >= dico["threshold"], ~pre_mask)
                str_details = f"equal to {dico['threshold']} or higher."
            elif dico["method"] == ">":
                mask = np.logical_and(vector_col > dico["threshold"], ~pre_mask)
                str_details = f"higher than {dico['threshold']}."
            else:
                raise ValueError(f"The provided method ({dico['method']}) is invalid ")
        logger.info(
            f"Outlier detection of column {column} ({det_name}): {sum(mask)} "
            f"({sum(mask) / len(mask) * 100:.2f} %) data points masked, {str_details}"
        )
        masks[det_name] = mask
        if plot:
            if unit == "ppm":
                axes[idx + 1, 0].plot(
                    table_LC["BJD_TIME"][~pre_mask],
                    ((vector_col / np.median(vector_col) - 1) * 1e6)[~pre_mask],
                    ".",
                )
                axes[idx + 1, 0].plot(
                    table_LC["BJD_TIME"][mask],
                    ((vector_col / np.median(vector_col) - 1) * 1e6)[mask],
                    "x",
                    label="masked",
                )
                # if sum(pre_mask) > 0:
                #     axes[idx + 1, 0].plot(
                #         table_LC["BJD_TIME"][pre_mask],
                #         ((vector_col / np.median(vector_col) - 1) * 1e6)[pre_mask],
                #         "x",
                #         color="C4",
                #         label="pre-masked",
                #     )
            else:
                axes[idx + 1, 0].plot(table_LC["BJD_TIME"][~pre_mask], vector_col[~pre_mask], ".")
                axes[idx + 1, 0].plot(
                    table_LC["BJD_TIME"][mask], vector_col[mask], "x", label="masked"
                )
                # if sum(pre_mask) > 0:
                #     axes[idx + 1, 0].plot(
                #         table_LC["BJD_TIME"][pre_mask],
                #         vector_col[pre_mask],
                #         "x",
                #         color="C4",
                #         label="pre-masked",
                #     )
            axes[0, 0].plot(
                table_LC["BJD_TIME"][mask],
                ((table_LC["FLUX"] / np.median(table_LC["FLUX"]) - 1) * 1e6)[mask],
                "x",
                label=f"masked({det_name})",
            )
            axes[idx + 1, 0].set_ylabel(f"{column} [{unit}] ({det_name})")
            axes[idx + 1, 0].legend()

    if plot:
        axes[0, 0].legend()
        full_mask = copy(base_mask)
        for column in detect_outliers_params.keys():
            full_mask = np.logical_or(full_mask, masks[column])
        axes[idx + 2, 0].plot(
            table_LC["BJD_TIME"][~full_mask],
            ((table_LC["FLUX"] / np.median(table_LC["FLUX"]) - 1) * 1e6)[~full_mask],
            ".",
        )
        axes[idx + 2, 0].set_ylabel("FLUX [ppm] (all masked)")
        axes[-1, 0].set_xlabel("Time [BJD]")
        if show_plot:
            plt.show()
        elif fig is not None:
            if save_plot_file_name is not None:
                fig.savefig(save_plot_file_name)
            plt.close(fig)

    return masks, fig


def create_manual_mask(
    table_LC: Table,
    l_manually_masked_times: Iterable[tuple(np.floating, np.floating)],
    pre_mask: NDArray[np.bool_] | None,
    show_plot: bool = True,
    save_plot_file_name: str | None = None,
):
    """
    Create a manual mask for specified time windows and plot the light curve before and after masking.

    Parameters:
    - table_LC: Astropy Table with 'BJD_TIME' and 'FLUX' columns
    - full_mask: Boolean array of existing masks (points already masked)
    - l_manually_masked_times: List of tuples (start_time, end_time) defining time windows to mask

    Returns:
    - manual_mask: Boolean array where True indicates points to be masked in the specified windows
    """
    manual_mask = np.zeros_like(table_LC["BJD_TIME"], dtype=bool)
    for start_time, end_time in l_manually_masked_times:
        manual_mask = np.logical_or(
            manual_mask,
            np.logical_and(
                table_LC["BJD_TIME"] >= start_time,
                table_LC["BJD_TIME"] <= end_time,
            ),
        )
    if pre_mask is None:
        pre_mask = np.zeros_like(table_LC["BJD_TIME"], dtype=bool)
    flux_ppm = (table_LC["FLUX"] / np.median(table_LC["FLUX"]) - 1) * 1e6
    manually_masked = np.logical_and(~pre_mask, manual_mask)

    # Plot before and after
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    fig, axes = plt.subplots(nrows=2, figsize=(10, 6))

    # Before: show all unmasked points, highlight the manually masked ones
    axes[0].scatter(
        table_LC["BJD_TIME"][~pre_mask],
        flux_ppm[~pre_mask],
        marker=".",
        color="C0",
    )
    axes[0].scatter(
        table_LC["BJD_TIME"][manually_masked],
        flux_ppm[manually_masked],
        marker=".",
        color="C1",
        label="Manually Masked",
    )
    axes[0].text(
        0.05,
        0.95,
        "Before Manual Masking",
        transform=axes[0].transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=props,
    )
    axes[0].set_ylabel("Flux [ppm]")
    axes[0].legend()

    # After: show only the remaining unmasked points
    axes[1].scatter(
        table_LC["BJD_TIME"][np.logical_and(~pre_mask, ~manual_mask)],
        flux_ppm[np.logical_and(~pre_mask, ~manual_mask)],
        marker=".",
        color="C0",
    )
    axes[1].text(
        0.05,
        0.95,
        "After Manual Masking",
        transform=axes[1].transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=props,
    )
    axes[1].set_xlabel("Time [BJD]")
    axes[1].set_ylabel("Flux [ppm]")

    plt.tight_layout()
    if show_plot:
        plt.show()
    else:
        if save_plot_file_name is not None:
            fig.savefig(save_plot_file_name)
        plt.close(fig)

    return manual_mask


def combine_masks(
    masks_dict: dict[str, NDArray[np.bool_]], masks_to_combine: list[str] | None = None
):
    """
    Combine multiple boolean masks into a single mask.

    Parameters:§
    - masks_dict: Dict of boolean masks to combine
    - masks_to_combine: List of keys in masks_dict to combine

    Returns:
    - combined_mask: Boolean array resulting from combining the input masks
    """
    if not masks_dict:
        raise ValueError("masks_dict is empty.")

    combined_mask = np.zeros_like(next(iter(masks_dict.values())), dtype=bool)

    if masks_to_combine is None:
        masks_to_combine = list(masks_dict.keys())

    for mask in masks_to_combine:
        combined_mask = np.logical_or(combined_mask, masks_dict[mask])

    return combined_mask


class Quantity(TypedDict):
    """Specification for a column name and content in the output file"""

    name: Required[str]  # column name for the value
    values: Required[NDArray[np.floating]]  # vector of values
    errors: NotRequired[NDArray[np.floating]]  # vector of errors


def is_quantity(obj: object) -> bool:
    """
    Check if an object has the structure of a Column.

    Args:
        obj: Object to check

    Returns:
        True if obj is a dict with required QuantitySpec keys and types
    """
    if not isinstance(obj, dict):
        return False

    # Check required keys
    if "name" not in obj or not isinstance(obj["name"], str):
        return False
    elif "values" not in obj or not isinstance(obj["values"], np.ndarray):
        return False
    if "errors" in obj and not isinstance(obj["errors"], np.ndarray):
        return False
    return True


def _write_lisa_file(
    time: Quantity,
    quantity: Quantity,
    target_name: str,
    folder_outputs: str,
    dst_nb: int,
    overwrite: bool = False,
):
    if quantity["name"] == "flux":
        inst_cat = "LC"
    elif quantity["name"] == "RV":
        inst_cat = "RV"
    else:
        inst_cat = f"IND-{quantity['name']}"
    file_name = os.path.join(
        folder_outputs,
        f"{inst_cat}_{target_name}_CHEOPS_{dst_nb}.txt",
    )
    if len(time["values"]) != len(quantity["values"]):
        raise ValueError(
            f"Cannot write {file_name}: time column has {len(time['values'])} "
            f"values but {quantity['name']} has {len(quantity['values'])} values."
        )
    if "errors" in quantity and len(quantity["errors"]) != len(quantity["values"]):
        raise ValueError(
            f"Cannot write {file_name}: {quantity['name']} has "
            f"{len(quantity['values'])} values but its errors column has "
            f"{len(quantity['errors'])} values."
        )
    if "errors" in quantity:
        data = np.column_stack((time["values"], quantity["values"], quantity["errors"]))
        column_names = [time["name"], quantity["name"], quantity["name"] + "_err"]
    else:
        data = np.column_stack((time["values"], quantity["values"]))
        column_names = [time["name"], quantity["name"]]
    astro_ascii.write(
        data,
        names=column_names,
        output=file_name,
        delimiter="\t",
        overwrite=overwrite,
    )
    logger.info(f"Created file {file_name}.")


TransformFunc = Callable[[NDArray[np.floating]], NDArray[np.floating]]
ContextFunc = Callable[[NDArray[np.floating]], Any]
TransformWithContextFunc = Callable[[NDArray[np.floating], Any], NDArray[np.floating]]


class QuantitySpec(TypedDict):
    """Specification for a quantity to write to output file"""

    output_name: Required[str]
    table_name: Required[str]  # column name for the value
    transform: NotRequired[TransformFunc]
    context: NotRequired[ContextFunc]
    transform_with_context: NotRequired[TransformWithContextFunc]
    table_error_name: NotRequired[str]  # column name for the error (optional)
    transform_error: NotRequired[TransformFunc]
    transform_error_with_context: NotRequired[TransformWithContextFunc]


def _create_quantity_from_spec(
    tables: Iterable[Table],
    spec_dict: QuantitySpec,
    mask: NDArray[np.bool_] | None = None,
) -> Quantity:
    # Check if table_name is found in one of the tables
    found = False
    for table in tables:
        if spec_dict["table_name"] in table.columns:
            found = True
            break
    if not (found):
        raise ValueError(f"Column {spec_dict['table_name']} wasn't found in the provided tables")
    # Create Column
    quant = Quantity(name=spec_dict["output_name"], values=table[spec_dict["table_name"]].copy())
    # Apply mask
    if mask is None:
        mask = np.zeros_like(quant["values"], dtype=bool)
    quant["values"] = quant["values"][np.logical_not(mask)]
    context = None
    if "context" in spec_dict:
        context = spec_dict["context"](quant["values"])
    # Apply transformation
    if "transform_with_context" in spec_dict:
        quant["values"] = spec_dict["transform_with_context"](quant["values"], context)
    elif "transform" in spec_dict:
        quant["values"] = spec_dict["transform"](quant["values"])
    # Create errors column
    if "table_error_name" in spec_dict:
        if spec_dict["table_error_name"] in table.columns:
            quant["errors"] = table[spec_dict["table_error_name"]][np.logical_not(mask)]
            if "transform_error_with_context" in spec_dict:
                quant["errors"] = spec_dict["transform_error_with_context"](
                    quant["errors"], context
                )
            elif "transform_error" in spec_dict:
                quant["errors"] = spec_dict["transform_error"](quant["errors"])
        else:
            logger.warning(
                f"Error column {spec_dict['table_error_name']} wasn't found. No error will be written in file."
            )
    return quant


def _apply_mask_to_quantity(
    quantity: Quantity,
    mask: NDArray[np.bool_] | None,
) -> Quantity:
    if mask is None:
        return quantity

    n_values = len(quantity["values"])
    n_mask = len(mask)
    n_unmasked = int(np.sum(~mask))
    if n_values == n_unmasked:
        return quantity
    if n_values != n_mask:
        raise ValueError(
            f"Quantity {quantity['name']} has {n_values} values, but mask has "
            f"{n_mask} values and {n_unmasked} unmasked values."
        )

    masked_quantity = Quantity(
        name=quantity["name"], values=quantity["values"][np.logical_not(mask)]
    )
    if "errors" in quantity:
        masked_quantity["errors"] = quantity["errors"][np.logical_not(mask)]
    return masked_quantity


def write_lisa_files(
    tables: Iterable[Table],
    time: QuantitySpec | Quantity,
    quantities: tuple[QuantitySpec | Quantity],
    mask: NDArray[np.bool_] | None,
    target_name: str,
    folder_outputs: str,
    dst_nb: int,
    overwrite: bool = False,
):
    # Create times Column if Needed
    if not is_quantity(time):
        time = _create_quantity_from_spec(tables=tables, spec_dict=time, mask=mask)
    else:
        time = _apply_mask_to_quantity(time, mask)
    # Create on file per element in quantities_dict
    for quantity in quantities:
        if not is_quantity(quantity):
            quantity = _create_quantity_from_spec(tables=tables, spec_dict=quantity, mask=mask)
        else:
            quantity = _apply_mask_to_quantity(quantity, mask)
        _write_lisa_file(
            time=time,
            quantity=quantity,
            target_name=target_name,
            folder_outputs=folder_outputs,
            dst_nb=dst_nb,
            overwrite=overwrite,
        )


def process_visit(
    visit_folder_path: str,
    aperture: str,
    dst_nb: int,
    target_name: str,
    quantities: tuple[QuantitySpec | Quantity, ...],
    time: QuantitySpec | Quantity | None = None,
    folder_outputs: str = "lisa_formated_data",
    folder_diagnostics: str | None = None,
    l_manually_masked_times: Iterable[tuple[np.floating, np.floating]] = (),
    detect_outliers_params: dict | None = None,
    masks_to_combine: list[str] | None = None,
    show_plots: bool = False,
    overwrite: bool = False,
):
    if folder_diagnostics is None:
        folder_diagnostics = folder_outputs
    os.makedirs(folder_outputs, exist_ok=True)
    os.makedirs(folder_diagnostics, exist_ok=True)
    path_LC_file, filekey, version = get_LC_file(
        visit_folder_path=visit_folder_path, aperture=aperture
    )
    path_RAW_SubArray_file, _, _ = get_SubArray_file(
        visit_folder_path=visit_folder_path,
        version=version,
        lvl="RAW",
        file_key=filekey,
    )
    logger.info(
        f"Processing {filekey}, data version {version}, aperture {aperture}, dataset {dst_nb}."
    )
    logger.info(f"Lightcurve file: {path_LC_file}")
    logger.info(f"RAW SubArray file: {path_RAW_SubArray_file}")

    table_LC, texptime = load_LC_file(path_LC_file)
    table_metadata = load_metada(path_RAW_SubArray_file, lvl="RAW")

    avg_location_x = np.mean(table_LC["LOCATION_X"])
    avg_location_y = np.mean(table_LC["LOCATION_Y"])
    visit_duration, efficiency = compute_visit_duration_efficiency(
        time_vector=table_LC["BJD_TIME"],
        time_unit=uu.day,
        texptime=texptime,
    )
    l_manually_masked_times = tuple(l_manually_masked_times)
    if l_manually_masked_times:
        manual_mask = create_manual_mask(
            table_LC=table_LC,
            l_manually_masked_times=l_manually_masked_times,
            pre_mask=None,
            show_plot=show_plots,
            save_plot_file_name=os.path.join(
                folder_diagnostics, f"manualmask_{target_name}_CHEOPS_{dst_nb}.pdf"
            ),
        )
    else:
        manual_mask = np.zeros_like(table_LC["BJD_TIME"], dtype=bool)
    if not detect_outliers_params:
        full_mask = manual_mask
    else:
        masks, fig_outliers = detect_outliers(
            table_LC,
            table_metadata,
            detect_outliers_params,
            plot=True,
            show_plot=show_plots,
            pre_mask=manual_mask,
            save_plot_file_name=os.path.join(
                folder_diagnostics, f"outliers_{target_name}_CHEOPS_{dst_nb}.pdf"
            ),
        )
        full_mask = np.logical_or(manual_mask, combine_masks(masks, masks_to_combine))
    visit_duration_unmasked, efficiency_unmasked = compute_visit_duration_efficiency(
        time_vector=table_LC["BJD_TIME"][~full_mask],
        time_unit=uu.day,
        texptime=texptime,
    )

    if time is None:
        time = {
            "output_name": "time",
            "table_name": "BJD_TIME",
            "transform": lambda values: values - 2457000,
        }
    write_lisa_files(
        tables=(table_LC, table_metadata),
        time=time,
        quantities=quantities,
        mask=full_mask,
        target_name=target_name,
        folder_outputs=folder_outputs,
        dst_nb=dst_nb,
        overwrite=overwrite,
    )

    n_masked = int(np.sum(full_mask))
    summary_file = os.path.join(folder_diagnostics, f"summary_{target_name}_CHEOPS_{dst_nb}.txt")
    summary_lines = [
        f"target_name\t{target_name}",
        f"dataset_number\t{dst_nb}",
        f"visit_folder\t{visit_folder_path}",
        f"file_key\t{filekey}",
        f"version\t{version}",
        f"aperture\t{aperture}",
        f"lightcurve_file\t{path_LC_file}",
        f"raw_subarray_file\t{path_RAW_SubArray_file}",
        f"average_location_x\t{avg_location_x}",
        f"average_location_y\t{avg_location_y}",
        f"n_points\t{len(table_LC)}",
        f"n_masked_points\t{n_masked}",
        f"n_unmasked_points\t{len(table_LC) - n_masked}",
        f"visit_duration\t{visit_duration}",
        f"visit_duration_hours\t{visit_duration.to(uu.h)}",
        f"efficiency\t{efficiency}",
        f"visit_duration_unmasked\t{visit_duration_unmasked}",
        f"visit_duration_unmasked_hours\t{visit_duration_unmasked.to(uu.h)}",
        f"efficiency_unmasked\t{efficiency_unmasked}",
    ]
    with open(summary_file, "w", encoding="utf-8") as file:
        file.write("\n".join(summary_lines) + "\n")

    logger.info(
        f"Average CCD location: x={avg_location_x}, y={avg_location_y}. "
        f"Visit duration: {visit_duration} ({efficiency * 100:.2f}% efficiency); "
        f"after outlier removal: {visit_duration_unmasked} "
        f"({efficiency_unmasked * 100:.2f}% efficiency)."
    )
    logger.info(f"Visit summary written to {summary_file}.")
    logger.success(f"Processing {filekey} as dataset {dst_nb} successfully processed.")
    return {
        "path_LC_file": path_LC_file,
        "path_RAW_SubArray_file": path_RAW_SubArray_file,
        "filekey": filekey,
        "version": version,
        "mask": full_mask,
        "summary_file": summary_file,
        "folder_outputs": folder_outputs,
        "folder_diagnostics": folder_diagnostics,
    }
