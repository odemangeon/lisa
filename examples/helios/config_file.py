# Configuration file for LISA analysis.

##############
## Object name
##############
# Give a name to the object that you are studying. DO NOT use _

object_name = 'Sun'

##########
## Folders
##########

#run_folder = '/home/pedro/Documents/Tese/lisa_n/lisa-helios/examples/helios (copy)/'
run_folder = '~/Softwares/lisa-dev/examples/helios/'

#data_folder = '/home/pedro/Documents/Tese/lisa_n/lisa-helios/examples/helios (copy)/data/'
data_folder = '~/Softwares/lisa-dev/examples/helios/data/'

###########
## Datasets
###########

# List of the paths to the dataset files that you want to use
l_dataset = ['RV_Sun_HELIOS_0.txt', 'IND-Ha_Sun_HELIOS_0.txt', 'IND-CaHK_Sun_HELIOS_0.txt']

##############################
## Instrument model definition
##############################
# Define which instrument model you want to use for each dataset
# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument
# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.
# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0').
d_inst_model_def = {'IND-CaHK': {'HELIOS': {'0': 'inst'}},
                    'IND-Ha': {'HELIOS': {'0': 'inst'}},
                    'RV': {'HELIOS': {'0': 'inst'}}}

####################################
## Model category definition
####################################
# Define the model category and the parameters of the model that are specfic to the model category.

# Available model categories are ['GravitionalGroups']
model_category = 'GravitionalGroups'

# Stars
#######
# Specify the number of stars in the gravitational group. This can be specified by giving a number (ex: 1)
stars = 1

# Planets
#########
# Specify the number of planets in the gravitational group. This can be specified by giving a number (ex: 1) or a list of planet names (ex: ['b'])
planets = 0

# Orbital models
################
orbital_model = {}

#############################
## Configuration of IND models
#############################
# Polynomial trend models for IND
#################################
# Define the model to use for each indicator category. Available models are ['polynomial']
CaHK = {'IND-CaHK_HELIOS_inst': {'polynomial': {'do': True,
                                                'order': 0,
                                                'tref': None}},
        'all': {'polynomial': {'do': False, 'order': 0, 'tref': None}}}
Ha = {'IND-Ha_HELIOS_inst': {'polynomial': {'do': True, 'order': 0, 'tref': None}},
      'all': {'polynomial': {'do': False, 'order': 0, 'tref': None}}}

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
# {'RV_HELIOS_inst': ['RV_Sun_HELIOS_0']}
#
# The list of datasets for each IND instrument model are:
# {'IND-CaHK_HELIOS_inst': ['IND-CaHK_Sun_HELIOS_0'], 'IND-Ha_HELIOS_inst': ['IND-Ha_Sun_HELIOS_0']}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}
# bispline: {'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}


# Decorrelation Model
#####################
decorrelation_model_RV = {'RV_HELIOS_inst': {'do': False,
                                             'what to decorrelate': {'add_2_totalrv': {'linear': {}},
                                                                     'multiply_2_totalrv': {'linear': {}}}}}

# Decorrelation likelihood
##########################
decorrelation_likelihood_RV = {'do': False, 'model_definitions': {}, 'order_models': []}


# Keplerian RV model
####################
keplerian_rv_model = {}

# Instrumental model for RV
###########################

# Polynomial trend models for RV
################################
polynomial_model_RV = {'A': {'do': True, 'order': 0, 'tref': None},
                       'RV_HELIOS_inst': {'do': False, 'order': 0, 'tref': None}}

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
d_noise_model_def = {'IND-CaHK': {'HELIOS': {'inst': 'GP1D'}},
                     'IND-Ha': {'HELIOS': {'inst': 'GP1D'}},
                     'RV': {'HELIOS': {'inst': 'GP1D'}}}

# GP1D noise models
###################
GP1D_models = {'GPmodel4instrument': {'IND-CaHK_HELIOS_inst': 'CaHK',
                                      'IND-Ha_HELIOS_inst': 'Ha',
                                      'RV_HELIOS_inst': 'RV'},
               'GPmodel_definitions': {'CaHK': {'category': 'QPGeorge',
                                                'param_extensions': {'GP': {'A': '',
                                                                            'P': '',
                                                                            'gamma': '',
                                                                            'tau': ''}},
                                                'parametrisation': {'log10': {'A': False,
                                                                              'P': False,
                                                                              'gamma': False,
                                                                              'tau': False}}},
                                       'Ha': {'category': 'QPGeorge',
                                              'param_extensions': {'GP': {'A': '',
                                                                          'P': '',
                                                                          'gamma': '',
                                                                          'tau': ''}},
                                              'parametrisation': {'log10': {'A': False,
                                                                            'P': False,
                                                                            'gamma': False,
                                                                            'tau': False}}},
                                       'RV': {'category': 'QPGeorge',
                                              'param_extensions': {'GP': {'A': '',
                                                                          'P': '',
                                                                          'gamma': '',
                                                                          'tau': ''}},
                                              'parametrisation': {'log10': {'A': False,
                                                                            'P': False,
                                                                            'gamma': False,
                                                                            'tau': False}}}},
               'jittermodel_definitions': {'IND-CaHK_HELIOS_inst': {'args': {'jitter_type': 'additive'},
                                                                    'param_extensions': {'instrument': {'jitter': ''}},
                                                                    'parametrisation': {'log10': False,
                                                                                        'use_Baluevfactor': False}},
                                           'IND-Ha_HELIOS_inst': {'args': {'jitter_type': 'additive'},
                                                                  'param_extensions': {'instrument': {'jitter': ''}},
                                                                  'parametrisation': {'log10': False,
                                                                                      'use_Baluevfactor': False}},
                                           'RV_HELIOS_inst': {'args': {'jitter_type': 'additive'},
                                                              'param_extensions': {'instrument': {'jitter': ''}},
                                                              'parametrisation': {'log10': False,
                                                                                  'use_Baluevfactor': False}}}}

###########################
## Parameters configuration
###########################

# The list of main parameter full names in the model is:
# ['IND-CaHK_HELIOS_inst_C0', 'IND-CaHK_HELIOS_inst_jitter', 'RV_HELIOS_inst_DeltaRV', 'RV_HELIOS_inst_jitter', 'IND-Ha_HELIOS_inst_C0', 'IND-Ha_HELIOS_inst_jitter', 'IND-CaHK_A', 'IND-CaHK_P', 'IND-CaHK_tau', 'IND-CaHK_gamma', 'RV_A', 'RV_P', 'RV_tau', 'RV_gamma', 'IND-Ha_A', 'IND-Ha_P', 'IND-Ha_tau', 'IND-Ha_gamma', 'A_v0']

# Duplicate parameters
######################
# Indicates in the duplicates dictionary which parameters you want to be seen being duplicates of another parameters
# Format: keys are the full name of main parameters that you want to be duplicated.
# Values are the list of main parameters full names that you want to be duplicates of the parameter named by the corresponding key.
duplicates = {'RV_P': ['CaHK_P', 'Ha_P'],'RV_gamma':['CaHK_gamma', 'Ha_gamma'],'RV_tau':['CaHK_tau', 'Ha_tau']}

# Frozen parameters
###################
# Indicates the list the main parameters full names that you want to freeze.
# A frozen parameter will have its value fixed to a given value that you will define in the next step.
frozens = ['RV_HELIOS_inst_DeltaRV']

# Indicates the values for the frozens main parameters
# You should not change the unit value. Every changes that you might make to unit will be ignored.
frozen_values = {'RV_HELIOS_inst_DeltaRV': {'unit': '[RV data unit]', 'value': 0.0}}

# Joint Priors
##############
# The units are provided as information and you should not change it. Any change will be ignored.
#
# These priors convert a given set of jumping parameter into a different set of parameters that
# can be better suited to define priors.
# The list of available joint priors is: 
joint_priors = {}

# Individual Priors
###################
# The units are provided as information and you should not change it. Any change will be ignored.
#
# The list of available individual priors is: 
individual_priors = {'GP1D': {'CaHK': {'A': {'args': {'vmax': 100, 'vmin': 0.0},
                                                 'category': 'uniform',
                                                 'unit': None}
                                                 },
                              'Ha': {'A': {'args': {'vmax': 100, 'vmin': 0.0},
                                               'category': 'uniform',
                                               'unit': None}
                                               },
                              'RV': {'A': {'args': {'vmax': 8.0, 'vmin': 0.0},
                                           'category': 'uniform',
                                           'unit': None},
                                     'P': {'args': {'vmax': 500.0, 'vmin': 10.0},
                                           'category': 'uniform',
                                           'unit': None},
                                     'gamma': {'args': {'vmax': 100.0, 'vmin': 0.1},
                                               'category': 'uniform',
                                               'unit': None},
                                     'tau': {'args': {'vmax': 100.0, 'vmin': 2.0},
                                             'category': 'uniform',
                                             'unit': None}}},
                     'instruments': {'IND-CaHK': {'HELIOS': {'inst': {'C0': {'args': {'vmax': 1.0,
                                                                                      'vmin': 0.0},
                                                                             'category': 'uniform',
                                                                             'unit': '[CaHK data '
                                                                                     'unit]'},
                                                                      'jitter': {'args': {'vmax': 1.0,
                                                                                          'vmin': 0.0},
                                                                                 'category': 'uniform',
                                                                                 'unit': None}}}},
                                     'IND-Ha': {'HELIOS': {'inst': {'C0': {'args': {'vmax': 1.0,
                                                                                    'vmin': 0.0},
                                                                           'category': 'uniform',
                                                                           'unit': '[Ha data '
                                                                                   'unit]'},
                                                                    'jitter': {'args': {'vmax': 1.0,
                                                                                        'vmin': 0.0},
                                                                               'category': 'uniform',
                                                                               'unit': None}}}},
                                     'RV': {'HELIOS': {'inst': {'jitter': {'args': {'vmax': 1.0,
                                                                                    'vmin': 0.0},
                                                                           'category': 'uniform',
                                                                           'unit': None}}}}},
                     'planets': {},
                     'stars': {'A': {'v0': {'args': {'vmax': 1.0, 'vmin': 0.0},
                                            'category': 'uniform',
                                            'unit': None}}},
                     'sys_Sun': {}}
