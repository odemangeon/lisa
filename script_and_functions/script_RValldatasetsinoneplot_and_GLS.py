"""Making plots that show all the RV data on the same plot (with the delta RV and the v0 removed)
modelsNresiduals
"""
import matplotlib.pyplot as pl
import numpy as np
import sys
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator

from lisa.emcee_tools.emcee_tools import add_twoaxeswithsharex, add_axeswithsharex
from lisa.posterior.exoplanet.model.datasim_creator_rv import RVdrift_tref_name

path_pyGLS = "/Users/olivier/Softwares/PyGLS"
if path_pyGLS not in sys.path:
    sys.path.append(path_pyGLS)
from gls_mod import Gls


l_RV_datasets = ['RV_HD109286_SOPHIEp_0', ]

RV_fact = 1e3

key_whole = "whole"

extra_dt = 10

kwargs_datasim = {}  # RVdrift_tref_name: 56040.0

pl_kwargs = {'RV_HD109286_SOPHIEp_0': {'fmt': 'o', 'color': 'C1', 'mfc': 'white', 'ms': 4, 'mew': 1, "alpha_jitter": 0.5, "color_jitter": 'C1', 'label': "SOPHIE+"},
             'model': {'color': 'C2', 'alpha': 1, 'linewidth': 0.5, 'label': 'model'},
             'GP': {'color': 'C2', 'alpha': 0.3, 'linewidth': 0.5, 'label': 'GP'},
             }

# Create the times array for the data, model, return_models residuals
time = {}
for rv_dst in l_RV_datasets:
    time[rv_dst] = modelsNresiduals[rv_dst][key_whole]["time"][0]
all_time = np.concatenate([time[dst] for dst in l_RV_datasets])
idx_sort = np.argsort(all_time)
all_time = all_time[idx_sort]
tmin = all_time[0]
tmax = all_time[-1]
tspan = tmax - tmin

# Create the rv_data and rv_data_err array where the v0 and the delta_RV are removed from the RV data
rv_data = {}
rv_data_err = {}
rv_data_err_jitter = {}
for rv_dst in l_RV_datasets:
    rv_data_err[rv_dst] = post_instance.dataset_db[rv_dst].get_data_err() * RV_fact
    if rv_dst == "RV_HD109286_SOPHIEp_0":
        rv_data[rv_dst] = (post_instance.dataset_db[rv_dst].get_data() - df_fittedval.loc["HD109286_A_v0"]["value"]) * RV_fact
        rv_data_err_jitter[rv_dst] = np.sqrt(rv_data_err[rv_dst]**2 + (df_fittedval.loc["RV_SOPHIEp_def_jitter"]["value"] * RV_fact)**2)
    elif rv_dst == "RV_HD109286_SOPHIE_0":
        rv_data[rv_dst] = (post_instance.dataset_db[rv_dst].get_data() - (df_fittedval.loc["HD109286_A_v0"]["value"] + df_fittedval.loc["RV_SOPHIE_def_DeltaRV"]["value"])) * RV_fact
        rv_data_err_jitter[rv_dst] = np.sqrt(rv_data_err[rv_dst]**2 + (df_fittedval.loc["RV_SOPHIE_def_jitter"]["value"] * RV_fact)**2)
    elif rv_dst == "RV_HD109286_ELODIE_0":
        rv_data[rv_dst] = (post_instance.dataset_db[rv_dst].get_data() - (df_fittedval.loc["HD109286_A_v0"]["value"] + df_fittedval.loc["RV_ELODIE_def_DeltaRV"]["value"])) * RV_fact
        rv_data_err_jitter[rv_dst] = np.sqrt(rv_data_err[rv_dst]**2 + (df_fittedval.loc["RV_ELODIE_def_jitter"]["value"] * RV_fact)**2)
all_rv_data = np.concatenate([rv_data[dst] for dst in l_RV_datasets])[idx_sort]
all_rv_data_err = np.concatenate([rv_data_err[dst] for dst in l_RV_datasets])[idx_sort]
all_rv_data_err_jitter = np.concatenate([rv_data_err_jitter[dst] for dst in l_RV_datasets])[idx_sort]

# Create the model for the time series
rv_inst_ref = "RV_SOPHIEp_def"
dsts_inst_ref = 'RV_HD109286_SOPHIEp_0'
tsim = np.linspace(tmin - extra_dt, tmax + extra_dt, 5000)
model, model_wGP, gp_pred, gp_pred_var = post_instance.compute_model(tsim=tsim, dataset_name=dsts_inst_ref,
                                                                     param=df_fittedval["value"].values,
                                                                     l_param_name=list(df_fittedval.index),
                                                                     key_obj=key_whole,
                                                                     datasim_kwargs=kwargs_datasim)
model -= df_fittedval["value"]["HD109286_A_v0"]
model *= RV_fact
if model_wGP is not None:
    model_wGP -= df_fittedval["value"]["HD109286_A_v0"]
    model_wGP *= RV_fact
    gp_pred *= RV_fact
    gp_pred_var *= RV_fact**2


# Create the model for the GLS
model_GLS, _, gp_pred_GLS, gp_pred_var_GLS = post_instance.compute_model(tsim=all_time, dataset_name=dsts_inst_ref,
                                                                         param=df_fittedval["value"].values, l_param_name=list(df_fittedval.index),
                                                                         key_obj=key_whole, datasim_kwargs=kwargs_datasim)
model_GLS *= RV_fact
if gp_pred_GLS is not None:
    gp_pred_GLS *= RV_fact
    gp_pred_var_GLS *= RV_fact**2

# Create the residuals arrays
resi = {}
for rv_dst in l_RV_datasets:
    if modelsNresiduals[rv_dst][key_whole]['residuals w GP'][0] is None:
        resi[rv_dst] = modelsNresiduals[rv_dst][key_whole]['residuals'][0] * RV_fact
    else:
        resi[rv_dst] = modelsNresiduals[rv_dst][key_whole]['residuals w GP'][0] * RV_fact
all_resi = np.concatenate([resi[dst] for dst in l_RV_datasets])
all_resi = all_resi[idx_sort]

# PLOTS
# fig, ax = pl.subplots(ncols=2, constrained_layout=True)
fig = pl.figure(figsize=(12, 8), constrained_layout=True)
gs = GridSpec(nrows=1, ncols=2, figure=fig)
gs_time_series = gs[0]
gs_gls = gs[1]
(axe_data, axe_resi) = add_twoaxeswithsharex(gs_time_series, fig, gs_from_sps_kw={"wspace": 0.2})

# RV TIME SERIES
axe_data.set_title("RV time series")
axe_resi.set_xlabel("time [BTJD]")
axe_data.set_ylabel("RV [m/s]")
axe_resi.set_ylabel("residuals [m/s]")

axe_data.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True, labelbottom=False)
axe_data.xaxis.set_minor_locator(AutoMinorLocator())
axe_data.yaxis.set_minor_locator(AutoMinorLocator())
axe_data.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
axe_data.grid(axis="y", color="black", alpha=.5, linewidth=.5)
axe_resi.yaxis.set_minor_locator(AutoMinorLocator())
axe_resi.tick_params(axis="both", direction="in", length=4, width=1, bottom=True, top=True, left=True, right=True)
axe_resi.tick_params(axis="both", direction="in", which="minor", length=2, width=0.5, left=True, right=True, bottom=True, top=True)
axe_resi.grid(axis="y", color="black", alpha=.5, linewidth=.5)

for dst in l_RV_datasets:
    axe_data.errorbar(time[dst], y=rv_data[dst], yerr=rv_data_err[dst], color=pl_kwargs[dst]['color'], fmt=pl_kwargs[dst]['fmt'],
                      mfc=pl_kwargs[dst]['mfc'], ms=pl_kwargs[dst]['ms'], mew=pl_kwargs[dst]['mew'], label=pl_kwargs[dst]['label'])  # Plot the data point and error bars without jitter
    axe_data.errorbar(time[dst], y=rv_data[dst], yerr=rv_data_err_jitter[dst], ecolor=pl_kwargs[dst]['color_jitter'],
                      fmt='None', alpha=pl_kwargs[dst]['alpha_jitter'])  # Plot the error bars with jitter
ylims = axe_data.get_ylim()
xlims = axe_data.get_xlim()
axe_data.hlines(0, *xlims, colors="k", linestyles="dashed")

axe_data.plot(tsim, model, color=pl_kwargs["model"]["color"], linewidth=pl_kwargs["model"]["linewidth"], label=pl_kwargs["model"]["label"])
if model_wGP is not None:
    GP_pred_var = axe_data.fill_between(tsim, model_wGP - np.sqrt(gp_pred_var), model_wGP + np.sqrt(gp_pred_var),
                                        color=pl_kwargs["GP"]["color"], alpha=pl_kwargs["GP"]["alpha"],
                                        label=pl_kwargs["GP"]["label"]  # **kwarg_GP_pred_var
                                        )
axe_data.legend()

for dst in l_RV_datasets:
    axe_resi.errorbar(time[dst], y=resi[dst], yerr=rv_data_err[dst], color=pl_kwargs[dst]['color'], fmt=pl_kwargs[dst]['fmt'],
                      mfc=pl_kwargs[dst]['mfc'], ms=pl_kwargs[dst]['ms'], mew=pl_kwargs[dst]['mew'], label=pl_kwargs[dst]['label'])
    axe_resi.errorbar(time[dst], y=resi[dst], yerr=rv_data_err_jitter[dst], ecolor=pl_kwargs[dst]['color_jitter'],
                      fmt='None', alpha=pl_kwargs[dst]['alpha_jitter'])  # Plot the error bars with jitter

axe_resi.hlines(0, *xlims, colors="k", linestyles="dashed")
axe_resi.set_xlim(xlims)

# RV GLS
if gp_pred_var_GLS is not None:
    gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err_jitter, 'label': "data", 'linewidth': "0.8"},
                  "model": {"data": model_GLS, "err": np.sqrt(gp_pred_var_GLS), 'label': "model", 'linewidth': "0.8"},  # np.sqrt(gp_pred_var_GLS)
                  "GP": {"data": gp_pred_GLS, "err": np.sqrt(gp_pred_var_GLS), 'label': "GP", 'linewidth': "0.8"},
                  "resi": {"data": all_resi, "err": all_rv_data_err_jitter, 'label': "residuals", 'linewidth': "0.8"},  # all_rv_data_err_jitter, all_rv_data_err
                  }
    l_gls_key = ["data", "model", "GP", "resi"]
else:
    gls_inputs = {"data": {"data": all_rv_data, "err": all_rv_data_err_jitter, 'label': "data", 'linewidth': "0.8"},
                  "model": {"data": model_GLS, "err": all_rv_data_err_jitter, 'label': "model", 'linewidth': "0.8"},  # np.sqrt(gp_pred_var_GLS)
                  "resi": {"data": all_resi, "err": all_rv_data_err_jitter, 'label': "residuals", 'linewidth': "0.8"},  # all_rv_data_err_jitter, all_rv_data_err
                  }
    l_gls_key = ["data", "model", "resi"]

if model_wGP:
    nb_axes = 4
else:
    nb_axes = 3
ax_gls = add_axeswithsharex(gs_gls, fig, nb_axes=nb_axes, gs_from_sps_kw={"wspace": 0.2})
for ii in range(nb_axes - 1):
    ax_gls[ii].tick_params(labelbottom=False)
ax_gls[0].set_title("GLS Periodograms")
ax_gls[-1].set_xscale("log")
ax_gls[-1].set_xlabel("Period [days]")

act_period = []
act_label = [r"$P_{rot}$", r"$\frac{P_{rot}}{2}$"]
act_align = ['left', 'right']
act_color = ['C6', 'C6']
act_shift = [5, 0.0]

pl_period = [2171.5]
pl_label = [r"$P_{b}$"]
pl_align = ['right', 'left', "left"]
pl_color = ['C3', 'C4', "C5"]
pl_shift = [-0.1, 0.3, 0.5]

fap = [0.1, 1., 10.]
fap_ls = ["dotted", "dashdot", "dashed"]
fap_align = ['bottom', 'center', 'top']
fap_yshift = [0.01, 0.0, -0.02]
fap_xshift = -0.01

for ii, key in enumerate(l_gls_key):
    gls = Gls((all_time, gls_inputs[key]["data"], gls_inputs[key]["err"]), Pbeg=0.1, Pend=3268, verbose=False)
# gls_data = Gls((all_time, all_rv_data, all_rv_data_err), Pbeg=0.4, Pend=150, verbose=False)
# gls_model = Gls((all_time, model_GLS, all_rv_data_err), Pbeg=0.4, Pend=150, verbose=False)  # np.sqrt(gp_pred_var_GLS)
# gls_GP = Gls((all_time, gp_pred_GLS, all_rv_data_err), Pbeg=0.4, Pend=150, verbose=False)  # np.sqrt(gp_pred_var_GLS)
# gls_resi = Gls((all_time, all_resi, all_rv_data_err), Pbeg=0.4, Pend=150, verbose=False)  # np.sqrt(gp_pred_var_GLS)
    ax_gls[ii].plot(1 / gls.freq, gls.power, 'k-', label=gls_inputs[key]["label"], linewidth=gls_inputs[key]["linewidth"])
# ax_gls[1].plot(1 / gls_model.freq, gls_model.power, 'k-', label="model")
# ax_gls[2].plot(1 / gls_GP.freq, gls_GP.power, 'k-', label="GP")
# ax_gls[3].plot(1 / gls_resi.freq, gls_resi.power, 'k-', label="GP")
    ax_gls[ii].set_ylabel(f"{gls.label['ylabel']}")  # {gls_inputs[key]['label']}
    ax_gls[ii].yaxis.set_label_position("right")
    ax_gls[ii].yaxis.tick_right()
    ax_gls[ii].yaxis.set_minor_locator(AutoMinorLocator())
    ax_gls[ii].tick_params(axis="both", direction="in", which="both", bottom=True, top=True, left=True, right=True)
    ax_gls[ii].tick_params(axis="both", which="major", length=4, width=1)
    ax_gls[ii].tick_params(axis="both", which="minor", length=2, width=0.5)

    ylims = ax_gls[ii].get_ylim()
    xlims = ax_gls[ii].get_xlim()
    for per, lab, align, shift, color in zip(act_period, act_label, act_align, act_shift, act_color):
        ax_gls[ii].vlines(per, *ylims, colors="k", linestyles="dotted", linewidth=0.5, color=color)
        if key == "data":
            ax_gls[ii].text(per + shift, ylims[0] + 0.9 * (ylims[1] - ylims[0]), lab, horizontalalignment=align, color=color)
    for per, lab, align, shift, color in zip(pl_period, pl_label, pl_align, pl_shift, pl_color):
        ax_gls[ii].vlines(per, *ylims, colors="k", linestyles="dashed", linewidth=0.5, color=color)
        if key == "data":
            ax_gls[ii].text(per + shift, ylims[0] + 0.9 * (ylims[1] - ylims[0]), lab, horizontalalignment=align, color=color)
    ax_gls[ii].set_ylim(ylims)
    for fap_ii, ls_ii, align, yshift in zip(fap, fap_ls, fap_align, fap_yshift):
        pow_ii = gls.powerLevel(fap_ii / 100)
        if pow_ii < ylims[1]:
            ax_gls[ii].hlines(pow_ii, *xlims, colors="k", linestyles=ls_ii, linewidth=0.5)
            ax_gls[ii].text(xlims[0] + fap_xshift, pow_ii + yshift * (ylims[1] - ylims[0]),
                            f"{fap_ii} %", verticalalignment=align, horizontalalignment="right")
    ax_gls[ii].set_xlim(xlims)
    ax_gls[ii].legend(handletextpad=-.1, handlelength=0)

pl.show()
