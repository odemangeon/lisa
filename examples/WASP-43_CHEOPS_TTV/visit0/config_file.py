# Configuration file for LISA analysis.

import json
import os

import astropy.units as uu
import numpy as np
import pandas as pd
import scipy as sp

# #########
# ## logger
from loguru import logger

if "sinkid_file_explore" in globals():
    logger.remove(sinkid_file_explore)
    del sinkid_file_explore
if "sinkid_file_analyze" in globals():
    logger.remove(sinkid_file_analyze)
    del sinkid_file_analyze
if "sinkid_file_plot" in globals():
    logger.remove(sinkid_file_plot)
    del sinkid_file_plot
if "sinkid_file_config" not in globals():
    from lisa.explore_analyze.misc import get_def_output_folders

    output_folders = get_def_output_folders(run_folder=None)
    sinkid_file_config = logger.add(
        os.path.join(output_folders["log"], "config.log"), level="DEBUG"
    )

##############
## Object name
##############
# Give a name to the object that you are studying. DO NOT use _

object_name = "WASP-43"

instrument = "CHEOPS"

##########
## Folders
##########

run_folder = "."

data_folder = "../data"


###########
## Datasets
###########

# List of the paths to the dataset files that you want to use

l_idxdst_all = [
    0,
]
l_IND = ["ROLL", "CX", "CY", "SMEAR", "TF2", "BKG", "DARK", "CONTA"]
l_dataset = []
for idxdst in l_idxdst_all:
    l_dataset.append(f"LC_{object_name}_{instrument}_{idxdst}.txt")
    for ind in l_IND:
        l_dataset.append(f"IND-{ind}_{object_name}_{instrument}_{idxdst}.txt")

##############################
## Instrument model definition
##############################
# Define which instrument model you want to use for each dataset
# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument
# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.
# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0').
d_inst_model_def: dict[str, dict[str, dict[str, str]]] = {}
for ind in l_IND:
    d_inst_model_def[f"IND-{ind}"] = {"CHEOPS": {}}
    for ii in l_idxdst_all:
        d_inst_model_def[f"IND-{ind}"]["CHEOPS"][f"{ii}"] = "inst"
d_inst_model_def["LC"] = {"CHEOPS": {}}
for ii in l_idxdst_all:
    d_inst_model_def["LC"]["CHEOPS"][f"{ii}"] = f"inst{ii}"

####################################
## Model category definition
####################################
# Define the model category and the parameters of the model that are specfic to the model category.

# Available model categories are [<class 'lisa.posterior.exoplanet.model.gravgroup.model.GravGroup'>]
model_category = "GravitionalGroups"

# Stars
#######
# Specify the number of stars in the gravitational group. This can be specified by giving a number (ex: 1)
stars = 1

# Planets
#########
# Specify the number of planets in the gravitational group. This can be specified by giving a number (ex: 1) or a list of planet names (ex: ['b'])
planets = 1

# Orbital models
################
orbital_model = {
    "b": {"do": True, "model4instrument": {}, "model_definitions": {}},
}

for idxdst in l_idxdst_all:
    orbital_model["b"]["model4instrument"][f"LC_{instrument}_inst{idxdst}"] = f"orb{idxdst}"
    orbital_model["b"]["model_definitions"][f"orb{idxdst}"] = {
        "category": "batman",
        "param_extensions": {
            "planet": {
                "P": "",
                "cosinc": "",
                "ecosw": "",
                "esinw": "",
                "tic": f"{idxdst}",
            },
            "star": {"rho": ""},
        },
        "parametrisation": {
            "ew_format": "ecosw-esinw",
            "inc_format": "cosinc",
            "use_aR": False,
            "use_tic": True,
        },
    }
#############################
## Configuration of LC models
#############################


# Decorrelation
###############
#
# Define if you want to include decorrelation models.
# In the dictionary below, each key corresponds to an instrument model and has for value a dictionary with the following structure:
# {"do": True/False,
#  "<decorrelation_model_name>": {"<Indicator instrument model name>": {decorrelation_model_options},  ...}
# If "do" is False no decorrelation is performed for the data taken with the instrument model.
# Otherwise, for each available decorrelation model you need to provide the name of the instrument
# model of the indicators that you want to use and the options for the decorrelation method
#
# The list of datasets for each LC instrument model are:
# {'LC_CHEOPS_inst0': ['LC_WASP-43_CHEOPS_0']}
#
# The list of datasets for each IND instrument model are:
# {'IND-SMEAR_CHEOPS_inst': ['IND-SMEAR_WASP-43_CHEOPS_0'], 'IND-DARK_CHEOPS_inst': ['IND-DARK_WASP-43_CHEOPS_0'], 'IND-CONTA_CHEOPS_inst': ['IND-CONTA_WASP-43_CHEOPS_0'], 'IND-TF2_CHEOPS_inst': ['IND-TF2_WASP-43_CHEOPS_0'], 'IND-CX_CHEOPS_inst': ['IND-CX_WASP-43_CHEOPS_0'], 'IND-ROLL_CHEOPS_inst': ['IND-ROLL_WASP-43_CHEOPS_0'], 'IND-CY_CHEOPS_inst': ['IND-CY_WASP-43_CHEOPS_0'], 'IND-BKG_CHEOPS_inst': ['IND-BKG_WASP-43_CHEOPS_0']}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}
# bispline: {'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}


# Decorrelation Model
#####################
decorrelation_model_LC = {}
for idxdst in l_idxdst_all:
    decorrelation_model_LC[f"LC_{instrument}_inst{idxdst}"] = {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    }

# Decorrelation likelihood
##########################

decorrelation_likelihood_LC = {"do": True, "model_definitions": {}, "order_models": []}

# Decorrelation against Temperature
for ii in l_idxdst_all:
    decorrelation_likelihood_LC["order_models"].append(f"T{ii}")
    decorrelation_likelihood_LC["model_definitions"][f"T{ii}"] = {
        "category": "spline",
        "spline_type": "UnivariateSpline",
        "spline_kwargs": {"k": 3},
        "match datasets": {f"LC_{object_name}_CHEOPS_{ii}": f"IND-TF2_{object_name}_CHEOPS_{ii}"},
    }

# Decorrelation against Background
for ii in l_idxdst_all:
    decorrelation_likelihood_LC["order_models"].append(f"BKG{ii}")
    decorrelation_likelihood_LC["model_definitions"][f"BKG{ii}"] = {
        "category": "spline",
        "spline_type": "UnivariateSpline",
        "spline_kwargs": {"k": 3},
        "match datasets": {f"LC_{object_name}_CHEOPS_{ii}": f"IND-BKG_{object_name}_CHEOPS_{ii}"},
    }

# Decorrelation against X and Y position
window_pos = {
    0: l_idxdst_all,
}
for window_pos_i, l_dataset_idx in window_pos.items():
    decorrelation_likelihood_LC["order_models"].append(f"XY{window_pos_i}")
    match_dataset = {}
    for ii in l_dataset_idx:
        match_dataset[f"LC_{object_name}_CHEOPS_{ii}"] = {
            "X": f"IND-CX_{object_name}_CHEOPS_{ii}",
            "Y": f"IND-CY_{object_name}_CHEOPS_{ii}",
        }
    decorrelation_likelihood_LC["model_definitions"][f"XY{window_pos_i}"] = {
        "category": "bispline",
        "spline_type": "SmoothBivariateSpline",
        "spline_kwargs": {"kx": 3, "ky": 3},
        "match datasets": match_dataset,
    }

# Decorrelation against ROLL angle
# One per visit
# for ii in l_idxdst_all:
#     decorrelation_likelihood_LC["order_models"].append(f"ROLL{ii}")
#     decorrelation_likelihood_LC["model_definitions"][f"ROLL{ii}"] = {
#         "category": "spline",
#         "spline_type": "UnivariateSpline",
#         "spline_kwargs": {"k": 3},
#         "match datasets": {
#             f"LC_{object_name}_CHEOPS_{ii}": f"IND-ROLL_{object_name}_CHEOPS_{ii}"
#         },
#     }
# # One for all visits
decorrelation_likelihood_LC["order_models"].append("ROLL")
decorrelation_likelihood_LC["model_definitions"]["ROLL"] = {
    "category": "spline",
    "spline_type": "UnivariateSpline",
    "spline_kwargs": {"k": 3},
    "match datasets": {},
}
for ii in l_idxdst_all:
    decorrelation_likelihood_LC["model_definitions"]["ROLL"]["match datasets"][
        f"LC_{object_name}_CHEOPS_{ii}"
    ] = f"IND-ROLL_{object_name}_CHEOPS_{ii}"

# Transit model
################

transit_model = {
    "b": {
        "do": True,
        "model4instrument": {},
        "model_definitions": {
            "": {
                "category": "batman",
                "param_extensions": {"planet": {"Rrat": ""}, "star": {}},
            }
        },
    }
}
for ii in l_idxdst_all:
    transit_model["b"]["model4instrument"][f"LC_{instrument}_inst{ii}"] = ""

# Limb-darkening.
#################
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {"A": {}}

for ii in l_idxdst_all:
    LDs["A"][f"LC_{instrument}_inst{ii}"] = "LDC"

LDs["A"]["LD_models"] = {"LDC": "nonlinear"}

# Phase curve model
####################
phasecurve_model = {
    "b": {
        "do": False,
        "model4instrument": {
            # "LC_CHEOPS_inst0": [""]
        },
        "model_definitions": {
            # "": {
            #     "args": {
            #         "factor_period": 1,
            #         "flux_offset": "param",
            #         "occultation": True,
            #         "phase_offset": "param",
            #         "sincos": "cos",
            #     },
            #     "category": "sincos",
            #     "param_extensions": {
            #         "planet": {"A": "", "Foffset": "", "Phi": "", "Rrat": ""},
            #         "star": {},
            #     },
            # }
        },
    }
}

# Occultation model
####################
# WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
occultation_model = {
    "b": {
        "do": False,
        "model4instrument": {
            # "LC_CHEOPS_inst0": ""
        },
        "model_definitions": {
            # "": {
            #     "category": "batman",
            #     "param_extensions": {"planet": {"Frat": "", "Rrat": ""}, "star": {}},
            # }
        },
    }
}

# Supersampling and exposure_time for LC
########################################
SuperSamps_LC = {}
for ii in l_idxdst_all:
    SuperSamps_LC[f"LC_{instrument}_inst{ii}"] = {
        "supersamp": 1,
        "exptime": 0.02043402778,
    }

# Instrumental model for LC
###########################

# Polynomial trend models for LC
################################
polynomial_model_LC = {"A": {"do": False, "order": 0, "tref": None}}
df_fluxs = {}
for ii in l_idxdst_all:
    df_fluxs[ii] = pd.read_table(
        os.path.join(data_folder, f"LC_{object_name}_{instrument}_{ii}.txt"),
        sep=r"\s+",
        comment="#",
    )
    polynomial_model_LC[f"LC_{instrument}_inst{ii}"] = {
        "do": True,
        "order": 1,
        "tref": df_fluxs[ii]["time"].min(),
    }

#############################
## Configuration of IND models
#############################
# Polynomial trend models for IND
#################################
# Define the model to use for each indicator category. Available models are ['polynomial']
SMEAR = {
    "IND-SMEAR_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
DARK = {
    "IND-DARK_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
CONTA = {
    "IND-CONTA_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
TF2 = {
    "IND-TF2_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
CX = {
    "IND-CX_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
ROLL = {
    "IND-ROLL_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
CY = {
    "IND-CY_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}
BKG = {
    "IND-BKG_CHEOPS_inst": {"polynomial": {"do": False, "order": 0, "tref": None}},
    "all": {"polynomial": {"do": False, "order": 0, "tref": None}},
}

#########################
## Noise model definition
#########################

# Noise model for intrument model
#################################
# Define which noise model you want to use for each instrument model
# By default the gaussian noise model is used for all the instrument models
# This is imposed by the fact that below all instrument models have 'gaussian' as entry.
# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].
# If you want to change the noise model used for a given instrument model, just change the value of its key.
# For indicator (IND) instrument models, you can provide None and the model will not try to model the data associated to this instrument.
d_noise_model_def = {"LC": {"CHEOPS": {f"inst{ii}": "gaussian" for ii in l_idxdst_all}}}
for ind in l_IND:
    d_noise_model_def[f"IND-{ind}"] = {"CHEOPS": {"inst": None}}

# Gaussian noise models
#######################
gaussian_models = {}

for ii in l_idxdst_all:
    gaussian_models[f"LC_{instrument}_inst{ii}"] = {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    }

###########################
## Parameters configuration
###########################

# The list of main parameter full names in the model is:
# ['LC_CHEOPS_inst0_contam', 'LC_CHEOPS_inst0_DeltaF', 'LC_CHEOPS_inst0_drift1', 'LC_CHEOPS_inst0_jitter', 'A_rho', 'b_P', 'b_cosinc', 'b_tic', 'b_Rrat', 'b_ecosw', 'b_esinw', 'A_LDC_ldc1', 'A_LDC_ldc2', 'A_LDC_ldc3', 'A_LDC_ldc4']

# Duplicate parameters
######################
# Indicates in the duplicates dictionary which parameters you want to be seen being duplicates of another parameters
# Format: keys are the full name of main parameters that you want to be duplicated.
# Values are the list of main parameters full names that you want to be duplicates of the parameter named by the corresponding key.
duplicates = {}

# For multiple visit the contamination is assumed to be the same
# duplicates = {
#     f"LC_{instrument}_inst0_contam": [],
# }
# for ii in l_idxdst_all:
#     if ii != 0:
#         duplicates[f"LC_{instrument}_inst0_contam"].append(
#             f"LC_{instrument}_inst{ii}_contam"
#         )

# Frozen parameters
###################
# Indicates the list the main parameters full names that you want to freeze.
# A frozen parameter will have its value fixed to a given value that you will define in the next step.
frozens = []

# Indicates the values for the frozens main parameters
# You should not change the unit value. Every changes that you might make to unit will be ignored.
frozen_values = {}

# Joint Priors
##############
# The units are provided as information and you should not change it. Any change will be ignored.
#
# These priors convert a given set of jumping parameter into a different set of parameters that
# can be better suited to define priors.
# The list of available joint priors is:
planet_parameters_file = "../priors/planet_parameters.json"
logger.info(f"Using planet parameter file: {planet_parameters_file}")
with open(planet_parameters_file) as f:
    planet_parameters = json.load(f)

joint_priors = {
    "polar_ew": {
        "category": "polar",
        "args": {
            "r_prior": {
                "category": "uniform",
                "args": {"vmin": 0, "vmax": planet_parameters["ecc_Upperlimit"]},
            },  # Artificial upper limit
            "theta_prior": {
                "category": "uniform",
                "args": {"vmin": -np.pi, "vmax": np.pi},
            },
        },
        "params": {"x": "b_ecosw", "y": "b_esinw"},
    },
}

# Individual Priors
###################
# The units are provided as information and you should not change it. Any change will be ignored.
#
# The list of available individual priors is:
stellar_parameters_file = "../priors/stellar_parameters.json"
logger.info(f"Using stellar parameter file: {stellar_parameters_file}")
with open(stellar_parameters_file) as f:
    stellar_parameters = json.load(f)

# Compute A_rho prior
rho_Sun_gcmm3 = ((3 * uu.M_sun) / (4 * np.pi * uu.R_sun**3)).to(uu.g / uu.cm**3).value
rho_mu = stellar_parameters["rho"] / rho_Sun_gcmm3
rho_std = stellar_parameters["rho_err"] / rho_Sun_gcmm3
logger.info(f"Stellar density = {rho_mu} +/- {rho_std} solar density")

# Set the T0 as the time of the last transit visit
tics = {}
T0_BTJD = planet_parameters["tic"] - 2457000.0  # to convert in BTJD
for idxdst in l_idxdst_all:
    df_flux = pd.read_table(
        os.path.join(data_folder, f"LC_{object_name}_CHEOPS_{idxdst}.txt"),
        sep=r"\s+",
        comment="#",
    )
    time_dst_mean = np.mean(df_flux["time"])
    epoch_sinceTO = np.round((time_dst_mean - T0_BTJD) / planet_parameters["period"])
    tics[idxdst] = {
        "mu": T0_BTJD + epoch_sinceTO * planet_parameters["period"],
        "sigma": planet_parameters["tic_err"] + epoch_sinceTO * planet_parameters["period_err"],
        "epoch": epoch_sinceTO,
    }

# Set the prior parameters on cosinc
inc = planet_parameters["inc"]
inc_err = planet_parameters["inc_err"]
cosinc_samples = np.cos(
    np.random.normal(loc=np.deg2rad(inc), scale=np.deg2rad(inc_err), size=10000)
)
cosinc = np.median(cosinc_samples)
cosinc_std = np.std(cosinc_samples)

individual_priors = {
    "GP1D": {},
    "LDs": {},
    "instruments": {},
    "planets": {
        "b": {
            "P": {
                "args": {
                    "mu": planet_parameters["period"],
                    "sigma": planet_parameters["period_err"],
                },
                "category": "normal",
                "unit": None,
            },
            "Rrat": {
                "args": {
                    "mu": planet_parameters["Rrat"],
                    "sigma": planet_parameters["Rrat_err"],
                    "lims": [0, 1],
                },
                "category": "normal",
                "unit": None,
            },
            "cosinc": {
                "args": {"mu": cosinc, "sigma": cosinc_std, "lims": [0, 1]},
                "category": "normal",
                "unit": "w/o unit",
            },
        }
    },
    "stars": {
        "A": {
            "rho": {
                "args": {
                    "mu": rho_mu,
                    "sigma": rho_std,
                    "lims": [0, 10],
                },
                "category": "normal",
                "unit": None,
            }
        }
    },
    "sys_WASP-43": {},
}

# Tic priors
for idxdst in l_idxdst_all:
    individual_priors["planets"]["b"][f"tic{idxdst}"] = {
        "args": {
            "mu": tics[idxdst]["mu"],
            "sigma": tics[idxdst]["sigma"],
        },
        "category": "normal",
        "unit": None,
    }

# LDC priors
LDC_file = "../priors/LDC_coeff.json"
logger.info(f"Using LDC file: {LDC_file}")
with open(LDC_file) as f:
    LDC_parameters = json.load(f)

for inst_name, LD_mode_name, filter_name in zip(
    ["CHEOPS"],
    [
        "A_LDC",
    ],
    [
        "CHEOPS",
    ],
):
    star_name, LDonly_model = LD_mode_name.split("_")
    individual_priors["LDs"][LD_mode_name] = {}
    qc = LDC_parameters[filter_name][LDs[star_name]["LD_models"][LDonly_model]]["qc"]
    qe = LDC_parameters[filter_name][LDs[star_name]["LD_models"][LDonly_model]]["qe"]
    for jj, c, e in zip(range(len(qc)), qc, qe, strict=True):
        individual_priors["LDs"][LD_mode_name][f"ldc{jj + 1}"] = {
            "args": {"mu": c, "sigma": e},
            "category": "normal",
            "unit": None,
        }
        logger.debug(
            f"{LD_mode_name}: ldc{jj + 1} prior {individual_priors['LDs'][LD_mode_name][f'ldc{jj + 1}']}"
        )

# Instrument priors
# Indicators
for ind in l_IND:
    individual_priors["instruments"][f"IND-{ind}"] = {"CHEOPS": {"inst": {}}}

# LCS
individual_priors["instruments"]["LC"] = {instrument: {}}

all_contas = []
for ii in l_idxdst_all:
    all_contas.append(
        pd.read_table(
            os.path.join(data_folder, f"IND-CONTA_{object_name}_{instrument}_{ii}.txt"),
            sep=r"\s+",
            comment="#",
        )["CONTA"]
    )
all_contas = np.concatenate(all_contas)
all_contas = all_contas / (1 + all_contas)

for ii in l_idxdst_all:
    individual_priors["instruments"]["LC"][instrument][f"inst{ii}"] = {}
    individual_priors["instruments"]["LC"][instrument][f"inst{ii}"]["DeltaF"] = {
        "args": {
            "mu": (df_fluxs[ii]["flux"].median() - 1) + np.median(all_contas),
            "sigma": np.sqrt(
                sp.stats.median_abs_deviation(df_fluxs[ii]["flux"]) ** 2
                + sp.stats.median_abs_deviation(all_contas) ** 2
            ),
            "sigma_lims": [3, 3],
        },
        "category": "normal",
        "unit": "wo unit",
    }
    logger.debug(
        f"{ii}: DeltaF prior {individual_priors['instruments']['LC'][instrument][f'inst{ii}']['DeltaF']}"
    )
    individual_priors["instruments"]["LC"][instrument][f"inst{ii}"]["drift1"] = {
        "args": {
            "mu": 0.0,
            "sigma": df_fluxs[ii]["flux"].std()
            / (df_fluxs[ii]["time"].max() - df_fluxs[ii]["time"].min()),
        },
        "category": "normal",
        "unit": "[LC data unit].s^(-1)",
    }
    logger.debug(
        f"{ii}: drift1 prior {individual_priors['instruments']['LC'][instrument][f'inst{ii}']['drift1']}"
    )
    individual_priors["instruments"]["LC"][instrument][f"inst{ii}"]["jitter"] = {
        "args": {"vmax": np.median(df_fluxs[ii]["flux_err"]) * 5, "vmin": 0.0},
        "category": "uniform",
        "unit": "wo unit",
    }
    logger.debug(
        f"{ii}: jitter prior {individual_priors['instruments']['LC'][instrument][f'inst{ii}']['jitter']}"
    )

individual_priors["instruments"]["LC"][instrument]["inst0"]["contam"] = {
    "args": {
        "mu": np.median(all_contas),
        "sigma": sp.stats.median_abs_deviation(all_contas),
    },
    "category": "normal",
    "unit": "wo unit",
}
logger.debug(
    f"{ii}: contamination prior {individual_priors['instruments']['LC'][instrument]['inst0']['contam']}"
)
