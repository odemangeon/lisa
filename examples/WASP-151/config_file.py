# Configuration file for LISA analysis.
import json
import os

import numpy as np
import pandas as pd

##############
## Object name
##############
# Give a name to the object that you are studying. DO NOT use _

object_name = "WASP-151"

##########
## Folders
##########

run_folder = "."

data_folder = "data"


###########
## Datasets
###########

# List of the paths to the dataset files that you want to use
l_dataset: list[str] = [
    "LC_WASP-151_K2.txt",
    "LC_WASP-151_EulerCam.txt",
    "LC_WASP-151_EulerCam_1.txt",
    "LC_WASP-151_IAC80.txt",
    "LC_WASP-151_IAC80_1.txt",
    "LC_WASP-151_TRAPPIST.txt",
    "RV_WASP-151_SOPHIE.txt",
    "RV_WASP-151_CORALIE.txt",
]

##############################
## Instrument model definition
##############################
# Define which instrument model you want to use for each dataset
# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument
# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.
# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0').
d_inst_model_def = {
    "LC": {
        "EulerCam": {"0": "inst0", "1": "inst1"},
        "IAC80": {"0": "inst0", "1": "inst1"},
        "K2": {"0": "inst"},
        "TRAPPIST": {"0": "inst"},
    },
    "RV": {"CORALIE": {"0": "inst"}, "SOPHIE": {"0": "inst"}},
}

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
    "b": {
        "do": True,
        "model4instrument": {
            "LC_EulerCam_inst0": "",
            "LC_EulerCam_inst1": "",
            "LC_IAC80_inst0": "",
            "LC_IAC80_inst1": "",
            "LC_K2_inst": "",
            "LC_TRAPPIST_inst": "",
            "RV_CORALIE_inst": "",
            "RV_SOPHIE_inst": "",
        },
        "model_definitions": {
            "": {
                "category": "batman",
                "param_extensions": {
                    "planet": {"P": "", "cosinc": "", "ecosw": "", "esinw": "", "tic": ""},
                    "star": {"rho": ""},
                },
                "parametrisation": {
                    "ew_format": "ecosw-esinw",
                    "inc_format": "cosinc",
                    "use_aR": False,
                    "use_tic": True,
                },
            }
        },
    }
}

#############################
## Configuration of RV models
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
# {'RV_SOPHIE_inst': ['RV_WASP-151_SOPHIE_0'], 'RV_CORALIE_inst': ['RV_WASP-151_CORALIE_0']}
#
# The list of datasets for each IND instrument model are:
# {}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}
# bispline: {'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}


# Decorrelation Model
#####################
decorrelation_model_RV = {
    "RV_CORALIE_inst": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalrv": {"linear": {}},
            "multiply_2_totalrv": {"linear": {}},
        },
    },
    "RV_SOPHIE_inst": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalrv": {"linear": {}},
            "multiply_2_totalrv": {"linear": {}},
        },
    },
}

# Decorrelation likelihood
##########################
decorrelation_likelihood_RV = {"do": False, "model_definitions": {}, "order_models": []}


# Keplerian RV model
####################
keplerian_rv_model = {
    "b": {
        "do": True,
        "model": {"category": "radvel", "param_extensions": {"planet": {"K": ""}, "star": {}}},
    }
}

# Instrumental model for RV
###########################

# Polynomial trend models for RV
################################
polynomial_model_RV = {
    "A": {"do": True, "order": 0, "tref": None},
    "RV_CORALIE_inst": {"do": True, "order": 0, "tref": None},
    "RV_SOPHIE_inst": {"do": False, "order": 0, "tref": None},
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
# {'LC_TRAPPIST_inst': ['LC_WASP-151_TRAPPIST_0'], 'LC_K2_inst': ['LC_WASP-151_K2_0'], 'LC_IAC80_inst1': ['LC_WASP-151_IAC80_1'], 'LC_IAC80_inst0': ['LC_WASP-151_IAC80_0'], 'LC_EulerCam_inst0': ['LC_WASP-151_EulerCam_0'], 'LC_EulerCam_inst1': ['LC_WASP-151_EulerCam_1']}
#
# The list of datasets for each IND instrument model are:
# {}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}
# bispline: {'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}


# Decorrelation Model
#####################
decorrelation_model_LC = {
    "LC_EulerCam_inst0": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
    "LC_EulerCam_inst1": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
    "LC_IAC80_inst0": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
    "LC_IAC80_inst1": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
    "LC_K2_inst": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
    "LC_TRAPPIST_inst": {
        "do": False,
        "what to decorrelate": {
            "add_2_totalflux": {"linear": {}},
            "multiply_2_totalflux": {"linear": {}},
        },
    },
}

# Decorrelation likelihood
##########################
decorrelation_likelihood_LC = {"do": False, "model_definitions": {}, "order_models": []}

# Transit model
################
transit_model = {
    "b": {
        "do": True,
        "model4instrument": {
            "LC_EulerCam_inst0": "",
            "LC_EulerCam_inst1": "",
            "LC_IAC80_inst0": "",
            "LC_IAC80_inst1": "",
            "LC_K2_inst": "",
            "LC_TRAPPIST_inst": "",
        },
        "model_definitions": {
            "": {
                "args": {"TransitModel_kwargs": {}},
                "category": "batman",
                "param_extensions": {"planet": {"Rrat": ""}, "star": {}},
            }
        },
    }
}

# Limb-darkening.
#################
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {
    "A": {
        "LC_K2_inst": "LDKp",
        "LC_EulerCam_inst0": "LDNG",
        "LC_EulerCam_inst1": "LDNG",
        "LC_TRAPPIST_inst": "LDz",
        "LC_IAC80_inst1": "LDR",
        "LC_IAC80_inst0": "LDR",
        "LD_models": {
            "LDKp": "quadratic",
            "LDNG": "quadratic",
            "LDR": "quadratic",
            "LDz": "quadratic",
        },
    }
}

# Phase curve model
####################
phasecurve_model = {
    "b": {
        "do": False,
        "model4instrument": {
            "LC_EulerCam_inst0": [""],
            "LC_EulerCam_inst1": [""],
            "LC_IAC80_inst0": [""],
            "LC_IAC80_inst1": [""],
            "LC_K2_inst": [""],
            "LC_TRAPPIST_inst": [""],
        },
        "model_definitions": {
            "": {
                "args": {
                    "factor_period": 1,
                    "flux_offset": "param",
                    "occultation": True,
                    "phase_offset": "param",
                    "sincos": "cos",
                },
                "category": "sincos",
                "param_extensions": {
                    "planet": {"A": "", "Foffset": "", "Phi": "", "Rrat": ""},
                    "star": {},
                },
            }
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
            "LC_EulerCam_inst0": "",
            "LC_EulerCam_inst1": "",
            "LC_IAC80_inst0": "",
            "LC_IAC80_inst1": "",
            "LC_K2_inst": "",
            "LC_TRAPPIST_inst": "",
        },
        "model_definitions": {
            "": {
                "category": "batman",
                "param_extensions": {"planet": {"Frat": "", "Rrat": ""}, "star": {}},
            }
        },
    }
}

# Supersampling and exposure_time for LC
########################################
SuperSamps_LC = {
    "LC_TRAPPIST_inst": {"supersamp": 10, "exptime": 0.02043402778},
    "LC_K2_inst": {"supersamp": 1, "exptime": 0.02043402778},
    "LC_IAC80_inst1": {"supersamp": 1, "exptime": 0.02043402778},
    "LC_IAC80_inst0": {"supersamp": 1, "exptime": 0.02043402778},
    "LC_EulerCam_inst0": {"supersamp": 1, "exptime": 0.02043402778},
    "LC_EulerCam_inst1": {"supersamp": 1, "exptime": 0.02043402778},
}

# Instrumental model for LC
###########################

# Polynomial trend models for LC
################################
polynomial_model_LC = {
    "A": {"do": False, "order": 0, "tref": None},
    "LC_EulerCam_inst0": {"do": True, "order": 0, "tref": None},
    "LC_EulerCam_inst1": {"do": True, "order": 0, "tref": None},
    "LC_IAC80_inst0": {"do": True, "order": 0, "tref": None},
    "LC_IAC80_inst1": {"do": True, "order": 0, "tref": None},
    "LC_K2_inst": {"do": True, "order": 0, "tref": None},
    "LC_TRAPPIST_inst": {"do": True, "order": 0, "tref": None},
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
d_noise_model_def = {
    "LC": {
        "EulerCam": {"inst0": "gaussian", "inst1": "gaussian"},
        "IAC80": {"inst0": "gaussian", "inst1": "gaussian"},
        "K2": {"inst": "GP1D"},
        "TRAPPIST": {"inst": "gaussian"},
    },
    "RV": {"CORALIE": {"inst": "GP1D"}, "SOPHIE": {"inst": "GP1D"}},
}

# GP1D noise models
###################
GP1D_models = {
    "GPmodel4instrument": {"LC_K2_inst": "LC", "RV_CORALIE_inst": "RV", "RV_SOPHIE_inst": "RV"},
    "GPmodel_definitions": {
        "LC": {
            "category": "SHOCelerite",
            "param_extensions": {"GP": {"A": "", "rho": "", "Q": ""}},
            "parametrisation": {
                "use_rho": True,
                "use_Q": True,
                "use_A": True,
                "log10": {"rho/omega0": False, "Q/tau": False, "A/S0": False},
            },
        },
        "RV": {
            "category": "QPGeorge",
            "param_extensions": {"GP": {"A": "", "P": "", "gamma": "", "tau": ""}},
            "parametrisation": {"log10": {"A": False, "P": False, "gamma": False, "tau": False}},
        },
    },
    "jittermodel_definitions": {
        "LC_K2_inst": {
            "args": {"jitter_type": "additive"},
            "param_extensions": {"instrument": {"jitter": ""}},
            "parametrisation": {"log10": False, "use_Baluevfactor": False},
        },
        "RV_CORALIE_inst": {
            "args": {"jitter_type": "additive"},
            "param_extensions": {"instrument": {"jitter": ""}},
            "parametrisation": {"log10": False, "use_Baluevfactor": False},
        },
        "RV_SOPHIE_inst": {
            "args": {"jitter_type": "additive"},
            "param_extensions": {"instrument": {"jitter": ""}},
            "parametrisation": {"log10": False, "use_Baluevfactor": False},
        },
    },
}

# Gaussian noise models
#######################
gaussian_models = {
    "LC_EulerCam_inst0": {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
    "LC_EulerCam_inst1": {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
    "LC_IAC80_inst0": {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
    "LC_IAC80_inst1": {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
    "LC_TRAPPIST_inst": {
        "args": {"jitter_type": "additive"},
        "param_extensions": {"instrument": {"jitter": ""}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
}

###########################
## Parameters configuration
###########################

# The list of main parameter full names in the model is:
# ['LC_TRAPPIST_inst_contam', 'LC_TRAPPIST_inst_DeltaF', 'LC_TRAPPIST_inst_jitter', 'LC_K2_inst_contam', 'LC_K2_inst_DeltaF', 'LC_K2_inst_jitter', 'RV_SOPHIE_inst_DeltaRV', 'RV_SOPHIE_inst_jitter', 'LC_IAC80_inst1_contam', 'LC_IAC80_inst1_DeltaF', 'LC_IAC80_inst1_jitter', 'LC_EulerCam_inst0_contam', 'LC_EulerCam_inst0_DeltaF', 'LC_EulerCam_inst0_jitter', 'LC_IAC80_inst0_contam', 'LC_IAC80_inst0_DeltaF', 'LC_IAC80_inst0_jitter', 'LC_EulerCam_inst1_contam', 'LC_EulerCam_inst1_DeltaF', 'LC_EulerCam_inst1_jitter', 'RV_CORALIE_inst_DeltaRV', 'RV_CORALIE_inst_jitter', 'LC_A', 'LC_P', 'LC_tau', 'LC_gamma', 'RV_A', 'RV_P', 'RV_tau', 'RV_gamma', 'A_rho', 'A_v0', 'b_P', 'b_cosinc', 'b_tic', 'b_K', 'b_Rrat', 'b_ecosw', 'b_esinw', 'A_LDKp_ldc1', 'A_LDKp_ldc2', 'A_LDNG_ldc1', 'A_LDNG_ldc2', 'A_LDR_ldc1', 'A_LDR_ldc2', 'A_LDz_ldc1', 'A_LDz_ldc2']

# Duplicate parameters
######################
# Indicates in the duplicates dictionary which parameters you want to be seen being duplicates of another parameters
# Format: keys are the full name of main parameters that you want to be duplicated.
# Values are the list of main parameters full names that you want to be duplicates of the parameter named by the corresponding key.
duplicates = {
    "LC_EulerCam_inst0_jitter": [
        "LC_EulerCam_inst1_jitter",
    ],
    "LC_rho": [
        "RV_P",
    ],
}

# Frozen parameters
###################
# Indicates the list the main parameters full names that you want to freeze.
# A frozen parameter will have its value fixed to a given value that you will define in the next step.
frozens = [
    "LC_TRAPPIST_inst_contam",
    "LC_K2_inst_contam",
    "RV_SOPHIE_inst_DeltaRV",
    "LC_IAC80_inst1_contam",
    "LC_EulerCam_inst0_contam",
    "LC_IAC80_inst0_contam",
    "LC_EulerCam_inst1_contam",
]

# Indicates the values for the frozens main parameters
# You should not change the unit value. Every changes that you might make to unit will be ignored.
frozen_values = {
    "LC_EulerCam_inst0_contam": {"unit": "wo unit", "value": 0},
    "LC_EulerCam_inst1_contam": {"unit": "wo unit", "value": 0},
    "LC_IAC80_inst0_contam": {"unit": "wo unit", "value": 0},
    "LC_IAC80_inst1_contam": {"unit": "wo unit", "value": 0},
    "LC_K2_inst_contam": {"unit": "wo unit", "value": 0},
    "LC_TRAPPIST_inst_contam": {"unit": "wo unit", "value": 0},
    "RV_SOPHIE_inst_DeltaRV": {"unit": "[RV data unit]", "value": 0.0},
}

# Joint Priors
##############
# The units are provided as information and you should not change it. Any change will be ignored.
#
# These priors convert a given set of jumping parameter into a different set of parameters that
# can be better suited to define priors.
# The list of available joint priors is:

# Compute rhostar prior from M and R
filepath_stellar_parameters = "stellar_parameters_WASP151.json"
with open(filepath_stellar_parameters) as f:
    stellar_parameters = json.load(f)

M_A_mean = stellar_parameters["mass"]
M_A_err = stellar_parameters["e_mass"]
M_A_samples = np.random.normal(loc=M_A_mean, scale=M_A_err, size=10000)
R_A_mean = stellar_parameters["radius"]
R_A_err = stellar_parameters["e_radius"]
R_A_samples = np.random.normal(loc=R_A_mean, scale=R_A_err, size=10000)
rho_A_samples = M_A_samples / R_A_samples**3

joint_priors = {
    "polar_ew": {
        "category": "polar",
        "args": {
            "r_prior": {
                "category": "uniform",
                "args": {"vmin": 0.0, "vmax": 0.1},
            },  # from Knutson+2014
            "theta_prior": {
                "category": "uniform",
                "args": {"vmin": np.deg2rad(-180), "vmax": np.deg2rad(180)},
            },
        },
        "params": {"x": "b_ecosw", "y": "b_esinw"},
    },
    "transiting": {
        "category": "transiting_rho",
        "args": {
            "rhostar_prior": {
                "category": "normal",
                "args": {
                    "mu": np.median(rho_A_samples),
                    "sigma": np.std(rho_A_samples),
                    "lims": [0, 2],
                },
            },
            "P_prior": [
                {
                    "category": "normal",
                    "args": {"mu": 4.5334, "sigma": 0.003},
                }
            ],
            "Phi_prior": [
                {
                    "category": "normal",
                    "args": {"mu": 0, "sigma": 0.005 / 4.5334},
                }
            ],
            "b_prior": [
                {
                    "category": "uniform",
                    "args": {"vmin": 0, "vmax": 1},
                }
            ],
            "Rrat_prior": [
                {
                    "category": "normal",
                    "args": {"mu": 0.097, "sigma": 0.01},
                }
            ],
            "t_ref": [57741.00885442065],
            "transiting": [True],
            "allow_grazing": [True],
        },
        "params": {
            "rhostar": "A_rho",
            "P": ["b_P"],
            "tic": ["b_tic"],
            "cosinc": ["b_cosinc"],
            "Rrat": ["b_Rrat"],
        },
    },
}

# Individual Priors
###################
# The units are provided as information and you should not change it. Any change will be ignored.
#
# The list of available individual priors is:


df_fluxs: dict[str, dict[str, pd.DataFrame]] = {}
for instrument, ii in [
    ("K2", "0"),
    ("EulerCam", "0"),
    ("EulerCam", "1"),
    ("IAC80", "0"),
    ("IAC80", "1"),
    ("TRAPPIST", "0"),
]:
    if instrument not in df_fluxs:
        df_fluxs[instrument] = {}
    if ii == "0":
        file_name = f"LC_{object_name}_{instrument}.txt"
    else:
        file_name = f"LC_{object_name}_{instrument}_{ii}.txt"
    df_fluxs[instrument][ii] = pd.read_table(
        os.path.join(data_folder, file_name),
        sep=r"\s+",
        comment="#",
    )


df_RVs: dict[str, pd.DataFrame] = {}
for instrument in ["SOPHIE", "CORALIE"]:
    df_RVs[instrument] = pd.read_table(
        os.path.join(data_folder, f"RV_{object_name}_{instrument}.txt"), sep=r"\s+", comment="#"
    )

individual_priors = {
    "GP1D": {
        "LC": {
            "A": {"args": {"vmax": 0.01, "vmin": 0.0}, "category": "uniform", "unit": None},
            "rho": {"args": {"vmax": 100.0, "vmin": 1.0}, "category": "uniform", "unit": None},
            "Q": {"args": {"vmax": 10, "vmin": 0.1}, "category": "uniform", "unit": None},
        },
        "RV": {
            "A": {"args": {"vmax": 0.1, "vmin": 0.0}, "category": "uniform", "unit": None},
            "gamma": {"args": {"vmax": 5.0, "vmin": 0.05}, "category": "uniform", "unit": None},
            "tau": {"args": {"vmax": 100.0, "vmin": 1.0}, "category": "uniform", "unit": None},
        },
    },
    "LDs": {
        "A_LDKp": {
            "ldc1": {"args": {"mu": 0.5501, "sigma": 0.0025}, "category": "normal", "unit": None},
            "ldc2": {"args": {"mu": 0.1191, "sigma": 0.0054}, "category": "normal", "unit": None},
        },
        "A_LDNG": {
            "ldc1": {"args": {"mu": 0.4861, "sigma": 0.0021}, "category": "normal", "unit": None},
            "ldc2": {"args": {"mu": 0.4861, "sigma": 0.0021}, "category": "normal", "unit": None},
        },
        "A_LDR": {
            "ldc1": {"args": {"mu": 0.4781, "sigma": 0.0022}, "category": "normal", "unit": None},
            "ldc2": {"args": {"mu": 0.1304, "sigma": 0.0055}, "category": "normal", "unit": None},
        },
        "A_LDz": {
            "ldc1": {"args": {"mu": 0.3412, "sigma": 0.0013}, "category": "normal", "unit": None},
            "ldc2": {"args": {"mu": 0.1269, "sigma": 0.0039}, "category": "normal", "unit": None},
        },
    },
    "instruments": {
        "LC": {
            "EulerCam": {
                "inst0": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["EulerCam"]["0"]["flux"].median() - 1,
                            "sigma": df_fluxs["EulerCam"]["0"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                    "jitter": {
                        "args": {
                            "vmax": df_fluxs["EulerCam"]["0"]["flux_err"].median() * 5,
                            "vmin": 0.0,
                        },
                        "category": "uniform",
                        "unit": None,
                    },
                },
                "inst1": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["EulerCam"]["1"]["flux"].median() - 1,
                            "sigma": df_fluxs["EulerCam"]["1"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                },
            },
            "IAC80": {
                "inst0": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["IAC80"]["0"]["flux"].median() - 1,
                            "sigma": df_fluxs["IAC80"]["0"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                    "jitter": {
                        "args": {
                            "vmax": df_fluxs["IAC80"]["0"]["flux_err"].median() * 5,
                            "vmin": 0.0,
                        },
                        "category": "uniform",
                        "unit": None,
                    },
                },
                "inst1": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["IAC80"]["1"]["flux"].median() - 1,
                            "sigma": df_fluxs["IAC80"]["1"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                    "jitter": {
                        "args": {
                            "vmax": df_fluxs["IAC80"]["1"]["flux_err"].median() * 5,
                            "vmin": 0.0,
                        },
                        "category": "uniform",
                        "unit": None,
                    },
                },
            },
            "K2": {
                "inst": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["K2"]["0"]["flux"].median() - 1,
                            "sigma": df_fluxs["K2"]["0"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                    "jitter": {
                        "args": {"vmax": df_fluxs["K2"]["0"]["flux_err"].median() * 5, "vmin": 0.0},
                        "category": "uniform",
                        "unit": None,
                    },
                }
            },
            "TRAPPIST": {
                "inst": {
                    "DeltaF": {
                        "args": {
                            "mu": df_fluxs["TRAPPIST"]["0"]["flux"].median() - 1,
                            "sigma": df_fluxs["TRAPPIST"]["0"]["flux"].std(),
                        },
                        "category": "normal",
                        "unit": "wo unit",
                    },
                    "jitter": {
                        "args": {
                            "vmax": df_fluxs["TRAPPIST"]["0"]["flux_err"].median() * 5,
                            "vmin": 0.0,
                        },
                        "category": "uniform",
                        "unit": None,
                    },
                }
            },
        },
        "RV": {
            "CORALIE": {
                "inst": {
                    "DeltaRV": {
                        "args": {
                            "mu": np.median(df_RVs["CORALIE"]["RV"])
                            - np.median(df_RVs["SOPHIE"]["RV"]),
                            "sigma": np.sqrt(
                                np.var(df_RVs["CORALIE"]["RV"]) + np.var(df_RVs["SOPHIE"]["RV"])
                            ),
                        },
                        "category": "normal",
                        "unit": "[RV data unit]",
                    },
                    "jitter": {
                        "args": {"vmax": 5 * np.std(df_RVs["CORALIE"]["RV_err"]), "vmin": 0.0},
                        "category": "uniform",
                        "unit": None,
                    },
                }
            },
            "SOPHIE": {
                "inst": {
                    "jitter": {
                        "args": {"vmax": 5 * np.std(df_RVs["SOPHIE"]["RV_err"]), "vmin": 0.0},
                        "category": "uniform",
                        "unit": None,
                    }
                }
            },
        },
    },
    "planets": {
        "b": {
            "K": {"args": {"vmax": 0.1, "vmin": 0.0}, "category": "uniform", "unit": None},
            "tic": {
                "args": {"mu": 57741.00885442065, "sigma": 0.1},
                "category": "normal",
                "unit": None,
            },
        }
    },
    "stars": {
        "A": {
            "v0": {
                "args": {
                    "mu": df_RVs["SOPHIE"]["RV"].median(),
                    "sigma": df_RVs["SOPHIE"]["RV"].std(),
                },
                "category": "normal",
                "unit": None,
            },
        }
    },
    "sys_WASP-151": {},
}
