# Configuration file for the analysis of WASP-151.

###########
## Datasets
###########

# List of the paths to the dataset files that you want to use
l_dataset = ["LC_WASP-151_K2.txt",
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
d_inst_model_def = {'LC': {'EulerCam': {'0': 'inst0', '1': 'inst1'},
                           'IAC80': {'0': 'inst0', '1': 'inst1'},
                           'K2': {'0': 'inst'},
                           'TRAPPIST': {'0': 'inst'}},
                    'RV': {'CORALIE': {'0': 'inst'}, 'SOPHIE': {'0': 'inst'}}}

####################################
## Model category definition
####################################
# Define the model category and the parameters of the model that are specfic to the model category.

# Available model categories are ['GravitionalGroups', 'GravitionalGroupsDynamic']
model_category = 'GravitionalGroups'

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
orbital_model = {'b': {'do': True,
                       'model4instrument': {'LC_EulerCam_inst0': '',
                                            'LC_EulerCam_inst1': '',
                                            'LC_IAC80_inst0': '',
                                            'LC_IAC80_inst1': '',
                                            'LC_K2_inst': '',
                                            'LC_TRAPPIST_inst': '',
                                            'RV_CORALIE_inst': '',
                                            'RV_SOPHIE_inst': ''},
                       'model_definitions': {'': {'category': 'batman',
                                                  'param_extensions': {'planet': {'P': '',
                                                                                  'cosinc': '',
                                                                                  'ecosw': '',
                                                                                  'esinw': '',
                                                                                  'tic': ''},
                                                                       'star': {'rho': ''}},
                                                  'parametrisation': {'ew_format': 'ecosw-esinw',
                                                                      'inc_format': 'cosinc',
                                                                      'use_aR': False,
                                                                      'use_tic': True}}}}}

#########################
## Noise model definition
#########################
# Define which noise model you want to use for each instrument model
# By default the gaussian noise model is used for all the instrument models
# This is imposed by the fact that below all instrument models have 'gaussian' as entry.
# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].
# If you want to change the noise model used for a given instrument model, just change the value of its key.
d_noise_model_def = {'LC': {'EulerCam': {'inst0': 'gaussian', 'inst1': 'gaussian'},
                            'IAC80': {'inst0': 'gaussian', 'inst1': 'gaussian'},
                            'K2': {'inst': 'GP1D'},
                            'TRAPPIST': {'inst': 'gaussian'}},
                     'RV': {'CORALIE': {'inst': 'GP1D'}, 'SOPHIE': {'inst': 'GP1D'}}}

#############################
## Configuration of LC models
#############################


# Decorrelation LC
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
# {'LC_K2_inst': ['LC_WASP-151_K2_0'], 'LC_EulerCam_inst0': ['LC_WASP-151_EulerCam_0'], 'LC_EulerCam_inst1': ['LC_WASP-151_EulerCam_1'], 'LC_TRAPPIST_inst': ['LC_WASP-151_TRAPPIST_0'], 'LC_IAC80_inst1': ['LC_WASP-151_IAC80_1'], 'LC_IAC80_inst0': ['LC_WASP-151_IAC80_0']}
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
decorrelation_model_LC = {'LC_EulerCam_inst0': {'do': False,
                                             'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                     'multiply_2_totalflux': {'linear': {}}}},
                       'LC_EulerCam_inst1': {'do': False,
                                             'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                     'multiply_2_totalflux': {'linear': {}}}},
                       'LC_IAC80_inst0': {'do': False,
                                          'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                  'multiply_2_totalflux': {'linear': {}}}},
                       'LC_IAC80_inst1': {'do': False,
                                          'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                  'multiply_2_totalflux': {'linear': {}}}},
                       'LC_K2_inst': {'do': False,
                                      'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                              'multiply_2_totalflux': {'linear': {}}}},
                       'LC_TRAPPIST_inst': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}}}

# Decorrelation likelihood
##########################
decorrelation_likelihood_LC = {'do': False, 'model_definitions': {}, 'order_models': []}

# Transit model
################
transit_model = {'b': {'do': True,
                       'model4instrument': {'LC_EulerCam_inst0': '',
                                            'LC_EulerCam_inst1': '',
                                            'LC_IAC80_inst0': '',
                                            'LC_IAC80_inst1': '',
                                            'LC_K2_inst': '',
                                            'LC_TRAPPIST_inst': ''},
                       'model_definitions': {'': {'category': 'batman',
                                                  'param_extensions': {'planet': {'Rrat': ''},
                                                                       'star': {}}}}}}

# Limb-darkening.
#################
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {'A': {'LC_K2_inst': 'default',
             'LC_EulerCam_inst0': 'default',
             'LC_EulerCam_inst1': 'default',
             'LC_TRAPPIST_inst': 'default',
             'LC_IAC80_inst1': 'default',
             'LC_IAC80_inst0': 'default',

             'LD_models': {'default': 'quadratic'}
             }
       }

# Phase curve model
####################
phasecurve_model = {'b': {'do': False,
                          'model4instrument': {'LC_EulerCam_inst0': [''],
                                               'LC_EulerCam_inst1': [''],
                                               'LC_IAC80_inst0': [''],
                                               'LC_IAC80_inst1': [''],
                                               'LC_K2_inst': [''],
                                               'LC_TRAPPIST_inst': ['']},
                          'model_definitions': {'': {'args': {'factor_period': 1,
                                                              'flux_offset': 'param',
                                                              'occultation': True,
                                                              'phase_offset': 'param',
                                                              'sincos': 'cos'},
                                                     'category': 'sincos',
                                                     'param_extensions': {'planet': {'A': '',
                                                                                     'Foffset': '',
                                                                                     'Phi': '',
                                                                                     'Rrat': ''},
                                                                          'star': {}}}}}}

# Occultation model
####################
# WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
occultation_model = {'b': {'do': False,
                           'model4instrument': {'LC_EulerCam_inst0': '',
                                                'LC_EulerCam_inst1': '',
                                                'LC_IAC80_inst0': '',
                                                'LC_IAC80_inst1': '',
                                                'LC_K2_inst': '',
                                                'LC_TRAPPIST_inst': ''},
                           'model_definitions': {'': {'category': 'batman',
                                                      'param_extensions': {'planet': {'Frat': '',
                                                                                      'Rrat': ''},
                                                                           'star': {}}}}}}

# Supersampling and exposure_time for LC
########################################
SuperSamps_LC = {'LC_K2_inst': {'supersamp': 1, 'exptime': 0.02043402778},
                 'LC_EulerCam_inst0': {'supersamp': 1, 'exptime': 0.02043402778},
                 'LC_EulerCam_inst1': {'supersamp': 1, 'exptime': 0.02043402778},
                 'LC_TRAPPIST_inst': {'supersamp': 1, 'exptime': 0.02043402778},
                 'LC_IAC80_inst1': {'supersamp': 1, 'exptime': 0.02043402778},
                 'LC_IAC80_inst0': {'supersamp': 1, 'exptime': 0.02043402778},
                 }

# Instrumental model for LC
###########################

# Polynomial trend models for LC
################################
polynomial_model_LC = {'A': {'do': False, 'order': 0, 'tref': None},
                    'LC_EulerCam_inst0': {'do': True, 'order': 0, 'tref': None},
                    'LC_EulerCam_inst1': {'do': True, 'order': 0, 'tref': None},
                    'LC_IAC80_inst0': {'do': True, 'order': 0, 'tref': None},
                    'LC_IAC80_inst1': {'do': True, 'order': 0, 'tref': None},
                    'LC_K2_inst': {'do': True, 'order': 0, 'tref': None},
                    'LC_TRAPPIST_inst': {'do': True, 'order': 0, 'tref': None}}
